# 5W-Pipeline：5W 根因分析画布执行细节（5W）

> 本文是 `agents/pratyaya.md`「标准画布管线」在 5W 画布的展开参考。治理不变式以 agent 为唯一事实源，只写执行。

<!-- rule:bump-version: 业务内容变更触发升版 version+1，重置 gate_recommendation / render_authorized / confirmation_mode / override_audit 并回落状态；仅第 12 节治理元数据写入不触发升版。 -->
<!-- rule:authorization-if-then: override 需 gate_recommendation=fail 且 render_authorized=true 且 override_audit 必填；gate_pass 需 pass 且 true；draft/gaps_open/review_ready 态 render_authorized 必须 false。 -->
<!-- rule:gate-summary: 全 PASS→gate_recommendation=pass；仅 business_risk FAIL→fail 且可 override；含 information_integrity FAIL→fail 且不可 override。 -->

## 画布参数（值来自 agent「画布注册表」，不改写）

| 参数 | 值 |
|---|---|
| `canvas_id` / `canvas_type` / `audit_type` | `5w` / `5w` / `5w` |
| `state_key` | `five_whys.{slug}` |
| 文件前缀 / 输出前缀 | `5W` / `5w` |
| distill / gate | `5w-distill` / `5w-gate` |
| Gate ID 前缀 / `page_type` | `5W-GATE-` / `5w-index` |

## 输入

- 用户转写（存档 `transcripts/5w-{slug}-TXX-raw.md`，更新 manifest）；
- 画布定义 `skills/5w-distill/references/5w-spec.md`。

## 输出

- `modules/5W-{slug}-keypoints.md`（草稿源）；
- `modules/5W-{slug}-gaps.md`；
- `modules/5W-{slug}-v{N}.md`（确认包，业务事实源）；
- `modules/5W-{slug}-gate-report-v{N}.md`；
- `output/5w-{slug}-canvas.html`；索引页 `output/5w-canvas.html`。

## 状态写入

- `state.five_whys.{slug}` 五态演进，随用户决策驱动；
- 第 12 节治理元数据写入不触发升版；
- 旧单字段 state 先按 v2.6 instance map 迁移为 `five_whys.default`。

## 流程（标准 8 步，δ 已并入）

- **步骤 0 模式选择**：A 引导 / B 转写 / C 覆盖检查；
- **步骤 1 Key Points**：问题陈述必须是事实，不做个人归因；抽取 5 条概览；
- **步骤 2–4 分支**：提炼 / 补问 / 先看个样子；
- **步骤 5 确认包展示**：5 条必展项 + 详情折叠；
- **步骤 6 Gate + 用户决策**：见「Gate」；
- **步骤 7 视觉模式与渲染**：扫描推荐 → 用户选定 → `canvas-render`；
- **步骤 8 完成**：`output/5w-{slug}-canvas.html`；索引页 `output/5w-canvas.html`。

**δ1**：丰田三层面追问框架（制造层 Why 1–2 / 检验层 Why 3–4 / 体系层 Why 5），五层锚点必须全在；层数弹性（少于 5 层）暂不支持。
**δ2**：每个 Why 必须附证据或显式标缺口；根因须过「因此」检验 + 对策四要素（对策 / 负责人 / 截止时间 / 验证方式）。

## Gate

- 调用 `5w-gate`，读取 `skills/5w-gate/references/5W-gate.md`，Gate ID 前缀 `5W-GATE-`；
- 输出 `5W-{slug}-gate-report-v{N}.md`；`gate_recommendation` 写 `state.five_whys.{slug}`；
- **δ3 override 边界**：`5W-GATE-01/02/03/04`（`information_integrity`）**不可 override**；`5W-GATE-05/06/07`（`business_risk`）可；
- **Template Gate**：模板结构与顺序是契约，`5W-TPL-GATE-XX` 失败不能由 Agent 自行豁免。

## 渲染审计

- 前置校验 `state.five_whys.{slug}.render_authorized=true`；
- 审计命令参数化：`--type 5w`、`--instance {slug}`、`--page-type 5w-index`、`--source modules/5W-{slug}-v{N}.md --state state.json`；
- **δ4**：审计**必须**显式传 `--template skills/canvas-render/examples/5w-canvas.html`；
- 审计 + 三视图全过后置 `rendered`；失败保持 `confirmed`。

## 强制执行指令

```text
# 在执行 5W 流程时强制应用以下指令：
1. 仅当用户关键词命中"5W / 丰田 5W / 五问法 / 根因分析 / Why-Why 分析"且不属于 MVL / GC / HMW / Persona / Journey / V2C VAC 时路由到 5W。
2. 默认采用丰田自身推荐的 5W 根因分析思考模型（三层面追问框架：制造层 Why 1-2 / 检验层 Why 3-4 / 体系层 Why 5）；层数弹性（少于 5 层）暂不支持，五层锚点必须全部存在。
3. 转写只整理用户语言，不改写专业术语，不把推断写成事实；问题陈述必须是事实，不做个人归因。
4. Key Points 仅用于草稿，正式渲染只读 `5W-{slug}-v{N}.md`。
5. 每个 Why 必须附证据或显式标缺口；根因必须通过"因此"检验并给出可行动对策（四要素：对策 / 负责人 / 截止时间 / 验证方式）。
6. Gate 只给建议；`render_authorized` 只能由用户显式授权（gate_pass 或 override）。
7. 只有 `business_risk` 可 override（`assessment_id` 为 `5W-GATE-05/06/07`）；`information_integrity`（`5W-GATE-01/02/03/04`）不可 override。
8. 模板结构与顺序是契约，Gate 报告里 `5W-TPL-GATE-XX` 失败不能由 Agent 自行豁免；正式交付必须传 `--template skills/canvas-render/examples/5w-canvas.html`。
```
