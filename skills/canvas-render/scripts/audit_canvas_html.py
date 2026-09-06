#!/usr/bin/env python3
"""Deterministic static audit for pratyaya Canvas HTML files."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # canvas_audit 包所在 scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # repo root（skills._engine 包，§7.6）
from canvas_audit.audit_core import audit, main, parse_args
from canvas_audit.audit_helpers import persona_source_identity
from canvas_audit.audit_models import (
    PERSONA_CONTRACT,
    Finding,
)

JOURNEY_STAGE_DATA_FIELDS = (
    "stage_index",
    "stage_name",
    "action",
    "touchpoint_system",
    "emotion",
    "pain_point",
    "opportunity",
)
JOURNEY_ANCHORS = (
    "canvas-headline",
    "journey-quality-user-perspective",
    "journey-quality-business-outcome",
    "journey-quality-pain-opportunity-visible",
    "journey-quality-no-solution-bias",
    "journey-map",
    "journey-quality",
    "quality-panel",
    "quality-version",
    "quality-approval",
    "quality-gaps",
    "quality-risks",
    "quality-caveat",
    "local-notes",
    "canvas-data",
)

__all__ = [
    "PERSONA_CONTRACT",
    "Finding",
    "JOURNEY_ANCHORS",
    "JOURNEY_STAGE_DATA_FIELDS",
    "audit",
    "main",
    "parse_args",
    "persona_source_identity",
]


def _append_render_trace(started_at, exit_code: int) -> None:
    """向被检 HTML 同目录的 .render-trace.jsonl 追加一条 L1 审计计时记录。

    trace 为派生性能数据：写入失败静默忽略，绝不影响审计结果与退出码。
    """
    try:  # 插桩不得反噬审计主流程
        import datetime
        import json

        ended_at = datetime.datetime.now().astimezone()
        argv = sys.argv[1:]
        html_path = argv[0] if argv and not argv[0].startswith("--") else None
        if not html_path:
            return
        trace_path = Path(html_path).resolve().parent / ".render-trace.jsonl"
        record = {
            "stage": "audit_l1",
            "tool": "audit_canvas_html.py",
            "html": str(Path(html_path).resolve()),
            "exit_code": exit_code,
            "status": "PASS" if exit_code == 0 else "FAIL",
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "duration_ms": int((ended_at - started_at).total_seconds() * 1000),
        }
        with trace_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    import datetime

    _t0 = datetime.datetime.now().astimezone()
    _code = main()
    _append_render_trace(_t0, _code)
    sys.exit(_code)
