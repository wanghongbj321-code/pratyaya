from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import cast

from .audit_models import (
    AUTH_FIELDS, DEFAULT_CONTRACT, INSTANCE_STATE_KEYS, JsonDict, Finding, HtmlSnapshot, CanvasParser,
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

def v2c_vac_source_identity(path: Path) -> tuple[str | None, str | None]:
    """从 V2C-VAC-{slug}-vN.md 确认包提取 slug 与版本号。"""
    try:
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:30])
    except OSError:
        return (None, None)
    filename_match = re.fullmatch(
        r"V2C-VAC-([a-z0-9]+(?:-[a-z0-9]+)*)-v(\d+)\.md",
        path.name,
    )
    filename_slug = filename_match.group(1) if filename_match else None
    filename_version = f"v{filename_match.group(2)}" if filename_match else None
    slug_match = re.search(
        r"^>\s*(?:instance slug|slug)：\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$",
        head,
        re.MULTILINE,
    )
    version_match = re.search(
        r"^#\s+V2C(?: Value Attribution Canvas)?(?: 源包| 确认包)?\s*(v\d+)\s*$",
        head,
        re.MULTILINE,
    )
    slug = slug_match.group(1) if slug_match else filename_slug
    version = version_match.group(1) if version_match else filename_version
    return (slug, version)

def v2c_vac_source_generation_path(path: Path) -> str | None:
    """从 V2C VAC 确认包头部提取生成路径。"""
    try:
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:30])
    except OSError:
        return None
    match = re.search(
        r"^>\s*生成路径：\s*(pipeline|transcript-direct)\s*$",
        head,
        re.MULTILINE,
    )
    return match.group(1) if match else None

def five_whys_source_identity(path: Path) -> tuple[str | None, str | None]:
    """从 5W-{slug}-v{N}.md 确认包提取 slug 与版本号。

    返回 ``(slug, "vN")``；无法解析时返回 ``(None, None)``。slug 从文件名提取，
    版本号优先取首行标题（`# 5W 根因分析确认包 v{N}`），失败时回退文件名。
    """
    try:
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:30])
    except OSError:
        return (None, None)
    filename_match = re.fullmatch(
        r"5W-([a-z0-9]+(?:-[a-z0-9]+)*)-v(\d+)\.md",
        path.name,
    )
    filename_slug = filename_match.group(1) if filename_match else None
    filename_version = f"v{filename_match.group(2)}" if filename_match else None
    version_match = re.search(
        r"^#\s+5W 根因分析确认包\s*(v\d+)\s*$",
        head,
        re.MULTILINE,
    )
    version = version_match.group(1) if version_match else filename_version
    return (filename_slug, version)

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

def audit_v2c_vac_override(canvas_data: JsonDict) -> list[Finding]:
    """校验 V2C VAC override 审计项：assessment_id 为 V2C-GATE-* 且 category=business_risk。"""
    findings: list[Finding] = []
    auth = canvas_data.get("auth")
    if not isinstance(auth, dict):
        return findings
    if auth.get("confirmation_mode") != "override":
        return findings
    override = auth.get("override_audit")
    if not isinstance(override, dict):
        findings.append(Finding("V2C_OVERRIDE", "override_audit must be an object"))
        return findings
    items = override.get("items")
    if not isinstance(items, list):
        findings.append(Finding("V2C_OVERRIDE", "override_audit.items must be an array"))
        return findings
    for item in items:
        if not isinstance(item, dict):
            findings.append(Finding("V2C_OVERRIDE", "override_audit item must be an object"))
            continue
        assessment_id = str(item.get("assessment_id", ""))
        if not re.fullmatch(r"V2C-GATE-[0-9]+", assessment_id):
            findings.append(
                Finding(
                    "V2C_OVERRIDE",
                    f"assessment_id={assessment_id!r} must match V2C-GATE-[0-9]+",
                )
            )
        if item.get("category") != "business_risk":
            findings.append(
                Finding(
                    "V2C_OVERRIDE",
                    f"assessment_id={assessment_id!r} category must be business_risk, got {item.get('category')!r}",
                )
            )
    return findings

