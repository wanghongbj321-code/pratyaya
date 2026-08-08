---
name: journey-gate
description: 对 User Journey（用户旅程）工作坊的确认包（JOURNEY-v{N}.md）做质量建议与风险分级，输出 gate_recommendation 供主 Agent 决策。Gate 只输出建议，不决定最终渲染授权；用户授权由主 Agent 根据 Gate 报告与用户决策写入。本 skill 不生成 HTML，也不替用户补结论。
---

# User Journey 结论质量建议

把“内容已讨论过”与“内容足以成为用户旅程结论”分开。本 skill 只做质量建议和风险分级，**不决定最终渲染授权**。最终授权由主 Agent 在用户决策后写入 `state.json` 的 `render_authorized` 与 `confirmation_mode` 字段。

质量鉴别采用正式画布外显方式：Gate 必须评估确认包第 6a 节四维度，但不得把质量鉴别只留在内部判断中；本 skill 不写入 render_authorized，不生成 HTML。

## 定位

**质量建议器（Gate）**：本 skill 是 Pratyaya Canvas Expert 的“质量建议”能力。完整工作流由主 agent 编排（见 `agents/pratyaya.md`），本 skill 不编排主流程，只在被调用时输出 Gate 建议报告（Markdown）。

本 skill 不调用 Canvas 渲染；Gate 报告输出后由主 Agent 展示给用户，等待用户决策并触发 `canvas-render`。

## 输入与输出

**输入**：

- `modules/JOURNEY-v{N}.md`（确认包，Markdown 格式，唯一事实源）
- `references/JOURNEY-gate.md`（Journey 放行条件与稳定 ID，位于本 Skill 的 `references/` 子目录）
- 当前状态（来自主 agent 维护的 `state.json` 的 `journey` 区块）

**输出**：

- Gate 建议报告（Markdown 文本），结构见下文“Gate 评估流程”
- `gate_recommendation: pass / fail`
- `override_eligible: true / false`（仅 `business_risk` FAIL 时才可能为 true）
- 不输出 `render_authorized`；不写最终授权。

## Gate 评估流程

**触发**：主 agent Journey 工作流对应步骤——确认包已生成、状态为 `review_ready`，主 Agent 自动调用本 skill。

1. 读取 `modules/JOURNEY-v{N}.md`（确认包第 1–11 节业务内容；第 12 节为治理元数据，不参与评估）；
2. 读取 `references/JOURNEY-gate.md`（Journey 放行条件 + 稳定 ID + 分类 + 风险等级）；
3. 逐项对照评估，输出 Gate 建议报告（Markdown）：

```markdown
## Gate 评估报告 — Journey v{N}

> 评估时间：{ISO 8601 datetime}
> 画布类型：User Journey（用户旅程）画布
> 确认包版本：v{N}
> gate_recommendation：pass / fail
> override_eligible：true / false

### 评估项

| ID | 检查项 | 结果 | 分类 | 风险等级 | 来源 ID | 影响 | 建议 |
|---|---|---|---|---|---|---|---|
| JOURNEY-GATE-01 | 至少 3 个有效阶段，且阶段名清晰 | PASS / FAIL | information_integrity | low | JOURNEY-map | ... | ... |
| JOURNEY-GATE-02 | 每个阶段 5 行字段全部有内容或显式标为缺口 | ... | ... | ... | ... | ... | ... |

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

6 条放行条件在 `references/JOURNEY-gate.md` 中拥有稳定 ID：

```text
JOURNEY-GATE-01
JOURNEY-GATE-02
JOURNEY-GATE-03
JOURNEY-GATE-04
JOURNEY-GATE-05
JOURNEY-GATE-06
```

评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响和建议。

## 分类与可 override 关系

每个评估项必须分类为 `information_integrity` 或 `business_risk`，且与“可 override 性”有明确对应：

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立（阶段数量、主表字段、痛点与机会条目覆盖等） | **否** |
| `business_risk` | 结论已有事实基础，但旅程边界、用户视角或方案预设存在风险 | **是**（填写理由后） |

> **核心规则**：用户可以接受现实中的业务判断风险，但不能通过 override 把不存在的信息变成事实。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得超过正式 override。

## 结论确认格式

确认包“详情 7：结论登记表”使用以下固定列：

| ID | 结论 | 类型 | 共识状态 |
|---|---|---|---|
| JOURNEY-C01 | ... | fact / decision / hypothesis / recommendation | 共识 / 待确认 / 争议 |

确认时必须让用户看到：

1. 阶段地图（动态阶段 × 5 行合并结构）；
2. 质量鉴别（第 6a 节，四维度判定）；
3. 痛点与机会（第 6b 节）；
4. 结论及共识状态；
5. 缺口和缺失影响；
6. 推断及接受/拒绝状态；
7. 当前版本号 v{N}。

## 质量鉴别附加闸门

Gate 评估时额外检查：

- 第 6a 节“质量鉴别”是否填写，四维度是否都有判定；
- 判定为“不通过”的维度，是否在缺口表中登记对应的 major/minor 缺口；
- 第 6 节主表是否仍为 5 行合并结构，不得改为七要素；
- 第 6b 节痛点与机会摘要是否来自阶段地图，而不是另造的新结论。

> **注意**：Journey 是单画布，不存在跨模块 caveat 检查。质量鉴别检查只在本 Gate 内完成。

## 草稿与正式版

- 草稿 Canvas 仅用于继续讨论，必须带“草稿 / 未确认 / 禁止用于管理层决策”水印。
- 草稿不进入正式输出。
- 正式 Canvas 必须来自已确认的同一版本确认包，且 `state.json.journey.render_authorized=true`、`confirmation_mode ∈ {gate_pass, override}`。
- 闸门评估未完成时（`gate_recommendation=pending`），不得调用 Canvas 渲染；只输出“待评估”状态与下一轮最少补问。

## 质量红线

1. 不编造、不拔高、不抹平冲突。
2. Gate 输出建议而非授权；不得写入 `render_authorized`。
3. `information_integrity` FAIL 不得进入 override 路径。
4. `business_risk` FAIL 用户可显式接受，必须填写理由、确认人与时间。
5. blocker 缺口不得以“先出图再补”绕过。
6. minor 缺口必须显式接受风险，不允许静默忽略。
7. 核心推断未接受/拒绝的不得建议 `gate_recommendation=pass`。
8. 确认人未填写且角色不清的不得建议 `gate_recommendation=pass`。
9. 不调用 Canvas 渲染；本 skill 只输出建议报告。
10. `information_integrity` FAIL 时 `override_eligible=false`；主 Agent 不向用户提供 override 选项。
11. 不修改 MVL M2，不读取或写入 `state.modules.M2`。
