---
name: hmw-gate
description: 对 HMW（How Might We，问题重构）工作坊的确认包（HMW-{slug}-v{N}.md）做质量建议与风险分级，输出 gate_recommendation 供主 Agent 决策。Gate 只输出建议，不决定最终渲染授权；用户授权由主 Agent 根据 Gate 报告与用户决策写入。本 skill 不生成 HTML，也不替用户补结论。
---

# HMW 结论质量建议

把"内容已讨论过"与"内容足以成为 HMW 问题重构结论"分开。本 skill 只做质量建议和风险分级，**不决定最终渲染授权**。最终授权由主 Agent 在用户决策后写入 `state.json` 的 `render_authorized` 与 `confirmation_mode` 字段。

## 定位

**质量建议器（Gate）**：本 skill 是 Pratyaya Canvas Expert 的"质量建议"能力。完整工作流由主 agent 编排（见 `agents/pratyaya.md`），本 skill 不编排主流程，只在被调用时输出 Gate 建议报告（Markdown）。

本 skill 不调用 Canvas 渲染；Gate 报告输出后由主 Agent 展示给用户，等待用户决策并触发 `canvas-render`。

## 输入与输出

**输入**：

- `modules/HMW-{slug}-v{N}.md`（确认包，Markdown 格式，唯一事实源）
- `references/HMW-gate.md`（HMW 放行条件与稳定 ID，位于本 Skill 的 `references/` 子目录）
- 当前状态（来自主 agent 维护的 `state.json` 的 `hmw` 区块）

**输出**：

- Gate 建议报告（Markdown 文本），结构见下文"Gate 评估流程"
- `gate_recommendation: pass / fail`
- `override_eligible: true / false`（仅 `business_risk` FAIL 时才可能为 true）
- 不输出 `render_authorized`；不写最终授权。

## Gate 评估流程

**触发**：主 agent HMW 工作流对应步骤——确认包已生成、状态为 `review_ready`，主 Agent 自动调用本 skill。

1. 读取 `modules/HMW-{slug}-v{N}.md`（确认包第 1–11 节业务内容；第 12 节为治理元数据，不参与评估）；
2. 输出 Gate 报告文件名使用 `modules/HMW-{slug}-gate-report-v{N}.md`；slug 不进入 `HMW-GATE-XX` 稳定 ID。
2. 读取 `references/HMW-gate.md`（HMW 放行条件 + 稳定 ID + 分类 + 风险等级）；
3. 逐项对照评估，输出 Gate 建议报告（Markdown）：

```markdown
## Gate 评估报告 — HMW v{N}

> 评估时间：{ISO 8601 datetime}
> 画布类型：How Might We（问题重构）画布
> 确认包版本：v{N}
> gate_recommendation：pass / fail
> override_eligible：true / false

### 评估项

| ID | 检查项 | 结果 | 分类 | 风险等级 | 来源 ID | 影响 | 建议 |
|---|---|---|---|---|---|---|---|
| HMW-GATE-01 | 问题情境含用户时刻 | PASS / FAIL | information_integrity / business_risk | low / medium / high | HMW-state | ... | ... |
| HMW-GATE-02 | HMW 问句不含预设解法 | ... | ... | ... | ... | ... | ... |

### Gate 建议

- gate_recommendation：pass / fail
- override_eligible：true / false
- 未通过项摘要：（仅 fail 时列出）

### 用户可选动作

- Gate PASS：确认 v{N} / 返回修订
- 仅业务风险 FAIL：显式 override 并填写理由 / 返回修订
- 含信息完整性 FAIL：补问或修订
```

4. 状态更新规则（由主 agent 执行，不在本 skill 内部）：
   - Gate 报告写入 `gate_recommendation` 字段；
   - `render_authorized` 与 `confirmation_mode` 只能由主 Agent 在用户决策后写入；
   - Gate FAIL 时**不自动**回退状态；状态仍为 `review_ready`，等待用户决策。

## 评估项与稳定 ID

6 条放行条件在 `references/HMW-gate.md` 中拥有稳定 ID：

```text
HMW-GATE-01
HMW-GATE-02
HMW-GATE-03
HMW-GATE-04
HMW-GATE-05
HMW-GATE-06
```

