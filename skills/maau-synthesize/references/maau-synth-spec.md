# MAAU 六板块综合提炼契约（maau-synth-spec）

> 供 `maau-synthesize` Skill 使用。把「一次性逐字稿」综合提炼为 MAAU 全局画布的六板块源包 `modules/MAAU-{slug}-v{N}.md`。
> 生成路径：`generation_path=transcript-direct`（与 M1-M6 Phase 2 全局汇总互斥隔离）。

## 六板块字段契约

源包只包含六大板块，**不新增第七板块**。每板块字段与来源模块映射如下：

| 板块 | 字段 | 来源模块映射 |
|---|---|---|
| **Intent** | 目标（goal）/ 价值（value）/ 成功指标（success_metrics，含指标、基线、目标、衡量方式） | M1（M3 回填） |
| **User** | 用户（users）/ 需求（needs）/ 痛点（pain_points）/ 最重要的结果（most_important_outcomes） | M2 |
| **Agent Team** | 角色 / 职责 / 是否 Agent / 决策边界 / 协作模式 | M4 |
| **Workflow** | 触发（trigger）/ 步骤（steps）/ 完成条件（completion_condition）+ 三类节点 + 关键规则（rules） | M3 草案 → M4 冻结 |
| **Context** | 知识库（knowledge）/ 数据源（data_sources）/ 工具与技能（tools_skills） | M4 |
| **Validation** | 能否执行（can_execute）/ 能否创造价值（can_create_value）/ 能否持续进化（evolution） | M5 + M6 |

### Workflow 三类节点（硬性）

Workflow 必须以 **AI 应用** 为原点（不是普通业务流程复述），必须包含三类节点且每类至少一项：

1. **Agent 执行节点**（agent_execution_nodes）：自动化节点（Agent 执行）
2. **人工操作/确认节点**（human_operation_confirmation_nodes）：人工操作/确认节点
3. **人审 + Agent 执行节点**（human_review_agent_execution_nodes）：人审后由 Agent 执行，或人审与 Agent 联合执行

三类节点缺任一类不能形成 Workflow，标 `information_integrity` 缺口，**不得自动补写**。

### Context 与 Validation 约束

- **Context**：只列逐字稿讨论确认项，并说明可获得性；不得按常见做法自动补全。
- **Validation**：三类（能否执行 / 能否创造价值 / 能否持续进化）逐项评估，未讨论标缺口，不自动生成资产名称。

## 源包模板

`modules/MAAU-{slug}-v{N}.md` 结构如下：