def audit_5w_override(canvas_data: JsonDict) -> list[Finding]:
    """校验 5W override 审计项：assessment_id 为 5W-GATE-* 且 category=business_risk。

    Gate 分类（5W-gate 规范）：information_integrity（5W-GATE-01..04）不可 override；
    business_risk（5W-GATE-05..07）可 override。此处只校验 ID pattern 与 category。
    """
    findings: list[Finding] = []
    auth = canvas_data.get("auth")
    if not isinstance(auth, dict):
        return findings
    if auth.get("confirmation_mode") != "override":
        return findings
    override = auth.get("override_audit")
    if not isinstance(override, dict):
        findings.append(Finding("5W_OVERRIDE", "override_audit must be an object"))
        return findings
    items = override.get("items")
    if not isinstance(items, list):
        findings.append(Finding("5W_OVERRIDE", "override_audit.items must be an array"))
        return findings
    for item in items:
        if not isinstance(item, dict):
            findings.append(Finding("5W_OVERRIDE", "override_audit item must be an object"))
            continue
        assessment_id = str(item.get("assessment_id", ""))
        if not re.fullmatch(r"5W-GATE-[0-9]+", assessment_id):
            findings.append(
                Finding(
                    "5W_OVERRIDE",
                    f"assessment_id={assessment_id!r} must match 5W-GATE-[0-9]+",
                )
            )
        if item.get("category") != "business_risk":
            findings.append(
                Finding(
                    "5W_OVERRIDE",
                    f"assessment_id={assessment_id!r} category must be business_risk, got {item.get('category')!r}",
                )
            )
    return findings

def audit_v2c_vac_identity(
    canvas_data: JsonDict,
    source_path: Path | None,
) -> list[Finding]:
    """校验 V2C VAC canvas-data 的生成路径与源包文件身份。"""
    findings: list[Finding] = []
    generation_path = canvas_data.get("generation_path")
    if generation_path not in ("pipeline", "transcript-direct"):
        findings.append(
            Finding(
                "V2C_GENERATION",
                f"canvas-data.generation_path must be 'pipeline' or 'transcript-direct', got {generation_path!r}",
            )
        )

    source_file = canvas_data.get("source_file")
    if source_path is not None:
        expected_source_file = source_path.name
        source_file_name = Path(str(source_file)).name if source_file else None
        if source_file_name != expected_source_file:
            findings.append(
                Finding(
                    "V2C_SOURCE_FILE",
                    f"canvas-data.source_file={source_file!r} must match --source name {expected_source_file!r}",
                )
            )
        source_generation = v2c_vac_source_generation_path(source_path)
        if source_generation is not None and generation_path != source_generation:
            findings.append(
                Finding(
                    "V2C_GENERATION",
                    f"canvas-data.generation_path={generation_path!r} != source {source_generation!r}",
                )
            )
    elif not source_file:
        findings.append(Finding("V2C_SOURCE_FILE", "canvas-data.source_file is required"))

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

WORKFLOW_FLOW_NODE_TYPES = (
    "start", "end", "gateway", "agent_execution", "human_operation", "human_review",
)
WORKFLOW_FLOW_REQUIRED_TYPES = ("agent_execution", "human_operation", "human_review")
WORKFLOW_FLOW_SOURCE_SECTIONS = ("Agent 执行节点", "人工操作/确认节点", "人审 + Agent 执行节点")


