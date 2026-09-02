"""画布注册表解析器单测（v3.3.0 P2 前置 · 提交 3a）。

本文件**只测试解析器本身**，使用内置 fixture 文本，不读取真实 ``agents/pratyaya.md``
——因此在 P2 注册表落地之前即可保持绿灯，落实"先有度量，后有重构"。

针对真实 agent md 的注册表断言将在 P2 完成、注册表落地后启用（提交 3b）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# §7.6 依赖边界：audit_core 的 --type choices 从 skills._engine.canvas_registry 读取。
# 此处把 canvas_audit 包所在目录加入 sys.path，以便交叉断言直接调用 `_audit_type_choices()`。
_CANVAS_AUDIT_DIR = REPO_ROOT / "skills" / "canvas-render" / "scripts"
if str(_CANVAS_AUDIT_DIR) not in sys.path:
    sys.path.insert(0, str(_CANVAS_AUDIT_DIR))

from scripts.contract_consistency.canvas_registry import (  # noqa: E402
    BEGIN,
    END,
    by_id,
    parse_canvas_registry,
)

# 内置 fixture：与 §3 注册表同构（8 个画布条目）
FIXTURE = f"""# 主 Agent（fixture）

{BEGIN}

| canvas_id | canvas_type（渲染+HTML） | audit_type（CLI `--type`） | state_key | 文件前缀 | 输出前缀 | distill | gate | Gate ID 前缀 | page_type | 示例模板 | 触发问法 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mvl | `mvl` | `mvl` | `modules.M1`…`M6` | `M1`…`M6` | `module-N` | `mvl-distill` | `module-conclusion-gate` | `M{{N}}-GATE-0N` | `module-detail` | `mvl-canvas/module-N-canvas.html` | "M1-M6 六模块管线" |
| maau | `mvl` | `mvl` | `maau.{{slug}}` | `MAAU` | `maau-global-canvas` | `maau-synthesize` | `module-conclusion-gate` | `MAAU-GATE-` | `global` | `mvl-canvas/maau-global-canvas.html` | "用这份逐字稿生成 MAAU" |
| gc | `golden-circle` | `gc` | `golden_circle.{{slug}}` | `GC` | `gc` | `gc-distill` | `gc-gate` | `GC-GATE-` | `golden-circle-index` | `goden-circle-canvas.html` | "黄金圈" |
| hmw | `hmw` | `hmw` | `hmw.{{slug}}` | `HMW` | `hmw` | `hmw-distill` | `hmw-gate` | `HMW-GATE-` | `hmw-index` | `hmw-canvas.html` | "HMW" |
| persona | `persona` | `persona` | `persona.{{slug}}` | `PERSONA` | `persona` | `persona-distill` | `persona-gate` | `PERSONA-GATE-` | `persona-index` | `user-persona-canvas.html` | "用户画像" |
| journey | `journey` | `journey` | `journey.{{slug}}` | `JOURNEY` | `journey` | `journey-distill` | `journey-gate` | `JOURNEY-GATE-` | `journey-index` | `user-journey-canvas.html` | "用户旅程" |
| v2c-vac | `v2c-vac` | `v2c-vac` | `v2c_vac.{{slug}}` | `V2C-VAC` | `v2c-vac` | `v2c-vac-distill` | `v2c-vac-gate` | `V2C-GATE-` | `v2c-vac-index` | `v2c-value-attribution-canvas.html` | "V2C" / "价值归因" |
| 5w | `5w` | `5w` | `five_whys.{{slug}}` | `5W` | `5w` | `5w-distill` | `5w-gate` | `5W-GATE-` | `5w-index` | `5w-canvas.html` | "5W" / "根因分析" |

{END}

## 后续正文

