# User Journey 模块规范

本文件是 `journey-distill` 和 `journey-gate` 共用的事实源定义。固化 Journey Key Points 与确认包的固定 section、ID 约定与 Canvas 映射。

> **v2.3.2 PATCH**：第 6 节 5 行字段由 `wait_rework` / `risk` 切换为 `pain_point` / `opportunity`，表头文本由「等待与返工 / 风险节点」切换为「痛点 / 机会」；6a 维度键 `friction_visible` 切换为 `pain_opportunity_visible`，中文标签「断点可见」切换为「痛点与机会可见」；6b 节标题由「关键断点与机会」切换为「痛点与机会」，数据列为「类型」（固定值 `pain_point` / `opportunity`）和「来源」（`user_stated` / `inferred_from_pain_point` / `inferred_from_quality`）；JOURNEY-Fxx 含义由「断点 / 机会」切换为「痛点 / 机会条目」；Canvas 映射的 HTML 锚点一律切到 `pain-point` / `opportunity` / `journey-pain-opportunity-summary` / `journey-quality-pain-opportunity-visible`。

## Journey Key Points 固定结构

参见 `journey-distill/SKILL.md` 的 Stage 1 模板。必含 section：

1. 讨论主题
2. 关键主张（按阶段 / 痛点与机会 / 质量信号组织）
3. 明显矛盾或未对齐
4. 阶段覆盖度初判（动态阶段 × 5 行合并结构）
5. 质量覆盖度初判（4 个质量鉴别维度）
6. 用户决策提示

## Journey 确认包固定 section

确认包 `JOURNEY-v{N}.md` 的必填 section（写入业务内容，名称固定）：

| 节号 | section 名称 | 内容 |
|---|---|---|
| 6 | 阶段地图 | 动态阶段 × 行动 / 触点与系统 / 情绪 / 痛点 / 机会 |
| 6a | 质量鉴别 | user_perspective / business_outcome / pain_opportunity_visible / no_solution_bias 四维度判定 |
| 6b | 痛点与机会 | 阶段内能标出的痛点与机会条目，按 ID（JOURNEY-Fxx）/ 阶段 / 类型（pain_point/opportunity）/ 来源（user_stated / inferred_from_pain_point / inferred_from_quality）四列组织 |
| 7 | 结论登记表 | ID（JOURNEY-Cxx）/ 结论 / 类型 / 共识状态 |
| 8 | 缺口表 | ID（JOURNEY-Gxx）/ 等级 / 状态 / 描述 / 缺失影响 / 最少补问 |
| 9 | 推断表 | ID（JOURNEY-Infxx）/ 推断 / 影响 / 状态 |
| 12 | Gate 与用户决策 | Gate 建议、用户决策、override 审计 |

section 没有讨论到时，不得补写。将它标为缺口并说明对本次 Journey 产出和最终 Canvas 的影响。

## ID 约定

| 前缀 | 含义 | 示例 |
|---|---|---|
| `JOURNEY-C` | 结论（Conclusion） | `JOURNEY-C01`：等待审批是最大痛点 |
| `JOURNEY-G` | 缺口（Gap） | `JOURNEY-G01`：终点未到业务结果 |
| `JOURNEY-Inf` | 推断（Inference） | `JOURNEY-Inf01`：基于等待时长推断跨部门交接存在瓶颈 |
| `JOURNEY-F` | 痛点 / 机会条目（Pain-point or Opportunity item） | `JOURNEY-F01`：阶段 2 的重复提交 |

## Canvas 映射

Journey 确认包到 `render-contract-journey.md` 的 HTML 锚点映射：

| 确认包 section | HTML 锚点 |
|---|---|
| 6：阶段 n | `journey-stage-{n}` |
| 6：阶段 n action | `journey-stage-{n}-action` |
| 6：阶段 n touchpoint_system | `journey-stage-{n}-touchpoint-system` |
| 6：阶段 n emotion | `journey-stage-{n}-emotion` |
| 6：阶段 n pain_point | `journey-stage-{n}-pain-point` |
| 6：阶段 n opportunity | `journey-stage-{n}-opportunity` |
| 6a：user_perspective | `journey-quality-user-perspective` |
| 6a：business_outcome | `journey-quality-business-outcome` |
| 6a：pain_opportunity_visible | `journey-quality-pain-opportunity-visible` |
| 6a：no_solution_bias | `journey-quality-no-solution-bias` |

> **v2.3.4 PATCH 起**：6b 节内容已并入 5 行主表的第 4 / 5 行（`pain-point` / `opportunity`），不再以独立 DOM 锚点承载；`JOURNEY-Fxx` 条目仍存在于 6b 确认包 Markdown 内，但运行时模板不再渲染独立 section。

## 动态阶段字段要求

第 6 节的每行必须包含：

- **阶段序号**：从 1 开始连续递增
- **阶段名**
- **行动**
- **触点与系统**
- **情绪**
- **痛点**
- **机会**
- **来源引用**

阶段数量由第 6 节表格数据行决定。最低 3 个有效阶段。每个有效阶段 5 行字段必须全部有内容或显式标为缺口。

## 质量鉴别字段要求

质量鉴别是正式画布外显能力，不只是 Gate 内部判断。确认包第 6a 节是后续 Canvas 治理区块的事实源。

第 6a 节的每行必须包含：

- **维度**：user_perspective / business_outcome / pain_opportunity_visible / no_solution_bias
- **判定**：通过 / 不通过
- **依据**：Key Points section 或确认包 section，不引用逐字稿段落

判定由 `journey-distill` 在 Stage 2 中基于讨论证据线索给出，不由 `canvas-render` 推断。若讨论中完全未涉及某维度，标"未判定"并在缺口表登记。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使 Journey 阶段地图或质量判定无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变痛点与机会的判断或旅程边界 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

## 不得自动引入

- 不得强制固定阶段数量。
- 不得把 Journey 主表改成七要素。
- 不得把质量鉴别写成主表第 6 行。
- 不得自动生成 Future Journey、解决方案或 AI 应用判断。
- 不得把"组织部门负责什么"当作用户行动。
