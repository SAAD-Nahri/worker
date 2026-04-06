from __future__ import annotations

import re
from collections import Counter
import unicodedata

from source_engine.cleaner import clean_text, word_count
from source_engine.models import SourceItem

from content_engine.drafts import create_draft_skeleton
from content_engine.models import DraftEligibilityResult, DraftRecord
from content_engine.quality import evaluate_draft_quality
from content_engine.taxonomy import assign_category_and_tags
from content_engine.templates import (
    BlogTemplateContract,
    get_blog_template_contract,
    resolve_blog_template_contract,
)


MIN_ELIGIBLE_SOURCE_WORDS = 120
LEAD_PARAGRAPH_LIMIT = 4
LEAD_BODY_WORD_LIMIT = 260
PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
TITLE_SEGMENT_SPLIT_RE = re.compile(r"\s+(?:\u2014|\u2013|-)+\s+|[()\[\]:]+")
TOKEN_RE = re.compile(r"[a-z0-9']+")
MEASUREMENT_RE = re.compile(
    r"\b(?:\d+[/-]?\d*|¼|½|¾)\s*(?:tbsp|tsp|cups?|oz|ounces?|lbs?|pounds?|grams?|g|kg|ml|l|inch(?:es)?|cm)\b"
)
BULLET_SECTION_KEYS = {"supporting_points", "practical_points"}
STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "also",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "but",
    "by",
    "can",
    "could",
    "do",
    "does",
    "during",
    "each",
    "even",
    "for",
    "from",
    "get",
    "give",
    "gives",
    "had",
    "has",
    "have",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "it's",
    "its",
    "just",
    "less",
    "like",
    "look",
    "looks",
    "lot",
    "made",
    "make",
    "makes",
    "many",
    "more",
    "most",
    "much",
    "next",
    "not",
    "of",
    "often",
    "on",
    "one",
    "only",
    "or",
    "other",
    "our",
    "out",
    "over",
    "people",
    "same",
    "see",
    "several",
    "should",
    "simple",
    "small",
    "so",
    "some",
    "something",
    "still",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "thinks",
    "through",
    "time",
    "to",
    "too",
    "turns",
    "twice",
    "up",
    "us",
    "use",
    "useful",
    "using",
    "very",
    "want",
    "was",
    "way",
    "we",
    "what",
    "when",
    "where",
    "which",
    "while",
    "why",
    "with",
    "work",
    "works",
    "would",
    "you",
    "your",
    "you'll",
}
LOW_SIGNAL_TERMS = {
    "article",
    "aside",
    "behavior",
    "better",
    "bowl",
    "changes",
    "chef",
    "common",
    "confidence",
    "cooks",
    "cooking",
    "crazy",
    "different",
    "everyday",
    "exceptions",
    "fact",
    "facts",
    "famously",
    "food",
    "foods",
    "good",
    "great",
    "habit",
    "habits",
    "home",
    "kind",
    "kitchen",
    "lead",
    "main",
    "method",
    "minutes",
    "people",
    "plus",
    "prove",
    "practical",
    "question",
    "questions",
    "reason",
    "reliable",
    "result",
    "results",
    "short",
    "single",
    "summary",
    "somewhere",
    "story",
    "surprises",
    "thats",
    "thing",
    "things",
    "think",
    "take",
    "trick",
    "types",
    "underlying",
    "understand",
    "until",
    "visible",
    "eating",
    "open",
    "shift",
    "shifts",
}
BODY_NOISE_TERMS = {
    "add",
    "bake",
    "baking",
    "boil",
    "boiling",
    "broth",
    "butter",
    "cook",
    "cooked",
    "cooking",
    "cups",
    "dough",
    "egg",
    "eggs",
    "flour",
    "heat",
    "ingredients",
    "knead",
    "large",
    "loaf",
    "loaves",
    "medium",
    "milk",
    "oven",
    "pan",
    "pot",
    "recipe",
    "recipes",
    "serve",
    "serving",
    "sheet",
    "small",
    "simmer",
    "salt",
    "saucepan",
    "step",
    "steps",
    "stir",
    "sugar",
    "tablespoon",
    "tablespoons",
    "teaspoon",
    "teaspoons",
    "time",
    "water",
    "whisk",
    "yeast",
}
NOISE_PHRASES = (
    "we may receive a commission",
    "get our favorite recipes",
    "delivered to your inbox",
    "articles may contain affiliate links",
    "registration on or use of this site",
    "share your kitchen adventure",
)
ATTRIBUTION_HINTS = (
    "photo:",
    "food styling",
    "getty images",
    "props:",
    "shutterstock",
    "instagram",
    "facebook",
)
SUMMARY_NOISE_TERMS = {
    "catching",
    "draw",
    "famously",
    "gross",
    "line",
    "matt",
    "openminded",
    "photo",
    "prove",
    "somewhere",
    "styling",
    "taylor",
    "types",
    "weiner",
}
PROCEDURAL_START_TERMS = {
    "add",
    "arrange",
    "bake",
    "beat",
    "blend",
    "boil",
    "bring",
    "brush",
    "chop",
    "cook",
    "cover",
    "divide",
    "drain",
    "fill",
    "fold",
    "fry",
    "grease",
    "heat",
    "knead",
    "mix",
    "place",
    "position",
    "pour",
    "preheat",
    "reduce",
    "remove",
    "repeat",
    "return",
    "serve",
    "set",
    "soak",
    "sprinkle",
    "stir",
    "switch",
    "taste",
    "turn",
    "whisk",
}
PROCEDURAL_PREFIXES = (
    "photo:",
    "photo ",
    "ingredients",
    "time ",
    "yield ",
    "serves ",
)
NON_UNIQUE_DEDUPE_STATUSES = {
    "exact_duplicate",
    "near_duplicate",
    "angle_collision",
    "duplicate_blocked",
}


