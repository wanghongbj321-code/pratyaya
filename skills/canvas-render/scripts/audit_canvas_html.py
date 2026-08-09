#!/usr/bin/env python3
"""Deterministic static audit for pratyaya Canvas HTML files (MVL + Golden Circle + HMW + Persona)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Union, cast

# JSON 反序列化后的通用值/字典类型（已知联合，避免 Any/Unknown 透传）
JsonValue = Union[
    str, int, float, bool, None, list["JsonValue"], dict[str, "JsonValue"]
]
JsonDict = dict[str, JsonValue]


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = (
    REPO_ROOT / "references" / "render-contract.md"
)
GC_CONTRACT = (
    REPO_ROOT / "references" / "render-contract-gc.md"
)
HMW_CONTRACT = (
    REPO_ROOT / "references" / "render-contract-hmw.md"
)
JOURNEY_CONTRACT = (
    REPO_ROOT / "references" / "render-contract-journey.md"
)
PERSONA_CONTRACT = (
    REPO_ROOT / "references" / "render-contract-persona.md"
)
HMW_TEMPLATE = (
    REPO_ROOT / "examples" / "hmw-canvas.html"
)
JOURNEY_TEMPLATE = (
    REPO_ROOT / "examples" / "user-journey-canvas.html"
)
HMW_TPL_MAIN_IDS = (
    "hmw-statement",
    "hmw-ideas",
    "hmw-coherence",
    "hmw-quality",
    "quality-panel",
    "local-notes",
    "canvas-data",
)
HMW_TPL_STABLE_ANCHORS = (
    "hmw-situation", "hmw-question", "hmw-for", "hmw-sothat",
    "hmw-quality-preset", "hmw-quality-vague",
    "hmw-quality-moment", "hmw-quality-tension",
    "hmw-idea-1", "hmw-idea-2", "hmw-idea-3", "hmw-idea-4",
    "hmw-idea-5", "hmw-idea-6", "hmw-idea-7", "hmw-idea-8",
    "hmw-coherence-map",
)
HMW_TPL_GOVERN_IDS = (
    "quality-version",
    "quality-approval",
    "quality-gaps",
    "quality-risks",
    "quality-caveat",
)
JOURNEY_TPL_MAIN_IDS = (
    "canvas-header",
    "journey-map",
    "journey-quality",
    "quality-panel",
    "local-notes",
    "canvas-data",
)
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
JOURNEY_MAIN_IDS = (
    "journey-map",
    "journey-quality",
)
JOURNEY_ANCHORS = (
    "canvas-headline",
    *JOURNEY_QUALITY_ANCHORS,
)
PERSONA_MAIN_IDS = (
    "persona-name",
    "persona-gender",
    "persona-age",
    "persona-location",
    "persona-education",
    "persona-job-title",
    "persona-industry",
    "persona-family-status",
    "persona-income",
    "persona-description",
    "persona-goals-needs",
    "persona-behaviors",
    "persona-pain-points",
    "persona-motivation",
    "persona-decision-factors",
)
PERSONA_STABLE_ANCHORS = (
    "canvas-headline",
    "persona-name",
    "persona-gender",
    "persona-age",
    "persona-location",
    "persona-education",
    "persona-job-title",
    "persona-industry",
    "persona-family-status",
    "persona-income",
    "persona-description",
    "persona-goals-needs",
    "persona-behaviors",
    "persona-pain-points",
    "persona-motivation",
    "persona-decision-factors",
)
PERSONA_TPL_GOVERN_IDS = (
    "quality-version",
    "quality-approval",
    "quality-gaps",
    "quality-risks",
    "quality-caveat",
)
# 约定隐藏方式（Template Gate 与内容/授权 Gate 共用）：任一命中即视为隐藏
HIDDEN_PATTERNS = (
    r"hidden\b",  # hidden HTML 属性
    r"display\s*:\s*none",  # style="display:none"
    r"visibility\s*:\s*hidden",  # style="visibility:hidden"
    r"class\s*=\s*[\"'][^\"']*\bhidden\b",  # class="hidden"
)
MODULE_MAIN_IDS = (
    "module-summary",
    "module-outputs",
    "module-conclusions",
    "module-evidence",
    "module-gaps",
)
GLOBAL_MAIN_IDS = ("intent", "user", "agent-team", "workflow", "context", "validation")
GC_MAIN_IDS = ("why", "how", "what", "cross-layer-alignment")
GC_ANCHORS = (
    "canvas-headline",
    "why-belief", "why-purpose", "why-mission",
    "how-principles", "how-differentiation", "how-methods",
    "what-products", "what-services", "what-evidence",
    "alignment-why-how", "alignment-how-what",
)
HMW_MAIN_IDS = (
    "hmw-statement",
    "hmw-quality",
    "hmw-ideas",
    "hmw-coherence",
)
HMW_ANCHORS = (
    "canvas-headline",
    "hmw-situation", "hmw-question", "hmw-for", "hmw-sothat",
    "hmw-quality-preset", "hmw-quality-vague",
    "hmw-quality-moment", "hmw-quality-tension",
    "hmw-idea-1", "hmw-idea-2", "hmw-idea-3", "hmw-idea-4",
    "hmw-idea-5", "hmw-idea-6", "hmw-idea-7", "hmw-idea-8",
    "hmw-coherence-map",
)
SHARED_IDS = (
    "canvas-header",
    "quality-panel",
    "quality-version",
    "quality-approval",
    "quality-gaps",
    "quality-risks",
    "quality-caveat",
    "alignment-section",
    "local-notes",
    "canvas-data",
)
AUTH_FIELDS = (
    "gate_recommendation",
    "render_authorized",
    "confirmation_mode",
    "override_audit",
)
INSTANCE_STATE_KEYS = {
    "gc": "golden_circle",
    "hmw": "hmw",
    "persona": "persona",
    "journey": "journey",
}
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


@dataclass(frozen=True)
class Finding:
    """一条审计发现（code 为规则代号，message 为人类可读说明）。"""

    code: str
    message: str


@dataclass
class HtmlSnapshot:
    """一次 HTML 解析后的结构化快照，供审计逻辑使用。"""

    body_attrs: dict[str, str]
    ids: list[str]
    output_ids: list[str]
    tags: list[str]
    attrs_by_id: dict[str, dict[str, str]]
    canvas_data_text: str
    text: str
    text_by_id: dict[str, str]
    external_urls: list[str]


class CanvasParser(HTMLParser):
    """遍历 Canvas HTML，收集 id、标签、属性与 canvas-data 片段。"""
    module_outputs_depth: int
    canvas_data_depth: int

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.body_attrs: dict[str, str] = {}
        self.ids: list[str] = []
        self.output_ids: list[str] = []
        self.tags: list[str] = []
        self.attrs_by_id: dict[str, dict[str, str]] = {}
        self.external_urls: list[str] = []
        self.text_parts: list[str] = []
        self.text_parts_by_id: dict[str, list[str]] = {}
        self.canvas_data_parts: list[str] = []
        self.stack: list[tuple[str, str | None]] = []
        self.module_outputs_depth = 0
        self.canvas_data_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        element_id = values.get("id")
        self.tags.append(tag)
        if tag == "body":
            self.body_attrs = values
        if element_id:
            self.ids.append(element_id)
            _ = self.attrs_by_id.setdefault(element_id, values)
            if self.module_outputs_depth:
                self.output_ids.append(element_id)
        if element_id == "module-outputs":
            self.module_outputs_depth = len(self.stack) + 1
        if element_id == "canvas-data":
            self.canvas_data_depth = len(self.stack) + 1
        for name in ("src", "href"):
            value = values.get(name, "").strip()
            if value.startswith(("http://", "https://", "//")):
                self.external_urls.append(value)
        if tag not in VOID_TAGS:
            self.stack.append((tag, element_id))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break
        if self.module_outputs_depth and len(self.stack) < self.module_outputs_depth:
            self.module_outputs_depth = 0
        if self.canvas_data_depth and len(self.stack) < self.canvas_data_depth:
            self.canvas_data_depth = 0

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)
        for _, element_id in self.stack:
            if element_id:
                self.text_parts_by_id.setdefault(element_id, []).append(data)
        if self.canvas_data_depth:
            self.canvas_data_parts.append(data)

    def error(self, message: str) -> None:
        raise ValueError(message)

    def snapshot(self) -> HtmlSnapshot:
        """返回当前解析状态的 HtmlSnapshot 快照。"""
        return HtmlSnapshot(
            body_attrs=self.body_attrs,
            ids=self.ids,
            output_ids=self.output_ids,
            tags=self.tags,
            attrs_by_id=self.attrs_by_id,
            canvas_data_text="".join(self.canvas_data_parts).strip(),
            text="".join(self.text_parts),
            text_by_id={element_id: "".join(parts) for element_id, parts in self.text_parts_by_id.items()},
            external_urls=self.external_urls,
        )


def normalize_version(value: object) -> str | None:
    """将版本字符串规整为 ``v<n>`` 形式；无法解析时返回 None。"""
    if value is None:
        return None
    match = re.fullmatch(r"v?(\d+)", str(value).strip(), re.IGNORECASE)
    return f"v{match.group(1)}" if match else None


def load_contract_anchor_orders(path: Path) -> dict[str, list[str]]:
    """从 render-contract.md 解析 M1-M6 各模块详情区的锚点 id 顺序表。"""
    text = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"^### M([1-6]) 模块详情\s*$", text, re.MULTILINE))
    orders: dict[str, list[str]] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else text.find("\n**关键规则**", heading.end())
        if end < 0:
            end = len(text)
        section = text[heading.end() : end]
        anchors = re.findall(r"\|\s*`id=\"([^\"]+)\"`\s*\|", section)
        if not anchors:
            raise ValueError(f"contract section M{heading.group(1)} has no anchor rows")
        orders[f"M{heading.group(1)}"] = anchors
    if set(orders) != {f"M{number}" for number in range(1, 7)}:
        raise ValueError("contract must define anchor tables for M1-M6")
    return orders


def parse_html(path: Path) -> tuple[str, HtmlSnapshot]:
    """解析 Canvas HTML，返回原始文本与结构化快照。"""
    source = path.read_text(encoding="utf-8")
    parser = CanvasParser()
    parser.feed(source)
    parser.close()
    return source, parser.snapshot()


def expected_in_order(actual: Iterable[str], expected: list[str]) -> bool:
    """判断 actual 中保留下来的 expected 元素是否按预期顺序排列。"""
    expected_set = set(expected)
    return [item for item in actual if item in expected_set] == expected


def load_json(path: Path) -> JsonDict:
    """读取并校验 JSON 文件，要求其为 JSON 对象，返回类型化的字典。"""
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return cast(JsonDict, raw)


def source_identity(path: Path) -> tuple[str | None, str | None]:
    """从 Mx-vN 确认包首行标题中提取模块代号与版本号。"""
    first_lines = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
    match = re.search(r"^#\s+(M[1-6])\s+确认包\s+(v\d+)\s*$", first_lines, re.MULTILINE)
    return (match.group(1), match.group(2)) if match else (None, None)


def load_gc_anchor_orders(path: Path) -> list[str]:
    """从 render-contract-gc.md 解析 GC 稳定锚点列表。"""
    text = path.read_text(encoding="utf-8")
    anchors = re.findall(r"\|\s*`([a-z][a-z0-9_-]+)`\s*\|", text)
    if not anchors:
        raise ValueError("GC contract has no anchor rows")
    return anchors


def gc_source_identity(path: Path) -> tuple[str | None, str | None]:
    """从 GC-vN 确认包首行标题中提取画布类型与版本号。"""
    first_lines = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
    match = re.search(r"^#\s+黄金圈确认包\s+(v\d+)\s*$", first_lines, re.MULTILINE)
    return ("GC", match.group(1)) if match else (None, None)


def hmw_source_identity(path: Path) -> tuple[str | None, str | None]:
    """从 HMW-vN 确认包首行标题中提取画布类型与版本号。"""
    first_lines = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
    match = re.search(r"^#\s+HMW 确认包\s+(v\d+)\s*$", first_lines, re.MULTILINE)
    return ("HMW", match.group(1)) if match else (None, None)


def journey_source_identity(path: Path) -> tuple[str | None, str | None]:
    """从 JOURNEY-vN 确认包首行标题中提取画布类型与版本号。"""
    first_lines = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
    match = re.search(r"^#\s+User Journey 确认包\s+(v\d+)\s*$", first_lines, re.MULTILINE)
    return ("JOURNEY", match.group(1)) if match else (None, None)
def persona_source_identity(path: Path) -> tuple[str | None, str | None]:
    """从 PERSONA-vN 确认包首行标题中提取画布类型与版本号。"""
    first_lines = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
    match = re.search(
        r"^#\s+(?:User Persona|用户画像)\s*确认包\s+(v\d+)\s*$",
        first_lines,
        re.MULTILINE,
    )
    return ("PERSONA", match.group(1)) if match else (None, None)


def maau_source_identity(path: Path) -> tuple[str | None, str | None]:
    """从 MAAU-{slug}-vN 源包头部提取 slug 与版本号。

    返回 ``(slug, "vN")``；无法解析时返回 ``(None, None)``。
    """
    try:
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:20])
    except OSError:
        return (None, None)
    version_match = re.search(r"^#\s+MAAU 六板块源包\s+(v\d+)\s*$", head, re.MULTILINE)
    slug_match = re.search(r"^> slug：\s*([a-z0-9]+(-[a-z0-9]+)*)\s*$", head, re.MULTILINE)
    version = version_match.group(1) if version_match else None
    slug = slug_match.group(1) if slug_match else None
    return (slug, version)


def select_maau_instance_state(state: JsonDict, instance_slug: str | None) -> JsonDict | None:
    """从 state.maau.{slug} 选择 MAAU transcript-direct 实例。"""
    if instance_slug is None:
        raise ValueError("--instance is required when auditing MAAU transcript-direct with --state")
    instances = state.get("maau")
    if not isinstance(instances, dict):
        return None
    instance = instances.get(instance_slug)
    if not isinstance(instance, dict):
        return None
    if instance.get("slug") != instance_slug:
        raise ValueError(f"state.maau.{instance_slug}.slug must match map key")
    return cast(JsonDict, instance)


def audit_maau_override(canvas_data: JsonDict) -> list[Finding]:
    """校验 MAAU override 审计项：assessment_id 为 MAAU-GATE-* 且 category=business_risk。"""
    findings: list[Finding] = []
    auth = canvas_data.get("auth")
    if not isinstance(auth, dict):
        return findings
    if auth.get("confirmation_mode") != "override":
        return findings
    override = auth.get("override_audit")
    if not isinstance(override, dict):
        findings.append(Finding("MAAU_OVERRIDE", "override_audit must be an object"))
        return findings
    items = override.get("items")
    if not isinstance(items, list):
        findings.append(Finding("MAAU_OVERRIDE", "override_audit.items must be an array"))
        return findings
    for item in items:
        if not isinstance(item, dict):
            findings.append(Finding("MAAU_OVERRIDE", "override_audit item must be an object"))
            continue
        assessment_id = str(item.get("assessment_id", ""))
        if not re.fullmatch(r"MAAU-GATE-[0-9]+", assessment_id):
            findings.append(
                Finding(
                    "MAAU_OVERRIDE",
                    f"assessment_id={assessment_id!r} must match MAAU-GATE-[0-9]+",
                )
            )
        if item.get("category") != "business_risk":
            findings.append(
                Finding(
                    "MAAU_OVERRIDE",
                    f"assessment_id={assessment_id!r} category must be business_risk, got {item.get('category')!r}",
                )
            )
    return findings


def audit_maau_transcript_direct(
    source: str,
    canvas_data: JsonDict,
    body_instance: str | None,
    source_path: Path | None,
    instance_slug: str | None,
) -> list[Finding]:
    """校验 MAAU transcript-direct 实例页的专属契约。

    - canvas-data.generation_path == transcript-direct
    - HTML data-instance 与 canvas-data.instance == slug
    - canvas-data.source_file 与 --source / state 一致
    - [来源: transcript-direct] 标头
    - override 时 override_audit.items[].assessment_id 为 MAAU-GATE-* 且 category=business_risk
    """
    findings: list[Finding] = []

    generation_path = canvas_data.get("generation_path")
    if generation_path != "transcript-direct":
        findings.append(
            Finding(
                "MAAU_GENERATION",
                f"canvas-data.generation_path must be 'transcript-direct', got {generation_path!r}",
            )
        )

    if instance_slug is not None:
        if body_instance != instance_slug:
            findings.append(
                Finding(
                    "INSTANCE",
                    f"body data-instance={body_instance!r} must match --instance {instance_slug!r}",
                )
            )
        data_instance = canvas_data.get("instance")
        if data_instance != instance_slug:
            findings.append(
                Finding(
                    "INSTANCE",
                    f"canvas-data.instance={data_instance!r} must match --instance {instance_slug!r}",
                )
            )

    if "[来源: transcript-direct]" not in source:
        findings.append(Finding("MAAU_HEADER", "missing '[来源: transcript-direct]' header"))

    source_file = canvas_data.get("source_file")
    if source_path is not None:
        expected_source_file = source_path.name
        if source_file != expected_source_file:
            findings.append(
                Finding(
                    "MAAU_SOURCE_FILE",
                    f"canvas-data.source_file={source_file!r} must match --source name {expected_source_file!r}",
                )
            )
    else:
        if not source_file:
            findings.append(Finding("MAAU_SOURCE_FILE", "canvas-data.source_file is required"))

    findings.extend(audit_maau_override(canvas_data))

    return findings


def load_persona_template_profile(contract_path: Path) -> dict[str, list[str]]:
    """从 render-contract-persona.md 解析 Persona 模板结构 profile（一级模块顺序 + 稳定锚点）。

    返回 {"main_order": [...], "stable_anchors": [...]}。
    """
    text = contract_path.read_text(encoding="utf-8")
    main_order: list[str] = []
    stable_anchors: list[str] = []

    # 解析一级模块顺序（§4）
    order_match = re.search(
        r"## 4\.\s*一级模块顺序.*?\n```text\s*(.*?)```",
        text,
        re.DOTALL,
    )
    if order_match:
        for line in order_match.group(1).splitlines():
            m = re.match(r"\s*→\s*([a-z][a-z0-9-]+)\s*$", line)
            if m:
                main_order.append(m.group(1))

    # 解析稳定锚点集合（§5）
    anchor_match = re.search(
        r"## 5\.\s*稳定锚点集合.*?\n(.*?)(?=\n## |\Z)",
        text,
        re.DOTALL,
    )
    if anchor_match:
        # 基本信息 9 字段 + 六宫格 6 区 + 质量 4 维度
        stable_anchors = re.findall(r"`(persona-[a-z0-9-]+)`", anchor_match.group(1))

    return {"main_order": main_order, "stable_anchors": stable_anchors}


def load_hmw_template_profile(contract_path: Path) -> dict[str, list[str]]:
    """从 render-contract-hmw.md 解析 HMW 模板结构 profile（一级模块顺序 + 稳定锚点）。

    返回 {"main_order": [...], "stable_anchors": [...]}。
    """
    text = contract_path.read_text(encoding="utf-8")
    main_order: list[str] = []
    stable_anchors: list[str] = []

    order_match = re.search(
        r"### 一级模块必需性与 DOM 相对顺序（强制）\s*```text\s*(.*?)```",
        text,
        re.DOTALL,
    )
    if order_match:
        for line in order_match.group(1).splitlines():
            m = re.match(r"\s*→\s*([a-z][a-z0-9-]+)\s*$", line)
            if m:
                main_order.append(m.group(1))

    anchor_match = re.search(
        r"### 稳定锚点集合（Template Gate 校验）(.*?)(?=\n### |\Z)",
        text,
        re.DOTALL,
    )
    if anchor_match:
        stable_anchors = re.findall(
            r"`(hmw-[a-z0-9-]+|quality-[a-z0-9-]+|local-notes|canvas-data)`",
            anchor_match.group(1),
        )
    return {"main_order": main_order, "stable_anchors": stable_anchors}


def load_journey_template_profile(contract_path: Path) -> dict[str, list[str]]:
    """从 render-contract-journey.md 解析 Journey 模板结构 profile。"""
    text = contract_path.read_text(encoding="utf-8")
    main_order: list[str] = []
    stable_anchors: list[str] = []

    order_match = re.search(
        r"### 一级模块必需性与 DOM 相对顺序（强制）\s*```text\s*(.*?)```",
        text,
        re.DOTALL,
    )
    if order_match:
        for line in order_match.group(1).splitlines():
            m = re.match(r"\s*→\s*([a-z][a-z0-9-]+)\s*$", line)
            if m:
                main_order.append(m.group(1))

    anchor_match = re.search(
        r"### 稳定锚点集合（Template Gate 校验）(.*?)(?=\n### |\Z)",
        text,
        re.DOTALL,
    )
    if anchor_match:
        stable_anchors = re.findall(
            r"`(journey-[a-z0-9-]+|quality-[a-z0-9-]+|local-notes|canvas-data)`",
            anchor_match.group(1),
        )
    return {"main_order": main_order, "stable_anchors": stable_anchors}


def element_is_hidden(source: str, attrs: dict[str, str]) -> bool:
    """判断元素是否以约定方式隐藏（hidden 属性 / display:none / visibility:hidden / class=hidden）。"""
    if "hidden" in attrs:
        return True
    style = attrs.get("style", "")
    if re.search(r"display\s*:\s*none", style, re.IGNORECASE):
        return True
    if re.search(r"visibility\s*:\s*hidden", style, re.IGNORECASE):
        return True
    classes = attrs.get("class", "").split()
    if "hidden" in classes:
        return True
    return False


def stylesheet_hides_element(source: str, element_id: str) -> bool:
    """检查 style 标签中直接命中指定 id 的隐藏规则。"""
    for stylesheet in re.findall(r"<style[^>]*>(.*?)</style>", source, re.IGNORECASE | re.DOTALL):
        for selectors, declarations in re.findall(r"([^{}]+)\{([^{}]*)\}", stylesheet, re.DOTALL):
            if f"#{element_id}" not in selectors:
                continue
            if re.search(r"display\s*:\s*none|visibility\s*:\s*hidden", declarations, re.IGNORECASE):
                return True
    return False


def audit_template_gate(
    html: HtmlSnapshot,
    source: str,
    html_path: Path,
    template: HtmlSnapshot,
    profile: dict[str, list[str]],
    gate_prefix: str = "HMW",
    check_ids: tuple[str, ...] = HMW_TPL_MAIN_IDS,
    check_stable_anchors: tuple[str, ...] = HMW_TPL_STABLE_ANCHORS,
    check_govern_ids: tuple[str, ...] = HMW_TPL_GOVERN_IDS,
    hidden_section_ids: tuple[str, ...] = ("hmw-quality", "hmw-coherence", "quality-panel"),
) -> list[Finding]:
    """Template Gate：比较成品与模板的一级模块、稳定锚点与相对 DOM 顺序。

    所有规则均为不可 override 的结构完整性检查（{gate_prefix}-TPL-GATE-01..06）。
    """
    findings: list[Finding] = []
    counts = Counter(html.ids)
    main_order = profile.get("main_order") or list(check_ids)

    # {gate_prefix}-TPL-GATE-01: data-page-type 与模板一致
    page_type = html.body_attrs.get("data-page-type")
    tpl_page_type = template.body_attrs.get("data-page-type")
    if page_type != tpl_page_type:
        findings.append(
            Finding(
                f"{gate_prefix}-TPL-GATE-01",
                f"data-page-type={page_type!r} 与模板 {tpl_page_type!r} 不一致",
            )
        )

    # {gate_prefix}-TPL-GATE-02: 一级模块全部存在且唯一
    missing = [i for i in main_order if counts[i] == 0]
    if missing:
        findings.append(Finding(f"{gate_prefix}-TPL-GATE-02", f"一级模块缺失: {', '.join(missing)}"))
    duplicates = [i for i in main_order if counts[i] > 1]
    if duplicates:
        findings.append(Finding(f"{gate_prefix}-TPL-GATE-02", f"一级模块重复: {', '.join(duplicates)}"))

    # {gate_prefix}-TPL-GATE-03: 一级模块 DOM 相对顺序符合模板 profile
    actual = [i for i in html.ids if i in set(main_order)]
    if actual != main_order:
        findings.append(
            Finding(
                f"{gate_prefix}-TPL-GATE-03",
                f"一级模块顺序偏离 profile: 期望 {main_order}, 实际 {actual}",
            )
        )

    # {gate_prefix}-TPL-GATE-04: 稳定锚点完整
    anchors = profile.get("stable_anchors") or list(check_stable_anchors)
    anchor_missing = [a for a in anchors if counts[a] == 0]
    if anchor_missing:
        findings.append(
            Finding(f"{gate_prefix}-TPL-GATE-04", f"稳定锚点缺失: {', '.join(anchor_missing)}")
        )

    # {gate_prefix}-TPL-GATE-05: quality-panel 含版本/授权/缺口/风险/caveat 插槽
    govern_missing = [i for i in check_govern_ids if counts[i] == 0]
    if govern_missing:
        findings.append(
            Finding(f"{gate_prefix}-TPL-GATE-05", f"quality-panel 缺插槽: {', '.join(govern_missing)}")
        )

    # {gate_prefix}-TPL-GATE-06: 共享主题/窄屏/@media print 钩子 + 无外部依赖
    # 方案 A（2026-08-09）：主题必须自包含——内联 <style>（含 [data-theme] 与主色 token）或
    # 指向本地已存在文件的 <link> 均视为合法；但**正式产物禁止依赖本地相对路径外链 CSS**，
    # 否则单独传播 HTML 时样式丢失。外部网络依赖恒为 FAIL。
    if "@media print" not in source.lower():
        findings.append(Finding(f"{gate_prefix}-TPL-GATE-06", "缺少 @media print 钩子"))
    if html.external_urls:
        findings.append(
            Finding(f"{gate_prefix}-TPL-GATE-06", f"存在外部网络依赖: {', '.join(html.external_urls)}")
        )
    stylesheet_hrefs = re.findall(
        r'<link\b[^>]*\brel=["\']stylesheet["\'][^>]*\bhref=["\']([^"\']+)["\']',
        source,
        re.IGNORECASE,
    )
    theme_inlined = bool(
        re.search(r"\[data-theme[^]]*\]", source)
        and re.search(r"--brand\s*:", source)
        and re.search(r"<style", source, re.IGNORECASE)
    )
    if not stylesheet_hrefs and not theme_inlined:
        findings.append(Finding(f"{gate_prefix}-TPL-GATE-06", "缺少共享主题（既无 <link> 外链也无内联 <style> 主题）"))
    for href in stylesheet_hrefs:
        if href.startswith(("http://", "https://", "//")):
            continue
        stylesheet_path = (html_path.parent / href).resolve()
        if not stylesheet_path.is_file():
            findings.append(Finding(f"{gate_prefix}-TPL-GATE-06", f"本地主题资源不存在: {href}"))
            continue
        # 正式产物禁止依赖本地相对路径外链 CSS（方案 A 收口）
        findings.append(
            Finding(f"{gate_prefix}-TPL-GATE-06", f"正式产物依赖本地相对路径外链 CSS: {href}（应内联）")
        )

    # 附加：质量鉴别 / 想法对应 / 治理面板不得隐藏（四态 hidden 检测）
    for section_id in hidden_section_ids:
        attrs = html.attrs_by_id.get(section_id, {})
        if counts[section_id] and (
            element_is_hidden(source, attrs) or stylesheet_hides_element(source, section_id)
        ):
            findings.append(
                Finding(
                    f"{gate_prefix}-TPL-GATE-06",
                    f"{section_id} 被隐藏（hidden/display:none/visibility:hidden/class=hidden 任一）",
                )
            )

    return findings


def journey_stage_numbers(ids: list[str]) -> list[int]:
    """提取 `journey-stage-{n}` 一级阶段锚点编号。"""
    numbers: list[int] = []
    for element_id in ids:
        match = re.fullmatch(r"journey-stage-(\d+)", element_id)
        if match:
            numbers.append(int(match.group(1)))
    return numbers


def audit_journey_dynamic_structure(
    html: HtmlSnapshot,
    canvas_data: JsonDict | None = None,
    source_path: Path | None = None,
) -> list[Finding]:
    """检查 Journey 动态阶段锚点、canvas-data.stages 与确认包第 6 节顺序。"""
    findings: list[Finding] = []
    counts = Counter(html.ids)
    stage_numbers = journey_stage_numbers(html.ids)
    unique_numbers = sorted(set(stage_numbers))

    if len(stage_numbers) != len(unique_numbers):
        findings.append(Finding("JOURNEY_STAGE", "journey-stage-{n} contains duplicate stage ids"))
    if len(unique_numbers) < 3:
        findings.append(Finding("JOURNEY_STAGE", "Journey requires at least 3 stages"))
    expected_numbers = list(range(1, len(unique_numbers) + 1))
    if unique_numbers and unique_numbers != expected_numbers:
        findings.append(
            Finding("JOURNEY_STAGE", f"stage numbers must be continuous from 1: {unique_numbers}")
        )

    for number in unique_numbers:
        expected_child_ids = [f"journey-stage-{number}-{field}" for field in JOURNEY_STAGE_FIELDS]
        missing = [child for child in expected_child_ids if counts[child] == 0]
        if missing:
            findings.append(
                Finding("JOURNEY_STAGE", f"stage {number} missing child anchors: {', '.join(missing)}")
            )
            continue
        duplicates = [child for child in expected_child_ids if counts[child] > 1]
        if duplicates:
            findings.append(
                Finding("JOURNEY_STAGE", f"stage {number} duplicate child anchors: {', '.join(duplicates)}")
            )
        actual = [item for item in html.ids if item in set(expected_child_ids)]
        if actual != expected_child_ids:
            findings.append(
                Finding(
                    "JOURNEY_STAGE_ORDER",
                    f"stage {number} child order mismatch; expected {expected_child_ids}, actual {actual}",
                )
            )

    if canvas_data is not None:
        stages = canvas_data.get("stages")
        if not isinstance(stages, list):
            findings.append(Finding("JOURNEY_DATA", "canvas-data.stages must be an array"))
        else:
            if len(stages) != len(unique_numbers):
                findings.append(
                    Finding(
                        "JOURNEY_DATA",
                        f"canvas-data.stages length {len(stages)} != DOM stages {len(unique_numbers)}",
                    )
                )
            for index, stage in enumerate(stages, start=1):
                if not isinstance(stage, dict):
                    findings.append(Finding("JOURNEY_DATA", f"stages[{index}] must be an object"))
                    continue
                missing_fields = [
                    field for field in JOURNEY_STAGE_DATA_FIELDS if field not in stage
                ]
                if missing_fields:
                    findings.append(
                        Finding(
                            "JOURNEY_DATA",
                            f"stages[{index}] missing fields: {', '.join(missing_fields)}",
                        )
                    )
                if stage.get("stage_index") != index:
                    findings.append(
                        Finding(
                            "JOURNEY_DATA",
                            f"stages[{index}].stage_index must be {index}, got {stage.get('stage_index')!r}",
                        )
                    )

        quality = canvas_data.get("quality")
        if not isinstance(quality, dict):
            findings.append(Finding("JOURNEY_DATA", "canvas-data.quality must be an object"))
        else:
            missing_quality = [key for key in JOURNEY_QUALITY_KEYS if key not in quality]
            if missing_quality:
                findings.append(
                    Finding("JOURNEY_DATA", f"canvas-data.quality missing: {', '.join(missing_quality)}")
                )

    if source_path is not None and canvas_data is not None:
        source_rows = extract_markdown_table_rows(source_path, "6. 阶段地图")
        if source_rows:
            source_stage_names = [row[1].strip() for row in source_rows if len(row) >= 2]
            stages = canvas_data.get("stages")
            if isinstance(stages, list):
                data_stage_names = [
                    str(stage.get("stage_name", "")).strip()
                    for stage in stages
                    if isinstance(stage, dict)
                ]
                if source_stage_names != data_stage_names:
                    findings.append(
                        Finding(
                            "JOURNEY_SOURCE_ORDER",
                            f"stage order differs from source section 6: source={source_stage_names}, canvas-data={data_stage_names}",
                        )
                    )
        else:
            findings.append(Finding("JOURNEY_SOURCE_ORDER", "source section 6. 阶段地图 has no table rows"))

    return findings


def audit_journey_template_gate(
    html: HtmlSnapshot,
    source: str,
    html_path: Path,
    template: HtmlSnapshot,
    profile: dict[str, list[str]],
) -> list[Finding]:
    """Journey Template Gate：一级模块、动态阶段、治理插槽、离线和隐藏检查。"""
    findings: list[Finding] = []
    counts = Counter(html.ids)
    main_order = profile.get("main_order") or list(JOURNEY_TPL_MAIN_IDS)

    page_type = html.body_attrs.get("data-page-type")
    tpl_page_type = template.body_attrs.get("data-page-type")
    if page_type != tpl_page_type:
        findings.append(
            Finding(
                "JOURNEY-TPL-GATE-01",
                f"data-page-type={page_type!r} 与模板 {tpl_page_type!r} 不一致",
            )
        )

    missing = [i for i in main_order if counts[i] == 0]
    if missing:
        findings.append(Finding("JOURNEY-TPL-GATE-02", f"一级模块缺失: {', '.join(missing)}"))
    duplicates = [i for i in main_order if counts[i] > 1]
    if duplicates:
        findings.append(Finding("JOURNEY-TPL-GATE-02", f"一级模块重复: {', '.join(duplicates)}"))

    actual = [i for i in html.ids if i in set(main_order)]
    if actual != main_order:
        findings.append(
            Finding(
                "JOURNEY-TPL-GATE-03",
                f"一级模块顺序偏离 profile: 期望 {main_order}, 实际 {actual}",
            )
        )

    stable_anchors = set(profile.get("stable_anchors") or [])
    stable_anchors.update(JOURNEY_ANCHORS)
    anchor_missing = [a for a in sorted(stable_anchors) if counts[a] == 0]
    if anchor_missing:
        findings.append(
            Finding("JOURNEY-TPL-GATE-04", f"稳定锚点缺失: {', '.join(anchor_missing)}")
        )
    findings.extend(
        Finding(f"JOURNEY-TPL-GATE-04", finding.message)
        for finding in audit_journey_dynamic_structure(html)
    )

    govern_missing = [i for i in HMW_TPL_GOVERN_IDS if counts[i] == 0]
    if govern_missing:
        findings.append(
            Finding("JOURNEY-TPL-GATE-05", f"quality-panel 缺插槽: {', '.join(govern_missing)}")
        )

    if "@media print" not in source.lower():
        findings.append(Finding("JOURNEY-TPL-GATE-06", "缺少 @media print 钩子"))
    if html.external_urls:
        findings.append(
            Finding("JOURNEY-TPL-GATE-06", f"存在外部网络依赖: {', '.join(html.external_urls)}")
        )
    stylesheet_hrefs = re.findall(
        r'<link\b[^>]*\brel=["\']stylesheet["\'][^>]*\bhref=["\']([^"\']+)["\']',
        source,
        re.IGNORECASE,
    )
    theme_inlined = bool(
        re.search(r"\[data-theme[^]]*\]", source)
        and re.search(r"--brand\s*:", source)
        and re.search(r"<style", source, re.IGNORECASE)
    )
    if not stylesheet_hrefs and not theme_inlined:
        findings.append(Finding("JOURNEY-TPL-GATE-06", "缺少共享主题（既无 <link> 外链也无内联 <style> 主题）"))
    for href in stylesheet_hrefs:
        if href.startswith(("http://", "https://", "//")):
            continue
        stylesheet_path = (html_path.parent / href).resolve()
        if not stylesheet_path.is_file():
            findings.append(Finding("JOURNEY-TPL-GATE-06", f"本地主题资源不存在: {href}"))
            continue
        # 正式产物禁止依赖本地相对路径外链 CSS（方案 A 收口）
        findings.append(
            Finding("JOURNEY-TPL-GATE-06", f"正式产物依赖本地相对路径外链 CSS: {href}（应内联）")
        )

    if "overflow-x:auto" not in source.replace(" ", ""):
        findings.append(Finding("JOURNEY-TPL-GATE-06", "缺少横向滚动钩子 overflow-x:auto"))

    for section_id in ("journey-map", "journey-quality", "quality-panel"):
        attrs = html.attrs_by_id.get(section_id, {})
        if counts[section_id] and (
            element_is_hidden(source, attrs) or stylesheet_hides_element(source, section_id)
        ):
            findings.append(
                Finding(
                    "JOURNEY-TPL-GATE-06",
                    f"{section_id} 被隐藏（hidden/display:none/visibility:hidden/class=hidden 任一）",
                )
            )

    return findings


def extract_markdown_table_rows(path: Path, heading: str) -> list[list[str]]:
    """从 Markdown 文件指定标题下提取表格数据行。"""
    markdown = path.read_text(encoding="utf-8")
    match = re.search(
        rf"^#{{1,6}}\s*{re.escape(heading)}\s*$\n?(.*?)(?=^#{{1,6}}\s|\Z)",
        markdown,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []
    rows: list[list[str]] = []
    for line in match.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def extract_hmw_table_rows(markdown: str, heading: str) -> list[list[str]]:
    """从 HMW 确认包提取指定三级标题下的 Markdown 表格数据行。"""
    match = re.search(
        rf"^#{{1,6}}\s*{re.escape(heading)}\s*$\n?(.*?)(?=^#{{1,6}}\s|\Z)",
        markdown,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []
    rows: list[list[str]] = []
    for line in match.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def audit_persona_content_mapping(html: HtmlSnapshot, source_path: Path) -> list[Finding]:
    """确认正式 Persona 画布的可见字段来自同版本确认包。"""
    try:
        package = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [Finding("CONTENT_MAPPING", f"cannot read Persona package: {exc}")]

    findings: list[Finding] = []
    field_ids = {
        "name": "persona-name",
        "gender": "persona-gender",
        "age": "persona-age",
        "location": "persona-location",
        "education": "persona-education",
        "job_title": "persona-job-title",
        "industry": "persona-industry",
        "family_status": "persona-family-status",
        "income": "persona-income",
        "description": "persona-description",
        "goals_needs": "persona-goals-needs",
        "behaviors": "persona-behaviors",
        "pain_points": "persona-pain-points",
        "motivation": "persona-motivation",
        "decision_factors": "persona-decision-factors",
    }
    for row in extract_hmw_table_rows(package, "6. 9 基本信息 + 6 宫格"):
        if len(row) < 2:
            continue
        field = next(
            (key for key in field_ids if row[0] == key or row[0].startswith(f"{key}（")),
            None,
        )
        if field and row[1] not in html.text_by_id.get(field_ids[field], ""):
            findings.append(
                Finding("CONTENT_MAPPING", f"{field_ids[field]} 未展示确认包字段内容")
            )

    quality_ids = {
        "evidence_based": "persona-quality-evidence",
        "concrete": "persona-quality-concrete",
        "pain_in_voice": "persona-quality-voice",
        "representative": "persona-quality-representative",
    }
    for row in extract_hmw_table_rows(package, "6a. 质量鉴别"):
        if len(row) < 2:
            continue
        field = next(
            (key for key in quality_ids if row[0] == key or row[0].startswith(f"{key}（")),
            None,
        )
        if field and row[1] not in html.text_by_id.get(quality_ids[field], ""):
            findings.append(
                Finding("CONTENT_MAPPING", f"{quality_ids[field]} 未展示确认包质量判定")
            )
    return findings


def audit_hmw_content_mapping(html: HtmlSnapshot, source_path: Path) -> list[Finding]:
    """确认正式 HMW 成品的可见业务事实来自同版本确认包。"""
    try:
        package = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [Finding("CONTENT_MAPPING", f"cannot read HMW package: {exc}")]

    findings: list[Finding] = []
    statement_rows = extract_hmw_table_rows(package, "6. HMW 陈述（4 字段）")
    statement_ids = {
        "situation": "hmw-situation",
        "question": "hmw-question",
        "for": "hmw-for",
        "so_that": "hmw-sothat",
    }
    for row in statement_rows:
        if len(row) < 2:
            continue
        field = next((key for key in statement_ids if row[0] == key or row[0].startswith(f"{key}（")), None)
        if field and row[1] not in html.text_by_id.get(statement_ids[field], ""):
            findings.append(
                Finding("CONTENT_MAPPING", f"{statement_ids[field]} 未展示确认包字段内容")
            )

    quality_rows = extract_hmw_table_rows(package, "6a. 质量鉴别")
    quality_ids = {
        "preset_solution": "hmw-quality-preset",
        "vague": "hmw-quality-vague",
        "user_moment": "hmw-quality-moment",
        "tension": "hmw-quality-tension",
    }
    for row in quality_rows:
        if len(row) < 2:
            continue
        dimension = next((key for key in quality_ids if row[0] == key or row[0].startswith(f"{key}（")), None)
        if dimension and row[1] not in html.text_by_id.get(quality_ids[dimension], ""):
            findings.append(
                Finding("CONTENT_MAPPING", f"{quality_ids[dimension]} 未展示确认包质量判定")
            )

    for index, row in enumerate(extract_hmw_table_rows(package, "6b. 想法种子")[:8], start=1):
        if len(row) >= 2 and row[1] not in html.text_by_id.get(f"hmw-idea-{index}", ""):
            findings.append(Finding("CONTENT_MAPPING", f"hmw-idea-{index} 未展示确认包想法内容"))

    for row in extract_hmw_table_rows(package, "6c. 想法 ↔ HMW 对应"):
        if row and row[0] not in html.text_by_id.get("hmw-coherence-map", ""):
            findings.append(Finding("CONTENT_MAPPING", "hmw-coherence-map 未展示确认包对齐关系"))
            break
    return findings


def select_instance_state(
    state: JsonDict,
    canvas_type: str,
    instance_slug: str | None,
) -> JsonDict | None:
    """Select a non-MVL canvas instance from state.{state_key}.{slug}."""
    state_key = INSTANCE_STATE_KEYS[canvas_type]
    if instance_slug is None:
        raise ValueError(f"--instance is required when auditing --type {canvas_type} with --state")
    instances = state.get(state_key)
    if not isinstance(instances, dict):
        return None
    instance = instances.get(instance_slug)
    if not isinstance(instance, dict):
        return None
    if instance.get("slug") != instance_slug:
        raise ValueError(f"state.{state_key}.{instance_slug}.slug must match map key")
    return cast(JsonDict, instance)


def audit_index_page(
    html: HtmlSnapshot,
    source: str,
    state_path: Path | None,
    canvas_type: str,
) -> list[Finding]:
    """Audit a non-MVL canvas instance index page."""
    findings: list[Finding] = []
    if canvas_type not in INSTANCE_STATE_KEYS:
        findings.append(Finding("INDEX", "--index is only supported for gc/hmw/persona/journey"))
        return findings

    expected_page_type = f"{canvas_type}-index" if canvas_type != "gc" else "golden-circle-index"
    page_type = html.body_attrs.get("data-page-type")
    if page_type != expected_page_type:
        findings.append(
            Finding("PAGE_TYPE", f"index page data-page-type must be {expected_page_type!r}, got {page_type!r}")
        )

    if "canvas-data" not in html.ids:
        findings.append(Finding("CANVAS_DATA", "index page requires canvas-data"))

    canvas_data: JsonDict | None = None
    if html.canvas_data_text:
        try:
            loaded = json.loads(html.canvas_data_text)
            if isinstance(loaded, dict):
                canvas_data = cast(JsonDict, loaded)
            else:
                findings.append(Finding("CANVAS_DATA", "canvas-data must be a JSON object"))
        except json.JSONDecodeError as exc:
            findings.append(Finding("CANVAS_DATA", str(exc)))

    if state_path is None:
        return findings

    try:
        state = load_json(state_path)
        state_key = INSTANCE_STATE_KEYS[canvas_type]
        instances = state.get(state_key)
        if not isinstance(instances, dict):
            raise ValueError(f"state.json has no {state_key} instance map")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        findings.append(Finding("STATE_READ", str(exc)))
        return findings

    slugs = sorted(instances)
    if len(slugs) != len(set(slugs)):
        findings.append(Finding("INDEX", "duplicate instance slugs"))

    data_instances = None
    if canvas_data is not None:
        data_instances = canvas_data.get("instances")
        if not isinstance(data_instances, list):
            findings.append(Finding("INDEX_DATA", "canvas-data.instances must be an array"))
        else:
            data_slugs = sorted(item.get("slug") for item in data_instances if isinstance(item, dict))
            if data_slugs != slugs:
                findings.append(Finding("INDEX_DATA", f"canvas-data slugs {data_slugs!r} != state slugs {slugs!r}"))

    for slug in slugs:
        if slug not in html.text:
            findings.append(Finding("INDEX", f"missing slug text: {slug}"))
        output_prefix = "gc" if canvas_type == "gc" else canvas_type
        expected_href = f"{output_prefix}-canvas-{slug}.html"
        if expected_href not in source:
            findings.append(Finding("INDEX_LINK", f"missing link href: {expected_href}"))

    return findings


def audit(
    html_path: Path,
    contract_path: Path = DEFAULT_CONTRACT,
    state_path: Path | None = None,
    source_path: Path | None = None,
    canvas_type: str = "mvl",
    instance_slug: str | None = None,
    index: bool = False,
    page_type_arg: str | None = None,
    generation_path_arg: str | None = None,
) -> list[Finding]:
    """对照 render-contract / state.json / 确认包，审计单个 Canvas HTML 文件。"""
    is_gc = canvas_type == "gc"
    is_hmw = canvas_type == "hmw"
    is_journey = canvas_type == "journey"
    is_persona = canvas_type == "persona"
    # MAAU transcript-direct：mvl + global + 显式 --instance 即判定为一次性综合实例页
    is_maau = canvas_type == "mvl" and instance_slug is not None and not index
    findings: list[Finding] = []
    orders: dict[str, list[str]] = {}
    gc_anchors: list[str] = []
    hmw_anchors: list[str] = []
    persona_anchors: list[str] = []
    if is_gc:
        try:
            gc_anchors = load_gc_anchor_orders(contract_path)
        except (OSError, ValueError) as exc:
            return [Finding("CONTRACT", str(exc))]
    elif is_hmw:
        try:
            hmw_anchors = load_gc_anchor_orders(contract_path)
        except (OSError, ValueError) as exc:
            return [Finding("CONTRACT", str(exc))]
    elif is_journey:
        # Journey 使用动态阶段锚点，固定锚点由常量与动态检查共同覆盖。
        hmw_anchors = list(JOURNEY_ANCHORS)
    elif is_persona:
        try:
            persona_anchors = load_gc_anchor_orders(contract_path)
        except (OSError, ValueError) as exc:
            return [Finding("CONTRACT", str(exc))]
    else:
        try:
            orders = load_contract_anchor_orders(contract_path)
        except (OSError, ValueError) as exc:
            return [Finding("CONTRACT", str(exc))]
    try:
        source, html = parse_html(html_path)
    except (OSError, UnicodeError) as exc:
        return [Finding("HTML_READ", str(exc))]

    if index:
        return audit_index_page(html, source, state_path, canvas_type)

    counts = Counter(html.ids)
    duplicates = sorted(element_id for element_id, count in counts.items() if count > 1)
    if duplicates:
        findings.append(Finding("DUPLICATE_ID", f"duplicate ids: {', '.join(duplicates)}"))

    page_type = html.body_attrs.get("data-page-type")
    module = html.body_attrs.get("data-module")
    body_instance = html.body_attrs.get("data-instance")
    body_version = normalize_version(html.body_attrs.get("data-version"))
    if is_gc:
        valid_types = {"golden-circle"}
    elif is_hmw:
        valid_types = {"hmw"}
    elif is_journey:
        valid_types = {"journey"}
    elif is_persona:
        valid_types = {"persona"}
    else:
        valid_types = {"module-detail", "global"}
    if page_type not in valid_types:
        findings.append(Finding("PAGE_TYPE", f"unsupported data-page-type: {page_type!r}"))
    if page_type_arg is not None and page_type != page_type_arg:
        findings.append(
            Finding("PAGE_TYPE", f"--page-type {page_type_arg!r} does not match HTML data-page-type {page_type!r}")
        )
    if is_maau and generation_path_arg not in (None, "transcript-direct"):
        findings.append(
            Finding(
                "MAAU_GENERATION",
                f"--generation-path must be 'transcript-direct' for MAAU, got {generation_path_arg!r}",
            )
        )
    if not body_version:
        findings.append(Finding("VERSION", "body data-version must be an integer or vN"))
    if canvas_type in INSTANCE_STATE_KEYS and instance_slug is not None:
        if body_instance != instance_slug:
            findings.append(
                Finding("INSTANCE", f"body data-instance={body_instance!r} must match --instance {instance_slug!r}")
            )

    required: list[str] = list(SHARED_IDS)
    if is_gc or is_hmw or is_journey or is_persona:
        if is_gc:
            required.extend(GC_MAIN_IDS)
        elif is_hmw:
            required.extend(HMW_MAIN_IDS)
        elif is_journey:
            required.extend(JOURNEY_MAIN_IDS)
        else:
            required.extend(PERSONA_MAIN_IDS)
        # 单画布契约无 alignment-section（MVL 专属），审计不要求
        if "alignment-section" in required:
            required.remove("alignment-section")
    elif page_type == "module-detail":
        required.extend(MODULE_MAIN_IDS)
    elif page_type == "global":
        required.extend(GLOBAL_MAIN_IDS)
    missing = [element_id for element_id in required if counts[element_id] == 0]
    if missing:
        findings.append(Finding("MISSING_ID", f"missing required ids: {', '.join(missing)}"))

    expected_anchors: list[str] = []
    if is_gc:
        expected_anchors = list(gc_anchors)
        anchor_missing = [anchor for anchor in expected_anchors if counts[anchor] == 0]
        if anchor_missing:
            findings.append(
                Finding("MISSING_ANCHOR", f"GC missing anchors: {', '.join(anchor_missing)}")
            )
    elif is_hmw:
        expected_anchors = list(hmw_anchors)
        anchor_missing = [anchor for anchor in expected_anchors if counts[anchor] == 0]
        if anchor_missing:
            findings.append(
                Finding("MISSING_ANCHOR", f"HMW missing anchors: {', '.join(anchor_missing)}")
            )
    elif is_journey:
        expected_anchors = list(JOURNEY_ANCHORS)
        anchor_missing = [anchor for anchor in expected_anchors if counts[anchor] == 0]
        if anchor_missing:
            findings.append(
                Finding("MISSING_ANCHOR", f"Journey missing anchors: {', '.join(anchor_missing)}")
            )
    elif is_persona:
        expected_anchors = list(persona_anchors)
        anchor_missing = [anchor for anchor in expected_anchors if counts[anchor] == 0]
        if anchor_missing:
            findings.append(
                Finding("MISSING_ANCHOR", f"Persona missing anchors: {', '.join(anchor_missing)}")
            )
    elif page_type == "module-detail":
        if module not in orders:
            findings.append(Finding("MODULE", f"unsupported data-module: {module!r}"))
        else:
            expected_anchors = orders[module]
            anchor_missing = [anchor for anchor in expected_anchors if counts[anchor] == 0]
            if anchor_missing:
                findings.append(
                    Finding("MISSING_ANCHOR", f"{module} missing anchors: {', '.join(anchor_missing)}")
                )
            if not anchor_missing and not expected_in_order(html.output_ids, expected_anchors):
                actual = [item for item in html.output_ids if item in set(expected_anchors)]
                findings.append(
                    Finding(
                        "ANCHOR_ORDER",
                        f"{module} anchor order mismatch; expected {expected_anchors}, actual {actual}",
                    )
                )

    canvas_data: JsonDict | None = None
    if not html.canvas_data_text:
        findings.append(Finding("CANVAS_DATA", "canvas-data is empty"))
    else:
        try:
            loaded: object = json.loads(html.canvas_data_text)
            if not isinstance(loaded, dict):
                raise ValueError("canvas-data must be a JSON object")
            canvas_data = cast(JsonDict, loaded)
        except (json.JSONDecodeError, ValueError) as exc:
            findings.append(Finding("CANVAS_DATA", str(exc)))

    if canvas_data is not None:
        data_version = normalize_version(canvas_data.get("version"))
        if body_version and data_version != body_version:
            findings.append(
                Finding("VERSION_MISMATCH", f"body={body_version!r}, canvas-data={data_version!r}")
            )
        if not is_gc and page_type == "module-detail" and canvas_data.get("module") != module:
            findings.append(
                Finding("MODULE_MISMATCH", f"body={module!r}, canvas-data={canvas_data.get('module')!r}")
            )
        if is_gc and canvas_data.get("canvas_type") != "golden-circle":
            findings.append(
                Finding("CANVAS_TYPE", f"canvas-data.canvas_type must be 'golden-circle', got {canvas_data.get('canvas_type')!r}")
            )
        if is_hmw and canvas_data.get("canvas_type") != "hmw":
            findings.append(
                Finding("CANVAS_TYPE", f"canvas-data.canvas_type must be 'hmw', got {canvas_data.get('canvas_type')!r}")
            )
        if is_journey and canvas_data.get("canvas_type") != "journey":
            findings.append(
                Finding("CANVAS_TYPE", f"canvas-data.canvas_type must be 'journey', got {canvas_data.get('canvas_type')!r}")
            )
        if is_persona and canvas_data.get("canvas_type") != "persona":
            findings.append(
                Finding("CANVAS_TYPE", f"canvas-data.canvas_type must be 'persona', got {canvas_data.get('canvas_type')!r}")
            )
        if canvas_type in INSTANCE_STATE_KEYS and instance_slug is not None:
            data_instance = canvas_data.get("instance") or canvas_data.get("instance_slug")
            if data_instance != instance_slug:
                findings.append(
                    Finding("INSTANCE", f"canvas-data instance={data_instance!r} must match --instance {instance_slug!r}")
                )
        sections = canvas_data.get("sections")
        if expected_anchors and isinstance(sections, dict):
            section_missing = [anchor for anchor in expected_anchors if anchor not in sections]
            if section_missing:
                findings.append(
                    Finding("SECTION_DATA", f"canvas-data.sections missing: {', '.join(section_missing)}")
                )
        elif expected_anchors:
            findings.append(Finding("SECTION_DATA", "canvas-data.sections must be an object"))
        if is_journey:
            findings.extend(audit_journey_dynamic_structure(html, canvas_data, source_path))
        if is_maau:
            if page_type != "global":
                findings.append(
                    Finding("PAGE_TYPE", f"MAAU transcript-direct requires data-page-type='global', got {page_type!r}")
                )
            if state_path is None:
                findings.append(
                    Finding("MAAU_STATE", "MAAU transcript-direct 正式验收必须传 --state 读取授权")
                )
            findings.extend(
                audit_maau_transcript_direct(
                    source, canvas_data, body_instance, source_path, instance_slug,
                )
            )

    lowered = source.lower()
    if "iframe" in html.tags:
        findings.append(Finding("OFFLINE", "iframe is forbidden"))
    if re.search(r"\bfetch\s*\(", source, re.IGNORECASE):
        findings.append(Finding("OFFLINE", "fetch() is forbidden"))
    if re.search(r"@import\s+", source, re.IGNORECASE):
        findings.append(Finding("OFFLINE", "CSS @import is forbidden"))
    if re.search(r"url\(\s*['\"]?(?:https?:)?//", source, re.IGNORECASE):
        findings.append(Finding("OFFLINE", "external CSS URL is forbidden"))
    if html.external_urls:
        findings.append(Finding("OFFLINE", f"external URLs: {', '.join(html.external_urls)}"))
    # 方案 A（2026-08-09）：正式产物禁止依赖本地相对路径外链 CSS（单文件自包含、可独立传播）
    local_css_hrefs = re.findall(
        r'<link\b[^>]*\brel=["\']stylesheet["\'][^>]*\bhref=["\']([^"\']+)["\']',
        source,
        re.IGNORECASE,
    )
    for href in local_css_hrefs:
        if not href.startswith(("http://", "https://", "//")):
            findings.append(Finding("OFFLINE", f"本地相对路径外链 CSS 禁止: {href}（应内联）"))
    if "@media print" not in lowered:
        findings.append(Finding("PRINT", "missing @media print rule"))

    # Caveat checks (for MVL module-detail / GC / HMW single-canvas pages)
    if is_gc:
        caveat_page_types = {"golden-circle"}
    elif is_hmw:
        caveat_page_types = {"hmw"}
    elif is_journey:
        caveat_page_types = {"journey"}
    elif is_persona:
        caveat_page_types = {"persona"}
    else:
        caveat_page_types = {"module-detail"}
    if canvas_data is not None and page_type in caveat_page_types:
        auth = canvas_data.get("auth")
        if not isinstance(auth, dict):
            findings.append(Finding("AUTH", "canvas-data.auth must be an object"))
            auth = None
        if auth is not None:
            mode = auth.get("confirmation_mode")
            caveat_attrs = html.attrs_by_id.get("quality-caveat", {})
            if mode == "override":
                if counts["quality-caveat"] == 0:
                    findings.append(Finding("CAVEAT", "override page requires quality-caveat"))
                elif element_is_hidden(source, caveat_attrs) or stylesheet_hides_element(source, "quality-caveat"):
                    findings.append(Finding("CAVEAT", "override quality-caveat must be visible"))
                if not auth.get("override_audit"):
                    findings.append(Finding("CAVEAT", "override page requires override_audit"))
            elif mode == "gate_pass" and counts["quality-caveat"] and "hidden" not in caveat_attrs:
                findings.append(Finding("CAVEAT", "gate_pass quality-caveat must be hidden"))
    if is_journey:
        for section_id in ("journey-map", "journey-quality", "quality-panel"):
            attrs = html.attrs_by_id.get(section_id, {})
            if counts[section_id] and (
                element_is_hidden(source, attrs) or stylesheet_hides_element(source, section_id)
            ):
                findings.append(
                    Finding(
                        "HIDDEN_SECTION",
                        f"{section_id} must be visible",
                    )
                )

    if html.body_attrs.get("data-mode") == "draft":
        if "草稿" not in html.text or "未确认" not in html.text:
            findings.append(Finding("DRAFT", "draft page must visibly contain 草稿 and 未确认"))

    if source_path is not None:
        try:
            if is_gc:
                source_module, source_version = gc_source_identity(source_path)
            elif is_hmw:
                source_module, source_version = hmw_source_identity(source_path)
            elif is_journey:
                source_module, source_version = journey_source_identity(source_path)
            elif is_persona:
                source_module, source_version = persona_source_identity(source_path)
            elif is_maau:
                source_module, source_version = maau_source_identity(source_path)
            else:
                source_module, source_version = source_identity(source_path)
        except OSError as exc:
            findings.append(Finding("SOURCE_READ", str(exc)))
        else:
            if source_module is None or source_version is None:
                findings.append(Finding("SOURCE", "cannot read module/version from confirmation package"))
            else:
                if (
                    not is_gc
                    and not is_hmw
                    and not is_journey
                    and not is_maau
                    and module
                    and source_module != module
                ):
                    findings.append(
                        Finding("SOURCE_MODULE", f"HTML={module!r}, source={source_module!r}")
                    )
                if is_maau and instance_slug is not None and source_module != instance_slug:
                    findings.append(
                        Finding(
                            "MAAU_SOURCE_SLUG",
                            f"source slug={source_module!r} must match --instance {instance_slug!r}",
                        )
                    )
                if body_version and source_version != body_version:
                    findings.append(
                        Finding("SOURCE_VERSION", f"HTML={body_version!r}, source={source_version!r}")
                    )

    if state_path is not None:
        try:
            state = load_json(state_path)
            if is_gc:
                state_module = select_instance_state(state, "gc", instance_slug)
                if not isinstance(state_module, dict):
                    raise ValueError("state.json has no golden_circle instance record")
            elif is_hmw:
                state_module = select_instance_state(state, "hmw", instance_slug)
                if not isinstance(state_module, dict):
                    raise ValueError("state.json has no hmw instance record")
            elif is_journey:
                state_module = select_instance_state(state, "journey", instance_slug)
                if not isinstance(state_module, dict):
                    raise ValueError("state.json has no journey instance record")
            elif is_persona:
                state_module = select_instance_state(state, "persona", instance_slug)
                if not isinstance(state_module, dict):
                    raise ValueError("state.json has no persona instance record")
            elif is_maau:
                state_module = select_maau_instance_state(state, instance_slug)
                if not isinstance(state_module, dict):
                    raise ValueError("state.json has no maau instance record")
            else:
                modules = state.get("modules", {})
                state_module = (
                    modules.get(module) if isinstance(modules, dict) and module is not None else None
                )
                if not isinstance(state_module, dict):
                    raise ValueError(f"state.json has no module record for {module}")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            findings.append(Finding("STATE_READ", str(exc)))
        else:
            state_version = normalize_version(state_module.get("version"))
            if body_version and state_version != body_version:
                findings.append(
                    Finding("STATE_VERSION", f"HTML={body_version!r}, state={state_version!r}")
                )
            if is_maau and canvas_data is not None:
                state_generation = state_module.get("generation_path")
                data_generation = canvas_data.get("generation_path")
                if state_generation != "transcript-direct":
                    findings.append(
                        Finding(
                            "MAAU_STATE_GENERATION",
                            f"state.maau.{instance_slug}.generation_path must be 'transcript-direct', got {state_generation!r}",
                        )
                    )
                if data_generation != state_generation:
                    findings.append(
                        Finding(
                            "MAAU_GENERATION",
                            f"canvas-data generation_path={data_generation!r} != state {state_generation!r}",
                        )
                    )
            auth = canvas_data.get("auth") if canvas_data else None
            if isinstance(auth, dict):
                for field in AUTH_FIELDS:
                    if auth.get(field) != state_module.get(field):
                        findings.append(
                            Finding(
                                "AUTH_MISMATCH",
                                f"{field}: canvas-data={auth.get(field)!r}, state={state_module.get(field)!r}",
                        )
                    )
                if is_hmw and source_path is not None:
                    findings.extend(audit_hmw_content_mapping(html, source_path))
                if is_persona and source_path is not None:
                    findings.extend(audit_persona_content_mapping(html, source_path))

    return findings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析命令行参数，返回 html/contract/state/source/type。"""
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument("html", type=Path, help="Canvas HTML file to audit")
    _ = parser.add_argument(
        "--contract", type=Path, help="render-contract.md path (auto-selects by --type if omitted)"
    )
    _ = parser.add_argument("--state", type=Path, help="project state.json for auth/version checks")
    _ = parser.add_argument("--source", type=Path, help="confirmation package (Mx-vN.md or GC-vN.md)")
    _ = parser.add_argument(
        "--template", type=Path,
        help="HMW/Persona/Journey 示例模板路径（Template Gate 比对基准；正式交付必须传入）",
    )
    _ = parser.add_argument(
        "--instance",
        dest="instance_slug",
        help="non-MVL canvas instance slug; required with --state for gc/hmw/persona/journey",
    )
    _ = parser.add_argument(
        "--index",
        action="store_true",
        help="audit a non-MVL canvas index page instead of a single instance page",
    )
    _ = parser.add_argument(
        "--type",
        dest="canvas_type",
        choices=("mvl", "gc", "hmw", "persona", "journey"),
        default="mvl",
        help="canvas type: mvl (default), gc (golden circle), hmw, persona or journey",
    )
    _ = parser.add_argument(
        "--page-type",
        dest="page_type_arg",
        choices=("global", "module-detail"),
        default=None,
        help="mvl page type hint (MAAU transcript-direct 实例页必须传 global)",
    )
    _ = parser.add_argument(
        "--generation-path",
        dest="generation_path_arg",
        choices=("m1-m6", "transcript-direct"),
        default=None,
        help="MVL 全局页生成路径（MAAU 一次性综合须传 transcript-direct）",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """脚本入口：执行双 Gate 审计并打印结果，返回进程退出码。

    - 内容/授权 Gate：所有画布类型（版本、事实源、授权、锚点、canvas-data、caveat、离线）。
    - Template Gate：HMW / Persona / Journey 且传入 --template 时运行（结构完整性，不可 override）。
    """
    args = parse_args(argv)
    html_arg = cast(Path, args.html)
    canvas_type = cast(str, args.canvas_type)
    if args.contract is not None:
        contract_arg = cast(Path, args.contract)
    elif canvas_type == "gc":
        contract_arg = GC_CONTRACT
    elif canvas_type == "hmw":
        contract_arg = HMW_CONTRACT
    elif canvas_type == "journey":
        contract_arg = JOURNEY_CONTRACT
    elif canvas_type == "persona":
        contract_arg = PERSONA_CONTRACT
    else:
        contract_arg = DEFAULT_CONTRACT
    state_arg = cast("Path | None", args.state)
    source_arg = cast("Path | None", args.source)
    template_arg = cast("Path | None", args.template)
    instance_slug = cast("str | None", args.instance_slug)
    index = cast(bool, args.index)
    page_type_arg = cast("str | None", args.page_type_arg)
    generation_path_arg = cast("str | None", args.generation_path_arg)

    findings = audit(
        html_arg, contract_arg, state_arg, source_arg, canvas_type, instance_slug,
        index, page_type_arg, generation_path_arg,
    )
    template_findings: list[Finding] = []

    # Template Gate：HMW / Persona / Journey 正式交付（--template 传入）时运行
    if index:
        template_findings = []
    elif canvas_type == "hmw":
        if template_arg is None:
            if source_arg is not None or state_arg is not None:
                template_findings.append(
                    Finding("HMW-TPL-GATE-00", "HMW 正式交付必须传入 --template 示例模板路径")
                )
        else:
            try:
                template_source, template = parse_html(template_arg)
                profile = load_hmw_template_profile(contract_arg)
                if not profile["main_order"]:
                    template_findings.append(
                        Finding("HMW-TPL-GATE-00", "render-contract-hmw.md 模板 profile 无法解析")
                    )
                else:
                    # 模板自审计：模板自身必须先通过结构检查（§6.2 步骤 13）
                    template_findings.extend(
                        audit_template_gate(
                            template, template_source, template_arg, template, profile,
                            gate_prefix="HMW",
                            check_ids=HMW_TPL_MAIN_IDS,
                            check_stable_anchors=HMW_TPL_STABLE_ANCHORS,
                            check_govern_ids=HMW_TPL_GOVERN_IDS,
                            hidden_section_ids=("hmw-quality", "hmw-coherence", "quality-panel"),
                        )
                    )
                    # 成品 Template Gate（复用已解析的 html）
                    html_source, html_snapshot = parse_html(html_arg)
                    template_findings.extend(
                        audit_template_gate(
                            html_snapshot, html_source, html_arg, template, profile,
                            gate_prefix="HMW",
                            check_ids=HMW_TPL_MAIN_IDS,
                            check_stable_anchors=HMW_TPL_STABLE_ANCHORS,
                            check_govern_ids=HMW_TPL_GOVERN_IDS,
                            hidden_section_ids=("hmw-quality", "hmw-coherence", "quality-panel"),
                        )
                    )
            except (OSError, UnicodeError) as exc:
                template_findings.append(Finding("HMW-TPL-GATE-00", f"模板读取失败: {exc}"))
    elif canvas_type == "journey":
        if template_arg is None:
            if source_arg is not None or state_arg is not None:
                template_findings.append(
                    Finding("JOURNEY-TPL-GATE-00", "Journey 正式交付必须传入 --template 示例模板路径")
                )
        else:
            try:
                template_source, template = parse_html(template_arg)
                profile = load_journey_template_profile(contract_arg)
                if not profile["main_order"]:
                    template_findings.append(
                        Finding("JOURNEY-TPL-GATE-00", "render-contract-journey.md 模板 profile 无法解析")
                    )
                else:
                    template_findings.extend(
                        audit_journey_template_gate(template, template_source, template_arg, template, profile)
                    )
                    html_source, html_snapshot = parse_html(html_arg)
                    template_findings.extend(
                        audit_journey_template_gate(html_snapshot, html_source, html_arg, template, profile)
                    )
            except (OSError, UnicodeError) as exc:
                template_findings.append(Finding("JOURNEY-TPL-GATE-00", f"模板读取失败: {exc}"))
    elif canvas_type == "persona":
        if template_arg is None:
            if source_arg is not None or state_arg is not None:
                template_findings.append(
                    Finding("PERSONA-TPL-GATE-00", "Persona 正式交付必须传入 --template 示例模板路径")
                )
        else:
            try:
                template_source, template = parse_html(template_arg)
                profile = load_persona_template_profile(contract_arg)
                if not profile["main_order"]:
                    template_findings.append(
                        Finding("PERSONA-TPL-GATE-00", "render-contract-persona.md 模板 profile 无法解析")
                    )
                else:
                    # 模板自审计
                    template_findings.extend(
                        audit_template_gate(
                            template, template_source, template_arg, template, profile,
                            gate_prefix="PERSONA",
                            check_ids=PERSONA_MAIN_IDS,
                            check_stable_anchors=PERSONA_STABLE_ANCHORS,
                            check_govern_ids=PERSONA_TPL_GOVERN_IDS,
                            hidden_section_ids=("persona-quality", "quality-panel"),
                        )
                    )
                    # 成品 Template Gate
                    html_source, html_snapshot = parse_html(html_arg)
                    template_findings.extend(
                        audit_template_gate(
                            html_snapshot, html_source, html_arg, template, profile,
                            gate_prefix="PERSONA",
                            check_ids=PERSONA_MAIN_IDS,
                            check_stable_anchors=PERSONA_STABLE_ANCHORS,
                            check_govern_ids=PERSONA_TPL_GOVERN_IDS,
                            hidden_section_ids=("persona-quality", "quality-panel"),
                        )
                    )
            except (OSError, UnicodeError) as exc:
                template_findings.append(Finding("PERSONA-TPL-GATE-00", f"模板读取失败: {exc}"))

    content_fail = bool(findings)
    template_fail = bool(template_findings)
    if content_fail or template_fail:
        print(f"FAIL {html_arg}")
        if findings:
            print("  [CONTENT/AUTH GATE]")
            for finding in findings:
                print(f"    - [{finding.code}] {finding.message}")
        if template_findings:
            print("  [TEMPLATE GATE]")
            for finding in template_findings:
                print(f"    - [{finding.code}] {finding.message}")
        return 1
    print(f"PASS {html_arg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
