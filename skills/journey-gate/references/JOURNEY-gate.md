# User Journey Gate 放行条件

本文件是 `journey-gate` 的评估依据，定义 Journey 确认包的稳定放行条件、分类与来源 ID。

> **v2.3.2 PATCH**：6a 质量维度来源由 `friction_visible` 切换为 `pain_opportunity_visible`，对应 gate 评估项 `JOURNEY-GATE-03` / `JOURNEY-GATE-06` 的判定来源同步；6b 来源 ID 由 `JOURNEY-friction` 切换为 `JOURNEY-pain-opportunity`；GATE-03 的覆盖要求由「至少 2 个等待 / 返工信息、1 个风险节点」切换为「至少 2 个痛点、1 个机会」；ID 前缀 `JOURNEY-Fxx` 含义由「断点 / 机会」切换为「痛点 / 机会条目」。

## 放行条件（6 条，稳定 ID）

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `JOURNEY-GATE-01` | 至少 3 个有效阶段，且阶段名清晰 | `information_integrity` | low | JOURNEY-map |
| `JOURNEY-GATE-02` | 每个阶段 5 行字段全部有内容或显式标为缺口 | `information_integrity` | low | JOURNEY-map |
| `JOURNEY-GATE-03` | 至少标出 2 个痛点、1 个机会，或明确说明未发现 | `information_integrity` | low | JOURNEY-map / JOURNEY-pain-opportunity |
| `JOURNEY-GATE-04` | 旅程终点到达业务结果，不停在系统处理完 | `business_risk` | medium | JOURNEY-quality（business_outcome） |
| `JOURNEY-GATE-05` | 以用户视角描述，不用组织图 / 部门流程替代 | `business_risk` | medium | JOURNEY-quality（user_perspective） |
| `JOURNEY-GATE-06` | 当前旅程没有提前写入解决方案 / AI 应用判断 | `business_risk` | medium | JOURNEY-quality（no_solution_bias） |

## 分类与可 override 关系

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立（阶段数量、主表字段、痛点与机会条目覆盖等） | **否** |
| `business_risk` | 结论已有事实基础，但旅程边界、用户视角或方案预设存在风险 | **是**（填写理由后） |

> **核心规则**：用户可以接受现实中的业务判断风险，但不能通过 override 把不存在的信息变成事实。

**分类汇总**：3 条 `information_integrity` + 3 条 `business_risk`。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得超过正式 override。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使 Journey 阶段地图或质量判定无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变痛点与机会的判断或旅程边界 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

严重度（blocker / major / minor）与分类（information_integrity / business_risk）是两个维度：

- `information_integrity`：无论严重度，均不可正式 override；
- `business_risk`：用户可在看见影响并填写理由后 override；
- minor 仍不得静默忽略，必须关闭或显式接受。

## 来源 ID 约定

- `JOURNEY-map`：确认包第 6 节（阶段地图）
- `JOURNEY-quality`：确认包第 6a 节（质量鉴别）
- `JOURNEY-pain-opportunity`：确认包第 6b 节（痛点与机会）
- `JOURNEY-Gxx`：本画布缺口 ID
- `JOURNEY-Infxx`：本画布推断 ID
- `JOURNEY-Cxx`：本画布结论 ID
- `JOURNEY-Fxx`：本画布痛点 / 机会条目 ID

## 评估表输出格式

Gate 评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响和建议。评估报告格式见 `journey-gate/SKILL.md` 的"Gate 评估流程"。
