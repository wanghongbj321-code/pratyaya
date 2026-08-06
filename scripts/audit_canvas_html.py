#!/usr/bin/env python3
"""Deterministic static audit for pratyaya Canvas HTML files (MVL + Golden Circle)."""

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
    REPO_ROOT / "skills" / "canvas-render" / "references" / "render-contract.md"
)
GC_CONTRACT = (
    REPO_ROOT / "skills" / "canvas-render" / "references" / "render-contract-gc.md"
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


def gc_source_identity(path: Path) -> tuple[str | None, str | None]:
    """从 GC-vN 确认包首行标题中提取画布类型与版本号。"""
    first_lines = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
    match = re.search(r"^#\s+黄金圈确认包\s+(v\d+)\s*$", first_lines, re.MULTILINE)
    return ("GC", match.group(1)) if match else (None, None)


def audit(
    html_path: Path,
    contract_path: Path = DEFAULT_CONTRACT,
    state_path: Path | None = None,
    source_path: Path | None = None,
    canvas_type: str = "mvl",
) -> list[Finding]:
    """对照 render-contract / state.json / 确认包，审计单个 Canvas HTML 文件。"""
    is_gc = canvas_type == "gc"
    findings: list[Finding] = []
    orders: dict[str, list[str]] = {}
    if not is_gc:
        try:
            orders = load_contract_anchor_orders(contract_path)
        except (OSError, ValueError) as exc:
            return [Finding("CONTRACT", str(exc))]
    try:
        source, html = parse_html(html_path)
    except (OSError, UnicodeError) as exc:
        return [Finding("HTML_READ", str(exc))]

    counts = Counter(html.ids)
    duplicates = sorted(element_id for element_id, count in counts.items() if count > 1)
    if duplicates:
        findings.append(Finding("DUPLICATE_ID", f"duplicate ids: {', '.join(duplicates)}"))

    page_type = html.body_attrs.get("data-page-type")
    module = html.body_attrs.get("data-module")
    body_version = normalize_version(html.body_attrs.get("data-version"))
    valid_types = {"module-detail", "global"} if not is_gc else {"golden-circle"}
    if page_type not in valid_types:
        findings.append(Finding("PAGE_TYPE", f"unsupported data-page-type: {page_type!r}"))
    if not body_version:
        findings.append(Finding("VERSION", "body data-version must be an integer or vN"))

    required: list[str] = list(SHARED_IDS)
    if is_gc:
        required.extend(GC_MAIN_IDS)
    elif page_type == "module-detail":
        required.extend(MODULE_MAIN_IDS)
    elif page_type == "global":
        required.extend(GLOBAL_MAIN_IDS)
    missing = [element_id for element_id in required if counts[element_id] == 0]
    if missing:
        findings.append(Finding("MISSING_ID", f"missing required ids: {', '.join(missing)}"))

    expected_anchors: list[str] = []
    if is_gc:
        expected_anchors = list(GC_ANCHORS)
        anchor_missing = [anchor for anchor in expected_anchors if counts[anchor] == 0]
        if anchor_missing:
            findings.append(
                Finding("MISSING_ANCHOR", f"GC missing anchors: {', '.join(anchor_missing)}")
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
        sections = canvas_data.get("sections")
        if expected_anchors and isinstance(sections, dict):
            section_missing = [anchor for anchor in expected_anchors if anchor not in sections]
            if section_missing:
                findings.append(
                    Finding("SECTION_DATA", f"canvas-data.sections missing: {', '.join(section_missing)}")
                )
        elif expected_anchors:
            findings.append(Finding("SECTION_DATA", "canvas-data.sections must be an object"))

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
    if "@media print" not in lowered:
        findings.append(Finding("PRINT", "missing @media print rule"))

    # Caveat checks (for both MVL module-detail and GC)
    caveat_page_types = {"module-detail"} if not is_gc else {"golden-circle"}
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
                elif "hidden" in caveat_attrs:
                    findings.append(Finding("CAVEAT", "override quality-caveat must be visible"))
                if not auth.get("override_audit"):
                    findings.append(Finding("CAVEAT", "override page requires override_audit"))
            elif mode == "gate_pass" and counts["quality-caveat"] and "hidden" not in caveat_attrs:
                findings.append(Finding("CAVEAT", "gate_pass quality-caveat must be hidden"))

    if html.body_attrs.get("data-mode") == "draft":
        if "草稿" not in html.text or "未确认" not in html.text:
            findings.append(Finding("DRAFT", "draft page must visibly contain 草稿 and 未确认"))

    if source_path is not None:
        try:
            if is_gc:
                source_module, source_version = gc_source_identity(source_path)
            else:
                source_module, source_version = source_identity(source_path)
        except OSError as exc:
            findings.append(Finding("SOURCE_READ", str(exc)))
        else:
            if source_module is None or source_version is None:
                findings.append(Finding("SOURCE", "cannot read module/version from confirmation package"))
            else:
                if not is_gc and module and source_module != module:
                    findings.append(
                        Finding("SOURCE_MODULE", f"HTML={module!r}, source={source_module!r}")
                    )
                if body_version and source_version != body_version:
                    findings.append(
                        Finding("SOURCE_VERSION", f"HTML={body_version!r}, source={source_version!r}")
                    )

    if state_path is not None:
        try:
            state = load_json(state_path)
            if is_gc:
                state_module = state.get("golden_circle")
                if not isinstance(state_module, dict):
                    raise ValueError("state.json has no golden_circle record")
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
        "--type", dest="canvas_type", choices=("mvl", "gc"), default="mvl",
        help="canvas type: mvl (default) or gc (golden circle)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """脚本入口：执行审计并打印结果，返回进程退出码。"""
    args = parse_args(argv)
    html_arg = cast(Path, args.html)
    canvas_type = cast(str, args.canvas_type)
    if args.contract is not None:
        contract_arg = cast(Path, args.contract)
    elif canvas_type == "gc":
        contract_arg = GC_CONTRACT
    else:
        contract_arg = DEFAULT_CONTRACT
    state_arg = cast("Path | None", args.state)
    source_arg = cast("Path | None", args.source)
    findings = audit(html_arg, contract_arg, state_arg, source_arg, canvas_type)
    if findings:
        print(f"FAIL {html_arg}")
        for finding in findings:
            print(f"- [{finding.code}] {finding.message}")
        return 1
    print(f"PASS {html_arg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