def evaluate_source_item_eligibility(source_item: SourceItem) -> DraftEligibilityResult:
    reasons: list[str] = []

    if not source_item.item_id:
        reasons.append("missing_source_item_id")
    if not source_item.source_id:
        reasons.append("missing_source_id")
    if not (source_item.canonical_url or source_item.source_url):
        reasons.append("missing_source_url")
    if source_item.dedupe_status in NON_UNIQUE_DEDUPE_STATUSES:
        reasons.append(f"non_unique_source_item:{source_item.dedupe_status}")
    if not source_item.template_suggestion:
        reasons.append("missing_template_suggestion")
    if word_count(source_item.raw_body_text or source_item.raw_summary) < MIN_ELIGIBLE_SOURCE_WORDS:
        reasons.append("insufficient_source_text")

    return DraftEligibilityResult(is_eligible=not reasons, reasons=tuple(reasons))


def format_source_item_to_draft(
    source_item: SourceItem,
    template_contract: BlogTemplateContract | None = None,
    created_at: str | None = None,
) -> DraftRecord:
    eligibility = evaluate_source_item_eligibility(source_item)
    if not eligibility.is_eligible:
        joined = ", ".join(eligibility.reasons)
        raise ValueError(f"Source item {source_item.item_id} is not eligible for draft formatting: {joined}")

    contract = resolve_blog_template_contract(source_item, template_contract=template_contract)
    draft = create_draft_skeleton(source_item, template_contract=contract, created_at=created_at)
    candidate_paragraphs = _extract_candidate_paragraphs(source_item)
    chunks = _assign_paragraph_chunks(candidate_paragraphs, len(contract.body_section_keys))
    topic_terms = _extract_topic_terms(source_item, candidate_paragraphs=candidate_paragraphs)

    draft.intro_text = _build_intro_text(source_item, contract, topic_terms)
    draft.headline_selected = source_item.raw_title
    draft.excerpt = _build_excerpt(draft.intro_text or candidate_paragraphs[0])
    draft.sections = _fill_sections(draft.sections, chunks, source_item, contract, topic_terms)
    draft.category, draft.tag_candidates = assign_category_and_tags(source_item, contract, topic_terms)
    quality_result = evaluate_draft_against_source(
        draft,
        source_item,
        template_contract=contract,
        candidate_paragraphs=candidate_paragraphs,
        topic_terms=topic_terms,
    )
    draft.quality_gate_status = quality_result.quality_gate_status
    draft.quality_flags = list(quality_result.quality_flags)
    draft.derivative_risk_level = quality_result.derivative_risk_level
    draft.derivative_risk_notes = quality_result.derivative_risk_notes
    draft.updated_at = draft.created_at
    return draft


