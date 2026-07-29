---
name: mvl-distill
description: 把 MVL 工作坊讨论产物提炼为模块化 Markdown 资产。先做 Key Points 概览抽取（对应 NotebookLM Mind Map / Briefing Doc），再按用户决策做原子提炼，输出唯一事实源 Mx-v{N}.md 确认包。收到 Key Points 抽取请求、原子提炼请求、确认包生成请求时使用。
---

# mvl-distill：模块化提炼

把 Key Points 概览与阶段框架结合，形成经过对齐的、唯一事实源的确认包（`modules/Mx-v{N}.md`）。完成标准是"经业务方、技术方、管理层各自动用都能成立的模块资产"，不是"看起来内容丰富"。

## 定位

**NotebookLM 场景化提炼流程**：本 skill 是 MVL 助教的"提炼与确认包生成"能力。完整的 MVL 工作流由主 agent 编排（见 `agents/mvl-workshop-facilitator.md`），本 skill 不编排主流程，只在被调用时执行以下两个独立 Stage：

- **Stage 1：Key Points 抽取** — 输入转写，输出 `modules/Mx-keypoints.md`（讨论地图，30 秒浏览）。
- **Stage 2：原子提炼** — 输入转写 + Key Points + 阶段框架，输出 `modules/Mx-v{N}.md`（确认包，唯一事实源）。

调用顺序由主 agent 决定，本 skill 不强制。本 skill 不调用 Canvas 渲染、不执行闸门判定。

## 唯一内容边界

开始任何 Stage 前必须读取：

1. 当前模块 `frameworks/m{1-6}-*.md`：讨论目标、引导问题、最低结论要求；
2. `references/workshop-canvas-map.md`：日程、模块产出与 Canvas 大/小模块的映射；
3. `references/mvl-canvas-spec.md`：最终 Canvas 固定结构。

只提取用户实际讨论的内容。其他方法文件（如 `references/methods/`）不自动成为必填项、补问项或放行条件；只有用户明确使用某个方法时，才可按原话记录为模块详情。

## 引用层级（重要）

**不引用逐字稿段落**。按 MVL 产品审查 2.2 节立场，头脑风暴的逐字稿不具备段落级权威性——同一人在讨论前后可能表达矛盾立场、口语化试探与跑题占据大量文本、真正的事实来自"确认环节达成的共识"而非某段话。引用应基于：

- **Key Points 内的 section**（如"M1 关键主张 3"）
- **确认包自身的 section**（如"M1 缺口表 G02"）

逐字稿从"证据"降级为"背景材料"，仅作存档，不作引用源。

## 输入与输出

| Stage | 输入 | 输出 |
|---|---|---|
| Stage 1：Key Points 抽取 | 逐字稿（文本或文件路径） | `modules/Mx-keypoints.md`（第 N 轮） |
| Stage 2：原子提炼 | 逐字稿 + Key Points + 阶段框架 | `modules/Mx-v{N}.md`（确认包，唯一事实源） |

Stage 1 与 Stage 2 可独立调用，不强制串联。但 Stage 2 的输入依赖 Stage 1 的 Key Points。

Stage 2 完成后交给主 agent 触发闸门（`module-conclusion-gate`），不直接进入 Canvas 渲染。

## Stage 1：Key Points 抽取

**目标**：在 30 秒内让用户了解"这次讨论了什么、覆盖度如何、缺什么"。

**触发**：主 agent 步骤 1（Key Points 抽取），输入为逐字稿（已由主 agent 存档为 `transcripts/module-N-TXX-raw.md`）。

**输出**：`modules/Mx-keypoints.md`，结构如下。

### Mx-keypoints.md 模板

```markdown
# M{N} Key Points（第 X 轮）

> 生成时间：{YYYY-MM-DD HH:MM}
> 模块：M{N} — {模块名}
> 轮次：第 X 轮
> 数据源：transcripts/module-N-TXX-raw.md

## 1. 讨论主题

本次讨论覆盖了哪些主题（每个 1-2 句，最多 5 条）：

- **主题 1**：...
- **主题 2**：...

## 2. 关键主张

每个主题下的主要观点（每项 1-2 句）：

- **主题 1**
  - 主张 1：...
  - 主张 2：...
- **主题 2**
  - 主张 1：...

## 3. 明显矛盾或未对齐

讨论中出现的内部不一致或分歧点（最多 5 条）：

- 矛盾 1：...
- 矛盾 2：...

## 4. 覆盖度初判

对照 M{N} 框架（`frameworks/m{N}-*.md`），粗略评估覆盖情况：

| 必填 section | 状态 | 简评 |
|---|---|---|
| {section 1} | 已覆盖 / 部分覆盖 / 未涉及 | ... |
| {section 2} | 已覆盖 / 部分覆盖 / 未涉及 | ... |

## 5. 用户决策提示

> 基于以上概览，请选择：**提炼** / **补问** / **先看个样子**
```

**约束**：

