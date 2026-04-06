from __future__ import annotations

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

from distribution_engine.scheduling import validate_facebook_schedule_allowed
from distribution_engine.facebook_publish_updates import record_facebook_publish_update
from distribution_engine.models import BlogPublishRecord, FacebookPublishRecord, SocialPackageRecord
from distribution_engine.transport_retry import (
    TransportRetryPolicy,
    execute_with_retry,
    is_retryable_transport_error,
)


ALLOWED_FACEBOOK_GRAPH_TRANSPORT_ACTIONS = frozenset({"scheduled", "published"})
DEFAULT_FACEBOOK_GRAPH_API_VERSION = "v24.0"
DEFAULT_TIMEOUT_SECONDS = 20


class FacebookGraphTransportError(RuntimeError):
    """Raised when a Facebook Graph transport call fails."""

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


FacebookRequestExecutor = Callable[
    ["FacebookGraphRequest", "FacebookGraphConfig"],
    dict[str, Any],
]
FacebookValidationRequestExecutor = Callable[
    ["FacebookGraphValidationRequest", "FacebookGraphConfig"],
    dict[str, Any],
]


@dataclass(frozen=True)
class FacebookGraphConfig:
    page_id: str
    page_access_token: str = field(repr=False)
    api_version: str = DEFAULT_FACEBOOK_GRAPH_API_VERSION
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        page_id = clean_text(self.page_id)
        page_access_token = clean_text(self.page_access_token)
        api_version = clean_text(self.api_version) or DEFAULT_FACEBOOK_GRAPH_API_VERSION
        if not page_id:
            raise ValueError("Facebook Graph config requires page_id.")
        if not page_access_token:
            raise ValueError("Facebook Graph config requires page_access_token.")
        if not api_version.startswith("v"):
            raise ValueError("Facebook Graph config api_version must look like 'v24.0'.")
        if self.timeout_seconds <= 0:
            raise ValueError("Facebook Graph config timeout_seconds must be greater than zero.")
        object.__setattr__(self, "page_id", page_id)
        object.__setattr__(self, "page_access_token", page_access_token)
        object.__setattr__(self, "api_version", api_version)

    @property
    def page_feed_endpoint(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}/{self.page_id}/feed"


@dataclass(frozen=True)
class FacebookGraphRequest:
    action: str
    method: str
    url: str
    form_fields: dict[str, str]
    scheduled_for_facebook: str | None = None
    deferred_comment_cta_text: str | None = None
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if self.action not in ALLOWED_FACEBOOK_GRAPH_TRANSPORT_ACTIONS:
            raise ValueError(f"Unsupported Facebook transport action: {self.action}")
        if not clean_text(self.method):
            raise ValueError("Facebook transport request requires method.")
        if not clean_text(self.url):
            raise ValueError("Facebook transport request requires url.")

    def to_preview_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "method": self.method,
            "url": self.url,
            "form_fields": self.form_fields,
            "scheduled_for_facebook": self.scheduled_for_facebook,
            "deferred_comment_cta_text": self.deferred_comment_cta_text,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class FacebookGraphExecutionResult:
    action: str
    facebook_post_id: str
    response_status_code: int | None = None
    attempt_count: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "facebook_post_id": self.facebook_post_id,
            "response_status_code": self.response_status_code,
            "attempt_count": self.attempt_count,
        }


@dataclass(frozen=True)
class FacebookGraphSyncResult:
    execution_mode: str
    request: FacebookGraphRequest
    updated_facebook_publish_record: FacebookPublishRecord | None = None
    execution_result: FacebookGraphExecutionResult | None = None

    def to_summary_dict(self) -> dict[str, Any]:
        payload = {
            "execution_mode": self.execution_mode,
            "action": self.request.action,
            "request": self.request.to_preview_dict(),
        }
        if self.updated_facebook_publish_record is not None:
            payload["updated_facebook_publish"] = {
                "facebook_publish_id": self.updated_facebook_publish_record.facebook_publish_id,
                "publish_status": self.updated_facebook_publish_record.publish_status,
                "facebook_post_id": self.updated_facebook_publish_record.facebook_post_id,
            }
        if self.execution_result is not None:
            payload["execution_result"] = self.execution_result.to_dict()
        return payload


@dataclass(frozen=True)
class FacebookGraphValidationRequest:
    method: str
    url: str
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if not clean_text(self.method):
            raise ValueError("Facebook Graph validation request requires method.")
        if not clean_text(self.url):
            raise ValueError("Facebook Graph validation request requires url.")

    def to_preview_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "url": self.url,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class FacebookGraphValidationExecutionResult:
    validated_page_id: str
    validated_page_name: str | None
    response_status_code: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "validated_page_id": self.validated_page_id,
            "validated_page_name": self.validated_page_name,
            "response_status_code": self.response_status_code,
        }


