from __future__ import annotations

import argparse
import json
from pathlib import Path

from source_engine.cleaner import clean_text

from distribution_engine.publish_updates import record_blog_publish_update
from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    append_blog_facebook_mapping_records,
    append_blog_publish_records,
    append_queue_item_records,
    load_latest_blog_publish_record,
    load_latest_facebook_publish_for_social_package,
    load_latest_social_package_for_blog_publish,
)
from distribution_engine.workflow import prepare_distribution_linkage_records
from distribution_engine.wordpress_transport import (
    PostStateRequestExecutor,
    WordPressRestTransportError,
    WordPressRestPostStateExecutionResult,
    inspect_wordpress_rest_post_state,
    load_wordpress_rest_config,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect a remote WordPress post state for an existing blog publish chain, "
            "and optionally reconcile the local publish snapshot from the remote result."
        )
    )
    parser.add_argument("--blog-publish-id", required=True, help="Blog publish identifier to inspect.")
    parser.add_argument(
        "--wordpress-post-id",
        help="Optional explicit WordPress post id override. Defaults to the latest local wordpress_post_id.",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        required=True,
        help="Path to the operator-provided WordPress REST config JSON file.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the remote inspection. Without this flag the command returns a dry-run preview only.",
    )
    parser.add_argument(
        "--reconcile-local-state",
        action="store_true",
        help="Append a local publish-state snapshot based on the remote WordPress status and refresh queue/mapping state.",
    )
    parser.add_argument(
        "--schedule-mode",
        choices=["manual", "auto"],
        default="manual",
        help="Scheduling mode to use if the remote post is scheduled (future). Default: manual.",
    )
    parser.add_argument(
        "--schedule-approved-by",
        help="Optional operator or policy label that approved the remote schedule state.",
    )
    parser.add_argument(
        "--schedule-applied-by",
        help="Optional actor label that applied the remote schedule state.",
    )
    parser.add_argument(
        "--blog-publish-records-path",
        type=Path,
        default=BLOG_PUBLISH_RECORDS_PATH,
        help="Path to the append-only blog publish records file.",
    )
    parser.add_argument(
        "--social-package-records-path",
        type=Path,
        default=SOCIAL_PACKAGE_RECORDS_PATH,
        help="Path to the append-only social package records file.",
    )
    parser.add_argument(
        "--facebook-publish-records-path",
        type=Path,
        default=FACEBOOK_PUBLISH_RECORDS_PATH,
        help="Path to the append-only Facebook publish records file.",
    )
    parser.add_argument(
        "--queue-item-records-path",
        type=Path,
        default=QUEUE_ITEM_RECORDS_PATH,
        help="Path to the append-only queue item records file.",
    )
    parser.add_argument(
        "--mapping-records-path",
        type=Path,
        default=BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
        help="Path to the append-only blog/Facebook mapping records file.",
    )
    return parser