def evaluate_draft_against_source(
    draft: DraftRecord,
    source_item: SourceItem,
    template_contract: BlogTemplateContract | None = None,
    candidate_paragraphs: list[str] | None = None,
    topic_terms: list[str] | None = None,
):
    contract = template_contract or get_blog_template_contract(draft.template_id)
    active_candidate_paragraphs = candidate_paragraphs or _extract_candidate_paragraphs(source_item)
    active_topic_terms = topic_terms or _extract_topic_terms(
        source_item,
        candidate_paragraphs=active_candidate_paragraphs,
    )
    semantic_profile = _build_semantic_profile(
        source_item,
        active_candidate_paragraphs,
        active_topic_terms,
    )
    return evaluate_draft_quality(
        draft,
        source_item,
        template_contract=contract,
        semantic_profile=semantic_profile,
    )


def _extract_candidate_paragraphs(source_item: SourceItem) -> list[str]:
    source_text = source_item.raw_body_text or source_item.raw_summary
    raw_parts = [part.strip() for part in PARAGRAPH_SPLIT_RE.split(source_text) if part.strip()]
    cleaned_parts = [clean_text(part) for part in raw_parts if clean_text(part)]
    filtered_parts = [
        part
        for part in cleaned_parts
        if not _is_noise_paragraph(part) and not _is_procedural_paragraph(part)
    ]

    if len(filtered_parts) >= 2:
        return filtered_parts

    non_noise_parts = [part for part in cleaned_parts if not _is_noise_paragraph(part)]
    if len(non_noise_parts) >= 2:
        return non_noise_parts

    compact_text = clean_text(source_text)
    sentences = [part.strip() for part in SENTENCE_SPLIT_RE.split(compact_text) if part.strip()]
    if len(sentences) < 2:
        return [compact_text]
    return _group_sentences_into_paragraphs(sentences)


def _group_sentences_into_paragraphs(sentences: list[str], max_sentences_per_group: int = 2) -> list[str]:
    paragraphs: list[str] = []
    for index in range(0, len(sentences), max_sentences_per_group):
        group = " ".join(sentences[index : index + max_sentences_per_group]).strip()
        if group:
            paragraphs.append(group)
    return paragraphs


def _is_procedural_paragraph(paragraph: str) -> bool:
    normalized = _normalize_token_text(paragraph).lower()
    if not normalized:
        return True
    if normalized.startswith(PROCEDURAL_PREFIXES):
        return True
    if normalized.startswith("how to ") and word_count(paragraph) <= 16:
        return True

    tokens = TOKEN_RE.findall(normalized)
    if not tokens:
        return True
    if normalized[0].isdigit():
        return True
    if tokens[0] in PROCEDURAL_START_TERMS:
        return True
    if normalized.startswith(("ingredients", "directions", "instructions", "method")):
        return True

    measurement_hits = len(MEASUREMENT_RE.findall(normalized))
    if measurement_hits >= 2:
        return True
    if measurement_hits >= 1 and word_count(paragraph) <= 20:
        return True

    imperative_hits = 0
    sentence_starts = [part.strip() for part in SENTENCE_SPLIT_RE.split(clean_text(paragraph)) if part.strip()]
    for sentence in sentence_starts:
        sentence_tokens = TOKEN_RE.findall(_normalize_token_text(sentence).lower())
        lead_tokens = sentence_tokens[:5]
        if lead_tokens and any(token in PROCEDURAL_START_TERMS for token in lead_tokens):
            imperative_hits += 1
    if imperative_hits >= 2:
        return True
    if imperative_hits >= 1 and measurement_hits >= 1:
        return True

    return False


def _is_noise_paragraph(paragraph: str) -> bool:
    cleaned = clean_text(paragraph)
    normalized = _normalize_token_text(cleaned).lower()
    if not normalized:
        return True
    if any(phrase in normalized for phrase in NOISE_PHRASES):
        return True
    if normalized.startswith("photo:"):
        return True
    if any(hint in normalized for hint in ATTRIBUTION_HINTS) and word_count(cleaned) <= 18:
        return True
    if normalized.startswith("how to ") and word_count(cleaned) <= 16:
        return True
    if _looks_like_related_link_title(cleaned):
        return True
    return False


