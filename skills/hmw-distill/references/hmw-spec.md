# HMW 模块规范

本文件是 `hmw-distill` 和 `hmw-gate` 共用的事实源定义。固化 HMW Key Points 与确认包的固定 section、ID 约定与 Canvas 映射。

## HMW Key Points 固定结构

参见 `hmw-distill/SKILL.md` 的 Stage 1 模板。必含 section：

1. 讨论主题
2. 关键主张（按痛点 / 用户时刻 / 现有解法组织）
3. 明显矛盾或未对齐
4. 覆盖度初判（陈述 4 字段 + 质量 4 维度 + 想法）
5. 用户决策提示

## HMW 确认包固定 section

确认包 `HMW-{slug}-v{N}.md` 的必填 section（写入业务内容，名称固定）：

| 节号 | section 名称 | 内容 |
|---|---|---|
| 6 | HMW 陈述 | situation / question / for / so_that 四字段 |
| 6a | 质量鉴别 | preset_solution / vague / user_moment / tension 四维度判定 |
| 6b | 想法种子 | content / type / link_to_statement / status（1–8 条） |
| 6c | 想法 ↔ HMW 对应 | 想法 ID / 回应问句 / 对应质量维度 / 一致性判断 / 来源引用 |
| 7 | 结论登记表 | ID（HMW-Cxx）/ 结论 / 类型 / 共识状态 |
| 8 | 缺口表 | ID（HMW-Gxx）/ 等级 / 状态 / 描述 / 缺失影响 / 最少补问 |
| 9 | 推断表 | ID（HMW-Inf-N 或 HMW-Ixx）/ 推断 / 影响 / 状态 |

section 没有讨论到时，不得补写。将它标为缺口并说明对本次 HMW 产出和最终 Canvas 的影响。

## ID 约定

| 前缀 | 含义 | 示例 |
|---|---|---|
| `HMW-C` | 结论（Conclusion） | `HMW-C01`：HMW 问句无预设解法 |
| `HMW-G` | 缺口（Gap） | `HMW-G01`：so_that 无可衡量结果 |
| `HMW-Inf` / `HMW-I` | 推断（Inference） | `HMW-Inf01`：基于现有张力推断想法方向 |
| `HMW-Idea-N` | 想法种子（Idea） | `HMW-Idea-1`：想法种子第 1 条 |

> **注意**：推断 ID 与想法种子 ID 必须区分——推断用 `HMW-Inf-N`，想法种子用 `HMW-Idea-N`，避免混淆。

## Canvas 映射

HMW 确认包到 `render-contract-hmw.md` 的 HTML 锚点映射：

| 确认包 section | HTML 锚点 |
|---|---|
| 6：situation（问题情境） | `hmw-situation` |
| 6：question（我们可以如何） | `hmw-question` |
| 6：for（为/给） | `hmw-for` |
| 6：so_that（以便） | `hmw-sothat` |
| 6a：preset_solution（预设解法） | `hmw-quality-preset` |
| 6a：vague（含糊） | `hmw-quality-vague` |
| 6a：user_moment（用户时刻） | `hmw-quality-moment` |
| 6a：tension（张力） | `hmw-quality-tension` |
| 6b：想法种子第 1–8 条 | `hmw-idea-1` … `hmw-idea-8` |
| 6c：想法 ↔ HMW 对应 | `hmw-coherence-map` |

## 质量鉴别字段要求

第 6a 节的每行必须包含：

- **维度**：preset_solution / vague / user_moment / tension
- **判定**：通过 / 不通过
- **依据**：转写中的证据线索（引 Key Points section，不引逐字稿段落）

判定由 `hmw-distill` 在 Stage 2 中基于转写证据给出，不由 `canvas-render` 推断。若讨论中完全未涉及某维度，标"未判定"并在缺口表登记。

## 想法种子字段要求

第 6b 节的每行必须包含：

- **content**：想法内容
- **type**：想法类型（功能/流程/机制/体验…）
- **link_to_statement**：回应的 HMW 问句（situation / question / for / so_that）
- **status**：候选 / 已采纳 / 已弃

第 6c 节（想法 ↔ HMW 对应）是 `render-contract-hmw.md` 中 `hmw-coherence-map` anchor 的事实源。每行包含：想法 ID / 回应哪条 HMW 问句 / 对应质量维度 / 一致性判断（一致 / 部分一致 / 未建立）/ 来源引用。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使画布核心产出（HMW 陈述或质量判定）无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变问题重构的方向 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

## 不得自动引入

- 不得强制固定想法数量（1–8 条内，讨论到几条写几条，空想法格渲染为占位）。
- 不得强制特定想法类型或固定权重评分。
- 不得因为模板有 8 个想法格而补写没有讨论过的想法。
- 不得把"提高效率""降低成本"扩写为日程没有讨论的内容。
- 质量鉴别判定必须有转写证据线索，不得由 LLM 主观构造。