@dataclass(frozen=True)
class FacebookGraphValidationResult:
    execution_mode: str
    request: FacebookGraphValidationRequest
    execution_result: FacebookGraphValidationExecutionResult | None = None

    def to_summary_dict(self) -> dict[str, Any]:
        payload = {
            "execution_mode": self.execution_mode,
            "request": self.request.to_preview_dict(),
        }
        if self.execution_result is not None:
            payload["execution_result"] = self.execution_result.to_dict()
        return payload


def load_facebook_graph_config(path: Path) -> FacebookGraphConfig:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Unknown Facebook Graph config path: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Facebook Graph config is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Facebook Graph config must contain a JSON object.")
    try:
        timeout_seconds = int(payload.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))
    except (TypeError, ValueError) as exc:
        raise ValueError("Facebook Graph config timeout_seconds must be an integer.") from exc
    return FacebookGraphConfig(
        page_id=str(payload.get("page_id", "")),
        page_access_token=str(payload.get("page_access_token", "")),
        api_version=str(payload.get("api_version", DEFAULT_FACEBOOK_GRAPH_API_VERSION)),
        timeout_seconds=timeout_seconds,
    )


def build_facebook_graph_validation_request(
    config: FacebookGraphConfig,
) -> FacebookGraphValidationRequest:
    return FacebookGraphValidationRequest(
        method="GET",
        url=f"https://graph.facebook.com/{config.api_version}/{config.page_id}?fields=id,name",
        timeout_seconds=config.timeout_seconds,
    )


def build_facebook_graph_request(
    social_package_record: SocialPackageRecord,
    blog_publish_record: BlogPublishRecord,
    action: str,
    scheduled_for_facebook: str | None = None,
) -> FacebookGraphRequest:
    if action not in ALLOWED_FACEBOOK_GRAPH_TRANSPORT_ACTIONS:
        raise ValueError(f"Unsupported Facebook transport action: {action}")
    _validate_transport_inputs(
        social_package_record,
        blog_publish_record,
        action=action,
        scheduled_for_facebook=scheduled_for_facebook,
    )
    message = _compose_facebook_post_message(social_package_record)
    form_fields = {
        "message": message,
        "link": clean_text(blog_publish_record.wordpress_post_url),
    }
    normalized_schedule = None
    if action == "scheduled":
        normalized_schedule = _resolve_timestamp(scheduled_for_facebook)
        form_fields["published"] = "false"
        form_fields["scheduled_publish_time"] = str(_iso_to_unix_timestamp(normalized_schedule))

    return FacebookGraphRequest(
        action=action,
        method="POST",
        url=f"https://graph.facebook.com/{DEFAULT_FACEBOOK_GRAPH_API_VERSION}/placeholder",
        form_fields=form_fields,
        scheduled_for_facebook=normalized_schedule,
        deferred_comment_cta_text=clean_text(social_package_record.comment_cta_text) or None,
    )


def build_facebook_graph_request_for_config(
    social_package_record: SocialPackageRecord,
    blog_publish_record: BlogPublishRecord,
    action: str,
    config: FacebookGraphConfig,
    scheduled_for_facebook: str | None = None,
) -> FacebookGraphRequest:
    request = build_facebook_graph_request(
        social_package_record,
        blog_publish_record,
        action=action,
        scheduled_for_facebook=scheduled_for_facebook,
    )
    return FacebookGraphRequest(
        action=request.action,
        method=request.method,
        url=config.page_feed_endpoint,
        form_fields=request.form_fields,
        scheduled_for_facebook=request.scheduled_for_facebook,
        deferred_comment_cta_text=request.deferred_comment_cta_text,
        timeout_seconds=config.timeout_seconds,
    )


def execute_facebook_graph_request(
    request: FacebookGraphRequest,
    config: FacebookGraphConfig,
    request_executor: FacebookRequestExecutor | None = None,
) -> FacebookGraphExecutionResult:
    if request_executor is not None:
        response_payload = request_executor(request, config)
    else:
        response_payload = _default_request_executor(request, config)
    if not isinstance(response_payload, dict):
        raise FacebookGraphTransportError("Facebook Graph response payload must be a JSON object.")
    facebook_post_id = clean_text(str(response_payload.get("id", "")))
    if not facebook_post_id:
        raise FacebookGraphTransportError("Facebook Graph response did not include a post id.")
    response_status_code = response_payload.get("_response_status_code")
    if response_status_code is not None:
        try:
            response_status_code = int(response_status_code)
        except (TypeError, ValueError):
            response_status_code = None
    return FacebookGraphExecutionResult(
        action=request.action,
        facebook_post_id=facebook_post_id,
        response_status_code=response_status_code,
    )


