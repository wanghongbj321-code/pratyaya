# 5W 模块规范

本文件是 `5w-distill` 和 `5w-gate` 共用的事实源定义。固化 5W Key Points 与确认包的固定 section、ID 约定与 Canvas 锚点映射。

## 5W Key Points 固定结构

参见 `5w-distill/SKILL.md` 的 Stage 1 模板。必含 section：

1. 讨论主题
2. 问题陈述（候选）
3. 因果链线索（按层组织：Why 1–5 + 证据线索）
4. 对策与行动线索
5. 覆盖度初判（问题陈述 / Why 1-5 各层 / 根本原因 / 对策四要素）
6. 用户决策提示

## 5W 确认包固定 section

确认包 `5W-{slug}-v{N}.md` 的必填 section（写入业务内容，名称固定）：

| 节号 | section 名称 | 内容 |
|---|---|---|
| 6 | 问题陈述 | statement（事实陈述）/ occurred_at / impact_frequency / participants |
| 7 | 因果链（五层，三层面） | 每层：层 / 层面 / 追问对象 / 答案（因为…）/ 证据 / 合格检查点 |
| 8 | 根本原因 | root_cause / so_therefore（"因此"检验链）/ stop_check（停止准则） |
| 9 | 对策四要素 | countermeasure / owner / due_date / verify |
| 10 | 其他原因分支 | 本次未追踪的分支；复发时首选线索 |
| 11 | 判别记录（rubric） | 坏答案（被打回）/ 问题类型 / 好答案（采纳） |
| 12 | 结论登记表 | ID（5W-Cxx）/ 结论 / 所属层 / 类型 / 共识状态 |
| 13 | 缺口表 | ID（5W-Gxx）/ 等级 / 所属区 / 状态 / 描述 / 缺失影响 / 最少补问 |
| 14 | 推断表 | ID（5W-Ixx）/ 推断 / 所属区 / 影响 / 状态 |

section 没有讨论到时，不得补写。将它标为缺口并说明对本次 5W 产出和最终 Canvas 的影响。

## 判别记录（rubric）字段要求

第 11 节的每行必须包含：

- **坏答案（被打回）**：工作坊中实际被打回的表述（如"某人不认真"）
- **问题类型**：个人归因 / 不可控笼统 / 甩锅外部 / 模糊无法落地
- **好答案（采纳）**：改写后的可验证表述

> 只记录工作坊中**实际发生**的判别对照（数据源为 Key Points 中的纠偏记录）；无实际打回记录时写"无"，不得编造示例。此节为 Canvas 渲染中 `5w-rubric-table` anchor 的唯一事实源。

## ID 约定

| 前缀 | 含义 | 示例 |
|---|---|---|
| `5W-C` | 结论（Conclusion） | `5W-C01`：问题陈述已改写为事实表述 |
| `5W-G` | 缺口（Gap） | `5W-G01`：Why 3 无证据 |
| `5W-I` | 推断（Inference） | `5W-I01`：基于证据缺失推断可能漏检环节 |
| `5W-GATE-` | 门禁评估项（仅 Gate 报告与 override 审计使用） | `5W-GATE-01` |

> 结论 / 缺口 / 推断 ID 与 Gate 评估项 ID（`5W-GATE-N`）必须区分：`5W-GATE-` 前缀仅用于 Gate 评估与 override 审计，不用于业务内容表。

## Canvas 锚点映射

5W 确认包到 `render-contract-5w.md` 的 HTML 锚点映射：

| 确认包 section | HTML 锚点 |
|---|---|
| 必展项 → 一句话结论 | `canvas-headline` |
| 6：statement（事实陈述） | `5w-problem-statement` |
| 6：occurred_at / impact_frequency / participants | `5w-problem-meta` |
| 7：因果链五层（Why 1–5） | `5w-why-1` … `5w-why-5` |
| 8：root_cause（根本原因） | `5w-root-cause` |
| 8：so_therefore（"因此"检验链）+ stop_check | `5w-root-check` |
| 9：countermeasure（对策） | `5w-countermeasure` |
| 9：owner（负责人） | `5w-owner` |
| 9：due_date（截止日期） | `5w-due` |
| 9：verify（如何验证有效） | `5w-verify` |
| 10：其他原因分支 | `5w-branches-list` |
| 11：判别记录（rubric） | `5w-rubric-table` |

**关键规则**：

- 已讨论字段正常展示；未讨论字段显示"未讨论"并标为缺口；
- `5w-why-*` 数据源为确认包第 7 节，不由 canvas-render 推断；
- 五层锚点 `5w-why-1` … `5w-why-5` **必须全部存在**（对齐 5 层固定结构，层数弹性暂不支持）。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使 5W 核心产出（问题陈述 / 因果链 / 根因）无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变根因分析的方向或对策 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

## 不得自动引入

- 不得强制固定答案数量；讨论到几条写几条，证据缺失的层标为缺口。
- 不得补写没有被讨论过的对策、负责人、截止日期或验证信号。
- 不得把"提高效率""加强管理"扩写为讨论中没有的内容。
- 问题陈述必须为事实；结论型表达（如"团队混乱"）必须改写为可验证事实并标注改写。
- 判别记录（rubric）不得编造示例；无实际打回记录时写"无"。
- 推断必须独立登记（第 14 节），不得混入结论登记表（第 12 节）或 Canvas section。
