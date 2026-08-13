"""Specialized checks for first-class canvas families."""

from __future__ import annotations

from .models import *  # noqa: F403


def check_persona_skill_paths(ctx: CheckContext) -> list[Finding]:
    """Persona 一等公民资源、稳定 Gate ID 与模板锚点必须同时存在。"""
    findings: list[Finding] = []
    for path_text, expected_name in (
        (PERSONA_DISTILL_SKILL, "persona-distill"),
        (PERSONA_GATE_SKILL, "persona-gate"),
    ):
        path = ctx.root / path_text
        if not path.is_file() or not re.search(
            rf"^name:\s*{expected_name}\s*$", read_text(path), re.MULTILINE
        ):
            findings.append(
                Finding(
                    code="PERSONA_SKILL_PATH",
                    level="error",
                    where=path_text,
                    message=f"Persona Skill 缺失或 frontmatter name 不是 {expected_name}",
                    hint="persona-distill 与 persona-gate 都必须以扁平路径注册",
                )
            )

    gate_text = read_text(ctx.root / PERSONA_GATE_FILE)
    missing_ids = [f"PERSONA-GATE-{n:02d}" for n in range(1, 7) if f"PERSONA-GATE-{n:02d}" not in gate_text]
    if missing_ids:
        findings.append(
            Finding(
                code="PERSONA_GATE_FILE_SET",
                level="error",
                where=PERSONA_GATE_FILE,
                message=f"Persona Gate 缺稳定 ID：{', '.join(missing_ids)}",
                hint="PERSONA-GATE-01..06 必须完整且唯一",
            )
        )

    template_text = read_text(ctx.root / PERSONA_TEMPLATE_HTML)
    missing_anchors = [anchor for anchor in PERSONA_REQUIRED_ANCHORS if f'id="{anchor}"' not in template_text]
    if missing_anchors:
        findings.append(
            Finding(
                code="PERSONA_TEMPLATE_ANCHORS",
                level="error",
                where=PERSONA_TEMPLATE_HTML,
                message=f"Persona 模板缺稳定锚点：{', '.join(missing_anchors)}",
                hint="模板必须保留 9 基本信息、6 宫格、4 质量鉴别和治理模块",
            )
        )

    contract_text = read_text(ctx.root / PERSONA_CONTRACT)
    if "PERSONA-TPL-GATE-01" not in contract_text or "PERSONA-TPL-GATE-06" not in contract_text:
        findings.append(
            Finding(
                code="PERSONA_TPL_GATE_IDS",
                level="error",
                where=PERSONA_CONTRACT,
                message="Persona 渲染契约缺 PERSONA-TPL-GATE-01..06 定义",
                hint="Template Gate 规则必须在 Persona 渲染契约中稳定定义",
            )
        )
    return findings


def check_hmw_skill_paths(ctx: CheckContext) -> list[Finding]:
    """执行计划 §8 规则 2：HMW Skill 路径存在且 frontmatter name 匹配。"""
    findings: list[Finding] = []
    for path, expected in (
        (ctx.root / HMW_DISTILL_SKILL, "hmw-distill"),
        (ctx.root / HMW_GATE_SKILL, "hmw-gate"),
    ):
        if not path.is_file():
            findings.append(
                Finding(
                    code="HMW_SKILL_PATH",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"缺少 HMW Skill：{path.name}",
                    hint="需按执行计划创建 hmw-distill / hmw-gate",
                )
            )
            continue
        text = read_text(path)
        if not re.search(rf"^name:\s*{expected}\s*$", text, re.MULTILINE):
            findings.append(
                Finding(
                    code="HMW_SKILL_NAME",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"frontmatter name 应为 {expected}",
                    hint="SKILL.md frontmatter name 必须与目录名一致",
                )
            )
    return findings


