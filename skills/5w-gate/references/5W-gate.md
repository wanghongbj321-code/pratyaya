# 5W Gate 放行条件

本文件是 `5w-gate` 的评估依据，定义 5W 确认包的稳定放行条件、分类与来源 ID。

## 放行条件（7 条，稳定 ID）

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `5W-GATE-01` | 问题陈述是**事实而非结论**（可验证，非"团队混乱"类结论） | `information_integrity` | low | 5W-problem |
| `5W-GATE-02` | Why 1-5 **每层有内容或显式标为缺口** | `information_integrity` | low | 5W-why-1..5 |
| `5W-GATE-03` | 每层"因为"答案**附证据**（日期 / 记录 / 日志） | `information_integrity` | low | 5W-why-1..5 |
| `5W-GATE-04` | **无个人归因**（判别记录 §11 无未处理坏答案；"没注意 / 素质差"已打回） | `information_integrity` | low | 5W-why-1..5, 5W-rubric |
| `5W-GATE-05` | 因果链通过**"因此"检验**（根因 → 因此 → … → 问题 逻辑可辨识） | `business_risk` | medium | 5W-root |
| `5W-GATE-06` | 根因**可行动**（处理它防复发）且**对策四要素齐全** | `business_risk` | medium | 5W-root, 5W-countermeasures |
| `5W-GATE-07` | 对策是**预防性回应**而非症状修复（加滤网 vs 换保险丝） | `business_risk` | medium | 5W-countermeasures |

## 分类与可 override 关系

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立（事实陈述、证据、反归因） | **否** |
| `business_risk` | 结论已有事实基础，但对策有效性的判断（因此链、可行动、预防性）不完整 | **是**（填写理由后） |

> **核心规则**：用户可以接受现实中对策有效性的主观风险，但不能通过 override 把不存在的信息变成事实。

**分类汇总**：4 条 `information_integrity`（不可 override）+ 3 条 `business_risk`（可 override）。

**与 GC / V2C Gate 的差异**：

- 5W-GATE-01~04 聚焦**因果链诚实性**（事实陈述、证据、反归因），不可 override——根因分析的底线是证据与诚实；
- 5W-GATE-05~07 聚焦**对策有效性**（因此链、可行动、预防性），属业务判断，可 override（团队可接受"对策方向对但尚不完美"的风险），override 时 caveat 显式呈现。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得超过正式 override。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使 5W 核心产出（问题陈述 / 因果链 / 根因）无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变根因分析的方向或对策 | 必须关闭或接受风险 |
| `minor` | 不改变核心结论 | 可后续补齐或明确接受风险 |

严重度（blocker / major / minor）与分类（information_integrity / business_risk）是两个维度：

- `information_integrity`：无论严重度，均不可正式 override；
- `business_risk`：用户可在看见影响并填写理由后 override；
- minor 仍不得静默忽略，必须关闭或显式接受。

## 来源 ID 约定

- `5W-problem`：确认包第 6 节（问题陈述）
- `5W-why-1..5`：确认包第 7 节（因果链五层）
- `5W-root`：确认包第 8 节（根本原因）
- `5W-countermeasures`：确认包第 9 节（对策四要素）
- `5W-rubric`：确认包第 11 节（判别记录）
- `5W-Gxx`：本画布缺口 ID
- `5W-Ixx`：本画布推断 ID
- `5W-Cxx`：本画布结论 ID

## 评估表输出格式

Gate 评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响和建议。评估报告格式见 `5w-gate/SKILL.md` 的"Gate 评估流程"。
