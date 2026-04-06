from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
import json
from pathlib import Path
import time
from typing import Any, Callable
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from source_engine.cleaner import clean_text

from distribution_engine.models import BlogPublishRecord
from distribution_engine.publish_updates import record_blog_publish_update
from distribution_engine.transport_retry import (
    TransportRetryPolicy,
    execute_with_retry,
    is_retryable_transport_error,
)


ALLOWED_WORDPRESS_DRAFT_SYNC_OPERATIONS = frozenset({"create_draft", "update_draft"})
ALLOWED_REMOTE_DRAFT_STATUSES = frozenset({"draft", "auto-draft"})
BLOCKED_REMOTE_DRAFT_SYNC_STATUSES = frozenset({"scheduled", "published"})
DEFAULT_TIMEOUT_SECONDS = 20


class WordPressRestTransportError(RuntimeError):
    """Raised when a remote WordPress REST draft sync attempt fails."""

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code


WordPressTransportError = WordPressRestTransportError


RequestExecutor = Callable[
    ["WordPressRestRequest", "WordPressRestConfig"],
    dict[str, Any],
]
ValidationRequestExecutor = Callable[
    ["WordPressRestValidationRequest", "WordPressRestConfig"],
    dict[str, Any],
]
PostStateRequestExecutor = Callable[
    ["WordPressRestPostStateRequest", "WordPressRestConfig"],
    dict[str, Any],
]


@dataclass(frozen=True)
class WordPressRestConfig:
    base_url: str
    username: str
    application_password: str = field(repr=False)
    category_id_by_name: dict[str, int] = field(default_factory=dict)
    tag_id_by_name: dict[str, int] = field(default_factory=dict)
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        base_url = clean_text(self.base_url).rstrip("/")
        username = clean_text(self.username)
        application_password = clean_text(self.application_password)
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("WordPress REST config base_url must start with http:// or https://")
        if not username:
            raise ValueError("WordPress REST config requires username.")
        if not application_password:
            raise ValueError("WordPress REST config requires application_password.")
        if self.timeout_seconds <= 0:
            raise ValueError("WordPress REST config timeout_seconds must be greater than zero.")
        object.__setattr__(self, "base_url", base_url)
        object.__setattr__(self, "username", username)
        object.__setattr__(self, "application_password", application_password)
        object.__setattr__(
            self,
        "category_id_by_name",
            _normalize_taxonomy_mapping(self.category_id_by_name, label="category_id_by_name"),
        )
        object.__setattr__(
            self,
            "tag_id_by_name",
            _normalize_taxonomy_mapping(self.tag_id_by_name, label="tag_id_by_name"),
        )

    @property
    def posts_endpoint(self) -> str:
        return f"{self.base_url}/wp-json/wp/v2/posts"


@dataclass(frozen=True)
class WordPressRestRequest:
    operation: str
    method: str
    url: str
    payload: dict[str, Any]
    category_id: int
    tag_ids: tuple[int, ...]
    skipped_tag_names: tuple[str, ...] = ()
    existing_wordpress_post_id: str | None = None
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if self.operation not in ALLOWED_WORDPRESS_DRAFT_SYNC_OPERATIONS:
            raise ValueError(f"Unsupported WordPress REST operation: {self.operation}")
        if not clean_text(self.method):
            raise ValueError("WordPress REST request requires method.")
        if not clean_text(self.url):
            raise ValueError("WordPress REST request requires url.")

    def to_preview_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "method": self.method,
            "url": self.url,
            "payload": self.payload,
            "category_id": self.category_id,
            "tag_ids": list(self.tag_ids),
            "skipped_tag_names": list(self.skipped_tag_names),
            "existing_wordpress_post_id": self.existing_wordpress_post_id,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class WordPressRestExecutionResult:
    operation: str
    wordpress_post_id: str
    wordpress_post_url: str | None
    remote_status: str | None
    response_status_code: int | None = None
    attempt_count: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "wordpress_post_id": self.wordpress_post_id,
            "wordpress_post_url": self.wordpress_post_url,
            "remote_status": self.remote_status,
            "response_status_code": self.response_status_code,
            "attempt_count": self.attempt_count,
        }