```markdown
# MAAU 六板块源包 v{N}

> 画布类型：MVL（MAAU 全局画布）
> 生成路径：transcript-direct
> slug：{slug}
> 版本：v{N}
> project_slug：{project_slug}
> group_id：{group_id}
> 状态：{draft / gaps_open / review_ready / confirmed / rendered}
> 生成时间：{ISO 8601 datetime，由 skill 生成时写入}
> 确认人：{待填写}
> 确认时间：{待填写，ISO 8601 datetime}
> 数据源：transcripts/maau-{slug}-raw.md（逐字稿，仅作背景材料，不作引用源）

---

## 必展项（紧凑前置）

### 1. 一句话结论
{≤50 字，概括整个 MAAU 源包的核心理念}

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

### 6. 六大板块

#### 6.1 Intent（意图）
| 字段 | 内容 | 来源线索 |
|---|---|---|
| goal（目标） | ... | MAAU 源包 关键主张 X |
| value（价值） | ... | ... |
| success_metrics（成功指标） | ... | ... |

#### 6.2 User（用户）
| 字段 | 内容 | 来源线索 |
|---|---|---|
| users（用户） | ... | ... |
| needs（需求） | ... | ... |
| pain_points（痛点） | ... | ... |
| most_important_outcomes（最重要的结果） | ... | ... |

#### 6.3 Agent Team（人 + Agent）
| 字段 | 内容 | 来源线索 |
|---|---|---|
| 角色 | ... | ... |
| 职责 | ... | ... |
| 是否 Agent | 人 / Agent / 人与 Agent 协作 | ... |
| 决策边界 | ... | ... |
| 协作模式 | ... | ... |

#### 6.4 Workflow（工作流）
| 字段 | 内容 | 来源线索 |
|---|---|---|
| 触发（trigger） | ... | ... |
| 步骤（steps） | ... | ... |
| 完成条件（completion_condition） | ... | ... |
| Agent 执行节点 | ... | ... |
| 人工操作/确认节点 | ... | ... |
| 人审 + Agent 执行节点 | ... | ... |
| 关键规则（rules） | ... | ... |

> 三类节点每类至少一项；缺类进入缺口表（`information_integrity`），不自动补写。

#### 6.5 Context（上下文）
| 字段 | 内容 | 可获得性 | 来源线索 |
|---|---|---|---|
| 知识库（knowledge） | ... | ... | ... |
| 数据源（data_sources） | ... | ... | ... |
| 工具与技能（tools_skills） | ... | ... | ... |

#### 6.6 Validation（闭环验证）
| 字段 | 内容 | 来源线索 |
|---|---|---|
| 能否执行（can_execute） | ... | ... |
| 能否创造价值（can_create_value） | ... | ... |
| 能否持续进化（evolution） | ... | ... |

### 7. 结论登记表
| ID | 结论 | 所属板块 | 类型 | 共识状态 |
|---|---|---|---|---|
| MAAU-C01 | ... | Intent | fact / decision / hypothesis / recommendation | 共识 / 待确认 / 争议 |

> 共识状态由"对齐检查"环节写入，不由本 skill 写入。

### 8. 缺口表
| ID | 等级 | 所属板块 | 状态 | 描述 | 缺失影响 | 最少补问 |
|---|---|---|---|---|---|---|
| MAAU-G01 | blocker | Workflow | open | ... | ... | ... |

> 等级定义：blocker = 使核心产出无法成立；major = 显著改变判断或方向；minor = 不改变核心结论。
> 状态：`open` / `closed` / `accepted_risk`（`accepted_risk` 由确认人写入）。

### 9. 推断表
| ID | 推断 | 所属板块 | 影响 | 状态 |
|---|---|---|---|---|
| MAAU-I01 | ... | Intent | ... | 待接受 / 待拒绝 |

> 推断不写入结论登记表与固定 Canvas section。

### 10. 关键证据引用
引用 Key Points / 源包自身 section（不引用逐字稿段落）。

### 11. 待用户决策
> 请在以下三项中任选其一回复：
> - **确认 v{N}**
> - **override**
> - **补问 / 修订**

---

## 12. Gate 与用户决策
> 本节属于治理元数据，由 Gate 流程与主 Agent 在用户决策后写入。
> 业务内容变化（第 1–11 节）必须升版 + 重跑 Gate + 重新确认；仅修改本节不触发业务版本升版。

### 12.1 Gate 建议
- `gate_recommendation`：`pending` / `pass` / `fail`
- Gate 评估时间：{ISO 8601 datetime}
- Gate 报告摘要：{见 `../module-conclusion-gate/references/MAAU-gate.md`}

### 12.2 用户决策
- `confirmation_mode`：`待决策` / `gate_pass` / `override`
- `render_authorized`：`false` / `true`
- 确认人：{用户填写}
- 确认时间：{ISO 8601 datetime}

### 12.3 Override 审计（仅 `confirmation_mode=override` 时填写）
| Gate 项 ID | 来源 ID | 分类 | 风险等级 | 影响 |
|---|---|---|---|---|
| MAAU-GATE-0X | MAAU-{section} | business_risk | low / medium / high | ... |

> 仅 `category=business_risk` 项可进入 override；`information_integrity` 失败不接受 override，必须返回补问或修订。

## 引用层级（重要）

**不引用逐字稿段落**。与 MVL / 黄金圈蒸馏一致的立场：一次性逐字稿不具备段落级权威性（口语化试探、跑题、前后矛盾），真正的事实来自"确认环节达成的共识"。来源线索应基于：

- 源包自身的 section（如"6.1 Intent goal"）
- 逐字稿综合提炼后的 Key Points（若存在）

逐字稿从"证据"降级为"背景材料"，仅作存档。

## 升版边界

| 写入范围 | 是否触发升版 | 是否重跑 Gate | 是否重置授权 |
|---|---|---|---|
| 第 1–11 节业务内容变化 | **是**（vN → vN+1） | **是** | **是**（清空 4 字段） |
| 仅第 12 节"Gate 与用户决策"治理元数据写入 | **否**（保留 vN） | 否 | 否 |

## 文件命名

| 文件 | 模板 |
|---|---|
| 源包 | `modules/MAAU-{slug}-v{N}.md` |
| 旧版归档 | `modules/maau/archive/MAAU-{slug}-v{N}.md.previous` |
| 补问清单 | `modules/MAAU-{slug}-gaps.md` |
| Gate 报告 | `modules/MAAU-{slug}-gate-report-v{N}.md` |
| 实例输出 HTML | `output/maau-global-canvas-{slug}.html` |

slug 必须为 kebab-case ASCII，且不得为 `default`。
