# GC 模块规范

本文件是 `gc-distill` 和 `gc-gate` 共用的事实源定义。固化 GC Key Points 与确认包的固定 section、ID 约定与 Canvas 映射。

## GC Key Points 固定结构

参见 `gc-distill/SKILL.md` 的 Stage 1 模板。必含 section：

1. 讨论主题
2. 关键主张（按 WHY / HOW / WHAT 三层）
3. 明显矛盾或未对齐
4. 覆盖度初判（9 子字段二维表）
5. 用户决策提示

## GC 确认包固定 section

确认包 `GC-{slug}-v{N}.md` 的必填 section（写入业务内容，名称固定）：

| 节号 | section 名称 | 内容 |
|---|---|---|
| 6 | 三层内容 — WHY | belief / purpose / mission 三子字段 |
| 6 | 三层内容 — HOW | principles / differentiation / methods 三子字段 |
| 6 | 三层内容 — WHAT | products / services / evidence 三子字段 |
| 6a | 跨层一致性 | WHY→HOW 推导链 / HOW→WHAT 推导链 |
| 7 | 结论登记表 | ID（GC-Cxx）/ 结论 / 所属层 / 类型 / 共识状态 |
| 8 | 缺口表 | ID（GC-Gxx）/ 等级 / 所属层 / 状态 / 描述 / 缺失影响 / 最少补问 |
| 9 | 推断表 | ID（GC-Ixx）/ 推断 / 所属层 / 影响 / 状态 |

section 没有讨论到时，不得补写。将它标为缺口并说明对本次 GC 产出和最终 Canvas 的影响。

## ID 约定

| 前缀 | 含义 | 示例 |
|---|---|---|
| `GC-C` | 结论（Conclusion） | `GC-C01`：WHY 层核心理念已共识 |
| `GC-G` | 缺口（Gap） | `GC-G01`：HOW 层差异化未量化 |
| `GC-I` | 推断（Inference） | `GC-I01`：基于现有 HOW 推断 WHAT 产品方向 |

## Canvas 映射

GC 确认包到 `render-contract-gc.md` 的 HTML 锚点映射：

| 确认包 section | HTML 锚点 |
|---|---|
| 6：WHY / belief | `why-belief` |
| 6：WHY / purpose | `why-purpose` |
| 6：WHY / mission | `why-mission` |
| 6：HOW / principles | `how-principles` |
| 6：HOW / differentiation | `how-differentiation` |
| 6：HOW / methods | `how-methods` |
| 6：WHAT / products | `what-products` |
| 6：WHAT / services | `what-services` |
| 6：WHAT / evidence | `what-evidence` |
| 6a：WHY→HOW 推导链 | `alignment-why-how` |
| 6a：HOW→WHAT 推导链 | `alignment-how-what` |

## 跨层一致性字段要求

第 6a 节的每行必须包含：

- **推导链**：WHY→HOW 或 HOW→WHAT
- **结论**：该推导链的核心陈述（如"创新信念驱动了技术差异化"）
- **一致性判断**：`一致` / `部分一致` / `未建立`
- **来源引用**：GC 关键主张 X 或 GC 覆盖度初判中的对应行

一致性判断由 `gc-distill` 在 Stage 2 中基于转写证据给出，不由 `canvas-render` 推断。若讨论中完全未涉及某条推导链，标注"未建立"。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使该层核心产出或对应 Canvas section 无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变该层的判断或方向 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

## 不得自动引入

- 不得强制固定年限的愿景、固定权重评分或固定产品层级。
- 不得强制特定头脑风暴、角色分层或旅程方法。
- 不得因为模板有空间而补充新信念、新差异化、新产品或新市场证据。
- 不得把"可扩展""规模化"扩写为日程没有讨论的内容。