@dataclass(frozen=True)
class WordPressDraftSyncResult:
    execution_mode: str
    request: WordPressRestRequest
    updated_blog_publish_record: BlogPublishRecord | None = None
    execution_result: WordPressRestExecutionResult | None = None

    def to_summary_dict(self) -> dict[str, Any]:
        payload = {
            "execution_mode": self.execution_mode,
            "operation": self.request.operation,
            "request": self.request.to_preview_dict(),
        }
        if self.updated_blog_publish_record is not None:
            payload["updated_blog_publish"] = {
                "blog_publish_id": self.updated_blog_publish_record.blog_publish_id,
                "wordpress_status": self.updated_blog_publish_record.wordpress_status,
                "wordpress_post_id": self.updated_blog_publish_record.wordpress_post_id,
                "wordpress_post_url": self.updated_blog_publish_record.wordpress_post_url,
            }
        if self.execution_result is not None:
            payload["execution_result"] = self.execution_result.to_dict()
        return payload


@dataclass(frozen=True)
class WordPressRestValidationRequest:
    method: str
    url: str
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if not clean_text(self.method):
            raise ValueError("WordPress REST validation request requires method.")
        if not clean_text(self.url):
            raise ValueError("WordPress REST validation request requires url.")

    def to_preview_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "url": self.url,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class WordPressRestValidationExecutionResult:
    validated_user_id: str
    validated_user_slug: str | None
    validated_user_name: str | None
    response_status_code: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "validated_user_id": self.validated_user_id,
            "validated_user_slug": self.validated_user_slug,
            "validated_user_name": self.validated_user_name,
            "response_status_code": self.response_status_code,
        }


@dataclass(frozen=True)
class WordPressRestValidationResult:
    execution_mode: str
    request: WordPressRestValidationRequest
    execution_result: WordPressRestValidationExecutionResult | None = None

    def to_summary_dict(self) -> dict[str, Any]:
        payload = {
            "execution_mode": self.execution_mode,
            "request": self.request.to_preview_dict(),
        }
        if self.execution_result is not None:
            payload["execution_result"] = self.execution_result.to_dict()
        return payload


@dataclass(frozen=True)
class WordPressRestPostStateRequest:
    wordpress_post_id: str
    method: str
    url: str
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if not clean_text(self.wordpress_post_id):
            raise ValueError("WordPress REST post-state request requires wordpress_post_id.")
        if not clean_text(self.method):
            raise ValueError("WordPress REST post-state request requires method.")
        if not clean_text(self.url):
            raise ValueError("WordPress REST post-state request requires url.")

    def to_preview_dict(self) -> dict[str, Any]:
        return {
            "wordpress_post_id": self.wordpress_post_id,
            "method": self.method,
            "url": self.url,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class WordPressRestPostStateExecutionResult:
    wordpress_post_id: str
    wordpress_post_url: str | None
    remote_status: str | None
    remote_slug: str | None = None
    remote_title: str | None = None
    remote_published_at: str | None = None
    remote_modified_at: str | None = None
    response_status_code: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "wordpress_post_id": self.wordpress_post_id,
            "wordpress_post_url": self.wordpress_post_url,
            "remote_status": self.remote_status,
            "remote_slug": self.remote_slug,
            "remote_title": self.remote_title,
            "remote_published_at": self.remote_published_at,
            "remote_modified_at": self.remote_modified_at,
            "response_status_code": self.response_status_code,
        }


