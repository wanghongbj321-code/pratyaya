# PERSONA-Pipeline：用户画像画布执行细节（Persona）

> 本文是 `agents/pratyaya.md`「标准画布管线」在 Persona 画布的展开参考。治理不变式以 agent 为唯一事实源，只写执行。

<!-- rule:bump-version: 业务内容变更触发升版 version+1，重置 gate_recommendation / render_authorized / confirmation_mode / override_audit 并回落状态；仅第 12 节治理元数据写入不触发升版。 -->
<!-- rule:authorization-if-then: override 需 gate_recommendation=fail 且 render_authorized=true 且 override_audit 必填；gate_pass 需 pass 且 true；draft/gaps_open/review_ready 态 render_authorized 必须 false。 -->
<!-- rule:gate-summary: 全 PASS→gate_recommendation=pass；仅 business_risk FAIL→fail 且可 override；含 information_integrity FAIL→fail 且不可 override。 -->

## 画布参数（值来自 agent「画布注册表」，不改写）

| 参数 | 值 |
|---|---|
| `canvas_id` / `canvas_type` / `audit_type` | `persona` / `persona` / `persona` |
| `state_key` | `persona.{slug}` |
| 文件前缀 / 输出前缀 | `PERSONA` / `persona` |
| distill / gate | `persona-distill` / `persona-gate` |
| Gate ID 前缀 / `page_type` | `PERSONA-GATE-` / `persona-index` |

## 输入

- 用户转写（存档 `transcripts/persona-{slug}-TXX-raw.md`，更新 manifest）；
- 画布定义 `skills/persona-distill/references/persona-spec.md`。

## 输出

- `modules/PERSONA-{slug}-keypoints.md`（草稿源）；
- `modules/PERSONA-{slug}-gaps.md`；
- `modules/PERSONA-{slug}-v{N}.md`（确认包，业务事实源）；
- `modules/PERSONA-{slug}-gate-report-v{N}.md`；
- `output/persona-{slug}-canvas.html`；索引页 `output/persona-canvas.html`。

## 状态写入

- `state.persona.{slug}` 五态演进，随用户决策驱动；
- 第 12 节治理元数据写入不触发升版；
- 旧单字段 state 先按 v2.6 instance map 迁移为 `persona.default`。

## 流程（标准 8 步，δ 已并入）

- **步骤 0 模式选择**：A 引导 / B 转写 / C 覆盖检查；
- **步骤 1 Key Points**：转写只整理用户语言，不改写专业术语，**不把推断写成事实**；
- **步骤 2–4 分支**：提炼 / 补问 / 先看个样子；
- **步骤 5 确认包展示**：5 条必展项 + 详情折叠；
- **步骤 6 Gate + 用户决策**：见「Gate」；
- **步骤 7 视觉模式与渲染**：扫描推荐 → 用户选定 → `canvas-render`；
- **步骤 8 完成**：`output/persona-{slug}-canvas.html`；索引页 `output/persona-canvas.html`。

**δ1**：Persona 是**独立单画布**，不改造 MVL M2 的 `08-user-persona.md`。
**δ2**：六宫格 6 区必须全有内容或显式标缺口。
**δ3**：关键基本信息 `name` / `job_title` / `industry` 必须有值。

## Gate

- 调用 `persona-gate`，读取 `skills/persona-gate/references/PERSONA-gate.md`，Gate ID 前缀 `PERSONA-GATE-`；
- 输出 `PERSONA-{slug}-gate-report-v{N}.md`；`gate_recommendation` 写 `state.persona.{slug}`；
- override 边界：按 agent「决策矩阵」；`information_integrity` FAIL 不提供 override。

## 渲染审计

- 前置校验 `state.persona.{slug}.render_authorized=true`（渲染前置校验示例，`state.json.persona.{slug}.render_authorized=true`）；
- 审计命令参数化：`--type persona`、`--instance {slug}`、`--page-type persona-index`、`--source modules/PERSONA-{slug}-v{N}.md --state state.json`；
- 示例模板按 agent「画布注册表」`示例模板` 列取；
- 审计 + 三视图全过后置 `rendered`；失败保持 `confirmed`。

## 强制执行指令

```text
# 在执行 Persona 流程时强制应用以下指令：
1. 仅当用户关键词命中"用户画像 / Persona / 画像 / 用户研究"且不属于 MVL / GC / HMW 时路由到 Persona。
2. 转写只整理用户语言，不改写专业术语，不把推断写成事实。
3. Key Points 仅用于草稿，正式渲染只读 `PERSONA-{slug}-v{N}.md`。
4. 六宫格 6 区必须全部有内容或显式标为缺口；关键基本信息 name / job_title / industry 必须有值。
5. Gate 只给建议；`render_authorized` 只能由用户显式授权（gate_pass 或 override）。
6. Persona 是独立单画布，不生成全局汇总，不改造 MVL M2 的 `08-user-persona.md`。
```
