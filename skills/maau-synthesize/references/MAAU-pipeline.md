# MAAU-Pipeline：逐字稿 → MAAU 源包（Phase 3，transcript-direct 一次性综合）

> 本文是 `agents/pratyaya.md`「Phase 3」的执行细节展开。冲突分流判定见下表；治理不变式以 agent 为唯一事实源。

<!-- rule:bump-version: 业务内容变更触发升版 version+1，重置 gate_recommendation / render_authorized / confirmation_mode / override_audit 并回落状态；仅第 12 节治理元数据写入不触发升版。 -->
<!-- rule:authorization-if-then: override 需 gate_recommendation=fail 且 render_authorized=true 且 override_audit 必填；gate_pass 需 pass 且 true；draft/gaps_open/review_ready 态 render_authorized 必须 false。 -->
<!-- rule:gate-summary: 全 PASS→gate_recommendation=pass；仅 business_risk FAIL→fail 且可 override；含 information_integrity FAIL→fail 且不可 override。 -->

## 输入

- 逐字稿 / 会议材料（`transcripts/maau-{slug}-raw.md`）；
- 源包契约 `skills/maau-synthesize/references/maau-synth-spec.md`；
- Canvas 规范 `skills/mvl-distill/references/mvl-canvas-spec.md`；
- 全局映射 `skills/mvl-distill/references/workshop-canvas-map.md`。

## 输出

- `modules/MAAU-{slug}-v{N}.md`（六板块源包，唯一事实源）；
- `modules/MAAU-{slug}-gate-report-v{N}.md`（Gate 报告）；
- `output/maau-global-canvas-{slug}.html`（全局画布）。

## 状态写入

初始化 `state.maau.{slug}`：`slug={slug}`、`generation_path=transcript-direct`、`version=0`、`status=draft`、`gate_recommendation=pending`、`render_authorized=false`、`confirmation_mode=null`、`source_file=null`、`output_file=null`。

按缺口进入 `gaps_open` 或 `review_ready`；授权后渲染验收通过置 `rendered`。**实例与 M1–M6 互斥**，见冲突分流。

## 冲突分流（必须先判定，不混用）

| 情况 | 走哪条路径 |
|---|---|
| 已有 M1–M6 全部 `rendered`，用户要汇总模块 | Phase 2（`skills/mvl-distill/references/global-pipeline.md`） |
| 用户提供新逐字稿并明确要求 MAAU 一次性综合 | Phase 3（逐字稿 → `MAAU-{slug}-v{N}.md` → `maau-global-canvas-{slug}.html`） |
| 两者同时成立 | **必须让用户选择**，不得自动混用；说明两条路径互斥；可说明基于新逐字稿走 Phase 3 会新建实例，用户也可改选基于既有 M1–M6 走 Phase 2 |

## 流程

1. 确定 `instance_slug`：用户指定或推荐 kebab-case ASCII slug；**拒绝 `default`**；
2. 初始化 `state.maau.{slug}`（见上）；
3. 存档转写为 `transcripts/maau-{slug}-raw.md`，更新 `transcripts/manifest.json`；
4. 调用 `maau-synthesize`，读取源包契约 + Canvas 规范 + 全局映射；
5. 写 `modules/MAAU-{slug}-v1.md`（六板块源包）；
6. 状态按缺口进入 `gaps_open` 或 `review_ready`；
7. 调用 `module-conclusion-gate` 的 MAAU 模式（`gate_reference=references/MAAU-gate.md`），输出 gate 报告，`gate_recommendation` 写 `state.maau.{slug}`；
8. 展示 Gate 报告，等用户 **确认 vN / override / 补问**；
9. 授权后调用 `canvas-render`（`canvas_type=mvl`、`page_type=global`、`generation_path=transcript-direct`、`instance_slug={slug}`），输出 `output/maau-global-canvas-{slug}.html`；
10. 运行分级渲染验收（L1 静态审计 + L2 双视口 DOM 断言必做，L3 截图目检按需；定义见 `skills/canvas-render/SKILL.md`「分级渲染验收」）通过后置 `rendered`：
    ```bash
    python3 skills/canvas-render/scripts/audit_canvas_html.py output/maau-global-canvas-{slug}.html \
      --source modules/MAAU-{slug}-v{N}.md \
      --state state.json \
      --type mvl \
      --page-type global \
      --instance {slug} \
      --generation-path transcript-direct
    ```

## 关键约束

- MAAU 源包**不引用逐字稿段落**；来源线索基于 Key Points / 源包自身 section；
- Workflow 三类节点（Agent 执行 / 人工操作确认 / 人审 + Agent 执行）缺类标 `information_integrity` 缺口，不自动补写；
- Context 只列逐字稿讨论确认项并说明可获得性，不按常见做法自动补全；
- `information_integrity` FAIL 不接受 override；`business_risk` 可 override（`override_audit.items[].assessment_id` 为 `MAAU-GATE-*` 且 `category=business_risk`）；
- 实例页**不伪造 M1–M6 模块详情下钻**；与 Phase 2 全局页互斥，不把 transcript-direct 实例混入 M1–M6 Phase 2 汇总。

## Gate

- MAAU 模式 gate 输出到 `MAAU-{slug}-gate-report-v{N}.md`；`information_integrity` 缺口只回补问 / 修订，不提供 override。

## 渲染审计

- 只渲染实例自身 `maau-global-canvas-{slug}.html`；审计命令参数见上；渲染契约 / 锚点映射以 `render-contract.md` 与 `mvl-canvas-spec.md` 为准。
