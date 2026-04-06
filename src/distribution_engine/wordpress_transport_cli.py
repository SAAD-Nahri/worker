from __future__ import annotations

import argparse
import json
from pathlib import Path

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
from distribution_engine.transport_retry import TransportRetryPolicy
from distribution_engine.wordpress_transport import (
    RequestExecutor,
    WordPressDraftSyncResult,
    WordPressRestTransportError,
    build_wordpress_rest_request,
    load_wordpress_rest_config,
    sync_wordpress_rest_draft,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview or execute a WordPress REST draft sync from a prepared local blog publish record."
    )
    parser.add_argument("--blog-publish-id", required=True, help="Prepared local blog_publish_id to sync.")
    parser.add_argument(
        "--config-path",
        type=Path,
        required=True,
        help="Path to the operator-provided WordPress REST config JSON file.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the remote draft sync. Without this flag the command returns a dry-run preview only.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=1,
        help="Maximum transport attempts for retryable WordPress REST failures. Default: 1.",
    )
    parser.add_argument(
        "--initial-delay-seconds",
        type=float,
        default=0.0,
        help="Initial retry delay in seconds for retryable transport failures. Default: 0.0.",
    )
    parser.add_argument(
        "--backoff-multiplier",
        type=float,
        default=2.0,
        help="Backoff multiplier applied between retry attempts. Default: 2.0.",
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


def main(argv: list[str] | None = None, request_executor: RequestExecutor | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        blog_publish_record = load_latest_blog_publish_record(
            args.blog_publish_id,
            path=args.blog_publish_records_path,
        )
        config = load_wordpress_rest_config(args.config_path)
        request = build_wordpress_rest_request(blog_publish_record, config)
        retry_policy = TransportRetryPolicy(
            max_attempts=args.max_attempts,
            initial_delay_seconds=args.initial_delay_seconds,
            backoff_multiplier=args.backoff_multiplier,
        )
    except ValueError as exc:
        parser.error(str(exc))

    if not args.execute:
        preview_result = WordPressDraftSyncResult(
            execution_mode="dry_run",
            request=request,
        )
        summary = preview_result.to_summary_dict()
        summary["blog_publish_id"] = blog_publish_record.blog_publish_id
        summary["config_path"] = str(args.config_path)
        summary["retry_policy"] = {
            "max_attempts": retry_policy.max_attempts,
            "initial_delay_seconds": retry_policy.initial_delay_seconds,
            "backoff_multiplier": retry_policy.backoff_multiplier,
        }
        print(json.dumps(summary, sort_keys=True))
        return 0

    try:
        sync_result = sync_wordpress_rest_draft(
            blog_publish_record,
            config,
            execute=True,
            retry_policy=retry_policy,
            request_executor=request_executor,
        )
        updated_blog_publish = sync_result.updated_blog_publish_record
        execution_result = sync_result.execution_result
        exit_code = 0
        transport_outcome = "success"
        error_message = None
    except WordPressRestTransportError as exc:
        updated_blog_publish = record_blog_publish_update(
            blog_publish_record,
            update_action="failed",
            error_message=str(exc),
        )
        execution_result = None
        exit_code = 1
        transport_outcome = "failed"
        error_message = str(exc)

    append_blog_publish_records([updated_blog_publish], path=args.blog_publish_records_path)
    blog_queue, facebook_queue, mapping = _refresh_related_workflow_records(
        updated_blog_publish,
        social_package_records_path=args.social_package_records_path,
        facebook_publish_records_path=args.facebook_publish_records_path,
        queue_item_records_path=args.queue_item_records_path,
        mapping_records_path=args.mapping_records_path,
    )

    summary_result = WordPressDraftSyncResult(
        execution_mode="execute",
        request=request,
        updated_blog_publish_record=updated_blog_publish,
        execution_result=execution_result,
    )
    summary = summary_result.to_summary_dict()
    summary.update(
        {
            "blog_publish_id": updated_blog_publish.blog_publish_id,
            "transport_outcome": transport_outcome,
            "error": error_message,
            "blog_queue_state": blog_queue.queue_state,
            "facebook_queue_state": facebook_queue.queue_state,
            "mapping_status": mapping.mapping_status,
            "blog_publish_records_path": str(args.blog_publish_records_path),
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