@dataclass(frozen=True)
class WordPressRestPostStateResult:
    execution_mode: str
    request: WordPressRestPostStateRequest
    execution_result: WordPressRestPostStateExecutionResult | None = None

    def to_summary_dict(self) -> dict[str, Any]:
        payload = {
            "execution_mode": self.execution_mode,
            "request": self.request.to_preview_dict(),
        }
        if self.execution_result is not None:
            payload["execution_result"] = self.execution_result.to_dict()
        return payload


def load_wordpress_rest_config(path: Path) -> WordPressRestConfig:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Unknown WordPress REST config path: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"WordPress REST config is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("WordPress REST config must contain a JSON object.")
    try:
        timeout_seconds = int(payload.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))
    except (TypeError, ValueError) as exc:
        raise ValueError("WordPress REST config timeout_seconds must be an integer.") from exc
    return WordPressRestConfig(
        base_url=str(payload.get("base_url", "")),
        username=str(payload.get("username", "")),
        application_password=str(payload.get("application_password", "")),
        category_id_by_name=_coerce_mapping_payload(payload.get("category_id_by_name"), "category_id_by_name"),
        tag_id_by_name=_coerce_mapping_payload(payload.get("tag_id_by_name"), "tag_id_by_name"),
        timeout_seconds=timeout_seconds,
    )


def build_wordpress_rest_validation_request(
    config: WordPressRestConfig,
) -> WordPressRestValidationRequest:
    return WordPressRestValidationRequest(
        method="GET",
        url=f"{config.base_url}/wp-json/wp/v2/users/me?context=edit",
        timeout_seconds=config.timeout_seconds,
    )


def build_wordpress_rest_post_state_request(
    wordpress_post_id: str,
    config: WordPressRestConfig,
) -> WordPressRestPostStateRequest:
    normalized_post_id = clean_text(wordpress_post_id)
    if not normalized_post_id:
        raise ValueError("WordPress REST post-state inspection requires wordpress_post_id.")
    return WordPressRestPostStateRequest(
        wordpress_post_id=normalized_post_id,
        method="GET",
        url=(
            f"{config.posts_endpoint}/{urllib_parse.quote(normalized_post_id, safe='')}"
            "?context=edit"
        ),
        timeout_seconds=config.timeout_seconds,
    )


def build_wordpress_rest_request(
    blog_publish_record: BlogPublishRecord,
    config: WordPressRestConfig,
) -> WordPressRestRequest:
    _validate_blog_publish_record_for_remote_draft_sync(blog_publish_record)
    category_name = clean_text(blog_publish_record.wordpress_category)
    category_id = _resolve_required_taxonomy_id(
        category_name,
        config.category_id_by_name,
        label="WordPress category",
    )
    tag_ids, skipped_tag_names = _resolve_tag_ids(blog_publish_record.wordpress_tags, config.tag_id_by_name)
    existing_post_id = clean_text(blog_publish_record.wordpress_post_id or "") or None
    operation = "update_draft" if existing_post_id else "create_draft"
    url = config.posts_endpoint
    if existing_post_id:
        url = f"{config.posts_endpoint}/{urllib_parse.quote(existing_post_id, safe='')}"

    payload: dict[str, Any] = {
        "title": clean_text(blog_publish_record.wordpress_title),
        "slug": clean_text(blog_publish_record.wordpress_slug),
        "excerpt": clean_text(blog_publish_record.wordpress_excerpt),
        "content": blog_publish_record.wordpress_body_html.strip(),
        "status": "draft",
        "categories": [category_id],
    }
    if tag_ids:
        payload["tags"] = list(tag_ids)

    return WordPressRestRequest(
        operation=operation,
        method="POST",
        url=url,
        payload=payload,
        category_id=category_id,
        tag_ids=tag_ids,
        skipped_tag_names=skipped_tag_names,
        existing_wordpress_post_id=existing_post_id,
        timeout_seconds=config.timeout_seconds,
    )


