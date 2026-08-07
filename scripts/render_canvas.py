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
import html
import json
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HMW_TEMPLATE = REPO_ROOT / "examples" / "canvas-html" / "hmw-canvas.html"
SHARED_THEME = HMW_TEMPLATE.parent / "shared" / "canvas-theme.css"

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


def extract_section(text: str, heading: str) -> str:
    """提取任意 Markdown 标题层级下、直到下一个标题的内容。"""
    match = re.search(
        rf"^#{{1,6}}\s*{re.escape(heading)}\s*$\n?(.*?)(?=^#{{1,6}}\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def extract_table_rows(text: str, heading: str) -> list[list[str]]:
    """提取 section 表格的数据行，忽略表头和分隔行。"""
    section = extract_section(text, heading)
    rows: list[list[str]] = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def extract_table(text: str, heading: str) -> dict[str, str]:
    """从确认包表格提取第一列→第二列映射。"""
    return {
        row[0]: row[1]
        for row in extract_table_rows(text, heading)
        if len(row) >= 2 and row[0] and row[1]
    }


def value_for_prefix(table: dict[str, str], prefix: str) -> str:
    """按字段英文前缀读取表格内容，兼容中文括号说明。"""
    for key, value in table.items():
        if key == prefix or key.startswith(f"{prefix}（"):
            return value
    return "未讨论"


def replace_element_text(source: str, element_id: str, value: str) -> str:
    """替换指定元素内文本，保留其标签和稳定锚点。"""
    escaped = html.escape(value)
    pattern = rf'(<(?:span|div|dd)[^>]*\bid="{re.escape(element_id)}"[^>]*>)(.*?)(</(?:span|div|dd)>)'
    return re.sub(pattern, rf"\1{escaped}\3", source, count=1, flags=re.DOTALL)


def replace_canvas_data(source: str, canvas_data: dict[str, object]) -> str:
    """用同一次确认包读取产生的 JSON 替换模板 canvas-data。"""
    serialized = json.dumps(canvas_data, ensure_ascii=False, indent=2)
    return re.sub(
        r'(<script\s+type="application/json"\s+id="canvas-data">).*?(</script>)',
        rf"\1\n{serialized}\n\2",
        source,
        count=1,
        flags=re.DOTALL,
    )


def render_hmw(template_path: Path, package: Path, state: dict) -> str:
    """把 HMW 确认包渲染进模板骨架。"""
    src = template_path.read_text(encoding="utf-8")
    pkg = read_package(package)
    hmw_state = state.get("hmw", {}) if isinstance(state, dict) else {}

    version = f"v{hmw_state.get('version', 1)}"
    confirmation_mode = hmw_state.get("confirmation_mode")
    gate = hmw_state.get("gate_recommendation") or "pending"
    authorized = str(bool(hmw_state.get("render_authorized"))).lower()

    # 4 字段
    statement_table = extract_table(pkg, "6. HMW 陈述（4 字段）")
    for anchor, key in _HMW_FIELD_MAP.items():
        value = value_for_prefix(statement_table, key)
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
        verdict = "通过" if value_for_prefix(quality_table, key).strip().startswith("通过") else "待判定"
        src = re.sub(
            r'(<div[^>]*\bid="%s"[^>]*>.*?<div class="q-verdict )verdict-pending(" data-verdict>)待判定(</div>)' % anchor,
            lambda m, v=verdict: m.group(1)
            + ("verdict-pass" if v == "通过" else "verdict-pending")
            + m.group(2)
            + v
            + m.group(3),
            src,
            count=1,
            flags=re.DOTALL,
        )

    # 想法种子：把确认包 6b 表格的行填入前 N 格
    idea_rows = [row for row in extract_table_rows(pkg, "6b. 想法种子") if len(row) >= 5]
    ideas_data: dict[str, object] = {}
    for index, row in enumerate(idea_rows[:8], start=1):
        idea_id, content, idea_type, link_to_statement, status = row[:5]
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
        ideas_data[f"idea_{index}"] = {
            "id": idea_id,
            "content": content,
            "type": idea_type,
            "link_to_statement": link_to_statement,
            "status": status,
        }

    for index in range(len(idea_rows[:8]) + 1, 9):
        ideas_data[f"idea_{index}"] = {
            "content": "",
            "type": "",
            "link_to_statement": "",
            "status": "placeholder",
        }

    coherence_rows = [row for row in extract_table_rows(pkg, "6c. 想法 ↔ HMW 对应") if len(row) >= 5]
    coherence_html = "".join(
        "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row[:5]) + "</tr>"
        for row in coherence_rows
    ) or "<tr><td colspan=\"5\">未讨论</td></tr>"
    src = re.sub(
        r'(<div id="hmw-coherence-map">\s*<table>\s*<thead>.*?</thead>\s*<tbody>).*?(</tbody>)',
        rf"\1{coherence_html}\2",
        src,
        count=1,
        flags=re.DOTALL,
    )

    headline = extract_section(pkg, "1. 一句话结论").strip().splitlines()
    if headline:
        src = replace_element_text(src, "canvas-headline", headline[0])

    gaps_rows = [row for row in extract_table_rows(pkg, "8. 缺口表") if len(row) >= 4]
    gaps = "；".join(f"{row[0]}：{row[3]}" for row in gaps_rows) or "无"
    src = replace_element_text(src, "quality-gaps", gaps)
    risks = "Gate 建议：" + gate
    src = replace_element_text(src, "quality-risks", risks)

    # 版本 / 治理
    src = re.sub(r'<span id="quality-version">[^<]*</span>', f'<span id="quality-version">{version}</span>', src)
    src = re.sub(r'<dd id="quality-version-dd">[^<]*</dd>', f'<dd id="quality-version-dd">{version}</dd>', src)
    src = re.sub(r'<dd id="quality-gate">[^<]*</dd>', f'<dd id="quality-gate">{gate}</dd>', src)
    src = re.sub(r'<dd id="quality-authorized">[^<]*</dd>', f'<dd id="quality-authorized">{authorized}</dd>', src)
    mode_label = confirmation_mode if confirmation_mode is not None else "null"
    src = re.sub(r'<dd id="quality-mode">[^<]*</dd>', f'<dd id="quality-mode">{mode_label}</dd>', src)

    canvas_match = re.search(
        r'<script\s+type="application/json"\s+id="canvas-data">(.*?)</script>', src, re.DOTALL
    )
    if not canvas_match:
        raise ValueError("template has no canvas-data")
    canvas_data = json.loads(canvas_match.group(1))
    canvas_data["version"] = version
    canvas_data["statement"] = {
        key: value_for_prefix(statement_table, key)
        for key in _HMW_FIELD_MAP.values()
    }
    canvas_data["quality"] = {
        key: value_for_prefix(quality_table, key)
        for key in ("preset_solution", "vague", "user_moment", "tension")
    }
    canvas_data["ideas"] = ideas_data
    canvas_data["coherence"] = {"map": coherence_rows}
    canvas_data["auth"] = {
        "gate_recommendation": gate,
        "render_authorized": hmw_state.get("render_authorized", False),
        "confirmation_mode": confirmation_mode,
        "override_audit": hmw_state.get("override_audit"),
    }
    src = replace_canvas_data(src, canvas_data)
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
    shared_output = args.output.parent / "shared"
    shared_output.mkdir(exist_ok=True)
    shutil.copy2(SHARED_THEME, shared_output / SHARED_THEME.name)
    print(f"rendered {args.output} ({len(rendered)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
