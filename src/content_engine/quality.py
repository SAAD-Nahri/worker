from __future__ import annotations

import re

from source_engine.cleaner import clean_text, word_count
from source_engine.models import SourceItem

from content_engine.models import BlogTemplateContract, DraftQualityEvaluation, DraftRecord
from content_engine.taxonomy import ALLOWED_CATEGORIES
from content_engine.templates import get_blog_template_contract


MIN_USEFUL_DRAFT_WORDS = 120
TITLE_BLOCK_TERMS = (
    "cure",
    "cures",
    "prevent disease",
    "guaranteed",
    "miracle",
)
TITLE_REVIEW_TERMS = (
    "secret",
    "shocking",
    "you won't believe",
    "best ever",
    "must know",
)
CLAIM_BLOCK_PATTERNS = (
    re.compile(r"\b(cure|cures|heals)\b"),
    re.compile(r"\btreats?\b(?:\s+\w+){0,3}\s+\b(disease|illness|condition|pain|diabetes|cancer)\b"),
    re.compile(r"\bprevents?\b(?:\s+\w+){0,3}\s+\b(disease|illness|cancer)\b"),
    re.compile(r"\bguaranteed\b"),
)
CLAIM_REVIEW_TERMS = (
    "best",
    "healthiest",
    "unhealthiest",
    "superfood",
)
TOKEN_RE = re.compile(r"[a-z0-9']+")


def evaluate_draft_quality(
    draft: DraftRecord,
    source_item: SourceItem,
    template_contract: BlogTemplateContract | None = None,
    semantic_profile: dict[str, object] | None = None,
) -> DraftQualityEvaluation:
    contract = template_contract or get_blog_template_contract(draft.template_id)
    blocking_flags: list[str] = []
    review_flags: list[str] = []

    _evaluate_lineage(draft, blocking_flags)
    _evaluate_template_completeness(draft, contract, blocking_flags, review_flags)
    _evaluate_slot_guidance(draft, contract, review_flags)
    _evaluate_length_and_thinness(draft, contract, blocking_flags, review_flags)
    _evaluate_readability(draft, blocking_flags, review_flags)
    _evaluate_title_integrity(draft, blocking_flags, review_flags)
    derivative_level, derivative_notes = _evaluate_derivative_risk(draft, source_item, review_flags)
    _evaluate_claim_safety(draft, blocking_flags, review_flags)
    _evaluate_category_and_tags(draft, review_flags)
    _evaluate_semantic_profile(semantic_profile or {}, review_flags)

    if derivative_level == "high":
        blocking_flags.append("derivative_risk_high")
    elif derivative_level == "medium":
        review_flags.append("derivative_risk_medium")

    quality_flags = _dedupe_flags(blocking_flags + review_flags)
    if blocking_flags:
        status = "blocked"
    elif review_flags:
        status = "review_flag"
    else:
        status = "pass"

    return DraftQualityEvaluation(
        quality_gate_status=status,
        quality_flags=tuple(quality_flags),
        derivative_risk_level=derivative_level,
        derivative_risk_notes=derivative_notes,
    )


def _evaluate_lineage(draft: DraftRecord, blocking_flags: list[str]) -> None:
    required_values = {
        "source_item_id": draft.source_item_id,
        "source_id": draft.source_id,
        "source_url": draft.source_url,
        "source_title": draft.source_title,
        "template_id": draft.template_id,
    }
    for key, value in required_values.items():
        if not clean_text(value if isinstance(value, str) else ""):
            blocking_flags.append(f"missing_{key}")


def _evaluate_template_completeness(
    draft: DraftRecord,
    contract: BlogTemplateContract,
    blocking_flags: list[str],
    review_flags: list[str],
) -> None:
    section_keys = [section.section_key for section in draft.sections]
    expected_keys = list(contract.body_section_keys)

    if not draft.headline_selected.strip():
        blocking_flags.append("missing_headline")
    if "intro" in contract.required_slot_order and not draft.intro_text.strip():
        blocking_flags.append("missing_intro")

    if any(key not in section_keys for key in expected_keys):
        blocking_flags.append("missing_required_section")
        return

    if section_keys != expected_keys:
        review_flags.append("section_order_mismatch")

    for section in draft.sections:
        if section.section_key in contract.body_section_keys and not (section.body_blocks or section.bullet_points):
            blocking_flags.append("empty_required_section")
            break


