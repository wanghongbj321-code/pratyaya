"""V2C VAC contract consistency checks."""

from __future__ import annotations

from .models import *  # noqa: F403


V2C_VAC_DISTILL_SKILL = "skills/v2c-vac-distill/SKILL.md"
V2C_VAC_GATE_SKILL = "skills/v2c-vac-gate/SKILL.md"
V2C_VAC_SPEC = "skills/v2c-vac-distill/references/v2c-vac-spec.md"
V2C_VAC_FRAME = "skills/v2c-vac-distill/frameworks/v2c-vac-value-attribution.md"
V2C_VAC_GATE_FILE = "skills/v2c-vac-gate/references/V2C-gate.md"
V2C_VAC_RENDER_CONTRACT = "skills/canvas-render/references/render-contract-v2c-vac.md"
V2C_VAC_TEMPLATE_HTML = "skills/canvas-render/examples/v2c-value-attribution-canvas.html"
V2C_VAC_CANVAS_RENDER_SKILL = "skills/canvas-render/SKILL.md"
V2C_VAC_STATE_SCHEMA = "schemas/state.schema.json"
V2C_VAC_AGENT = "agents/pratyaya.md"
V2C_VAC_PLUGIN_JSON = ".codebuddy-plugin/plugin.json"

V2C_VAC_GATE_ID_RE = re.compile(r"^V2C-GATE-\d{2}$")
V2C_VAC_TPL_GATE_IDS = tuple(f"V2C-VAC-TPL-GATE-{n:02d}" for n in range(1, 9))
V2C_VAC_DEFAULT_GAPS = tuple(f"V2C-AG{n:02d}" for n in range(1, 7))
V2C_VAC_REQUIRED_ANCHORS = (
    "canvas-header",
    "v2c-vac-headline",
    "v2c-vac-summary",
    "v2c-vac-key-gaps",
    "v2c-vac-next-step",
    "v2c-vac-canvas",
    "v2c-vac-attribution-chain",
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
    *(f"v2c-vac-gap-{gap}" for gap in V2C_VAC_DEFAULT_GAPS),
    "v2c-vac-quality-check",
    "v2c-vac-quality-semantics",
    "v2c-vac-quality-honesty",
    "v2c-vac-quality-verifiability",
    "v2c-vac-quality-next-step",
    "v2c-vac-inferences",
    "quality-panel",
    "quality-version",
    "quality-approval",
    "quality-gaps",
    "quality-risks",
    "quality-caveat",
    "local-notes",
    "canvas-data",
)


def _skill_name_ok(ctx: CheckContext, path_text: str, expected_name: str) -> Finding | None:
    path = ctx.root / path_text
    text = read_text(path)
    if not path.is_file() or not re.search(
        rf"^name:\s*{re.escape(expected_name)}\s*$",
        text,
        re.MULTILINE,
    ):
        return Finding(
            code="V2C_VAC_SKILL_PATH",
            level="error",
            where=path_text,
            message=f"V2C VAC Skill 缺失或 frontmatter name 不是 {expected_name}",
            hint="v2c-vac-distill 与 v2c-vac-gate 必须保持扁平 skill 名与目录名一致",
        )
    return None


def _parse_gate_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    columns: list[str] = []
    in_table = False
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            in_table = False
            columns = []
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        if not in_table:
            if cells[0].strip().lower() == "id":
                in_table = True
                columns = [cell.strip().strip("`").lower() for cell in cells]
            continue
        gate_id = cells[0].strip().strip("`")
        if not gate_id.startswith("V2C-GATE-"):
            continue
        row: dict[str, str] = {"id": gate_id}
        col_map = {"分类": "category", "风险等级": "risk", "来源": "source"}
        for index, value in enumerate(cells[1:], start=1):
            if index >= len(columns):
                continue
            header = columns[index]
            row[col_map.get(header, header)] = value.strip().strip("`")
        rows.append(row)
    return rows


