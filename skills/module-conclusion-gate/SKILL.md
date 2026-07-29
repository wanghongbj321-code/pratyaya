---
name: module-conclusion-gate
description: 审核 MVL 工作坊单模块的确认包（Mx-v{N}.md），评估缺口、对齐与人工确认状态，决定是否允许生成正式 Canvas。收到主 agent 步骤 6 的 Gate 评估请求、全局汇总前的跨模块对齐校验时使用。
---

# 模块结论闸门

把"内容已讨论过"与"内容足以成为项目结论"分开。本 skill 只做质量闸门评估和状态建议，不生成 HTML，也不替用户补结论。

## 定位

**NotebookLM 场景化闸门评估**：本 skill 是 MVL 助教的"确认 → 渲染"闸门能力。完整工作流由主 agent 编排（见 `agents/mvl-workshop-facilitator.md` 步骤 6），本 skill 不编排主流程，只在被调用时输出 Gate 判定报告（Markdown）。

本 skill 不调用 Canvas 渲染；Gate 通过后由主 agent 触发 `canvas-render`。

## 输入与输出

**输入**：

- `modules/Mx-v{N}.md`（确认包，Markdown 格式，唯一事实源）
- `gate-policy/Mx-gate.md`（本模块的最低可用结论与常见 blocker）
- 当前状态（来自主 agent 维护的 `state.json`）

**输出**：

- Gate 判定报告（Markdown 文本），结构见下文"Gate 评估流程"
- `render_allowed: true / false`
- 未通过项及补问建议（如 false）

## Gate 评估流程

**触发**：主 agent 步骤 6（用户回复"确认 vN"后调用）。

1. 读取 `modules/Mx-v{N}.md`（确认包）；
2. 读取 `gate-policy/Mx-gate.md`（本模块的最低可用结论与常见 blocker）；
3. 逐项对照评估，输出 Gate 判定报告（Markdown）：

```markdown
## Gate 判定报告 — M{N} v{X}

> 评估时间：{YYYY-MM-DD HH:MM}
> 模块：M{N} — {模块名}
> 确认包版本：v{X}

评估项：
- [ ] 关键结论都已通过"确认 vN"  → PASS / FAIL（说明）
- [ ] blocker/major 缺口已关闭     → PASS / FAIL（说明）
- [ ] minor 缺口已解决或接受风险     → PASS / FAIL（说明）
- [ ] 核心推断已接受或拒绝          → PASS / FAIL（说明）
- [ ] 确认人角色与版本一致          → PASS / FAIL（说明）

render_allowed: true / false

{若 false：列出未通过项及补问建议}
{若 true：「闸门通过。请告诉我你想用哪个模板生成画布？」}
```

4. 状态更新规则（由主 agent 执行，不在本 skill 内部）：
   - `render_allowed = false` → 状态回到 `gaps_open`，输出未通过项及补问建议
   - `render_allowed = true` → 状态改为 `confirmed`，触发模板选择

## 评估项详解

### 1. 关键结论都已通过"确认 vN"

按 MVL 产品审查 2.2 节立场，确认包内每条结论的合法性来自"本模块已通过确认 vN"，不依赖逐字稿段落级引用。本项检查确认包"必展项 2：对齐摘要"与"详情 7：结论登记表"是否一致——每条结论都应有明确的确认标记（共识/待确认/争议）。

**FAIL 情形**：结论登记表存在"待确认"或"争议"状态的结论。

### 2. blocker/major 缺口已关闭

检查确认包"详情 8：缺口表"：

- `blocker` 缺口状态必须为 `closed` 或 `accepted_risk`；
- `major` 缺口状态必须为 `closed` 或 `accepted_risk`；
- 任何 `blocker` 或 `major` 处于 `open` 即为 FAIL。

**FAIL 情形**：存在 open 状态的 blocker/major 缺口。

### 3. minor 缺口已解决或接受风险

`minor` 缺口允许在人工明确接受风险后保留，但必须在确认包中显式标注 `accepted_risk` 状态。

**FAIL 情形**：minor 缺口既未关闭也未接受风险（即仍为 `open`）。

### 4. 核心推断已接受或拒绝

确认包"详情 9：推断表"中的每条推断必须明确标记为 `accepted` 或 `rejected`。未标记的推断视为待处理。

**FAIL 情形**：存在 `pending` 状态的推断。

### 5. 确认人角色与版本一致

检查确认包顶部元数据：

- 确认人已填写（不为空）；
- 确认人角色明确（业务方/技术方/管理层等）；
- 确认时间在确认包生成时间之后；
- 确认人未对版本 v{X} 提出过升版请求。

**FAIL 情形**：确认人未填写、角色不清、确认时间早于确认包生成时间、或对当前版本提出过升版。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使当前日程的核心产出或对应 Canvas 模块无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变范围、方案或验证判断 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

