#!/usr/bin/env python3
"""画布注册表解析器（v3.3.0 P2 前置）。

从主 Agent 文档（``agents/pratyaya.md``）中解析「画布注册表」表格，供契约一致性
检查与后续引擎共用，避免注册表在文档与代码之间出现第二份事实源。

设计原则
--------
* **纯标准库、零副作用**：只做文本解析，不写文件、不读文件系统状态（P4 依赖边界
  §7.6 要求注册表模块可被 audit / contract checker / engine 三方安全导入）。
* **用 HTML 注释标记表格边界**（``<!-- canvas-registry:begin -->`` … ``:end -->``），
  不依赖章节标题字面量——后者会随文档重构而失效，正是本模块要消除的脆弱性。
* 表头列名即字段名；新增列只需扩展 ``FIELDS``。

参考：``internal/pratyaya-internal/docs/dev-plan/主Agent薄控制面重构与共享画布引擎执行计划-20260902.md`` §3 / §8.3
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

BEGIN = "<!-- canvas-registry:begin -->"
END = "<!-- canvas-registry:end -->"

# 注册表列名（与 agent md 表头一一对应，顺序敏感）
FIELDS: tuple[str, ...] = (
    "canvas_id",
    "canvas_type",
    "audit_type",
    "state_key",
    "file_prefix",
    "output_prefix",
    "distill",
    "gate",
    "gate_id_prefix",
    "page_type",
    "triggers",
)


@dataclass(frozen=True)
class CanvasRow:
    """注册表的一行＝一个画布条目。"""

    canvas_id: str
    canvas_type: str
    audit_type: str
    state_key: str
    file_prefix: str
    output_prefix: str
    distill: str
    gate: str
    gate_id_prefix: str
    page_type: str
    triggers: str

    def value(self, field: str) -> str:
        """按字段名取值（字段不存在时抛 AttributeError，便于早失败）。"""
        return str(getattr(self, field))


def _strip_backticks(cell: str) -> str:
    """去掉单元格的 Markdown 反引号，返回裸值。"""
    return cell.replace("`", "").strip()


def _split_row(line: str) -> list[str]:
    """拆分 Markdown 表格的一行为单元格列表。"""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_separator(cells: list[str]) -> bool:
    """判断是否为表头下的分隔行（如 ``|---|---|``）。"""
    joined = "".join(cells)
    return bool(joined) and set(joined) <= set("-: ")


def parse_canvas_registry(text: str) -> list[CanvasRow]:
    """从任意文本中解析画布注册表。

    找不到标记块、或块内无有效数据行时返回空列表——由调用方据此给出明确报错，
    本模块不抛异常，保持零副作用。
    """
    start = text.find(BEGIN)
    end = text.find(END)
    if start == -1 or end == -1 or end <= start:
        return []

    block = text[start + len(BEGIN) : end]
    rows: list[CanvasRow] = []
    header_seen = False

    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = _split_row(line)
        if not header_seen:
            header_seen = True  # 第一行表格即表头
            continue
        if _is_separator(cells):
            continue
        if len(cells) != len(FIELDS):
            continue
        values = {f: _strip_backticks(c) for f, c in zip(FIELDS, cells)}
        rows.append(CanvasRow(**values))

    return rows


def load_canvas_registry(agent_md: Path) -> list[CanvasRow]:
    """从主 Agent 文档读取画布注册表。"""
    return parse_canvas_registry(agent_md.read_text(encoding="utf-8"))


def by_id(rows: Iterable[CanvasRow], canvas_id: str) -> CanvasRow | None:
    """按 canvas_id 取条目；不存在则返回 None。"""
    for row in rows:
        if row.canvas_id == canvas_id:
            return row
    return None
