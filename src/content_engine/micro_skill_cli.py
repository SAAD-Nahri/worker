from __future__ import annotations

import argparse
import json
from pathlib import Path

from content_engine.micro_skills import ALLOWED_MICRO_SKILLS, HeuristicMicroSkillProvider, apply_micro_skills
from content_engine.storage import DRAFT_RECORDS_PATH, append_draft_records, load_latest_draft_record
from source_engine.storage import SOURCE_ITEMS_PATH, load_latest_source_item


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply bounded micro-skills to a draft record.")
    parser.add_argument("--draft-id", required=True, help="Draft identifier to enrich.")
    parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        required=True,
        choices=sorted(ALLOWED_MICRO_SKILLS),
        help="Micro-skill to apply. Repeat for multiple skills.",
    )
    parser.add_argument(
        "--provider",
        default="heuristic",
        choices=("heuristic",),
        help="Current local micro-skill provider. External AI providers can be added later.",
    )
    parser.add_argument(
        "--draft-records-path",
        type=Path,
        default=DRAFT_RECORDS_PATH,
        help="Path to the append-only draft records file.",
    )
    parser.add_argument(
        "--source-items-path",
        type=Path,
        default=SOURCE_ITEMS_PATH,
        help="Path to the append-only source item file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        draft = load_latest_draft_record(args.draft_id, args.draft_records_path)
        source_item = load_latest_source_item(draft.source_item_id, args.source_items_path)
        provider = HeuristicMicroSkillProvider()
        updated_draft = apply_micro_skills(draft, source_item, args.skills, provider=provider)
        append_draft_records([updated_draft], path=args.draft_records_path)
    except ValueError as exc:
        parser.error(str(exc))

    summary = {
        "draft_id": updated_draft.draft_id,
        "provider": provider.provider_label,
        "skills": args.skills,
        "headline_variants": updated_draft.headline_variants,
        "intro_text": updated_draft.intro_text,
        "excerpt": updated_draft.excerpt,
        "approval_state": updated_draft.approval_state,
        "workflow_state": updated_draft.workflow_state,
        "quality_gate_status": updated_draft.quality_gate_status,
        "quality_flags": updated_draft.quality_flags,
        "ai_assistance_log_size": len(updated_draft.ai_assistance_log),
        "draft_records_path": str(args.draft_records_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0
