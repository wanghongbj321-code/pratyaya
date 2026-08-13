from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import cast

from .audit_models import (
    AUTH_FIELDS, DEFAULT_CONTRACT, GC_CONTRACT, GC_MAIN_IDS, GLOBAL_MAIN_IDS, HMW_ANCHORS, HMW_CONTRACT,
    HMW_MAIN_IDS, HMW_TPL_GOVERN_IDS, HMW_TPL_MAIN_IDS, HMW_TPL_STABLE_ANCHORS, INSTANCE_STATE_KEYS,
    JOURNEY_ANCHORS, JOURNEY_CONTRACT, JOURNEY_MAIN_IDS, JOURNEY_TEMPLATE, JOURNEY_TPL_MAIN_IDS,
    MODULE_MAIN_IDS, PERSONA_CONTRACT, PERSONA_MAIN_IDS, PERSONA_STABLE_ANCHORS, PERSONA_TPL_GOVERN_IDS,
    SHARED_IDS, V2C_VAC_ANCHORS, V2C_VAC_CONTRACT, V2C_VAC_MAIN_IDS, V2C_VAC_TPL_GOVERN_IDS,
    Finding, JsonDict,
)
from .audit_helpers import (
    audit_hmw_content_mapping, audit_index_page, audit_maau_transcript_direct, audit_persona_content_mapping,
    audit_v2c_vac_override, expected_in_order, gc_source_identity, hmw_source_identity, journey_source_identity,
    load_contract_anchor_orders, load_gc_anchor_orders, load_json, maau_source_identity, normalize_version, parse_html,
    persona_source_identity, select_instance_state, select_maau_instance_state, source_identity, audit_v2c_vac_identity,
    v2c_vac_source_identity,
)
from .audit_template_gates import (
    audit_journey_dynamic_structure, audit_journey_template_gate, audit_template_gate, element_is_hidden,
    load_hmw_template_profile, load_journey_template_profile, load_persona_template_profile, load_v2c_vac_template_profile,
    stylesheet_hides_element,
)

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
    is_v2c_vac = canvas_type == "v2c-vac"
    # MAAU transcript-direct：mvl + global + 显式 --instance 即判定为一次性综合实例页
    is_maau = canvas_type == "mvl" and instance_slug is not None and not index
    findings: list[Finding] = []
    orders: dict[str, list[str]] = {}
    gc_anchors: list[str] = []
    hmw_anchors: list[str] = []
    persona_anchors: list[str] = []
    v2c_vac_anchors: list[str] = []
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
    elif is_v2c_vac:
        profile = load_v2c_vac_template_profile(contract_path)
        v2c_vac_anchors = profile.get("stable_anchors") or list(V2C_VAC_ANCHORS)
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
    elif is_v2c_vac:
        valid_types = {"v2c-vac"}
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
    if is_gc or is_hmw or is_journey or is_persona or is_v2c_vac:
        if is_gc:
            required.extend(GC_MAIN_IDS)
        elif is_hmw:
            required.extend(HMW_MAIN_IDS)
        elif is_journey:
            required.extend(JOURNEY_MAIN_IDS)
        elif is_v2c_vac:
            required.extend(V2C_VAC_MAIN_IDS)
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
    elif is_v2c_vac:
        expected_anchors = list(v2c_vac_anchors)
        anchor_missing = [anchor for anchor in expected_anchors if counts[anchor] == 0]
        if anchor_missing:
            findings.append(
                Finding("MISSING_ANCHOR", f"V2C VAC missing anchors: {', '.join(anchor_missing)}")
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
        if is_v2c_vac and canvas_data.get("canvas_type") != "v2c-vac":
            findings.append(
                Finding("CANVAS_TYPE", f"canvas-data.canvas_type must be 'v2c-vac', got {canvas_data.get('canvas_type')!r}")
            )
        if canvas_type in INSTANCE_STATE_KEYS and instance_slug is not None:
            data_instance = canvas_data.get("instance") or canvas_data.get("instance_slug")
            if data_instance != instance_slug:
                findings.append(
                    Finding("INSTANCE", f"canvas-data instance={data_instance!r} must match --instance {instance_slug!r}")
                )
        sections = canvas_data.get("sections")
        if expected_anchors and isinstance(sections, dict) and not is_v2c_vac:
            section_missing = [anchor for anchor in expected_anchors if anchor not in sections]
            if section_missing:
                findings.append(
                    Finding("SECTION_DATA", f"canvas-data.sections missing: {', '.join(section_missing)}")
                )
        elif expected_anchors and not isinstance(sections, dict):
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
        if is_v2c_vac:
            findings.extend(audit_v2c_vac_identity(canvas_data, source_path))
            findings.extend(audit_v2c_vac_override(canvas_data))

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

    # Caveat checks (for MVL module-detail / GC / HMW single-canvas pages)
    if is_gc:
        caveat_page_types = {"golden-circle"}
    elif is_hmw:
        caveat_page_types = {"hmw"}
    elif is_journey:
        caveat_page_types = {"journey"}
    elif is_persona:
        caveat_page_types = {"persona"}
    elif is_v2c_vac:
        caveat_page_types = {"v2c-vac"}
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
            elif is_v2c_vac:
                source_module, source_version = v2c_vac_source_identity(source_path)
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
                    and not is_v2c_vac
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
                if is_v2c_vac and instance_slug is not None and source_module != instance_slug:
                    findings.append(
                        Finding(
                            "V2C_SOURCE_SLUG",
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
            elif is_v2c_vac:
                state_module = select_instance_state(state, "v2c-vac", instance_slug)
                if not isinstance(state_module, dict):
                    raise ValueError("state.json has no v2c_vac instance record")
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
            if is_v2c_vac and canvas_data is not None:
                state_generation = state_module.get("generation_path")
                data_generation = canvas_data.get("generation_path")
                if state_generation not in ("pipeline", "transcript-direct"):
                    findings.append(
                        Finding(
                            "V2C_STATE_GENERATION",
                            f"state.v2c_vac.{instance_slug}.generation_path must be 'pipeline' or 'transcript-direct', got {state_generation!r}",
                        )
                    )
                if data_generation != state_generation:
                    findings.append(
                        Finding(
                            "V2C_GENERATION",
                            f"canvas-data generation_path={data_generation!r} != state {state_generation!r}",
                        )
                    )
                data_source_file = canvas_data.get("source_file")
                state_source_file = state_module.get("source_file")
                if data_source_file != state_source_file:
                    findings.append(
                        Finding(
                            "V2C_SOURCE_FILE",
                            f"canvas-data source_file={data_source_file!r} != state {state_source_file!r}",
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
        choices=("mvl", "gc", "hmw", "persona", "journey", "v2c-vac"),
        default="mvl",
        help="canvas type: mvl (default), gc (golden circle), hmw, persona, journey or v2c-vac",
    )
    _ = parser.add_argument(
        "--page-type",
        dest="page_type_arg",
        choices=("global", "module-detail", "golden-circle-index", "hmw-index", "persona-index", "journey-index", "v2c-vac-index"),
        default=None,
        help="page type hint (MAAU transcript-direct 实例页必须传 global；非 MVL 索引页可传 {canvas_type}-index)",
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
    elif canvas_type == "v2c-vac":
        contract_arg = V2C_VAC_CONTRACT
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
    elif canvas_type == "v2c-vac":
        if template_arg is None:
            if source_arg is not None or state_arg is not None:
                template_findings.append(
                    Finding("V2C-VAC-TPL-GATE-00", "V2C VAC 正式交付必须传入 --template 示例模板路径")
                )
        else:
            try:
                template_source, template = parse_html(template_arg)
                profile = load_v2c_vac_template_profile(contract_arg)
                if not profile["main_order"]:
                    template_findings.append(
                        Finding("V2C-VAC-TPL-GATE-00", "render-contract-v2c-vac.md 模板 profile 无法解析")
                    )
                else:
                    template_findings.extend(
                        audit_template_gate(
                            template, template_source, template_arg, template, profile,
                            gate_prefix="V2C-VAC",
                            check_ids=V2C_VAC_MAIN_IDS,
                            check_stable_anchors=V2C_VAC_ANCHORS,
                            check_govern_ids=V2C_VAC_TPL_GOVERN_IDS,
                            hidden_section_ids=(
                                "v2c-vac-attribution-chain",
                                "v2c-vac-attribution-gaps",
                                "v2c-vac-quality-check",
                                "v2c-vac-inferences",
                                "quality-panel",
                            ),
                        )
                    )
                    html_source, html_snapshot = parse_html(html_arg)
                    template_findings.extend(
                        audit_template_gate(
                            html_snapshot, html_source, html_arg, template, profile,
                            gate_prefix="V2C-VAC",
                            check_ids=V2C_VAC_MAIN_IDS,
                            check_stable_anchors=V2C_VAC_ANCHORS,
                            check_govern_ids=V2C_VAC_TPL_GOVERN_IDS,
                            hidden_section_ids=(
                                "v2c-vac-attribution-chain",
                                "v2c-vac-attribution-gaps",
                                "v2c-vac-quality-check",
                                "v2c-vac-inferences",
                                "quality-panel",
                            ),
                        )
                    )
            except (OSError, UnicodeError) as exc:
                template_findings.append(Finding("V2C-VAC-TPL-GATE-00", f"模板读取失败: {exc}"))

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
