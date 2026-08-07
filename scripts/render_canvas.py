#!/usr/bin/env python3
"""Render HMW / GC / persona formal canvas HTML from a confirmation package + template.

用途：把确认包（如 `examples/modules/HMW-v1.md`）渲染为正式 Canvas HTML，
供 smoke test / 视觉验收使用。产物写入 `--output` 指定路径（建议使用临时文件）。

设计约束：
- 本脚本是**渲染辅助工具**，把确认包内容映射进示例模板骨架；
  正式工作流仍由 `canvas-render` Skill 编排（LLM 阅读 render-contract 现场生成）。
- 渲染结果必须通过 `audit_canvas_html.py --type hmw --template ...` 双 Gate 审计。
- 不修改确认包、state.json 或任何仓库文件。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HMW_TEMPLATE = REPO_ROOT / "examples" / "canvas-html" / "hmw-canvas.html"

# 确认包 section → 模板锚点的映射（HMW）
_HMW_FIELD_MAP = {
    "hmw-situation": "situation",
    "hmw-question": "question",
    "hmw-for": "for",
    "hmw-sothat": "so_that",
}


def read_package(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_state(path: Path | None) -> dict:
    if path is None:
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def extract_table(text: str, heading: str) -> dict[str, str]:
    """从确认包 Markdown 中提取 `## {heading}` 下表格的第一列→第二列映射（粗糙但够用）。"""
    result: dict[str, str] = {}
    match = re.search(rf"^##\s*{heading}\s*$.*?(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        return result
    for row in re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", match.group(0), re.MULTILINE):
        key = row[0].strip()
        value = row[1].strip()
        if key and value and "…" not in value:
            result[key] = value
    return result


def render_hmw(template_path: Path, package: Path, state: dict) -> str:
    """把 HMW 确认包渲染进模板骨架。"""
    src = template_path.read_text(encoding="utf-8")
    pkg = read_package(package)
    hmw_state = state.get("hmw", {}) if isinstance(state, dict) else {}

    version = f"v{hmw_state.get('version', 1)}"
    confirmation_mode = hmw_state.get("confirmation_mode") or "null"
    gate = hmw_state.get("gate_recommendation") or "pending"
    authorized = str(bool(hmw_state.get("render_authorized"))).lower()

    # 4 字段
    statement_table = extract_table(pkg, "6. HMW 陈述（4 字段）")
    for anchor, key in _HMW_FIELD_MAP.items():
        value = statement_table.get(key, "未讨论")
        src = re.sub(
            r'(id="%s"[^>]*>.*?<b>[^<]+</b>)[^<]*(</span>)' % anchor,
            lambda m, v=value: m.group(1) + v + m.group(2),
            src,
            count=1,
        )

    # 质量鉴别
    quality_table = extract_table(pkg, "6a. 质量鉴别")
    q_map = {
        "hmw-quality-preset": "preset_solution（预设解法）",
        "hmw-quality-vague": "vague（含糊）",
        "hmw-quality-moment": "user_moment（用户时刻）",
        "hmw-quality-tension": "tension（张力）",
    }
    for anchor, key in q_map.items():
        verdict = "通过" if quality_table.get(key, "").strip().startswith("通过") else "待判定"
        src = re.sub(
            r'(id="%s"[^>]*>)\s*<div class="q-verdict verdict-pending" data-verdict>待判定</div>' % anchor,
            lambda m, v=verdict: m.group(1) + f'<div class="q-verdict verdict-pass" data-verdict>{v}</div>'
            if v == "通过" else m.group(1) + f'<div class="q-verdict verdict-pending" data-verdict>{v}</div>',
            src,
            count=1,
        )

    # 想法种子：把确认包 6b 表格的行填入前 N 格
    ideas_table = extract_table(pkg, "6b. 想法种子")
    idea_rows = [
        (key, value) for key, value in ideas_table.items() if key.startswith("HMW-Idea")
    ]
    for index, (idea_id, content) in enumerate(idea_rows[:8], start=1):
        anchor = f"hmw-idea-{index}"
        content = re.sub(r"\s+", " ", content).strip() or "未讨论"
        src = re.sub(
            r'(<div class="idea" id="%s" data-state="placeholder">)' % anchor,
            f'<div class="idea" id="{anchor}" data-state="discussed">',
            src,
            count=1,
        )
        src = re.sub(
            r'(id="%s"[^>]*>.*?<div class="idea-fill">)[^<]*(</div>)' % anchor,
            lambda m, v=content: m.group(1) + v + m.group(2),
            src,
            count=1,
            flags=re.S,
        )

    # 版本 / 治理
    src = re.sub(r'<span id="quality-version">[^<]*</span>', f'<span id="quality-version">{version}</span>', src)
    src = re.sub(r'<dd id="quality-version-dd">[^<]*</dd>', f'<dd id="quality-version-dd">{version}</dd>', src)
    src = re.sub(r'<dd id="quality-gate">[^<]*</dd>', f'<dd id="quality-gate">{gate}</dd>', src)
    src = re.sub(r'<dd id="quality-authorized">[^<]*</dd>', f'<dd id="quality-authorized">{authorized}</dd>', src)
    src = re.sub(r'<dd id="quality-mode">[^<]*</dd>', f'<dd id="quality-mode">{confirmation_mode}</dd>', src)

    # canvas-data：版本 + auth
    src = re.sub(r'"version":\s*"[^"]*",\s*\n\s*"schema_version_target"', f'"version": "{version}",\n  "schema_version_target"', src)
    src = re.sub(
        r'"gate_recommendation":\s*"[^"]*",\s*\n\s*"render_authorized":\s*(?:true|false),\s*\n\s*"confirmation_mode":\s*(?:null|"[^"]*"),\s*\n\s*"override_audit":\s*null',
        f'"gate_recommendation": "{gate}",\n    "render_authorized": {authorized},\n    "confirmation_mode": "{confirmation_mode}",\n    "override_audit": null',
        src,
    )
    return src


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="confirmation package (HMW-v{N}.md)")
    parser.add_argument("--state", type=Path, help="project state.json")
    parser.add_argument("--type", dest="canvas_type", choices=("hmw",), default="hmw", help="canvas type (当前仅 hmw)")
    parser.add_argument("--template", type=Path, default=HMW_TEMPLATE, help="HMW 示例模板路径")
    parser.add_argument("--output", required=True, type=Path, help="输出 HTML 路径（建议临时文件）")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    state = read_state(args.state)
    rendered = render_hmw(args.template, args.source, state)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"rendered {args.output} ({len(rendered)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
