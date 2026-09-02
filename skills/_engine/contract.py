"""确认包结构契约校验（只做结构，不做内容）。

红线（§7.1）：
- ✅ 引擎做：文件名契约、slug/version 与文件名/state 一致、ID 格式、状态枚举合法。
- ❌ 引擎不做：判断内容是否充分 / 隐含推断、补写内容、改写用户已确认表述。
  越界症状：本模块与 Gate Skill 对同一确认包给出冲突判定时，以 Gate Skill（LLM）为准。

依赖：只依赖 `canvas_registry`（零副作用）+ 标准库。
"""

from __future__ import annotations

import re
from typing import Any

from . import canvas_registry, session
from .canvas_registry import CanvasSpec

# 确认包文件名：`{前缀}-{slug}-v{N}.md`。前缀可含连字符（V2C-VAC / 5W），
# slug 为 kebab-case ASCII，末尾 `-v{数字}`。
_FILENAME_RE = re.compile(r"^(.+?)-([a-z0-9]+(?:-[a-z0-9]+)*)-v(\d+)\.md$")

# MVL 模块确认包文件名：`M{1-6}-v{N}.md`（无 slug）。
_MVL_FILENAME_RE = re.compile(r"^(M[1-6])-v(\d+)\.md$")

# 治理元数据小节（升版边界：第 12 节 Gate 与用户决策，分 12.1 / 12.2 / 12.3）。
GOVERNANCE_SECTION_MARKERS = ("12.1", "12.2", "12.3")


class ContractError(ValueError):
    """结构契约违反。"""


def parse_confirmation_filename(filename: str) -> dict[str, Any] | None:
    """解析非 MVL 确认包文件名 `{前缀}-{slug}-v{N}.md`，返回 {prefix, slug, version}。

    不匹配返回 None。
    """
    m = _FILENAME_RE.match(filename)
    if not m:
        return None
    return {"prefix": m.group(1), "slug": m.group(2), "version": int(m.group(3))}


def parse_mvl_filename(filename: str) -> dict[str, Any] | None:
    """解析 MVL 确认包文件名 `M{1-6}-v{N}.md`，返回 {module, version}。"""
    m = _MVL_FILENAME_RE.match(filename)
    if not m:
        return None
    return {"module": m.group(1), "version": int(m.group(2))}


def gate_id_regex(canvas_id: str) -> re.Pattern[str]:
    """由注册表 `gate_id_prefix` 派生 Gate 检查项 ID 格式。

    - mvl：`M{1-6}-GATE-{两位数字}`（模块号 + 两位序号）；
    - 其余：`{前缀}-{数字}`（如 `GC-GATE-01`、`5W-GATE-04`）。
    """
    spec = canvas_registry.by_id(canvas_id)
    if spec is None:
        raise ContractError(f"未知 canvas_id：{canvas_id!r}")
    if canvas_id == "mvl":
        return re.compile(r"^M[1-6]-GATE-\d{2}$")
    base = re.escape(spec.gate_id_prefix.rstrip("-"))
    return re.compile(rf"^{base}-\d+$")


def validate_gate_ids(text: str, canvas_id: str) -> list[str]:
    """校验文本中出现的 Gate ID 是否符合注册表前缀格式，返回问题列表（空 = 通过）。

    只按前缀 + 数字结构校验，不做逐项 ID 是否在 Gate 参考清单内的语义判定。
    """
    spec = canvas_registry.by_id(canvas_id)
    if spec is None:
        return [f"未知 canvas_id：{canvas_id!r}"]
    pattern = gate_id_regex(canvas_id)
    # 提取 Gate ID 候选：mvl 为 `M{1-6}-GATE-{数字}`（两位序号），其余为 `{前缀}-{数字}`。
    if canvas_id == "mvl":
        candidates = re.findall(r"M[1-6]-GATE-\d+", text)
    else:
        prefix = re.escape(spec.gate_id_prefix.rstrip("-"))
        candidates = re.findall(rf"{prefix}-\d+", text)
    problems: list[str] = []
    for c in candidates:
        if not pattern.match(c):
            problems.append(f"Gate ID 格式不符：{c!r}")
    return problems


def assert_filename_consistent(
    filename: str,
    *,
    canvas_id: str,
    slug: str,
    version: int,
) -> None:
    """校验确认包文件名与 canvas_id / slug / version 三元一致，不一致即 raise。"""
    spec = canvas_registry.by_id(canvas_id)
    if spec is None:
        raise ContractError(f"未知 canvas_id：{canvas_id!r}")

    if canvas_id == "mvl":
        parsed = parse_mvl_filename(filename)
        if parsed is None:
            raise ContractError(f"MVL 确认包文件名非法：{filename!r}")
        if parsed["version"] != version:
            raise ContractError(
                f"确认包文件名版本 {parsed['version']} 与 state version {version} 不一致"
            )
        return

    parsed = parse_confirmation_filename(filename)
    if parsed is None:
        raise ContractError(f"确认包文件名非法：{filename!r}（须为 {{前缀}}-{{slug}}-v{{N}}.md）")
    if parsed["prefix"] != spec.file_prefix:
        raise ContractError(f"确认包前缀 {parsed['prefix']!r} != 注册表 {spec.file_prefix!r}")
    if parsed["slug"] != slug:
        raise ContractError(f"确认包 slug {parsed['slug']!r} != state slug {slug!r}")
    if parsed["version"] != version:
        raise ContractError(f"确认包版本 {parsed['version']} != state version {version}")


def validate_version_marker(text: str, version: int) -> list[str]:
    """校验确认包正文存在 `v{N}` 版本标记（结构存在性，不判语义）。"""
    if re.search(rf"\bv{version}\b", text):
        return []
    return [f"确认包正文缺少版本标记 v{version}"]


def validate_governance_sections(text: str) -> list[str]:
    """校验确认包含治理元数据小节（12.1 Gate 建议 / 12.2 用户决策 / 12.3 Override 审计）。

    只按小节编号结构存在性校验；override 时 12.3 是否必填由 authorization 校验。
    """
    problems: list[str] = []
    for marker in GOVERNANCE_SECTION_MARKERS:
        if marker not in text:
            problems.append(f"确认包缺治理小节 {marker}")
    return problems
