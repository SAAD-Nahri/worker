from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
import re
import string
from typing import Protocol

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


def apply_micro_skills(
    draft: DraftRecord,
    source_item: SourceItem,
    requested_skills: list[str] | tuple[str, ...],
    provider: MicroSkillProvider | None = None,
    created_at: str | None = None,
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
            variants = _normalize_headline_variants(generated, updated_draft, source_item)
            if len(variants) < HEADLINE_MIN_VARIANTS:
                variants = _fallback_headline_variants(updated_draft, source_item, HEADLINE_VARIANT_COUNT)
            updated_draft.headline_variants = variants[:HEADLINE_MAX_VARIANTS]
            _append_ai_log(updated_draft, active_provider, skill_name, "headline_variants", timestamp)
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
            updated_draft.intro_text = _normalize_intro_value(
                generated or updated_draft.intro_text,
                min_words=intro_min_words,
                max_words=intro_max_words,
                fallback=updated_draft.intro_text,
            )
            if skill_name in CONTENT_AFFECTING_MICRO_SKILLS and updated_draft.intro_text != previous_intro:
                content_affecting_change = True
            _append_ai_log(updated_draft, active_provider, skill_name, "intro_text", timestamp)
        elif skill_name == "generate_excerpt":
            generated = active_provider.generate_excerpt(
                updated_draft,
                source_item,
                EXCERPT_MIN_WORDS,
                EXCERPT_MAX_WORDS,
            )
            updated_draft.excerpt = _normalize_excerpt_value(
                generated or updated_draft.excerpt,
                min_words=EXCERPT_MIN_WORDS,
                max_words=EXCERPT_MAX_WORDS,
                fallback=updated_draft.excerpt or updated_draft.intro_text,
            )
            _append_ai_log(updated_draft, active_provider, skill_name, "excerpt", timestamp)
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
    provider: MicroSkillProvider,
    skill_name: str,
    target_field: str,
    created_at: str,
) -> None:
    if not provider.records_ai_usage:
        return
    draft.ai_assistance_log.append(
        AiAssistanceRecord(
            skill_name=skill_name,
            target_field=target_field,
            model_label=provider.provider_label,
            created_at=created_at,
        )
    )


def _resolve_timestamp(created_at: str | None) -> str:
    if created_at:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
