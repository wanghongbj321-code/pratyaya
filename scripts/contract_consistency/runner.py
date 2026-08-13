"""Command-line runner for pratyaya contract consistency checks."""

from __future__ import annotations

from .models import *  # noqa: F403
from .phase_a import *  # noqa: F403
from .phase_a import _ensure_plugin
from .canvas_checks import *  # noqa: F403
from .patterns import *  # noqa: F403
from .sync_checks import *  # noqa: F403
from .v2c_vac_checks import *  # noqa: F403


@dataclass(frozen=True)
class Rule:
    code: str
    category: str  # "A" | "B"
    description: str
    runner: Callable[[CheckContext], list[Finding]]


RULES: tuple[Rule, ...] = (
    # Phase A
    Rule("MANIFEST_JSON", "A", "plugin.json 存在且为合法 JSON", check_manifest_json),
    Rule("IDENTITY_MATCH", "A", "plugin.json name / agentName / displayName 派生关系", check_identity_match),
    Rule("ENTRY_EXISTS", "A", "agents/{name}.md 必须存在", check_entry_exists),
    Rule("AGENT_ENTRY", "A", "主 Agent frontmatter 必填 name + description", check_agent_entry),
    Rule("SKILL_ENTRY", "A", "主 Agent 引用的 skills/*/SKILL.md 必须存在", check_skill_entry),
    Rule("VERSION_FORMAT", "A", "plugin.json version 必须为 SemVer", check_version_format),
    Rule("CHANGELOG_VERSION", "A", "CHANGELOG.md 必含当前版本标题", check_changelog_version),
    Rule("GATE_FILE_SET", "A", "M1-M6 闸门策略文件齐全", check_gate_file_set),
    Rule("MAAU_GATE_TABLE", "A", "MAAU-gate.md 表格可解析且 ID/分类/风险/来源合法", check_maau_gate_table),
    Rule("GATE_TABLE_PARSE", "A", "Mx-gate.md 表格可解析", check_gate_table_parse),
    Rule("GATE_TABLE_WIDTH", "A", "Mx-gate.md 表格列数（正式 5 列，兼容 8 列）", check_gate_table_width),
    Rule("GATE_ID_FORMAT", "A", "GATE ID 格式 M{N}-GATE-{NN}", check_gate_id_format),
    Rule("GATE_ID_MODULE", "A", "GATE ID 模块号与文件名一致", check_gate_id_module),
    Rule("GATE_ID_UNIQUE", "A", "GATE ID 全 M1-M6 唯一", check_gate_id_unique),
    Rule("GATE_CATEGORY", "A", "GATE 分类在白名单内", check_gate_category),
    Rule("GATE_RISK", "A", "GATE 风险等级在白名单内", check_gate_risk),
    Rule("GATE_SOURCE", "A", "GATE 来源 ID 必填", check_gate_source),
    Rule("GC_GATE_FILE_SET", "A", "黄金圈闸门策略文件 GC-gate.md 存在", check_gc_gate_file_set),
    Rule("GC_GATE_TABLE", "A", "GC-gate.md 表格可解析 + ID/分类/风险/来源合法", check_gc_gate_table),
    Rule("PATTERN_COUNT", "A", "视觉模式文件数 = 当前基线（10）", check_pattern_count),
    Rule("PATTERN_FILENAME", "A", "视觉模式文件名 NN-id.md", check_pattern_filename),
    Rule("PATTERN_SEQUENCE", "A", "视觉模式序号 01..10", check_pattern_sequence),
    Rule("PATTERN_ID", "A", "视觉模式 frontmatter id 与文件名一致", check_pattern_id),
    Rule("PATTERN_METADATA", "A", "视觉模式 frontmatter 字段完整", check_pattern_metadata),
    Rule("PATTERN_ENUM", "A", "视觉模式 layout/formality/density 取值在白名单内", check_pattern_enum),
    Rule("LOCAL_LINK", "A", "Markdown 本地链接目标存在", check_local_link),
    Rule("DEPRECATED_TERM", "A", "文档不得出现废弃术语（除非显式说明废弃）", check_deprecated_term),
    # Phase B
    Rule("GATE_SECTION_SYNC", "B", "闸门文件必填 section ⊆ workshop-canvas-map", check_gate_section_sync),
    Rule("RENDER_SECTION_SYNC", "B", "render-contract.md 锚点与 audit 脚本一致", check_render_section_sync),
    Rule("SKILL_TEMPLATE_SYNC", "B", "examples 模板 section 与 workshop-canvas-map 一致", check_template_skill_sync),
    Rule("STATE_ENUM_SYNC", "B", "权威文档状态值在 5 态白名单内", check_state_enum),
    Rule("AUTH_FIELDS", "B", "schema 必含 4 个授权字段", check_auth_fields),
    Rule("OVERRIDE_CATEGORY", "B", "override_audit.items.category enum ⊆ {business_risk}", check_override_category),
    # HMW（执行计划 §8）
    Rule("HMW_SKILL_PATH", "A", "HMW Skill 路径存在且 frontmatter name 匹配", check_hmw_skill_paths),
    Rule("HMW_GATE_FILE_SET", "A", "HMW 闸门策略文件 HMW-gate.md 存在且合法", check_hmw_gate_table),
    Rule("HMW_TEMPLATE_MISSING", "A", "HMW 一等公民模板存在且含 8 想法锚点", check_hmw_template_and_anchors),
    Rule("HMW_INF_ID", "A", "HMW 推断 ID 用 HMW-Inf-N（与 HMW-Idea-N 区分）", check_hmw_id_naming),
    Rule("HMW_TPL_GATE_UNIQUE", "B", "HMW-TPL-GATE-01..06 稳定 ID 定义且与 HMW-GATE 区分", check_hmw_tpl_gate_ids),
    # Journey（执行计划 §8）
    Rule("JOURNEY_SKILL_PATH", "A", "Journey Skill 路径存在且 frontmatter name 匹配", check_journey_skill_paths),
    Rule("JOURNEY_GATE_FILE_SET", "A", "Journey 闸门策略文件 JOURNEY-gate.md 存在且合法", check_journey_gate_table),
    Rule("JOURNEY_ANCHOR_SYNC", "B", "Journey render contract / 审计脚本 / 示例模板锚点一致", check_journey_render_contract_sync),
    Rule("JOURNEY_EXAMPLE_MISSING", "A", "Journey 示例模块 Key Points / 确认包 / gaps 齐全", check_journey_examples),
    Rule("JOURNEY_SEVEN_ELEMENTS", "B", "Journey 主表不得定义为七要素", check_journey_no_seven_elements),
    Rule("PERSONA_SKILL_PATH", "A", "Persona Skill、Gate、模板与渲染契约保持一致", check_persona_skill_paths),
    Rule("V2C_VAC_SKILL_PATH", "A", "V2C VAC Skill、spec、Gate、模板与渲染契约文件齐全", check_v2c_vac_skill_paths),
    Rule("V2C_VAC_GATE_FILE", "A", "V2C VAC Gate 表格 ID/分类/风险/来源合法", check_v2c_vac_gate_table),
    Rule("V2C_VAC_RENDER_CONTRACT", "B", "V2C VAC render contract / canvas-render Skill / 示例模板同步", check_v2c_vac_render_contract_sync),
    Rule("V2C_VAC_STATE_SCHEMA", "B", "V2C VAC state schema、主 Agent 路由与 plugin 注册同步", check_v2c_vac_state_schema_and_routing),
)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def run_checks(
    root: Path,
    selected: Sequence[str] | None = None,
    stop_on_error: bool = False,
) -> list[Finding]:
    ctx = CheckContext(root=root.resolve())
    findings: list[Finding] = []
    selected_set: set[str] = set(selected) if selected else set[str]()
    for rule in RULES:
        if selected_set and rule.code not in selected_set:  # pylint: disable=unsupported-membership-test
            continue
        # 注入 plugin（让单条规则在 --rules 过滤时仍可工作）
        _ensure_plugin(ctx)
        try:
            new_findings = rule.runner(ctx)
        except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:  # noqa: BLE001  # 防御：单条规则崩溃不应让整次检查失败
            new_findings = [
                Finding(
                    code=rule.code,
                    level="error",
                    where="<runner>",
                    message=f"规则执行异常：{type(exc).__name__}: {exc}",
                    hint="请将此问题反馈给门禁维护者",
                )
            ]
        findings.extend(new_findings)
        if stop_on_error and any(f.level == "error" for f in new_findings):
            break
    return findings


