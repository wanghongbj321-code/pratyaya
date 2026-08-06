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

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT

PLUGIN_JSON = ".codebuddy-plugin/plugin.json"
AGENTS_DIR = "agents"
SKILLS_DIR = "skills"
VISUAL_PATTERNS_DIR = "skills/canvas-render/visual-patterns"
VISUAL_PATTERNS_README = "skills/canvas-render/visual-patterns/README.md"
GATE_REFERENCES_DIR = "skills/module-conclusion-gate/references"
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


def _ensure_plugin(ctx: CheckContext) -> None:
    """按需加载 plugin.json；用于让单条规则在被独立执行时也能工作。"""
    if ctx.plugin:
        return
    path = ctx.root / PLUGIN_JSON
    if not path.is_file():
        return
    try:
        ctx.plugin = json.loads(read_text(path))
        ctx.plugin_path = path
    except json.JSONDecodeError:
        pass


def check_manifest_json(ctx: CheckContext) -> list[Finding]:
    plugin_path = ctx.root / PLUGIN_JSON
    ctx.plugin_path = plugin_path
    if not plugin_path.is_file():
        return [
            Finding(
                code="MANIFEST_JSON",
                level="error",
                where=PLUGIN_JSON,
                message="缺少 plugin.json 清单文件",
                hint="需创建 .codebuddy-plugin/plugin.json",
            )
        ]
    text = read_text(plugin_path)
    try:
        ctx.plugin = json.loads(text)
    except json.JSONDecodeError as exc:
        return [
            Finding(
                code="MANIFEST_JSON",
                level="error",
                where=PLUGIN_JSON,
                message=f"plugin.json 不是合法 JSON：{exc.msg} (line {exc.lineno})",
                hint="修正 JSON 语法",
            )
        ]
    return []


def check_identity_match(ctx: CheckContext) -> list[Finding]:
    """plugin.json 的 name / agentName / displayName 之间的派生关系。"""
    if not ctx.plugin:
        return []
    findings: list[Finding] = []
    name = ctx.plugin.get("name")
    agent_name = ctx.plugin.get("agentName")
    display_name = ctx.plugin.get("displayName")
    if not name:
        findings.append(
            Finding(
                code="IDENTITY_MATCH",
                level="error",
                where=PLUGIN_JSON,
                message="plugin.json 缺 name 字段",
                hint="name 为专家包唯一标识（kebab-case）",
            )
        )
    if not agent_name:
        findings.append(
            Finding(
                code="IDENTITY_MATCH",
                level="error",
                where=PLUGIN_JSON,
                message="plugin.json 缺 agentName 字段",
                hint="agentName 应等于 agents/{name}.md 的文件名",
            )
        )
    elif name and agent_name and name != agent_name:
        findings.append(
            Finding(
                code="IDENTITY_MATCH",
                level="error",
                where=PLUGIN_JSON,
                message=f"name={name!r} 与 agentName={agent_name!r} 不一致",
                hint="name 与 agentName 应严格相等（开发指导 §10.3）",
            )
        )
    if not display_name:
        findings.append(
            Finding(
                code="IDENTITY_MATCH",
                level="warning",
                where=PLUGIN_JSON,
                message="plugin.json 缺 displayName 字段",
                hint="WorkBuddy 显示名应由 plugin.json 统一提供",
            )
        )
    return findings


def check_entry_exists(ctx: CheckContext) -> list[Finding]:
    """主 Agent MD 文件存在性。"""
    if not ctx.plugin:
        return []
    name = ctx.plugin.get("name") or ctx.plugin.get("agentName")
    if not name:
        return []  # 已由 IDENTITY_MATCH 报错
    agent_path = ctx.root / AGENTS_DIR / f"{name}.md"
    if not agent_path.is_file():
        return [
            Finding(
                code="ENTRY_EXISTS",
                level="error",
                where=str(agent_path.relative_to(ctx.root)),
                message=f"主 Agent 文件 {name}.md 不存在",
                hint="需创建 agents/{name}.md（与 plugin.json agentName 一致）",
            )
        ]
    return []


def check_agent_entry(ctx: CheckContext) -> list[Finding]:
    """主 Agent MD frontmatter 必须有 name + description。"""
    if not ctx.plugin:
        return []
    name = ctx.plugin.get("name") or ctx.plugin.get("agentName")
    if not name:
        return []
    agent_path = ctx.root / AGENTS_DIR / f"{name}.md"
    if not agent_path.is_file():
        return []
    text = read_text(agent_path)
    fm, _ = parse_frontmatter(text)
    findings: list[Finding] = []
    if not fm.get("name"):
        findings.append(
            Finding(
                code="AGENT_ENTRY",
                level="error",
                where=str(agent_path.relative_to(ctx.root)),
                message="主 Agent frontmatter 缺 name 字段",
                hint="frontmatter 必填 name 与 description",
            )
        )
    if not fm.get("description"):
        findings.append(
            Finding(
                code="AGENT_ENTRY",
                level="error",
                where=str(agent_path.relative_to(ctx.root)),
                message="主 Agent frontmatter 缺 description 字段",
                hint="frontmatter 必填 name 与 description",
            )
        )
    return findings