def execute_wordpress_rest_request(
    request: WordPressRestRequest,
    config: WordPressRestConfig,
    request_executor: RequestExecutor | None = None,
) -> WordPressRestExecutionResult:
    if request_executor is not None:
        response_payload = request_executor(request, config)
    else:
        response_payload = _default_request_executor(request, config)
    if not isinstance(response_payload, dict):
        raise WordPressRestTransportError("WordPress REST response payload must be a JSON object.")

    remote_post_id = clean_text(str(response_payload.get("id", "")))
    if not remote_post_id:
        raise WordPressRestTransportError("WordPress REST response did not include a post id.")

    remote_status_raw = response_payload.get("status")
    remote_status = clean_text(str(remote_status_raw)) if remote_status_raw is not None else ""
    remote_status = remote_status or None
    if remote_status and remote_status not in ALLOWED_REMOTE_DRAFT_STATUSES:
        raise WordPressRestTransportError(
            f"WordPress REST response returned unsupported remote status '{remote_status}' for draft sync."
        )

    remote_link = response_payload.get("link")
    wordpress_post_url = clean_text(str(remote_link)) if remote_link is not None else ""
    wordpress_post_url = wordpress_post_url or None
    response_status_code = response_payload.get("_response_status_code")
    if response_status_code is not None:
        try:
            response_status_code = int(response_status_code)
        except (TypeError, ValueError):
            response_status_code = None

    return WordPressRestExecutionResult(
        operation=request.operation,
        wordpress_post_id=remote_post_id,
        wordpress_post_url=wordpress_post_url,
        remote_status=remote_status,
        response_status_code=response_status_code,
    )