def _looks_like_related_link_title(paragraph: str) -> bool:
    cleaned = clean_text(paragraph)
    if word_count(cleaned) > 12:
        return False
    if any(marker in cleaned for marker in ".!?"):
        return False
    tokens = cleaned.split()
    if not tokens:
        return True
    lowercase_initials = sum(token[:1].islower() for token in tokens if token[:1].isalpha())
    alpha_tokens = sum(token[:1].isalpha() for token in tokens)
    if alpha_tokens == 0:
        return True
    return lowercase_initials <= max(1, alpha_tokens // 4)


def _build_intro_text(
    source_item: SourceItem,
    contract: BlogTemplateContract,
    topic_terms: list[str],
) -> str:
    subject = _select_subject_label(source_item, topic_terms)
    focus_phrase = _join_terms(_select_focus_terms(topic_terms, subject, limit=2), fallback="the key supporting detail")
    if contract.template_family == "food_benefit_article":
        sentences = (
            f"The main point here is {subject}. The useful part is understanding {focus_phrase} in a practical, everyday way.",
            "The goal is to keep the explanation practical, honest, and easy to scan on mobile for everyday readers.",
        )
    elif contract.template_family == "curiosity_article":
        sentences = (
            f"The short version is that this question is really about {subject}. The useful part is understanding {focus_phrase} before the article drifts into extra detail.",
            "This version answers the question quickly and then adds the supporting context people actually need on mobile.",
        )
    else:
        sentences = (
            f"The main point here is {subject}. The useful part is understanding {focus_phrase} without dragging in the full source structure.",
            "This draft keeps the explanation short, answer-first, and easier to scan on mobile for everyday readers.",
        )
    return " ".join(sentences)


def _build_excerpt(value: str) -> str:
    return _limit_words(value, 35)


def _assign_paragraph_chunks(candidate_paragraphs: list[str], section_count: int) -> list[list[str]]:
    if section_count <= 0:
        return []

    normalized_paragraphs = candidate_paragraphs or [""]
    chunks: list[list[str]] = []
    start = 0
    for index in range(section_count):
        remaining_sections = section_count - index
        remaining_paragraphs = len(normalized_paragraphs) - start
        slice_size = max(1, (remaining_paragraphs + remaining_sections - 1) // remaining_sections)
        end = min(len(normalized_paragraphs), start + slice_size)
        chunk = normalized_paragraphs[start:end]
        chunks.append(chunk or [normalized_paragraphs[-1]])
        start = end

    fallback_text = normalized_paragraphs[-1]
    while len(chunks) < section_count:
        chunks.append([fallback_text])
    return chunks


def _fill_sections(
    sections: list,
    chunks: list[list[str]],
    source_item: SourceItem,
    contract: BlogTemplateContract,
    topic_terms: list[str],
) -> list:
    subject = _select_subject_label(source_item, topic_terms)
    focus_terms = _select_focus_terms(topic_terms, subject, limit=2)
    updated_sections = []
    for section, chunk in zip(sections, chunks):
        section_terms = _select_section_terms(chunk, topic_terms)
        if section.section_key in BULLET_SECTION_KEYS:
            bullet_points = _build_bullet_points(section.section_key, section_terms, subject, focus_terms)
            updated_sections.append(
                type(section)(
                    section_key=section.section_key,
                    section_label=section.section_label,
                    position=section.position,
                    body_blocks=[],
                    bullet_points=bullet_points,
                )
            )
            continue

        body_blocks = _build_section_body_blocks(
            section.section_key,
            section_terms,
            contract.template_family,
            subject,
            focus_terms,
        )
        updated_sections.append(
            type(section)(
                section_key=section.section_key,
                section_label=section.section_label,
                position=section.position,
                body_blocks=body_blocks or [""],
                bullet_points=[],
            )
        )
    return updated_sections


def _build_bullet_points(
    section_key: str,
    terms: list[str],
    subject: str,
    focus_terms: list[str],
) -> list[str]:
    primary = terms[0] if terms else "the key detail"
    secondary = terms[1] if len(terms) > 1 else "the supporting context"
    tertiary = terms[2] if len(terms) > 2 else "the main limitation"
    if section_key == "practical_points":
        points = [
            f"Use {primary} as a clue when planning a simple meal that still feels manageable on an ordinary weeknight.",
            f"Pair {secondary} with familiar staples instead of overcomplicating the idea or turning the ingredient into a special project.",
            f"Watch how {tertiary} changes the practical value of the ingredient across portions, timing, and basic meal structure.",
            "Keep the takeaway grounded in routine use, pantry flexibility, and repeatable cooking decisions rather than dramatic promises.",
            "Treat the ingredient as part of a repeatable meal pattern, not as a one-time miracle fix or trend.",
        ]
    elif section_key == "supporting_points":
        focus_label = _join_terms(focus_terms[:2], fallback="the main supporting detail")
        points = [
            f"Keep {subject} at the center instead of retelling the full source structure or every side detail from the original article.",
            f"Use {focus_label} as the detail readers should remember first when they try to explain the point later.",
            f"Treat {secondary} as supporting context, not as filler wording that slows down the answer-first structure.",
            "Keep the explanation factual, short, and easy to scan on mobile without losing the useful supporting context.",
        ]
    else:
        points = [
            f"Watch how {primary} changes before adjusting everything else.",
            f"Notice what {secondary} does to timing and consistency.",
            f"Treat shifts in {tertiary} as signals the process is changing.",
            "Use the pattern to make the result easier to repeat next time.",
        ]
    return [_limit_words(point, 24) for point in points]


def _build_section_body_blocks(
    section_key: str,
    terms: list[str],
    template_family: str,
    subject: str,
    focus_terms: list[str],
) -> list[str]:
    primary = terms[0] if terms else "the main supporting detail"
    secondary = terms[1] if len(terms) > 1 else "the supporting context"
    tertiary = terms[2] if len(terms) > 2 else "the next useful example"
    focus_phrase = _join_terms(
        focus_terms[:2],
        fallback=_join_terms([primary, secondary], fallback="the main supporting details"),
    )

    templates: dict[str, tuple[str, ...]] = {
        "direct_answer": (
            f"The short answer is that {subject} stands out because of {focus_phrase}. Starting with that point makes the article easier to scan and easier to remember.",
            "The goal is to surface the useful fact early, then use the rest of the draft to explain why it matters without copying the source structure.",
        ),
        "why_it_happens": (
            f"That becomes clearer once {primary} and {secondary} are treated as the main supporting details instead of background noise. They explain the point better than a long retelling of every step or anecdote.",
            f"Keeping the focus on those details gives the article a cleaner shape and helps the reader understand why {subject} is worth noticing. It also shows why small changes can lead to noticeably different outcomes even when the setup looks almost the same.",
        ),
        "why_this_food_matters": (
            f"This food matters because {focus_phrase} make it easier to build meals that feel practical, filling, and repeatable. It fits normal cooking routines without asking for a complicated plan.",
            "The value here is mostly operational. It helps people make simpler decisions about what to cook, how to stretch familiar ingredients, and how to keep regular meals manageable through the week.",
        ),
        "caution_or_limit": (
            f"The useful part is practical, not magical. Factors like {focus_phrase} still depend on the rest of the meal, the portion, and how the ingredient is prepared. That perspective keeps the article useful without drifting into exaggerated health promises.",
        ),
        "conclusion": (
            f"That is why {subject} works best as part of a steady routine rather than a dramatic claim. Used well, it supports simpler planning, more flexible meals, and a calmer decision-making process in the kitchen.",
        ),
        "fast_answer": (
            f"The fast answer is that {subject} is mainly a question about {focus_phrase}. The useful part is getting to that explanation before the article drifts into extra detail.",
            "In other words, the headline question usually has a practical explanation rather than a mysterious one. The answer becomes clearer when the background is shortened and reorganized.",
        ),
        "background_explanation": (
            f"The background is mostly about {primary} and {secondary}. Those details explain why the question sounds more surprising than it really is.",
            f"That is why short explanations help so much. They give context for {tertiary} without forcing people to read a long, source-shaped article first.",
            "They also keep the piece focused on one clear theme instead of piling on trivia that makes the answer harder to remember.",
        ),
        "example_or_context": (
            f"A useful way to think about it is to see how {subject} shows up in an ordinary food or storage situation. Once the point appears in context, the core idea becomes easier to remember.",
            f"That context is also what makes the explanation more usable. People can connect {secondary} and {tertiary} to a real decision instead of a vague piece of trivia.",
        ),
        "recap": (
            f"The takeaway is simple: {subject} is easier to understand once the key details are stated plainly. That leaves the reader with a clear fact instead of a vague impression.",
        ),
        "close": (
            f"The closing point is simple: once {subject} is explained plainly, the question stops feeling mysterious. The answer becomes easier to remember and easier to apply.",
        ),
    }

    body_blocks = templates.get(section_key)
    if body_blocks is None:
        fallback = (
            f"This section focuses on how {focus_phrase} support the main explanation. The goal is to keep the material short, readable, and clearly separated from the original source structure.",
        )
        body_blocks = fallback
    return [_limit_words(block, 110) for block in body_blocks]


def _limit_words(value: str, max_words: int) -> str:
    words = clean_text(value).split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]).strip() + "..."


