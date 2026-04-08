from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import re
import string
from typing import Protocol

from ai_layer.openai_provider import (
    OpenAiPromptRequest,
    OpenAiProviderConfig,
    OpenAiResponseCreator,
    request_openai_output,
)
from source_engine.cleaner import clean_text, word_count
from source_engine.models import SourceItem

from content_engine.formatting import derive_subject_anchor, evaluate_draft_against_source
from content_engine.models import AiAssistanceRecord, DraftRecord
from content_engine.templates import get_blog_template_contract, validate_template_contract_for_source_item


ALLOWED_MICRO_SKILLS = frozenset(
    {
        "generate_headline_variants",
        "generate_short_intro",
        "generate_excerpt",
    }
)
CONTENT_AFFECTING_MICRO_SKILLS = frozenset({"generate_short_intro"})
HEADLINE_VARIANT_COUNT = 3
HEADLINE_MIN_VARIANTS = 2
HEADLINE_MAX_VARIANTS = 5
INTRO_MIN_WORDS = 40
INTRO_MAX_WORDS = 90
EXCERPT_MIN_WORDS = 20
EXCERPT_MAX_WORDS = 50
HEADLINE_MIN_WORDS = 4
HEADLINE_MAX_WORDS = 16
HEADLINE_TOKEN_RE = re.compile(r"[a-z0-9']+")
HOW_TO_SECOND_LIFE_RE = re.compile(r"^How To Give (?P<object>.+?) A Second Life$", re.IGNORECASE)
AVOIDANCE_LIST_RE = re.compile(
    r"^The (?:Only )?\d+ Foods? (?P<person>.+?) Thinks Twice About Eating$",
    re.IGNORECASE,
)
HEADLINE_REJECT_PATTERNS = (
    re.compile(r"\b(?:why|what|how)\s+to\b", re.IGNORECASE),
    re.compile(r"\bmatters in the kitchen\b", re.IGNORECASE),
)
HEADLINE_REJECT_TERMS = frozenset(
    {
        "secret",
        "shocking",
        "must know",
        "you won't believe",
        "best ever",
    }
)
OPENAI_RETRY_ATTEMPTS = 2
OPENAI_MAX_HEADLINE_OUTPUT_TOKENS = 220
OPENAI_MAX_INTRO_OUTPUT_TOKENS = 220
OPENAI_MAX_EXCERPT_OUTPUT_TOKENS = 180
HEADLINE_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "at",
        "be",
        "for",
        "from",
        "how",
        "in",
        "into",
        "is",
        "it",
        "its",
        "more",
        "of",
        "on",
        "or",
        "than",
        "that",
        "the",
        "this",
        "to",
        "what",
        "why",
        "with",
        "your",
    }
)


class MicroSkillProvider(Protocol):
    provider_label: str
    records_ai_usage: bool

    def generate_headline_variants(
        self,
        draft: DraftRecord,
        source_item: SourceItem,
        desired_count: int,
    ) -> list[str]: ...

    def generate_short_intro(
        self,
        draft: DraftRecord,
        source_item: SourceItem,
        min_words: int,
        max_words: int,
    ) -> str: ...

    def generate_excerpt(
        self,
        draft: DraftRecord,
        source_item: SourceItem,
        min_words: int,
        max_words: int,
    ) -> str: ...


@dataclass(frozen=True)
class ProviderCallMetadata:
    ai_used: bool
    model_label: str | None = None
    fallback_reason: str | None = None


@dataclass(frozen=True)
class HeuristicMicroSkillProvider:
    provider_label: str = "heuristic-v1"
    records_ai_usage: bool = False

    def generate_headline_variants(
        self,
        draft: DraftRecord,
        source_item: SourceItem,
        desired_count: int,
    ) -> list[str]:
        return _fallback_headline_variants(draft, source_item, desired_count)

    def generate_short_intro(
        self,
        draft: DraftRecord,
        source_item: SourceItem,
        min_words: int,
        max_words: int,
    ) -> str:
        return _normalize_intro_value(draft.intro_text, min_words=min_words, max_words=max_words)

    def generate_excerpt(
        self,
        draft: DraftRecord,
        source_item: SourceItem,
        min_words: int,
        max_words: int,
    ) -> str:
        base = draft.excerpt or draft.intro_text or source_item.raw_summary or source_item.raw_title
        return _normalize_excerpt_value(base, min_words=min_words, max_words=max_words)


