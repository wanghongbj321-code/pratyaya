"""Phase A and shared gate-table consistency checks."""

from __future__ import annotations

from .models import *  # noqa: F403


def _ensure_plugin(ctx: CheckContext) -> None:
    """按需加载 plugin.json；用于让单条规则在被独立执行时也能工作。"""
    if ctx.plugin:
        return
    path = ctx.root / PLUGIN_JSON
    if not path.is_file():
        return
    try:
        ctx.plugin = json.loads(read_text(path))
        ctx.plugin_path = path
    except json.JSONDecodeError:
        pass


def check_manifest_json(ctx: CheckContext) -> list[Finding]:
    plugin_path = ctx.root / PLUGIN_JSON
    ctx.plugin_path = plugin_path
    if not plugin_path.is_file():
        return [
            Finding(
                code="MANIFEST_JSON",
                level="error",
                where=PLUGIN_JSON,
                message="缺少 plugin.json 清单文件",
                hint="需创建 .codebuddy-plugin/plugin.json",
            )
        ]
    text = read_text(plugin_path)
    try:
        ctx.plugin = json.loads(text)
    except json.JSONDecodeError as exc:
        return [
            Finding(
                code="MANIFEST_JSON",
                level="error",
                where=PLUGIN_JSON,
                message=f"plugin.json 不是合法 JSON：{exc.msg} (line {exc.lineno})",
                hint="修正 JSON 语法",
            )
        ]
    return []


def check_identity_match(ctx: CheckContext) -> list[Finding]:
    """plugin.json 的 name / agentName / displayName 之间的派生关系。"""
    if not ctx.plugin:
        return []
    findings: list[Finding] = []
    name = ctx.plugin.get("name")
    agent_name = ctx.plugin.get("agentName")
    display_name = ctx.plugin.get("displayName")
    if not name:
        findings.append(
            Finding(
                code="IDENTITY_MATCH",
                level="error",
                where=PLUGIN_JSON,
                message="plugin.json 缺 name 字段",
                hint="name 为专家包唯一标识（kebab-case）",
            )
        )
    if not agent_name:
        findings.append(
            Finding(
                code="IDENTITY_MATCH",
                level="error",
                where=PLUGIN_JSON,
                message="plugin.json 缺 agentName 字段",
                hint="agentName 应等于 agents/{name}.md 的文件名",
            )
        )
    elif name and agent_name and name != agent_name:
        findings.append(
            Finding(
                code="IDENTITY_MATCH",
                level="error",
                where=PLUGIN_JSON,
                message=f"name={name!r} 与 agentName={agent_name!r} 不一致",
                hint="name 与 agentName 应严格相等（开发指导 §10.3）",
            )
        )
    if not display_name:
        findings.append(
            Finding(
                code="IDENTITY_MATCH",
                level="warning",
                where=PLUGIN_JSON,
                message="plugin.json 缺 displayName 字段",
                hint="WorkBuddy 显示名应由 plugin.json 统一提供",
            )
        )
    return findings


def check_entry_exists(ctx: CheckContext) -> list[Finding]:
    """主 Agent MD 文件存在性。"""
    if not ctx.plugin:
        return []
    name = ctx.plugin.get("name") or ctx.plugin.get("agentName")
    if not name:
        return []  # 已由 IDENTITY_MATCH 报错
    agent_path = ctx.root / AGENTS_DIR / f"{name}.md"
    if not agent_path.is_file():
        return [
            Finding(
                code="ENTRY_EXISTS",
                level="error",
                where=str(agent_path.relative_to(ctx.root)),
                message=f"主 Agent 文件 {name}.md 不存在",
                hint="需创建 agents/{name}.md（与 plugin.json agentName 一致）",
            )
        ]
    return []