def check_hmw_gate_table(ctx: CheckContext) -> list[Finding]:
    """执行计划 §8 规则 3：HMW-gate.md 表格可解析，ID/分类/风险/来源合法。"""
    findings: list[Finding] = []
    p = ctx.root / HMW_GATE_FILE
    if not p.is_file():
        return [
            Finding(
                code="HMW_GATE_FILE_SET",
                level="error",
                where=HMW_GATE_FILE,
                message="缺少 HMW 闸门策略文件 HMW-gate.md",
                hint="需在 skills/hmw-gate/references/HMW-gate.md 写入 6 条放行条件",
            )
        ]
    text = p.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    in_table = False
    columns: list[str] = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            in_table = False
            columns = []
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        if not in_table:
            if cells and cells[0].strip().lower() == "id":
                in_table = True
                columns = [c.strip().strip("`").lower() for c in cells]
            continue
        first = cells[0].strip().strip("`")
        if not HMW_GATE_ID_RE.match(first):
            continue
        row: dict[str, str] = {"id": first}
        col_map = {"分类": "category", "风险等级": "risk", "来源": "source"}
        for idx, value in enumerate(cells[1:], start=1):
            if idx >= len(columns):
                continue
            header = columns[idx]
            alias = col_map.get(header, header)
            row[alias] = value.strip().strip("`")
        for key in ("category", "risk", "source"):
            if key not in row:
                row[key] = ""
        rows.append(row)
    if not rows:
        findings.append(
            Finding(
                code="HMW_GATE_TABLE",
                level="error",
                where=HMW_GATE_FILE,
                message="HMW-gate.md 表格无数据行",
                hint="表格需要 6 条放行条件",
            )
        )
        return findings
    ids_seen: list[str] = []
    for row in rows:
        gid = row.get("id", "")
        cat = row.get("category", "")
        risk = row.get("risk", "")
        source = row.get("source", "")
        if not HMW_GATE_ID_RE.match(gid):
            findings.append(
                Finding(
                    code="HMW_GATE_ID_FORMAT",
                    level="error",
                    where=HMW_GATE_FILE,
                    message=f"HMW-GATE ID 格式不符：{gid}（期望 HMW-GATE-NN）",
                    hint="HMW-GATE ID 须为 HMW-GATE-01..HMW-GATE-06",
                )
            )
        if cat not in ALLOWED_GATE_CATEGORIES:
            findings.append(
                Finding(
                    code="HMW_GATE_CATEGORY",
                    level="error",
                    where=HMW_GATE_FILE,
                    message=f"HMW-GATE {gid} 分类 {cat!r} 不在白名单 {ALLOWED_GATE_CATEGORIES}",
                    hint="分类必须为 information_integrity 或 business_risk",
                )
            )
        if risk not in ALLOWED_GATE_RISK_LEVELS:
            findings.append(
                Finding(
                    code="HMW_GATE_RISK",
                    level="error",
                    where=HMW_GATE_FILE,
                    message=f"HMW-GATE {gid} 风险等级 {risk!r} 不在白名单 {ALLOWED_GATE_RISK_LEVELS}",
                    hint="风险等级必须为 low / medium / high",
                )
            )
        if not source:
            findings.append(
                Finding(
                    code="HMW_GATE_SOURCE",
                    level="error",
                    where=HMW_GATE_FILE,
                    message=f"HMW-GATE {gid} 来源 ID 为空",
                    hint="每条放行条件必须填写来源 ID",
                )
            )
        ids_seen.append(gid)
    if len(ids_seen) != 6:
        findings.append(
            Finding(
                code="HMW_GATE_COUNT",
                level="error",
                where=HMW_GATE_FILE,
                message=f"HMW-GATE 共 {len(ids_seen)} 条（期望 6 条）",
                hint="HMW 闸门必须有 6 条放行条件：HMW-GATE-01..HMW-GATE-06",
            )
        )
    if len(set(ids_seen)) != len(ids_seen):
        findings.append(
            Finding(
                code="HMW_GATE_ID_UNIQUE",
                level="error",
                where=HMW_GATE_FILE,
                message="HMW-GATE ID 重复",
                hint="每个 HMW-GATE-xx ID 必须唯一",
            )
        )
    return findings


