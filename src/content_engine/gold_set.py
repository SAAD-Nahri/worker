from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from content_engine.formatting import derive_subject_anchor, format_source_item_to_draft
from content_engine.routing import RoutingDecision, recommend_routing_action
from source_engine.models import SourceItem
from source_engine.storage import SOURCE_ITEMS_PATH, load_latest_source_item


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GOLD_SET_MANIFEST_PATH = REPO_ROOT / "docs" / "execution" / "PHASE_2_GOLD_SET_V1.json"


@dataclass(frozen=True)
class GoldSetCase:
    case_id: str
    reason: str
    expected_routing_action: str
    expected_format_result: str
    source_item_id: str | None = None
    source_item: SourceItem | None = None
    expected_template_id: str | None = None
    expected_subject_anchor: str | None = None
    expected_intro_terms: tuple[str, ...] = ()
    forbidden_intro_terms: tuple[str, ...] = ()
    expected_quality_gate_status: str | None = None
    expected_required_flags: tuple[str, ...] = ()
    expected_error_fragment: str | None = None


@dataclass(frozen=True)
class GoldSetCaseResult:
    case_id: str
    passed: bool
    issues: tuple[str, ...]
    routing_action: str
    routing_reasons: tuple[str, ...]
    quality_gate_status: str | None
    quality_flags: tuple[str, ...]
    subject_anchor: str | None
    draft_id: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "issues": list(self.issues),
            "routing_action": self.routing_action,
            "routing_reasons": list(self.routing_reasons),
            "quality_gate_status": self.quality_gate_status,
            "quality_flags": list(self.quality_flags),
            "subject_anchor": self.subject_anchor,
            "draft_id": self.draft_id,
        }


def load_gold_set_cases(path: Path = DEFAULT_GOLD_SET_MANIFEST_PATH) -> list[GoldSetCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases: list[GoldSetCase] = []
    for record in payload.get("cases", []):
        source_item_payload = record.get("source_item")
        source_item = SourceItem(**source_item_payload) if source_item_payload else None
        cases.append(
            GoldSetCase(
                case_id=record["case_id"],
                reason=record["reason"],
                expected_routing_action=record["expected_routing_action"],
                expected_format_result=record.get("expected_format_result", "draft"),
                source_item_id=record.get("source_item_id"),
                source_item=source_item,
                expected_template_id=record.get("expected_template_id"),
                expected_subject_anchor=record.get("expected_subject_anchor"),
                expected_intro_terms=tuple(record.get("expected_intro_terms", [])),
                forbidden_intro_terms=tuple(record.get("forbidden_intro_terms", [])),
                expected_quality_gate_status=record.get("expected_quality_gate_status"),
                expected_required_flags=tuple(record.get("expected_required_flags", [])),
                expected_error_fragment=record.get("expected_error_fragment"),
            )
        )
    return cases


def evaluate_gold_set_cases(
    cases: list[GoldSetCase],
    source_items_path: Path = SOURCE_ITEMS_PATH,
) -> list[GoldSetCaseResult]:
    return [evaluate_gold_set_case(case, source_items_path=source_items_path) for case in cases]


def evaluate_gold_set_case(
    case: GoldSetCase,
    source_items_path: Path = SOURCE_ITEMS_PATH,
) -> GoldSetCaseResult:
    source_item = case.source_item or load_latest_source_item(case.source_item_id or "", path=source_items_path)

    try:
        draft = format_source_item_to_draft(source_item, created_at="2026-04-03T04:00:00+00:00")
    except Exception as exc:
        issues = _evaluate_error_case(case, exc)
        passed = not issues
        return GoldSetCaseResult(
            case_id=case.case_id,
            passed=passed,
            issues=tuple(issues),
            routing_action="reject_for_v1",
            routing_reasons=("formatting_error",),
            quality_gate_status=None,
            quality_flags=(),
            subject_anchor=None,
            draft_id=None,
        )

    subject_anchor = derive_subject_anchor(source_item)
    routing = recommend_routing_action(source_item, draft)
    issues = _evaluate_draft_case(case, draft, subject_anchor, routing)
    return GoldSetCaseResult(
        case_id=case.case_id,
        passed=not issues,
        issues=tuple(issues),
        routing_action=routing.action,
        routing_reasons=routing.reasons,
        quality_gate_status=draft.quality_gate_status,
        quality_flags=tuple(draft.quality_flags),
        subject_anchor=subject_anchor,
        draft_id=draft.draft_id,
    )


def build_gold_set_summary(results: list[GoldSetCaseResult]) -> dict[str, object]:
    passed = sum(result.passed for result in results)
    failed = len(results) - passed
    return {
        "case_count": len(results),
        "passed": passed,
        "failed": failed,
        "all_passed": failed == 0,
        "cases": [result.to_dict() for result in results],
    }


def _evaluate_error_case(case: GoldSetCase, exc: Exception) -> list[str]:
    issues: list[str] = []
    if case.expected_format_result != "error":
        issues.append(f"unexpected_formatting_error:{type(exc).__name__}")
        return issues
    if case.expected_routing_action != "reject_for_v1":
        issues.append(f"unexpected_expected_routing_action:{case.expected_routing_action}")
    if case.expected_error_fragment and case.expected_error_fragment not in str(exc):
        issues.append("missing_expected_error_fragment")
    return issues


def _evaluate_draft_case(
    case: GoldSetCase,
    draft,
    subject_anchor: str,
    routing: RoutingDecision,
) -> list[str]:
    issues: list[str] = []
    intro_lower = draft.intro_text.lower()

    if case.expected_format_result != "draft":
        issues.append("expected_error_but_draft_succeeded")
    if case.expected_template_id and draft.template_id != case.expected_template_id:
        issues.append("template_id_mismatch")
    if case.expected_subject_anchor and subject_anchor.lower() != case.expected_subject_anchor.lower():
        issues.append("subject_anchor_mismatch")
    if case.expected_quality_gate_status and draft.quality_gate_status != case.expected_quality_gate_status:
        issues.append("quality_gate_status_mismatch")
    if routing.action != case.expected_routing_action:
        issues.append("routing_action_mismatch")

    missing_flags = [flag for flag in case.expected_required_flags if flag not in draft.quality_flags]
    if missing_flags:
        issues.append("missing_required_flags")

    missing_terms = [term for term in case.expected_intro_terms if term.lower() not in intro_lower]
    if missing_terms:
        issues.append("missing_intro_terms")

    present_forbidden = [term for term in case.forbidden_intro_terms if term.lower() in intro_lower]
    if present_forbidden:
        issues.append("forbidden_intro_terms_present")

    return issues
