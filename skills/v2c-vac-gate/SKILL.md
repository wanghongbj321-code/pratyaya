---
name: v2c-vac-gate
description: 对 V2C Value Attribution Canvas（VAC，价值归因画布）的确认包（V2C-VAC-{slug}-v{N}.md）做质量建议与风险分级，输出 gate_recommendation 与 override_eligible 供主 Agent 决策。Gate 只输出建议报告，不决定最终渲染授权；用户授权由主 Agent 根据 Gate 报告与用户决策写入。本 skill 不生成 HTML、不写 state.json、不替用户补齐归因结论。
---

# V2C VAC 结论质量建议

把“归因链已经写得完整”与“归因链足以作为正式 V2C VAC 结论”分开。本 Skill 只做质量建议和风险分级，**不决定最终渲染授权**。最终授权由主 Agent 在用户决策后写入 `state.json` 的 `render_authorized` 与 `confirmation_mode` 字段。

V2C VAC 的思路来源于王鸿的 V2C FDE 工作方法论。Gate 的目标不是证明价值已经发生，而是审查 AI-enabled Capability 到 Observable Change、Business Impact 与 Value 的归因假设是否诚实、可验证、可治理。

## 定位

**质量建议器（Gate）**：本 Skill 是 Pratyaya Canvas Expert 的 V2C VAC 治理层能力。完整工作流由主 Agent 编排（见 `agents/pratyaya.md`），本 Skill 不编排主流程，只在被调用时输出 Gate 建议报告（Markdown）。

本 Skill 不调用 Canvas 渲染；Gate 报告输出后由主 Agent 展示给用户，等待用户决策并触发后续流程。

## 输入与输出

**输入**：

- `modules/V2C-VAC-{slug}-v{N}.md`（确认包，Markdown 格式，唯一事实源）
- `references/V2C-gate.md`（V2C VAC 放行条件与稳定 ID，位于本 Skill 的 `references/` 子目录）
- `../v2c-vac-distill/references/v2c-vac-spec.md`（字段、section、ID、证据状态与缺口定义）
- 当前状态（来自主 Agent 维护的 `state.json` 的 `v2c_vac.{slug}` 区块）

**输出**：

- Gate 建议报告（Markdown 文本），结构见下文“Gate 评估流程”
- `gate_recommendation: pass / fail`
- `override_eligible: true / false`（仅 `business_risk` FAIL 时才可能为 true）
- 不输出 `render_authorized`；不写最终授权；不写 `state.json`。

## 必读资料

开始评估前必须读取：

1. `references/V2C-gate.md`：V2C VAC 专用 Gate 条件、稳定 ID、分类、风险等级、来源约定；
2. `../v2c-vac-distill/references/v2c-vac-spec.md`：确认包 section、字段契约、证据状态、Attribution Gap 与红线。

若上述任一文件不可读，输出 Gate FAIL，分类为 `information_integrity`，并建议回到环境检查或补齐 Skill 文件。

## Gate 评估流程

**触发**：主 Agent V2C VAC 工作流中，确认包已生成、状态为 `review_ready` 或用户要求对当前确认包做 Gate 审查时调用本 Skill。

1. 读取 `modules/V2C-VAC-{slug}-v{N}.md`。
2. 只评估确认包第 1-12 节业务内容；第 13 节是治理元数据，不参与业务内容质量判定。
3. 校验 `{slug}`、`v{N}`、`canvas_type=v2c-vac`、`generation_path` 与 `state.v2c_vac.{slug}` 一致。
4. 读取 `references/V2C-gate.md`。
5. 逐项对照 `V2C-GATE-01` 到 `V2C-GATE-12`，输出 Gate 建议报告。
6. Gate 报告文件名使用 `modules/V2C-VAC-{slug}-gate-report-v{N}.md`；slug 不进入 `V2C-GATE-*` 稳定 ID。

```markdown
## Gate 评估报告 — V2C VAC v{N}

> 评估时间：{ISO 8601 datetime}
> 画布类型：V2C Value Attribution Canvas
> canvas_type：v2c-vac
> instance slug：{slug}
> generation_path：pipeline / transcript-direct
> 确认包版本：v{N}
> gate_recommendation：pass / fail
> override_eligible：true / false

### 评估项

| ID | 检查项 | 结果 | 分类 | 风险等级 | 来源 ID | 影响 | 建议 |
|---|---|---|---|---|---|---|---|
| V2C-GATE-01 | 确认包身份与 state 一致 | PASS / FAIL | information_integrity | low | state.v2c_vac.{slug} | ... | ... |
| V2C-GATE-02 | 画布类型与生成路径明确 | PASS / FAIL | information_integrity | low | 确认包头部 | ... | ... |

### Gate 建议

- gate_recommendation：pass / fail
- override_eligible：true / false
- 未通过项摘要：（仅 fail 时列出）

### Override 可行性

- 含 `information_integrity` FAIL：不可 override，必须补问或修订
- 仅 `business_risk` FAIL：可由用户显式 override，必须填写理由、确认人、确认时间和补救措施

### 用户可选动作

- Gate PASS：确认 v{N} / 返回修订
- 仅业务风险 FAIL：显式 override 并填写理由 / 返回修订
- 含信息完整性 FAIL：补问或修订
```

