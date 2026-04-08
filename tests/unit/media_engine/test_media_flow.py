from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.formatting import format_source_item_to_draft
from content_engine.review import record_draft_review
from distribution_engine.facebook import prepare_social_package_record
from distribution_engine.wordpress import prepare_blog_publish_record
from media_engine.assets import prepare_asset_record, resolve_asset_readiness
from media_engine.briefs import prepare_media_brief_record
from media_engine.review import record_asset_review
from media_engine.storage import (
    append_asset_records,
    append_asset_review_records,
    append_media_brief_records,
    load_latest_asset_for_blog_publish,
    load_latest_media_brief_for_draft,
    read_asset_review_records,
)
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-media-1",
        source_id="src-media-1",
        source_name="Media Test Source",
        source_family="editorial_food",
        run_id="run-media-1",
        source_url="https://example.com/olive-oil",
        canonical_url="https://example.com/olive-oil",
        discovered_at="2026-04-04T09:00:00+00:00",
        fetched_at="2026-04-04T09:00:00+00:00",
        raw_title="Why Olive Oil Looks Cloudy in the Cold",
        raw_summary="A short explainer about chilled olive oil.",
        raw_body_text=(
            "Olive oil can look cloudy in the cold because some waxes and fatty compounds solidify at lower temperatures. "
            "That visual change is usually temporary and clears when the bottle warms back up.\n\n"
            "The cloudy look does not automatically mean the oil has spoiled. In many kitchens it simply means the bottle stayed in a cool pantry or refrigerator long enough for the texture to shift.\n\n"
            "Once the oil warms again, the appearance usually changes back. That practical detail matters because readers often assume the haze means something is wrong when the bigger factor is just temperature.\n\n"
            "For a useful article, the takeaway is simple: cold storage changes how the oil looks more than it changes whether the oil is safe or usable."
        ),
        author_name="Editor",
        published_at="2026-04-03T10:00:00+00:00",
        topical_label="food_question",
        freshness_label="evergreen",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion="curiosity_article",
    )


class MediaFlowTests(unittest.TestCase):
    def test_prepare_media_brief_record_uses_approved_draft_context(self) -> None:
        source_item = _build_source_item()
        draft_seed = format_source_item_to_draft(source_item, created_at="2026-04-04T10:00:00+00:00")
        approved_draft, _ = record_draft_review(
            draft_seed,
            review_outcome="approved",
            review_notes=["ready_for_media"],
            reviewer_label="seed_operator",
            reviewed_at="2026-04-04T10:05:00+00:00",
        )
        blog_record = prepare_blog_publish_record(
            approved_draft,
            publish_intent="draft",
            created_at="2026-04-04T10:06:00+00:00",
            allow_non_pass_quality=True,
        )
        social_package = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-04T10:07:00+00:00",
        )

        media_brief = prepare_media_brief_record(
            approved_draft,
            blog_publish_record=blog_record,
            social_package_record=social_package,
            created_at="2026-04-04T10:08:00+00:00",
        )

        self.assertEqual(media_brief.draft_id, approved_draft.draft_id)
        self.assertEqual(media_brief.blog_publish_id, blog_record.blog_publish_id)
        self.assertEqual(media_brief.social_package_id, social_package.social_package_id)
        self.assertEqual(media_brief.intended_usage, "blog_and_facebook")
        self.assertIn("rights-safe lead visual", media_brief.brief_goal)
        self.assertIn("unclear rights status", media_brief.prohibited_visual_patterns)
        self.assertGreaterEqual(len(media_brief.visual_style_notes), 3)

    def test_asset_storage_and_review_preserve_linkage_and_readiness(self) -> None:
        source_item = _build_source_item()
        draft_seed = format_source_item_to_draft(source_item, created_at="2026-04-04T10:00:00+00:00")
        approved_draft, _ = record_draft_review(
            draft_seed,
            review_outcome="approved",
            review_notes=["ready_for_media"],
            reviewer_label="seed_operator",
            reviewed_at="2026-04-04T10:05:00+00:00",
        )
        blog_record = prepare_blog_publish_record(
            approved_draft,
            publish_intent="draft",
            created_at="2026-04-04T10:06:00+00:00",
            allow_non_pass_quality=True,
        )
        social_package = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-04T10:07:00+00:00",
        )
        media_brief = prepare_media_brief_record(
            approved_draft,
            blog_publish_record=blog_record,
            social_package_record=social_package,
            created_at="2026-04-04T10:08:00+00:00",
        )
        asset_record = prepare_asset_record(
            media_brief,
            asset_source_kind="ai_generated",
            provenance_reference="prompt:olive-cloudy-v1",
            asset_url_or_path="C:/assets/olive-cloudy-v1.png",
            alt_text="Bottle of olive oil that appears cloudy after being chilled.",
            caption_support_text="Use as the shared lead image for the article.",
            created_at="2026-04-04T10:09:00+00:00",
        )
        updated_asset, review_record = record_asset_review(
            asset_record,
            review_outcome="approved",
            review_notes=["prompt_and_alt_text_checked"],
            reviewer_label="media_operator",
            reviewed_at="2026-04-04T10:10:00+00:00",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            brief_path = root / "media_briefs.jsonl"
            asset_path = root / "asset_records.jsonl"
            review_path = root / "asset_reviews.jsonl"

            append_media_brief_records([media_brief], path=brief_path)
            append_asset_records([asset_record, updated_asset], path=asset_path)
            append_asset_review_records([review_record], path=review_path)

            loaded_brief = load_latest_media_brief_for_draft(approved_draft.draft_id, path=brief_path)
            loaded_asset = load_latest_asset_for_blog_publish(blog_record.blog_publish_id, path=asset_path)
            loaded_reviews = read_asset_review_records(path=review_path)

        self.assertEqual(loaded_brief.media_brief_id, media_brief.media_brief_id)
        self.assertEqual(loaded_asset.approval_state, "approved")
        self.assertEqual(loaded_asset.social_package_id, social_package.social_package_id)
        self.assertEqual(len(loaded_reviews), 1)
        self.assertEqual(loaded_reviews[0].review_outcome, "approved")
        self.assertEqual(resolve_asset_readiness(loaded_asset), (True, None))


if __name__ == "__main__":
    unittest.main()
