---
name: module-conclusion-gate
description: 对 MVL 工作坊单模块的确认包（Mx-v{N}.md）做质量建议与风险分级，输出 gate_recommendation 供主 Agent 决策。Gate 只输出建议，不决定最终渲染授权；用户授权由主 Agent 根据 Gate 报告与用户决策写入。本 skill 不生成 HTML，也不替用户补结论。
---

# 模块结论质量建议

把"内容已讨论过"与"内容足以成为项目结论"分开。本 skill 只做质量建议和风险分级，**不决定最终渲染授权**。最终授权由主 Agent 在用户决策后写入 `state.json` 的 `render_authorized` 与 `confirmation_mode` 字段。

## 定位

**质量建议器（Gate）**：本 skill 是 Pratyaya MVL Expert 的"质量建议"能力。完整工作流由主 agent 编排（见 `agents/pratyaya.md` 步骤 5–7），本 skill 不编排主流程，只在被调用时输出 Gate 建议报告（Markdown）。

本 skill 不调用 Canvas 渲染；Gate 报告输出后由主 Agent 展示给用户，等待用户决策并触发 `canvas-render`。

## 输入与输出

**输入**：

- `modules/Mx-v{N}.md`（确认包，Markdown 格式，唯一事实源）
- `references/Mx-gate.md`（本模块的放行条件与稳定 ID，位于本 Skill 的 `references/` 子目录）
- 当前状态（来自主 agent 维护的 `state.json`）

**输出**：

- Gate 建议报告（Markdown 文本），结构见下文"Gate 评估流程"
- `gate_recommendation: pass / fail`
- `override_eligible: true / false`（业务风险 FAIL 时才可能为 true）
- 不输出 `render_authorized`；不写最终授权。

## Gate 评估流程

**触发**：主 agent 步骤 5 完成（确认包已生成、状态为 `review_ready`），主 Agent 在步骤 6 自动调用本 skill，不等用户先回复"确认 vN"。

1. 读取 `modules/Mx-v{N}.md`（确认包第 1–11 节业务内容；第 12 节为治理元数据，不参与评估）；
2. 读取 `references/Mx-gate.md`（本模块的放行条件 + 稳定 ID + 分类 + 风险等级）；
3. 逐项对照评估，输出 Gate 建议报告（Markdown）：

```markdown
## Gate 评估报告 — M{N} v{X}

> 评估时间：{ISO 8601 datetime}
> 模块：M{N} — {模块名}
> 确认包版本：v{X}
> gate_recommendation：pass / fail
> override_eligible：true / false

### 评估项

| ID | 检查项 | 结果 | 分类 | 风险等级 | 来源 ID | 影响 | 建议 |
|---|---|---|---|---|---|---|---|
| M{N}-GATE-01 | ... | PASS / FAIL | information_integrity / business_risk | low / medium / high | M{N}-Gxx / M{N}-Ixx / section | ... | ... |

### Gate 建议

- gate_recommendation：pass / fail
- override_eligible：true / false
- 未通过项摘要：（仅 fail 时列出）

### 用户可选动作

- Gate PASS：确认 v{X} / 返回修订
- 仅业务风险 FAIL：显式 override 并填写理由 / 返回修订
- 含信息完整性 FAIL：补问或修订
```

4. 状态更新规则（由主 agent 执行，不在本 skill 内部）：
   - Gate 报告只写入 `gate_recommendation` 字段；
   - `render_authorized` 与 `confirmation_mode` 只能由主 Agent 在用户决策后写入；
   - Gate FAIL 时**不自动**回退状态；状态仍为 `review_ready`，等待用户决策。

## 评估项与稳定 ID

六个模块的每条放行条件在 `references/Mx-gate.md` 中拥有稳定 ID：

```text
M1-GATE-01
M1-GATE-02
...
M6-GATE-07
```

评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响和建议。

## 分类与可 override 关系

每个评估项必须分类为 `information_integrity` 或 `business_risk`，且与"可 override 性"有明确对应：

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立（核心事实源、当前版本、确认对象、确认包与授权版本一致等） | **否** |
| `business_risk` | 结论已有事实基础，但现实验证仍不完整（生产环境验证、数据样本、外部依赖、业务假设等） | **是**（填写理由后） |

> **核心规则**：用户可以接受现实中的业务风险，但不能通过 override 把不存在的信息变成事实。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得正式 override。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使当前日程的核心产出或对应 Canvas 模块无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变范围、方案或验证判断 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

每个缺口必须包含：缺什么、缺失影响、最少补问、状态（`open` / `closed` / `accepted_risk`）。

严重度（blocker / major / minor）与分类（information_integrity / business_risk）是两个维度：

- `information_integrity`：无论严重度，均不可正式 override；
- `business_risk`：用户可在看见影响并填写理由后 override；
- minor 仍不得静默忽略，必须关闭或显式接受。

## 结论确认格式

确认包"详情 7：结论登记表"使用以下固定列：

| ID | 结论 | 类型 | 共识状态 |
|---|---|---|---|
| M{N}-C01 | ... | fact / decision / hypothesis / recommendation | 共识 / 待确认 / 争议 |

> **不保留 evidence 引用列**。按 MVL 产品审查 2.2 节立场，结论合法性来自"本模块已通过'确认 vN'"，不依赖逐字稿段落级引用。

确认时必须让用户看到：

1. 当前模块固定 section（参见 `references/Mx-gate.md`）；
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

**跨模块 caveat 检查**：

- 扫描六个当前版本的 `confirmation_mode`；
- 收集所有 `confirmation_mode=override` 模块的 `override_audit.items`；
- 检查每项业务风险是否影响其他模块；
- 若下游模块依赖被 override 的假设或未验证项，必须显式标注，或回退相关模块升版重审；
- 不得因模块已进入 `rendered` 而忽略 caveat。

如果存在跨模块对齐冲突或 caveat 跨模块未处理，必须回退相关模块升版和重审，不在全局页面中静默修正。

## 草稿与正式版

- 草稿 Canvas 仅用于继续讨论，必须带"草稿 / 未确认 / 禁止用于管理层决策"水印。
- 草稿不得进入全局 Canvas 或领导汇报。
- 正式 Canvas 必须来自已确认的同一版本确认包，且 `state.json` 的 `render_authorized=true`、`confirmation_mode ∈ {gate_pass, override}`。
- 闸门评估未完成时（`gate_recommendation=pending`），不得调用 Canvas 渲染；只输出"待评估"状态与下一轮最少补问。

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
2. Gate 输出建议而非授权；不得写入 `render_authorized`。
3. `information_integrity` FAIL 不得进入 override 路径。
4. `business_risk` FAIL 用户可显式接受，必须填写理由、确认人与时间。
5. blocker 缺口不得以"先出图再补"绕过。
6. minor 缺口必须显式接受风险，不允许静默忽略。
7. 核心推断未接受/拒绝的不得建议 `gate_recommendation=pass`。
8. 确认人未填写或角色不清的不得建议 `gate_recommendation=pass`。
9. 不调用 Canvas 渲染；本 skill 只输出建议报告。
