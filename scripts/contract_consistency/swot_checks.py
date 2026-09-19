"""Static consistency checks for the SWOT/TOWS integration."""
from __future__ import annotations

import json
import re

from .models import *  # noqa: F403


def _finding(code: str, where: str, message: str) -> Finding:
    return Finding(code, "error", where, message, "修正后重新运行契约一致性检查")


def check_swot_skill_sync(ctx: CheckContext) -> list[Finding]:
    expected = ("swot-distill", "swot-gate")
    skills = ctx.plugin.get("skills", [])
    findings = []
    if not all(isinstance(skills, list) and f"./skills/{name}" in skills for name in expected):
        findings.append(_finding("SWOT_SKILL_SYNC", PLUGIN_JSON, "plugin.json 未完整注册两个 SWOT Skill"))
    agent = read_text(ctx.root / AGENTS_DIR / "pratyaya.md")
    for name in expected:
        if not (ctx.root / SKILLS_DIR / name / "SKILL.md").is_file() or name not in agent:
            findings.append(_finding("SWOT_SKILL_SYNC", name, "Skill 文件或 Agent 引用缺失"))
    return findings


def check_swot_gate_table(ctx: CheckContext) -> list[Finding]:
    path = ctx.root / "skills/swot-gate/references/SWOT-gate.md"
    text = read_text(path)
    ids = set(re.findall(r"`?(SWOT-GATE-0[1-8])`?", text))
    return [] if ids == {f"SWOT-GATE-0{i}" for i in range(1, 9)} else [_finding("SWOT_GATE_TABLE", str(path), "Gate 表必须包含 SWOT-GATE-01 至 08")]


def check_swot_section_sync(ctx: CheckContext) -> list[Finding]:
    path = ctx.root / "skills/swot-distill/SKILL.md"
    text = read_text(path)
    headings = re.findall(r"^## (\d+)\. ", text, re.MULTILINE)
    expected = [str(i) for i in range(1, 13)]
    return [] if headings[:12] == expected and "## 12. Gate 与用户决策" in text else [_finding("SWOT_SECTION_SYNC", str(path), "确认包必须固定为 12 节且第 12 节为治理")]


def check_swot_template_profile(ctx: CheckContext) -> list[Finding]:
    path = ctx.root / "skills/canvas-render/examples/swot-canvas.html"
    text = read_text(path)
    required = ("swot-topic-summary", "swot-quadrants", "swot-tows", "swot-comparison", "swot-handover", "swot-supplementary")
    missing = [anchor for anchor in required if f'id="{anchor}"' not in text]
    return [_finding("SWOT_TEMPLATE_PROFILE", str(path), f"模板缺少锚点：{', '.join(missing)}")] if missing else []


def check_swot_state_schema(ctx: CheckContext) -> list[Finding]:
    path = ctx.root / "schemas/state.schema.json"
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return [_finding("SWOT_STATE_SCHEMA", str(path), "state schema 不是合法 JSON")]
    defs = data.get("$defs", {})
    props = data.get("properties", {})
    if "swot" not in props or "swot_instance_map" not in defs or "swot_instance_state" not in defs:
        return [_finding("SWOT_STATE_SCHEMA", str(path), "schema 缺少 SWOT 实例定义或顶层入口")]
    return []
