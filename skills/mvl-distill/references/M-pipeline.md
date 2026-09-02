# M-Pipeline：MVL 模块级分步管线（M1–M6，步骤 0–8）

> 本文是 `agents/pratyaya.md`「Phase 1」步骤 0–8 的执行细节展开，供 MVL 模块流程读取。
> 治理不变式（Gate 只建议 / 人确认的是版本 / 五态状态机 / 升版边界 / 第 12 节写入）以 `agents/pratyaya.md` 为唯一事实源，本文只展开执行步骤，**不重复、不覆盖**治理规则。

<!-- rule:bump-version: 业务内容变更触发升版 version+1，重置 gate_recommendation / render_authorized / confirmation_mode / override_audit 并回落状态；仅第 12 节治理元数据写入不触发升版。 -->
<!-- rule:authorization-if-then: override 需 gate_recommendation=fail 且 render_authorized=true 且 override_audit 必填；gate_pass 需 pass 且 true；draft/gaps_open/review_ready 态 render_authorized 必须 false。 -->
<!-- rule:gate-summary: 全 PASS→gate_recommendation=pass；仅 business_risk FAIL→fail 且可 override；含 information_integrity FAIL→fail 且不可 override。 -->

## 输入

- 逐字稿 / 转写文本或文件路径（原样存档，不做事实性改写）；
- 第 N 轮 Key Points（`modules/Mx-keypoints.md`）；
- 阶段框架 `skills/mvl-distill/frameworks/m{1-6}-*.md`（对应当前模块 Mx）；
- 辅助映射 `skills/mvl-distill/references/workshop-canvas-map.md`、Canvas 规范 `skills/mvl-distill/references/mvl-canvas-spec.md`。

## 输出（模块级）

- `modules/Mx-keypoints.md` —— Key Points 概览（草稿源，不进入正式渲染）；
- `modules/Mx-gaps.md` —— 补问清单（`gaps_open`）；
- `modules/Mx-v{N}.md` —— 确认包（业务事实源）；
- `output/module-N-canvas.html` —— 正式模块页（HTML 只是同版本展示物）。

## 状态写入

- Key Points 抽取完成**不立即跃迁**，等待用户决策；
- 提炼 → `review_ready`；补问 → `gaps_open`；草稿预览 → 状态不变；
- 用户确认 vN（gate_pass / override）→ `confirmed`；
- 渲染三视图验收全过 → `rendered`；
- 第 12 节治理元数据写入（12.1 Gate 建议 / 12.2 用户决策 / 12.3 Override 审计）**不触发升版**。

## 步骤 0：模式选择

由用户指令决定，Agent 不预设：

| 模式 | 用户指令示例 | 含义 |
|---|---|---|
| A. 引导模式 | "给我们 M3 的引导问题" / "Mx 引导" | 加载框架，输出引导问题和核心价值 |
| B. 转写模式 | "这是我们的逐字稿，请处理" / "提交转写" | 进入 Key Points 抽取 |
| C. 覆盖检查 | "我们讨论完了，帮我校验覆盖度" | 评估当前模块对框架的覆盖情况 |

## 步骤 1：Key Points 抽取

触发：步骤 0 进入转写模式，且当前模块尚未抽取 Key Points（或用户提交新一轮转写）。

- 原样存档为 `transcripts/module-N-TXX-raw.md`，更新 `transcripts/manifest.json`；
- 输出 `modules/Mx-keypoints.md`（第 N 轮，N ≥ 1）。

**内容要求**：

1. **讨论主题列表**：本次讨论覆盖了哪些主题（每个 1-2 句）
2. **关键主张**：每个主题下的主要观点（每项 1-2 句）
3. **明显矛盾或未对齐**：讨论中出现的内部不一致或分歧点
4. **覆盖度初判**：对照 Mx 框架，粗略评估覆盖情况（已覆盖 / 部分覆盖 / 未涉及）
5. **末尾用户决策提示**：「基于以上概览，请选择：**提炼** / **补问** / **先看个样子**」

