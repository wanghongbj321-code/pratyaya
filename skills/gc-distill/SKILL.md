---
name: gc-distill
description: 把黄金圈（Golden Circle）工作坊讨论产物提炼为 Markdown 资产。先做 Key Points 概览抽取（生成 WHY / HOW / WHAT 三层的讨论地图），再按用户决策做原子提炼，输出唯一事实源 GC-{slug}-v{N}.md 确认包。收到黄金圈 Key Points 抽取请求、原子提炼请求、确认包生成请求时使用。
---

# gc-distill：黄金圈模块化提炼

把 Key Points 概览与黄金圈框架结合，形成经过对齐的、唯一事实源的确认包（`modules/GC-{slug}-v{N}.md`）。完成标准是"经业务方、技术方、管理层各自动用都能成立的黄金圈品牌定位资产"，不是"看起来内容丰富"。

所有黄金圈产物必须绑定 instance slug。slug 由主 Agent 提供，必须为 kebab-case，并与 `state.golden_circle.{slug}.slug` 一致；本 Skill 不自动生成 `default` slug。

## 定位

**分步提炼流程**：本 skill 是 Pratyaya Canvas Expert 的"黄金圈提炼与确认包生成"能力。完整的 GC 工作流由主 agent 编排（见 `agents/pratyaya.md`），本 skill 不编排主流程，只在被调用时执行以下两个独立 Stage：

- **Stage 1：Key Points 抽取** — 输入转写，输出 `modules/GC-{slug}-keypoints.md`（讨论地图，30 秒浏览）。
- **Stage 2：原子提炼** — 输入转写 + Key Points + 黄金圈框架，输出 `modules/GC-{slug}-v{N}.md`（确认包，唯一事实源）。

调用顺序由主 agent 决定，本 skill 不强制。本 skill 不调用 Canvas 渲染、不执行闸门判定。

## 唯一内容边界

开始任何 Stage 前必须读取：

1. 黄金圈框架 `frameworks/gc-golden-circle.md`：三层结构、引导问题、最低结论要求；
2. `references/gc-spec.md`：GC Key Points 与确认包的固定 section 定义。

只提取用户实际讨论的内容。框架之外的方法或术语不自动成为必填项、补问项或放行条件；只有用户明确使用时，才按原话记录。

## 引用层级（重要）

**不引用逐字稿段落**。与 MVL 蒸馏一致的立场——头脑风暴的逐字稿不具备段落级权威性：同一人在讨论前后可能表达矛盾立场、口语化试探与跑题占据大量文本、真正的事实来自"确认环节达成的共识"而非某段话。引用应基于：

- **Key Points 内的 section**（如"WHY 关键主张 2"）
- **确认包自身的 section**（如"GC 缺口表 G02"）

逐字稿从"证据"降级为"背景材料"，仅作存档，不作引用源。

## 输入与输出

| Stage | 输入 | 输出 |
|---|---|---|
| Stage 1：Key Points 抽取 | 逐字稿（文本或文件路径） | `modules/GC-{slug}-keypoints.md`（第 N 轮） |
| Stage 2：原子提炼 | 逐字稿 + Key Points + 黄金圈框架 | `modules/GC-{slug}-v{N}.md`（确认包，唯一事实源） |

Stage 1 与 Stage 2 可独立调用，不强制串联。但 Stage 2 的输入依赖 Stage 1 的 Key Points。

Stage 2 完成后交给主 agent 触发闸门（`gc-gate`），不直接进入 Canvas 渲染。

## Stage 1：Key Points 抽取

**目标**：在 30 秒内让用户了解"这次讨论了什么、三层覆盖度如何、缺什么"。

**触发**：主 agent GC 工作流对应步骤，输入为逐字稿（已由主 agent 存档为 `transcripts/gc-TXX-raw.md`）。

**输出**：`modules/GC-{slug}-keypoints.md`，结构如下。

### GC-{slug}-keypoints.md 模板