def render_text(findings: list[Finding]) -> str:
    if not findings:
        return "OK：契约一致性检查全部通过。"
    counts = Counter(f.level for f in findings)
    header = (
        f"契约一致性检查结果：error={counts.get('error', 0)}, "
        f"warning={counts.get('warning', 0)}, info={counts.get('info', 0)}"
    )
    lines = [header, "-" * len(header), ""]
    by_code: dict[str, list[Finding]] = {}
    for f in findings:
        by_code.setdefault(f.code, []).append(f)
    for code in sorted(by_code):
        group = by_code[code]
        lines.append(f"[{group[0].level.upper()}] {code}（{len(group)} 条）")
        for f in group:
            where = f.where or "-"
            lines.append(f"  - {where}: {f.message}")
            if f.hint:
                lines.append(f"      建议：{f.hint}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_json(findings: list[Finding]) -> str:
    return json.dumps(
        {
            "count": len(findings),
            "findings": [f.to_dict() for f in findings],
        },
        ensure_ascii=False,
        indent=2,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pratyaya 契约一致性检查器（阶段 A + 阶段 B）",
    )
    _ = parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        help=f"仓库根目录（默认 {DEFAULT_ROOT}）",
    )
    _ = parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出",
    )
    _ = parser.add_argument(
        "--strict",
        action="store_true",
        help="将 warning 视作 error 退出",
    )
    _ = parser.add_argument(
        "--rules",
        default="",
        help="只跑指定规则（逗号分隔 code）",
    )
    _ = parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有规则后退出",
    )
    args = parser.parse_args(argv)

    list_opt = cast(bool, args.list)
    root_opt = cast(str, args.root)
    json_opt = cast(bool, args.json)
    rules_opt = cast(str, args.rules)
    strict_opt = cast(bool, args.strict)

    if list_opt:
        for rule in RULES:
            print(f"{rule.code}\t{rule.category}\t{rule.description}")
        return 0

    root = Path(root_opt).resolve()
    if not root.is_dir():
        print(f"root 不是有效目录：{root}", file=sys.stderr)
        return 2

    selected = [s.strip() for s in rules_opt.split(",") if s.strip()] or None
    findings = run_checks(root, selected=selected)

    if json_opt:
        print(render_json(findings))
    else:
        print(render_text(findings))

    has_error = any(f.level == "error" for f in findings)
    has_warning = any(f.level == "warning" for f in findings)
    if has_error:
        return 1
    if strict_opt and has_warning:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