def _extract_topic_terms(
    source_item: SourceItem,
    candidate_paragraphs: list[str] | None = None,
    limit: int = 6,
) -> list[str]:
    title_segments = _extract_title_segments(source_item.raw_title)
    display_segment = _select_display_title_segment(title_segments)
    title_anchor_terms = _extract_title_anchor_terms(title_segments)
    summary_anchor_terms = _extract_summary_anchor_terms(source_item.raw_summary)
    lead_body_text = _build_lead_body_text(candidate_paragraphs or _extract_candidate_paragraphs(source_item))
    body_tokens = TOKEN_RE.findall(_normalize_token_text(lead_body_text).lower())
    body_counts = Counter(_filter_term_tokens(body_tokens, body_mode=True))
    body_phrase_counts = Counter(_extract_term_phrases(body_tokens, body_mode=True))

    ordered_body_terms = [token for token in body_tokens if token in body_counts]
    ordered_body_phrases = [
        phrase
        for phrase in _extract_term_phrases(body_tokens, body_mode=True)
        if phrase in body_phrase_counts
    ]
    body_positions = {token: index for index, token in enumerate(dict.fromkeys(ordered_body_terms))}
    body_phrase_positions = {phrase: index for index, phrase in enumerate(dict.fromkeys(ordered_body_phrases))}

    scored_terms: list[tuple[int, int, str]] = []
    seen: set[str] = set(title_anchor_terms + summary_anchor_terms)

    for term, count in body_phrase_counts.items():
        if term in seen:
            continue
        seen.add(term)
        scored_terms.append((-(count * 3), body_phrase_positions.get(term, 100), term))

    for term, count in body_counts.items():
        if term in seen:
            continue
        seen.add(term)
        scored_terms.append((-(count * 2), body_positions.get(term, 100), term))

    scored_terms.sort()
    terms: list[str] = []
    for term in title_anchor_terms:
        if display_segment and _term_overlaps_existing(term, [display_segment]):
            continue
        if term not in terms and not _term_overlaps_existing(term, terms):
            terms.append(term)
        if len(terms) == limit:
            return terms

    for term in summary_anchor_terms[:2]:
        if term not in terms and not _term_overlaps_existing(term, terms):
            terms.append(term)
        if len(terms) == limit:
            return terms

    for _, _, term in scored_terms:
        if term not in terms and not _term_overlaps_existing(term, terms):
            terms.append(term)
        if len(terms) == limit:
            break

    return terms or ["timing", "texture", "ingredients"]


