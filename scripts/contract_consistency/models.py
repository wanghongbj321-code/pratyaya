#!/usr/bin/env python3
"""Deterministic static gate for pratyaya contract consistency.

本检查器实现《契约一致性检查器门禁方案》(tmp/pratyaya-internal/docs/design/契约一致性检查器-206-0801-1003.md)
中阶段 A（最小强门禁）与阶段 B（跨契约结构比较）的规则。

设计原则
--------
* 纯文本/Python 静态检查，不依赖 LLM 与网络。
* 每条规则以稳定的 ``<CATEGORY>-<NAME>`` 代码标识（如 ``MANIFEST_JSON``），输出包含
  ``code / level / where / message / hint`` 五字段，便于脚本和未来机器消费。
* 失败按级别归类：``error``（必须修） / ``warning``（建议修） / ``info``（说明）。
* 默认输出人类可读文本；``--json`` 输出 JSON；``--strict`` 将 ``warning`` 视作错误退出。
* 通过 ``--root`` 可指向任意目录，方便对合成仓库做单元测试。

参考：tmp/pratyaya-internal/docs/design/契约一致性检查器-206-0801-1003.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Union, cast


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# JSON 反序列化后的通用值/字典类型（已知联合，避免 Any/Unknown 透传）
JsonValue = Union[
    str, int, float, bool, None, list["JsonValue"], dict[str, "JsonValue"]
]
JsonDict = dict[str, JsonValue]


def _dig(d: JsonDict, *keys: str) -> JsonDict:
    """逐层安全取值，缺失或类型不符则回退空 dict。"""
    cur: JsonDict = d
    for k in keys:
        val = cur.get(k)
        if not isinstance(val, dict):
            return {}
        cur = val
    return cur



# ---------------------------------------------------------------------------
# 常量与权威源
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO_ROOT

PLUGIN_JSON = ".codebuddy-plugin/plugin.json"
AGENTS_DIR = "agents"
SKILLS_DIR = "skills"
VISUAL_PATTERNS_DIR = "skills/canvas-render/visual-patterns"
VISUAL_PATTERNS_README = "skills/canvas-render/visual-patterns/README.md"
GATE_REFERENCES_DIR = "skills/module-conclusion-gate/references"
GC_GATE_DIR = "skills/gc-gate/references"
GC_GATE_FILE = "skills/gc-gate/references/GC-gate.md"
WORKSHOP_CANVAS_MAP = "skills/mvl-distill/references/workshop-canvas-map.md"
RENDER_CONTRACT = "skills/canvas-render/references/render-contract.md"
CANVAS_SPEC = "skills/mvl-distill/references/mvl-canvas-spec.md"
MODULE_GATE_SKILL = "skills/module-conclusion-gate/SKILL.md"
EXAMPLES_MODULES = "examples/modules"

# Phase A 常量
EXPECTED_VISUAL_PATTERN_COUNT = 10
EXPECTED_VISUAL_PATTERN_NN_RANGE = tuple(f"{n:02d}" for n in range(1, 11))
EXPECTED_VISUAL_PATTERN_METADATA = (
    "id",
    "zh_name",
    "visual_system",
    "layout",
    "formality",
    "density",
    "best_for",
)
PATTERN_LAYOUT_ENUM = {"balanced", "flow"}
PATTERN_FORMALITY_ENUM = {"medium-high", "high"}
PATTERN_DENSITY_ENUM = {"medium", "medium-high", "high"}
ALLOWED_GATE_CATEGORIES = {"information_integrity", "business_risk"}
ALLOWED_GATE_RISK_LEVELS = {"low", "medium", "high"}
# 设计：8 列 | ID | 检查项 | 结果 | 分类 | 风险等级 | 来源 ID | 影响 | 建议 |
# 实际：5 列 | ID | 条件 | 分类 | 风险等级 | 来源 |
# 解析器按表头行决定列映射，兼容两种格式
GATE_ID_RE = re.compile(r"^M(\d)-GATE-(\d{2})$")
MAAU_GATE_ID_RE = re.compile(r"^MAAU-GATE-(\d+)$")
MAAU_GATE_FILE = "skills/module-conclusion-gate/references/MAAU-gate.md"
GATE_TABLE_HEADER_RE = re.compile(
    r"^\|\s*`?(M\d-GATE-\d{2})`?\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$"
)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.\-]+)?(?:\+[0-9A-Za-z.\-]+)?$")

# Phase B 常量
AUTH_FIELDS = (
    "gate_recommendation",
    "render_authorized",
    "confirmation_mode",
    "override_audit",
)
ALLOWED_STATES = {"draft", "gaps_open", "review_ready", "confirmed", "rendered"}
ALLOWED_OVERRIDE_CATEGORY = {"business_risk"}
ALLOWED_BUSINESS_RISK = {"low", "medium", "high"}
# 文档中必须严格回避的废弃术语
DEPRECATED_TERMS = {
    "render_allowed": "字段已删除；当前以 render_authorized + confirmation_mode 表达",
    "module-N.json": "已弃用 JSON 数据源；当前以 Mx-v{N}.md 确认包为唯一事实源",
    "check_gate.py": "已删除的旧 Python 脚本；本仓库内不得再被引用",
}


# ---------------------------------------------------------------------------
# 数据类
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """检查器输出的一条结果。"""

    code: str
    level: str  # "error" | "warning" | "info"
    where: str
    message: str
    hint: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class CheckContext:
    """检查器运行上下文：根目录、解析出的 plugin.json。"""

    root: Path
    plugin: dict[str, object] = field(default_factory=dict)
    plugin_path: Path | None = None


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """解析 ``---`` 包裹的 YAML 风格 frontmatter。

    本检查器只识别最常见的 ``key: value`` 形式，不引入 PyYAML 依赖；遇到复杂结构时
    返回原始字符串供上层处理。
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm_block = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    out: dict[str, str] = {}
    for line in fm_block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out, body


