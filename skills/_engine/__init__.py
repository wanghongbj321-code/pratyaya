"""Pratyaya 共享画布引擎（§7 P4：全量引擎化）。

红线（执行计划 §7.4）：
1. 引擎**不渲染 HTML**——渲染只经 canvas-render Skill；引擎里出现写 HTML 即违规。
2. 引擎**不做语义判定**——只做结构 / 契约 / 状态 / 授权等规则型判定。
3. 引擎**不替人拍板**——所有越过 Gate 的授权（override）必须携带用户确认证据。
4. 引擎**不改 schema_version**（恒为 "2.4"）。
5. 引擎**不改 --type / --page-type 合法集**——合法集由 canvas_registry 单一事实源导出。
6. 依赖方向单向：`canvas_registry` ← `canvas_audit` ← `audit_canvas_html.py`。

子模块：
- canvas_registry：八类画布唯一参数事实源（零副作用）。
- paths：路径与命名模板唯一拼接处（零副作用）。
- state：5 态机、if/then 授权约束、升版边界。
- gate：Gate 三态汇总与 override 资格判定。
- authorization：授权写入（强制用户确认证据）。
- session：会话定位与三元一致、slug 校验。
- executor：标准 8 步推进/回退、轮次与版本映射。
- contract：确认包结构契约校验（只做结构）。
- files：文件级 gate（存在性/版本/旧 HTML 过期标记）。
- reconcile：跨模块 caveat 浮现与对齐总检数据收集。
- migration：legacy v2.6 instance / v2.9 default topic 迁移。
- manifest：group/project manifest 自重建。
"""

from __future__ import annotations

from . import (
    authorization,
    canvas_registry,
    contract,
    executor,
    files,
    gate,
    manifest,
    migration,
    paths,
    reconcile,
    session,
    state,
)
from .canvas_registry import (
    CANVASES,
    CanvasSpec,
    audit_types,
    by_audit_type,
    by_id,
    by_prefix,
    canvas_types,
    get,
    validate,
)
from .gate import Assessment, GateSummary, evaluate
from .authorization import AuthorizationError, grant, validate_override_audit
from .session import (
    RESERVED_SLUGS,
    SessionError,
    assert_valid_slug,
    is_valid_slug,
    validate_group_meta,
    validate_three_way_consistency,
    validate_topic_meta,
)
from .executor import (
    BRANCH_STATUS,
    NEXT_STEPS,
    STEPS,
    ExecutorError,
    assert_advance,
    assert_valid_step,
    branch_to_status,
    can_advance,
    is_valid_step,
    round_to_version,
)
from .contract import (
    ContractError,
    assert_filename_consistent,
    gate_id_regex,
    parse_confirmation_filename,
    parse_mvl_filename,
    validate_gate_ids,
    validate_governance_sections,
    validate_version_marker,
)
from .state import (
    ALLOWED_STATUSES,
    SCHEMA_VERSION,
    StateMachineError,
    assert_transition,
    can_transition,
    reset_for_bump,
    validate_if_then,
)

__all__ = [
    "CANVASES",
    "CanvasSpec",
    "SCHEMA_VERSION",
    "ALLOWED_STATUSES",
    "StateMachineError",
    "SessionError",
    "AuthorizationError",
    "ExecutorError",
    "ContractError",
    "Assessment",
    "GateSummary",
    "STEPS",
    "NEXT_STEPS",
    "BRANCH_STATUS",
    "RESERVED_SLUGS",
    "authorization",
    "canvas_registry",
    "contract",
    "executor",
    "files",
    "gate",
    "manifest",
    "migration",
    "paths",
    "reconcile",
    "session",
    "state",
    "get",
    "by_id",
    "by_audit_type",
    "by_prefix",
    "canvas_types",
    "audit_types",
    "validate",
    "evaluate",
    "grant",
    "validate_override_audit",
    "is_valid_slug",
    "assert_valid_slug",
    "validate_three_way_consistency",
    "validate_group_meta",
    "validate_topic_meta",
    "is_valid_step",
    "assert_valid_step",
    "can_advance",
    "assert_advance",
    "round_to_version",
    "branch_to_status",
    "parse_confirmation_filename",
    "parse_mvl_filename",
    "gate_id_regex",
    "validate_gate_ids",
    "assert_filename_consistent",
    "validate_version_marker",
    "validate_governance_sections",
    "can_transition",
    "assert_transition",
    "reset_for_bump",
    "validate_if_then",
]
