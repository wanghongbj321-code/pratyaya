#!/usr/bin/env python3
"""Deterministic pre-render gate for a single MVL module record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


APPROVED_REVIEW_STATUSES = {"confirmed", "validated"}
BLOCKING_GAP_SEVERITIES = {"blocker", "major"}
REQUIRED_CANVAS_FIELDS = {
    "M1": (
        "goal",
        "value",
        "success_metrics",
        "evidence",
        "boundary",
        "acceptance",
        "grouping",
    ),
    "M2": (
        "users",
        "needs",
        "pain_points",
        "most_important_outcomes",
        "current_workflow",
        "requirements",
    ),
    "M3": (
        "hmw",
        "loop_goal",
        "capability_metrics",
        "acceptance",
        "boundary",
        "solution_direction",
        "workflow_draft",
        "validation_dimensions",
    ),
    "M4": (
        "agent_team",
        "collaboration_mode",
        "workflow_final",
        "knowledge",
        "data_sources",
        "tools_skills",
        "prototype_rounds",
        "delivery_preparation",
    ),
    "M5": (
        "validation_rounds",
        "can_execute",
        "can_create_value",
        "trust_risk_controls",
        "issues_corrections",
    ),
    "M6": (
        "final_solution",
        "solution_comparison",
        "demo_summary",
        "validation_review",
        "capability_boundary",
        "applicable_scenarios",
        "optimization_space",
        "evolution_assets",
        "next_step_plan",
        "headline",
        "takeaway",
    ),
}
EMPTY_MARKERS = {"", "未讨论", "待确认", "未知", "暂无"}
AI_WORKFLOW_FIELDS = (
    "trigger",
    "steps",
    "completion_condition",
    "agent_execution_nodes",
    "human_operation_confirmation_nodes",
    "human_review_agent_execution_nodes",
    "rules",
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in EMPTY_MARKERS
    if isinstance(value, dict):
        return bool(value) and any(has_content(item) for item in value.values())
    if isinstance(value, list):
        return bool(value) and any(has_content(item) for item in value)
    return True


def validate_ai_workflow(value: Any, field_path: str) -> list[str]:
    """Require an AI workflow with all three workshop-defined node types."""
    if not isinstance(value, dict):
        return [f"{field_path} must be a structured AI workflow object"]

    reasons: list[str] = []
    for field in AI_WORKFLOW_FIELDS:
        if field not in value or not has_content(value[field]):
            reasons.append(f"missing required {field_path}.{field}")
    return reasons


def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    module_id = record.get("module_id")
    version = record.get("version")

    if module_id not in {"M1", "M2", "M3", "M4", "M5", "M6"}:
        reasons.append("invalid module_id")
    if not isinstance(version, int) or version < 1:
        reasons.append("invalid version")
    if record.get("status") not in {"review_ready", "confirmed"}:
        reasons.append("status must be review_ready or confirmed before gate check")

    canvas_fields = record.get("canvas_fields")
    if not isinstance(canvas_fields, dict):
        reasons.append("canvas_fields must be an object")
    elif module_id in REQUIRED_CANVAS_FIELDS:
        for field in REQUIRED_CANVAS_FIELDS[module_id]:
            if field not in canvas_fields or not has_content(canvas_fields[field]):
                reasons.append(f"missing required canvas_fields.{field}")
        if module_id == "M3" and "workflow_draft" in canvas_fields:
            reasons.extend(
                validate_ai_workflow(
                    canvas_fields["workflow_draft"],
                    "canvas_fields.workflow_draft",
                )
            )
        if module_id == "M4" and "workflow_final" in canvas_fields:
            reasons.extend(
                validate_ai_workflow(
                    canvas_fields["workflow_final"],
                    "canvas_fields.workflow_final",
                )
            )

    conclusions = record.get("conclusions")
    if not isinstance(conclusions, list) or not conclusions:
        reasons.append("no conclusions registered")
    else:
        for conclusion in conclusions:
            conclusion_id = conclusion.get("id", "unknown conclusion")
            if not conclusion.get("evidence_refs"):
                reasons.append(f"{conclusion_id}: missing evidence_refs")
            if conclusion.get("review_status") not in APPROVED_REVIEW_STATUSES:
                reasons.append(
                    f"{conclusion_id}: review_status must be confirmed or validated"
                )

    gaps = record.get("gaps")
    accepted_gap_ids: set[str] = set()
    approval = record.get("approval")
    if isinstance(approval, dict) and isinstance(
        approval.get("accepted_gap_ids"), list
    ):
        accepted_gap_ids = set(approval["accepted_gap_ids"])

    if not isinstance(gaps, list):
        reasons.append("gaps must be an array")
    else:
        for gap in gaps:
            severity = gap.get("severity")
            status = gap.get("status")
            gap_id = gap.get("id", "unknown gap")
            topic = gap.get("topic", "")
            if severity in BLOCKING_GAP_SEVERITIES and status == "open":
                reasons.append(f"open {severity} {gap_id}: {topic}")
            elif severity == "minor" and status == "open":
                reasons.append(
                    f"open minor {gap_id}: resolve it or mark accepted_risk"
                )
            if severity == "blocker" and status == "accepted_risk":
                reasons.append(
                    f"blocker {gap_id} cannot be accepted as residual risk"
                )
            if status == "accepted_risk" and gap_id not in accepted_gap_ids:
                reasons.append(
                    f"accepted_risk {gap_id} is not acknowledged in approval"
                )
            if not gap.get("impact"):
                reasons.append(f"{gap_id}: missing impact")
            if not gap.get("question"):
                reasons.append(f"{gap_id}: missing question")

    inferences = record.get("inferences")
    if not isinstance(inferences, list):
        reasons.append("inferences must be an array")
    else:
        for inference in inferences:
            if (
                inference.get("impact") == "core"
                and inference.get("status") == "pending"
            ):
                reasons.append(
                    f"{inference.get('id', 'unknown inference')}: core inference pending"
                )

    # ── Alignment gate ──────────────────────────────────────────────
    alignment = record.get("alignment")
    if not isinstance(alignment, dict):
        reasons.append("alignment is missing")
    else:
        if not isinstance(alignment.get("consensus"), list):
            reasons.append("alignment.consensus must be an array")
        if not isinstance(alignment.get("decisions"), list):
            reasons.append("alignment.decisions must be an array")

        divergences = alignment.get("divergences")
        if not isinstance(divergences, list):
            reasons.append("alignment.divergences must be an array")
        else:
            accepted_divergence_ids: set[str] = set()
            approval_obj = record.get("approval")
            if isinstance(approval_obj, dict):
                for conf in approval_obj.get("confirmed_by", []):
                    if isinstance(conf, dict):
                        accepted_divergence_ids.add(conf.get("name", ""))

            for divergence in divergences:
                div_id = divergence.get("id", "unknown divergence")
                severity = divergence.get("severity")
                res_status = divergence.get("resolution_status")

                if severity in BLOCKING_GAP_SEVERITIES and res_status == "open":
                    reasons.append(
                        f"open {severity} alignment divergence {div_id}: "
                        f"{divergence.get('topic', 'unknown topic')}"
                    )
                if res_status == "accepted_risk":
                    accepted_by = divergence.get("accepted_by", [])
                    if not accepted_by:
                        reasons.append(
                            f"{div_id}: accepted_risk divergence missing accepted_by"
                        )
                    for name in accepted_by:
                        if name not in accepted_divergence_ids:
                            reasons.append(
                                f"{div_id}: {name} accepted risk but is not in approval.confirmed_by"
                            )

    if not isinstance(approval, dict):
        reasons.append("approval is missing")
    else:
        if approval.get("version") != version:
            reasons.append("approval.version does not match current version")
        confirmed_by = approval.get("confirmed_by")
        if not isinstance(confirmed_by, list) or not confirmed_by:
            reasons.append("no human confirmer registered")
        else:
            for confirmer in confirmed_by:
                if not isinstance(confirmer, dict) or not all(
                    isinstance(confirmer.get(field), str)
                    and confirmer[field].strip()
                    for field in ("name", "role", "confirmed_at")
                ):
                    reasons.append(
                        "each confirmer requires non-empty name, role and confirmed_at"
                    )

    return {
        "module_id": module_id,
        "version": version,
        "render_allowed": not reasons,
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether an MVL module record may be formally rendered."
    )
    parser.add_argument("record", type=Path, help="Path to modules/module-N.json")
    args = parser.parse_args()

    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            raise ValueError("module record root must be an object")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        result = {
            "module_id": None,
            "version": None,
            "render_allowed": False,
            "reasons": [f"invalid input: {exc}"],
        }
        print(json.dumps(result, ensure_ascii=False))
        return 1

    result = evaluate(record)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["render_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
