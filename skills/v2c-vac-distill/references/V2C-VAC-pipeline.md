# V2C-VAC-Pipeline：V2C 价值归因画布执行细节（V2C VAC）

> 本文是 `agents/pratyaya.md`「标准画布管线」在 V2C VAC 画布的展开参考。治理不变式以 agent 为唯一事实源，只写执行。

<!-- rule:bump-version: 业务内容变更触发升版 version+1，重置 gate_recommendation / render_authorized / confirmation_mode / override_audit 并回落状态；仅第 12 节治理元数据写入不触发升版。 -->
<!-- rule:authorization-if-then: override 需 gate_recommendation=fail 且 render_authorized=true 且 override_audit 必填；gate_pass 需 pass 且 true；draft/gaps_open/review_ready 态 render_authorized 必须 false。 -->
<!-- rule:gate-summary: 全 PASS→gate_recommendation=pass；仅 business_risk FAIL→fail 且可 override；含 information_integrity FAIL→fail 且不可 override。 -->

## 画布参数（值来自 agent「画布注册表」，不改写）

| 参数 | 值 |
|---|---|
| `canvas_id` / `canvas_type` / `audit_type` | `v2c-vac` / `v2c-vac` / `v2c-vac` |
| `state_key` | `v2c_vac.{slug}` |
| 文件前缀 / 输出前缀 | `V2C-VAC` / `v2c-vac` |
| distill / gate | `v2c-vac-distill` / `v2c-vac-gate` |
| Gate ID 前缀 / `page_type` | `V2C-GATE-` / `v2c-vac-index` |

## 输入

- 用户转写（存档 `transcripts/v2c-vac-{slug}-TXX-raw.md`，更新 manifest）；
- 画布定义 `skills/v2c-vac-distill/references/v2c-vac-spec.md`。

## 输出

- `modules/V2C-VAC-{slug}-keypoints.md`（草稿源）；
- `modules/V2C-VAC-{slug}-gaps.md`；
- `modules/V2C-VAC-{slug}-v{N}.md`（确认包，业务事实源）；
- `modules/V2C-VAC-{slug}-gate-report-v{N}.md`；
- `output/v2c-vac-{slug}-canvas.html`；索引页 `output/v2c-vac-canvas.html`。

## 状态写入

- `state.v2c_vac.{slug}` 五态演进，随用户决策驱动；
- **δ1**：`generation_path ∈ {pipeline, transcript-direct}`；`transcript-direct` 时 `pipeline_stage=null`；
- 第 12 节治理元数据写入不触发升版；
- 旧单字段 state 先按 v2.6 instance map 迁移为 `v2c_vac.default`。

## 流程（标准 8 步，δ 已并入）

- **步骤 0 模式选择**：A 引导 / B 转写 / C 覆盖检查；
- **步骤 1 Key Points**：抽取 5 条概览，末尾决策提示；
- **步骤 2–4 分支**：提炼 / 补问 / 先看个样子；
- **步骤 5 确认包展示**：5 条必展项 + 详情折叠；
- **步骤 6 Gate + 用户决策**：见「Gate」；
- **步骤 7 视觉模式与渲染**：扫描并列出全部候选（默认预选 10 黑灰）→ 用户确认/改选 → `canvas-render`；
- **步骤 8 完成**：`output/v2c-vac-{slug}-canvas.html`；索引页 `output/v2c-vac-canvas.html`。

**δ2**：pipeline 六阶段顺序 `scenario → capability → change → impact → value → attribution_review`。
**δ3**：`V2C-AGxx` 只能作归因断点 / 来源 ID，**不得**作 override 的 `assessment_id`。

## Gate

- 调用 `v2c-vac-gate`，读取 `skills/v2c-vac-gate/references/V2C-gate.md`，Gate ID 前缀 `V2C-GATE-`；
- 输出 `V2C-VAC-{slug}-gate-report-v{N}.md`；`gate_recommendation` 写 `state.v2c_vac.{slug}`；
- **δ4 Template Gate**：`V2C-VAC-TPL-GATE-01..08` **不可 override**；override 的 `assessment_id` 必须为 `V2C-*` 且 `category=business_risk`（不得是 `V2C-AGxx`，见 δ3）。

## 渲染审计

- 前置校验 `state.v2c_vac.{slug}.render_authorized=true`；
- 审计命令参数化：`--type v2c-vac`、`--instance {slug}`、`--page-type v2c-vac-index`、`--source modules/V2C-VAC-{slug}-v{N}.md --state state.json`；
- **δ4**：分级渲染验收（L1 静态审计含 Template Gate + L2 双视口 DOM 断言必做，L3 截图目检按需；定义见 `skills/canvas-render/SKILL.md`「分级渲染验收」）**通过**才置 `rendered`；
- 示例模板按 agent「画布注册表」`示例模板` 列取；失败保持 `confirmed`。