def _filter_term_tokens(tokens: list[str], body_mode: bool = False) -> list[str]:
    filtered: list[str] = []
    for token in tokens:
        if len(token) < 4:
            continue
        if token in STOPWORDS or token in LOW_SIGNAL_TERMS:
            continue
        if body_mode and token in BODY_NOISE_TERMS:
            continue
        filtered.append(token)
    return filtered


def _extract_term_phrases(
    tokens: list[str],
    body_mode: bool = False,
    sizes: tuple[int, ...] = (3, 2),
) -> list[str]:
    phrases: list[str] = []
    for size in sizes:
        if len(tokens) < size:
            continue
        for index in range(len(tokens) - size + 1):
            phrase_tokens = tokens[index : index + size]
            if any(len(token) < 4 for token in phrase_tokens):
                continue
            if any(token in STOPWORDS or token in LOW_SIGNAL_TERMS for token in phrase_tokens):
                continue
            if body_mode and any(token in BODY_NOISE_TERMS for token in phrase_tokens):
                continue
            phrases.append(" ".join(phrase_tokens))
    return phrases


def _select_section_terms(chunk: list[str], topic_terms: list[str], limit: int = 4) -> list[str]:
    local_tokens = TOKEN_RE.findall(_normalize_token_text(" ".join(chunk)).lower())
    local_terms = _extract_term_phrases(local_tokens, body_mode=True) + _filter_term_tokens(local_tokens, body_mode=True)
    ordered: list[str] = []
    for term in topic_terms + local_terms:
        if term not in ordered:
            ordered.append(term)
        if len(ordered) == limit:
            break
    return ordered or topic_terms[:limit]