```markdown
# 黄金圈 Key Points（第 X 轮）

> 生成时间：{YYYY-MM-DD HH:MM}
> 画布类型：黄金圈 Golden Circle
> 轮次：第 X 轮
> 数据源：transcripts/gc-TXX-raw.md

## 1. 讨论主题

本次讨论覆盖了哪些主题（每个 1-2 句，最多 5 条）：

- **主题 1**：...
- **主题 2**：...

## 2. 关键主张

按 WHY / HOW / WHAT 三层组织（每层每项 1-2 句）：

- **WHY — 信念、目标与使命**
  - 主张 1：...
  - 主张 2：...
- **HOW — 核心差异化与方法**
  - 主张 1：...
  - 主张 2：...
- **WHAT — 产品与服务**
  - 主张 1：...
  - 主张 2：...

## 3. 明显矛盾或未对齐

讨论中出现的内部不一致或分歧点（最多 5 条）：

- 矛盾 1：...（如 WHY 声称是创新者，但 HOW 描述的是跟随策略）
- 矛盾 2：...

## 4. 覆盖度初判

对照黄金圈三层 9 子字段（`frameworks/gc-golden-circle.md`），粗略评估覆盖情况：

| 层 | 子字段 | 状态 | 简评 |
|---|---|---|---|
| WHY | belief（领导信念） | 已覆盖 / 部分覆盖 / 未涉及 | ... |
| WHY | purpose（存在目的） | ... | ... |
| WHY | mission（使命/愿景） | ... | ... |
| HOW | principles（做事原则） | ... | ... |
| HOW | differentiation（差异化） | ... | ... |
| HOW | methods（方法/流程） | ... | ... |
| WHAT | products（产品） | ... | ... |
| WHAT | services（服务） | ... | ... |
| WHAT | evidence（市场证据） | ... | ... |

## 5. 用户决策提示

> 基于以上概览，请选择：**提炼** / **补问** / **先看个样子**
```

**约束**：

- 长度控制：每节最多 5 条，供 30 秒快速浏览。
- 不做原子提炼、不写结论登记表、不评估缺口。
- 末尾必须输出用户决策提示。
- 跨轮次覆盖：第 N 轮 Key Points 覆盖第 N-1 轮摘要（同文件覆盖式更新，保留最后一轮）。
- 覆盖度初判必须包含全部 9 个子字段。

## Stage 2：原子提炼

**目标**：将 Key Points 转化为经过对齐的、唯一事实源的确认包 `GC-{slug}-v{N}.md`。

**触发**：主 agent GC 工作流对应步骤（用户回复"提炼"后调用）。

**输入**：
- 逐字稿（已存档）
- `modules/GC-{slug}-keypoints.md`（Stage 1 产物）
- `frameworks/gc-golden-circle.md`（黄金圈框架）

**输出**：`modules/GC-{slug}-v{N}.md`，全 Markdown，结构如下。

### GC-{slug}-v{N}.md 确认包模板