def check_hmw_template_and_anchors(ctx: CheckContext) -> list[Finding]:
    """执行计划 §8 规则 5-6：HMW 模板存在且含 8 固定 idea 锚点；canvas-render 示例映射准确。"""
    findings: list[Finding] = []
    tpl = ctx.root / HMW_TEMPLATE_HTML
    if not tpl.is_file():
        findings.append(
            Finding(
                code="HMW_TEMPLATE_MISSING",
                level="error",
                where=HMW_TEMPLATE_HTML,
                message="缺少 HMW 一等公民模板 hmw-canvas.html",
                hint="需在 skills/canvas-render/examples/hmw-canvas.html 创建 4 字段 + 8 想法格模板",
            )
        )
    else:
        text = tpl.read_text(encoding="utf-8")
        missing_ideas = [a for a in HMW_IDEA_ANCHORS if a not in text]
        if missing_ideas:
            findings.append(
                Finding(
                    code="HMW_IDEA_ANCHORS",
                    level="error",
                    where=HMW_TEMPLATE_HTML,
                    message=f"模板缺固定想法锚点：{', '.join(missing_ideas)}",
                    hint="hmw-idea-1..hmw-idea-8 必须全部存在",
                )
            )
        if "hmw-quality" not in text or "hmw-coherence" not in text or "quality-panel" not in text:
            findings.append(
                Finding(
                    code="HMW_TPL_MODULES",
                    level="error",
                    where=HMW_TEMPLATE_HTML,
                    message="模板必须含独立的 hmw-quality / hmw-coherence / quality-panel 模块",
                    hint="质量鉴别、想法对应与治理面板不能只存在于 canvas-data",
                )
            )
    # canvas-render 示例映射
    render_skill = ctx.root / "skills/canvas-render/SKILL.md"
    if render_skill.is_file():
        render_text = read_text(render_skill)
        # SKILL.md 是 skill 内部文档；示例映射表按 P0-2 修订用 skill 内相对。
        # 接受 skill 内相对或仓库根相对任一形式。
        if (
            "examples/hmw-canvas.html" not in render_text
            and "skills/canvas-render/examples/hmw-canvas.html" not in render_text
        ):
            findings.append(
                Finding(
                    code="HMW_RENDER_MAP",
                    level="error",
                    where="skills/canvas-render/SKILL.md",
                    message="canvas-render 示例映射缺少 HMW 行",
                    hint="在示例映射表补 `hmw` → examples/hmw-canvas.html（skill 内相对）或 skills/canvas-render/examples/hmw-canvas.html（仓库根相对）",
                )
            )
    return findings


def check_hmw_id_naming(ctx: CheckContext) -> list[Finding]:
    """执行计划 §8 规则 12：HMW 推断 ID 用 HMW-Inf-N，与想法种子 HMW-Idea-N 区分。"""
    findings: list[Finding] = []
    spec = ctx.root / "skills/hmw-distill/references/hmw-spec.md"
    if spec.is_file():
        text = read_text(spec)
        if "HMW-Inf" not in text:
            findings.append(
                Finding(
                    code="HMW_INF_ID",
                    level="error",
                    where=str(spec.relative_to(ctx.root)),
                    message="hmw-spec.md 未定义推断 ID HMW-Inf-N",
                    hint="推断 ID 必须为 HMW-Inf-N，与想法种子 HMW-Idea-N 严格区分",
                )
            )
        if "HMW-Idea" not in text:
            findings.append(
                Finding(
                    code="HMW_IDEA_ID",
                    level="error",
                    where=str(spec.relative_to(ctx.root)),
                    message="hmw-spec.md 未定义想法种子 ID HMW-Idea-N",
                    hint="想法种子 ID 必须为 HMW-Idea-N",
                )
            )
    return findings


def check_hmw_tpl_gate_ids(ctx: CheckContext) -> list[Finding]:
    """执行计划 §8 规则 8：HMW-TPL-GATE-01..06 稳定 ID 定义且与 HMW-GATE-XX 区分。"""
    findings: list[Finding] = []
    render_skill = ctx.root / "skills/canvas-render/references/render-contract-hmw.md"
    if not render_skill.is_file():
        return findings
    text = read_text(render_skill)
    missing = [gid for gid in HMW_TPL_GATE_IDS if gid not in text]
    if missing:
        findings.append(
            Finding(
                code="HMW_TPL_GATE_UNIQUE",
                level="error",
                where="skills/canvas-render/references/render-contract-hmw.md",
                message=f"render-contract-hmw.md 缺 Template Gate ID：{', '.join(missing)}",
                hint="HMW-TPL-GATE-01..06 必须在模板结构 profile 中定义",
            )
        )
    return findings


# ---- Journey ---------------------------------------------------------------


