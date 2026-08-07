# Persona 模块规范

本文件是 `persona-distill` 和 `persona-gate` 共用的事实源定义。固化 Persona Key Points 与确认包的固定 section、ID 约定与 Canvas 映射。

## Persona Key Points 固定结构

参见 `persona-distill/SKILL.md` 的 Stage 1 模板。必含 section：

1. 讨论主题（最多 5 条）
2. 关键主张（按基本信息 / 六宫格 / 质量信号组织）
3. 明显矛盾或未对齐
4. 覆盖度初判（基本信息 9 字段 + 六宫格 6 区 + 质量 4 维度）
5. 用户决策提示（提炼 / 补问 / 先看个样子）

## Persona 确认包固定 section

确认包 `PERSONA-v{N}.md` 的必填 section（写入业务内容，名称固定）：

| 节号 | section 名称 | 内容 |
|---|---|---|
| 1 | 一句话结论 | 这个画像是谁，代表什么用户群体 |
| 2 | 对齐摘要 | 与业务方/产品方的对齐情况 |
| 3 | 阻塞项 | 阻碍画像成立的关键问题 |
| 4 | 缺口速览 | 快速列出缺失的关键信息 |
| 5 | 待确认版本 | 当前版本号和状态 |
| 6 | 9 基本信息 + 6 宫格 | 画像的核心内容（基本信息 9 字段 + 六宫格 6 区） |
| 6a | 质量鉴别 | evidence_based / concrete / pain_in_voice / representative 四维度判定 |
| 7 | 结论登记表 | ID（PERSONA-Cxx）/ 结论 / 类型 / 共识状态 |
| 8 | 缺口表 | ID（PERSONA-Gxx）/ 等级 / 状态 / 描述 / 缺失影响 / 最少补问 |
| 9 | 推断表 | ID（PERSONA-Infxx）/ 推断 / 影响 / 状态 |
| 10 | 关键证据引用 | 支撑结论的关键证据（引用 Key Points section，不引逐字稿） |
| 11 | 待用户决策 | 需要用户确认的事项 |
| 12 | Gate 与用户决策 | 治理元数据（Gate 建议、用户最终决策、override 审计） |

section 没有讨论到时，不得补写。将它标为缺口并说明对本次画像产出和最终 Canvas 的影响。

## ID 约定

| 前缀 | 含义 | 示例 |
|---|---|---|
| `PERSONA-C` | 结论（Conclusion） | `PERSONA-C01`：画像核心主张 |
| `PERSONA-G` | 缺口（Gap） | `PERSONA-G01`：某宫格未讨论 |
| `PERSONA-Inf` | 推断（Inference） | `PERSONA-Inf01`：基于现有信息推断的行为模式 |

## Canvas 映射

Persona 确认包到 `render-contract-persona.md` 的 HTML 锚点映射：

| 确认包 section | HTML 锚点 |
|---|---|
| 6：9 基本信息 | `persona-basic` |
| 6：name | `persona-name` |
| 6：gender | `persona-gender` |
| 6：age | `persona-age` |
| 6：location | `persona-location` |
| 6：education | `persona-education` |
| 6：job_title | `persona-job-title` |
| 6：industry | `persona-industry` |
| 6：family_status | `persona-family-status` |
| 6：income | `persona-income` |
| 6：description | `persona-description` |
| 6：goals_needs | `persona-goals-needs` |
| 6：behaviors | `persona-behaviors` |
| 6：pain_points | `persona-pain-points` |
| 6：motivation | `persona-motivation` |
| 6：decision_factors | `persona-decision-factors` |
| 6a：evidence_based | `persona-quality-evidence` |
| 6a：concrete | `persona-quality-concrete` |
| 6a：pain_in_voice | `persona-quality-voice` |
| 6a：representative | `persona-quality-representative` |

## 质量鉴别字段要求

第 6a 节的每行必须包含：

- **维度**：evidence_based / concrete / pain_in_voice / representative
- **判定**：通过 / 不通过
- **依据**：转写中的证据线索（引 Key Points section，不引逐字稿段落）

判定由 `persona-distill` 在 Stage 2 中基于转写证据给出，不由 `canvas-render` 推断。若讨论中完全未涉及某维度，标"未判定"并在缺口表登记。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使画像核心产出（基本信息或六宫格）无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变画像的代表性或可信度 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

## 不得自动引入

- 不得因为模板有 9 基本信息而补写没有讨论过的字段。
- 不得因为模板有 6 宫格而补写没有讨论过的宫格。
- 不得把"年轻""高净值""追求品质"等泛泛之词当作具体描述。
- 质量鉴别判定必须有转写证据线索，不得由 LLM 主观构造。
- 不得编造用户原话；痛点必须来自转写中的真实表述。
