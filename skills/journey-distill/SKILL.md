---
name: journey-distill
description: 把 User Journey（用户旅程）工作坊讨论产物提炼为 Markdown 资产。先做 Key Points 概览抽取（生成动态阶段、5 行合并结构、痛点与机会和质量信号的讨论地图），再按用户决策做原子提炼，输出唯一事实源 JOURNEY-{slug}-v{N}.md 确认包。收到 Journey Key Points 抽取请求、原子提炼请求、确认包生成请求时使用。
---

# journey-distill：用户旅程提炼

把 Key Points 概览与 Journey 框架结合，形成经过对齐的、唯一事实源的确认包（`modules/JOURNEY-{slug}-v{N}.md`）。完成标准是“真实呈现用户当前旅程、痛点与机会和质量判断”，不是“画出完整漂亮的流程图”。

所有 Journey 产物必须绑定 instance slug。slug 由主 Agent 提供，必须为 kebab-case，并与 `state.journey.{slug}.slug` 一致；本 Skill 不自动生成 `default` slug。

质量鉴别采用正式画布外显方式：`user_perspective`、`business_outcome`、`pain_opportunity_visible`、`no_solution_bias` 四维度必须写入确认包第 6a 节，并在后续 Canvas 中作为治理区块呈现，而不是只作为 Gate 内部判断。

## 定位

**分步提炼流程**：本 skill 是 Pratyaya Canvas Expert 的“Journey 提炼与确认包生成”能力。完整的 Journey 工作流由主 agent 编排（见 `agents/pratyaya.md`），本 skill 不编排主流程，只在被调用时执行以下两个独立 Stage：

- **Stage 1：Key Points 抽取** — 输入转写，输出 `modules/JOURNEY-{slug}-keypoints.md`（讨论地图，30 秒浏览）。
- **Stage 2：原子提炼** — 输入转写 + Key Points + Journey 框架，输出 `modules/JOURNEY-{slug}-v{N}.md`（确认包，唯一事实源）。

调用顺序由主 agent 决定，本 skill 不强制。本 skill 不调用 Canvas 渲染、不执行闸门判定。

## 唯一内容边界

开始任何 Stage 前必须读取：

1. Journey 框架 `frameworks/journey-frame.md`：动态阶段、5 行合并结构、质量鉴别四维度、最低结论要求；
2. `references/journey-spec.md`：Journey Key Points 与确认包的固定 section 定义、ID 约定、Canvas 锚点映射。

只提取用户实际讨论的内容。框架之外的方法或术语不自动成为必填项、补问项或放行条件；只有用户明确使用时，才按原话记录。

## 与 MVL 的边界

Journey 是独立一等公民画布，不影响 MVL：

- 不修改、覆盖或依赖 MVL M2 的 `skills/mvl-distill/references/methods/09-user-journey.md`。
- 不读取或写入 `state.modules.M2`。
- 不把 MVL method09 的七要素作为正式 Journey 主表契约。
- 独立 Journey 结论可被用户人工引用到 MVL，但系统层面不自动同步。

## 引用层级（重要）

**不引用逐字稿段落**。与 GC / HMW / MVL 蒸馏一致的立场：逐字稿不具备段落级权威性，正式引用应基于：

- **Key Points 内的 section**（如“Journey 阶段覆盖度初判”）
- **确认包自身的 section**（如“Journey 缺口表 G01”）

逐字稿从“证据”降级为“背景材料”，仅作存档，不作引用源。

## 输入与输出

| Stage | 输入 | 输出 |
|---|---|---|
| Stage 1：Key Points 抽取 | 逐字稿（文本或文件路径） | `modules/JOURNEY-{slug}-keypoints.md`（第 N 轮） |
| Stage 2：原子提炼 | 逐字稿 + Key Points + Journey 框架 | `modules/JOURNEY-{slug}-v{N}.md`（确认包，唯一事实源） |
| 补问分支 | 确认包缺口 / Key Points 缺口 | `modules/JOURNEY-{slug}-gaps.md` |