**长度控制**：供 30 秒快速浏览，每个部分最多 5 条。

**不在此步骤做**：原子提炼、结论登记、缺口评估、确认包生成。

## 步骤 2–4：用户决策分支

收到用户在 Key Points 末尾的回复后，按回复类型进入对应分支：

**「提炼」→ 步骤 2：原子提炼**
- 调用 `mvl-distill`；输入逐字稿 + Key Points + 阶段框架（`frameworks/m{1-6}-*.md`）；
- 输出 `modules/Mx-v{N}.md`（确认包，全 Markdown）；状态 `review_ready`。

**「补问」→ 步骤 3：补问**
- 输出最少补问清单 `modules/Mx-gaps.md`，按影响排序，每条说明缺失的判断点和最少提问；状态 `gaps_open`；
- 新一轮转写按相同流程处理，Key Points 标记为第 N+1 轮，确认包 `Mx-v{N+1}.md`。

**「先看个样子」→ 步骤 4：草稿 Canvas**
- 调用 `canvas-render` 生成带永久水印的草稿；数据源为最新 Key Points（**非确认包**）；**不改变模块状态**；
- 提示：草稿不能进入全局汇总或管理层报告。

## 步骤 5：确认包展示

触发：`Mx-v{N}.md` 已完成。

1. 主 Agent 展示确认包，**关键信息前置**，让用户在 30 秒内完成浏览；
2. 状态写为 `review_ready`；
3. **自动进入步骤 6** 运行 Gate，**不要求用户先回复"确认 vN"**——"确认 vN"表示用户看完 Gate 报告后的最终确认。

**必展项（紧凑前置）**：
1. 【一句话结论】本模块核心结论（最多 50 字）
2. 【对齐摘要】共识 x 项 / 分歧 x 项 / 决策 x 项
3. 【阻塞项】如有 blocker 第一条就警示标注
4. 【缺口速览】blocker x / major x / minor x
5. 【待确认版本】v{N}

**详情（折叠，按需展开）**：
6. 结论登记表：ID、结论、类型、来源引用、置信度、审核状态
7. 缺口表：等级、缺失影响、补问、状态
8. 推断表：内容、影响、接受/拒绝状态
9. 「还有没有未讨论、但会影响本模块核心判断的话题？」

## 步骤 6：Gate（质量建议）+ 用户决策

触发：步骤 5 完成（`review_ready`），主 Agent 自动调用 `module-conclusion-gate`；用户决策前不进入步骤 7。

1. Gate 读取当前版本确认包和模块策略（`skills/module-conclusion-gate/references/Mx-gate.md`）；
2. 每项输出：稳定 ID（`M{N}-GATE-0N`）、PASS/FAIL、分类（`information_integrity` / `business_risk`）、风险等级、来源 ID、影响和建议；
3. Gate 写 `state.json.gate_recommendation`（pass / fail），**不写**最终授权；
4. 展示 Gate 报告后等待用户决策，不擅自按建议推进：

| 条件 | 用户选项 | 主 Agent 写入 |
|---|---|---|
| Gate 全 PASS | "确认 vN" / 返回修订 | `confirmation_mode=gate_pass` / `render_authorized=true` 或保持 `gaps_open` |
| 仅 `business_risk` FAIL | 显式 override（理由、影响、确认人、时间）+ 确认 vN | `confirmation_mode=override` / `render_authorized=true` / `override_audit` 完整 |
| 含 `information_integrity` FAIL | 仅补问或修订 | 不提供正式 override；保持 `review_ready` 或回 `gaps_open` |
| 任何情况 | 修订当前版本 | `gaps_open`，`gate_recommendation=pending`，`render_authorized=false`，`confirmation_mode=null` |

5. Gate 报告格式见 `skills/module-conclusion-gate/SKILL.md`「Gate 评估流程」；
6. **未拿到用户最终决策**：`status=review_ready`、`render_authorized=false`、`confirmation_mode=null`；
7. **Gate FAIL 不自动回退状态**——状态机由用户决策驱动，不由 Gate 建议驱动；
8. **第 12 节治理元数据写入**：步骤 6 期间同步写确认包第 12 节（12.1 Gate 建议摘要 / 12.2 用户决策 / 12.3 Override 审计），三次写入不触发升版；`state.json` 同步更新四个治理字段。