def _extract_title_segments(raw_title: str) -> list[str]:
    segments = [clean_text(segment) for segment in TITLE_SEGMENT_SPLIT_RE.split(raw_title) if clean_text(segment)]
    return segments or [clean_text(raw_title)]


def _extract_title_anchor_terms(title_segments: list[str]) -> list[str]:
    phrase_anchors: list[str] = []
    token_anchors: list[str] = []
    for segment in title_segments:
        segment_tokens = TOKEN_RE.findall(_normalize_token_text(segment).lower())
        phrase_candidates = _extract_term_phrases(segment_tokens, sizes=(3, 2))
        token_candidates = _filter_term_tokens(segment_tokens)
        for term in phrase_candidates:
            if _term_overlaps_existing(term, phrase_anchors):
                continue
            phrase_anchors.append(term)
        for term in token_candidates:
            if _term_overlaps_existing(term, phrase_anchors + token_anchors):
                continue
            token_anchors.append(term)
    return phrase_anchors + token_anchors


def _extract_summary_anchor_terms(raw_summary: str) -> list[str]:
    summary_text = _clean_summary_text(raw_summary)
    if " The post " in summary_text:
        summary_text = summary_text.split(" The post ", maxsplit=1)[0]
    summary_tokens = TOKEN_RE.findall(_normalize_token_text(summary_text).lower())
    candidate_terms = _extract_term_phrases(summary_tokens, body_mode=True, sizes=(3, 2)) + _filter_term_tokens(
        summary_tokens,
        body_mode=True,
    )
    summary_terms: list[str] = []
    for term in candidate_terms:
        term_tokens = TOKEN_RE.findall(term)
        if any(token in SUMMARY_NOISE_TERMS or "'" in token for token in term_tokens):
            continue
        if _term_overlaps_existing(term, summary_terms):
            continue
        summary_terms.append(term)
    return summary_terms


def _clean_summary_text(raw_summary: str) -> str:
    summary_text = clean_text(raw_summary)
    segments = [segment.strip() for segment in re.split(r"\s+[•|]\s+|\s{2,}", summary_text) if segment.strip()]
    kept_segments: list[str] = []
    for segment in segments:
        lowered = _normalize_token_text(segment).lower()
        if lowered.startswith("photo:"):
            continue
        if any(hint in lowered for hint in ATTRIBUTION_HINTS):
            continue
        if any(phrase in lowered for phrase in NOISE_PHRASES):
            continue
        kept_segments.append(segment)
    return " ".join(kept_segments)


def _select_display_title_segment(title_segments: list[str]) -> str | None:
    for segment in reversed(title_segments):
        lowered = clean_text(segment).lower()
        if lowered.startswith(("and ", "but ")):
            continue
        if lowered.startswith(("how to ", "what ", "why ", "the only ", "the real ")):
            continue
        segment_tokens = TOKEN_RE.findall(_normalize_token_text(segment).lower())
        meaningful_tokens = _filter_term_tokens(segment_tokens)
        if len(meaningful_tokens) >= 2:
            return clean_text(segment)
    return None


def _build_lead_body_text(candidate_paragraphs: list[str]) -> str:
    lead_text = " ".join(candidate_paragraphs[:LEAD_PARAGRAPH_LIMIT])
    words = clean_text(lead_text).split()
    return " ".join(words[:LEAD_BODY_WORD_LIMIT])


def _normalize_token_text(value: str) -> str:
    return unicodedata.normalize("NFKD", clean_text(value)).encode("ascii", "ignore").decode("ascii")


def derive_subject_anchor(source_item: SourceItem) -> str:
    candidate_paragraphs = _extract_candidate_paragraphs(source_item)
    topic_terms = _extract_topic_terms(source_item, candidate_paragraphs=candidate_paragraphs)
    return _select_subject_label(source_item, topic_terms)


