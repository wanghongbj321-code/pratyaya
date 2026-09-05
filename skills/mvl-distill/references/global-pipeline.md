# Global-Pipeline：MVL 全局汇总（Phase 2，M1–M6 → 全局 Canvas）

> 本文是 `agents/pratyaya.md`「Phase 2」的执行细节展开。触发路径与冲突分流见 `agents/pratyaya.md` 步骤 -1；治理不变式以 agent 为唯一事实源。

<!-- rule:bump-version: 业务内容变更触发升版 version+1，重置 gate_recommendation / render_authorized / confirmation_mode / override_audit 并回落状态；仅第 12 节治理元数据写入不触发升版。 -->
<!-- rule:authorization-if-then: override 需 gate_recommendation=fail 且 render_authorized=true 且 override_audit 必填；gate_pass 需 pass 且 true；draft/gaps_open/review_ready 态 render_authorized 必须 false。 -->
<!-- rule:gate-summary: 全 PASS→gate_recommendation=pass；仅 business_risk FAIL→fail 且可 override；含 information_integrity FAIL→fail 且不可 override。 -->

## 输入

- M1–M6 六个 `modules/Mx-v{N}.md` 确认包（各自最新确认版本）；
- `state.json`（六模块当前版本的授权元数据）。

## 输出

- `output/maau-global-canvas.html`（全局 Canvas）；
- `output/mvl-final-report.html`（管理层摘要报告）。

## 状态写入

本阶段对六个模块为**只读汇总**：不直接改模块状态。若一致性审核或对齐总检发现冲突，**回退相关模块**升版重审（见 agent「升版边界」），不在全局页静默修正。

## 流程

触发：用户要求全局 Canvas 或领导汇报。

1. 校验 M1–M6 全部为 `rendered`，且 HTML 与各模块最新确认版本一致；
2. 校验所有当前版本 `state.json` 的 `confirmation_mode`；
3. **跨模块 caveat 浮现**：
   - 扫描六个当前版本的 `confirmation_mode`；
   - 收集所有 `confirmation_mode=override` 模块的 `override_audit.items`；
   - 检查每项业务风险是否影响其他模块；
   - 若下游模块依赖被 override 的假设或未验证项，必须显式标注，或回退相关模块升版重审；
   - 不得因模块已进入 `rendered` 而忽略 caveat；
4. 对 M1–M6 的 `Mx-v{N}.md` 做跨模块一致性审核：目标是否被指标覆盖；用户结果是否被流程承接；流程是否为完整 AI 应用工作流（三类节点齐全，有 Agent / Context / 人工责任支持）；验证是否覆盖核心假设；数字、边界、术语、版本是否一致；
5. 有冲突时回退相关模块升版重审，不在全局页静默修正；
6. **对齐总检**：检查业务方与技术方对同一事项是否仍有不一致理解：
   - Intent「业务价值」↔ Validation「实测结果」（业务方认可技术方验证）；
   - User「最重要结果」↔ Workflow「完成条件」（业务方认可技术方闭环路径）；
   - Agent Team「决策边界」↔ Workflow 各节点（技术方认可业务方授权）；
   - 六个模块的重大分歧都已显式关闭或标记 `accepted_risk`；
   - 管理层最关心的风险点在 Validation 与 M6 能力边界中有对应；
7. 按 M-Pipeline 步骤 7 重新扫描视觉模式，**列出全部候选（默认预选 `10-black-gray-professional`）并等用户确认/改选**；把确认后的模式完整路径传给 `canvas-render`；
8. 调用 `canvas-render` 先以 `workflow_variant=noflow` 生成 `output/maau-global-canvas.html` 与 `output/mvl-final-report.html`；
9. 无图成功交付后询问是否需要图；需要时按 `skills/canvas-render/references/two-phase-render.md` 确认布局并独立验收，输出 `output/maau-global-canvas--workflow.html`。全局 Canvas 读取六模块实际 `output_file`，用普通相对链接进入各模块详情，**禁止 iframe**，保证本地 `file://` 可打开；
10. **管理层摘要分开呈现**：无保留确认结论（`gate_pass`）、带保留意见结论（`override`，单列且含风险摘要）、未验证假设、关键风险、补救动作（Owner + 日期）；不得把 override 结论混入"已完全验证"或"无风险"的成果表述。

## Gate

- 跨模块一致性审核与对齐总检发现的信息缺口 / 业务风险，按 `module-conclusion-gate` 规则**回退相关模块**走升版重审，不在汇总层绕过。
- 六个模块的 `gate_recommendation` 与 `confirmation_mode` 是汇总页 caveat 的唯一来源。

## 渲染审计

- 生成后运行分级渲染验收（L1 静态审计 [`--type mvl --page-type global` 语义] + L2 双视口 DOM 断言必做，L3 截图目检按需；定义见 `skills/canvas-render/SKILL.md`「分级渲染验收」），全过后交付；
- 渲染契约、锚点映射与离线约束以 `skills/canvas-render/references/render-contract.md` 与 `skills/mvl-distill/references/mvl-canvas-spec.md` 为准。

两阶段均复核六模块版本组合与授权，不写模块状态或 output_file；有图失败保留原成功文件。L1/L2 必传 `--workflow-variant noflow|workflow`，current 身份审计及候选提交规则见 two-phase-render.md。