评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响和建议。

## 分类与可 override 关系

每个评估项必须分类为 `information_integrity` 或 `business_risk`，且与"可 override 性"有明确对应：

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立（核心事实源、当前版本、确认包字段覆盖等） | **否** |
| `business_risk` | 结论已有事实基础，但问题框定的正确性（是否预设解法、是否含张力）不完整 | **是**（填写理由后） |

> **核心规则**：用户可以接受现实中问题框定的主观风险，但不能通过 override 把不存在的信息变成事实。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得超过正式 override。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使 HMW 陈述或质量判定无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变问题重构的方向 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

严重度（blocker / major / minor）与分类（information_integrity / business_risk）是两个维度：

- `information_integrity`：无论严重度，均不可正式 override；
- `business_risk`：用户可在看见影响并填写理由后 override；
- minor 仍不得静默忽略，必须关闭或显式接受。

## 结论确认格式

确认包"详情 7：结论登记表"使用以下固定列：

| ID | 结论 | 类型 | 共识状态 |
|---|---|---|---|
| HMW-C01 | ... | fact / decision / hypothesis / recommendation | 共识 / 待确认 / 争议 |

确认时必须让用户看到：

1. HMW 陈述四字段（situation / question / for / so_that）；
2. 质量鉴别（第 6a 节，四维度判定）；
3. 想法种子（第 6b 节）与想法 ↔ HMW 对应（第 6c 节）；
4. 结论及共识状态；
5. 缺口和缺失影响；
6. 推断及接受/拒绝状态；
7. 当前版本号 v{N}。

## 对齐闸门

每个模块在进入 `review_ready` 之前，必须完成对齐检查，并将结果写入确认包的对齐 section。

对齐检查 5 项要点（Markdown 描述）：

1. **角色识别**：列出参与讨论的所有角色（业务方、技术方、管理层等）
2. **分歧点提取**：识别各方在同一话题上的不同理解
3. **共识地图**：标注共识点、分歧点、决策留痕
4. **语言翻译**：检查业务语言和技术语言混用
5. **决策留痕**：记录关键决策由谁拍板、谁认可

### 状态跃迁规则

- 存在未解决的 blocker/major 分歧 → 不得进入 `review_ready`
- 所有 blocker/major 分歧已 resolved 或 accepted_risk → 可进入 `review_ready`

## 质量鉴别附加闸门

Gate 评估时额外检查：

- 第 6a 节"质量鉴别"是否填写，四维度是否都有判定
- 判定为"不通过"的维度，是否在缺口表中登记对应的 major/minor 缺口
- 想法种子的 `link_to_statement` 是否能在确认包中找到对应问句（非 LLM 构造）

> **注意**：HMW 是单画布，不存在跨模块 caveat 检查。质量鉴别检查只在本 Gate 内完成。

## 草稿与正式版

- 草稿 Canvas 仅用于继续讨论，必须带"草稿 / 未确认 / 禁止用于管理层决策"水印。
- 草稿不进入正式输出。
- 正式 Canvas 必须来自已确认的同一版本确认包，且对应 `state.json.hmw.{slug}.render_authorized=true`、`confirmation_mode ∈ {gate_pass, override}`；确认包 `{slug}`、state key、`state.json.hmw.{slug}.slug` 与输出文件名必须一致。
- 闸门评估未完成时（`gate_recommendation=pending`），不得调用 Canvas 渲染；只输出"待评估"状态与下一轮最少补问。

## 质量红线

1. 不编造、不拔高、不抹平冲突。
2. Gate 输出建议而非授权；不得写入 `render_authorized`。
3. `information_integrity` FAIL 不得进入 override 路径。
4. `business_risk` FAIL 用户可显式接受，必须填写理由、确认人与时间。
5. blocker 缺口不得以"先出图再补"绕过。
6. minor 缺口必须显式接受风险，不允许静默忽略。
7. 核心推断未接受/拒绝的不得建议 `gate_recommendation=pass`。
8. 确认人未填写且角色不清的不得建议 `gate_recommendation=pass`。
9. 不调用 Canvas 渲染；本 skill 只输出建议报告。
10. `information_integrity` FAIL 时 `override_eligible=false`；主 Agent 不向用户提供 override 选项。