class OpenAiMicroSkillProvider:
    records_ai_usage = True

    def __init__(
        self,
        config: OpenAiProviderConfig,
        *,
        response_creator: OpenAiResponseCreator | None = None,
        heuristic_provider: HeuristicMicroSkillProvider | None = None,
    ) -> None:
        self.config = config
        self.provider_label = config.model
        self._response_creator = response_creator
        self._heuristic_provider = heuristic_provider or HeuristicMicroSkillProvider()
        self._last_call_metadata: ProviderCallMetadata | None = None

    def consume_last_call_metadata(self) -> ProviderCallMetadata | None:
        metadata = self._last_call_metadata
        self._last_call_metadata = None
        return metadata

    def generate_headline_variants(
        self,
        draft: DraftRecord,
        source_item: SourceItem,
        desired_count: int,
    ) -> list[str]:
        request = _build_headline_prompt_request(draft, source_item, desired_count=desired_count)
        last_error: str | None = None
        for attempt in range(OPENAI_RETRY_ATTEMPTS):
            active_request = request if attempt == 0 else _build_retry_prompt_request(request)
            try:
                payload = _request_openai_json_payload(
                    active_request,
                    self.config,
                    response_creator=self._response_creator,
                )
                values = payload.get("headline_variants")
                if not isinstance(values, list):
                    raise ValueError("OpenAI headline response must contain a headline_variants list.")
                variants = [clean_text(str(value)) for value in values if clean_text(str(value))]
                normalized = _normalize_headline_variants(variants, draft, source_item)
                if len(normalized) >= HEADLINE_MIN_VARIANTS:
                    self._last_call_metadata = ProviderCallMetadata(
                        ai_used=True,
                        model_label=self.provider_label,
                    )
                    return variants
                last_error = "OpenAI headline variants did not meet the current headline quality bounds."
            except Exception as exc:
                last_error = str(exc)
        self._last_call_metadata = ProviderCallMetadata(
            ai_used=False,
            fallback_reason=f"generate_headline_variants fell back to heuristic provider: {last_error}",
        )
        return self._heuristic_provider.generate_headline_variants(draft, source_item, desired_count)

    def generate_short_intro(
        self,
        draft: DraftRecord,
        source_item: SourceItem,
        min_words: int,
        max_words: int,
    ) -> str:
        request = _build_intro_prompt_request(
            draft,
            source_item,
            min_words=min_words,
            max_words=max_words,
        )
        last_error: str | None = None
        for attempt in range(OPENAI_RETRY_ATTEMPTS):
            active_request = request if attempt == 0 else _build_retry_prompt_request(request)
            try:
                payload = _request_openai_json_payload(
                    active_request,
                    self.config,
                    response_creator=self._response_creator,
                )
                intro_text = clean_text(str(payload.get("intro_text", "") or ""))
                intro_word_count = word_count(intro_text)
                if intro_text and min_words <= intro_word_count <= max_words:
                    self._last_call_metadata = ProviderCallMetadata(
                        ai_used=True,
                        model_label=self.provider_label,
                    )
                    return intro_text
                last_error = "OpenAI intro output did not stay within the required intro bounds."
            except Exception as exc:
                last_error = str(exc)
        self._last_call_metadata = ProviderCallMetadata(
            ai_used=False,
            fallback_reason=f"generate_short_intro fell back to heuristic provider: {last_error}",
        )
        return self._heuristic_provider.generate_short_intro(draft, source_item, min_words, max_words)

    def generate_excerpt(
        self,
        draft: DraftRecord,
        source_item: SourceItem,
        min_words: int,
        max_words: int,
    ) -> str:
        request = _build_excerpt_prompt_request(
            draft,
            source_item,
            min_words=min_words,
            max_words=max_words,
        )
        last_error: str | None = None
        for attempt in range(OPENAI_RETRY_ATTEMPTS):
            active_request = request if attempt == 0 else _build_retry_prompt_request(request)
            try:
                payload = _request_openai_json_payload(
                    active_request,
                    self.config,
                    response_creator=self._response_creator,
                )
                excerpt_text = clean_text(str(payload.get("excerpt_text", "") or ""))
                excerpt_word_count = word_count(excerpt_text)
                if excerpt_text and min_words <= excerpt_word_count <= max_words:
                    self._last_call_metadata = ProviderCallMetadata(
                        ai_used=True,
                        model_label=self.provider_label,
                    )
                    return excerpt_text
                last_error = "OpenAI excerpt output did not stay within the required excerpt bounds."
            except Exception as exc:
                last_error = str(exc)
        self._last_call_metadata = ProviderCallMetadata(
            ai_used=False,
            fallback_reason=f"generate_excerpt fell back to heuristic provider: {last_error}",
        )
        return self._heuristic_provider.generate_excerpt(draft, source_item, min_words, max_words)


