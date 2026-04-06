from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from operator_api.config import OperatorApiConfig, load_operator_api_config
from operator_api.services import (
    OperatorApiPaths,
    apply_draft_review_action,
    apply_queue_review_action,
    apply_queue_schedule_action,
    apply_social_package_review_action,
    build_combined_health_payload,
    build_dashboard_payload,
    build_draft_detail_payload,
    build_draft_inbox_payload,
    build_operator_validation_payload,
    build_queue_detail_payload,
    build_queue_inbox_payload,
    build_social_package_detail_payload,
    build_social_package_inbox_payload,
)


class DraftReviewRequest(BaseModel):
    review_outcome: str
    review_notes: list[str] = Field(default_factory=list)
    reviewer_label: str | None = None


class SocialPackageReviewRequest(BaseModel):
    review_outcome: str
    review_notes: list[str] = Field(default_factory=list)
    reviewer_label: str | None = None


class QueueApproveRequest(BaseModel):
    review_outcome: str = "approved"
    review_notes: list[str] = Field(default_factory=list)
    reviewer_label: str | None = None


class QueueScheduleRequest(BaseModel):
    scheduled_for: str
    reviewer_label: str | None = None
    schedule_mode: str = "manual"


def build_app(
    config: OperatorApiConfig | None = None,
    paths: OperatorApiPaths | None = None,
) -> FastAPI:
    active_config = config or load_operator_api_config()
    active_paths = paths or OperatorApiPaths()
    app = FastAPI(
        title="Content Ops Operator API",
        docs_url="/docs" if active_config.enable_docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if active_config.enable_docs else None,
    )

    @app.get("/healthz")
    def get_healthz() -> dict[str, object]:
        return {
            "status": "ok",
            "service": "content_ops_operator_api",
        }

    def require_shared_secret(
        x_content_ops_shared_secret: str | None = Header(
            default=None,
            alias="X-Content-Ops-Shared-Secret",
        ),
    ) -> None:
        if not x_content_ops_shared_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing operator API shared secret.",
            )
        if x_content_ops_shared_secret != active_config.shared_secret:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid operator API shared secret.",
            )

    @app.get("/dashboard/summary", dependencies=[Depends(require_shared_secret)])
    def get_dashboard_summary() -> dict[str, object]:
        return build_dashboard_payload(paths=active_paths)

    @app.get("/drafts/inbox", dependencies=[Depends(require_shared_secret)])
    def get_drafts_inbox() -> dict[str, object]:
        return build_draft_inbox_payload(paths=active_paths)

    @app.get("/drafts/{draft_id}", dependencies=[Depends(require_shared_secret)])
    def get_draft_detail(draft_id: str) -> dict[str, object]:
        return _handle_value_error(lambda: build_draft_detail_payload(draft_id, paths=active_paths))

    @app.post("/drafts/{draft_id}/review", dependencies=[Depends(require_shared_secret)])
    def review_draft(draft_id: str, request: DraftReviewRequest) -> dict[str, object]:
        return _handle_value_error(
            lambda: apply_draft_review_action(
                draft_id,
                review_outcome=request.review_outcome,
                review_notes=request.review_notes,
                reviewer_label=request.reviewer_label or "operator_ui",
                paths=active_paths,
            )
        )

    @app.get("/social-packages/inbox", dependencies=[Depends(require_shared_secret)])
    def get_social_packages_inbox() -> dict[str, object]:
        return build_social_package_inbox_payload(paths=active_paths)

    @app.get("/social-packages/{social_package_id}", dependencies=[Depends(require_shared_secret)])
    def get_social_package_detail(social_package_id: str) -> dict[str, object]:
        return _handle_value_error(
            lambda: build_social_package_detail_payload(social_package_id, paths=active_paths)
        )

    @app.post("/social-packages/{social_package_id}/review", dependencies=[Depends(require_shared_secret)])
    def review_social_package(
        social_package_id: str,
        request: SocialPackageReviewRequest,
    ) -> dict[str, object]:
        return _handle_value_error(
            lambda: apply_social_package_review_action(
                social_package_id,
                review_outcome=request.review_outcome,
                review_notes=request.review_notes,
                reviewer_label=request.reviewer_label or "operator_ui",
                paths=active_paths,
            )
        )

    @app.get("/queue/inbox", dependencies=[Depends(require_shared_secret)])
    def get_queue_inbox() -> dict[str, object]:
        return build_queue_inbox_payload(paths=active_paths)

    @app.get("/queue/{queue_item_id}", dependencies=[Depends(require_shared_secret)])
    def get_queue_detail(queue_item_id: str) -> dict[str, object]:
        return _handle_value_error(lambda: build_queue_detail_payload(queue_item_id, paths=active_paths))

    @app.post("/queue/{queue_item_id}/approve", dependencies=[Depends(require_shared_secret)])
    def approve_queue_item(queue_item_id: str, request: QueueApproveRequest) -> dict[str, object]:
        return _handle_value_error(
            lambda: apply_queue_review_action(
                queue_item_id,
                review_outcome=request.review_outcome,
                review_notes=request.review_notes,
                reviewer_label=request.reviewer_label or "operator_ui",
                paths=active_paths,
            )
        )

    @app.post("/queue/{queue_item_id}/schedule", dependencies=[Depends(require_shared_secret)])
    def schedule_queue_item(queue_item_id: str, request: QueueScheduleRequest) -> dict[str, object]:
        return _handle_value_error(
            lambda: apply_queue_schedule_action(
                queue_item_id,
                scheduled_for=request.scheduled_for,
                reviewer_label=request.reviewer_label or "operator_ui",
                schedule_mode=request.schedule_mode,
                paths=active_paths,
            )
        )

    @app.get("/health/combined", dependencies=[Depends(require_shared_secret)])
    def get_combined_health() -> dict[str, object]:
        return build_combined_health_payload(paths=active_paths)

    @app.get("/validation/operator-baseline", dependencies=[Depends(require_shared_secret)])
    def get_operator_validation_baseline() -> dict[str, object]:
        return build_operator_validation_payload(paths=active_paths)

    return app


def _handle_value_error(fn):
    try:
        return fn()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
