#!/usr/bin/env python3
"""Audit an MVL Canvas HTML file for structure and offline safety.

Supports two page types:
- data-page-type="global": the six-section MAAU global canvas.
- data-page-type="module-detail": per-module detail canvas with module-specific sections.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


GLOBAL_REQUIRED_IDS = {
    "canvas-header",
    "intent",
    "intent-goal",
    "intent-value",
    "intent-success-metrics",
    "user",
    "user-users",
    "user-needs",
    "user-pain-points",
    "user-most-important-outcomes",
    "agent-team",
    "agent-team-roles",
    "agent-team-collaboration",
    "workflow",
    "workflow-steps",
    "workflow-automation",
    "workflow-human-checkpoints",
    "workflow-human-agent-nodes",
    "workflow-rules",
    "context",
    "context-knowledge",
    "context-data-sources",
    "context-tools-skills",
    "validation",
    "validation-executable",
    "validation-value",
    "validation-evolution",
    "quality-panel",
    "alignment-consensus",
    "alignment-divergences",
    "alignment-decisions",
    "local-notes",
    "canvas-data",
}

MODULE_DETAIL_REQUIRED_IDS = {
    "canvas-header",
    "module-summary",
    "module-summary-headline",
    "module-summary-overview",
    "module-outputs",
    "module-conclusions",
    "conclusions-table",
    "module-evidence",
    "evidence-list",
    "module-gaps",
    "gaps-table",
    "inferences-table",
    "quality-panel",
    "alignment-consensus",
    "alignment-divergences",
    "alignment-decisions",
    "local-notes",
    "canvas-data",
}

VALID_MODULES = {"M1", "M2", "M3", "M4", "M5", "M6"}


class CanvasInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.tags: list[str] = []
        self.body_attrs: dict[str, str] = {}
        self.external_resources: list[str] = []
        self.local_notes_editable = False
        self.canvas_data_type = ""
        self.canvas_data_parts: list[str] = []
        self._in_canvas_data = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {key.lower(): value or "" for key, value in attrs}
        self.tags.append(tag)

        element_id = values.get("id", "")
        if element_id:
            self.ids.add(element_id)

        if tag == "body":
            self.body_attrs = values
        if element_id == "local-notes":
            self.local_notes_editable = values.get("contenteditable", "").lower() == "true"
        if tag == "script" and element_id == "canvas-data":
            self._in_canvas_data = True
            self.canvas_data_type = values.get("type", "").lower()

        for attribute in ("src", "href"):
            value = values.get(attribute, "").strip()
            if re.match(r"^(?:https?:)?//", value, flags=re.IGNORECASE):
                self.external_resources.append(value)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._in_canvas_data:
            self._in_canvas_data = False

    def handle_data(self, data: str) -> None:
        if self._in_canvas_data:
            self.canvas_data_parts.append(data)


def audit(path: Path) -> dict[str, object]:
    errors: list[str] = []
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {"path": str(path), "valid": False, "errors": [f"cannot read UTF-8 HTML: {exc}"]}

    inspector = CanvasInspector()
    try:
        inspector.feed(source)
    except Exception as exc:  # HTMLParser errors are uncommon, but must be reported.
        errors.append(f"HTML parse error: {exc}")

    page_type = inspector.body_attrs.get("data-page-type", "").strip()
    if page_type == "global":
        required_ids = GLOBAL_REQUIRED_IDS
    elif page_type == "module-detail":
        required_ids = MODULE_DETAIL_REQUIRED_IDS
    else:
        errors.append('body data-page-type must be "global" or "module-detail"')
        required_ids = set()

    for element_id in sorted(required_ids - inspector.ids):
        errors.append(f"missing required id: {element_id}")

    mode = inspector.body_attrs.get("data-mode", "")
    if mode not in {"formal", "draft"}:
        errors.append("body data-mode must be formal or draft")

    version = inspector.body_attrs.get("data-version", "").strip()
    if not version:
        errors.append("body data-version is required")

    module = inspector.body_attrs.get("data-module", "").strip()
    if page_type == "module-detail":
        if module not in VALID_MODULES:
            errors.append(f"body data-module must be one of {sorted(VALID_MODULES)} for module-detail pages")

    if not inspector.local_notes_editable:
        errors.append("local-notes must have contenteditable=true")
    if inspector.canvas_data_type != "application/json":
        errors.append("canvas-data must use type=application/json")
    else:
        embedded = "".join(inspector.canvas_data_parts).strip()
        try:
            payload = json.loads(embedded)
            if not isinstance(payload, dict):
                errors.append("canvas-data JSON must be an object")
        except json.JSONDecodeError as exc:
            errors.append(f"canvas-data contains invalid JSON: {exc}")

    if "iframe" in inspector.tags:
        errors.append("iframe is forbidden for local Canvas composition")
    if re.search(r"\bfetch\s*\(", source, flags=re.IGNORECASE):
        errors.append("fetch is forbidden in offline Canvas HTML")
    if inspector.external_resources:
        errors.append(
            "external resources are forbidden: " + ", ".join(sorted(set(inspector.external_resources)))
        )
    if "@media print" not in source.lower():
        errors.append("@media print rules are required")

    return {"path": str(path), "valid": not errors, "errors": errors}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            json.dumps(
                {"valid": False, "errors": ["usage: audit_canvas_html.py HTML_FILE"]},
                ensure_ascii=False,
            )
        )
        return 1

    result = audit(Path(argv[1]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