def _evaluate_slot_guidance(
    draft: DraftRecord,
    contract: BlogTemplateContract,
    review_flags: list[str],
) -> None:
    section_by_key = {section.section_key: section for section in draft.sections}

    for guidance in contract.slot_guidance:
        slot_key = guidance.slot_key
        if slot_key == "intro":
            slot_word_count = word_count(draft.intro_text)
            bullet_count = 0
        elif slot_key == "related_read_bridge":
            if not draft.related_read_bridge:
                continue
            slot_word_count = word_count(draft.related_read_bridge)
            bullet_count = 0
        else:
            section = section_by_key.get(slot_key)
            if section is None:
                continue
            slot_word_count = _section_word_count(section)
            bullet_count = len([point for point in section.bullet_points if clean_text(point)])
            if guidance.requires_bullets and bullet_count == 0:
                review_flags.append(f"{slot_key}_bullet_shape_mismatch")

        if guidance.soft_min_words is not None and slot_word_count < guidance.soft_min_words:
            review_flags.append(f"{slot_key}_length_outside_target")
        if guidance.soft_max_words is not None and slot_word_count > guidance.soft_max_words:
            review_flags.append(f"{slot_key}_length_outside_target")

        if guidance.min_bullet_count is not None and bullet_count < guidance.min_bullet_count:
            review_flags.append(f"{slot_key}_bullet_count_outside_target")
        if guidance.max_bullet_count is not None and bullet_count > guidance.max_bullet_count:
            review_flags.append(f"{slot_key}_bullet_count_outside_target")

        if guidance.max_words_before_slot is not None:
            words_before_slot = _words_before_slot(draft, slot_key)
            if words_before_slot > guidance.max_words_before_slot:
                review_flags.append(f"{slot_key}_position_too_late")


def _evaluate_length_and_thinness(
    draft: DraftRecord,
    contract: BlogTemplateContract,
    blocking_flags: list[str],
    review_flags: list[str],
) -> None:
    total_words = _draft_body_word_count(draft)
    if total_words < MIN_USEFUL_DRAFT_WORDS:
        blocking_flags.append("draft_too_thin")
        return

    guidance = contract.target_length_guidance
    if total_words < guidance.soft_min or total_words > guidance.soft_max:
        review_flags.append("draft_length_outside_target")
    if total_words > 900:
        review_flags.append("draft_too_long")


def _evaluate_readability(
    draft: DraftRecord,
    blocking_flags: list[str],
    review_flags: list[str],
) -> None:
    long_paragraphs = 0
    for section in draft.sections:
        if section.position < 1 or not section.section_label.strip():
            blocking_flags.append("invalid_section_structure")
            return
        for paragraph in section.body_blocks:
            if word_count(paragraph) > 110:
                long_paragraphs += 1
                review_flags.append("paragraph_too_long")

    if long_paragraphs >= 2:
        blocking_flags.append("wall_of_text")


def _evaluate_title_integrity(
    draft: DraftRecord,
    blocking_flags: list[str],
    review_flags: list[str],
) -> None:
    lowered = clean_text(draft.headline_selected).lower()
    if any(term in lowered for term in TITLE_BLOCK_TERMS):
        blocking_flags.append("title_integrity_issue")
        return
    if any(term in lowered for term in TITLE_REVIEW_TERMS):
        review_flags.append("title_clicky")


def _evaluate_claim_safety(
    draft: DraftRecord,
    blocking_flags: list[str],
    review_flags: list[str],
) -> None:
    combined_text = " ".join(_draft_text_blocks(draft)).lower()
    if any(pattern.search(combined_text) for pattern in CLAIM_BLOCK_PATTERNS):
        blocking_flags.append("claim_safety_issue")
        return
    if any(term in combined_text for term in CLAIM_REVIEW_TERMS):
        review_flags.append("claim_tone_review")


def _evaluate_category_and_tags(draft: DraftRecord, review_flags: list[str]) -> None:
    if draft.category not in ALLOWED_CATEGORIES:
        review_flags.append("category_uncertain")
    if len(draft.tag_candidates) > 6:
        review_flags.append("too_many_tags")
    if any(" " in tag.strip() for tag in draft.tag_candidates):
        review_flags.append("tag_format_issue")