正文不应被解析为注册表行。
"""

REQUIRED_FIELDS = (
    "canvas_type",
    "audit_type",
    "state_key",
    "file_prefix",
    "output_prefix",
    "distill",
    "gate",
    "gate_id_prefix",
    "page_type",
    "template",
)


def test_parse_returns_all_eight_canvases_in_order() -> None:
    rows = parse_canvas_registry(FIXTURE)
    assert [r.canvas_id for r in rows] == [
        "mvl",
        "maau",
        "gc",
        "hmw",
        "persona",
        "journey",
        "v2c-vac",
        "5w",
    ]


def test_parse_strips_markdown_backticks() -> None:
    gc = by_id(parse_canvas_registry(FIXTURE), "gc")
    assert gc is not None
    assert gc.canvas_type == "golden-circle"
    assert gc.audit_type == "gc"
    assert "`" not in gc.state_key
    assert "`" not in gc.gate_id_prefix


def test_gc_is_the_only_canvas_with_split_types() -> None:
    """§3 实施红线：GC 是唯一 canvas_type != audit_type 的画布。"""
    rows = parse_canvas_registry(FIXTURE)
    assert [r.canvas_id for r in rows if r.canvas_type != r.audit_type] == ["gc"]


def test_maau_shares_audit_type_with_mvl() -> None:
    """§3 O-5：MAAU 与 MVL 共用 canvas_type / audit_type，靠 canvas_id 区分。"""
    rows = parse_canvas_registry(FIXTURE)
    # 按 audit_type 去重后只剩 7 种——这正是双集合断言存在的理由（§8.3）
    assert {r.audit_type for r in rows} == {
        "mvl",
        "gc",
        "hmw",
        "persona",
        "journey",
        "v2c-vac",
        "5w",
    }
    maau = by_id(rows, "maau")
    assert maau is not None
    assert maau.canvas_type == "mvl"
    assert maau.audit_type == "mvl"


@pytest.mark.parametrize(
    "canvas_id",
    ["mvl", "maau", "gc", "hmw", "persona", "journey", "v2c-vac", "5w"],
)
def test_each_row_has_all_required_fields(canvas_id: str) -> None:
    row = by_id(parse_canvas_registry(FIXTURE), canvas_id)
    assert row is not None, f"注册表缺少 {canvas_id}"
    for field in REQUIRED_FIELDS:
        assert row.value(field), f"{canvas_id}.{field} 为空"


def test_content_outside_markers_is_ignored() -> None:
    """标记块之外的表格不应被误解析。"""
    rows = parse_canvas_registry(FIXTURE)
    assert all(r.canvas_id for r in rows)
    assert len(rows) == 8


def test_missing_markers_returns_empty() -> None:
    assert parse_canvas_registry("# 无注册表\n\n正文。\n") == []


def test_unclosed_marker_returns_empty() -> None:
    assert parse_canvas_registry(f"{BEGIN}\n\n| a | b |\n|---|---|\n") == []


def test_reversed_markers_returns_empty() -> None:
    assert parse_canvas_registry(f"{END}\n| a |\n{BEGIN}") == []


def test_by_id_missing_returns_none() -> None:
    assert by_id(parse_canvas_registry(FIXTURE), "not-a-canvas") is None


# ---------------------------------------------------------------------------
# 针对真实 agents/pratyaya.md 的注册表断言（P2 注册表落地后启用 · 提交 3b）
# ---------------------------------------------------------------------------

AGENT_MD = REPO_ROOT / "agents" / "pratyaya.md"
GC_EXAMPLE = REPO_ROOT / "skills/canvas-render" / "examples" / "goden-circle-canvas.html"
STATE_SCHEMA = REPO_ROOT / "schemas" / "state.schema.json"
PLUGIN_JSON = REPO_ROOT / ".codebuddy-plugin" / "plugin.json"

EXPECTED_CANVAS_IDS = {
    "mvl",
    "maau",
    "gc",
    "hmw",
    "persona",
    "journey",
    "v2c-vac",
    "5w",
}

# 画布区块顶层键（schema properties 中属于画布的部分，排除元数据键）。
CANVAS_SCHEMA_BLOCKS = {
    "modules",
    "maau",
    "golden_circle",
    "hmw",
    "persona",
    "journey",
    "v2c_vac",
    "five_whys",
}
# 需从 schema 顶层排除的元数据键（注册表 state_key root 不覆盖它们）。
SCHEMA_META_KEYS = {
    "schema_version",
    "project_slug",
    "project_name",
    "group_id",
    "topic_slug",
    "topic_name",
    "current_module",
    "_meta",
    "updated_at",
}


def _real_rows():
    return parse_canvas_registry(AGENT_MD.read_text(encoding="utf-8"))


def test_real_registry_has_all_eight_canvases() -> None:
    """① 按画布条目断言 8 个（MAAU 与 MVL 是两个条目）。"""
    assert {r.canvas_id for r in _real_rows()} == EXPECTED_CANVAS_IDS


def test_real_registry_audit_types_are_seven() -> None:
    """② 按审计类型断言 7 种（MAAU 复用 mvl，故比 ① 少一个）。

    ①② 双断言缺一不可：只用 canvas_type 做集合断言时，MAAU 会被去重掉，
    8 个条目只能证出 7 种，测试通过但注册表其实漏了 MAAU（§8.3 R1）。
    """
    assert {r.audit_type for r in _real_rows()} == {
        "mvl", "gc", "hmw", "persona", "journey", "v2c-vac", "5w",
    }


def test_registry_matches_audit_choices() -> None:
    """§8.3 交叉断言：注册表 audit_type 集合 == audit CLI `--type` choices。

    P4 后 `audit_core._audit_type_choices()` 从 `skills._engine.canvas_registry`
    读取（§7.6），此处直接调用 audit 侧函数，锁定「注册表 = audit 合法集」单一事实源。
    """
    from canvas_audit.audit_core import _audit_type_choices

    assert {r.audit_type for r in _real_rows()} == set(_audit_type_choices())


def test_registry_matches_state_schema() -> None:
    """§8.3 交叉断言：注册表 state_key 顶层区块名 ⊆ schema 顶层属性。

    每个画布条目的 state_key root（如 golden_circle.{slug} → golden_circle）必须
    是 state.schema.json 的顶层属性，且画布区块集合与 schema 完全一致。
    """
    schema = json.loads(STATE_SCHEMA.read_text(encoding="utf-8"))
    schema_blocks = set(schema["properties"]) - SCHEMA_META_KEYS
    rows = _real_rows()

    registry_roots = {r.state_key.split(".", 1)[0] for r in rows}
    assert registry_roots == CANVAS_SCHEMA_BLOCKS
    assert registry_roots == schema_blocks, (
        f"注册表 state_key root {sorted(registry_roots)} 与 schema 画布区块 "
        f"{sorted(schema_blocks)} 不一致"
    )


def test_registry_skills_declared_in_plugin() -> None:
    """§8.3 交叉断言：每个条目的 distill / gate skill 都在 plugin.json skills 数组。

    替代 test_contract_consistency.py 中按画布硬编码的 EXPECTED_*_SKILLS——
    从注册表推导，防止某画布新增 skill 后漏声明。
    """
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    declared = {p.removeprefix("./skills/") for p in plugin["skills"]}
    rows = _real_rows()

    assert len(rows) == 8
    for r in rows:
        assert r.distill in declared, f"{r.canvas_id}.distill={r.distill} 未在 plugin.json skills 声明"
        assert r.gate in declared, f"{r.canvas_id}.gate={r.gate} 未在 plugin.json skills 声明"


def test_real_registry_maau_shares_mvl_types() -> None:
    """③ MAAU 靠 canvas_id 与 generation_path 与 MVL 区分。"""
    maau = by_id(_real_rows(), "maau")
    assert maau is not None
    assert maau.canvas_type == "mvl"
    assert maau.audit_type == "mvl"


def test_real_registry_gc_keeps_split_types() -> None:
    """④ GC 是唯一 canvas_type != audit_type 的画布（§3 实施红线）。"""
    rows = _real_rows()
    gc = by_id(rows, "gc")
    assert gc is not None
    assert gc.canvas_type == "golden-circle"
    assert gc.audit_type == "gc"
    assert [r.canvas_id for r in rows if r.canvas_type != r.audit_type] == ["gc"]


def test_real_gc_example_html_canvas_type_is_golden_circle() -> None:
    """防实施者把 audit_type=gc 误写进 HTML `canvas-data.canvas_type`（§11 R9）。"""
    assert '"canvas_type": "golden-circle"' in GC_EXAMPLE.read_text(encoding="utf-8")


@pytest.mark.parametrize("canvas_id", sorted(EXPECTED_CANVAS_IDS))
def test_real_registry_each_row_complete(canvas_id: str) -> None:
    row = by_id(_real_rows(), canvas_id)
    assert row is not None, f"真实注册表缺少 {canvas_id}"
    for field in REQUIRED_FIELDS:
        assert row.value(field), f"{canvas_id}.{field} 为空"
