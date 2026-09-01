from __future__ import annotations

import json
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Union

# JSON 反序列化后的通用值/字典类型（已知联合，避免 Any/Unknown 透传）
JsonValue = Union[
    str, int, float, bool, None, list["JsonValue"], dict[str, "JsonValue"]
]
JsonDict = dict[str, JsonValue]


REPO_ROOT = Path(__file__).resolve().parents[2]
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
V2C_VAC_CONTRACT = (
    REPO_ROOT / "references" / "render-contract-v2c-vac.md"
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
V2C_VAC_MAIN_IDS = (
    "v2c-vac-canvas",
    "v2c-vac-attribution-chain",
    "v2c-vac-attribution-gaps",
    "v2c-vac-quality-check",
    "v2c-vac-inferences",
)
V2C_VAC_ANCHORS = (
    "v2c-vac-headline",
    "v2c-vac-summary",
    "v2c-vac-key-gaps",
    "v2c-vac-next-step",
    "v2c-vac-scenario",
    "v2c-vac-capability",
    "v2c-vac-primary-capability",
    "v2c-vac-secondary-capabilities",
    "v2c-vac-change",
    "v2c-vac-primary-change",
    "v2c-vac-other-changes",
    "v2c-vac-business-impact",
    "v2c-vac-impact-chain",
    "v2c-vac-value",
    "v2c-vac-value-anchor",
    "v2c-vac-measurement",
    "v2c-vac-attribution-gaps",
    "v2c-vac-gap-V2C-AG01",
    "v2c-vac-gap-V2C-AG02",
    "v2c-vac-gap-V2C-AG03",
    "v2c-vac-gap-V2C-AG04",
    "v2c-vac-gap-V2C-AG05",
    "v2c-vac-gap-V2C-AG06",
    "v2c-vac-quality-check",
    "v2c-vac-quality-semantics",
    "v2c-vac-quality-honesty",
    "v2c-vac-quality-verifiability",
    "v2c-vac-quality-next-step",
    "v2c-vac-inferences",
)
V2C_VAC_TPL_GOVERN_IDS = (
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
GLOBAL_MAIN_IDS = ("intent", "user", "agent-team", "workflow", "context", "validation", "workflow-flow")
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
    "v2c-vac": "v2c_vac",
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
