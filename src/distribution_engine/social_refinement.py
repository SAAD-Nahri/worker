from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
import json

from ai_layer.openai_provider import (
    OpenAiPromptRequest,
    OpenAiProviderConfig,
    OpenAiResponseCreator,
    request_openai_output,
)
from content_engine.models import AiAssistanceRecord, DraftRecord
from distribution_engine.facebook import validate_social_package_shape
from distribution_engine.models import BlogPublishRecord, SocialPackageRecord
from source_engine.cleaner import clean_text


SOCIAL_REFINEMENT_SKILL_NAME = "refine_social_package_variants"
SOCIAL_REFINEMENT_TARGET_FIELD = "variant_options"
OPENAI_SOCIAL_RETRY_ATTEMPTS = 2
OPENAI_SOCIAL_MAX_OUTPUT_TOKENS = 320


@dataclass(frozen=True)
class SocialPackageRefinementResult:
    updated_package: SocialPackageRecord
    added_variant_labels: tuple[str, ...]
    provider_label: str | None
    fallback_reason: str | None = None


class OpenAiSocialPackageRefiner:
    def __init__(
        self,
        config: OpenAiProviderConfig,
        *,
        response_creator: OpenAiResponseCreator | None = None,
    ) -> None:
        self.config = config
        self.provider_label = config.model
        self._response_creator = response_creator

    def generate_variant_payloads(
        self,
        social_package: SocialPackageRecord,
        draft: DraftRecord,
        *,
        blog_publish_record: BlogPublishRecord | None,
        desired_variant_count: int,
    ) -> tuple[list[dict[str, str]], str | None]:
        request = _build_social_refinement_prompt_request(
            social_package,
            draft,
            blog_publish_record=blog_publish_record,
            desired_variant_count=desired_variant_count,
        )
        last_error: str | None = None
        for attempt in range(OPENAI_SOCIAL_RETRY_ATTEMPTS):
            active_request = request if attempt == 0 else _build_retry_prompt_request(request)
            try:
                payload = _request_openai_json_payload(
                    active_request,
                    self.config,
                    response_creator=self._response_creator,
                )
                variants = payload.get("variants")
                if not isinstance(variants, list):
                    raise ValueError("OpenAI social refinement response must contain a variants list.")
                normalized = _normalize_variant_payloads(
                    variants,
                    package_template_id=social_package.package_template_id,
                )
                if normalized:
                    return normalized[:desired_variant_count], None
                last_error = "OpenAI social refinement did not produce any valid package variants."
            except Exception as exc:
                last_error = str(exc)
        return [], last_error or "OpenAI social refinement failed."


def refine_social_package_with_openai(
    social_package: SocialPackageRecord,
    draft: DraftRecord,
    *,
    config: OpenAiProviderConfig,
    blog_publish_record: BlogPublishRecord | None = None,
    desired_variant_count: int = 2,
    response_creator: OpenAiResponseCreator | None = None,
    created_at: str | None = None,
) -> SocialPackageRefinementResult:
    normalized_count = max(1, min(int(desired_variant_count), 2))
    refiner = OpenAiSocialPackageRefiner(config, response_creator=response_creator)
    variants, fallback_reason = refiner.generate_variant_payloads(
        social_package,
        draft,
        blog_publish_record=blog_publish_record,
        desired_variant_count=normalized_count,
    )
    if not variants:
        return SocialPackageRefinementResult(
            updated_package=social_package,
            added_variant_labels=(),
            provider_label=None,
            fallback_reason=fallback_reason,
        )

    timestamp = _resolve_timestamp(created_at)
    existing_signatures = {
        _variant_signature(option)
        for option in getattr(social_package, "variant_options", []) or []
        if _variant_signature(option)
    }
    existing_labels = {
        clean_text(str(option.get("label", "") or ""))
        for option in getattr(social_package, "variant_options", []) or []
    }
    added_variants: list[dict[str, str]] = []
    next_index = 1
    for variant in variants:
        signature = _variant_signature(variant)
        if not signature or signature in existing_signatures:
            continue
        while f"openai_refined_{next_index}_v1" in existing_labels:
            next_index += 1
        label = f"openai_refined_{next_index}_v1"
        existing_labels.add(label)
        existing_signatures.add(signature)
        added_variants.append(
            {
                "label": label,
                "hook_text": variant["hook_text"],
                "caption_text": variant["caption_text"],
                "comment_cta_text": variant["comment_cta_text"],
            }
        )
        next_index += 1

    if not added_variants:
        return SocialPackageRefinementResult(
            updated_package=social_package,
            added_variant_labels=(),
            provider_label=None,
            fallback_reason="OpenAI social refinement only produced duplicate or invalid variants.",
        )

    updated_package = deepcopy(social_package)
    updated_package.variant_options = list(updated_package.variant_options) + added_variants
    updated_package.ai_assistance_log = list(updated_package.ai_assistance_log) + [
        AiAssistanceRecord(
            skill_name=SOCIAL_REFINEMENT_SKILL_NAME,
            target_field=SOCIAL_REFINEMENT_TARGET_FIELD,
            model_label=config.model,
            created_at=timestamp,
        )
    ]
    updated_package.updated_at = timestamp
    return SocialPackageRefinementResult(
        updated_package=updated_package,
        added_variant_labels=tuple(variant["label"] for variant in added_variants),
        provider_label=config.model,
        fallback_reason=None,
    )