def apply_micro_skills(
    draft: DraftRecord,
    source_item: SourceItem,
    requested_skills: list[str] | tuple[str, ...],
    provider: MicroSkillProvider | None = None,
    created_at: str | None = None,
    fallback_events: list[str] | None = None,
) -> DraftRecord:
    active_provider = provider or HeuristicMicroSkillProvider()
    _validate_requested_skills(requested_skills)

    updated_draft = deepcopy(draft)
    timestamp = _resolve_timestamp(created_at)
    contract = validate_template_contract_for_source_item(
        source_item,
        get_blog_template_contract(draft.template_id),
    )
    content_affecting_change = False
    intro_min_words, intro_max_words = _intro_word_bounds(contract)

    for skill_name in requested_skills:
        if skill_name == "generate_headline_variants":
            generated = active_provider.generate_headline_variants(updated_draft, source_item, HEADLINE_VARIANT_COUNT)
            call_metadata = _consume_provider_call_metadata(active_provider)
            variants = _normalize_headline_variants(generated, updated_draft, source_item)
            model_label = _resolve_model_label(active_provider, call_metadata)
            if len(variants) < HEADLINE_MIN_VARIANTS:
                variants = _fallback_headline_variants(updated_draft, source_item, HEADLINE_VARIANT_COUNT)
                if call_metadata is not None:
                    model_label = None
                fallback_reason = _resolve_fallback_reason(
                    call_metadata,
                    default_reason="generate_headline_variants fell back to heuristic provider because provider output did not meet headline quality bounds.",
                )
                _record_fallback_event(fallback_events, fallback_reason)
            else:
                _record_fallback_event(fallback_events, _resolve_fallback_reason(call_metadata))
            updated_draft.headline_variants = variants[:HEADLINE_MAX_VARIANTS]
            _append_ai_log(updated_draft, skill_name, "headline_variants", timestamp, model_label=model_label)
        elif skill_name == "generate_short_intro":
            if "intro" not in contract.required_slot_order:
                raise ValueError(
                    f"generate_short_intro is not supported for template {contract.template_id} because it has no intro slot."
                )
            previous_intro = updated_draft.intro_text
            generated = active_provider.generate_short_intro(
                updated_draft,
                source_item,
                intro_min_words,
                intro_max_words,
            )
            call_metadata = _consume_provider_call_metadata(active_provider)
            model_label = _resolve_model_label(active_provider, call_metadata)
            updated_draft.intro_text = _normalize_intro_value(
                generated or updated_draft.intro_text,
                min_words=intro_min_words,
                max_words=intro_max_words,
                fallback=updated_draft.intro_text,
            )
            if skill_name in CONTENT_AFFECTING_MICRO_SKILLS and updated_draft.intro_text != previous_intro:
                content_affecting_change = True
            if clean_text(generated) != clean_text(updated_draft.intro_text) and call_metadata and call_metadata.ai_used:
                model_label = None
                _record_fallback_event(
                    fallback_events,
                    "generate_short_intro fell back to bounded deterministic normalization after provider output missed the accepted intro contract.",
                )
            else:
                _record_fallback_event(fallback_events, _resolve_fallback_reason(call_metadata))
            _append_ai_log(updated_draft, skill_name, "intro_text", timestamp, model_label=model_label)
        elif skill_name == "generate_excerpt":
            generated = active_provider.generate_excerpt(
                updated_draft,
                source_item,
                EXCERPT_MIN_WORDS,
                EXCERPT_MAX_WORDS,
            )
            call_metadata = _consume_provider_call_metadata(active_provider)
            model_label = _resolve_model_label(active_provider, call_metadata)
            updated_draft.excerpt = _normalize_excerpt_value(
                generated or updated_draft.excerpt,
                min_words=EXCERPT_MIN_WORDS,
                max_words=EXCERPT_MAX_WORDS,
                fallback=updated_draft.excerpt or updated_draft.intro_text,
            )
            if clean_text(generated) != clean_text(updated_draft.excerpt) and call_metadata and call_metadata.ai_used:
                model_label = None
                _record_fallback_event(
                    fallback_events,
                    "generate_excerpt fell back to bounded deterministic normalization after provider output missed the accepted excerpt contract.",
                )
            else:
                _record_fallback_event(fallback_events, _resolve_fallback_reason(call_metadata))
            _append_ai_log(updated_draft, skill_name, "excerpt", timestamp, model_label=model_label)
        else:
            raise ValueError(f"Unsupported micro-skill: {skill_name}")

    updated_draft.updated_at = timestamp
    if contract.template_family == "food_fact_article" and not updated_draft.headline_variants:
        updated_draft.headline_variants = _fallback_headline_variants(updated_draft, source_item, HEADLINE_VARIANT_COUNT)
    if content_affecting_change:
        _refresh_post_edit_state(updated_draft, source_item, contract)
    return updated_draft


