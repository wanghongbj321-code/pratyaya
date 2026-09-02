"""画布注册表解析器单测（v3.3.0 P2 前置 · 提交 3a）。

本文件**只测试解析器本身**，使用内置 fixture 文本，不读取真实 ``agents/pratyaya.md``
——因此在 P2 注册表落地之前即可保持绿灯，落实"先有度量，后有重构"。

针对真实 agent md 的注册表断言将在 P2 完成、注册表落地后启用（提交 3b）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.contract_consistency.canvas_registry import (  # noqa: E402
    BEGIN,
    END,
    by_id,
    parse_canvas_registry,
)

# 内置 fixture：与 §3 注册表同构（8 个画布条目）
FIXTURE = f"""# 主 Agent（fixture）

{BEGIN}

| canvas_id | canvas_type（渲染+HTML） | audit_type（CLI `--type`） | state_key | 文件前缀 | 输出前缀 | distill | gate | Gate ID 前缀 | page_type | 触发问法 |
|---|---|---|---|---|---|---|---|---|---|---|
| mvl | `mvl` | `mvl` | `modules.M1`…`M6` | `M1`…`M6` | `module-N` | `mvl-distill` | `module-conclusion-gate` | `M{{N}}-GATE-0N` | `module-detail` | "M1-M6 六模块管线" |
| maau | `mvl` | `mvl` | `maau.{{slug}}` | `MAAU` | `maau-global-canvas` | `maau-synthesize` | `module-conclusion-gate` | `MAAU-GATE-` | `global` | "用这份逐字稿生成 MAAU" |
| gc | `golden-circle` | `gc` | `golden_circle.{{slug}}` | `GC` | `gc` | `gc-distill` | `gc-gate` | `GC-GATE-` | `golden-circle-index` | "黄金圈" |
| hmw | `hmw` | `hmw` | `hmw.{{slug}}` | `HMW` | `hmw` | `hmw-distill` | `hmw-gate` | `HMW-GATE-` | `hmw-index` | "HMW" |
| persona | `persona` | `persona` | `persona.{{slug}}` | `PERSONA` | `persona` | `persona-distill` | `persona-gate` | `PERSONA-GATE-` | `persona-index` | "用户画像" |
| journey | `journey` | `journey` | `journey.{{slug}}` | `JOURNEY` | `journey` | `journey-distill` | `journey-gate` | `JOURNEY-GATE-` | `journey-index` | "用户旅程" |
| v2c-vac | `v2c-vac` | `v2c-vac` | `v2c_vac.{{slug}}` | `V2C-VAC` | `v2c-vac` | `v2c-vac-distill` | `v2c-vac-gate` | `V2C-GATE-` | `v2c-vac-index` | "V2C" / "价值归因" |
| 5w | `5w` | `5w` | `five_whys.{{slug}}` | `5W` | `5w` | `5w-distill` | `5w-gate` | `5W-GATE-` | `5w-index` | "5W" / "根因分析" |

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
