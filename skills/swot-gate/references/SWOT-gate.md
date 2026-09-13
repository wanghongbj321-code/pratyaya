# SWOT Gate 放行条件

本文件是 `swot-gate` 的评估依据，定义 SWOT 确认包的稳定放行条件、分类与来源 ID。

## 放行条件（8 条，稳定 ID）

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `SWOT-GATE-01` | 课题边界已确认，因素与策略符合该边界 | `information_integrity` | low | SWOT-topic |
| `SWOT-GATE-02` | 事实、判断、假设及来源如实记录，重要反证与冲突未被隐去 | `information_integrity` | low | SWOT-evidence |
| `SWOT-GATE-03` | 正式分类正确，策略引用存在且组合匹配，假设沿推导链保留 | `information_integrity` | low | SWOT-classification |
| `SWOT-GATE-04` | AI 推荐、用户决定、交接建议与已确认安排清楚区分 | `information_integrity` | low | SWOT-decision |
| `SWOT-GATE-05` | 因素足够具体，重要性有理由，已知重要因素没有无解释地遗漏 | `business_risk` | medium | SWOT-factors |
| `SWOT-GATE-06` | 策略说明作用机制、成立条件、资源约束及主要风险 | `business_risk` | medium | SWOT-strategies |
| `SWOT-GATE-07` | 比较了有意义的选项，取舍理由能回应决策问题 | `business_risk` | medium | SWOT-comparison |
| `SWOT-GATE-08` | 当前需要推进的事项有可承接的交接、验证与复审安排 | `business_risk` | medium | SWOT-handover |

## 分类与可 override 关系

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立（课题边界、证据记录、分类正确性、决定区分） | **否** |
| `business_risk` | 结论已有事实基础，但分析质量（因素具体性、策略完整性、取舍理由、交接安排）不完整 | **是**（填写理由后） |

> **核心规则**：用户可以接受现实中分析质量的主观风险，但不能通过 override 把不存在的信息变成事实。

**分类汇总**：4 条 `information_integrity` + 4 条 `business_risk`。

前四项（SWOT-GATE-01 至 04）属于**不可 override 的信息完整性**——课题边界、证据记录、分类正确性和决定区分是 SWOT 分析能否成立的基础，不能通过风险接受绕过。

后四项（SWOT-GATE-05 至 08）属于**可 override 的业务风险**——因素具体性、策略完整性、取舍理由和交接安排在现实中带主观性，团队可以接受"当前分析不完美但方向对"的风险。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得超过正式 override。

## 放行边界规则

| 场景 | 判定 |
|---|---|
| 假设已标明且结论限定为"先验证"，验证安排充分 | 可通过 |
| 候选因素不作为分类已成立的 TOWS 依据 | 可通过（保留候选身份） |
| 策略仍待决策但交接明确 | 可通过（用于提交评审） |
| 交接缺口：已明确角色但姓名未指定 | 提示（WARN） |
| 交接缺口：无人承接或缺时间/触发条件 | 商业风险失败（SWOT-GATE-08 FAIL） |
| 无可采用策略不自动失败 | 有依据的暂缓、停止或补证建议可通过 |
| 轻微不足 | 提示（WARN） |
| 影响当前决策的不足 | 失败（FAIL） |

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使画布核心产出（课题卡、因素分类、策略推导）无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变态势分析或策略方向 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

严重度（blocker / major / minor）与分类（information_integrity / business_risk）是两个维度：

- `information_integrity`：无论严重度，均不可正式 override；
- `business_risk`：用户可在看见影响并填写理由后 override；
- minor 仍不得静默忽略，必须关闭或显式接受。

## 来源 ID 约定

- `SWOT-topic`：确认包第 2 节（课题卡）
- `SWOT-evidence`：确认包第 3 节（SWOT 四象限）的因素证据字段
- `SWOT-classification`：确认包第 3 节（SWOT 四象限）的分类与第 6 节（TOWS 策略）的引用
- `SWOT-decision`：确认包第 7 节（选项比较与取舍）和第 8 节（最小交接与复审）
- `SWOT-factors`：确认包第 3 节（SWOT 四象限）的因素具体性与重要性
- `SWOT-strategies`：确认包第 6 节（TOWS 策略）的策略完整性
- `SWOT-comparison`：确认包第 7 节（选项比较与取舍）
- `SWOT-handover`：确认包第 8 节（最小交接与复审）
- `SWOT-Gxx`：本画布缺口 ID
- `SWOT-INF-NN`：本画布推断 ID
- `SWOT-Cxx`：本画布结论 ID

## 评估表输出格式

Gate 评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL/WARN、分类、风险等级、来源 ID、影响和建议。评估报告格式见 `swot-gate/SKILL.md` 的"Gate 评估流程"。
