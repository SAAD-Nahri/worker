from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ALLOWED_ASSET_SOURCE_KINDS = frozenset({"owned", "licensed", "ai_generated"})
ALLOWED_ASSET_APPROVAL_STATES = frozenset({"pending_review", "approved", "needs_edits", "rejected"})
ALLOWED_ASSET_INTENDED_USAGES = frozenset(
    {"blog_featured_image", "facebook_link_post_image", "blog_and_facebook"}
)


@dataclass
class MediaBriefRecord:
    media_brief_id: str
    draft_id: str
    blog_publish_id: str | None
    social_package_id: str | None
    template_family: str
    category: str
    tag_candidates: list[str] = field(default_factory=list)
    brief_goal: str = ""
    subject_focus: str = ""
    visual_style_notes: list[str] = field(default_factory=list)
    prohibited_visual_patterns: list[str] = field(default_factory=list)
    alt_text_seed: str = ""
    intended_usage: str = "blog_and_facebook"
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not self.media_brief_id.strip():
            raise ValueError("Media brief records require media_brief_id.")
        if not self.draft_id.strip():
            raise ValueError("Media brief records require draft_id.")
        if self.blog_publish_id is not None and not self.blog_publish_id.strip():
            raise ValueError("Media brief blog_publish_id must be blank or non-empty text.")
        if self.social_package_id is not None and not self.social_package_id.strip():
            raise ValueError("Media brief social_package_id must be blank or non-empty text.")
        if not self.template_family.strip():
            raise ValueError("Media brief records require template_family.")
        if not self.category.strip():
            raise ValueError("Media brief records require category.")
        if self.intended_usage not in ALLOWED_ASSET_INTENDED_USAGES:
            raise ValueError(f"Unsupported media brief intended_usage: {self.intended_usage}")
        if not self.brief_goal.strip():
            raise ValueError("Media brief records require brief_goal.")
        if not self.subject_focus.strip():
            raise ValueError("Media brief records require subject_focus.")
        if not [note for note in self.visual_style_notes if str(note).strip()]:
            raise ValueError("Media brief records require at least one visual_style_note.")
        if not [pattern for pattern in self.prohibited_visual_patterns if str(pattern).strip()]:
            raise ValueError("Media brief records require prohibited_visual_patterns.")
        if not self.alt_text_seed.strip():
            raise ValueError("Media brief records require alt_text_seed.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AssetRecord:
    asset_record_id: str
    media_brief_id: str
    draft_id: str
    blog_publish_id: str | None
    social_package_id: str | None
    asset_source_kind: str
    provenance_reference: str
    approval_state: str = "pending_review"
    intended_usage: str = "blog_and_facebook"
    asset_url_or_path: str = ""
    alt_text: str = ""
    caption_support_text: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not self.asset_record_id.strip():
            raise ValueError("Asset records require asset_record_id.")
        if not self.media_brief_id.strip():
            raise ValueError("Asset records require media_brief_id.")
        if not self.draft_id.strip():
            raise ValueError("Asset records require draft_id.")
        if self.blog_publish_id is not None and not self.blog_publish_id.strip():
            raise ValueError("Asset record blog_publish_id must be blank or non-empty text.")
        if self.social_package_id is not None and not self.social_package_id.strip():
            raise ValueError("Asset record social_package_id must be blank or non-empty text.")
        if self.asset_source_kind not in ALLOWED_ASSET_SOURCE_KINDS:
            raise ValueError(f"Unsupported asset_source_kind: {self.asset_source_kind}")
        if self.approval_state not in ALLOWED_ASSET_APPROVAL_STATES:
            raise ValueError(f"Unsupported asset approval_state: {self.approval_state}")
        if self.intended_usage not in ALLOWED_ASSET_INTENDED_USAGES:
            raise ValueError(f"Unsupported asset intended_usage: {self.intended_usage}")
        if not self.provenance_reference.strip():
            raise ValueError("Asset records require provenance_reference.")
        if not self.asset_url_or_path.strip():
            raise ValueError("Asset records require asset_url_or_path.")
        if not self.alt_text.strip():
            raise ValueError("Asset records require alt_text.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AssetReviewRecord:
    review_id: str
    asset_record_id: str
    media_brief_id: str
    draft_id: str
    blog_publish_id: str | None
    social_package_id: str | None
    reviewer_label: str
    reviewed_at: str
    review_outcome: str
    previous_approval_state: str
    updated_approval_state: str
    review_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