def check_v2c_vac_skill_paths(ctx: CheckContext) -> list[Finding]:
    """V2C VAC 分析层、治理层与权威参考文件必须齐全。"""
    findings: list[Finding] = []
    for path_text, expected_name in (
        (V2C_VAC_DISTILL_SKILL, "v2c-vac-distill"),
        (V2C_VAC_GATE_SKILL, "v2c-vac-gate"),
    ):
        finding = _skill_name_ok(ctx, path_text, expected_name)
        if finding is not None:
            findings.append(finding)

    for path_text, purpose in (
        (V2C_VAC_SPEC, "分析层 spec"),
        (V2C_VAC_FRAME, "Value-to-Capability 框架"),
        (V2C_VAC_GATE_FILE, "治理层 Gate"),
        (V2C_VAC_RENDER_CONTRACT, "渲染契约"),
        (V2C_VAC_TEMPLATE_HTML, "示例模板"),
    ):
        if not (ctx.root / path_text).is_file():
            findings.append(
                Finding(
                    code="V2C_VAC_SKILL_PATH",
                    level="error",
                    where=path_text,
                    message=f"缺少 V2C VAC {purpose} 文件",
                    hint="Step 1-4 的资源文件必须同时存在，后续路由和渲染才有共同契约",
                )
            )
    return findings


def check_v2c_vac_gate_table(ctx: CheckContext) -> list[Finding]:
    """V2C-gate.md 必须定义 12 条稳定 Gate，并保持分类/风险/来源合法。"""
    path = ctx.root / V2C_VAC_GATE_FILE
    if not path.is_file():
        return [
            Finding(
                code="V2C_VAC_GATE_FILE",
                level="error",
                where=V2C_VAC_GATE_FILE,
                message="缺少 V2C VAC Gate 文件",
                hint="需要 skills/v2c-vac-gate/references/V2C-gate.md",
            )
        ]

    text = read_text(path)
    rows = _parse_gate_rows(text)
    findings: list[Finding] = []
    expected_ids = {f"V2C-GATE-{n:02d}" for n in range(1, 13)}
    actual_ids = [row.get("id", "") for row in rows]
    missing_ids = sorted(expected_ids - set(actual_ids))
    extra_ids = sorted(set(actual_ids) - expected_ids)
    if missing_ids or extra_ids or len(actual_ids) != 12:
        findings.append(
            Finding(
                code="V2C_VAC_GATE_FILE",
                level="error",
                where=V2C_VAC_GATE_FILE,
                message=f"V2C VAC Gate ID 集合不完整：missing={missing_ids}, extra={extra_ids}, count={len(actual_ids)}",
                hint="必须恰好定义 V2C-GATE-01..12",
            )
        )
    if len(actual_ids) != len(set(actual_ids)):
        findings.append(
            Finding(
                code="V2C_VAC_GATE_FILE",
                level="error",
                where=V2C_VAC_GATE_FILE,
                message="V2C VAC Gate ID 重复",
                hint="每个 V2C-GATE-xx 只能出现一次表格数据行",
            )
        )

    categories = {row.get("category", "") for row in rows}
    for row in rows:
        gate_id = row.get("id", "")
        category = row.get("category", "")
        risk = row.get("risk", "")
        source = row.get("source", "")
        if not V2C_VAC_GATE_ID_RE.match(gate_id):
            findings.append(
                Finding(
                    code="V2C_VAC_GATE_ID_FORMAT",
                    level="error",
                    where=V2C_VAC_GATE_FILE,
                    message=f"Gate ID 格式不符：{gate_id}",
                    hint="V2C VAC Gate ID 必须形如 V2C-GATE-01",
                )
            )
        if category not in ALLOWED_GATE_CATEGORIES:
            findings.append(
                Finding(
                    code="V2C_VAC_GATE_CATEGORY",
                    level="error",
                    where=V2C_VAC_GATE_FILE,
                    message=f"{gate_id} 分类 {category!r} 不在白名单内",
                    hint="分类必须为 information_integrity 或 business_risk",
                )
            )
        if risk not in ALLOWED_GATE_RISK_LEVELS:
            findings.append(
                Finding(
                    code="V2C_VAC_GATE_RISK",
                    level="error",
                    where=V2C_VAC_GATE_FILE,
                    message=f"{gate_id} 风险等级 {risk!r} 不在白名单内",
                    hint="风险等级必须为 low / medium / high",
                )
            )
        if not source:
            findings.append(
                Finding(
                    code="V2C_VAC_GATE_SOURCE",
                    level="error",
                    where=V2C_VAC_GATE_FILE,
                    message=f"{gate_id} 来源为空",
                    hint="每条 V2C Gate 都必须能回指确认包 section、state 或 V2C-* 来源 ID",
                )
            )
    if categories != ALLOWED_GATE_CATEGORIES:
        findings.append(
            Finding(
                code="V2C_VAC_GATE_CATEGORY",
                level="error",
                where=V2C_VAC_GATE_FILE,
                message=f"V2C VAC Gate 必须同时包含信息完整性和业务风险分类，当前={sorted(categories)}",
                hint="V2C VAC 的 override 边界依赖两类 Gate 的明确区分",
            )
        )
    for gap_id in V2C_VAC_DEFAULT_GAPS:
        if gap_id not in text:
            findings.append(
                Finding(
                    code="V2C_VAC_GATE_GAPS",
                    level="error",
                    where=V2C_VAC_GATE_FILE,
                    message=f"Gate 文件缺默认归因断点 {gap_id}",
                    hint="V2C-AG01..06 必须在 Gate 文件中有映射与边界说明",
                )
            )
    return findings