def execute_wordpress_rest_request_with_retry(
    request: WordPressRestRequest,
    config: WordPressRestConfig,
    *,
    retry_policy: TransportRetryPolicy | None = None,
    request_executor: RequestExecutor | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> WordPressRestExecutionResult:
    policy = retry_policy or TransportRetryPolicy()
    sleep_callable = sleeper if sleeper is not None else time.sleep
    execution_result, attempt_count = execute_with_retry(
        lambda: execute_wordpress_rest_request(
            request,
            config,
            request_executor=request_executor,
        ),
        policy,
        is_retryable_error=is_retryable_transport_error,
        sleeper=sleep_callable,
    )
    if attempt_count == execution_result.attempt_count:
        return execution_result
    return replace(execution_result, attempt_count=attempt_count)


def execute_wordpress_rest_validation_request(
    request: WordPressRestValidationRequest,
    config: WordPressRestConfig,
    request_executor: ValidationRequestExecutor | None = None,
) -> WordPressRestValidationExecutionResult:
    if request_executor is not None:
        response_payload = request_executor(request, config)
    else:
        response_payload = _default_validation_request_executor(request, config)
    if not isinstance(response_payload, dict):
        raise WordPressRestTransportError("WordPress REST validation response payload must be a JSON object.")

    validated_user_id = clean_text(str(response_payload.get("id", "")))
    if not validated_user_id:
        raise WordPressRestTransportError("WordPress REST validation response did not include a user id.")
    validated_user_slug = clean_text(str(response_payload.get("slug", ""))) or None
    validated_user_name = clean_text(str(response_payload.get("name", ""))) or None
    response_status_code = response_payload.get("_response_status_code")
    if response_status_code is not None:
        try:
            response_status_code = int(response_status_code)
        except (TypeError, ValueError):
            response_status_code = None
    return WordPressRestValidationExecutionResult(
        validated_user_id=validated_user_id,
        validated_user_slug=validated_user_slug,
        validated_user_name=validated_user_name,
        response_status_code=response_status_code,
    )


def execute_wordpress_rest_post_state_request(
    request: WordPressRestPostStateRequest,
    config: WordPressRestConfig,
    request_executor: PostStateRequestExecutor | None = None,
) -> WordPressRestPostStateExecutionResult:
    if request_executor is not None:
        response_payload = request_executor(request, config)
    else:
        response_payload = _default_post_state_request_executor(request, config)
    if not isinstance(response_payload, dict):
        raise WordPressRestTransportError("WordPress REST post-state response payload must be a JSON object.")

    remote_post_id = clean_text(str(response_payload.get("id", "")))
    if not remote_post_id:
        raise WordPressRestTransportError("WordPress REST post-state response did not include a post id.")

    remote_status_raw = response_payload.get("status")
    remote_status = clean_text(str(remote_status_raw)) if remote_status_raw is not None else ""
    remote_status = remote_status or None

    remote_link = response_payload.get("link")
    wordpress_post_url = clean_text(str(remote_link)) if remote_link is not None else ""
    wordpress_post_url = wordpress_post_url or None

    remote_slug = clean_text(str(response_payload.get("slug", ""))) or None
    remote_title = _extract_remote_title(response_payload.get("title"))
    remote_published_at = _normalize_wordpress_timestamp(
        response_payload.get("date_gmt") or response_payload.get("date")
    )
    remote_modified_at = _normalize_wordpress_timestamp(
        response_payload.get("modified_gmt") or response_payload.get("modified")
    )

    response_status_code = response_payload.get("_response_status_code")
    if response_status_code is not None:
        try:
            response_status_code = int(response_status_code)
        except (TypeError, ValueError):
            response_status_code = None

    return WordPressRestPostStateExecutionResult(
        wordpress_post_id=remote_post_id,
        wordpress_post_url=wordpress_post_url,
        remote_status=remote_status,
        remote_slug=remote_slug,
        remote_title=remote_title,
        remote_published_at=remote_published_at,
        remote_modified_at=remote_modified_at,
        response_status_code=response_status_code,
    )


def sync_wordpress_rest_draft(
    blog_publish_record: BlogPublishRecord,
    config: WordPressRestConfig,
    execute: bool = False,
    retry_policy: TransportRetryPolicy | None = None,
    request_executor: RequestExecutor | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> WordPressDraftSyncResult:
    request = build_wordpress_rest_request(blog_publish_record, config)
    if not execute:
        return WordPressDraftSyncResult(execution_mode="dry_run", request=request)

    execution_result = execute_wordpress_rest_request_with_retry(
        request,
        config,
        retry_policy=retry_policy,
        request_executor=request_executor,
        sleeper=sleeper,
    )
    update_action = "draft_updated" if request.operation == "update_draft" else "draft_created"
    updated_blog_publish = record_blog_publish_update(
        blog_publish_record,
        update_action=update_action,
        wordpress_post_id=execution_result.wordpress_post_id,
        wordpress_post_url=execution_result.wordpress_post_url,
    )
    return WordPressDraftSyncResult(
        execution_mode="execute",
        request=request,
        updated_blog_publish_record=updated_blog_publish,
        execution_result=execution_result,
    )


def validate_wordpress_rest_transport(
    config: WordPressRestConfig,
    execute: bool = False,
    request_executor: ValidationRequestExecutor | None = None,
) -> WordPressRestValidationResult:
    request = build_wordpress_rest_validation_request(config)
    if not execute:
        return WordPressRestValidationResult(execution_mode="dry_run", request=request)
    execution_result = execute_wordpress_rest_validation_request(
        request,
        config,
        request_executor=request_executor,
    )
    return WordPressRestValidationResult(
        execution_mode="execute",
        request=request,
        execution_result=execution_result,
    )


def inspect_wordpress_rest_post_state(
    wordpress_post_id: str,
    config: WordPressRestConfig,
    execute: bool = False,
    request_executor: PostStateRequestExecutor | None = None,
) -> WordPressRestPostStateResult:
    request = build_wordpress_rest_post_state_request(wordpress_post_id, config)
    if not execute:
        return WordPressRestPostStateResult(execution_mode="dry_run", request=request)
    execution_result = execute_wordpress_rest_post_state_request(
        request,
        config,
        request_executor=request_executor,
    )
    return WordPressRestPostStateResult(
        execution_mode="execute",
        request=request,
        execution_result=execution_result,
    )


def _validate_blog_publish_record_for_remote_draft_sync(blog_publish_record: BlogPublishRecord) -> None:
    if blog_publish_record.wordpress_status in BLOCKED_REMOTE_DRAFT_SYNC_STATUSES:
        raise ValueError(
            "WordPress REST draft sync only supports prepared or remote-draft records, not scheduled or published posts."
        )
    if not clean_text(blog_publish_record.blog_publish_id):
        raise ValueError("WordPress REST draft sync requires blog_publish_id.")
    if not clean_text(blog_publish_record.wordpress_title):
        raise ValueError("WordPress REST draft sync requires wordpress_title.")
    if not clean_text(blog_publish_record.wordpress_slug):
        raise ValueError("WordPress REST draft sync requires wordpress_slug.")
    if not clean_text(blog_publish_record.wordpress_body_html):
        raise ValueError("WordPress REST draft sync requires wordpress_body_html.")
    if not clean_text(blog_publish_record.wordpress_category):
        raise ValueError("WordPress REST draft sync requires wordpress_category.")


def _resolve_required_taxonomy_id(
    value: str,
    mapping: dict[str, int],
    label: str,
) -> int:
    normalized_value = _normalize_taxonomy_key(value)
    candidate_id = mapping.get(normalized_value)
    if candidate_id is None:
        raise ValueError(f"{label} '{value}' is missing from the WordPress REST config mapping.")
    return candidate_id


def _resolve_tag_ids(tag_names: list[str], mapping: dict[str, int]) -> tuple[tuple[int, ...], tuple[str, ...]]:
    tag_ids: list[int] = []
    skipped: list[str] = []
    seen_ids: set[int] = set()
    for tag_name in tag_names:
        normalized_tag = clean_text(tag_name)
        if not normalized_tag:
            continue
        tag_id = mapping.get(_normalize_taxonomy_key(normalized_tag))
        if tag_id is None:
            skipped.append(normalized_tag)
            continue
        if tag_id in seen_ids:
            continue
        seen_ids.add(tag_id)
        tag_ids.append(tag_id)
    return tuple(tag_ids), tuple(skipped)


def _normalize_taxonomy_mapping(mapping: dict[str, int], label: str) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for key, value in mapping.items():
        normalized_key = _normalize_taxonomy_key(str(key))
        if not normalized_key:
            raise ValueError(f"WordPress REST config {label} cannot contain an empty taxonomy label.")
        try:
            normalized_value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"WordPress REST config {label} values must be integer ids.") from exc
        normalized[normalized_key] = normalized_value
    return normalized


def _coerce_mapping_payload(value: object, label: str) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"WordPress REST config {label} must be a JSON object.")
    return dict(value)