def _refresh_post_edit_state(
    draft: DraftRecord,
    source_item: SourceItem,
    template_contract,
) -> None:
    quality_result = evaluate_draft_against_source(
        draft,
        source_item,
        template_contract=template_contract,
    )
    draft.quality_gate_status = quality_result.quality_gate_status
    draft.quality_flags = list(quality_result.quality_flags)
    draft.derivative_risk_level = quality_result.derivative_risk_level
    draft.derivative_risk_notes = quality_result.derivative_risk_notes
    draft.approval_state = "pending_review"
    draft.workflow_state = "drafted"


def _intro_word_bounds(template_contract) -> tuple[int, int]:
    for guidance in template_contract.slot_guidance:
        if guidance.slot_key != "intro":
            continue
        min_words = guidance.soft_min_words or INTRO_MIN_WORDS
        max_words = guidance.soft_max_words or INTRO_MAX_WORDS
        return min_words, max_words
    return INTRO_MIN_WORDS, INTRO_MAX_WORDS


def _validate_requested_skills(requested_skills: list[str] | tuple[str, ...]) -> None:
    if not requested_skills:
        raise ValueError("At least one micro-skill must be requested.")
    invalid = [skill for skill in requested_skills if skill not in ALLOWED_MICRO_SKILLS]
    if invalid:
        raise ValueError(f"Unsupported micro-skill(s): {', '.join(sorted(invalid))}")


def _normalize_headline_variants(values: list[str], draft: DraftRecord, source_item: SourceItem) -> list[str]:
    anchor_tokens = _headline_anchor_tokens(draft, source_item)
    variants: list[str] = []
    for value in values:
        normalized = _normalize_line(value)
        if not normalized:
            continue
        if normalized == draft.headline_selected:
            continue
        if not _is_usable_headline_variant(normalized, anchor_tokens):
            continue
        if normalized not in variants:
            variants.append(normalized)
    return variants


def _normalize_intro_value(
    value: str,
    min_words: int,
    max_words: int,
    fallback: str | None = None,
) -> str:
    fallback_value = clean_text(fallback or value)
    normalized = clean_text(value)
    if not normalized:
        normalized = fallback_value
    if word_count(normalized) < min_words:
        normalized = _expand_intro_to_minimum(normalized or fallback_value, min_words)
    normalized = _truncate_to_max_words(normalized, max_words)
    if word_count(normalized) < min_words:
        normalized = _expand_intro_to_minimum(fallback_value or normalized, min_words)
    return normalized


def _normalize_excerpt_value(
    value: str,
    min_words: int,
    max_words: int,
    fallback: str | None = None,
) -> str:
    candidate = clean_text(value)
    fallback_value = clean_text(fallback or value)
    if not candidate:
        candidate = fallback_value
    if word_count(candidate) < min_words:
        candidate = _expand_excerpt_to_minimum(candidate or fallback_value, min_words)
    candidate = _truncate_to_max_words(candidate, max_words)
    if word_count(candidate) < min_words:
        candidate = _expand_excerpt_to_minimum(fallback_value or candidate, min_words)
    return candidate


