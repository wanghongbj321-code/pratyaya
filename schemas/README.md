# Pratyaya Schemas（非强制参考）

本目录下的 JSON Schema 仅作为非强制参考。**模块产物的唯一中间格式是 Markdown**（`modules/Mx-keypoints.md`、`modules/Mx-v{N}.md`、`modules/GC-keypoints.md`、`modules/GC-v{N}.md`），运行时不强制执行 JSON Schema 校验。

## 文件说明

### `state.schema.json`（v2.0）

- **用途**：描述 `state.json` 的项目状态、模块版本、状态与审批结构，支持 MVL 和黄金圈（Golden Circle）两种画布类型。
- **v2.0 变更**：
  - `schema_version` 从 `"1.0"` 升级到 `"2.0"`。
  - `current_module` 和 `modules` 从顶层 `required` 降为可选字段（仅 MVL 画布需要）。
  - 新增顶层 `golden_circle` 对象，字段包括 `status` / `version` / `gate_recommendation` / `render_authorized` / `confirmation_mode` / `override_audit`。
  - `override_audit.items.assessment_id` 模式扩展为 `^(M[1-6]|GC)-GATE-[0-9]+$`。
- **向后兼容**：旧 MVL-only state.json（含 `modules` 但无 `golden_circle`）仍可使用；GC-only 项目不需要 `modules`。
- **当前状态**：保留作为**非强制参考**；LLM 不强制调用校验器。

### `module-record.schema.json`

- **用途**：参考旧 `modules/module-N.json` 的模块字段结构（canvas_fields、conclusions、gaps、inferences、alignment、approval、gate）。
- **当前状态**：保留作为**非强制参考**。`modules/Mx-v{N}.md`（确认包 Markdown）是当前唯一事实源。

## 当前实际数据源

| 资产 | 当前实现 |
|---|---|
| 状态 | `state.json`（参考 state.schema.json v2.0，不强制校验；MVL 存 `modules`，GC 存 `golden_circle`） |
| 模块中间产物 | `modules/Mx-keypoints.md` + `modules/Mx-v{N}.md`（MVL）/ `modules/GC-keypoints.md` + `modules/GC-v{N}.md`（黄金圈） |
| 闸门判定 | LLM 阅读确认包 + 对应 Gate 策略文件（MVL: `Mx-gate.md` / GC: `GC-gate.md`），输出 Markdown 判定报告 |
| 事实源 | `Mx-v{N}.md` 或 `GC-v{N}.md`（唯一事实源） |

## 后续评估

- 后续 MAJOR 版本可评估是否完全移除 `module-record.schema.json`。
- `state.schema.json` 视当前 5 态状态机与多画布类型的兼容需求再决定，无删除紧迫性。
