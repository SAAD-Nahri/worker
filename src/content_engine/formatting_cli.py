from __future__ import annotations

import argparse
import json
from pathlib import Path

from content_engine.formatting import format_source_item_to_draft
from content_engine.routing import recommend_routing_action
from content_engine.storage import DRAFT_RECORDS_PATH, append_draft_records
from content_engine.templates import get_blog_template_contract, list_blog_template_contracts
from source_engine.storage import SOURCE_ITEMS_PATH, load_latest_source_item


def build_parser() -> argparse.ArgumentParser:
    available_template_ids = sorted(contract.template_id for contract in list_blog_template_contracts())
    parser = argparse.ArgumentParser(description="Create a structured draft record from a source item.")
    parser.add_argument("--source-item-id", required=True, help="Source item identifier to convert into a draft.")
    parser.add_argument(
        "--template-id",
        choices=available_template_ids,
        help="Optional explicit template override. Defaults to the source item's template suggestion.",
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
        source_item = load_latest_source_item(args.source_item_id, path=args.source_items_path)
        template_contract = get_blog_template_contract(args.template_id) if args.template_id else None
        draft = format_source_item_to_draft(source_item, template_contract=template_contract)
        routing = recommend_routing_action(source_item, draft)
        append_draft_records([draft], path=args.draft_records_path)
    except ValueError as exc:
        parser.error(str(exc))

    summary = {
        "draft_id": draft.draft_id,
        "source_item_id": draft.source_item_id,
        "template_id": draft.template_id,
        "category": draft.category,
        "quality_gate_status": draft.quality_gate_status,
        "derivative_risk_level": draft.derivative_risk_level,
        "quality_flags": draft.quality_flags,
        "routing_action": routing.action,
        "routing_reasons": list(routing.reasons),
        "draft_records_path": str(args.draft_records_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0