- 长度控制：每节最多 5 条，供 30 秒快速浏览。
- 不做原子提炼、不写结论登记表、不评估缺口。
- 末尾必须输出用户决策提示。
- 跨轮次覆盖：第 N 轮 Key Points 覆盖第 N-1 轮摘要（同文件覆盖式更新，保留最后一轮）。

## Stage 2：原子提炼

**目标**：将 Key Points 转化为经过对齐的、唯一事实源的确认包 `Mx-v{N}.md`。

**触发**：主 agent 步骤 2（用户回复"提炼"后调用）。

**输入**：
- 逐字稿（已存档）
- `modules/Mx-keypoints.md`（Stage 1 产物）
- `frameworks/m{1-6}-*.md`（阶段框架）

**输出**：`modules/Mx-v{N}.md`，全 Markdown，结构如下。

### Mx-v{N}.md 确认包模板

```markdown
# M{N} 确认包 v{N}

> 模块：M{N} — {模块名}
> 版本：v{N}（基于第 X 轮 Key Points）
> 状态：待用户确认
> 确认人：{待填写}
> 确认时间：{待填写}

---

## 必展项（紧凑前置）

### 1. 一句话结论

{≤50 字}

### 2. 对齐摘要

- 共识：x 项
- 分歧：x 项
- 决策：x 项

### 3. 阻塞项

{如有 blocker，第一条就警示标注；无则写"无"}

### 4. 缺口速览

- blocker：x
- major：x
- minor：x

### 5. 待确认版本

v{N}

---

## 详情

### 6. 当前模块固定字段预览

| section | 内容 | 来源引用 |
|---|---|---|
| {section 1} | ... | M{N} 关键主张 X / M{N} 覆盖度初判 |
| {section 2} | ... | ... |

> section 名称固定，参见 `references/workshop-canvas-map.md` 的"模块 Markdown 必填 section"表。

### 7. 结论登记表

| ID | 结论 | 类型 | 共识状态 |
|---|---|---|---|
| M{N}-C01 | ... | fact / decision / hypothesis / recommendation | 共识 / 待确认 / 争议 |
| M{N}-C02 | ... | ... | ... |

> 共识状态由本模块的"对齐检查"环节写入，不由本 skill 写入。
> 本表只记录"经过讨论产生的结论"；推断不写入此表。

### 8. 缺口表

| ID | 等级 | 描述 | 缺失影响 | 最少补问 |
|---|---|---|---|---|
| M{N}-G01 | blocker | ... | ... | ... |
| M{N}-G02 | major | ... | ... | ... |
| M{N}-G03 | minor | ... | ... | ... |

> 等级定义：blocker = 使核心产出/Canvas 模块无法成立；major = 显著改变范围/方案/验证判断；minor = 不改变核心结论，可后续补齐或明确接受风险。

### 9. 推断表

| ID | 推断 | 影响 | 状态 |
|---|---|---|---|
| M{N}-I01 | ... | ... | 待接受 / 待拒绝 |

> 推断不写入结论登记表与固定 Canvas section。
> "待接受"或"待拒绝"由本模块的"对齐检查"环节写入，不由本 skill 写入。

### 10. 关键证据引用

引用 Key Points / 确认包内 section（不引用逐字稿段落）：

- M{N} 关键主张 X 中关于 ...
- M{N} 覆盖度初判：{section} {状态}
- M{N} 缺口表 G{XX}（如已在本表登记）

### 11. 待用户确认

> 请回复"**确认 v{N}**"以放行闸门并生成画布，或指出需要修正的内容。
```

**约束**：

- 引用格式：仅引用 Key Points 与确认包自身的 section，**不引用逐字稿段落**。
- 推断必须独立登记，不写入结论登记表。
- 缺口必须说明"缺失影响"，不能只说"信息不足"。
- 不调用 Canvas 渲染、不执行闸门判定。
- 状态写入由主 agent 在"确认 vN"后执行，不在本 skill 内部。
- 版本号管理：升版时 vN → vN+1，旧版本归档为 `modules/Mx-v{N}.md.previous`，不清空。

## 模块索引

| 模块 | 框架 | Canvas 贡献 |
|---|---|---|
| M1 | `frameworks/m1-intent.md` | Intent |
| M2 | `frameworks/m2-user.md` | User + 现状流程 |
| M3 | `frameworks/m3-workflow.md` | Intent 回填 + Workflow 草案 |
| M4 | `frameworks/m4-agent-context.md` | Workflow 冻结 + Agent Team + Context |
| M5 | `frameworks/m5-validation.md` | Validation：执行、价值、信任与风控 |
| M6 | `frameworks/m6-summary.md` | Validation：持续进化 + 全局总结 |

## 质量红线

1. 不编造、不拔高、不抹平冲突。
2. 关键数字、决策和结论必须有 Key Points 内的依据。
3. 日程没要求、样图没包含、用户没讨论的内容，不得自动加入。
4. 模板 section 缺失时标缺口，不能用通用话术补满。
5. 推断必须独立登记，不得混入结论或固定 Canvas section。
6. 不引用逐字稿段落；引用应基于 Key Points / 确认包内的 section。
7. 未完成人工确认前，不视为提炼完成；状态由主 agent 在"确认 vN"后写入。