def _fallback_headline_variants(draft: DraftRecord, source_item: SourceItem, desired_count: int) -> list[str]:
    title = clean_text(draft.headline_selected or source_item.raw_title)
    subject = _headline_subject_label(title, source_item)
    patterns = _headline_patterns_for_title(title, subject)
    normalized = _normalize_headline_variants(list(patterns), draft, source_item)
    if len(normalized) < HEADLINE_MIN_VARIANTS:
        normalized = _normalize_headline_variants(_generic_headline_patterns(subject), draft, source_item)
    if len(normalized) < HEADLINE_MIN_VARIANTS:
        fallback_subject = _headline_case(_headline_stem(title))
        normalized = _normalize_headline_variants(_generic_headline_patterns(fallback_subject), draft, source_item)
    return normalized[: max(desired_count, HEADLINE_MIN_VARIANTS)]


def _headline_stem(title: str) -> str:
    for prefix in ("Why ", "What ", "How ", "When ", "Where "):
        if title.startswith(prefix):
            return title[len(prefix) :]
    return title


def _strip_terminal_phrase(value: str, suffixes: tuple[str, ...]) -> str:
    for suffix in suffixes:
        if value.endswith(suffix):
            return value[: -len(suffix)].strip()
    return value


def _headline_patterns_for_title(title: str, subject: str) -> list[str]:
    second_life_match = HOW_TO_SECOND_LIFE_RE.match(title)
    if second_life_match:
        object_label = clean_text(second_life_match.group("object"))
        return [
            f"Why {object_label} Is Worth Saving",
            f"A Better Second Use For {object_label}",
            f"How {object_label} Can Be Reused",
            f"What To Know About Reusing {object_label}",
        ]

    avoidance_match = AVOIDANCE_LIST_RE.match(title)
    if avoidance_match:
        person_label = clean_text(avoidance_match.group("person"))
        return [
            f"Which Foods {person_label} Avoids",
            f"Why {person_label} Still Skips Certain Foods",
            f"A Clearer Look At The Foods {person_label} Avoids",
        ]

    if title.startswith("Why "):
        stem = clean_text(title[4:])
        work_base = _strip_terminal_phrase(stem, (" Works", " Work"))
        patterns = [
            f"The Pattern Behind {subject}",
            f"What To Know About {subject}",
            f"A Clearer Look At {subject}",
        ]
        if work_base and work_base != stem:
            patterns.insert(0, f"What Makes {work_base} Work")
        return patterns

    if title.startswith("What "):
        return [
            f"The Short Answer About {subject}",
            f"What To Know About {subject}",
            f"A Clearer Look At {subject}",
        ]

    if title.startswith("How To "):
        return [
            f"What To Know About {subject}",
            f"A Practical Look At {subject}",
            f"How {subject} Can Be Used More Effectively",
        ]

    return _generic_headline_patterns(subject)


def _generic_headline_patterns(subject: str) -> list[str]:
    return [
        f"What To Know About {subject}",
        f"A Clearer Look At {subject}",
        f"Why {subject} Stands Out",
    ]


def _headline_subject_label(title: str, source_item: SourceItem) -> str:
    title_subject = _headline_title_subject(title)
    if title_subject:
        return title_subject

    derived_subject = clean_text(derive_subject_anchor(source_item))
    if derived_subject:
        return _headline_case(derived_subject)

    stem = clean_text(_headline_stem(title))
    if stem:
        return _headline_case(stem)
    return "This Food Topic"


def _headline_title_subject(title: str) -> str:
    second_life_match = HOW_TO_SECOND_LIFE_RE.match(title)
    if second_life_match:
        return _headline_case(clean_text(second_life_match.group("object")))

    for prefix in ("Why ", "What ", "How "):
        if title.startswith(prefix):
            stem = clean_text(title[len(prefix) :])
            stem = _strip_terminal_phrase(stem, (" Works", " Work"))
            if stem:
                return _headline_case(stem)
    return ""


def _headline_case(value: str) -> str:
    cleaned = clean_text(value)
    if not cleaned:
        return ""
    if cleaned == cleaned.lower():
        return string.capwords(cleaned)
    return cleaned