def _normalize_taxonomy_key(value: str) -> str:
    return clean_text(value).lower()


def _default_request_executor(
    request: WordPressRestRequest,
    config: WordPressRestConfig,
) -> dict[str, Any]:
    payload_bytes = json.dumps(request.payload).encode("utf-8")
    http_request = urllib_request.Request(
        request.url,
        data=payload_bytes,
        method=request.method,
        headers=_build_wordpress_auth_headers(config, include_content_type=True),
    )

    try:
        with urllib_request.urlopen(http_request, timeout=request.timeout_seconds) as response:
            response_body = response.read().decode("utf-8") or "{}"
            payload = json.loads(response_body)
            payload["_response_status_code"] = getattr(response, "status", None)
            return payload
    except urllib_error.HTTPError as exc:
        response_text = _read_http_error_body(exc)
        raise WordPressRestTransportError(
            f"WordPress REST draft sync failed with HTTP {exc.code}: {response_text or exc.reason}",
            retryable=exc.code in {408, 425, 429, 500, 502, 503, 504},
            status_code=exc.code,
        ) from exc
    except urllib_error.URLError as exc:
        raise WordPressRestTransportError(
            f"WordPress REST draft sync request failed: {exc.reason}",
            retryable=True,
        ) from exc
    except json.JSONDecodeError as exc:
        raise WordPressRestTransportError("WordPress REST response was not valid JSON.") from exc