每个缺口必须包含：缺什么、缺失影响、最少补问、状态（`open` / `closed` / `accepted_risk`）。

## 结论确认格式

确认包"详情 7：结论登记表"使用以下固定列：

| ID | 结论 | 类型 | 共识状态 |
|---|---|---|---|
| M{N}-C01 | ... | fact / decision / hypothesis / recommendation | 共识 / 待确认 / 争议 |

> **不保留 evidence 引用列**。按 MVL 产品审查 2.2 节立场，结论合法性来自"本模块已通过'确认 vN'"，不依赖逐字稿段落级引用。

确认时必须让用户看到：

1. 当前模块固定 section（参见 `gate-policy/Mx-gate.md`）；
2. 结论及共识状态；
3. 缺口和缺失影响；
4. 推断及接受/拒绝状态；
5. 当前版本号 v{N}。

## 对齐闸门

每个模块在进入 `review_ready` 之前，必须完成对齐检查，并将结果写入确认包的对齐 section。

对齐检查 5 项要点（Markdown 描述）：

1. **角色识别**：列出参与讨论的所有角色（业务方、技术方、管理层等）
2. **分歧点提取**：识别各方在同一话题上的不同理解
3. **共识地图**：标注共识点、分歧点、决策留痕
4. **语言翻译**：检查业务语言和技术语言混用
5. **决策留痕**：记录关键决策由谁拍板、谁认可

### 对齐数据结构（Markdown 表示）

> 以下结构作为**非强制参考**保留。实际闸门评估不依赖此结构，LLM 阅读确认包中的对齐 section 即可完成判断。

```markdown
## 对齐检查

### 共识点
- M{N}-CONS-01：...（参与人：业务方/技术方/管理层）

### 分歧点
- M{N}-DIV-01：...（话题；严重度：blocker/major/minor；影响：...；状态：open/resolved/accepted_risk）

### 决策留痕
- M{N}-DEC-01：...（决策人：业务方/技术方；认可人：...；时间：...）
```

### 状态跃迁规则

- 存在未解决的 blocker/major 分歧（`status=open` 且 `严重度 ∈ {blocker, major}`）→ 不得进入 `review_ready`
- 所有 blocker/major 分歧已 `resolved` 或 `accepted_risk` → 可进入 `review_ready`

## 全局汇总附加闸门

全局汇总时（主 agent Phase 2），额外执行以下对齐检查：

- Intent 的成功指标是否在 Validation 中有对应验证结果；
- User 的最重要结果是否由冻结 Workflow 承接；
- Workflow 是否是从触发到结果的 AI 应用工作流，三类节点是否齐全，并有 Agent Team 和 Context 支撑；
- M4 两轮原型与 M5 三轮验证的修改是否进入最终方案；
- M6 的能力边界、适配场景和总结是否与验证证据一致；
- 六大模块名称、数字、边界和版本是否一致；
- 页面是否明确"模拟环境概念验证原型，非生产级系统"。
- **跨模块对齐检查**：业务方定义的"价值"（M1）是否在技术方的"验证结果"（M5）中得到证实？业务方的"用户痛点"（M2）是否在"冻结工作流"（M4）中被逐一承接？技术方的"Agent 决策边界"（M4）是否与业务方在 Workflow 各节点的期望一致？管理层关注的风险是否在 Validation（M5）和能力边界（M6）中有对应？

如果存在跨模块对齐冲突，必须回退相关模块升版和重审，不在全局页面中静默修正。

## 草稿与正式版

- 草稿 Canvas 仅用于继续讨论，必须带"草稿 / 未确认 / 禁止用于管理层决策"水印。
- 草稿不得进入全局 Canvas 或领导汇报。
- 正式 Canvas 必须来自已确认的同一版本确认包。
- 闸门未通过时，不得调用 Canvas 渲染；只输出阻断原因和下一轮最少补问。

## 模块索引

| 模块 | 闸门策略文件 | 必填 section 来源 |
|---|---|---|
| M1 | `references/M1-gate.md` | `../../mvl-distill/references/workshop-canvas-map.md` |
| M2 | `references/M2-gate.md` | 同上 |
| M3 | `references/M3-gate.md` | 同上 |
| M4 | `references/M4-gate.md` | 同上 |
| M5 | `references/M5-gate.md` | 同上 |
| M6 | `references/M6-gate.md` | 同上 |

## 质量红线

1. 不编造、不拔高、不抹平冲突。
2. 评估项 1-5 全部 PASS 才可 `render_allowed=true`。
3. blocker 缺口不得以"先出图再补"绕过。
4. minor 缺口必须显式接受风险，不允许静默忽略。
5. 核心推断未接受/拒绝的不得放行。
6. 确认人未填写或角色不清的不得放行。
7. 不调用 Canvas 渲染；本 skill 只输出判定报告。