def check_agent_entry(ctx: CheckContext) -> list[Finding]:
    """主 Agent MD frontmatter 必须有 name + description。"""
    if not ctx.plugin:
        return []
    name = ctx.plugin.get("name") or ctx.plugin.get("agentName")
    if not name:
        return []
    agent_path = ctx.root / AGENTS_DIR / f"{name}.md"
    if not agent_path.is_file():
        return []
    text = read_text(agent_path)
    fm, _ = parse_frontmatter(text)
    findings: list[Finding] = []
    if not fm.get("name"):
        findings.append(
            Finding(
                code="AGENT_ENTRY",
                level="error",
                where=str(agent_path.relative_to(ctx.root)),
                message="主 Agent frontmatter 缺 name 字段",
                hint="frontmatter 必填 name 与 description",
            )
        )
    if not fm.get("description"):
        findings.append(
            Finding(
                code="AGENT_ENTRY",
                level="error",
                where=str(agent_path.relative_to(ctx.root)),
                message="主 Agent frontmatter 缺 description 字段",
                hint="frontmatter 必填 name 与 description",
            )
        )
    return findings


def check_skill_entry(ctx: CheckContext) -> list[Finding]:
    """主 Agent MD 中声明的 Skill 路径必须真实存在。"""
    if not ctx.plugin:
        return []
    name = ctx.plugin.get("name") or ctx.plugin.get("agentName")
    if not name:
        return []
    agent_path = ctx.root / AGENTS_DIR / f"{name}.md"
    if not agent_path.is_file():
        return []
    text = read_text(agent_path)
    findings: list[Finding] = []
    # 匹配 skills/<name>/SKILL.md 与 skills/<name>/references/...
    pattern = re.compile(r"skills/([a-z0-9][a-z0-9\-]*)/SKILL\.md")
    skill_names: list[str] = sorted(set(pattern.findall(text)))
    for skill_name in skill_names:
        skill_path = ctx.root / SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_path.is_file():
            findings.append(
                Finding(
                    code="SKILL_ENTRY",
                    level="error",
                    where=str(agent_path.relative_to(ctx.root)),
                    message=f"主 Agent 引用了 skills/{skill_name}/SKILL.md，但文件不存在",
                    hint="在 skills/<name>/ 下补齐 SKILL.md",
                )
            )
    return findings


def check_version_format(ctx: CheckContext) -> list[Finding]:
    if not ctx.plugin:
        return []
    version = ctx.plugin.get("version")
    if not version:
        return [
            Finding(
                code="VERSION_FORMAT",
                level="error",
                where=PLUGIN_JSON,
                message="plugin.json 缺 version 字段",
                hint="version 必须为 SemVer（如 1.0.0）",
            )
        ]
    if not SEMVER_RE.match(str(version)):
        return [
            Finding(
                code="VERSION_FORMAT",
                level="error",
                where=PLUGIN_JSON,
                message=f"plugin.json version={version!r} 不是合法 SemVer",
                hint="version 必须为 SemVer（如 1.0.0）",
            )
        ]
    return []


def check_changelog_version(ctx: CheckContext) -> list[Finding]:
    """CHANGELOG.md 必须包含一个与 plugin.json version 一致的标题行。"""
    if not ctx.plugin:
        return []
    plugin_version = str(ctx.plugin.get("version", ""))
    if not plugin_version:
        return []
    path = ctx.root / "CHANGELOG.md"
    if not path.is_file():
        return [
            Finding(
                code="CHANGELOG_VERSION",
                level="error",
                where="CHANGELOG.md",
                message="缺少 CHANGELOG.md",
                hint="需维护 CHANGELOG.md，并在首条记录当前版本",
            )
        ]
    text = read_text(path)
    # 同时支持 ## v1.0.0 与 ## [v1.0.0] - 2026-08-01 两种格式
    headings = re.findall(r"^##\s+\[?v?(\d+\.\d+\.\d+[^\s\]]*)", text, re.M)
    if not headings:
        return [
            Finding(
                code="CHANGELOG_VERSION",
                level="error",
                where="CHANGELOG.md",
                message="CHANGELOG.md 缺少 ## vX.Y.Z 形式的版本标题",
                hint="为每个发布版本添加 ## vX.Y.Z 标题（或 ## [vX.Y.Z] - 日期）",
            )
        ]
    if plugin_version not in headings:
        return [
            Finding(
                code="CHANGELOG_VERSION",
                level="error",
                where="CHANGELOG.md",
                message=f"CHANGELOG 标题版本 {headings} 不含 plugin.json 的 {plugin_version}",
                hint=f"在 CHANGELOG.md 添加 ## [v{plugin_version}] 段",
            )
        ]
    return []