def _headline_anchor_tokens(draft: DraftRecord, source_item: SourceItem) -> set[str]:
    subject = _headline_subject_label(clean_text(draft.headline_selected or source_item.raw_title), source_item)
    tokens = _meaningful_headline_tokens(subject)
    if tokens:
        return tokens
    return _meaningful_headline_tokens(draft.headline_selected or source_item.raw_title)


def _is_usable_headline_variant(value: str, anchor_tokens: set[str]) -> bool:
    lowered = clean_text(value).lower()
    if word_count(value) < HEADLINE_MIN_WORDS or word_count(value) > HEADLINE_MAX_WORDS:
        return False
    if any(term in lowered for term in HEADLINE_REJECT_TERMS):
        return False
    if any(pattern.search(value) for pattern in HEADLINE_REJECT_PATTERNS):
        return False

    variant_tokens = _meaningful_headline_tokens(value)
    if not variant_tokens:
        return False
    if anchor_tokens and not (variant_tokens & anchor_tokens):
        return False
    return True


def _meaningful_headline_tokens(value: str) -> set[str]:
    tokens: set[str] = set()
    for token in HEADLINE_TOKEN_RE.findall(clean_text(value).lower()):
        if len(token) < 3:
            continue
        if token in HEADLINE_STOPWORDS:
            continue
        tokens.add(token)
    return tokens


def _expand_intro_to_minimum(value: str, min_words: int) -> str:
    base = clean_text(value)
    sentences = [
        base,
        "The goal is to keep the wording useful, answer-first, and easy to scan on mobile without widening the article scope.",
    ]
    combined = " ".join(sentence for sentence in sentences if sentence)
    if word_count(combined) < min_words:
        combined += " This keeps the draft aligned with the source while still giving review a cleaner starting point."
    return _truncate_to_max_words(combined, INTRO_MAX_WORDS)


def _expand_excerpt_to_minimum(value: str, min_words: int) -> str:
    base = clean_text(value)
    if word_count(base) >= min_words:
        return base
    combined = (
        f"{base} This short summary keeps the main point visible without turning the excerpt into a new article."
    ).strip()
    return _truncate_to_max_words(combined, EXCERPT_MAX_WORDS)


def _truncate_to_max_words(value: str, max_words: int) -> str:
    words = clean_text(value).split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]).strip() + "..."


def _normalize_line(value: str) -> str:
    return clean_text(value)


def _append_ai_log(
    draft: DraftRecord,
    skill_name: str,
    target_field: str,
    created_at: str,
    *,
    model_label: str | None,
) -> None:
    if not model_label:
        return
    draft.ai_assistance_log.append(
        AiAssistanceRecord(
            skill_name=skill_name,
            target_field=target_field,
            model_label=model_label,
            created_at=created_at,
        )
    )


def _consume_provider_call_metadata(provider: MicroSkillProvider) -> ProviderCallMetadata | None:
    consume = getattr(provider, "consume_last_call_metadata", None)
    if callable(consume):
        return consume()
    return None


def _resolve_model_label(
    provider: MicroSkillProvider,
    call_metadata: ProviderCallMetadata | None,
) -> str | None:
    if call_metadata is not None:
        return call_metadata.model_label if call_metadata.ai_used else None
    if getattr(provider, "records_ai_usage", False):
        return getattr(provider, "provider_label", None)
    return None


def _resolve_fallback_reason(
    call_metadata: ProviderCallMetadata | None,
    *,
    default_reason: str | None = None,
) -> str | None:
    if call_metadata and call_metadata.fallback_reason:
        return call_metadata.fallback_reason
    return default_reason


def _record_fallback_event(fallback_events: list[str] | None, fallback_reason: str | None) -> None:
    if fallback_events is None or not fallback_reason:
        return
    if fallback_reason not in fallback_events:
        fallback_events.append(fallback_reason)


def _build_headline_prompt_request(
    draft: DraftRecord,
    source_item: SourceItem,
    *,
    desired_count: int,
) -> OpenAiPromptRequest:
    instructions = (
        "You are refining bounded editorial headline variants for a food-content workflow. "
        "Return only valid JSON with one key named headline_variants containing 2 to 5 standalone headline strings. "
        "Keep subject-anchor relevance, avoid clicky or misleading language, avoid weak 'you won't believe' phrasing, "
        "and do not include commentary or markdown."
    )
    input_text = json.dumps(
        {
            "target_field": "headline_variants",
            "selected_headline": draft.headline_selected,
            "source_title": source_item.raw_title,
            "template_family": draft.template_family,
            "desired_count": desired_count,
            "prohibited_patterns": sorted(HEADLINE_REJECT_TERMS),
        },
        sort_keys=True,
    )
    return OpenAiPromptRequest(
        task_name="generate_headline_variants",
        instructions=instructions,
        input_text=input_text,
        max_output_tokens=OPENAI_MAX_HEADLINE_OUTPUT_TOKENS,
    )