def check_skill_entry(ctx: CheckContext) -> list[Finding]:
    """主 Agent MD 中声明的 Skill 路径必须真实存在。"""
    if not ctx.plugin:
        return []
    name = ctx.plugin.get("name") or ctx.plugin.get("agentName")
    if not name:
        return []
    agent_path = ctx.root / AGENTS_DIR / f"{name}.md"
    if not agent_path.is_file():
        return []
    text = read_text(agent_path)
    findings: list[Finding] = []
    # 匹配 skills/<name>/SKILL.md 与 skills/<name>/references/...
    pattern = re.compile(r"skills/([a-z0-9][a-z0-9\-]*)/SKILL\.md")
    skill_names: list[str] = sorted(set(pattern.findall(text)))
    for skill_name in skill_names:
        skill_path = ctx.root / SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_path.is_file():
            findings.append(
                Finding(
                    code="SKILL_ENTRY",
                    level="error",
                    where=str(agent_path.relative_to(ctx.root)),
                    message=f"主 Agent 引用了 skills/{skill_name}/SKILL.md，但文件不存在",
                    hint="在 skills/<name>/ 下补齐 SKILL.md",
                )
            )
    return findings


def check_version_format(ctx: CheckContext) -> list[Finding]:
    if not ctx.plugin:
        return []
    version = ctx.plugin.get("version")
    if not version:
        return [
            Finding(
                code="VERSION_FORMAT",
                level="error",
                where=PLUGIN_JSON,
                message="plugin.json 缺 version 字段",
                hint="version 必须为 SemVer（如 1.0.0）",
            )
        ]
    if not SEMVER_RE.match(str(version)):
        return [
            Finding(
                code="VERSION_FORMAT",
                level="error",
                where=PLUGIN_JSON,
                message=f"plugin.json version={version!r} 不是合法 SemVer",
                hint="version 必须为 SemVer（如 1.0.0）",
            )
        ]
    return []


def check_changelog_version(ctx: CheckContext) -> list[Finding]:
    """CHANGELOG.md 必须包含一个与 plugin.json version 一致的标题行。"""
    if not ctx.plugin:
        return []
    plugin_version = str(ctx.plugin.get("version", ""))
    if not plugin_version:
        return []
    path = ctx.root / "CHANGELOG.md"
    if not path.is_file():
        return [
            Finding(
                code="CHANGELOG_VERSION",
                level="error",
                where="CHANGELOG.md",
                message="缺少 CHANGELOG.md",
                hint="需维护 CHANGELOG.md，并在首条记录当前版本",
            )
        ]
    text = read_text(path)
    # 同时支持 ## v1.0.0 与 ## [v1.0.0] - 2026-08-01 两种格式
    headings = re.findall(r"^##\s+\[?v?(\d+\.\d+\.\d+[^\s\]]*)", text, re.M)
    if not headings:
        return [
            Finding(
                code="CHANGELOG_VERSION",
                level="error",
                where="CHANGELOG.md",
                message="CHANGELOG.md 缺少 ## vX.Y.Z 形式的版本标题",
                hint="为每个发布版本添加 ## vX.Y.Z 标题（或 ## [vX.Y.Z] - 日期）",
            )
        ]
    if plugin_version not in headings:
        return [
            Finding(
                code="CHANGELOG_VERSION",
                level="error",
                where="CHANGELOG.md",
                message=f"CHANGELOG 标题版本 {headings} 不含 plugin.json 的 {plugin_version}",
                hint=f"在 CHANGELOG.md 添加 ## [v{plugin_version}] 段",
            )
        ]
    return []


# ---- Gate 文件 ------------------------------------------------------------


def _parse_gate_file(path: Path) -> list[dict[str, str]]:
    """解析 Mx-gate.md 中的 GATE 表格，输出每行字典。

    支持两种列格式（按表头识别）：
    * 设计 8 列：| ID | 检查项 | 结果 | 分类 | 风险等级 | 来源 ID | 影响 | 建议 |
    * 实际 5 列：| ID | 条件 | 分类 | 风险等级 | 来源 |
    """
    text = read_text(path)
    rows: list[dict[str, str]] = []
    in_table = False
    columns: list[str] = []
    column_alias: dict[str, str] = {
        "id": "id",
        "检查项": "check",
        "条件": "check",
        "结果": "result",
        "分类": "category",
        "风险等级": "risk",
        "risk": "risk",
        "来源": "source",
        "来源 id": "source",
        "影响": "impact",
        "建议": "advice",
    }
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            in_table = False
            columns = []
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        # 跳过分隔行
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        if not in_table:
            # 必须是 ID 列表头才视为 GATE 表
            if cells and cells[0].strip().lower() == "id":
                in_table = True
                columns = [c.strip().strip("`").lower() for c in cells]
            continue
        first = cells[0].strip().strip("`")
        if not GATE_ID_RE.match(first):
            continue
        row: dict[str, str] = {"id": first}
        for idx, value in enumerate(cells[1:], start=1):
            if idx >= len(columns):
                continue
            header = columns[idx]
            alias = column_alias.get(header, header)
            row[alias] = value.strip().strip("`")
        for key in ("category", "risk", "source"):
            if key not in row:
                row[key] = ""  # 兜底，确保下游按固定 key 取值
        rows.append(row)
    return rows


def check_gate_file_set(ctx: CheckContext) -> list[Finding]:
    """M1-M6 闸门策略文件必须齐全。"""
    findings: list[Finding] = []
    base = ctx.root / GATE_REFERENCES_DIR
    if not base.is_dir():
        return [
            Finding(
                code="GATE_FILE_SET",
                level="error",
                where=GATE_REFERENCES_DIR,
                message="缺少 module-conclusion-gate references 目录",
                hint="需在 skills/module-conclusion-gate/references/ 下放 M1-gate.md..M6-gate.md",
            )
        ]
    for n in range(1, 7):
        path = base / f"M{n}-gate.md"
        if not path.is_file():
            findings.append(
                Finding(
                    code="GATE_FILE_SET",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"缺少 M{n} 闸门策略文件 M{n}-gate.md",
                    hint="补齐 references/M{n}-gate.md",
                )
            )
    return findings