def _default_validation_request_executor(
    request: WordPressRestValidationRequest,
    config: WordPressRestConfig,
) -> dict[str, Any]:
    http_request = urllib_request.Request(
        request.url,
        method=request.method,
        headers=_build_wordpress_auth_headers(config),
    )
    try:
        with urllib_request.urlopen(http_request, timeout=request.timeout_seconds) as response:
            response_body = response.read().decode("utf-8") or "{}"
            payload = json.loads(response_body)
            payload["_response_status_code"] = getattr(response, "status", None)
            return payload
    except urllib_error.HTTPError as exc:
        response_text = _read_http_error_body(exc)
        raise WordPressRestTransportError(
            f"WordPress REST validation failed with HTTP {exc.code}: {response_text or exc.reason}",
            retryable=exc.code in {408, 425, 429, 500, 502, 503, 504},
            status_code=exc.code,
        ) from exc
    except urllib_error.URLError as exc:
        raise WordPressRestTransportError(
            f"WordPress REST validation request failed: {exc.reason}",
            retryable=True,
        ) from exc
    except json.JSONDecodeError as exc:
        raise WordPressRestTransportError("WordPress REST validation response was not valid JSON.") from exc


def _default_post_state_request_executor(
    request: WordPressRestPostStateRequest,
    config: WordPressRestConfig,
) -> dict[str, Any]:
    http_request = urllib_request.Request(
        request.url,
        method=request.method,
        headers=_build_wordpress_auth_headers(config),
    )
    try:
        with urllib_request.urlopen(http_request, timeout=request.timeout_seconds) as response:
            response_body = response.read().decode("utf-8") or "{}"
            payload = json.loads(response_body)
            payload["_response_status_code"] = getattr(response, "status", None)
            return payload
    except urllib_error.HTTPError as exc:
        response_text = _read_http_error_body(exc)
        raise WordPressRestTransportError(
            f"WordPress REST post-state inspection failed with HTTP {exc.code}: {response_text or exc.reason}",
            retryable=exc.code in {408, 425, 429, 500, 502, 503, 504},
            status_code=exc.code,
        ) from exc
    except urllib_error.URLError as exc:
        raise WordPressRestTransportError(
            f"WordPress REST post-state request failed: {exc.reason}",
            retryable=True,
        ) from exc
    except json.JSONDecodeError as exc:
        raise WordPressRestTransportError("WordPress REST post-state response was not valid JSON.") from exc


def _build_wordpress_auth_headers(
    config: WordPressRestConfig,
    *,
    include_content_type: bool = False,
) -> dict[str, str]:
    auth_token = b64encode(f"{config.username}:{config.application_password}".encode("utf-8")).decode("ascii")
    headers = {
        "Authorization": f"Basic {auth_token}",
        "Accept": "application/json",
    }
    if include_content_type:
        headers["Content-Type"] = "application/json"
    return headers


def _extract_remote_title(value: object) -> str | None:
    if isinstance(value, dict):
        rendered = clean_text(str(value.get("rendered", "")))
        return rendered or None
    if value is None:
        return None
    rendered = clean_text(str(value))
    return rendered or None


def _normalize_wordpress_timestamp(value: object) -> str | None:
    raw_value = clean_text(str(value)) if value is not None else ""
    if not raw_value or raw_value.startswith("0000-00-00"):
        return None
    normalized = raw_value.replace("Z", "+00:00")
    if len(normalized) == 19 and "T" in normalized:
        normalized = f"{normalized}+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.isoformat()


def _read_http_error_body(exc: urllib_error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8")
    except Exception:
        return ""
    return clean_text(body)
