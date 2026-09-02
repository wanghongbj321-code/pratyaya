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


if __name__ == "__main__":
    sys.exit(main())