def _iter_gate_rows(ctx: CheckContext) -> list[tuple[Path, dict[str, str]]]:
    out: list[tuple[Path, dict[str, str]]] = []
    base = ctx.root / GATE_REFERENCES_DIR
    if not base.is_dir():
        return out
    for path in sorted(base.glob("M*-gate.md")):
        for row in _parse_gate_file(path):
            out.append((path, row))
    return out


def check_gate_table_parse(ctx: CheckContext) -> list[Finding]:
    """每个 Mx-gate.md 必须至少解析出一行；解析失败给出明确位置。"""
    findings: list[Finding] = []
    base = ctx.root / GATE_REFERENCES_DIR
    if not base.is_dir():
        return findings
    for path in sorted(base.glob("M*-gate.md")):
        rows = _parse_gate_file(path)
        if not rows:
            findings.append(
                Finding(
                    code="GATE_TABLE_PARSE",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message="未解析到任何 GATE 表格行（首列必须为 ID，且符合 M<N>-GATE-<NN> 格式）",
                    hint="确认表头首列为 ID 行；行内首列为 M1-GATE-01..M6-GATE-07 形式",
                )
            )
    return findings


def check_gate_table_width(ctx: CheckContext) -> list[Finding]:
    """设计要求 GATE 表格 8 列；当前实现多为 5 列，告警而非阻塞。"""
    findings: list[Finding] = []
    base = ctx.root / GATE_REFERENCES_DIR
    if not base.is_dir():
        return findings
    for path in sorted(base.glob("M*-gate.md")):
        text = read_text(path)
        # 找到首条 ID 行的列数
        for line in text.splitlines():
            if not line.lstrip().startswith("|"):
                continue
            cells = line.strip().strip("|").split("|")
            if not cells:
                continue
            # 跳过表头/分隔/非 ID 行
            if cells[0].strip().strip("`").lower() == "id":
                continue
            if all(set(c) <= {"-", ":", " "} for c in cells):
                continue
            if not GATE_ID_RE.match(cells[0].strip().strip("`")):
                continue
            col_count = len(cells)
            if col_count != 8:
                findings.append(
                    Finding(
                        code="GATE_TABLE_WIDTH",
                        level="warning",
                        where=str(path.relative_to(ctx.root)),
                        message=f"GATE 表行 {col_count} 列（设计 8 列：ID/检查项/结果/分类/风险等级/来源 ID/影响/建议）",
                        hint="补全 结果/影响/建议 三列以对齐设计；或更新设计文档接受 5 列精简版",
                    )
                )
            break
    return findings