def check_v2c_vac_render_contract_sync(ctx: CheckContext) -> list[Finding]:
    """V2C VAC render contract、canvas-render Skill 与示例模板必须共享机器标识和锚点。"""
    findings: list[Finding] = []
    contract_text = read_text(ctx.root / V2C_VAC_RENDER_CONTRACT)
    template_text = read_text(ctx.root / V2C_VAC_TEMPLATE_HTML)
    render_skill_text = read_text(ctx.root / V2C_VAC_CANVAS_RENDER_SKILL)
    combined = {
        V2C_VAC_RENDER_CONTRACT: contract_text,
        V2C_VAC_TEMPLATE_HTML: template_text,
        V2C_VAC_CANVAS_RENDER_SKILL: render_skill_text,
    }

    bad_canvas_type_patterns = (
        re.compile(r"canvas_type\s*=\s*v2c(?!-)"),
        re.compile(r'"canvas_type"\s*:\s*"v2c"(?!-)'),
        re.compile(r'"canvas_type":"v2c"(?!-)'),
    )
    for path_text, text in combined.items():
        for token in ('canvas_type=v2c-vac', 'canvas_type":"v2c-vac"', '"canvas_type": "v2c-vac"'):
            if token in text:
                break
        else:
            findings.append(
                Finding(
                    code="V2C_VAC_CANVAS_TYPE",
                    level="error",
                    where=path_text,
                    message="缺少 V2C VAC 的精确机器标识 canvas_type=v2c-vac",
                    hint="v2c 是系列名；Value Attribution Canvas 这张画布必须使用 v2c-vac",
                )
            )
        if any(pattern.search(text) for pattern in bad_canvas_type_patterns):
            findings.append(
                Finding(
                    code="V2C_VAC_CANVAS_TYPE",
                    level="error",
                    where=path_text,
                    message="发现不精确的 canvas_type=v2c",
                    hint="请使用 canvas_type=v2c-vac",
                )
            )

    if 'data-page-type="v2c-vac"' not in template_text:
        findings.append(
            Finding(
                code="V2C_VAC_TEMPLATE_ANCHORS",
                level="error",
                where=V2C_VAC_TEMPLATE_HTML,
                message='V2C VAC 模板缺 body data-page-type="v2c-vac"',
                hint="Template Gate 依赖稳定页面类型",
            )
        )
    template_missing = [
        anchor for anchor in V2C_VAC_REQUIRED_ANCHORS
        if f'id="{anchor}"' not in template_text
    ]
    if template_missing:
        findings.append(
            Finding(
                code="V2C_VAC_TEMPLATE_ANCHORS",
                level="error",
                where=V2C_VAC_TEMPLATE_HTML,
                message=f"模板缺 V2C VAC 稳定锚点：{', '.join(template_missing)}",
                hint="render-contract-v2c-vac.md 与示例模板必须共同覆盖所有稳定锚点",
            )
        )
    contract_missing = [
        anchor for anchor in V2C_VAC_REQUIRED_ANCHORS
        if f"`{anchor}`" not in contract_text and f'id="{anchor}"' not in contract_text
    ]
    if contract_missing:
        findings.append(
            Finding(
                code="V2C_VAC_RENDER_CONTRACT",
                level="error",
                where=V2C_VAC_RENDER_CONTRACT,
                message=f"渲染契约缺稳定锚点：{', '.join(contract_missing)}",
                hint="契约锚点集合必须与 Template Gate 保持一致",
            )
        )
    skill_has_tpl_gate_range = "V2C-VAC-TPL-GATE-01..08" in render_skill_text
    tpl_gate_missing = [
        gate_id for gate_id in V2C_VAC_TPL_GATE_IDS
        if gate_id not in contract_text or (gate_id not in render_skill_text and not skill_has_tpl_gate_range)
    ]
    if tpl_gate_missing:
        findings.append(
            Finding(
                code="V2C_VAC_TPL_GATE_IDS",
                level="error",
                where=V2C_VAC_RENDER_CONTRACT,
                message=f"V2C VAC Template Gate ID 未在契约和 canvas-render Skill 中同步：{', '.join(tpl_gate_missing)}",
                hint="V2C-VAC-TPL-GATE-01..08 是不可 override 的模板治理 ID",
            )
        )
    for token in (
        "output/v2c-vac-canvas-{slug}--v{N}.html",
        "output/v2c-vac-canvas.html",
        "v2c-vac-index",
        "skills/canvas-render/examples/v2c-value-attribution-canvas.html",
    ):
        if token not in contract_text:
            findings.append(
                Finding(
                    code="V2C_VAC_RENDER_CONTRACT",
                    level="error",
                    where=V2C_VAC_RENDER_CONTRACT,
                    message=f"渲染契约缺输出/模板约定：{token}",
                    hint="详情页、索引页与示例模板路径必须稳定",
                )
            )
    return findings