# ---- Gate 文件 ------------------------------------------------------------


def _parse_gate_file(path: Path, id_re: "re.Pattern[str]" = GATE_ID_RE) -> list[dict[str, str]]:
    """解析 Mx-gate.md 中的 GATE 表格，输出每行字典。

    支持两种列格式（按表头识别）：
    * 设计 8 列：| ID | 检查项 | 结果 | 分类 | 风险等级 | 来源 ID | 影响 | 建议 |
    * 实际 5 列：| ID | 条件 | 分类 | 风险等级 | 来源 |
    """
    text = read_text(path)
    rows: list[dict[str, str]] = []
    in_table = False
    columns: list[str] = []
    column_alias: dict[str, str] = {
        "id": "id",
        "检查项": "check",
        "条件": "check",
        "结果": "result",
        "分类": "category",
        "风险等级": "risk",
        "risk": "risk",
        "来源": "source",
        "来源 id": "source",
        "影响": "impact",
        "建议": "advice",
    }
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            in_table = False
            columns = []
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        # 跳过分隔行
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        if not in_table:
            # 必须是 ID 列表头才视为 GATE 表
            if cells and cells[0].strip().lower() == "id":
                in_table = True
                columns = [c.strip().strip("`").lower() for c in cells]
            continue
        first = cells[0].strip().strip("`")
        if not id_re.match(first):
            continue
        row: dict[str, str] = {"id": first}
        for idx, value in enumerate(cells[1:], start=1):
            if idx >= len(columns):
                continue
            header = columns[idx]
            alias = column_alias.get(header, header)
            row[alias] = value.strip().strip("`")
        for key in ("category", "risk", "source"):
            if key not in row:
                row[key] = ""  # 兜底，确保下游按固定 key 取值
        rows.append(row)
    return rows


def check_gate_file_set(ctx: CheckContext) -> list[Finding]:
    """M1-M6 闸门策略文件必须齐全。"""
    findings: list[Finding] = []
    base = ctx.root / GATE_REFERENCES_DIR
    if not base.is_dir():
        return [
            Finding(
                code="GATE_FILE_SET",
                level="error",
                where=GATE_REFERENCES_DIR,
                message="缺少 module-conclusion-gate references 目录",
                hint="需在 skills/module-conclusion-gate/references/ 下放 M1-gate.md..M6-gate.md",
            )
        ]
    for n in range(1, 7):
        path = base / f"M{n}-gate.md"
        if not path.is_file():
            findings.append(
                Finding(
                    code="GATE_FILE_SET",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"缺少 M{n} 闸门策略文件 M{n}-gate.md",
                    hint="补齐 references/M{n}-gate.md",
                )
            )
    return findings


def _iter_gate_rows(ctx: CheckContext) -> list[tuple[Path, dict[str, str]]]:
    out: list[tuple[Path, dict[str, str]]] = []
    base = ctx.root / GATE_REFERENCES_DIR
    if not base.is_dir():
        return out
    for path in sorted(base.glob("M?-gate.md")):
        for row in _parse_gate_file(path):
            out.append((path, row))
    return out