def check_gate_id_format(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        if not GATE_ID_RE.match(row["id"]):
            findings.append(
                Finding(
                    code="GATE_ID_FORMAT",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"行 ID {row['id']!r} 不符合 M<N>-GATE-<NN> 格式",
                    hint="稳定 ID 必须为 M1-GATE-01..M6-GATE-07 形式",
                )
            )
    return findings


def check_gate_id_module(ctx: CheckContext) -> list[Finding]:
    """每个 ID 的 M{N} 前缀必须与所在文件名一致。"""
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        match = GATE_ID_RE.match(row["id"])
        if not match:
            continue
        id_module = int(match.group(1))
        file_module = int(path.stem.split("-")[0][1:])  # "M1-gate" -> 1
        if id_module != file_module:
            findings.append(
                Finding(
                    code="GATE_ID_MODULE",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"ID {row['id']} 的模块号 {id_module} 与文件模块号 {file_module} 不一致",
                    hint="ID 的 M{N} 前缀必须与所在文件名一致",
                )
            )
    return findings


def check_gate_id_unique(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    counter: Counter[str] = Counter()
    location: dict[str, str] = {}
    for path, row in _iter_gate_rows(ctx):
        counter[row["id"]] += 1
        rel = str(path.relative_to(ctx.root))
        _ = location.setdefault(row["id"], rel)
    for gid, count in counter.items():
        if count > 1:
            findings.append(
                Finding(
                    code="GATE_ID_UNIQUE",
                    level="error",
                    where=location[gid],
                    message=f"稳定 ID {gid} 出现 {count} 次",
                    hint="每个 ID 在全 M1–M6 范围内必须唯一",
                )
            )
    return findings


def check_gate_category(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        category = row["category"]
        if category not in ALLOWED_GATE_CATEGORIES:
            findings.append(
                Finding(
                    code="GATE_CATEGORY",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"行 {row['id']} 分类 {category!r} 不在 {sorted(ALLOWED_GATE_CATEGORIES)} 内",
                    hint="分类必须为 information_integrity 或 business_risk",
                )
            )
    return findings


def check_gate_risk(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        risk = row["risk"]
        if risk not in ALLOWED_GATE_RISK_LEVELS:
            findings.append(
                Finding(
                    code="GATE_RISK",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"行 {row['id']} 风险等级 {risk!r} 不在 {sorted(ALLOWED_GATE_RISK_LEVELS)} 内",
                    hint="风险等级必须为 low / medium / high",
                )
            )
    return findings


def check_gate_source(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        if not row["source"] or row["source"] in {"-", "—", "/"}:
            findings.append(
                Finding(
                    code="GATE_SOURCE",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"行 {row['id']} 缺来源 ID",
                    hint="来源 ID 必填（如 M{N}-Gxx / section 引用）",
                )
            )
    return findings


# ---- 视觉模式 -------------------------------------------------------------


def _iter_pattern_files(ctx: CheckContext) -> list[Path]:
    base = ctx.root / VISUAL_PATTERNS_DIR
    if not base.is_dir():
        return []
    return sorted(
        p
        for p in base.glob("*.md")
        if p.is_file() and p.name != "README.md"
    )


def check_pattern_count(ctx: CheckContext) -> list[Finding]:
    base = ctx.root / VISUAL_PATTERNS_DIR
    if not base.is_dir():
        return [
            Finding(
                code="PATTERN_COUNT",
                level="error",
                where=VISUAL_PATTERNS_DIR,
                message="缺少 visual-patterns 目录",
                hint="需在 skills/canvas-render/visual-patterns/ 下放 10 个模式文件 + README",
            )
        ]
    readme = base / "README.md"
    if not readme.is_file():
        return [
            Finding(
                code="PATTERN_COUNT",
                level="error",
                where=VISUAL_PATTERNS_README,
                message="缺少 visual-patterns/README.md",
                hint="补齐 visual-patterns 目录说明",
            )
        ]
    files = _iter_pattern_files(ctx)
    if len(files) != EXPECTED_VISUAL_PATTERN_COUNT:
        return [
            Finding(
                code="PATTERN_COUNT",
                level="error",
                where=VISUAL_PATTERNS_DIR,
                message=f"模式文件 {len(files)} 个 ≠ 期望 {EXPECTED_VISUAL_PATTERN_COUNT}",
                hint="按 visual-patterns/README.md 当前基线维护 10 个模式",
            )
        ]
    return []


def check_pattern_filename(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    pattern_re = re.compile(r"^(\d{2})-(.+)\.md$")
    for path in _iter_pattern_files(ctx):
        match = pattern_re.match(path.name)
        if not match:
            findings.append(
                Finding(
                    code="PATTERN_FILENAME",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"文件名 {path.name!r} 不符合 NN-id.md 规范",
                    hint="文件名必须为 NN-id.md（两位序号 + kebab-case id）",
                )
            )
    return findings


def check_pattern_sequence(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    nn_seen: list[str] = []
    pattern_re = re.compile(r"^(\d{2})-(.+)\.md$")
    for path in _iter_pattern_files(ctx):
        match = pattern_re.match(path.name)
        if not match:
            continue
        nn_seen.append(match.group(1))
    nn_sorted = sorted(set(nn_seen))
    if nn_sorted != list(EXPECTED_VISUAL_PATTERN_NN_RANGE):
        findings.append(
            Finding(
                code="PATTERN_SEQUENCE",
                level="error",
                where=VISUAL_PATTERNS_DIR,
                message=f"模式序号集合 {nn_sorted} ≠ 期望 {list(EXPECTED_VISUAL_PATTERN_NN_RANGE)}",
                hint="必须使用 01..10；不得跳号或重排已发布序号",
            )
        )
    if len(nn_seen) != len(set(nn_seen)):
        duplicates = sorted({n for n, c in Counter(nn_seen).items() if c > 1})
        findings.append(
            Finding(
                code="PATTERN_SEQUENCE",
                level="error",
                where=VISUAL_PATTERNS_DIR,
                message=f"模式序号重复：{duplicates}",
                hint="每个 NN 只能被一个模式占用",
            )
        )
    return findings


def check_pattern_id(ctx: CheckContext) -> list[Finding]:
    """frontmatter id 必须等于去掉 NN- 和 .md 后的文件名。"""
    findings: list[Finding] = []
    pattern_re = re.compile(r"^(\d{2})-(.+)\.md$")
    for path in _iter_pattern_files(ctx):
        match = pattern_re.match(path.name)
        if not match:
            continue
        expected_id = match.group(2)
        text = read_text(path)
        fm, _ = parse_frontmatter(text)
        actual_id = fm.get("id", "")
        if not actual_id:
            findings.append(
                Finding(
                    code="PATTERN_ID",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message="frontmatter 缺 id 字段",
                    hint="每个模式必须声明 id 且与文件名 {id} 一致",
                )
            )
            continue
        if actual_id != expected_id:
            findings.append(
                Finding(
                    code="PATTERN_ID",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"frontmatter id={actual_id!r} 与文件名 {expected_id!r} 不一致",
                    hint="id 字段必须等于去掉 NN- 和 .md 的文件名",
                )
            )
    return findings


def check_pattern_metadata(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_pattern_files(ctx):
        text = read_text(path)
        fm, _ = parse_frontmatter(text)
        missing = [k for k in EXPECTED_VISUAL_PATTERN_METADATA if k not in fm]
        if missing:
            findings.append(
                Finding(
                    code="PATTERN_METADATA",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"frontmatter 缺字段 {missing}",
                    hint=f"frontmatter 必须包含 {EXPECTED_VISUAL_PATTERN_METADATA}",
                )
            )
    return findings


def check_pattern_enum(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_pattern_files(ctx):
        text = read_text(path)
        fm, _ = parse_frontmatter(text)
        if fm.get("layout") not in PATTERN_LAYOUT_ENUM:
            findings.append(
                Finding(
                    code="PATTERN_ENUM",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"layout={fm.get('layout')!r} 不在 {sorted(PATTERN_LAYOUT_ENUM)} 内",
                    hint="layout 必须为 balanced 或 flow",
                )
            )
        if fm.get("formality") not in PATTERN_FORMALITY_ENUM:
            findings.append(
                Finding(
                    code="PATTERN_ENUM",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"formality={fm.get('formality')!r} 不在 {sorted(PATTERN_FORMALITY_ENUM)} 内",
                    hint="formality 必须为 medium-high 或 high",
                )
            )
        if fm.get("density") not in PATTERN_DENSITY_ENUM:
            findings.append(
                Finding(
                    code="PATTERN_ENUM",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"density={fm.get('density')!r} 不在 {sorted(PATTERN_DENSITY_ENUM)} 内",
                    hint="density 必须为 medium / medium-high / high",
                )
            )
    return findings


# ---- 本地 Markdown 链接 ---------------------------------------------------


def check_local_link(ctx: CheckContext) -> list[Finding]:
    """扫描 Markdown 文件中形如 ``./xxx.md`` 或 ``../xxx.md`` 的本地链接。

    仅在目标像路径（含 ``.md`` / ``.html`` / 含 ``/``）时检查；纯数字锚点或单字符引用忽略。
    """
    findings: list[Finding] = []
    candidates: list[Path] = []
    for sub in (
        "README.md",
        "DEVELOPMENT.md",
        "DESIGN.md",
        "CHANGELOG.md",
        "AGENTS.md",
        "docs",
        "skills",
        "agents",
        "examples",
        "schemas",
    ):
        path = ctx.root / sub
        if path.is_file():
            candidates.append(path)
        elif path.is_dir():
            candidates.extend(p for p in path.rglob("*.md") if p.is_file())
    for path in candidates:
        text = read_text(path)
        for _, target, lineno in split_md_links(text):
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            # 只检查路径形态的目标（至少含 / 或文件后缀），避免误报纯数字锚点
            if "/" not in clean and "." not in clean:
                continue
            link_path = (path.parent / clean).resolve()
            if not _is_within(link_path, ctx.root.resolve()):
                findings.append(
                    Finding(
                        code="LOCAL_LINK",
                        level="error",
                        where=f"{path.relative_to(ctx.root)}:{lineno}",
                        message=f"链接 {target!r} 跳出仓库根目录",
                        hint="若非有意指向其他仓库，请改用仓库内相对路径（一般 1–2 个 ../）",
                    )
                )
                continue
            if not link_path.exists():
                findings.append(
                    Finding(
                        code="LOCAL_LINK",
                        level="error",
                        where=f"{path.relative_to(ctx.root)}:{lineno}",
                        message=f"链接 {target!r} 解析为不存在的路径 {link_path.relative_to(ctx.root)}",
                        hint="修正为目标文件真实路径",
                    )
                )
    return findings


# ---- 废弃术语 -------------------------------------------------------------


def check_deprecated_term(ctx: CheckContext) -> list[Finding]:
    """在权威文档中检查废弃术语（仅扫描关键目录，避免对所有 Markdown 误报）。"""
    findings: list[Finding] = []
    scan_paths = [
        "README.md",
        "DEVELOPMENT.md",
        "DESIGN.md",
        "docs",
        "skills",
        "agents",
        "schemas",
        ".codebuddy-plugin",
    ]
    for sub in scan_paths:
        path = ctx.root / sub
        if path.is_file():
            files = [path]
        elif path.is_dir():
            files = [p for p in path.rglob("*") if p.is_file()]
        else:
            continue
        for f in files:
            if f.suffix not in {".md", ".json", ".yaml", ".yml"}:
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            for term, explanation in DEPRECATED_TERMS.items():
                if term not in text:
                    continue
                # README/DESIGN/DEVELOPMENT 等"显式说明废弃"的上下文不视为违规。
                # 扩大上下文窗口到 6 行（前后各 3），覆盖 schema 注释和文档说明。
                lines = text.splitlines()
                for lineno, line in enumerate(lines, 1):
                    if term not in line:
                        continue
                    start = max(0, lineno - 4)
                    window = "\n".join(lines[start : lineno + 2])
                    if any(
                        kw in window
                        for kw in (
                            "已弃用",
                            "已删除",
                            "deprecated",
                            "不推荐",
                            "不得再",
                            "删除",
                            "不再使用",
                            "不作为当前",
                            "非强制参考",
                            "旧",
                        )
                    ):
                        continue
                    findings.append(
                        Finding(
                            code="DEPRECATED_TERM",
                            level="error",
                            where=f"{f.relative_to(ctx.root)}:{lineno}",
                            message=f"出现废弃术语 {term!r}",
                            hint=explanation,
                        )
                    )
    return findings


# ---------------------------------------------------------------------------
# Phase B 规则：跨契约结构比较
# ---------------------------------------------------------------------------


def _section_map(path: Path) -> dict[str, list[str]]:
    """解析 ``| 模块 | 必填 section |`` 表，返回 ``{M1: [sections], M2: [...]}`` 映射。

    表中右列以反引号包裹 section 名称；多个 section 以 ``、`xxx` `` 分隔。
    """
    text = read_text(path)
    result: dict[str, list[str]] = {}
    in_table = False
    for line in text.splitlines():
        if not in_table:
            if line.startswith("| 模块") and "section" in line:
                in_table = True
            continue
        if not line.startswith("|"):
            if result:
                break
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if set(cells[0]) <= {"-", " "} or cells[0].startswith("---"):
            continue
        module = cells[0].strip()
        if not re.match(r"^M\d$", module):
            continue
        # section 列可能为 `` `a`、`b` `` 或 `` `a`, `b` ``
        sections = re.findall(r"`([^`]+)`", cells[1])
        result[module] = sections
    return result


def _gate_section_list(path: Path) -> list[str]:
    """从 Mx-gate.md 的 ``## 必填 section`` 节中按列表项 ``- `xxx`（...）`` 提取 section 名称。"""
    text = read_text(path)
    section = find_anchor_section(text, "必填 section")
    if not section:
        return []
    out: list[str] = []
    for line in section.splitlines():
        match = re.match(r"^\s*-\s+`([^`]+)`", line)
        if match:
            out.append(match.group(1).strip())
    return out


def _gate_section_names(ctx: CheckContext) -> dict[str, list[str]]:
    """读取各 Mx-gate.md 的必填 section 列表，返回 ``{M1: [sections], ...}`` 映射。"""
    out: dict[str, list[str]] = {}
    base = ctx.root / GATE_REFERENCES_DIR
    if not base.is_dir():
        return out
    for path in sorted(base.glob("M*-gate.md")):
        module = path.stem.split("-")[0]  # "M1"
        out[module] = _gate_section_list(path)
    return out


def check_gate_section_sync(ctx: CheckContext) -> list[Finding]:
    """M1-M6 闸门文件的必填 section 集合与 workshop-canvas-map 的同名集合逐模块对齐。"""
    map_path = ctx.root / WORKSHOP_CANVAS_MAP
    if not map_path.is_file():
        return []
    map_sections = _section_map(map_path)
    findings: list[Finding] = []
    gate_sections = _gate_section_names(ctx)
    for module in sorted(gate_sections):
        expected = set(map_sections.get(module, []))
        actual = set(gate_sections[module])
        missing = expected - actual
        extra = actual - expected
        if missing:
            findings.append(
                Finding(
                    code="GATE_SECTION_SYNC",
                    level="error",
                    where=f"{GATE_REFERENCES_DIR}/{module}-gate.md",
                    message=f"{module} 闸门必填 section 缺 {sorted(missing)}（来源 {WORKSHOP_CANVAS_MAP}）",
                    hint="将缺失 section 补到 Mx-gate.md 的必填 section 列表",
                )
            )
        if extra:
            findings.append(
                Finding(
                    code="GATE_SECTION_SYNC",
                    level="warning",
                    where=f"{GATE_REFERENCES_DIR}/{module}-gate.md",
                    message=f"{module} 闸门 section 多出 {sorted(extra)}（未在 {WORKSHOP_CANVAS_MAP} 中登记）",
                    hint="与 workshop-canvas-map.md 对齐后再额外扩展",
                )
            )
    return findings


def check_template_skill_sync(ctx: CheckContext) -> list[Finding]:
    """examples/modules 模板文件的 section 与 workshop-canvas-map 必填 section 集合对齐。

    按模板文件名 ``Mx-*.md`` 的 M{N} 前缀与 map 中对应模块的 section 集合比对。
    """
    map_path = ctx.root / WORKSHOP_CANVAS_MAP
    if not map_path.is_file():
        return []
    map_sections = _section_map(map_path)
    findings: list[Finding] = []
    base = ctx.root / EXAMPLES_MODULES
    if not base.is_dir():
        return []
    for path in sorted(base.glob("*.md")):
        match = re.match(r"^(M\d)-", path.name)
        if not match:
            continue
        module = match.group(1)
        text = read_text(path)
        sections = re.findall(r"^##\s+详情\s+\d+[：:]\s*`?([a-z_]+)`?", text, re.M)
        if not sections:
            continue
        expected = set(map_sections.get(module, []))
        actual = set(sections)
        # 模板应包含 module 在 map 中登记的全部 section；多出不视为违规
        missing = expected - actual
        if missing:
            findings.append(
                Finding(
                    code="SKILL_TEMPLATE_SYNC",
                    level="warning",
                    where=str(path.relative_to(ctx.root)),
                    message=f"模板缺 {module} 的必填 section {sorted(missing)}（来源 {WORKSHOP_CANVAS_MAP}）",
                    hint="按 workshop-canvas-map.md 补全模板的 ## 详情 N 节",
                )
            )
    return findings


def _flatten_locale(value: JsonValue) -> list[str]:
    """将 ``{en: ..., zh: ...}`` 类多语字段展开为字符串列表。"""
    if isinstance(value, dict):
        return [str(v) for v in value.values()]
    if isinstance(value, list):
        out: list[str] = []
        for v in value:
            out.extend(_flatten_locale(v))
        return out
    return [str(value)] if value is not None else []


def check_state_enum(ctx: CheckContext) -> list[Finding]:
    """扫描权威文档中出现的状态值是否在 5 态集合内。

    只识别显式**模块级**状态上下文：

    * 5 态声明段落（``## 5 态``、``## 状态机`` 等），值的形式是 `` `draft` ``；
    * ``module.status = draft`` / ``status: draft`` 紧跟的状态值。

    缺口/任务/风险等子状态机（``open / closed / accepted_risk`` 等）不在本规则约束范围。
    """
    findings: list[Finding] = []
    # 仅在标题明确以"状态机 / 5 态 / 状态总览"开头的段落内匹配
    # （避免误中"缺口子状态机"等子状态机小节）
    section_re = re.compile(
        r"^(#{1,4})\s+(状态机|5\s*态|状态总览|状态机定义|module\s*state)\b[^#\n]*$",
        re.M | re.I,
    )
    # 段落内的状态值
    value_re = re.compile(r"`([a-z][a-z0-9_]*)`")
    seen: set[tuple[str, str]] = set()
    for rel in (
        "agents/pratyaya.md",
        "docs/MVL-整体架构设计.md",
        "docs/user-guide.md",
        "skills/module-conclusion-gate/SKILL.md",
        "skills/canvas-render/SKILL.md",
    ):
        path = ctx.root / rel
        if not path.is_file():
            continue
        text = read_text(path)
        # 切分章节
        for match in section_re.finditer(text):
            start = match.end()
            # 切到下一同级/上级标题
            heading_level = len(match.group(1))
            next_match = re.search(
                rf"^#{{1,{heading_level}}}\s+",
                text[start:],
                re.M,
            )
            end = start + next_match.start() if next_match else len(text)
            section_text = text[start:end]
            for vmatch in value_re.finditer(section_text):
                token = vmatch.group(1)
                if token in ALLOWED_STATES:
                    continue
                key = (rel, token)
                if key in seen:
                    continue
                seen.add(key)
                findings.append(
                    Finding(
                        code="STATE_ENUM_SYNC",
                        level="error",
                        where=rel,
                        message=(
                            f"模块状态机章节出现未授权状态 {token!r}"
                        ),
                        hint=(
                            f"模块状态机只接受 {sorted(ALLOWED_STATES)}；"
                            "如为子状态机（缺口/任务）请改放到独立小节，"
                            "不要混用 '5 态 / 状态机' 标题"
                        ),
                    )
                )
    return findings


def check_auth_fields(ctx: CheckContext) -> list[Finding]:
    """所有 4 个授权字段名（gate_recommendation / render_authorized / confirmation_mode / override_audit）必须出现在 schema 与主 Agent 中。"""
    findings: list[Finding] = []
    targets: list[tuple[str, str]] = []  # (rel, mode) mode="required"|"preferred"
    name = ctx.plugin.get("name") or ctx.plugin.get("agentName") if ctx.plugin else None
    if name:
        targets.append((f"agents/{name}.md", "preferred"))
    targets.append(("schemas/module-record.schema.json", "required"))
    for rel, mode in targets:
        path = ctx.root / rel
        if not path.is_file():
            continue
        text = read_text(path)
        for field_name in AUTH_FIELDS:
            if field_name not in text:
                findings.append(
                    Finding(
                        code="AUTH_FIELDS",
                        level="error" if mode == "required" else "warning",
                        where=rel,
                        message=f"授权字段 {field_name!r} 未在 {rel} 中出现",
                        hint=(
                            "schema 必须定义 4 个授权字段（顶层或嵌套对象内），"
                            f"以对齐 state.json 契约：{AUTH_FIELDS}"
                        ),
                    )
                )
    return findings


def check_override_category(ctx: CheckContext) -> list[Finding]:
    """override_audit.items[].category 在 schema 中只允许 business_risk。"""
    schema_path = ctx.root / "schemas" / "module-record.schema.json"
    if not schema_path.is_file():
        return []
    try:
        schema = cast(JsonDict, json.loads(read_text(schema_path)))
    except json.JSONDecodeError:
        return []
    findings: list[Finding] = []
    audit = _dig(schema, "properties", "override_audit")
    if not audit:
        findings.append(
            Finding(
                code="OVERRIDE_CATEGORY",
                level="error",
                where="schemas/module-record.schema.json",
                message="schema 缺顶层 override_audit 字段",
                hint="按设计，override_audit 必须是顶层字段；当前 schema 用 gate.render_allowed 表达，违背设计",
            )
        )
        return findings
    cat = _dig(audit, "properties", "items", "properties", "category")
    enum_raw = cat.get("enum")
    enum_items = enum_raw if isinstance(enum_raw, list) else []
    enum_values: set[str] = {str(x) for x in enum_items}
    if not enum_values:
        findings.append(
            Finding(
                code="OVERRIDE_CATEGORY",
                level="warning",
                where="schemas/module-record.schema.json",
                message="override_audit.items.category 未声明 enum",
                hint=f"建议显式约束为 {sorted(ALLOWED_OVERRIDE_CATEGORY)}",
            )
        )
    elif not enum_values.issubset(ALLOWED_OVERRIDE_CATEGORY):
        findings.append(
            Finding(
                code="OVERRIDE_CATEGORY",
                level="error",
                where="schemas/module-record.schema.json",
                message=f"override_audit.items.category enum {sorted(enum_values)} ⊄ {sorted(ALLOWED_OVERRIDE_CATEGORY)}",
                hint="按设计只允许 business_risk",
            )
        )
    return findings


def check_render_section_sync(ctx: CheckContext) -> list[Finding]:
    """render-contract.md 中提到的模块主 ID 集合应与 audit_canvas_html.py 常量一致。"""
    contract_path = ctx.root / RENDER_CONTRACT
    if not contract_path.is_file():
        return []
    contract_text = read_text(contract_path)
    findings: list[Finding] = []
    for anchor in ("module-summary", "module-outputs", "module-conclusions", "module-evidence", "module-gaps"):
        if anchor not in contract_text:
            findings.append(
                Finding(
                    code="RENDER_SECTION_SYNC",
                    level="warning",
                    where=RENDER_CONTRACT,
                    message=f"render-contract.md 未提及锚点 {anchor!r}",
                    hint="render-contract.md 应与 audit_canvas_html.py 的 MODULE_MAIN_IDS 一致",
                )
            )
    return findings


# ---------------------------------------------------------------------------
# 规则注册表
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Rule:
    code: str
    category: str  # "A" | "B"
    description: str
    runner: Callable[[CheckContext], list[Finding]]


RULES: tuple[Rule, ...] = (
    # Phase A
    Rule("MANIFEST_JSON", "A", "plugin.json 存在且为合法 JSON", check_manifest_json),
    Rule("IDENTITY_MATCH", "A", "plugin.json name / agentName / displayName 派生关系", check_identity_match),
    Rule("ENTRY_EXISTS", "A", "agents/{name}.md 必须存在", check_entry_exists),
    Rule("AGENT_ENTRY", "A", "主 Agent frontmatter 必填 name + description", check_agent_entry),
    Rule("SKILL_ENTRY", "A", "主 Agent 引用的 skills/*/SKILL.md 必须存在", check_skill_entry),
    Rule("VERSION_FORMAT", "A", "plugin.json version 必须为 SemVer", check_version_format),
    Rule("CHANGELOG_VERSION", "A", "CHANGELOG.md 必含当前版本标题", check_changelog_version),
    Rule("GATE_FILE_SET", "A", "M1-M6 闸门策略文件齐全", check_gate_file_set),
    Rule("GATE_TABLE_PARSE", "A", "Mx-gate.md 表格可解析", check_gate_table_parse),
    Rule("GATE_TABLE_WIDTH", "A", "Mx-gate.md 表格列数（设计 8 列）", check_gate_table_width),
    Rule("GATE_ID_FORMAT", "A", "GATE ID 格式 M{N}-GATE-{NN}", check_gate_id_format),
    Rule("GATE_ID_MODULE", "A", "GATE ID 模块号与文件名一致", check_gate_id_module),
    Rule("GATE_ID_UNIQUE", "A", "GATE ID 全 M1-M6 唯一", check_gate_id_unique),
    Rule("GATE_CATEGORY", "A", "GATE 分类在白名单内", check_gate_category),
    Rule("GATE_RISK", "A", "GATE 风险等级在白名单内", check_gate_risk),
    Rule("GATE_SOURCE", "A", "GATE 来源 ID 必填", check_gate_source),
    Rule("PATTERN_COUNT", "A", "视觉模式文件数 = 当前基线（10）", check_pattern_count),
    Rule("PATTERN_FILENAME", "A", "视觉模式文件名 NN-id.md", check_pattern_filename),
    Rule("PATTERN_SEQUENCE", "A", "视觉模式序号 01..10", check_pattern_sequence),
    Rule("PATTERN_ID", "A", "视觉模式 frontmatter id 与文件名一致", check_pattern_id),
    Rule("PATTERN_METADATA", "A", "视觉模式 frontmatter 字段完整", check_pattern_metadata),
    Rule("PATTERN_ENUM", "A", "视觉模式 layout/formality/density 取值在白名单内", check_pattern_enum),
    Rule("LOCAL_LINK", "A", "Markdown 本地链接目标存在", check_local_link),
    Rule("DEPRECATED_TERM", "A", "文档不得出现废弃术语（除非显式说明废弃）", check_deprecated_term),
    # Phase B
    Rule("GATE_SECTION_SYNC", "B", "闸门文件必填 section ⊆ workshop-canvas-map", check_gate_section_sync),
    Rule("RENDER_SECTION_SYNC", "B", "render-contract.md 锚点与 audit 脚本一致", check_render_section_sync),
    Rule("SKILL_TEMPLATE_SYNC", "B", "examples 模板 section 与 workshop-canvas-map 一致", check_template_skill_sync),
    Rule("STATE_ENUM_SYNC", "B", "权威文档状态值在 5 态白名单内", check_state_enum),
    Rule("AUTH_FIELDS", "B", "schema 必含 4 个授权字段", check_auth_fields),
    Rule("OVERRIDE_CATEGORY", "B", "override_audit.items.category enum ⊆ {business_risk}", check_override_category),
)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def run_checks(
    root: Path,
    selected: Sequence[str] | None = None,
    stop_on_error: bool = False,
) -> list[Finding]:
    ctx = CheckContext(root=root.resolve())
    findings: list[Finding] = []
    selected_set: set[str] = set(selected) if selected else set[str]()
    for rule in RULES:
        if selected_set and rule.code not in selected_set:  # pylint: disable=unsupported-membership-test
            continue
        # 注入 plugin（让单条规则在 --rules 过滤时仍可工作）
        _ensure_plugin(ctx)
        try:
            new_findings = rule.runner(ctx)
        except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:  # noqa: BLE001  # 防御：单条规则崩溃不应让整次检查失败
            new_findings = [
                Finding(
                    code=rule.code,
                    level="error",
                    where="<runner>",
                    message=f"规则执行异常：{type(exc).__name__}: {exc}",
                    hint="请将此问题反馈给门禁维护者",
                )
            ]
        findings.extend(new_findings)
        if stop_on_error and any(f.level == "error" for f in new_findings):
            break
    return findings


def render_text(findings: list[Finding]) -> str:
    if not findings:
        return "OK：契约一致性检查全部通过。"
    counts = Counter(f.level for f in findings)
    header = (
        f"契约一致性检查结果：error={counts.get('error', 0)}, "
        f"warning={counts.get('warning', 0)}, info={counts.get('info', 0)}"
    )
    lines = [header, "-" * len(header), ""]
    by_code: dict[str, list[Finding]] = {}
    for f in findings:
        by_code.setdefault(f.code, []).append(f)
    for code in sorted(by_code):
        group = by_code[code]
        lines.append(f"[{group[0].level.upper()}] {code}（{len(group)} 条）")
        for f in group:
            where = f.where or "-"
            lines.append(f"  - {where}: {f.message}")
            if f.hint:
                lines.append(f"      建议：{f.hint}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_json(findings: list[Finding]) -> str:
    return json.dumps(
        {
            "count": len(findings),
            "findings": [f.to_dict() for f in findings],
        },
        ensure_ascii=False,
        indent=2,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pratyaya 契约一致性检查器（阶段 A + 阶段 B）",
    )
    _ = parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        help=f"仓库根目录（默认 {DEFAULT_ROOT}）",
    )
    _ = parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出",
    )
    _ = parser.add_argument(
        "--strict",
        action="store_true",
        help="将 warning 视作 error 退出",
    )
    _ = parser.add_argument(
        "--rules",
        default="",
        help="只跑指定规则（逗号分隔 code）",
    )
    _ = parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有规则后退出",
    )
    args = parser.parse_args(argv)

    list_opt = cast(bool, args.list)
    root_opt = cast(str, args.root)
    json_opt = cast(bool, args.json)
    rules_opt = cast(str, args.rules)
    strict_opt = cast(bool, args.strict)

    if list_opt:
        for rule in RULES:
            print(f"{rule.code}\t{rule.category}\t{rule.description}")
        return 0

    root = Path(root_opt).resolve()
    if not root.is_dir():
        print(f"root 不是有效目录：{root}", file=sys.stderr)
        return 2

    selected = [s.strip() for s in rules_opt.split(",") if s.strip()] or None
    findings = run_checks(root, selected=selected)

    if json_opt:
        print(render_json(findings))
    else:
        print(render_text(findings))

    has_error = any(f.level == "error" for f in findings)
    has_warning = any(f.level == "warning" for f in findings)
    if has_error:
        return 1
    if strict_opt and has_warning:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
