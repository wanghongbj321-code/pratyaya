# MVL Schemas（非强制参考）

本目录下的 JSON Schema 是 v1.x 阶段的强约束产物。v2.0 起，**模块产物的唯一中间格式是 Markdown**（`modules/Mx-keypoints.md`、`modules/Mx-v{N}.md`），JSON Schema 不再被强制校验。

## 文件说明

### `state.schema.json`

- **原用途**：校验 `state.json`（项目状态、模块版本/状态/审批）。
- **当前状态**：保留作为**非强制参考**。`state.json` 仍按其结构组织（M1-M6 状态/版本/审批），但 LLM 不强制调用校验器。
- **不删除原因**：保留向后兼容，且状态机结构与 v1.x 兼容，便于既有用户平滑迁移。

### `module-record.schema.json`

- **原用途**：校验 `modules/module-N.json`（模块 JSON，含 canvas_fields、conclusions、gaps、inferences、alignment、approval、gate）。
- **当前状态**：保留作为**非强制参考**。`modules/Mx-v{N}.md`（确认包 Markdown）是 v2.0 的唯一事实源。
- **不删除原因**：旧项目可能仍有 `module-N.json` 资产；Schema 仍可作 v1.x 项目的回退校验。

## v2.0 时代的实际数据源

| 资产 | v1.x | v2.0 |
|---|---|---|
| 状态 | `state.json`（按 state.schema.json） | `state.json`（结构同 v1.x，但不强校验） |
| 模块中间产物 | `modules/module-N.json`（按 module-record.schema.json） | `modules/Mx-keypoints.md` + `modules/Mx-v{N}.md` |
| 闸门判定 | `module-conclusion-gate` 调 `check_gate.py` | LLM 阅读 `Mx-v{N}.md` + `gate-policy/Mx-gate.md`，输出 Markdown 判定报告 |
| 事实源 | module-N.json | `Mx-v{N}.md`（唯一事实源） |

## 后续评估

- v2.1 可评估是否完全移除 `module-record.schema.json`（当无 v1.x 存量项目时）。
- `state.schema.json` 视 v2.0 状态机稳定性再决定（当前结构与 v1.x 完全一致，无删除紧迫性）。