```markdown
# 黄金圈确认包 v{N}

> 画布类型：黄金圈 Golden Circle
> 版本：v{N}（基于第 X 轮 Key Points）
> 状态：{draft / gaps_open / review_ready / confirmed / rendered}
> 生成时间：{ISO 8601 datetime，由 skill 生成时写入}
> 确认人：{待填写}
> 确认人角色（可选）：{待填写}
> 确认时间：{待填写，ISO 8601 datetime}

---

## 必展项（紧凑前置）

### 1. 一句话结论

{≤50 字，概括整个黄金圈的核心理念}

### 2. 对齐摘要

- 共识：x 项
- 分歧：x 项
- 决策：x 项

### 3. 阻塞项

{如有 blocker，第一条就警示标注；无则写"无"}

### 4. 缺口速览

- blocker：x（open / closed / accepted_risk）
- major：x（open / closed / accepted_risk）
- minor：x（open / closed / accepted_risk）

### 5. 待确认版本

v{N}

---

## 详情

### 6. 三层内容

#### WHY：信念、目标与使命

| 子字段 | 内容 | 来源引用 |
|---|---|---|
| belief（领导信念） | ... | GC 关键主张 X |
| purpose（存在目的） | ... | ... |
| mission（使命/愿景） | ... | ... |

#### HOW：核心差异化与方法

| 子字段 | 内容 | 来源引用 |
|---|---|---|
| principles（做事原则） | ... | ... |
| differentiation（差异化） | ... | ... |
| methods（方法/流程） | ... | ... |

#### WHAT：产品与服务

| 子字段 | 内容 | 来源引用 |
|---|---|---|
| products（产品） | ... | ... |
| services（服务） | ... | ... |
| evidence（市场证据） | ... | ... |

### 6a. 跨层一致性

| 推导链 | 结论 | 一致性判断 | 来源引用 |
|---|---|---|---|
| WHY→HOW | HOW 的差异化如何源自 WHY 的信念 | 一致 / 部分一致 / 未建立 | GC 关键主张 X |
| HOW→WHAT | WHAT 的产品/服务如何体现 HOW 的方法和原则 | 一致 / 部分一致 / 未建立 | ... |

> 此节为 Canvas 渲染中跨层一致性 section 的唯一事实源。一致性判断由本 skill 在 Stage 2 中基于转写证据给出，不由 canvas-render 推断。

### 7. 结论登记表

| ID | 结论 | 所属层 | 类型 | 共识状态 |
|---|---|---|---|---|
| GC-C01 | ... | WHY | fact / decision / hypothesis / recommendation | 共识 / 待确认 / 争议 |
| GC-C02 | ... | HOW | ... | ... |

> 共识状态由"对齐检查"环节写入，不由本 skill 写入。
> 本表只记录"经过讨论产生的结论"；推断不写入此表。

### 8. 缺口表

| ID | 等级 | 所属层 | 状态 | 描述 | 缺失影响 | 最少补问 |
|---|---|---|---|---|---|---|
| GC-G01 | blocker | WHY | open | ... | ... | ... |
| GC-G02 | major | HOW | open | ... | ... | ... |
| GC-G03 | minor | WHAT | open | ... | ... | ... |

> 等级定义：blocker = 使该层核心产出无法成立；major = 显著改变该层的判断或方向；minor = 不改变核心结论，可后续补齐或明确接受风险。
> 状态定义：
> - `open`：未关闭；Gate 评估时仍按等级计入 PASS/FAIL。
> - `closed`：已解决；可作为关闭依据进入下一轮或当前轮评估。
> - `accepted_risk`：用户/确认人已显式接受风险；属治理元数据，由用户在确认环节写入，不由本 skill 写入。

### 9. 推断表

| ID | 推断 | 所属层 | 影响 | 状态 |
|---|---|---|---|---|
| GC-I01 | ... | WHY | ... | 待接受 / 待拒绝 |

> 推断不写入结论登记表与固定 Canvas section。
> "待接受"或"待拒绝"由"对齐检查"环节写入，不由本 skill 写入。

### 10. 关键证据引用

引用 Key Points / 确认包内 section（不引用逐字稿段落）：

- GC 关键主张 X 中关于 ...
- GC 覆盖度初判：{层} / {子字段} {状态}
- GC 缺口表 G{XX}（如已在本表登记）

### 11. 待用户决策

> 请在以下三项中任选其一回复：
> - **确认 v{N}**：Gate 已通过，希望对当前版本作最终确认并授权渲染。
> - **override**：Gate 报告含 `business_risk` FAIL，我已阅读影响并接受该风险；请补充 override 理由、确认人、确认时间，可选角色与补救措施。
> - **补问 / 修订**：当前版本存在需要补问的问题或需修改的业务内容，请回到工作流对应步骤。

---

## 12. Gate 与用户决策

> **本节属于治理元数据**，由 Gate 流程与主 Agent 在用户决策后写入。
> **业务内容变化**（第 1–11 节任何字段）必须升版 + 重跑 Gate + 重新确认；**仅修改本节不触发业务版本升版**。
> 旧版本本节审计信息随旧版确认包保留，用于历史追溯。

### 12.1 Gate 建议

- `gate_recommendation`：`pending` / `pass` / `fail`
- Gate 评估时间：{ISO 8601 datetime}
- Gate 报告摘要：{见 `../gc-gate/references/GC-gate.md`；本字段可写评估项 PASS/FAIL 数与最关键 1–2 项摘要}

### 12.2 用户决策

- `confirmation_mode`：`待决策` / `gate_pass` / `override`
- `render_authorized`：`false` / `true`
- 确认人：{用户填写}
- 确认人角色（可选）：{用户填写}
- 确认时间：{ISO 8601 datetime}

### 12.3 Override 审计（仅 `confirmation_mode=override` 时填写）

| Gate 项 ID | 来源 ID | 分类 | 风险等级 | 影响 |
|---|---|---|---|---|
| GC-GATE-0X | GC-{section} | business_risk | low / medium / high | ... |

> - **Override 理由**：{用户填写的影响确认 + 业务上下文}
> - **补救措施**：{用户填写的后续动作与验收条件}
> - **核心约束**：仅 `category=business_risk` 项可进入 override；`information_integrity` 失败不接受 override，必须返回补问或修订。
> - **审计完整性**：`override_audit.items` 非空且每项 `category=business_risk`，否则 Canvas 渲染前置检查阻断。
```