def _build_social_refinement_prompt_request(
    social_package: SocialPackageRecord,
    draft: DraftRecord,
    *,
    blog_publish_record: BlogPublishRecord | None,
    desired_variant_count: int,
) -> OpenAiPromptRequest:
    instructions = (
        "You are refining Facebook package variants for a bounded approval workflow. "
        "Return only valid JSON with one key named variants containing 1 or 2 objects. "
        "Each object must include hook_text, caption_text, and comment_cta_text. "
        "Keep the output practical, non-clicky, source-grounded, and within the provided word bounds. "
        "Do not add markdown, commentary, hashtags, or unsupported claims."
    )
    input_text = json.dumps(
        {
            "target_field": SOCIAL_REFINEMENT_TARGET_FIELD,
            "desired_variant_count": desired_variant_count,
            "package_template_id": social_package.package_template_id,
            "comment_template_id": social_package.comment_template_id,
            "current_package": {
                "hook_text": social_package.hook_text,
                "caption_text": social_package.caption_text,
                "comment_cta_text": social_package.comment_cta_text,
                "selected_variant_label": social_package.selected_variant_label,
            },
            "current_variant_labels": [
                clean_text(str(option.get("label", "") or ""))
                for option in getattr(social_package, "variant_options", []) or []
                if clean_text(str(option.get("label", "") or ""))
            ],
            "bounds": _package_bounds_description(social_package.package_template_id),
            "draft_context": {
                "headline_selected": draft.headline_selected,
                "excerpt": draft.excerpt,
                "template_id": draft.template_id,
                "template_family": draft.template_family,
                "category": draft.category,
            },
            "blog_context": {
                "blog_publish_id": blog_publish_record.blog_publish_id if blog_publish_record else None,
                "wordpress_title": blog_publish_record.wordpress_title if blog_publish_record else None,
                "wordpress_post_url": blog_publish_record.wordpress_post_url if blog_publish_record else None,
            },
            "tone_notes": ["facebook_page", "clear", "review_safe", "non_clicky"],
            "prohibited_patterns": ["misleading claims", "you won't believe", "unsupported facts", "hashtags"],
        },
        sort_keys=True,
    )
    return OpenAiPromptRequest(
        task_name=SOCIAL_REFINEMENT_SKILL_NAME,
        instructions=instructions,
        input_text=input_text,
        max_output_tokens=OPENAI_SOCIAL_MAX_OUTPUT_TOKENS,
    )


def _package_bounds_description(package_template_id: str) -> dict[str, object]:
    if package_template_id == "fb_curiosity_hook_v1":
        return {
            "hook_words": {"min": 8, "max": 18},
            "hook_plus_caption_words": {"min": 8, "max": 34},
            "comment_cta_words_max": 20,
        }
    if package_template_id == "fb_soft_cta_post_v1":
        return {
            "hook_plus_caption_words": {"min": 25, "max": 55},
            "comment_cta_words_max": 20,
        }
    return {
        "hook_plus_caption_words": {"min": 20, "max": 45},
        "comment_cta_words_max": 20,
    }


def _request_openai_json_payload(
    request: OpenAiPromptRequest,
    config: OpenAiProviderConfig,
    *,
    response_creator: OpenAiResponseCreator | None = None,
) -> dict[str, object]:
    output_text = request_openai_output(
        request,
        config,
        response_creator=response_creator,
    )
    try:
        payload = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError("OpenAI social refinement returned invalid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("OpenAI social refinement returned an invalid JSON root.")
    return payload


def _build_retry_prompt_request(request: OpenAiPromptRequest) -> OpenAiPromptRequest:
    return OpenAiPromptRequest(
        task_name=request.task_name,
        instructions=request.instructions
        + " Retry once and return only valid JSON with complete variant objects that respect all bounds.",
        input_text=request.input_text,
        max_output_tokens=request.max_output_tokens,
    )


def _normalize_variant_payloads(
    variants: list[object],
    *,
    package_template_id: str,
) -> list[dict[str, str]]:
    normalized_variants: list[dict[str, str]] = []
    seen_signatures: set[tuple[str, str, str]] = set()
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        hook_text = clean_text(str(variant.get("hook_text", "") or ""))
        caption_text = clean_text(str(variant.get("caption_text", "") or ""))
        comment_cta_text = clean_text(str(variant.get("comment_cta_text", "") or ""))
        if not hook_text or not caption_text or not comment_cta_text:
            continue
        try:
            validate_social_package_shape(
                package_template_id,
                hook_text,
                caption_text,
                comment_cta_text,
            )
        except ValueError:
            continue
        signature = (hook_text, caption_text, comment_cta_text)
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        normalized_variants.append(
            {
                "hook_text": hook_text,
                "caption_text": caption_text,
                "comment_cta_text": comment_cta_text,
            }
        )
    return normalized_variants


def _variant_signature(variant: dict[str, str]) -> tuple[str, str, str] | None:
    hook_text = clean_text(str(variant.get("hook_text", "") or ""))
    caption_text = clean_text(str(variant.get("caption_text", "") or ""))
    comment_cta_text = clean_text(str(variant.get("comment_cta_text", "") or ""))
    if not hook_text or not caption_text or not comment_cta_text:
        return None
    return (hook_text, caption_text, comment_cta_text)


def _resolve_timestamp(created_at: str | None) -> str:
    if created_at:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