def _select_subject_label(source_item: SourceItem, topic_terms: list[str]) -> str:
    title_segments = _extract_title_segments(source_item.raw_title)
    display_segment = _select_display_title_segment(title_segments)
    if display_segment:
        return display_segment
    title_anchors = _extract_title_anchor_terms(title_segments)
    if title_anchors:
        return title_anchors[0]
    if topic_terms:
        return topic_terms[0]
    return "the main food point"


def _select_focus_terms(topic_terms: list[str], subject: str, limit: int = 2) -> list[str]:
    focus_terms: list[str] = []
    for term in topic_terms:
        if term == subject:
            continue
        if _term_overlaps_existing(term, [subject, *focus_terms]):
            continue
        focus_terms.append(term)
        if len(focus_terms) == limit:
            break
    return focus_terms


def _build_semantic_profile(
    source_item: SourceItem,
    candidate_paragraphs: list[str],
    topic_terms: list[str],
) -> dict[str, object]:
    raw_text = source_item.raw_body_text or source_item.raw_summary
    raw_parts = [clean_text(part) for part in PARAGRAPH_SPLIT_RE.split(raw_text) if clean_text(part)]
    lead_body_text = _build_lead_body_text(candidate_paragraphs)
    lead_body_tokens = TOKEN_RE.findall(_normalize_token_text(lead_body_text).lower())
    title_anchor_terms = _extract_title_anchor_terms(_extract_title_segments(source_item.raw_title))

    recipe_like_count = sum(_is_procedural_paragraph(part) for part in raw_parts)
    noise_like_count = sum(_is_noise_paragraph(part) for part in raw_parts)
    low_signal_topic_term_count = sum(
        _is_low_signal_topic_term(term, lead_body_tokens, title_anchor_terms)
        for term in topic_terms[:4]
    )
    body_supported_topic_term_count = sum(_term_has_token_support(term, lead_body_tokens) for term in topic_terms[:4])

    total_parts = len(raw_parts) or 1
    return {
        "candidate_paragraph_count": len(candidate_paragraphs),
        "recipe_like_paragraph_ratio": recipe_like_count / total_parts,
        "noise_like_paragraph_ratio": noise_like_count / total_parts,
        "low_signal_topic_term_count": low_signal_topic_term_count,
        "body_supported_topic_term_count": body_supported_topic_term_count,
    }


def _is_low_signal_topic_term(term: str, body_tokens: list[str], title_anchor_terms: list[str]) -> bool:
    term_tokens = TOKEN_RE.findall(_normalize_token_text(term).lower())
    if not term_tokens:
        return True
    if any(token in LOW_SIGNAL_TERMS or token in SUMMARY_NOISE_TERMS or "'" in token for token in term_tokens):
        return True
    if _term_has_token_support(term, body_tokens):
        return False
    return not _term_has_anchor_support(term, title_anchor_terms)


def _term_has_token_support(term: str, tokens: list[str]) -> bool:
    term_tokens = TOKEN_RE.findall(_normalize_token_text(term).lower())
    if not term_tokens:
        return False
    token_set = set(tokens)
    if len(term_tokens) == 1:
        return term_tokens[0] in token_set
    return sum(token in token_set for token in term_tokens) >= max(1, len(term_tokens) - 1)


def _term_has_anchor_support(term: str, anchors: list[str]) -> bool:
    return any(_term_overlaps_existing(term, [anchor]) for anchor in anchors)


def _term_overlaps_existing(term: str, existing_terms: list[str]) -> bool:
    normalized_term = clean_text(term).lower()
    for existing in existing_terms:
        normalized_existing = clean_text(existing).lower()
        if not normalized_existing:
            continue
        if normalized_term == normalized_existing:
            return True
        if normalized_term in normalized_existing or normalized_existing in normalized_term:
            return True
    return False


def _join_terms(terms: list[str], fallback: str) -> str:
    cleaned_terms = [clean_text(term) for term in terms if clean_text(term)]
    if not cleaned_terms:
        return fallback
    if len(cleaned_terms) == 1:
        return cleaned_terms[0]
    if len(cleaned_terms) == 2:
        return f"{cleaned_terms[0]} and {cleaned_terms[1]}"
    return ", ".join(cleaned_terms[:-1]) + f", and {cleaned_terms[-1]}"