def _parse_prefixed_gate_rows(path: Path, gate_re: re.Pattern[str]) -> list[dict[str, str]]:
    """解析 GC / HMW / Journey 这类单画布 Gate 表。"""
    text = read_text(path)
    rows: list[dict[str, str]] = []
    in_table = False
    columns: list[str] = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            in_table = False
            columns = []
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        if not in_table:
            if cells and cells[0].strip().lower() == "id":
                in_table = True
                columns = [c.strip().strip("`").lower() for c in cells]
            continue
        first = cells[0].strip().strip("`")
        if not gate_re.match(first):
            continue
        row: dict[str, str] = {"id": first}
        col_map = {"分类": "category", "风险等级": "risk", "来源": "source"}
        for idx, value in enumerate(cells[1:], start=1):
            if idx >= len(columns):
                continue
            header = columns[idx]
            alias = col_map.get(header, header)
            row[alias] = value.strip().strip("`")
        for key in ("category", "risk", "source"):
            if key not in row:
                row[key] = ""
        rows.append(row)
    return rows


def _table_rows_from_heading(text: str, heading: str) -> list[list[str]]:
    """从 Markdown 指定标题下提取表格数据行。"""
    match = re.search(
        rf"^#{{1,6}}\s*{re.escape(heading)}\s*$\n?(.*?)(?=^#{{1,6}}\s|\Z)",
        text,
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


def _journey_stage_numbers(text: str) -> list[int]:
    numbers: list[int] = []
    for match in re.finditer(r'id="journey-stage-(\d+)"', text):
        numbers.append(int(match.group(1)))
    return numbers


def check_journey_skill_paths(ctx: CheckContext) -> list[Finding]:
    """Journey Skill 路径存在且 frontmatter name 匹配。"""
    findings: list[Finding] = []
    for path, expected in (
        (ctx.root / JOURNEY_DISTILL_SKILL, "journey-distill"),
        (ctx.root / JOURNEY_GATE_SKILL, "journey-gate"),
    ):
        if not path.is_file():
            findings.append(
                Finding(
                    code="JOURNEY_SKILL_PATH",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"缺少 Journey Skill：{path.name}",
                    hint="需按执行计划创建 journey-distill / journey-gate",
                )
            )
            continue
        text = read_text(path)
        if not re.search(rf"^name:\s*{expected}\s*$", text, re.MULTILINE):
            findings.append(
                Finding(
                    code="JOURNEY_SKILL_NAME",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"frontmatter name 应为 {expected}",
                    hint="SKILL.md frontmatter name 必须与目录名一致",
                )
            )
    return findings


def check_journey_gate_table(ctx: CheckContext) -> list[Finding]:
    """Journey Gate 表格可解析，ID/分类/风险/来源合法。"""
    p = ctx.root / JOURNEY_GATE_FILE
    if not p.is_file():
        return [
            Finding(
                code="JOURNEY_GATE_FILE_SET",
                level="error",
                where=JOURNEY_GATE_FILE,
                message="缺少 Journey 闸门策略文件 JOURNEY-gate.md",
                hint="需在 skills/journey-gate/references/JOURNEY-gate.md 写入 6 条放行条件",
            )
        ]
    findings: list[Finding] = []
    rows = _parse_prefixed_gate_rows(p, JOURNEY_GATE_ID_RE)
    if not rows:
        return [
            Finding(
                code="JOURNEY_GATE_TABLE",
                level="error",
                where=JOURNEY_GATE_FILE,
                message="JOURNEY-gate.md 表格无数据行",
                hint="表格需要 6 条放行条件",
            )
        ]
    ids_seen: list[str] = []
    for row in rows:
        gid = row.get("id", "")
        cat = row.get("category", "")
        risk = row.get("risk", "")
        source = row.get("source", "")
        if not JOURNEY_GATE_ID_RE.match(gid):
            findings.append(
                Finding(
                    code="JOURNEY_GATE_ID_FORMAT",
                    level="error",
                    where=JOURNEY_GATE_FILE,
                    message=f"JOURNEY-GATE ID 格式不符：{gid}",
                    hint="JOURNEY-GATE ID 须为 JOURNEY-GATE-01..JOURNEY-GATE-06",
                )
            )
        if cat not in ALLOWED_GATE_CATEGORIES:
            findings.append(
                Finding(
                    code="JOURNEY_GATE_CATEGORY",
                    level="error",
                    where=JOURNEY_GATE_FILE,
                    message=f"JOURNEY-GATE {gid} 分类 {cat!r} 不在白名单 {ALLOWED_GATE_CATEGORIES}",
                    hint="分类必须为 information_integrity 或 business_risk",
                )
            )
        if risk not in ALLOWED_GATE_RISK_LEVELS:
            findings.append(
                Finding(
                    code="JOURNEY_GATE_RISK",
                    level="error",
                    where=JOURNEY_GATE_FILE,
                    message=f"JOURNEY-GATE {gid} 风险等级 {risk!r} 不在白名单 {ALLOWED_GATE_RISK_LEVELS}",
                    hint="风险等级必须为 low / medium / high",
                )
            )
        if not source:
            findings.append(
                Finding(
                    code="JOURNEY_GATE_SOURCE",
                    level="error",
                    where=JOURNEY_GATE_FILE,
                    message=f"JOURNEY-GATE {gid} 来源 ID 为空",
                    hint="每条放行条件必须填写来源 ID",
                )
            )
        ids_seen.append(gid)
    expected_ids = [f"JOURNEY-GATE-{n:02d}" for n in range(1, 7)]
    if sorted(ids_seen) != expected_ids:
        findings.append(
            Finding(
                code="JOURNEY_GATE_COUNT",
                level="error",
                where=JOURNEY_GATE_FILE,
                message=f"JOURNEY-GATE ID 集合 {sorted(ids_seen)} ≠ 期望 {expected_ids}",
                hint="Journey 闸门必须有 6 条放行条件：JOURNEY-GATE-01..06",
            )
        )
    if len(set(ids_seen)) != len(ids_seen):
        findings.append(
            Finding(
                code="JOURNEY_GATE_ID_UNIQUE",
                level="error",
                where=JOURNEY_GATE_FILE,
                message="JOURNEY-GATE ID 重复",
                hint="每个 JOURNEY-GATE-xx ID 必须唯一",
            )
        )
    return findings


def check_journey_render_contract_sync(ctx: CheckContext) -> list[Finding]:
    """Journey render contract、审计脚本、示例模板三者锚点和动态阶段规则一致。"""
    findings: list[Finding] = []
    contract_path = ctx.root / JOURNEY_RENDER_CONTRACT
    template_path = ctx.root / JOURNEY_TEMPLATE_HTML
    audit_path = ctx.root / "skills/canvas-render/scripts/audit_canvas_html.py"
    render_skill = ctx.root / "skills/canvas-render/SKILL.md"
    for path, code, hint in (
        (contract_path, "JOURNEY_RENDER_CONTRACT", "需创建 render-contract-journey.md"),
        (template_path, "JOURNEY_TEMPLATE_MISSING", "需创建 skills/canvas-render/examples/user-journey-canvas.html"),
    ):
        if not path.is_file():
            findings.append(
                Finding(
                    code=code,
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"缺少 {path.name}",
                    hint=hint,
                )
            )
    if not contract_path.is_file() or not template_path.is_file():
        return findings
    contract = read_text(contract_path)
    template = read_text(template_path)
    audit = read_text(audit_path)
    render_text = read_text(render_skill)

    required_anchors = (
        "journey-map",
        "journey-quality",
        *JOURNEY_QUALITY_ANCHORS,
        "quality-panel",
        "quality-version",
        "quality-approval",
        "quality-gaps",
        "quality-risks",
        "quality-caveat",
        "local-notes",
        "canvas-data",
    )
    for anchor in required_anchors:
        for text, where in ((contract, JOURNEY_RENDER_CONTRACT), (template, JOURNEY_TEMPLATE_HTML), (audit, "scripts/audit_canvas_html.py")):
            if anchor not in text:
                findings.append(
                    Finding(
                        code="JOURNEY_ANCHOR_SYNC",
                        level="error",
                        where=where,
                        message=f"缺 Journey 锚点 {anchor}",
                        hint="render contract / 示例模板 / 审计脚本必须共享稳定锚点集合",
                    )
                )

    stage_numbers = sorted(set(_journey_stage_numbers(template)))
    if stage_numbers != [1, 2, 3]:
        findings.append(
            Finding(
                code="JOURNEY_TEMPLATE_STAGE",
                level="error",
                where=JOURNEY_TEMPLATE_HTML,
                message=f"模板阶段编号 {stage_numbers} ≠ [1, 2, 3]",
                hint="示例模板至少包含 3 个连续阶段占位",
            )
        )
    for number in stage_numbers:
        for field_name in JOURNEY_STAGE_FIELDS:
            anchor = f"journey-stage-{number}-{field_name}"
            if anchor not in template:
                findings.append(
                    Finding(
                        code="JOURNEY_TEMPLATE_STAGE_FIELD",
                        level="error",
                        where=JOURNEY_TEMPLATE_HTML,
                        message=f"模板缺阶段子锚点 {anchor}",
                        hint="每个阶段必须包含 action / touchpoint-system / emotion / wait-rework / risk",
                    )
                )
    if '"canvas_type": "journey"' not in template:
        findings.append(
            Finding(
                code="JOURNEY_CANVAS_DATA",
                level="error",
                where=JOURNEY_TEMPLATE_HTML,
                message='模板 canvas-data 缺 "canvas_type": "journey"',
                hint="canvas-data.canvas_type 必须为 journey",
            )
        )
    for field_name in JOURNEY_STAGE_DATA_FIELDS:
        if f'"{field_name}"' not in template:
            findings.append(
                Finding(
                    code="JOURNEY_CANVAS_DATA",
                    level="error",
                    where=JOURNEY_TEMPLATE_HTML,
                    message=f"模板 canvas-data.stages[] 缺字段 {field_name}",
                    hint="canvas-data.stages[] 字段必须与审计脚本一致",
                )
            )
    for gid in JOURNEY_TPL_GATE_IDS:
        if gid not in contract:
            findings.append(
                Finding(
                    code="JOURNEY_TPL_GATE_IDS",
                    level="error",
                    where=JOURNEY_RENDER_CONTRACT,
                    message=f"render-contract-journey.md 缺 Template Gate ID {gid}",
                    hint="JOURNEY-TPL-GATE-01..06 必须在模板结构 profile 中定义",
                )
            )
    if (
        "examples/user-journey-canvas.html" not in render_text
        and "skills/canvas-render/examples/user-journey-canvas.html" not in render_text
    ):
        findings.append(
            Finding(
                code="JOURNEY_RENDER_MAP",
                level="error",
                where="skills/canvas-render/SKILL.md",
                message="canvas-render 示例映射缺 Journey 行",
                hint="在示例映射表补 `journey` → examples/user-journey-canvas.html（skill 内相对）或 skills/canvas-render/examples/user-journey-canvas.html（仓库根相对）",
            )
        )
    if "--type journey" not in render_text:
        findings.append(
            Finding(
                code="JOURNEY_RENDER_AUDIT_CMD",
                level="error",
                where="skills/canvas-render/SKILL.md",
                message="canvas-render 文档缺 Journey 审计命令",
                hint="正式 Journey 审计命令必须包含 --type journey",
            )
        )
    return findings


def check_journey_examples(ctx: CheckContext) -> list[Finding]:
    """Journey 示例模块必须覆盖 Key Points、确认包和 gaps，并保持缺口同源。"""
    findings: list[Finding] = []
    paths = [
        ctx.root / JOURNEY_EXAMPLE_KEYPOINTS,
        ctx.root / JOURNEY_EXAMPLE_PACKAGE,
        ctx.root / JOURNEY_EXAMPLE_GAPS,
    ]
    for path in paths:
        if not path.is_file():
            findings.append(
                Finding(
                    code="JOURNEY_EXAMPLE_MISSING",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"缺少 Journey 示例文件 {path.name}",
                    hint="需补齐 examples/modules/JOURNEY-retail-demo-keypoints.md / JOURNEY-retail-demo-v1.md / JOURNEY-retail-demo-gaps.md",
                )
            )
    package_path = ctx.root / JOURNEY_EXAMPLE_PACKAGE
    if not package_path.is_file():
        return findings
    package = read_text(package_path)
    for section in (
        "### 6. 阶段地图",
        "### 6a. 质量鉴别",
        "### 6b. 痛点与机会",
        "### 7. 结论登记表",
        "### 8. 缺口表",
        "### 9. 推断表",
        "## 12. Gate 与用户决策",
    ):
        if section not in package:
            findings.append(
                Finding(
                    code="JOURNEY_EXAMPLE_SECTION",
                    level="error",
                    where=JOURNEY_EXAMPLE_PACKAGE,
                    message=f"JOURNEY-retail-demo-v1.md 缺 section {section}",
                    hint="确认包示例必须包含 6 / 6a / 6b / 7 / 8 / 9 / 12 节",
                )
            )
    stage_rows = _table_rows_from_heading(package, "6. 阶段地图")
    if len(stage_rows) < 3:
        findings.append(
            Finding(
                code="JOURNEY_EXAMPLE_STAGE",
                level="error",
                where=JOURNEY_EXAMPLE_PACKAGE,
                message=f"阶段地图只有 {len(stage_rows)} 行（期望至少 3）",
                hint="Journey 示例确认包至少包含 3 个动态阶段",
            )
        )
    if package.count("JOURNEY-F") < 1:
        findings.append(
            Finding(
                code="JOURNEY_EXAMPLE_FRICTION",
                level="error",
                where=JOURNEY_EXAMPLE_PACKAGE,
                message="确认包示例缺 JOURNEY-Fxx 断点 / 机会 ID",
                hint="第 6b 节至少包含 1 条痛点或机会",
            )
        )
    for key in JOURNEY_QUALITY_KEYS:
        if key not in package:
            findings.append(
                Finding(
                    code="JOURNEY_EXAMPLE_QUALITY",
                    level="error",
                    where=JOURNEY_EXAMPLE_PACKAGE,
                    message=f"确认包示例缺质量维度 {key}",
                    hint="第 6a 节必须包含 4 个质量鉴别维度",
                )
            )
    for token, code, hint in (
        ("JOURNEY-C", "JOURNEY_EXAMPLE_IDS", "结论 ID 使用 JOURNEY-Cxx"),
        ("JOURNEY-G", "JOURNEY_EXAMPLE_IDS", "缺口 ID 使用 JOURNEY-Gxx"),
        ("JOURNEY-Inf", "JOURNEY_EXAMPLE_IDS", "推断 ID 使用 JOURNEY-Infxx"),
    ):
        if token not in package:
            findings.append(
                Finding(
                    code=code,
                    level="error",
                    where=JOURNEY_EXAMPLE_PACKAGE,
                    message=f"确认包示例缺 {token} ID",
                    hint=hint,
                )
            )

    gaps_path = ctx.root / JOURNEY_EXAMPLE_GAPS
    if gaps_path.is_file():
        gaps = read_text(gaps_path)
        package_gap_ids = set(re.findall(r"JOURNEY-G\d+", package))
        gaps_ids = set(re.findall(r"JOURNEY-G\d+", gaps))
        if gaps_ids and not gaps_ids.issubset(package_gap_ids):
            findings.append(
                Finding(
                    code="JOURNEY_GAPS_SYNC",
                    level="error",
                    where=JOURNEY_EXAMPLE_GAPS,
                    message=f"JOURNEY-retail-demo-gaps.md 缺口 ID {sorted(gaps_ids)} 未全部出现在确认包第 8 节 {sorted(package_gap_ids)}",
                    hint="JOURNEY-retail-demo-gaps.md 与确认包第 8 节缺口表必须同源",
                )
            )
    return findings


def check_journey_no_seven_elements(ctx: CheckContext) -> list[Finding]:
    """Journey 主表不得被定义为七要素。"""
    findings: list[Finding] = []
    scan = [
        ctx.root / JOURNEY_FRAME,
        ctx.root / JOURNEY_SPEC,
        ctx.root / JOURNEY_RENDER_CONTRACT,
        ctx.root / JOURNEY_TEMPLATE_HTML,
        ctx.root / JOURNEY_EXAMPLE_PACKAGE,
    ]
    for path in scan:
        if not path.is_file():
            continue
        text = read_text(path)
        if "七要素" not in text:
            continue
        lines = text.splitlines()
        for lineno, line in enumerate(lines, 1):
            if "七要素" not in line:
                continue
            window = "\n".join(lines[max(0, lineno - 2) : lineno + 2])
            if any(word in window for word in ("不得", "不把", "不要", "禁止", "非", "不作为", "不是")):
                continue
            findings.append(
                Finding(
                    code="JOURNEY_SEVEN_ELEMENTS",
                    level="warning",
                    where=f"{path.relative_to(ctx.root)}:{lineno}",
                    message="Journey 文件出现七要素表述，需人工确认是否误把主表定义为七要素",
                    hint="Journey 正式主表必须是动态阶段 × 5 行合并结构",
                )
            )
    return findings


# ---- 视觉模式 -------------------------------------------------------------


