from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .audit_models import (
    HMW_TPL_GOVERN_IDS, HMW_TPL_MAIN_IDS, HMW_TPL_STABLE_ANCHORS,
    JOURNEY_ANCHORS, JOURNEY_STAGE_DATA_FIELDS, JOURNEY_STAGE_FIELDS,
    JOURNEY_QUALITY_KEYS, Finding, HtmlSnapshot,
)
from .audit_helpers import extract_markdown_table_rows

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

def load_v2c_vac_template_profile(contract_path: Path) -> dict[str, list[str]]:
    """从 render-contract-v2c-vac.md 解析 V2C VAC 模板结构 profile。"""
    text = contract_path.read_text(encoding="utf-8")
    main_order: list[str] = []
    stable_anchors: list[str] = []

    order_match = re.search(
        r"## 5\.\s*一级模块顺序.*?\n```text\s*(.*?)```",
        text,
        re.DOTALL,
    )
    if order_match:
        for line in order_match.group(1).splitlines():
            m = re.match(r"\s*(?:->|→)?\s*([a-z][A-Za-z0-9-]+)\s*$", line)
            if m:
                main_order.append(m.group(1))

    anchor_match = re.search(
        r"## 6\.\s*稳定锚点集合.*?\n(.*?)(?=\n## |\Z)",
        text,
        re.DOTALL,
    )
    if anchor_match:
        stable_anchors = re.findall(
            r"`(v2c-vac-[A-Za-z0-9-]+|quality-[a-z0-9-]+|local-notes|canvas-data)`",
            anchor_match.group(1),
        )
    return {"main_order": main_order, "stable_anchors": stable_anchors}

def load_5w_template_profile(contract_path: Path) -> dict[str, list[str]]:
    """从 render-contract-5w.md 解析 5W 模板结构 profile（一级模块顺序 + 稳定锚点）。

    返回 {"main_order": [...], "stable_anchors": [...]}。

    注意：5W 锚点以数字开头（`5w-*`），一级模块解析正则须允许数字首字符，
    不能直接复用 hmw/persona 的 `[a-z]` 开头正则。
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
            m = re.match(r"\s*→\s*([a-z0-9][a-z0-9-]*)\s*$", line)
            if m:
                main_order.append(m.group(1))

    anchor_match = re.search(
        r"### 稳定锚点集合（Template Gate 校验）(.*?)(?=\n### |\Z)",
        text,
        re.DOTALL,
    )
    if anchor_match:
        stable_anchors = re.findall(
            r"`(5w-[a-z0-9-]+|quality-[a-z0-9-]+|local-notes|canvas-data)`",
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

    # {gate_prefix}-TPL-GATE-06: 共享主题/窄屏 + 无外部依赖
    # 方案 A（2026-08-09）：主题必须自包含——内联 <style>（含 [data-theme] 与主色 token）或
    # 指向本地已存在文件的 <link> 均视为合法；但**正式产物禁止依赖本地相对路径外链 CSS**，
    # 否则单独传播 HTML 时样式丢失。外部网络依赖恒为 FAIL。
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