def audit_workflow_flow(
    source: str,
    html: HtmlSnapshot,
    canvas_data: JsonDict,
    source_path: Path | None,
) -> list[Finding]:
    """校验全局页 Workflow BPMN 流程图（#workflow-flow）契约。

    断言（设计方案 §7.1 + v3.1.1 优化）：
    - SVG 必须含 Start Event（data-node-type="start"）与 End Event（data-node-type="end"）；
    - Sequence Flow 禁止曲线命令（C/Q/S/A），只允许正交 M/H/V；
    - canvas-data.workflow.nodes 必须覆盖三类节点（agent_execution / human_operation / human_review）；
    - canvas-data.workflow.nodes 必须有 number 字段且唯一（节点编号徽标）；
    - SVG 中 bpmn-node 数量必须等于 canvas-data.workflow.nodes 数量；
    - edges.from / to 必须引用存在的 node id；
    - 有 --source 时，确认包必须含三类节点章节（与派生来源一致）。
    """
    findings: list[Finding] = []
    if "workflow-flow" not in html.ids:
        # GLOBAL_MAIN_IDS 已报 MISSING_ID，此处不重复
        return findings
    if 'data-node-type="start"' not in source:
        findings.append(
            Finding("WORKFLOW_FLOW", 'Workflow 流程图缺少 Start Event（data-node-type="start"）')
        )
    if 'data-node-type="end"' not in source:
        findings.append(
            Finding("WORKFLOW_FLOW", 'Workflow 流程图缺少 End Event（data-node-type="end"）')
        )
    # 正交连接线：Sequence Flow 只允许横/竖/肘型（M/H/V），禁止曲线/斜线命令（C/Q/S/A）
    sequence_paths = (
        re.findall(r'class="[^"]*\bbpmn-sequence\b"[^>]*\bd="([^"]*)"', source)
        + re.findall(r'\bd="([^"]*)"[^>]*class="[^"]*\bbpmn-sequence\b"', source)
    )
    for path_d in sequence_paths:
        if re.search(r"[CQSA]", path_d):
            findings.append(
                Finding(
                    "WORKFLOW_FLOW",
                    f"Sequence Flow 禁止曲线命令（必须正交 M/H/V）: {path_d}",
                )
            )
            break
    workflow = canvas_data.get("workflow")
    if not isinstance(workflow, dict):
        findings.append(Finding("WORKFLOW_FLOW", "canvas-data.workflow must be an object"))
        return findings
    nodes = workflow.get("nodes")
    edges = workflow.get("edges")
    if not isinstance(nodes, list) or not nodes:
        findings.append(Finding("WORKFLOW_FLOW", "canvas-data.workflow.nodes must be a non-empty array"))
    if not isinstance(edges, list):
        findings.append(Finding("WORKFLOW_FLOW", "canvas-data.workflow.edges must be an array"))
    if isinstance(nodes, list) and nodes:
        node_ids: set[str] = set()
        node_types: set[str] = set()
        numbers: list[str] = []
        for node in nodes:
            if not isinstance(node, dict):
                findings.append(Finding("WORKFLOW_FLOW", "canvas-data.workflow.nodes item must be an object"))
                continue
            node_id = node.get("id")
            node_type = node.get("type")
            node_number = node.get("number")
            numbers.append(str(node_number) if node_number is not None else "")
            if node_id:
                node_ids.add(str(node_id))
            if node_type not in WORKFLOW_FLOW_NODE_TYPES:
                findings.append(
                    Finding(
                        "WORKFLOW_FLOW",
                        f"node {node_id!r} type={node_type!r} must be one of {', '.join(WORKFLOW_FLOW_NODE_TYPES)}",
                    )
                )
            else:
                node_types.add(str(node_type))
        if not all(numbers):
            findings.append(Finding("WORKFLOW_FLOW", "canvas-data.workflow.nodes 缺少 number 字段"))
        elif len(set(numbers)) != len(numbers):
            findings.append(Finding("WORKFLOW_FLOW", "canvas-data.workflow.nodes number 必须唯一"))
        for required in WORKFLOW_FLOW_REQUIRED_TYPES:
            if required not in node_types:
                findings.append(
                    Finding("WORKFLOW_FLOW", f"canvas-data.workflow.nodes 缺少三类节点之一: {required}")
                )
        svg_node_count = len(re.findall(r"class=\"[^\"]*\bbpmn-node\b", source))
        if svg_node_count != len(nodes):
            findings.append(
                Finding(
                    "WORKFLOW_FLOW",
                    f"SVG bpmn-node 数量 {svg_node_count} != canvas-data.workflow.nodes 数量 {len(nodes)}",
                )
            )
        if isinstance(edges, list):
            for edge in edges:
                if not isinstance(edge, dict):
                    findings.append(Finding("WORKFLOW_FLOW", "canvas-data.workflow.edges item must be an object"))
                    continue
                edge_from = str(edge.get("from", ""))
                edge_to = str(edge.get("to", ""))
                if edge_from not in node_ids:
                    findings.append(Finding("WORKFLOW_FLOW", f"edge.from={edge_from!r} 引用了不存在的 node id"))
                if edge_to not in node_ids:
                    findings.append(Finding("WORKFLOW_FLOW", f"edge.to={edge_to!r} 引用了不存在的 node id"))
    if source_path is not None:
        try:
            package = source_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(Finding("WORKFLOW_FLOW", f"cannot read source for workflow flow: {exc}"))
        else:
            for section in WORKFLOW_FLOW_SOURCE_SECTIONS:
                if section not in package:
                    findings.append(Finding("WORKFLOW_FLOW", f"source 缺少 Workflow 三类节点章节: {section}"))
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