def check_gate_table_parse(ctx: CheckContext) -> list[Finding]:
    """每个 Mx-gate.md 必须至少解析出一行；解析失败给出明确位置。"""
    findings: list[Finding] = []
    base = ctx.root / GATE_REFERENCES_DIR
    if not base.is_dir():
        return findings
    for path in sorted(base.glob("M?-gate.md")):
        rows = _parse_gate_file(path)
        if not rows:
            findings.append(
                Finding(
                    code="GATE_TABLE_PARSE",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message="未解析到任何 GATE 表格行（首列必须为 ID，且符合 M<N>-GATE-<NN> 格式）",
                    hint="确认表头首列为 ID 行；行内首列为 M1-GATE-01..M6-GATE-07 形式",
                )
            )
    return findings


def check_gate_table_width(ctx: CheckContext) -> list[Finding]:
    """设计要求 GATE 表格 8 列；当前实现多为 5 列，告警而非阻塞。"""
    findings: list[Finding] = []
    base = ctx.root / GATE_REFERENCES_DIR
    if not base.is_dir():
        return findings
    for path in sorted(base.glob("M?-gate.md")):
        text = read_text(path)
        # 找到首条 ID 行的列数
        for line in text.splitlines():
            if not line.lstrip().startswith("|"):
                continue
            cells = line.strip().strip("|").split("|")
            if not cells:
                continue
            # 跳过表头/分隔/非 ID 行
            if cells[0].strip().strip("`").lower() == "id":
                continue
            if all(set(c) <= {"-", ":", " "} for c in cells):
                continue
            if not GATE_ID_RE.match(cells[0].strip().strip("`")):
                continue
            col_count = len(cells)
            if col_count != 8:
                findings.append(
                    Finding(
                        code="GATE_TABLE_WIDTH",
                        level="warning",
                        where=str(path.relative_to(ctx.root)),
                        message=f"GATE 表行 {col_count} 列（设计 8 列：ID/检查项/结果/分类/风险等级/来源 ID/影响/建议）",
                        hint="补全 结果/影响/建议 三列以对齐设计；或更新设计文档接受 5 列精简版",
                    )
                )
            break
    return findings


