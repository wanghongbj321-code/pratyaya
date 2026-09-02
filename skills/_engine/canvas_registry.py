"""画布注册表 —— 八类画布的唯一参数事实源。

红线（见执行计划 §7.4 / §7.6）：
- 本模块**零副作用、标准库 only**：import 时不得读文件、写日志、发起网络或创建目录。
- 不得 import 任何 audit / render / state 写入模块，只依赖标准库与自身。
- 依赖方向单向：`_engine/canvas_registry` ← `canvas_audit` ← `audit_canvas_html.py`。
- 本模块的 `CANVASES` 是运行时唯一事实源；`agents/pratyaya.md` 的「画布注册表」表格是人读视图，
  二者一致性由 `tests/test_engine/test_canvas_registry.py` 与 `tests/test_contract_consistency.py`
  交叉断言锁定，不由运行时解析。
"""

from __future__ import annotations

from dataclasses import dataclass

# MVL 六模块管线（显式备选路径）的模块序号；仅 mvl 画布使用。
MVL_MODULES: tuple[str, ...] = ("M1", "M2", "M3", "M4", "M5", "M6")

# 8 类画布共有 7 种审计类型（maau 复用 mvl），用于 CLI `--type` choices。
AUDIT_TYPES: tuple[str, ...] = (
    "mvl", "gc", "hmw", "persona", "journey", "v2c-vac", "5w",
)


@dataclass(frozen=True)
class CanvasSpec:
    """单条画布注册项。字段与 `agents/pratyaya.md` 的注册表列一一对应。"""

    canvas_id: str          # 条目唯一键（mvl/maau 是两个条目）
    canvas_type: str        # 渲染输入 + HTML `canvas-data.canvas_type`
    audit_type: str         # 审计 CLI `--type`
    state_key: str          # 实例态路径模板（"maau.{slug}"；mvl 为 "modules.M{N}"）
    file_prefix: str        # 源包 / 产物文件名前缀
    output_prefix: str      # 渲染输出前缀
    distill_skill: str      # 蒸馏 Skill（plugin.json skills 数组成员）
    gate_skill: str         # Gate Skill
    gate_id_prefix: str     # Gate 检查项 ID 前缀（override_audit.assessment_id 用）
    page_type: str          # 索引页 `--page-type`
    template: str           # 示例模板仓库相对路径
    generation_path: str | None = None   # 固定生成路径；None 表示可变或不适用
    is_instance_map: bool = True         # 是否按 {slug} 建实例 map；mvl=False

    @property
    def state_key_root(self) -> str:
        """实例态顶层区块名（"modules" / "maau" / "golden_circle" / ...）。"""
        return self.state_key.split(".", 1)[0]


CANVASES: tuple[CanvasSpec, ...] = (
    CanvasSpec(
        canvas_id="mvl",
        canvas_type="mvl",
        audit_type="mvl",
        state_key="modules.M{N}",
        file_prefix="M{N}",
        output_prefix="module-N",
        distill_skill="mvl-distill",
        gate_skill="module-conclusion-gate",
        gate_id_prefix="M{N}-GATE-0N",
        page_type="module-detail",
        template="skills/canvas-render/examples/mvl-canvas/module-N-canvas.html",
        generation_path=None,
        is_instance_map=False,
    ),
    CanvasSpec(
        canvas_id="maau",
        canvas_type="mvl",
        audit_type="mvl",
        state_key="maau.{slug}",
        file_prefix="MAAU",
        output_prefix="maau-global-canvas",
        distill_skill="maau-synthesize",
        gate_skill="module-conclusion-gate",
        gate_id_prefix="MAAU-GATE-",
        page_type="global",
        template="skills/canvas-render/examples/mvl-canvas/maau-global-canvas.html",
        generation_path="transcript-direct",
        is_instance_map=True,
    ),
    CanvasSpec(
        canvas_id="gc",
        canvas_type="golden-circle",
        audit_type="gc",
        state_key="golden_circle.{slug}",
        file_prefix="GC",
        output_prefix="gc",
        distill_skill="gc-distill",
        gate_skill="gc-gate",
        gate_id_prefix="GC-GATE-",
        page_type="golden-circle-index",
        template="skills/canvas-render/examples/goden-circle-canvas.html",
        generation_path=None,
        is_instance_map=True,
    ),
    CanvasSpec(
        canvas_id="hmw",
        canvas_type="hmw",
        audit_type="hmw",
        state_key="hmw.{slug}",
        file_prefix="HMW",
        output_prefix="hmw",
        distill_skill="hmw-distill",
        gate_skill="hmw-gate",
        gate_id_prefix="HMW-GATE-",
        page_type="hmw-index",
        template="skills/canvas-render/examples/hmw-canvas.html",
        generation_path=None,
        is_instance_map=True,
    ),
    CanvasSpec(
        canvas_id="persona",
        canvas_type="persona",
        audit_type="persona",
        state_key="persona.{slug}",
        file_prefix="PERSONA",
        output_prefix="persona",
        distill_skill="persona-distill",
        gate_skill="persona-gate",
        gate_id_prefix="PERSONA-GATE-",
        page_type="persona-index",
        template="skills/canvas-render/examples/user-persona-canvas.html",
        generation_path=None,
        is_instance_map=True,
    ),
    CanvasSpec(
        canvas_id="journey",
        canvas_type="journey",
        audit_type="journey",
        state_key="journey.{slug}",
        file_prefix="JOURNEY",
        output_prefix="journey",
        distill_skill="journey-distill",
        gate_skill="journey-gate",
        gate_id_prefix="JOURNEY-GATE-",
        page_type="journey-index",
        template="skills/canvas-render/examples/user-journey-canvas.html",
        generation_path=None,
        is_instance_map=True,
    ),
    CanvasSpec(
        canvas_id="v2c-vac",
        canvas_type="v2c-vac",
        audit_type="v2c-vac",
        state_key="v2c_vac.{slug}",
        file_prefix="V2C-VAC",
        output_prefix="v2c-vac",
        distill_skill="v2c-vac-distill",
        gate_skill="v2c-vac-gate",
        gate_id_prefix="V2C-GATE-",
        page_type="v2c-vac-index",
        template="skills/canvas-render/examples/v2c-value-attribution-canvas.html",
        generation_path=None,
        is_instance_map=True,
    ),
    CanvasSpec(
        canvas_id="5w",
        canvas_type="5w",
        audit_type="5w",
        state_key="five_whys.{slug}",
        file_prefix="5W",
        output_prefix="5w",
        distill_skill="5w-distill",
        gate_skill="5w-gate",
        gate_id_prefix="5W-GATE-",
        page_type="5w-index",
        template="skills/canvas-render/examples/5w-canvas.html",
        generation_path=None,
        is_instance_map=True,
    ),
)