def _evaluate_semantic_profile(semantic_profile: dict[str, object], review_flags: list[str]) -> None:
    low_signal_topic_term_count = int(semantic_profile.get("low_signal_topic_term_count", 0) or 0)
    body_supported_topic_term_count = int(semantic_profile.get("body_supported_topic_term_count", 0) or 0)
    recipe_like_ratio = float(semantic_profile.get("recipe_like_paragraph_ratio", 0.0) or 0.0)
    noise_like_ratio = float(semantic_profile.get("noise_like_paragraph_ratio", 0.0) or 0.0)

    if low_signal_topic_term_count >= 2:
        review_flags.append("semantic_term_noise")
    if recipe_like_ratio >= 0.45:
        review_flags.append("source_context_recipe_heavy")
    if noise_like_ratio >= 0.3:
        review_flags.append("source_context_noisy")
    if low_signal_topic_term_count >= 1 and body_supported_topic_term_count <= 1:
        review_flags.append("anchor_title_mismatch")


def _evaluate_derivative_risk(
    draft: DraftRecord,
    source_item: SourceItem,
    review_flags: list[str],
) -> tuple[str, str]:
    source_tokens = _tokenize(source_item.raw_body_text or source_item.raw_summary)
    draft_tokens = _tokenize(" ".join(_draft_text_blocks(draft)))

    if not source_tokens or not draft_tokens:
        return "high", "Missing source or draft text for derivative-risk evaluation."

    if _shared_ngram_exists(source_tokens, draft_tokens, 12):
        return "high", "Detected obvious 12-plus word carryover from source phrasing."

    if _shared_ngram_exists(source_tokens, draft_tokens, 8):
        return "medium", "Detected repeated 8-plus word carryover from source phrasing."

    overlap_ratio = _token_overlap_ratio(source_tokens, draft_tokens)
    if overlap_ratio >= 0.6:
        return "medium", "Draft retains too much source vocabulary overlap for a comfortable pass."

    if overlap_ratio <= 0.35:
        return "low", "Draft wording appears sufficiently distinct from the source text."

    review_flags.append("derivative_risk_borderline")
    return "medium", "Transformation is meaningful but still closer to source wording than ideal."


def _draft_body_word_count(draft: DraftRecord) -> int:
    return word_count(" ".join(_draft_text_blocks(draft)))


def _section_word_count(section) -> int:
    return word_count(" ".join([*section.body_blocks, *section.bullet_points]))


def _words_before_slot(draft: DraftRecord, slot_key: str) -> int:
    words_before = 0
    if slot_key == "intro":
        return 0

    if draft.intro_text:
        words_before += word_count(draft.intro_text)

    for section in draft.sections:
        if section.section_key == slot_key:
            return words_before
        words_before += _section_word_count(section)

    if slot_key == "related_read_bridge":
        return words_before

    return words_before


def _draft_text_blocks(draft: DraftRecord) -> list[str]:
    blocks = [draft.intro_text]
    for section in draft.sections:
        blocks.extend(section.body_blocks)
        blocks.extend(section.bullet_points)
    if draft.related_read_bridge:
        blocks.append(draft.related_read_bridge)
    return [clean_text(block) for block in blocks if clean_text(block)]


def _tokenize(value: str) -> list[str]:
    return TOKEN_RE.findall(clean_text(value).lower())


def _shared_ngram_exists(source_tokens: list[str], draft_tokens: list[str], size: int) -> bool:
    if len(source_tokens) < size or len(draft_tokens) < size:
        return False

    source_ngrams = {tuple(source_tokens[index : index + size]) for index in range(len(source_tokens) - size + 1)}
    for index in range(len(draft_tokens) - size + 1):
        if tuple(draft_tokens[index : index + size]) in source_ngrams:
            return True
    return False


def _token_overlap_ratio(source_tokens: list[str], draft_tokens: list[str]) -> float:
    source_set = set(source_tokens)
    draft_set = set(draft_tokens)
    if not draft_set:
        return 1.0
    return len(source_set & draft_set) / len(draft_set)


def _dedupe_flags(flags: list[str]) -> list[str]:
    ordered: list[str] = []
    for flag in flags:
        if flag not in ordered:
            ordered.append(flag)
    return ordered