Stage 1 与 Stage 2 可独立调用，不强制串联。但 Stage 2 的输入依赖 Stage 1 的 Key Points。

Stage 2 完成后交给主 agent 触发闸门（`journey-gate`），不直接进入 Canvas 渲染。

## Stage 1：Key Points 抽取

**目标**：在 30 秒内让用户了解“这次讨论了什么、阶段覆盖度如何、痛点与机会和质量信号在哪里、缺什么”。

**触发**：主 agent Journey 工作流对应步骤，输入为逐字稿（已由主 agent 存档为 `transcripts/journey-TXX-raw.md`）。

**输出**：`modules/JOURNEY-{slug}-keypoints.md`，结构如下。

### JOURNEY-{slug}-keypoints.md 模板

```markdown
# User Journey Key Points（第 X 轮）

> 生成时间：{YYYY-MM-DD HH:MM}
> 画布类型：User Journey（用户旅程）画布
> 轮次：第 X 轮
> 数据源：transcripts/journey-TXX-raw.md

## 1. 讨论主题

本次讨论覆盖了哪些用户、场景、任务或流程（每个 1-2 句，最多 5 条）：

- **主题 1**：...
- **主题 2**：...

## 2. 关键主张

按「阶段 / 痛点与机会 / 质量信号」组织（每项 1-2 句）：

- **阶段**：...
  - 主张 1：...
- **痛点**：...
  - 主张 1：...
- **质量信号**：...
  - 主张 1：...

## 3. 明显矛盾或未对齐

讨论中出现的内部不一致或分歧点（最多 5 条）：

- 矛盾 1：...（如一处说“系统自动完成”，另一处又说“人工反复确认”）
- 矛盾 2：...

## 4. 阶段覆盖度初判

对照 Journey 框架（`frameworks/journey-frame.md`），粗略评估覆盖情况：

| 阶段序号 | 阶段名 | 行动 | 触点与系统 | 情绪 | 痛点 | 机会 | 覆盖状态 | 简评 |
|---|---|---|---|---|---|---|---|---|
| 1 | ... | 已覆盖 / 部分覆盖 / 未涉及 | ... | ... | ... | ... | 已覆盖 / 部分覆盖 / 未涉及 | ... |

## 5. 质量覆盖度初判

| 维度 | 状态 | 简评 |
|---|---|---|
| user_perspective | 已判定 / 未判定 | ... |
| business_outcome | 已判定 / 未判定 | ... |
| pain_opportunity_visible | 已判定 / 未判定 | ... |
| no_solution_bias | 已判定 / 未判定 | ... |

## 6. 用户决策提示

> 基于以上概览，请选择：**提炼** / **补问** / **先看个样子**
```

**约束**：

- 长度控制：每节最多 5 条，供 30 秒快速浏览。
- 不做原子提炼、不写结论登记表、不评估 Gate。
- 末尾必须输出用户决策提示。
- 覆盖度初判必须使用 5 行合并结构，不得改为七要素。

## Stage 2：原子提炼

**目标**：将 Key Points 转化为经过对齐的、唯一事实源的确认包 `JOURNEY-{slug}-v{N}.md`。

**触发**：主 agent Journey 工作流对应步骤（用户回复“提炼”后调用）。

**输入**：

- 逐字稿（已存档）
- `modules/JOURNEY-{slug}-keypoints.md`（Stage 1 产物）
- `frameworks/journey-frame.md`（Journey 框架）

**输出**：`modules/JOURNEY-{slug}-v{N}.md`，全 Markdown，结构如下。

### JOURNEY-{slug}-v{N}.md 确认包模板

