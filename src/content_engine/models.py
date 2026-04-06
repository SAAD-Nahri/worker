from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class LengthGuidance:
    preferred_min: int
    preferred_max: int
    soft_min: int
    soft_max: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SlotGuidance:
    slot_key: str
    soft_min_words: int | None = None
    soft_max_words: int | None = None
    min_bullet_count: int | None = None
    max_bullet_count: int | None = None
    requires_bullets: bool = False
    max_words_before_slot: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BlogTemplateContract:
    template_id: str
    template_name: str
    template_family: str
    content_goal: str
    required_slot_order: tuple[str, ...]
    body_section_keys: tuple[str, ...]
    optional_slots: tuple[str, ...]
    tone_notes: tuple[str, ...]
    prohibited_patterns: tuple[str, ...]
    target_length_guidance: LengthGuidance
    default_category: str
    slot_guidance: tuple[SlotGuidance, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def get_slot_guidance(self, slot_key: str) -> SlotGuidance | None:
        for guidance in self.slot_guidance:
            if guidance.slot_key == slot_key:
                return guidance
        return None


@dataclass(frozen=True)
class DraftSection:
    section_key: str
    section_label: str
    position: int
    body_blocks: list[str] = field(default_factory=list)
    bullet_points: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AiAssistanceRecord:
    skill_name: str
    target_field: str
    model_label: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DraftEligibilityResult:
    is_eligible: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DraftQualityEvaluation:
    quality_gate_status: str
    quality_flags: tuple[str, ...]
    derivative_risk_level: str
    derivative_risk_notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DraftReviewRecord:
    review_id: str
    draft_id: str
    source_item_id: str
    reviewer_label: str
    reviewed_at: str
    review_outcome: str
    previous_approval_state: str
    updated_approval_state: str
    updated_workflow_state: str
    quality_gate_status: str
    derivative_risk_level: str
    review_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DraftRecord:
    draft_id: str
    workflow_state: str
    approval_state: str
    language: str
    source_item_id: str
    source_id: str
    source_url: str
    source_domain: str
    source_title: str
    source_published_at: str | None
    template_id: str
    template_family: str
    template_version: str
    category: str
    tag_candidates: list[str] = field(default_factory=list)
    headline_selected: str = ""
    headline_variants: list[str] = field(default_factory=list)
    intro_text: str = ""
    sections: list[DraftSection] = field(default_factory=list)
    excerpt: str = ""
    related_read_bridge: str | None = None
    quality_gate_status: str = "blocked"
    quality_flags: list[str] = field(default_factory=list)
    derivative_risk_level: str = "high"
    derivative_risk_notes: str = ""
    ai_assistance_log: list[AiAssistanceRecord] = field(default_factory=list)
    review_notes: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