def _build_intro_prompt_request(
    draft: DraftRecord,
    source_item: SourceItem,
    *,
    min_words: int,
    max_words: int,
) -> OpenAiPromptRequest:
    instructions = (
        "You are refining one answer-first blog intro for a bounded content workflow. "
        "Return only valid JSON with one key named intro_text. "
        "Stay within the requested word bounds, do not add unsupported facts, keep the framing answer-first, "
        "and do not expand into a free-form article."
    )
    input_text = json.dumps(
        {
            "target_field": "intro_text",
            "selected_headline": draft.headline_selected,
            "template_id": draft.template_id,
            "template_family": draft.template_family,
            "tone_notes": ["answer_first", "clean", "mobile_friendly"],
            "intro_bounds": {"min_words": min_words, "max_words": max_words},
            "source_lineage": {
                "source_title": source_item.raw_title,
                "source_summary": source_item.raw_summary,
                "source_url": source_item.source_url,
            },
            "draft_context": {
                "intro_text": draft.intro_text,
                "excerpt": draft.excerpt,
                "section_context": _draft_section_context(draft),
            },
        },
        sort_keys=True,
    )
    return OpenAiPromptRequest(
        task_name="generate_short_intro",
        instructions=instructions,
        input_text=input_text,
        max_output_tokens=OPENAI_MAX_INTRO_OUTPUT_TOKENS,
    )


def _build_excerpt_prompt_request(
    draft: DraftRecord,
    source_item: SourceItem,
    *,
    min_words: int,
    max_words: int,
) -> OpenAiPromptRequest:
    instructions = (
        "You are refining one bounded blog excerpt. "
        "Return only valid JSON with one key named excerpt_text. "
        "Stay summary-like instead of promotional, remain within the requested word bounds, and do not add unsupported claims."
    )
    input_text = json.dumps(
        {
            "target_field": "excerpt",
            "selected_headline": draft.headline_selected,
            "template_family": draft.template_family,
            "excerpt_bounds": {"min_words": min_words, "max_words": max_words},
            "tone_notes": ["summary_like", "non_promotional", "mobile_friendly"],
            "source_lineage": {
                "source_title": source_item.raw_title,
                "source_summary": source_item.raw_summary,
            },
            "draft_context": {
                "intro_text": draft.intro_text,
                "excerpt": draft.excerpt,
                "section_context": _draft_section_context(draft),
            },
        },
        sort_keys=True,
    )
    return OpenAiPromptRequest(
        task_name="generate_excerpt",
        instructions=instructions,
        input_text=input_text,
        max_output_tokens=OPENAI_MAX_EXCERPT_OUTPUT_TOKENS,
    )


def _draft_section_context(draft: DraftRecord) -> list[dict[str, str]]:
    context: list[dict[str, str]] = []
    for section in draft.sections[:3]:
        primary_text = ""
        if section.body_blocks:
            primary_text = clean_text(section.body_blocks[0])
        elif section.bullet_points:
            primary_text = clean_text(section.bullet_points[0])
        context.append(
            {
                "section_key": section.section_key,
                "section_label": section.section_label,
                "primary_text": primary_text,
            }
        )
    return context


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
        raise ValueError(f"OpenAI returned invalid JSON for task {request.task_name}.") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"OpenAI returned an invalid JSON root for task {request.task_name}.")
    return payload


def _build_retry_prompt_request(request: OpenAiPromptRequest) -> OpenAiPromptRequest:
    return OpenAiPromptRequest(
        task_name=request.task_name,
        instructions=request.instructions
        + " Retry once and return only valid JSON that exactly matches the requested key and bounds.",
        input_text=request.input_text,
        max_output_tokens=request.max_output_tokens,
    )


def _resolve_timestamp(created_at: str | None) -> str:
    if created_at:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