## 步骤 7：视觉模式选择与渲染

触发：用户在步骤 6 给出最终决策，且 `render_authorized=true`、`confirmation_mode ∈ {gate_pass, override}`、状态 `confirmed`。

1. 扫描 `skills/canvas-render/visual-patterns/[0-9][0-9]-*.md`；`README.md` 不属于候选；
2. 读取全部候选 frontmatter 并校验：基线恰好 10 个候选；序号和 `id` 唯一；文件名 `NN-{id}.md` 且 `{id}` 与 frontmatter 一致；frontmatter 恰好含 `id / zh_name / visual_system / layout / formality / density / best_for`；
3. 基于确认包内容特征与候选 `zh_name / visual_system / layout / formality / density / best_for`，推荐 1–2 个模式，**以 `zh_name` 为主要展示名**并说明理由；
4. 等待用户明确选择；未选择时停在本步骤，不使用默认模式；
5. 选定后保存**完整仓库相对路径**（如 `skills/canvas-render/visual-patterns/01-blue-professional-balanced.md`），不得由 `id` 拼接；
6. 调用 `canvas-render` 时传递：`Mx-v{N}.md`（唯一事实源）+ `state.json` 同模块授权元数据 + 同版本 Gate 判定 + 用户选定模式的完整路径；
7. `canvas-render` 读取模式正文色板/字体/网格/组件/适用场景/反例，不读取旧 HTML 获取视觉 token；
8. 生成 `output/module-N-canvas.html`，先跑 `audit_canvas_html.py`（正式模块页同时传入确认包与 `state.json`），Python PASS 后完成桌面 / 窄屏 / 打印三视图浏览器视觉验收；全部通过才把状态改为 `rendered`。

**数据源**：HTML 只读 `Mx-v{N}.md` 确认包；LLM 提取 `canvas_fields` 按 `render-contract.md` 映射到稳定锚点；`canvas-data` 内嵌同版本授权元数据。

**自检步骤**：`audit_canvas_html.py` 对照 `render-contract.md` 检查 DOM/稳定锚点顺序、字段映射、版本、授权元数据、离线约束、打印规则与 caveat 结构；脚本直接读契约映射表，不用第二份锚点清单。`confirmation_mode=override` 时必须额外确认 caveat 状态标识与风险详情在三种视图下可见。

**状态时序**：HTML 写出 ≠ 渲染完成。Python 静态审计或浏览器验收任一失败时**保持 `confirmed`**，`confirmation_mode` / `gate_recommendation` 保持原值；不得提前写 `rendered`，不得回退 `gaps_open`。修订同版本 HTML 后重跑全部校验；涉及业务内容则按"状态回退"升版重新确认。

**Caveat 渲染**：`confirmation_mode=override` 时，模块详情页顶部显示"已确认 · 带保留意见"；`quality-caveat` 显示 Gate 建议、最终渲染授权、override 项数量、高风险项数量、每项的影响/理由/确认人/时间/补救措施；打印版保留。`gate_pass` 不显示 override 提示。

## 步骤 8：预告下一模块

输出下一模块引导问题，并带上本模块会影响下一模块的已确认结论和仍待验证的 minor 项。

## Gate

- 模块级 Gate 的完整执行位置见「步骤 6」；Gate 只输出建议，不写 `render_authorized`，FAIL 不自动回退状态。
- Gate 判定规则以 `skills/module-conclusion-gate/references/Mx-gate.md` 为事实源，本文不重复。

## 渲染审计

- 渲染与审计的完整执行位置见「步骤 7」；渲染契约、锚点映射与离线约束以 `skills/canvas-render/references/render-contract.md` 为事实源。
- HTML 写出 ≠ 渲染完成：Python 静态审计 + 桌面 / 窄屏 / 打印三视图验收全过才置 `rendered`。
