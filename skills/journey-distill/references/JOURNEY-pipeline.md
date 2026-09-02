# JOURNEY-Pipeline：用户旅程画布执行细节（Journey）

> 本文是 `agents/pratyaya.md`「标准画布管线」在 Journey 画布的展开参考。治理不变式以 agent 为唯一事实源，只写执行。

## 画布参数（值来自 agent「画布注册表」，不改写）

| 参数 | 值 |
|---|---|
| `canvas_id` / `canvas_type` / `audit_type` | `journey` / `journey` / `journey` |
| `state_key` | `journey.{slug}` |
| 文件前缀 / 输出前缀 | `JOURNEY` / `journey` |
| distill / gate | `journey-distill` / `journey-gate` |
| Gate ID 前缀 / `page_type` | `JOURNEY-GATE-` / `journey-index` |

## 输入

- 用户转写（存档 `transcripts/journey-{slug}-TXX-raw.md`，更新 manifest）；
- 画布定义 `skills/journey-distill/references/journey-spec.md`。

## 输出

- `modules/JOURNEY-{slug}-keypoints.md`（草稿源）；
- `modules/JOURNEY-{slug}-gaps.md`；
- `modules/JOURNEY-{slug}-v{N}.md`（确认包，业务事实源）；
- `modules/JOURNEY-{slug}-gate-report-v{N}.md`；
- `output/journey-{slug}-canvas.html`；索引页 `output/journey-canvas.html`。

## 状态写入

- `state.journey.{slug}` 五态演进，随用户决策驱动；
- 第 12 节治理元数据写入不触发升版；
- 旧单字段 state 先按 v2.6 instance map 迁移为 `journey.default`。

## 流程（标准 8 步，δ 已并入）

- **步骤 0 模式选择**：A 引导 / B 转写 / C 覆盖检查；
- **步骤 1 Key Points**：抽取 5 条概览，末尾决策提示；
- **步骤 2–4 分支**：提炼 / 补问 / 先看个样子；
- **步骤 5 确认包展示**：5 条必展项 + 详情折叠；
- **步骤 6 Gate + 用户决策**：见「Gate」；
- **步骤 7 视觉模式与渲染**：扫描推荐 → 用户选定 → `canvas-render`；
- **步骤 8 完成**：`output/journey-{slug}-canvas.html`；索引页 `output/journey-canvas.html`。

**δ1**：动态阶段 × 5 行合并结构（行动 / 触点与系统 / 情绪 / 痛点 / 机会），不得改成七要素。
**δ2**：最低 3 个有效阶段。
**δ3**：质量鉴别外显但**不得成为第 6 行**。
**δ4**：Journey 是独立一等公民画布，不写 `state.modules.M2`。

## Gate

- 调用 `journey-gate`，读取 `skills/journey-gate/references/JOURNEY-gate.md`，Gate ID 前缀 `JOURNEY-GATE-`；
- 输出 `JOURNEY-{slug}-gate-report-v{N}.md`；`gate_recommendation` 写 `state.journey.{slug}`；
- override 边界：按 agent「决策矩阵」；只有 `business_risk` 可 override，`information_integrity` 不可。

## 渲染审计

- 前置校验 `state.journey.{slug}.render_authorized=true`；
- 审计命令参数化：`--type journey`、`--instance {slug}`、`--page-type journey-index`、`--source modules/JOURNEY-{slug}-v{N}.md --state state.json`；
- 示例模板按 agent「画布注册表」`示例模板` 列取；
- 审计 + 三视图全过后置 `rendered`；失败保持 `confirmed`。

## 强制执行指令

```text
# 在执行 Journey 流程时强制应用以下指令：
1. 仅当用户关键词命中"用户旅程 / Journey / User Journey / 旅程画布 / 当前旅程"且不属于 MVL / GC / HMW / Persona 时路由到 Journey。
2. Journey 是独立一等公民画布，不修改 MVL M2 的 `09-user-journey.md`，不写 `state.modules.M2`。
3. 主表忠实保留 5 行合并结构：行动 / 触点与系统 / 情绪 / 痛点 / 机会；不得改成七要素。
4. 阶段按实际阶段动态生成，最低 3 个有效阶段；单次运行只承载一条 Journey。
5. Key Points 仅用于草稿，正式渲染只读 `JOURNEY-{slug}-v{N}.md`。
6. 质量鉴别必须在正式画布外显，但不得进入主表成为第 6 行。
7. Gate 只给建议；`render_authorized` 只能由用户显式授权（gate_pass 或 override）。
8. 只有 `business_risk` 可 override；`information_integrity` 不可 override。
```
