# MVL Schemas（非强制参考）

本目录下的 JSON Schema 仅作为非强制参考。**模块产物的唯一中间格式是 Markdown**（`modules/Mx-keypoints.md`、`modules/Mx-v{N}.md`），运行时不强制执行 JSON Schema 校验。

## 文件说明

### `state.schema.json`

- **用途**：描述 `state.json` 的项目状态、模块版本、状态与审批结构。
- **当前状态**：保留作为**非强制参考**；LLM 不强制调用校验器。

### `module-record.schema.json`

- **用途**：参考旧 `modules/module-N.json` 的模块字段结构（canvas_fields、conclusions、gaps、inferences、alignment、approval、gate）。
- **当前状态**：保留作为**非强制参考**。`modules/Mx-v{N}.md`（确认包 Markdown）是当前唯一事实源。

## 当前实际数据源

| 资产 | 当前实现 |
|---|---|
| 状态 | `state.json`（参考 state.schema.json，不强制校验） |
| 模块中间产物 | `modules/Mx-keypoints.md` + `modules/Mx-v{N}.md` |
| 闸门判定 | LLM 阅读 `Mx-v{N}.md` + `../skills/module-conclusion-gate/references/Mx-gate.md`，输出 Markdown 判定报告 |
| 事实源 | `Mx-v{N}.md`（唯一事实源） |

## 后续评估

- 后续 MAJOR 版本可评估是否完全移除 `module-record.schema.json`。
- `state.schema.json` 视当前 5 态状态机的兼容需求再决定，无删除紧迫性。