**约束**：

- 引用格式：仅引用 Key Points 与确认包自身的 section，**不引用逐字稿段落**。
- 推断必须独立登记，不写入结论登记表。
- 缺口必须说明"缺失影响"，不能只说"信息不足"。
- 不调用 Canvas 渲染、不执行闸门判定。
- 状态写入由主 agent 在"确认 vN"后执行，不在本 skill 内部。
- 版本号管理：升版时 vN → vN+1，旧版本归档为 `modules/GC-{slug}-v{N}.md.previous`，不清空。
- **缺口表必须含 `状态` 列**（`open` / `closed` / `accepted_risk`），其中 `accepted_risk` 由确认人在确认环节写入，不由本 skill 写入。
- **元数据必须包含**：`画布类型` / `版本` / `状态` / `生成时间`（ISO 8601 datetime，skill 生成时自动写入） / `确认人` / `确认人角色（可选）` / `确认时间`（用户填写）。
- **第 6a 节"跨层一致性"**是 Canvas 渲染跨层一致性 section 的唯一事实源，必须在 Stage 2 中基于转写证据填写，不得留空或写泛化描述。
- **第 12 节"Gate 与用户决策"由 Gate 流程与主 Agent 在用户决策后写入**；本 skill 不写第 12 节。本 skill 只负责在模板中预留该节结构。

## 升版边界

确认包版本受两类写入影响：

| 写入范围 | 是否触发升版 | 是否重跑 Gate | 是否重置授权 |
|---|---|---|---|
| 第 1–11 节业务内容（含结论、缺口、推断、引用、决策、跨层一致性）变化 | **是**（vN → vN+1） | **是** | **是**（清空 `gate_recommendation` / `render_authorized` / `confirmation_mode` / `override_audit`） |
| 仅第 12 节"Gate 与用户决策"治理元数据写入（Gate 报告、用户决策、Override 审计） | **否**（保留 vN） | 否（已是当前评估结果） | 否（这是当前版本的授权写入） |

**规则**：

- **业务内容变化**：必须 `version + 1` + `gate_recommendation=pending` + `render_authorized=false` + `confirmation_mode=null` + 清空当前版本 `override_audit`；旧版本确认包归档为 `GC-{slug}-v{N}.md.previous`，旧版第 12 节审计随旧版保留。
- **治理元数据写入**（仅第 12 节）：不触发升版；Gate 报告摘要与用户授权属于当前版本的元数据补充。
- **历史版本审计**不得清空：旧版 `GC-{slug}-v{N}.md.previous` 的第 12 节（包括历史 override 审计）必须完整保留，用于追溯。

## 元数据生成时间字段

- `生成时间`（`GC-{slug}-v{N}.md` 顶部）由本 skill 在 Stage 2 生成确认包时按系统真实时间写入（ISO 8601 datetime）。
- `确认时间`由主 Agent 在用户决策后写入；不得使用 skill 生成时间。
- 禁止在文件名、文档标题、报告标识中编造时间戳。

## 质量红线

1. 不编造、不拔高、不抹平冲突。
2. 关键数字、决策和结论必须有 Key Points 内的依据。
3. WHY/HOW/WHAT 任意层完全未讨论时，整个确认包标为 `gaps_open`，不出 `review_ready`。
4. 推断必须独立登记，不写入结论或固定 Canvas section。
5. 模板 section 缺失时标缺口，不能用通用话术补满。
6. 不引用逐字稿段落；引用应基于 Key Points / 确认包内的 section。
7. 跨层推导链（WHY→HOW、HOW→WHAT）必须在讨论中有线索，不能完全由 LLM 构造。第 6a 节的一致性判断必须基于转写证据。
8. 未完成人工确认前，不视为提炼完成；状态由主 agent 在"确认 vN"后写入。