```markdown
# User Journey 确认包 v{N}

> 画布类型：User Journey 用户旅程画布
> 版本：v{N}（基于第 X 轮 Key Points）
> 状态：{draft / gaps_open / review_ready / confirmed / rendered}
> 生成时间：{ISO 8601 datetime，由 skill 生成时写入}
> 确认人：{待填写}
> 确认人角色（可选）：{待填写}
> 确认时间：{待填写，ISO 8601 datetime}

---

## 必展项（紧凑前置）

### 1. 一句话结论

{≤50 字，概括这条旅程的核心痛点与机会}

### 2. 对齐摘要

- 共识：x 项
- 分歧：x 项
- 决策：x 项

### 3. 阻塞项

{如有 blocker，第一条就警示标注；无则写“无”}

### 4. 缺口速览

- blocker：x（open / closed / accepted_risk）
- major：x（open / closed / accepted_risk）
- minor：x（open / closed / accepted_risk）

### 5. 待确认版本

v{N}

---

## 详情

### 6. 阶段地图

| 阶段序号 | 阶段名 | 行动 | 触点与系统 | 情绪 | 痛点 | 机会 | 来源引用 |
|---|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | ... | ... | ... | Journey 关键主张 X |
| 2 | ... | ... | ... | ... | ... | ... | ... |

> 此节为 `render-contract-journey.md` 中 `journey-stage-*` 动态锚点的事实源。阶段数量由本表数据行决定，不使用固定 7 槽位。

### 6a. 质量鉴别

| 维度 | 判定 | 依据 |
|---|---|---|
| user_perspective（用户视角） | 通过 / 不通过 | ... |
| business_outcome（到达业务结果） | 通过 / 不通过 | ... |
| pain_opportunity_visible（痛点与机会可见） | 通过 / 不通过 | ... |
| no_solution_bias（未预设方案） | 通过 / 不通过 | ... |

### 6b. 痛点与机会

| ID | 阶段 | 类型 | 来源 | 描述 | 影响 | 机会判断 | 来源引用 |
|---|---|---|---|---|---|---|---|
| JOURNEY-F01 | 阶段 2 | pain_point / opportunity | user_stated / inferred_from_pain_point / inferred_from_quality | ... | ... | ... | ... |

### 7. 结论登记表

| ID | 结论 | 类型 | 共识状态 |
|---|---|---|---|
| JOURNEY-C01 | ... | fact / decision / hypothesis / recommendation | 共识 / 待确认 / 争议 |

### 8. 缺口表

| ID | 等级 | 状态 | 描述 | 缺失影响 | 最少补问 |
|---|---|---|---|---|---|
| JOURNEY-G01 | blocker | open | ... | ... | ... |

### 9. 推断表

| ID | 推断 | 影响 | 状态 |
|---|---|---|---|
| JOURNEY-Inf01 | ... | ... | 待接受 / 待拒绝 |

### 10. 关键证据引用

引用 Key Points / 确认包内 section（不引用逐字稿段落）。

### 11. 待用户决策

> 请在以下三项中任选其一回复：
> - **确认 v{N}**：Gate 已通过，希望对当前版本作最终确认并授权渲染。
> - **override**：Gate 报告含 `business_risk` FAIL，我已阅读影响并接受该风险。
> - **补问 / 修订**：当前版本存在需要补问的问题或需修改的业务内容。

---

## 12. Gate 与用户决策
（治理元数据，由 Gate 流程与主 Agent 写入，不触发业务升版）
```

## 补问分支：JOURNEY-{slug}-gaps.md

用户选择“补问”时，输出 `modules/JOURNEY-{slug}-gaps.md`。每条补问必须包含：

- 缺口 ID（`JOURNEY-Gxx`）
- 缺失判断点
- 缺失影响
- 最少补问

`JOURNEY-{slug}-gaps.md` 与确认包第 8 节缺口表同源，不引入独立 ID 空间。

## 质量红线

1. 不编造、不拔高、不抹平冲突。
2. 关键数字、决策和结论必须有 Key Points 内依据。
3. 阶段数量低于 3 时，确认包必须标为 `gaps_open`，不得进入 `review_ready`。
4. 每个阶段 5 行字段不能用空白占位伪装为已覆盖；缺失必须显式登记为缺口。
5. 推断必须独立登记，不得混入结论或 Canvas 主表。
6. 质量鉴别四维度必须在讨论中有线索，不能完全由 LLM 构造。
7. 主表不得提前写入解决方案、AI 应用判断或 Future Journey 设计；本画布只表达当前真实旅程。
8. 未完成人工确认前，不视为提炼完成。