def audit_5w_content_mapping(html: HtmlSnapshot, source_path: Path) -> list[Finding]:
    """确认正式 5W 成品的可见业务事实来自同版本确认包（第 6-9 节）。

    校验：
    - 6. 问题陈述：statement → 5w-problem-statement；occurred_at/impact_frequency/participants → 5w-problem-meta
    - 7. 因果链：Why 1-5 的"答案（因为…）"列 → 5w-why-1..5
    - 8. 根本原因：root_cause → 5w-root-cause；so_therefore/stop_check → 5w-root-check
    - 9. 对策四要素：countermeasure/owner/due_date/verify → 5w-countermeasure/5w-owner/5w-due/5w-verify
    """
    try:
        package = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [Finding("CONTENT_MAPPING", f"cannot read 5W package: {exc}")]

    findings: list[Finding] = []

    # 6. 问题陈述
    for row in extract_hmw_table_rows(package, "6. 问题陈述"):
        if len(row) < 2:
            continue
        if row[0] == "statement" or row[0].startswith("statement（"):
            if row[1] not in html.text_by_id.get("5w-problem-statement", ""):
                findings.append(
                    Finding("CONTENT_MAPPING", "5w-problem-statement 未展示确认包问题陈述")
                )
        elif row[0] in ("occurred_at", "impact_frequency", "participants") or any(
            row[0].startswith(f"{key}（") for key in ("occurred_at", "impact_frequency", "participants")
        ):
            if row[1] not in html.text_by_id.get("5w-problem-meta", ""):
                findings.append(
                    Finding("CONTENT_MAPPING", "5w-problem-meta 未展示确认包问题元数据")
                )

    # 7. 因果链（五层，三层面）：答案列（row[3]）→ 5w-why-1..5
    for index, row in enumerate(
        extract_hmw_table_rows(package, "7. 因果链（五层，三层面）")[:5],
        start=1,
    ):
        if len(row) >= 4 and row[3] not in html.text_by_id.get(f"5w-why-{index}", ""):
            findings.append(
                Finding("CONTENT_MAPPING", f"5w-why-{index} 未展示确认包因果链答案")
            )

    # 8. 根本原因
    root_ids = {
        "root_cause": "5w-root-cause",
        "so_therefore": "5w-root-check",
        "stop_check": "5w-root-check",
    }
    for row in extract_hmw_table_rows(package, "8. 根本原因"):
        if len(row) < 2:
            continue
        field = next(
            (key for key in root_ids if row[0] == key or row[0].startswith(f"{key}（")),
            None,
        )
        if field and row[1] not in html.text_by_id.get(root_ids[field], ""):
            findings.append(
                Finding("CONTENT_MAPPING", f"{root_ids[field]} 未展示确认包根本原因字段")
            )

    # 9. 对策四要素
    countermeasure_ids = {
        "countermeasure": "5w-countermeasure",
        "owner": "5w-owner",
        "due_date": "5w-due",
        "verify": "5w-verify",
    }
    for row in extract_hmw_table_rows(package, "9. 对策四要素"):
        if len(row) < 2:
            continue
        field = next(
            (key for key in countermeasure_ids if row[0] == key or row[0].startswith(f"{key}（")),
            None,
        )
        if field and row[1] not in html.text_by_id.get(countermeasure_ids[field], ""):
            findings.append(
                Finding("CONTENT_MAPPING", f"{countermeasure_ids[field]} 未展示确认包对策字段")
            )

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
        findings.append(Finding("INDEX", "--index is only supported for gc/hmw/persona/journey/v2c-vac/5w"))
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
