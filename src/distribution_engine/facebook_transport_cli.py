from __future__ import annotations

import argparse
import json
from pathlib import Path

from distribution_engine.facebook_transport import (
    FacebookGraphSyncResult,
    FacebookGraphTransportError,
    FacebookRequestExecutor,
    sync_facebook_graph_post,
    load_facebook_graph_config,
)
from distribution_engine.facebook_publish_updates import record_facebook_publish_update
from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    append_blog_facebook_mapping_records,
    append_facebook_publish_records,
    append_queue_item_records,
    load_latest_blog_publish_record,
    load_latest_facebook_publish_for_social_package,
    load_latest_social_package_record,
)
from distribution_engine.transport_retry import TransportRetryPolicy
from distribution_engine.workflow import prepare_distribution_linkage_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview or execute a Facebook Graph Page-post transport from an approved social package."
    )
    parser.add_argument("--social-package-id", required=True, help="Approved social package to transport.")
    parser.add_argument(
        "--action",
        required=True,
        choices=["published", "scheduled"],
        help="Remote Facebook transport action to prepare or execute.",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        required=True,
        help="Path to the operator-provided Facebook Graph config JSON file.",
    )
    parser.add_argument(
        "--scheduled-for-facebook",
        help="Required for scheduled actions. ISO timestamp for the Facebook post schedule time.",
    )
    parser.add_argument(
        "--schedule-mode",
        choices=["manual", "auto"],
        help="Required for scheduled actions. Use manual for operator scheduling or auto for policy-approved auto scheduling.",
    )
    parser.add_argument(
        "--schedule-approved-by",
        help="Operator or policy label that approved the schedule decision.",
    )
    parser.add_argument(
        "--schedule-applied-by",
        help="Actor that applied the schedule. Use system_auto_scheduler for auto scheduling.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the remote Graph request. Without this flag the command returns a dry-run preview only.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=1,
        help="Maximum transport attempts for retryable Facebook Graph failures. Default: 1.",
    )
    parser.add_argument(
        "--initial-delay-seconds",
        type=float,
        default=0.0,
        help="Initial retry delay in seconds for retryable Facebook Graph failures. Default: 0.0.",
    )
    parser.add_argument(
        "--backoff-multiplier",
        type=float,
        default=2.0,
        help="Backoff multiplier applied between retry attempts. Default: 2.0.",
    )
    parser.add_argument(
        "--social-package-records-path",
        type=Path,
        default=SOCIAL_PACKAGE_RECORDS_PATH,
        help="Path to the append-only social package records file.",
    )
    parser.add_argument(
        "--blog-publish-records-path",
        type=Path,
        default=BLOG_PUBLISH_RECORDS_PATH,
        help="Path to the append-only blog publish records file.",
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


def main(argv: list[str] | None = None, request_executor: FacebookRequestExecutor | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        social_package_record = load_latest_social_package_record(
            args.social_package_id,
            path=args.social_package_records_path,
        )
        if not social_package_record.blog_publish_id:
            raise ValueError("Facebook transport requires a social package linked to blog_publish_id.")
        blog_publish_record = load_latest_blog_publish_record(
            social_package_record.blog_publish_id,
            path=args.blog_publish_records_path,
        )
        config = load_facebook_graph_config(args.config_path)
        retry_policy = TransportRetryPolicy(
            max_attempts=args.max_attempts,
            initial_delay_seconds=args.initial_delay_seconds,
            backoff_multiplier=args.backoff_multiplier,
        )
        existing_publish_record = None
        try:
            existing_publish_record = load_latest_facebook_publish_for_social_package(
                social_package_record.social_package_id,
                path=args.facebook_publish_records_path,
            )
        except ValueError:
            existing_publish_record = None
    except ValueError as exc:
        parser.error(str(exc))

    if not args.execute:
        try:
            summary_result = sync_facebook_graph_post(
                social_package_record,
                blog_publish_record,
                config,
                action=args.action,
                scheduled_for_facebook=args.scheduled_for_facebook,
                execute=False,
                existing_publish_record=existing_publish_record,
            )
        except ValueError as exc:
            parser.error(str(exc))
        summary = summary_result.to_summary_dict()
        summary["social_package_id"] = social_package_record.social_package_id
        summary["config_path"] = str(args.config_path)
        summary["retry_policy"] = {
            "max_attempts": retry_policy.max_attempts,
            "initial_delay_seconds": retry_policy.initial_delay_seconds,
            "backoff_multiplier": retry_policy.backoff_multiplier,
        }
        print(json.dumps(summary, sort_keys=True))
        return 0

    try:
        sync_result = sync_facebook_graph_post(
            social_package_record,
            blog_publish_record,
            config,
            action=args.action,
            existing_publish_record=existing_publish_record,
            scheduled_for_facebook=args.scheduled_for_facebook,
            execute=True,
            schedule_mode=args.schedule_mode,
            schedule_approved_by=args.schedule_approved_by,
            schedule_applied_by=args.schedule_applied_by,
            retry_policy=retry_policy,
            request_executor=request_executor,
        )
        updated_facebook_publish = sync_result.updated_facebook_publish_record
        execution_result = sync_result.execution_result
        exit_code = 0
        transport_outcome = "success"
        error_message = None
        request = sync_result.request
    except FacebookGraphTransportError as exc:
        failed_preview = sync_facebook_graph_post(
            social_package_record,
            blog_publish_record,
            config,
            action=args.action,
            scheduled_for_facebook=args.scheduled_for_facebook,
            execute=False,
            existing_publish_record=existing_publish_record,
        )
        request = failed_preview.request
        updated_facebook_publish = record_facebook_publish_update(
            social_package_record,
            blog_publish_record,
            update_action="failed",
            existing_publish_record=existing_publish_record,
            error_message=str(exc),
        )
        execution_result = None
        exit_code = 1
        transport_outcome = "failed"
        error_message = str(exc)
    except ValueError as exc:
        parser.error(str(exc))

    append_facebook_publish_records([updated_facebook_publish], path=args.facebook_publish_records_path)
    blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
        blog_publish_record,
        social_package_record=social_package_record,
        facebook_publish_record=updated_facebook_publish,
    )
    append_queue_item_records([blog_queue, facebook_queue], path=args.queue_item_records_path)
    append_blog_facebook_mapping_records([mapping], path=args.mapping_records_path)

    summary_result = FacebookGraphSyncResult(
        execution_mode="execute",
        request=request,
        updated_facebook_publish_record=updated_facebook_publish,
        execution_result=execution_result,
    )
    summary = summary_result.to_summary_dict()
    summary.update(
        {
            "social_package_id": social_package_record.social_package_id,
            "facebook_publish_id": updated_facebook_publish.facebook_publish_id,
            "transport_outcome": transport_outcome,
            "error": error_message,
            "facebook_queue_state": facebook_queue.queue_state,
            "mapping_status": mapping.mapping_status,
            "facebook_publish_records_path": str(args.facebook_publish_records_path),
            "config_path": str(args.config_path),
            "retry_policy": {
                "max_attempts": retry_policy.max_attempts,
                "initial_delay_seconds": retry_policy.initial_delay_seconds,
                "backoff_multiplier": retry_policy.backoff_multiplier,
            },
        }
    )
    print(json.dumps(summary, sort_keys=True))
    return exit_code
