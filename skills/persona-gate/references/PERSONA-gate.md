# Persona Gate 放行条件

本文件是 `persona-gate` 的评估依据，定义 Persona 确认包的稳定放行条件、分类与来源 ID。

## 放行条件（6 条，稳定 ID）

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `PERSONA-GATE-01` | 关键基本信息（`name` / `job_title` / `industry`）有值 | `information_integrity` | low | `PERSONA-basic` |
| `PERSONA-GATE-02` | 六宫格 6 区全部有内容或显式标为缺口 | `information_integrity` | low | `PERSONA-cells` |
| `PERSONA-GATE-03` | 行为 / 痛点有真实出处（`evidence_based` 通过） | `business_risk` | medium | `PERSONA-quality` |
| `PERSONA-GATE-04` | 痛点用用户原话（`pain_in_voice` 通过） | `business_risk` | medium | `PERSONA-quality` |
| `PERSONA-GATE-05` | 画像具体非刻板（`concrete` 通过） | `information_integrity` | low | `PERSONA-quality` |
| `PERSONA-GATE-06` | 质量鉴别四维度全部判定，无未判定项 | `information_integrity` | low | `PERSONA-quality` |

## 分类与可 override 关系

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立（基本信息覆盖、六宫格覆盖、质量判定完整性、画像具体性） | **否** |
| `business_risk` | 结论已有事实基础，但行为/痛点的真实出处或用户原话不完整 | **是**（填写理由后） |

> **核心规则**：用户可以接受现实中画像行为/痛点描述的主观风险，但不能通过 override 把不存在的信息变成事实。

**分类汇总**：4 条 `information_integrity` + 2 条 `business_risk`。

与 HMW Gate 结构一致；PERSONA-GATE-03 / 04 属于**可 override 的业务风险**——行为/痛点的真实出处在现实中带主观性，团队可以接受"当前描述不完美但方向对"的风险。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得超过正式 override。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使画像核心产出（基本信息或六宫格）无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变画像的代表性或可信度 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

严重度（blocker / major / minor）与分类（information_integrity / business_risk）是两个维度：

- `information_integrity`：无论严重度，均不可正式 override；
- `business_risk`：用户可在看见影响并填写理由后 override；
- minor 仍不得静默忽略，必须关闭或显式接受。

## 来源 ID 约定

- `PERSONA-basic`：确认包第 6 节（9 基本信息）
- `PERSONA-cells`：确认包第 6 节（6 宫格）
- `PERSONA-quality`：确认包第 6a 节（质量鉴别）
- `PERSONA-Gxx`：本画布缺口 ID
- `PERSONA-Infxx`：本画布推断 ID
- `PERSONA-Cxx`：本画布结论 ID

## 评估表输出格式

Gate 评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响和建议。评估报告格式见 `persona-gate/SKILL.md` 的"Gate 评估流程"。