def check_gate_id_format(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        if not GATE_ID_RE.match(row["id"]):
            findings.append(
                Finding(
                    code="GATE_ID_FORMAT",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"行 ID {row['id']!r} 不符合 M<N>-GATE-<NN> 格式",
                    hint="稳定 ID 必须为 M1-GATE-01..M6-GATE-07 形式",
                )
            )
    return findings


def check_gate_id_module(ctx: CheckContext) -> list[Finding]:
    """每个 ID 的 M{N} 前缀必须与所在文件名一致。"""
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        match = GATE_ID_RE.match(row["id"])
        if not match:
            continue
        id_module = int(match.group(1))
        file_module = int(path.stem.split("-")[0][1:])  # "M1-gate" -> 1
        if id_module != file_module:
            findings.append(
                Finding(
                    code="GATE_ID_MODULE",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"ID {row['id']} 的模块号 {id_module} 与文件模块号 {file_module} 不一致",
                    hint="ID 的 M{N} 前缀必须与所在文件名一致",
                )
            )
    return findings


def check_gate_id_unique(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    counter: Counter[str] = Counter()
    location: dict[str, str] = {}
    for path, row in _iter_gate_rows(ctx):
        counter[row["id"]] += 1
        rel = str(path.relative_to(ctx.root))
        _ = location.setdefault(row["id"], rel)
    for gid, count in counter.items():
        if count > 1:
            findings.append(
                Finding(
                    code="GATE_ID_UNIQUE",
                    level="error",
                    where=location[gid],
                    message=f"稳定 ID {gid} 出现 {count} 次",
                    hint="每个 ID 在全 M1–M6 范围内必须唯一",
                )
            )
    return findings


def check_gate_category(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        category = row["category"]
        if category not in ALLOWED_GATE_CATEGORIES:
            findings.append(
                Finding(
                    code="GATE_CATEGORY",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"行 {row['id']} 分类 {category!r} 不在 {sorted(ALLOWED_GATE_CATEGORIES)} 内",
                    hint="分类必须为 information_integrity 或 business_risk",
                )
            )
    return findings


def check_gate_risk(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        risk = row["risk"]
        if risk not in ALLOWED_GATE_RISK_LEVELS:
            findings.append(
                Finding(
                    code="GATE_RISK",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"行 {row['id']} 风险等级 {risk!r} 不在 {sorted(ALLOWED_GATE_RISK_LEVELS)} 内",
                    hint="风险等级必须为 low / medium / high",
                )
            )
    return findings


def check_gate_source(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path, row in _iter_gate_rows(ctx):
        if not row["source"] or row["source"] in {"-", "—", "/"}:
            findings.append(
                Finding(
                    code="GATE_SOURCE",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"行 {row['id']} 缺来源 ID",
                    hint="来源 ID 必填（如 M{N}-Gxx / section 引用）",
                )
            )
    return findings


# ---- MAAU 闸门 -------------------------------------------------------------


def check_maau_gate_table(ctx: CheckContext) -> list[Finding]:
    """MAAU-gate.md 表格可解析，ID/分类/风险/来源合法（独立 MAAU-GATE-* ID 空间）。"""
    findings: list[Finding] = []
    path = ctx.root / MAAU_GATE_FILE
    if not path.is_file():
        findings.append(
            Finding(
                code="MAAU_GATE_FILE",
                level="error",
                where=MAAU_GATE_FILE,
                message="缺少 MAAU 闸门策略文件 MAAU-gate.md",
                hint="补齐 references/MAAU-gate.md（MAAU-GATE-01..09）",
            )
        )
        return findings
    rows = _parse_gate_file(path, MAAU_GATE_ID_RE)
    if not rows:
        findings.append(
            Finding(
                code="MAAU_GATE_PARSE",
                level="error",
                where=MAAU_GATE_FILE,
                message="MAAU-gate.md 未解析到任何 GATE 表格行",
                hint="表头首列为 ID，行内首列为 MAAU-GATE-01..09",
            )
        )
        return findings
    seen: set[str] = set()
    for row in rows:
        gid = row["id"]
        if not MAAU_GATE_ID_RE.match(gid):
            findings.append(
                Finding(
                    code="MAAU_GATE_ID",
                    level="error",
                    where=MAAU_GATE_FILE,
                    message=f"行 ID {gid!r} 不符合 MAAU-GATE-<NN> 格式",
                    hint="MAAU 稳定 ID 必须为 MAAU-GATE-01..09，且不得复用 M1-GATE-* 到 M6-GATE-*",
                )
            )
        if gid in seen:
            findings.append(
                Finding(
                    code="MAAU_GATE_ID",
                    level="error",
                    where=MAAU_GATE_FILE,
                    message=f"稳定 ID {gid} 重复",
                )
            )
        seen.add(gid)
        if row["category"] not in ALLOWED_GATE_CATEGORIES:
            findings.append(
                Finding(
                    code="MAAU_GATE_CATEGORY",
                    level="error",
                    where=MAAU_GATE_FILE,
                    message=f"行 {gid} 分类 {row['category']!r} 不在 {sorted(ALLOWED_GATE_CATEGORIES)} 内",
                )
            )
        if row["risk"] not in ALLOWED_GATE_RISK_LEVELS:
            findings.append(
                Finding(
                    code="MAAU_GATE_RISK",
                    level="error",
                    where=MAAU_GATE_FILE,
                    message=f"行 {gid} 风险等级 {row['risk']!r} 不在 {sorted(ALLOWED_GATE_RISK_LEVELS)} 内",
                )
            )
        if not row["source"] or row["source"] in {"-", "—", "/"}:
            findings.append(
                Finding(
                    code="MAAU_GATE_SOURCE",
                    level="error",
                    where=MAAU_GATE_FILE,
                    message=f"行 {gid} 缺来源 ID",
                )
            )
    return findings


# ---- GC 闸门 ---------------------------------------------------------------



def _iter_gc_gate_path(path: Path) -> Path | None:
    p = path / GC_GATE_FILE
    return p if p.is_file() else None


def check_gc_gate_file_set(ctx: CheckContext) -> list[Finding]:
    """黄金圈闸门策略文件 GC-gate.md 必须存在。"""
    p = ctx.root / GC_GATE_FILE
    if not p.is_file():
        return [
            Finding(
                code="GC_GATE_FILE_SET",
                level="error",
                where=GC_GATE_FILE,
                message="缺少黄金圈闸门策略文件 GC-gate.md",
                hint="需在 skills/gc-gate/references/GC-gate.md 写入 6 条放行条件",
            )
        ]
    return []


def check_gc_gate_table(ctx: CheckContext) -> list[Finding]:
    """GC-gate.md 表格可解析，ID/分类/风险/来源 合法。"""
    findings: list[Finding] = []
    p = ctx.root / GC_GATE_FILE
    if not p.is_file():
        return findings
    text = p.read_text(encoding="utf-8")
    # 直接解析 GC gate 表格（GATE_ID_RE 只匹配 M{N}-GATE-{NN}，不适用）
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
        if not GC_GATE_ID_RE.match(first):
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
                code="GC_GATE_TABLE",
                level="error",
                where=GC_GATE_FILE,
                message="GC-gate.md 表格无数据行",
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
        if not GC_GATE_ID_RE.match(gid):
            findings.append(
                Finding(
                    code="GC_GATE_ID_FORMAT",
                    level="error",
                    where=GC_GATE_FILE,
                    message=f"GC-GATE ID 格式不符：{gid}（期望 GC-GATE-NN）",
                    hint="GC-GATE ID 须为 GC-GATE-01..GC-GATE-06",
                )
            )
        if cat not in ALLOWED_GATE_CATEGORIES:
            findings.append(
                Finding(
                    code="GC_GATE_CATEGORY",
                    level="error",
                    where=GC_GATE_FILE,
                    message=f"GC-GATE {gid} 分类 {cat!r} 不在白名单 {ALLOWED_GATE_CATEGORIES}",
                    hint="分类必须为 information_integrity 或 business_risk",
                )
            )
        if risk not in ALLOWED_GATE_RISK_LEVELS:
            findings.append(
                Finding(
                    code="GC_GATE_RISK",
                    level="error",
                    where=GC_GATE_FILE,
                    message=f"GC-GATE {gid} 风险等级 {risk!r} 不在白名单 {ALLOWED_GATE_RISK_LEVELS}",
                    hint="风险等级必须为 low / medium / high",
                )
            )
        if not source:
            findings.append(
                Finding(
                    code="GC_GATE_SOURCE",
                    level="error",
                    where=GC_GATE_FILE,
                    message=f"GC-GATE {gid} 来源 ID 为空",
                    hint="每条放行条件必须填写来源 ID",
                )
            )
        ids_seen.append(gid)
    if len(ids_seen) != 6:
        findings.append(
            Finding(
                code="GC_GATE_COUNT",
                level="error",
                where=GC_GATE_FILE,
                message=f"GC-GATE 共 {len(ids_seen)} 条（期望 6 条）",
                hint="黄金圈闸门必须有 6 条放行条件：GC-GATE-01..GC-GATE-06",
            )
        )
    if len(set(ids_seen)) != len(ids_seen):
        findings.append(
            Finding(
                code="GC_GATE_ID_UNIQUE",
                level="error",
                where=GC_GATE_FILE,
                message="GC-GATE ID 重复",
                hint="每个 GC-GATE-xx ID 必须唯一",
            )
        )
    return findings


# ---- HMW -------------------------------------------------------------------