def main(argv: list[str] | None = None, request_executor: PostStateRequestExecutor | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.reconcile_local_state and not args.execute:
        parser.error("--reconcile-local-state requires --execute.")

    try:
        blog_publish_record = load_latest_blog_publish_record(
            args.blog_publish_id,
            path=args.blog_publish_records_path,
        )
        config = load_wordpress_rest_config(args.config_path)
        wordpress_post_id = _resolve_wordpress_post_id(args.wordpress_post_id, blog_publish_record.wordpress_post_id)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        inspection_result = inspect_wordpress_rest_post_state(
            wordpress_post_id,
            config,
            execute=args.execute,
            request_executor=request_executor,
        )
    except WordPressRestTransportError as exc:
        summary = {
            "blog_publish_id": blog_publish_record.blog_publish_id,
            "config_path": str(args.config_path),
            "local_wordpress_status": blog_publish_record.wordpress_status,
            "local_wordpress_post_id": blog_publish_record.wordpress_post_id,
            "requested_wordpress_post_id": wordpress_post_id,
            "reconciled": False,
            "transport_outcome": "failed",
            "error": str(exc),
        }
        print(json.dumps(summary, sort_keys=True))
        return 1

    summary = inspection_result.to_summary_dict()
    summary.update(
        {
            "blog_publish_id": blog_publish_record.blog_publish_id,
            "config_path": str(args.config_path),
            "local_wordpress_status": blog_publish_record.wordpress_status,
            "local_wordpress_post_id": blog_publish_record.wordpress_post_id,
            "reconciled": False,
        }
    )

    if not args.execute:
        print(json.dumps(summary, sort_keys=True))
        return 0

    try:
        execution_result = inspection_result.execution_result
        assert execution_result is not None
        if args.reconcile_local_state:
            updated_blog_publish = _reconcile_remote_state(
                blog_publish_record,
                execution_result,
                schedule_mode=args.schedule_mode,
                schedule_approved_by=args.schedule_approved_by,
                schedule_applied_by=args.schedule_applied_by,
            )
            append_blog_publish_records([updated_blog_publish], path=args.blog_publish_records_path)
            blog_queue, facebook_queue, mapping = _refresh_related_workflow_records(
                updated_blog_publish,
                social_package_records_path=args.social_package_records_path,
                facebook_publish_records_path=args.facebook_publish_records_path,
                queue_item_records_path=args.queue_item_records_path,
                mapping_records_path=args.mapping_records_path,
            )
            summary.update(
                {
                    "reconciled": True,
                    "reconciled_action": updated_blog_publish.wordpress_status,
                    "updated_blog_publish": {
                        "blog_publish_id": updated_blog_publish.blog_publish_id,
                        "wordpress_status": updated_blog_publish.wordpress_status,
                        "wordpress_post_id": updated_blog_publish.wordpress_post_id,
                        "wordpress_post_url": updated_blog_publish.wordpress_post_url,
                        "scheduled_for_blog": updated_blog_publish.scheduled_for_blog,
                        "published_at_blog": updated_blog_publish.published_at_blog,
                    },
                    "blog_queue_state": blog_queue.queue_state,
                    "facebook_queue_state": facebook_queue.queue_state,
                    "mapping_status": mapping.mapping_status,
                    "blog_publish_records_path": str(args.blog_publish_records_path),
                }
            )
    except (ValueError, WordPressRestTransportError) as exc:
        summary.update(
            {
                "reconciled": False,
                "reconcile_error": str(exc),
            }
        )
        print(json.dumps(summary, sort_keys=True))
        return 1

    print(json.dumps(summary, sort_keys=True))
    return 0


def _resolve_wordpress_post_id(cli_value: str | None, record_value: str | None) -> str:
    wordpress_post_id = clean_text(cli_value or "") or clean_text(record_value or "")
    if not wordpress_post_id:
        raise ValueError(
            "WordPress post-state inspection requires wordpress_post_id or a blog publish record with wordpress_post_id."
        )
    return wordpress_post_id


def _reconcile_remote_state(
    blog_publish_record,
    execution_result: WordPressRestPostStateExecutionResult,
    *,
    schedule_mode: str,
    schedule_approved_by: str | None,
    schedule_applied_by: str | None,
):
    remote_status = clean_text(execution_result.remote_status or "").lower()
    if remote_status in {"draft", "auto-draft"}:
        update_action = "draft_updated" if clean_text(blog_publish_record.wordpress_post_id or "") else "draft_created"
        return record_blog_publish_update(
            blog_publish_record,
            update_action=update_action,
            wordpress_post_id=execution_result.wordpress_post_id,
            wordpress_post_url=execution_result.wordpress_post_url,
        )
    if remote_status == "future":
        if not execution_result.remote_published_at:
            raise ValueError("Remote scheduled WordPress post is missing a usable publish timestamp.")
        return record_blog_publish_update(
            blog_publish_record,
            update_action="scheduled",
            wordpress_post_id=execution_result.wordpress_post_id,
            wordpress_post_url=execution_result.wordpress_post_url,
            schedule_mode=schedule_mode,
            schedule_approved_by=schedule_approved_by,
            schedule_applied_by=schedule_applied_by,
            scheduled_for_blog=execution_result.remote_published_at,
        )
    if remote_status == "publish":
        if not execution_result.remote_published_at:
            raise ValueError("Remote published WordPress post is missing a usable published timestamp.")
        return record_blog_publish_update(
            blog_publish_record,
            update_action="published",
            wordpress_post_id=execution_result.wordpress_post_id,
            wordpress_post_url=execution_result.wordpress_post_url,
            published_at_blog=execution_result.remote_published_at,
        )
    raise ValueError(
        f"Unsupported remote WordPress status for local reconciliation: {execution_result.remote_status or '<empty>'}"
    )


def _refresh_related_workflow_records(
    blog_publish_record,
    *,
    social_package_records_path: Path,
    facebook_publish_records_path: Path,
    queue_item_records_path: Path,
    mapping_records_path: Path,
):
    social_package = None
    try:
        social_package = load_latest_social_package_for_blog_publish(
            blog_publish_record.blog_publish_id,
            path=social_package_records_path,
        )
    except ValueError:
        social_package = None

    facebook_publish_record = None
    if social_package is not None:
        try:
            facebook_publish_record = load_latest_facebook_publish_for_social_package(
                social_package.social_package_id,
                path=facebook_publish_records_path,
            )
        except ValueError:
            facebook_publish_record = None

    blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
        blog_publish_record,
        social_package_record=social_package,
        facebook_publish_record=facebook_publish_record,
    )
    append_queue_item_records([blog_queue, facebook_queue], path=queue_item_records_path)
    append_blog_facebook_mapping_records([mapping], path=mapping_records_path)
    return blog_queue, facebook_queue, mapping
