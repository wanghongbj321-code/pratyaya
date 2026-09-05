# GC-Pipeline：黄金圈画布执行细节（GC）

> 本文是 `agents/pratyaya.md`「标准画布管线」在 GC 画布的展开参考。治理不变式（Gate 只建议 / 人确认的是版本 / 五态状态机 / 升版边界）以 agent 为唯一事实源，本文只写执行。

<!-- rule:bump-version: 业务内容变更触发升版 version+1，重置 gate_recommendation / render_authorized / confirmation_mode / override_audit 并回落状态；仅第 12 节治理元数据写入不触发升版。 -->
<!-- rule:authorization-if-then: override 需 gate_recommendation=fail 且 render_authorized=true 且 override_audit 必填；gate_pass 需 pass 且 true；draft/gaps_open/review_ready 态 render_authorized 必须 false。 -->
<!-- rule:gate-summary: 全 PASS→gate_recommendation=pass；仅 business_risk FAIL→fail 且可 override；含 information_integrity FAIL→fail 且不可 override。 -->

## 画布参数（值来自 agent「画布注册表」，不改写）

| 参数 | 值 |
|---|---|
| `canvas_id` / `audit_type`（CLI `--type`） | `gc`（注意：`canvas_type=golden-circle`，二者不同，见注册表注） |
| `state_key` | `golden_circle.{slug}` |
| 文件前缀 / 输出前缀 | `GC` / `gc` |
| distill / gate | `gc-distill` / `gc-gate` |
| Gate ID 前缀 / `page_type` | `GC-GATE-` / `golden-circle-index` |

## 输入

- 用户转写 / 会议材料（存档 `transcripts/gc-{slug}-TXX-raw.md`，更新 `transcripts/manifest.json`）；
- 画布定义 `skills/gc-distill/references/gc-spec.md`；
- （GC 无 frameworks 目录。）

## 输出

- `modules/GC-{slug}-keypoints.md`（草稿源，不进入正式渲染）；
- `modules/GC-{slug}-gaps.md`（补问清单）；
- `modules/GC-{slug}-v{N}.md`（确认包，业务事实源）；
- `modules/GC-{slug}-gate-report-v{N}.md`（Gate 报告）；
- `output/gc-canvas-{slug}--v{N}.html`；索引页 `output/gc-canvas.html`。

## 状态写入

- `state.golden_circle.{slug}` 五态演进（draft → review_ready → confirmed → rendered），随用户决策驱动；
- 第 12 节治理元数据（Gate 建议 / 用户决策 / Override 审计）写入**不触发升版**；
- 旧单字段 state 先按 v2.6 instance map 迁移为 `golden_circle.default`，见 agent「实例管理」。

## 流程（标准 8 步，δ 已并入）

- **步骤 0 模式选择（δ1）**：A 引导（依次给出 WHY / HOW / WHAT 三层引导问题）、B 转写、C 覆盖检查；由用户指令决定，Agent 不预设；
- **步骤 1 Key Points**：抽取内容要求同标准管线；末尾提示「提炼 / 补问 / 先看个样子」；
- **步骤 2–4 分支**：提炼 → `GC-{slug}-v{N}.md`（`review_ready`）；补问 → `GC-{slug}-gaps.md`（`gaps_open`）；先看个样子 → 草稿 Canvas（水印，状态不变）；
- **步骤 5 确认包展示**：5 条必展项前置 + 详情折叠；自动进步骤 6；
- **步骤 6 Gate + 用户决策**：见「Gate」节；
- **步骤 7 视觉模式与渲染**：扫描并列出全部候选（默认预选 10 黑灰），等用户确认/改选后调用 `canvas-render`（`canvas_type=golden-circle`），参数见「渲染审计」；
- **步骤 8 完成**：`output/gc-canvas-{slug}--v{N}.html`；索引页 `output/gc-canvas.html`。

**δ2**：GC **不进全局 Canvas**，无 M1–M6 汇总路径、无 MAAU 实例。

## Gate

- 调用 `gc-gate`，读取 `skills/gc-gate/references/GC-gate.md` 的评估项，Gate ID 前缀 `GC-GATE-`；
- 输出 `GC-{slug}-gate-report-v{N}.md`；写 `state.golden_circle.{slug}.gate_recommendation`（pass / fail），**不写**最终授权；
- override 边界：按 agent「决策矩阵」——含 `information_integrity` FAIL 不提供 override；仅 `business_risk` FAIL 可显式 override（`override_audit` 完整）。

## 渲染审计

- 正式渲染前置校验 `state.golden_circle.{slug}.render_authorized=true`；
- 审计命令参数化：`--type gc`（**必须显式传**）、`--instance {slug}`、`--source modules/GC-{slug}-v{N}.md --state state.json`，`--page-type golden-circle-index`；
- 示例模板按 agent「画布注册表」的 `示例模板` 列取（渲染页 `canvas_type` 写 `golden-circle`）；
- 分级渲染验收（L1 静态审计 + L2 双视口 DOM 断言必做，L3 截图目检按需；定义见 `skills/canvas-render/SKILL.md`「分级渲染验收」）全过后才置 `rendered`；首次失败保持 `confirmed`；已有本版本成功产物后的失败保持原 `rendered`、output_file 和文件，不回退状态。

正式输出遵循 `skills/canvas-render/references/two-phase-render.md` 的机器后缀和候选提交规则：current 审计（默认），临时候选传 `--target-output <正式路径>`；成功才更新实际 output_file，索引读取该值。legacy 仅用于历史复查。索引 `--page-type` 参数只用于 `--index` 命令，详情审计不传 index page type。