# 私有索引（模块级构建，纯内存，无 IO）。
_BY_ID: dict[str, CanvasSpec] = {c.canvas_id: c for c in CANVASES}
_BY_AUDIT_TYPE: dict[str, CanvasSpec] = {c.audit_type: c for c in CANVASES}


def get(canvas_type: str) -> CanvasSpec | None:
    """按 canvas_type 取条目（maau 复用 mvl 的 canvas_type，返回先声明者 mvl）。"""
    for c in CANVASES:
        if c.canvas_type == canvas_type:
            return c
    return None


def by_id(canvas_id: str) -> CanvasSpec | None:
    """按 canvas_id 取条目（唯一）。"""
    return _BY_ID.get(canvas_id)


def by_audit_type(audit_type: str) -> CanvasSpec | None:
    """按 audit_type 取条目。"""
    return _BY_AUDIT_TYPE.get(audit_type)


def by_prefix(file_prefix: str) -> CanvasSpec | None:
    """按文件前缀取条目（精确匹配；M{N} 前缀单独处理）。"""
    for c in CANVASES:
        if c.file_prefix == file_prefix:
            return c
    return None


def canvas_types() -> tuple[str, ...]:
    """去重后的 canvas_type 集合（7 种：mvl / golden-circle / hmw / persona / journey / v2c-vac / 5w）。"""
    seen: list[str] = []
    for c in CANVASES:
        if c.canvas_type not in seen:
            seen.append(c.canvas_type)
    return tuple(seen)


def audit_types() -> tuple[str, ...]:
    """去重后的 audit_type 集合（7 种，即 CLI `--type` choices）。"""
    return AUDIT_TYPES


def validate() -> list[str]:
    """校验注册表内部一致性，返回问题列表（空 = 通过）。

    锁定的不变式：
    - canvas_id 唯一且恰为 8 个；
    - audit_type 去重后恰为 7 种（maau 复用 mvl）；
    - gc 是唯一 canvas_type != audit_type 的画布，且 canvas_type 必须为 "golden-circle"；
    - maau 的 canvas_type / audit_type 均须为 "mvl"，且 generation_path == "transcript-direct"；
    - 所有 distill_skill / gate_skill / gate_id_prefix / page_type / template / state_key / file_prefix
      / output_prefix 非空。
    """
    problems: list[str] = []

    ids = [c.canvas_id for c in CANVASES]
    if len(set(ids)) != len(ids):
        problems.append("canvas_id 重复")
    if set(ids) != {"mvl", "maau", "gc", "hmw", "persona", "journey", "v2c-vac", "5w"}:
        problems.append("canvas_id 集合不完整")

    if set(audit_types()) != {"mvl", "gc", "hmw", "persona", "journey", "v2c-vac", "5w"}:
        problems.append("audit_type 去重集合异常")

    gc = by_id("gc")
    if gc is None or gc.canvas_type != "golden-circle" or gc.audit_type != "gc":
        problems.append("gc 的 canvas_type/audit_type 双值不正确")
    if gc is not None and gc.canvas_type == gc.audit_type:
        problems.append("gc 的 canvas_type 与 audit_type 被合并")

    maau = by_id("maau")
    if maau is None or maau.canvas_type != "mvl" or maau.audit_type != "mvl":
        problems.append("maau 未复用 mvl 的 canvas_type/audit_type")
    if maau is not None and maau.generation_path != "transcript-direct":
        problems.append("maau 的 generation_path 必须为 transcript-direct")

    for c in CANVASES:
        for field in (
            "canvas_type", "audit_type", "state_key", "file_prefix",
            "output_prefix", "distill_skill", "gate_skill", "gate_id_prefix",
            "page_type", "template",
        ):
            if not getattr(c, field):
                problems.append(f"{c.canvas_id} 缺字段 {field}")

    return problems
