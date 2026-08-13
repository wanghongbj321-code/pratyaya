"""Cross-document schema, state, authorization, and render sync checks."""

from __future__ import annotations

from .models import *  # noqa: F403


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
    cat = _dig(audit, "properties", "items", "items", "properties", "category")
    if not cat.get("enum"):
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