def execute_facebook_graph_request_with_retry(
    request: FacebookGraphRequest,
    config: FacebookGraphConfig,
    *,
    retry_policy: TransportRetryPolicy | None = None,
    request_executor: FacebookRequestExecutor | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> FacebookGraphExecutionResult:
    policy = retry_policy or TransportRetryPolicy()
    sleep_callable = sleeper if sleeper is not None else time.sleep
    execution_result, attempt_count = execute_with_retry(
        lambda: execute_facebook_graph_request(
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


def execute_facebook_graph_validation_request(
    request: FacebookGraphValidationRequest,
    config: FacebookGraphConfig,
    request_executor: FacebookValidationRequestExecutor | None = None,
) -> FacebookGraphValidationExecutionResult:
    if request_executor is not None:
        response_payload = request_executor(request, config)
    else:
        response_payload = _default_validation_request_executor(request, config)
    if not isinstance(response_payload, dict):
        raise FacebookGraphTransportError("Facebook Graph validation response payload must be a JSON object.")
    validated_page_id = clean_text(str(response_payload.get("id", "")))
    if not validated_page_id:
        raise FacebookGraphTransportError("Facebook Graph validation response did not include a page id.")
    validated_page_name = clean_text(str(response_payload.get("name", ""))) or None
    response_status_code = response_payload.get("_response_status_code")
    if response_status_code is not None:
        try:
            response_status_code = int(response_status_code)
        except (TypeError, ValueError):
            response_status_code = None
    return FacebookGraphValidationExecutionResult(
        validated_page_id=validated_page_id,
        validated_page_name=validated_page_name,
        response_status_code=response_status_code,
    )


def sync_facebook_graph_post(
    social_package_record: SocialPackageRecord,
    blog_publish_record: BlogPublishRecord,
    config: FacebookGraphConfig,
    action: str,
    scheduled_for_facebook: str | None = None,
    execute: bool = False,
    existing_publish_record: FacebookPublishRecord | None = None,
    schedule_mode: str | None = None,
    schedule_approved_by: str | None = None,
    schedule_applied_by: str | None = None,
    retry_policy: TransportRetryPolicy | None = None,
    request_executor: FacebookRequestExecutor | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> FacebookGraphSyncResult:
    request = build_facebook_graph_request_for_config(
        social_package_record,
        blog_publish_record,
        action=action,
        config=config,
        scheduled_for_facebook=scheduled_for_facebook,
    )
    _validate_existing_publish_state(existing_publish_record)
    if not execute:
        return FacebookGraphSyncResult(execution_mode="dry_run", request=request)

    execution_result = execute_facebook_graph_request_with_retry(
        request,
        config,
        retry_policy=retry_policy,
        request_executor=request_executor,
        sleeper=sleeper,
    )
    updated_record = record_facebook_publish_update(
        social_package_record,
        blog_publish_record,
        update_action=action,
        existing_publish_record=existing_publish_record,
        facebook_post_id=execution_result.facebook_post_id,
        schedule_mode=schedule_mode,
        schedule_approved_by=schedule_approved_by,
        schedule_applied_by=schedule_applied_by,
        scheduled_for_facebook=request.scheduled_for_facebook,
        published_at_facebook=(_resolve_timestamp(None) if action == "published" else None),
    )
    return FacebookGraphSyncResult(
        execution_mode="execute",
        request=request,
        updated_facebook_publish_record=updated_record,
        execution_result=execution_result,
    )


def validate_facebook_graph_transport(
    config: FacebookGraphConfig,
    execute: bool = False,
    request_executor: FacebookValidationRequestExecutor | None = None,
) -> FacebookGraphValidationResult:
    request = build_facebook_graph_validation_request(config)
    if not execute:
        return FacebookGraphValidationResult(execution_mode="dry_run", request=request)
    execution_result = execute_facebook_graph_validation_request(
        request,
        config,
        request_executor=request_executor,
    )
    return FacebookGraphValidationResult(
        execution_mode="execute",
        request=request,
        execution_result=execution_result,
    )


def _compose_facebook_post_message(social_package_record: SocialPackageRecord) -> str:
    hook = clean_text(social_package_record.hook_text)
    caption = clean_text(social_package_record.caption_text)
    if not hook:
        raise ValueError("Facebook transport requires hook_text.")
    if not caption:
        raise ValueError("Facebook transport requires caption_text.")
    if hook == caption:
        return hook
    return f"{hook}\n\n{caption}"


def _validate_transport_inputs(
    social_package_record: SocialPackageRecord,
    blog_publish_record: BlogPublishRecord,
    *,
    action: str,
    scheduled_for_facebook: str | None,
) -> None:
    if social_package_record.approval_state != "approved":
        raise ValueError("Facebook Graph transport requires an approved social package.")
    if social_package_record.blog_publish_id != blog_publish_record.blog_publish_id:
        raise ValueError("Facebook Graph transport requires a social package linked to the same blog publish record.")
    confirmed_blog_url = clean_text(blog_publish_record.wordpress_post_url)
    if not confirmed_blog_url:
        raise ValueError("Facebook Graph transport requires a confirmed blog URL.")
    if blog_publish_record.wordpress_status in {"prepared_local", "", "draft_created", "draft_updated"}:
        if action == "published":
            raise ValueError("Facebook Graph publish transport requires the linked blog post to already be published.")
    if action == "published" and blog_publish_record.wordpress_status != "published":
        raise ValueError("Facebook Graph publish transport requires the linked blog post to already be published.")
    if action == "scheduled":
        if not clean_text(scheduled_for_facebook or ""):
            raise ValueError("Facebook Graph scheduled transport requires scheduled_for_facebook.")
        validate_facebook_schedule_allowed(
            blog_publish_record,
            scheduled_for_facebook=_resolve_timestamp(scheduled_for_facebook),
        )


def _validate_existing_publish_state(existing_publish_record: FacebookPublishRecord | None) -> None:
    if existing_publish_record is None:
        return
    if existing_publish_record.publish_status in {"scheduled", "published"}:
        raise ValueError(
            "Facebook Graph transport cannot create another live post for a social package that is already scheduled or published."
        )


def _default_request_executor(
    request: FacebookGraphRequest,
    config: FacebookGraphConfig,
) -> dict[str, Any]:
    payload_bytes = urllib_parse.urlencode(request.form_fields).encode("utf-8")
    http_request = urllib_request.Request(
        request.url,
        data=payload_bytes,
        method=request.method,
        headers={
            "Authorization": f"Bearer {config.page_access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    try:
        with urllib_request.urlopen(http_request, timeout=request.timeout_seconds) as response:
            response_body = response.read().decode("utf-8") or "{}"
            payload = json.loads(response_body)
            payload["_response_status_code"] = getattr(response, "status", None)
            return payload
    except urllib_error.HTTPError as exc:
        response_text = _read_http_error_body(exc)
        raise FacebookGraphTransportError(
            f"Facebook Graph transport failed with HTTP {exc.code}: {response_text or exc.reason}",
            retryable=exc.code in {408, 425, 429, 500, 502, 503, 504},
            status_code=exc.code,
        ) from exc
    except urllib_error.URLError as exc:
        raise FacebookGraphTransportError(
            f"Facebook Graph transport request failed: {exc.reason}",
            retryable=True,
        ) from exc
    except json.JSONDecodeError as exc:
        raise FacebookGraphTransportError("Facebook Graph response was not valid JSON.") from exc


def _default_validation_request_executor(
    request: FacebookGraphValidationRequest,
    config: FacebookGraphConfig,
) -> dict[str, Any]:
    http_request = urllib_request.Request(
        request.url,
        method=request.method,
        headers={
            "Authorization": f"Bearer {config.page_access_token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib_request.urlopen(http_request, timeout=request.timeout_seconds) as response:
            response_body = response.read().decode("utf-8") or "{}"
            payload = json.loads(response_body)
            payload["_response_status_code"] = getattr(response, "status", None)
            return payload
    except urllib_error.HTTPError as exc:
        response_text = _read_http_error_body(exc)
        raise FacebookGraphTransportError(
            f"Facebook Graph validation failed with HTTP {exc.code}: {response_text or exc.reason}",
            retryable=exc.code in {408, 425, 429, 500, 502, 503, 504},
            status_code=exc.code,
        ) from exc
    except urllib_error.URLError as exc:
        raise FacebookGraphTransportError(
            f"Facebook Graph validation request failed: {exc.reason}",
            retryable=True,
        ) from exc
    except json.JSONDecodeError as exc:
        raise FacebookGraphTransportError("Facebook Graph validation response was not valid JSON.") from exc


def _read_http_error_body(exc: urllib_error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8")
    except Exception:
        return ""
    return clean_text(body)


def _resolve_timestamp(value: str | None) -> str:
    if value:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()


def _iso_to_unix_timestamp(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
