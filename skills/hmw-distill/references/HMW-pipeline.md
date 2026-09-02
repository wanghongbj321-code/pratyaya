# HMW-Pipeline：HMW 画布执行细节（HMW）

> 本文是 `agents/pratyaya.md`「标准画布管线」在 HMW 画布的展开参考。治理不变式以 agent 为唯一事实源，只写执行。

## 画布参数（值来自 agent「画布注册表」，不改写）

| 参数 | 值 |
|---|---|
| `canvas_id` / `canvas_type` / `audit_type` | `hmw` / `hmw` / `hmw` |
| `state_key` | `hmw.{slug}` |
| 文件前缀 / 输出前缀 | `HMW` / `hmw` |
| distill / gate | `hmw-distill` / `hmw-gate` |
| Gate ID 前缀 / `page_type` | `HMW-GATE-` / `hmw-index` |

## 输入

- 用户转写（存档 `transcripts/hmw-{slug}-TXX-raw.md`，更新 manifest）；
- 画布定义 `skills/hmw-distill/references/hmw-spec.md`。

## 输出

- `modules/HMW-{slug}-keypoints.md`（草稿源）；
- `modules/HMW-{slug}-gaps.md`；
- `modules/HMW-{slug}-v{N}.md`（确认包，业务事实源）；
- `modules/HMW-{slug}-gate-report-v{N}.md`；
- `output/hmw-{slug}-canvas.html`；索引页 `output/hmw-canvas.html`。

## 状态写入

- `state.hmw.{slug}` 五态演进，随用户决策驱动；
- 第 12 节治理元数据写入不触发升版；
- 旧单字段 state 先按 v2.6 instance map 迁移为 `hmw.default`。

## 流程（标准 8 步，δ 已并入）

- **步骤 0 模式选择**：A 引导 / B 转写 / C 覆盖检查；用户指令决定；
- **步骤 1 Key Points**：转写只整理用户语言，**不改写专业术语**；抽取 5 条概览，末尾决策提示；
- **步骤 2–4 分支**：提炼 → `HMW-{slug}-v{N}.md`（`review_ready`）；补问 → `HMW-{slug}-gaps.md`；先看个样子 → 草稿（水印）；
- **步骤 5 确认包展示**：5 条必展项 + 详情折叠；
- **步骤 6 Gate + 用户决策**（δ3 相关见「Gate」）；
- **步骤 7 视觉模式与渲染**：扫描推荐 → 用户选定 → `canvas-render`；
- **步骤 8 完成**：`output/hmw-{slug}-canvas.html`；索引页 `output/hmw-canvas.html`。

**δ1**：三分支（落地 / 抽象 / 重构）必须全部产出 Idea，禁止只覆盖 1–2 个。
**δ2**：HMW 不进全局 Canvas。
**δ3**：HMW **永不**进入 `state.modules.M2`（不写 MVL M2 字段）。

## Gate

- 调用 `hmw-gate`，读取 `skills/hmw-gate/references/HMW-gate.md`，Gate ID 前缀 `HMW-GATE-`；
- 输出 `HMW-{slug}-gate-report-v{N}.md`；`gate_recommendation` 写 `state.hmw.{slug}`；
- **Template Gate**：模板结构与顺序是契约，`HMW-TPL-GATE-XX` 失败不能由 Agent 自行豁免；
- override 边界：按 agent「决策矩阵」；`information_integrity` FAIL 不提供 override。

## 渲染审计

- 前置校验 `state.hmw.{slug}.render_authorized=true`；
- 审计命令参数化：`--type hmw`、`--instance {slug}`、`--page-type hmw-index`、`--source modules/HMW-{slug}-v{N}.md --state state.json`；
- 示例模板按 agent「画布注册表」`示例模板` 列取；
- 审计 + 三视图全过后置 `rendered`；失败保持 `confirmed`。

## 强制执行指令

> 执行计划 `HMW画布实现执行计划-20260807.md` §7 要求以下指令原文落字，执行 HMW 流程时强制应用：

```text
# 在执行 HMW 流程时强制应用以下指令：
1. 仅当用户关键词命中"如何…/怎么做/能否…/如果…会…"且不属于 MVL / GC 时路由到 HMW。
2. 转写只整理用户语言，不改写专业术语。
3. Key Points 仅用于草稿，正式渲染只读 `HMW-{slug}-v{N}.md`。
4. 三分支（落地 / 抽象 / 重构）必须全部产出 Idea，禁止只覆盖 1–2 个。
5. Gate 只给建议；`render_authorized` 只能由用户显式授权（gate_pass 或 override）。
6. 模板结构与顺序是契约，Gate 报告里 `HMW-TPL-GATE-XX` 失败不能由 Agent 自行豁免。
```
