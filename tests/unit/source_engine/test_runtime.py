from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from source_engine.runtime import archive_runtime_state, build_runtime_reset_plan
from content_engine.storage import DRAFT_RECORDS_PATH, DRAFT_REVIEWS_PATH
from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    SOCIAL_PACKAGE_REVIEWS_PATH,
)
from tracking_engine.storage import TRACKING_AUDIT_RECORDS_PATH


class RuntimeTests(unittest.TestCase):
    def test_default_runtime_artifacts_include_content_and_phase3_records(self) -> None:
        plan = build_runtime_reset_plan(
            artifact_paths=[
                DRAFT_RECORDS_PATH,
                DRAFT_REVIEWS_PATH,
                BLOG_PUBLISH_RECORDS_PATH,
                SOCIAL_PACKAGE_RECORDS_PATH,
                SOCIAL_PACKAGE_REVIEWS_PATH,
                FACEBOOK_PUBLISH_RECORDS_PATH,
                QUEUE_ITEM_RECORDS_PATH,
                BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
                TRACKING_AUDIT_RECORDS_PATH,
            ],
            archive_root=DRAFT_RECORDS_PATH.parent / "archive",
            data_dir=DRAFT_RECORDS_PATH.parent,
        )

        self.assertIn(DRAFT_RECORDS_PATH, plan.missing_files + plan.existing_files)
        self.assertIn(DRAFT_REVIEWS_PATH, plan.missing_files + plan.existing_files)
        self.assertIn(BLOG_PUBLISH_RECORDS_PATH, plan.missing_files + plan.existing_files)
        self.assertIn(SOCIAL_PACKAGE_RECORDS_PATH, plan.missing_files + plan.existing_files)
        self.assertIn(SOCIAL_PACKAGE_REVIEWS_PATH, plan.missing_files + plan.existing_files)
        self.assertIn(FACEBOOK_PUBLISH_RECORDS_PATH, plan.missing_files + plan.existing_files)
        self.assertIn(QUEUE_ITEM_RECORDS_PATH, plan.missing_files + plan.existing_files)
        self.assertIn(BLOG_FACEBOOK_MAPPING_RECORDS_PATH, plan.missing_files + plan.existing_files)
        self.assertIn(TRACKING_AUDIT_RECORDS_PATH, plan.missing_files + plan.existing_files)

    def test_build_runtime_reset_plan_separates_existing_and_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            data_dir = temp_root / "data"
            data_dir.mkdir()
            existing = data_dir / "source_items.jsonl"
            existing.write_text("{}", encoding="utf-8")
            missing = data_dir / "intake_history.jsonl"
            archive_root = data_dir / "archive"

            plan = build_runtime_reset_plan(
                artifact_paths=[existing, missing],
                archive_root=archive_root,
                data_dir=data_dir,
            )

            self.assertEqual(plan.existing_files, [existing])
            self.assertEqual(plan.missing_files, [missing])
            self.assertTrue(str(plan.archive_dir).startswith(str(archive_root)))

    def test_archive_runtime_state_moves_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            data_dir = temp_root / "data"
            data_dir.mkdir()
            artifact = data_dir / "source_items.jsonl"
            artifact.write_text("payload", encoding="utf-8")
            archive_root = data_dir / "archive"

            plan = build_runtime_reset_plan(
                artifact_paths=[artifact],
                archive_root=archive_root,
                data_dir=data_dir,
            )
            actions = archive_runtime_state(plan)

            self.assertEqual(len(actions), 1)
            self.assertFalse(artifact.exists())
            archived_copy = Path(actions[0]["destination"])
            self.assertTrue(archived_copy.exists())
            self.assertEqual(archived_copy.read_text(encoding="utf-8"), "payload")


if __name__ == "__main__":
    unittest.main()
