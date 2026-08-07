# HMW Gate 放行条件

本文件是 `hmw-gate` 的评估依据，定义 HMW 确认包的稳定放行条件、分类与来源 ID。

## 放行条件（6 条，稳定 ID）

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `HMW-GATE-01` | 问题情境含用户时刻（谁 / 何时 / 卡住） | `information_integrity` | low | HMW-state |
| `HMW-GATE-02` | HMW 问句**不含预设解法**（删技术名词可读通） | `business_risk` | medium | HMW-quality（preset_solution） |
| `HMW-GATE-03` | HMW 含**张力**（想要 vs 现实可辨识） | `business_risk` | medium | HMW-quality（tension） |
| `HMW-GATE-04` | for / so_that 明确具体 | `information_integrity` | low | HMW-state |
| `HMW-GATE-05` | 至少 1–2 条想法种子，且回应 HMW 问句 | `information_integrity` | low | HMW-idea |
| `HMW-GATE-06` | 质量鉴别四维度全部判定，无未判定项 | `information_integrity` | low | HMW-quality |

## 分类与可 override 关系

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立（陈述字段覆盖、想法种子、质量判定完整性） | **否** |
| `business_risk` | 结论已有事实基础，但问题框定的正确性（是否预设解法、是否含张力）不完整 | **是**（填写理由后） |

> **核心规则**：用户可以接受现实中问题框定的主观风险，但不能通过 override 把不存在的信息变成事实。

**分类汇总**：4 条 `information_integrity` + 2 条 `business_risk`。

与 GC Gate 结构一致；HMW-GATE-02 / 03 属于**可 override 的业务风险**——问题框定的正确性在现实中带主观性，团队可以接受"当前问句不完美但方向对"的风险。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得超过正式 override。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使 HMW 陈述或质量判定无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变问题重构的方向 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

严重度（blocker / major / minor）与分类（information_integrity / business_risk）是两个维度：

- `information_integrity`：无论严重度，均不可正式 override；
- `business_risk`：用户可在看见影响并填写理由后 override；
- minor 仍不得静默忽略，必须关闭或显式接受。

## 来源 ID 约定

- `HMW-state`：确认包第 6 节（HMW 陈述）
- `HMW-quality`：确认包第 6a 节（质量鉴别）
- `HMW-idea`：确认包第 6b 节（想法种子）
- `HMW-coherence`：确认包第 6c 节（想法 ↔ HMW 对应）
- `HMW-Gxx`：本画布缺口 ID
- `HMW-Inf-N`：本画布推断 ID（与想法种子 `HMW-Idea-N` 区分）
- `HMW-Cxx`：本画布结论 ID

## 评估表输出格式

Gate 评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响和建议。评估报告格式见 `hmw-gate/SKILL.md` 的"Gate 评估流程"。