def check_v2c_vac_state_schema_and_routing(ctx: CheckContext) -> list[Finding]:
    """state schema、主 Agent 路由与 plugin 注册必须显式支持 v2c-vac。"""
    findings: list[Finding] = []
    schema_text = read_text(ctx.root / V2C_VAC_STATE_SCHEMA)
    agent_text = read_text(ctx.root / V2C_VAC_AGENT)
    plugin_text = read_text(ctx.root / V2C_VAC_PLUGIN_JSON)
    for token in (
        '"v2c_vac"',
        '"3.0-v2c-vac-1"',
        '"generation_path"',
        '"pipeline"',
        '"transcript-direct"',
        '"override_audit"',
        '"assessment_id"',
        '"^V2C-GATE-[0-9]+$"',
    ):
        if token not in schema_text:
            findings.append(
                Finding(
                    code="V2C_VAC_STATE_SCHEMA",
                    level="error",
                    where=V2C_VAC_STATE_SCHEMA,
                    message=f"state schema 缺 V2C VAC token：{token}",
                    hint="state.v2c_vac.{slug} 必须显式约束生成路径、授权与 override 审计",
                )
            )

    for token in (
        "v2c-vac-distill",
        "v2c-vac-gate",
        "canvas_type=v2c-vac",
        "state.v2c_vac",
        "V2C-VAC-{slug}-v{N}.md",
        "V2C-VAC-TPL-GATE-01..08",
        "追问画布类型，不进入 MAAU、V2C VAC 或任何其他画布",
    ):
        if token not in agent_text:
            findings.append(
                Finding(
                    code="V2C_VAC_ROUTING",
                    level="error",
                    where=V2C_VAC_AGENT,
                    message=f"主 Agent 缺 V2C VAC 路由/治理约定：{token}",
                    hint="V2C VAC 不得由默认 MAAU 入口隐式承接，必须显式指定画布",
                )
            )

    for token in ('"./skills/v2c-vac-distill"', '"./skills/v2c-vac-gate"'):
        if token not in plugin_text:
            findings.append(
                Finding(
                    code="V2C_VAC_ROUTING",
                    level="error",
                    where=V2C_VAC_PLUGIN_JSON,
                    message=f"plugin.json 未注册 {token}",
                    hint="plugin 与 Agent 的 skill 列表必须同步",
                )
            )
    return findings