## 状态更新边界

本 Skill 不更新状态。主 Agent 可以在用户看见 Gate 报告后执行后续状态动作，但这些动作不属于本 Skill：

- Gate 报告中的 `gate_recommendation` 可由主 Agent记录到当前 instance 的治理字段；
- `render_authorized` 与 `confirmation_mode` 只能由主 Agent 在用户决策后写入；
- Gate FAIL 时不自动回退状态；状态仍等待用户决策；
- 业务内容变化必须升版、重跑 Gate、重新确认；
- 仅第 13 节治理元数据写入不触发业务升版。

## 评估项与稳定 ID

12 条放行条件在 `references/V2C-gate.md` 中拥有稳定 ID：

```text
V2C-GATE-01
V2C-GATE-02
V2C-GATE-03
V2C-GATE-04
V2C-GATE-05
V2C-GATE-06
V2C-GATE-07
V2C-GATE-08
V2C-GATE-09
V2C-GATE-10
V2C-GATE-11
V2C-GATE-12
```

评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响和建议。

## 分类与可 override 关系

每个评估项必须分类为 `information_integrity` 或 `business_risk`，且与“可 override 性”有明确对应：

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立，包括身份一致、字段覆盖、语义分层、证据状态、缺口登记与推断登记 | **否** |
| `business_risk` | 归因链已有事实基础，但价值判断、Baseline、验证计划或下一步投入建议仍有业务不确定性 | **是**（填写理由后） |

> 核心规则：用户可以接受现实中的业务风险，但不能通过 override 把不存在的信息、未登记的缺口或未验证的价值变成事实。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得进入正式 override。

## V2C-GATE 与 V2C-AG 的边界

`V2C-GATE-*` 是 Gate 条件稳定 ID，用于 Gate 报告、override 审计和后续授权检查。

`V2C-AGxx` 是确认包中的 Attribution Gap ID，用于描述归因断点、补问和验证计划。

边界规则：

1. Gate 报告的 `来源 ID` 可以引用 `V2C-AGxx`、确认包 section 或 `state.v2c_vac.{slug}`。
2. `override_audit.assessment_id` 必须引用 `V2C-GATE-*`。
3. 不得把 `V2C-AGxx` 写入 `override_audit.assessment_id`。
4. 不得把 Gate 条件写成新的 Attribution Gap。
5. Gate 可指出某个 `V2C-AGxx` 未关闭或等级不正确，但该判定本身仍归属于对应的 `V2C-GATE-*`。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使主归因链或 Gate 评估无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变归因链、价值判断或下一步建议 | 必须关闭或明确接受风险 |
| `minor` | 不改变核心归因判断 | 可后续补齐或明确接受风险 |

严重度（blocker / major / minor）与分类（information_integrity / business_risk）是两个维度：

- `information_integrity`：无论严重度，均不可正式 override；
- `business_risk`：用户可在看见影响并填写理由后 override；
- minor 仍不得静默忽略，必须关闭或显式接受。

## 证据状态规则

V2C 使用 `F / H / ? / E` 四类证据状态：

| 状态 | Gate 处理 |
|---|---|
| `F` | 可作为当前项目事实或明确来源线索 |
| `H` | 可进入假设链，但必须有验证计划或登记为归因风险 |
| `?` | 必须进入 `V2C-AGxx` 或推断/补问，不得静默放行 |
| `E` | 必须有 Pilot、业务数据、现场观察或对照验证说明 |

估算、行业基准或外部材料若未在当前项目验证，不得标为 `E`。无 Baseline 时不得输出量化改善幅度或收益承诺。

## 草稿与正式版

- 草稿 Canvas 仅用于继续讨论，必须带“草稿 / 未确认 / 禁止用于管理层决策”水印。
- 草稿不进入正式输出。
- 正式 Canvas 必须来自已确认、同版本、已授权的确认包，且对应 `state.json.v2c_vac.{slug}.render_authorized=true`、`confirmation_mode ∈ {gate_pass, override}`。
- 闸门评估未完成时（`gate_recommendation=pending`），不得调用 Canvas 渲染；只输出“待评估”状态与下一轮最少补问。

## 质量红线

1. 不编造、不拔高、不抹平冲突。
2. Gate 输出建议而非授权；不得写入 `render_authorized`。
3. 不写 `state.json`，不生成 HTML，不调用 Canvas 渲染。
4. `information_integrity` FAIL 不得进入 override 路径。
5. `business_risk` FAIL 用户可显式接受，必须填写理由、确认人与时间。
6. blocker 缺口不得以“先出图再补”绕过。
7. 任何 `?` 关系不得静默放行；必须进入缺口或推断表。
8. 无 Baseline 时不得建议通过含量化收益的确认包。
9. 未验证的外部估算、行业基准或管理口号不得标为 `E`。
10. 不得从 Adoption / Usage 直接推导 Business Impact。
11. `override_audit.assessment_id` 必须使用 `V2C-GATE-*`，不得使用 `V2C-AGxx`。
12. 第 13 节是治理元数据区，不参与业务内容质量判定。