def split_md_links(text: str) -> list[tuple[str, str, int]]:
    """提取 Markdown 行内链接与引用式链接，输出 (text, target, line_no) 三元组。"""
    out: list[tuple[str, str, int]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", line):
            out.append((match.group(1), match.group(2), lineno))
        for match in re.finditer(r"\[([^\]]+)\]:\s*(\S+)", line):
            out.append((match.group(1), match.group(2), lineno))
    return out


def find_anchor_section(text: str, anchor: str) -> str:
    """返回 ``## {anchor}`` 节起至下一同级/上级节前的原文。"""
    pattern = re.compile(rf"^(##\s+{re.escape(anchor)}\b.*?)(?=^##\s|\Z)", re.M | re.S)
    match = pattern.search(text)
    return match.group(1) if match else ""


def list_md_files(root: Path, sub: str) -> list[Path]:
    """列出 root/sub 目录下所有 .md 文件（按路径排序）；目录不存在则返回空列表。"""
    base = root / sub
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob("*.md") if p.is_file())


def _is_within(child: Path, parent: Path) -> bool:
    """判断 child 是否位于 parent 目录树内（含相等）。"""
    try:
        _ = child.relative_to(parent)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Phase A 规则：最小强门禁
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# Canvas-specific constants
# ---------------------------------------------------------------------------

GC_GATE_ID_RE = re.compile(r"^GC-GATE-\d+$")
HMW_GATE_ID_RE = re.compile(r"^HMW-GATE-\d+$")
HMW_GATE_FILE = "skills/hmw-gate/references/HMW-gate.md"
HMW_DISTILL_SKILL = "skills/hmw-distill/SKILL.md"
HMW_GATE_SKILL = "skills/hmw-gate/SKILL.md"
HMW_TEMPLATE_HTML = "skills/canvas-render/examples/hmw-canvas.html"
HMW_TPL_GATE_IDS = tuple(f"HMW-TPL-GATE-{n:02d}" for n in range(1, 7))
HMW_IDEA_ANCHORS = tuple(f"hmw-idea-{n}" for n in range(1, 9))
JOURNEY_GATE_ID_RE = re.compile(r"^JOURNEY-GATE-\d+$")
JOURNEY_GATE_FILE = "skills/journey-gate/references/JOURNEY-gate.md"
JOURNEY_DISTILL_SKILL = "skills/journey-distill/SKILL.md"
JOURNEY_GATE_SKILL = "skills/journey-gate/SKILL.md"
JOURNEY_FRAME = "skills/journey-distill/frameworks/journey-frame.md"
JOURNEY_SPEC = "skills/journey-distill/references/journey-spec.md"
JOURNEY_RENDER_CONTRACT = "skills/canvas-render/references/render-contract-journey.md"
JOURNEY_TEMPLATE_HTML = "skills/canvas-render/examples/user-journey-canvas.html"
JOURNEY_EXAMPLE_KEYPOINTS = "examples/modules/JOURNEY-retail-demo-keypoints.md"
JOURNEY_EXAMPLE_PACKAGE = "examples/modules/JOURNEY-retail-demo-v1.md"
JOURNEY_EXAMPLE_GAPS = "examples/modules/JOURNEY-retail-demo-gaps.md"
JOURNEY_TPL_GATE_IDS = tuple(f"JOURNEY-TPL-GATE-{n:02d}" for n in range(1, 7))
JOURNEY_STAGE_FIELDS = (
    "action",
    "touchpoint-system",
    "emotion",
    "pain-point",
    "opportunity",
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
JOURNEY_QUALITY_KEYS = (
    "user_perspective",
    "business_outcome",
    "pain_opportunity_visible",
    "no_solution_bias",
)
JOURNEY_QUALITY_ANCHORS = (
    "journey-quality-user-perspective",
    "journey-quality-business-outcome",
    "journey-quality-pain-opportunity-visible",
    "journey-quality-no-solution-bias",
)
PERSONA_DISTILL_SKILL = "skills/persona-distill/SKILL.md"
PERSONA_GATE_SKILL = "skills/persona-gate/SKILL.md"
PERSONA_GATE_FILE = "skills/persona-gate/references/PERSONA-gate.md"
PERSONA_CONTRACT = "skills/canvas-render/references/render-contract-persona.md"
PERSONA_TEMPLATE_HTML = "skills/canvas-render/examples/user-persona-canvas.html"
PERSONA_REQUIRED_ANCHORS = (
    "canvas-header", "persona-basic", "persona-grid6", "persona-quality", "quality-panel",
    "persona-name", "persona-gender", "persona-age", "persona-location", "persona-education",
    "persona-job-title", "persona-industry", "persona-family-status", "persona-income",
    "persona-description", "persona-goals-needs", "persona-behaviors", "persona-pain-points",
    "persona-motivation", "persona-decision-factors", "persona-quality-evidence",
    "persona-quality-concrete", "persona-quality-voice", "persona-quality-representative",
)




__all__ = [name for name in globals() if not name.startswith("__")]
