from __future__ import annotations

from source_engine.models import SourceItem

from content_engine.models import BlogTemplateContract, LengthGuidance, SlotGuidance


_TEMPLATE_FAMILY_TO_ID = {
    "food_fact_article": "blog_food_fact_v1",
    "food_benefit_article": "blog_food_benefit_v1",
    "curiosity_article": "blog_curiosity_food_v1",
}


_BLOG_TEMPLATE_CONTRACTS = {
    "blog_food_fact_v1": BlogTemplateContract(
        template_id="blog_food_fact_v1",
        template_name="Food Fact Article",
        template_family="food_fact_article",
        content_goal="Present a surprising or useful food fact in a clean explanatory format.",
        required_slot_order=(
            "headline",
            "intro",
            "direct_answer",
            "why_it_happens",
            "supporting_points",
            "recap",
        ),
        body_section_keys=("direct_answer", "why_it_happens", "supporting_points", "recap"),
        optional_slots=("related_read_bridge",),
        tone_notes=(
            "curiosity-driven but honest",
            "answer early",
            "clear and mobile-friendly",
        ),
        prohibited_patterns=(
            "delay_answer_until_end",
            "overpromise_novelty",
            "unsupported_claims",
            "source_order_copying",
        ),
        target_length_guidance=LengthGuidance(preferred_min=260, preferred_max=520, soft_min=180, soft_max=620),
        default_category="food-facts",
        slot_guidance=(
            SlotGuidance(slot_key="intro", soft_min_words=35, soft_max_words=70),
            SlotGuidance(
                slot_key="direct_answer",
                soft_min_words=45,
                soft_max_words=90,
                max_words_before_slot=120,
            ),
            SlotGuidance(slot_key="why_it_happens", soft_min_words=70, soft_max_words=140),
            SlotGuidance(
                slot_key="supporting_points",
                soft_min_words=60,
                soft_max_words=140,
                min_bullet_count=2,
                max_bullet_count=4,
                requires_bullets=True,
            ),
            SlotGuidance(slot_key="recap", soft_min_words=30, soft_max_words=70),
            SlotGuidance(slot_key="related_read_bridge", soft_min_words=20, soft_max_words=60),
        ),
    ),
    "blog_food_benefit_v1": BlogTemplateContract(
        template_id="blog_food_benefit_v1",
        template_name="Food Benefit Article",
        template_family="food_benefit_article",
        content_goal="Present a food-related practical value angle without drifting into exaggerated claims.",
        required_slot_order=(
            "headline",
            "intro",
            "why_this_food_matters",
            "practical_points",
            "caution_or_limit",
            "conclusion",
        ),
        body_section_keys=("why_this_food_matters", "practical_points", "caution_or_limit", "conclusion"),
        optional_slots=(),
        tone_notes=(
            "practical and moderate",
            "avoid medical framing",
            "stay clear and useful",
        ),
        prohibited_patterns=(
            "cure_language",
            "absolute_health_promises",
            "aggressive_wellness_framing",
            "missing_caution_section",
        ),
        target_length_guidance=LengthGuidance(preferred_min=280, preferred_max=560, soft_min=200, soft_max=650),
        default_category="food-benefits-light",
        slot_guidance=(
            SlotGuidance(slot_key="intro", soft_min_words=35, soft_max_words=70),
            SlotGuidance(slot_key="why_this_food_matters", soft_min_words=60, soft_max_words=120),
            SlotGuidance(
                slot_key="practical_points",
                soft_min_words=80,
                soft_max_words=180,
                min_bullet_count=3,
                max_bullet_count=5,
                requires_bullets=True,
            ),
            SlotGuidance(slot_key="caution_or_limit", soft_min_words=35, soft_max_words=80),
            SlotGuidance(slot_key="conclusion", soft_min_words=30, soft_max_words=70),
        ),
    ),
    "blog_curiosity_food_v1": BlogTemplateContract(
        template_id="blog_curiosity_food_v1",
        template_name="Curiosity Article",
        template_family="curiosity_article",
        content_goal="Turn a surprising food-related question into a fast, readable article.",
        required_slot_order=(
            "headline",
            "fast_answer",
            "background_explanation",
            "example_or_context",
            "close",
        ),
        body_section_keys=("fast_answer", "background_explanation", "example_or_context", "close"),
        optional_slots=(),
        tone_notes=(
            "question-led or contrast-led",
            "answer quickly",
            "clean and concise",
        ),
        prohibited_patterns=(
            "vague_question_no_answer",
            "bury_answer_too_late",
            "speculation_as_fact",
            "trivia_overload",
        ),
        target_length_guidance=LengthGuidance(preferred_min=220, preferred_max=440, soft_min=160, soft_max=520),
        default_category="food-questions",
        slot_guidance=(
            SlotGuidance(slot_key="fast_answer", soft_min_words=35, soft_max_words=80),
            SlotGuidance(slot_key="background_explanation", soft_min_words=70, soft_max_words=140),
            SlotGuidance(slot_key="example_or_context", soft_min_words=60, soft_max_words=130),
            SlotGuidance(slot_key="close", soft_min_words=25, soft_max_words=60),
        ),
    ),
}


def list_blog_template_contracts() -> tuple[BlogTemplateContract, ...]:
    return tuple(_BLOG_TEMPLATE_CONTRACTS.values())


def get_blog_template_contract(template_id: str) -> BlogTemplateContract:
    try:
        return _BLOG_TEMPLATE_CONTRACTS[template_id]
    except KeyError as exc:
        raise ValueError(f"Unknown blog template_id: {template_id}") from exc


def validate_template_contract_for_source_item(
    item: SourceItem,
    template_contract: BlogTemplateContract,
) -> BlogTemplateContract:
    expected_contract = select_blog_template_contract(item)
    if template_contract.template_family != expected_contract.template_family:
        raise ValueError(
            "Template override does not match the source item's template_suggestion: "
            f"{template_contract.template_id} vs {expected_contract.template_id}"
        )
    return template_contract


def resolve_blog_template_contract(
    item: SourceItem,
    template_contract: BlogTemplateContract | None = None,
) -> BlogTemplateContract:
    if template_contract is None:
        return select_blog_template_contract(item)
    return validate_template_contract_for_source_item(item, template_contract)


def select_blog_template_contract(item: SourceItem) -> BlogTemplateContract:
    if not item.template_suggestion:
        raise ValueError(f"Source item {item.item_id} has no template_suggestion.")

    template_id = _TEMPLATE_FAMILY_TO_ID.get(item.template_suggestion)
    if template_id is None:
        raise ValueError(f"Unsupported template_suggestion: {item.template_suggestion}")
    return get_blog_template_contract(template_id)
