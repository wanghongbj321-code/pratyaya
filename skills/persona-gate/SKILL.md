---
name: persona-gate
description: 用户画像闸门。对 PERSONA-{slug}-v{N}.md 确认包执行 6 项放行条件检查，只输出 gate_recommendation 与 override_eligible 建议。
triggers:
  - "用户画像闸门"
  - "persona gate"
  - "画像质量检查"
---

# Persona Gate（用户画像闸门）

> 对 `PERSONA-{slug}-v{N}.md` 确认包执行确定性的 6 项放行条件检查。Gate 是建议者：只输出 Markdown 报告，绝不修改 `state.json`、确认包治理字段或最终渲染授权。

## 输入

- 当前版本 `modules/PERSONA-{slug}-v{N}.md`
- `references/PERSONA-gate.md`

读取确认包的 9 基本信息、6 宫格、6a 质量鉴别和 §8 缺口表；只引用确认包与 Key Points，不把逐字稿写成正式事实。

## 放行条件

逐项执行 `references/PERSONA-gate.md` 中的稳定 ID：

| ID | 检查项 | 分类 | 可 override |
|---|---|---|---|
| `PERSONA-GATE-01` | name / job_title / industry 有值 | information_integrity | 否 |
| `PERSONA-GATE-02` | 六宫格 6 区有内容或显式缺口 | information_integrity | 否 |
| `PERSONA-GATE-03` | 行为 / 痛点有真实出处 | business_risk | 是 |
| `PERSONA-GATE-04` | 痛点用用户原话 | business_risk | 是 |
| `PERSONA-GATE-05` | 画像具体非刻板 | information_integrity | 否 |
| `PERSONA-GATE-06` | 质量四维度均已判定 | information_integrity | 否 |

规则：

1. 全部 PASS → `gate_recommendation=pass`、`override_eligible=false`。
2. 只有 `PERSONA-GATE-03 / 04` 的 `business_risk` FAIL → `gate_recommendation=fail`、`override_eligible=true`。
3. 任一 `information_integrity` FAIL → `gate_recommendation=fail`、`override_eligible=false`。
4. `information_integrity` 失败不得以 override 把缺失信息变成事实。

## 输出：Gate 建议报告

输出 `PERSONA-gate-report-v{N}.md`：

```markdown
# 用户画像 Gate 报告 v{N}

> 画布类型：User Persona
> 确认包版本：v{N}
> gate_recommendation：pass / fail
> override_eligible：true / false

## 检查明细

| 稳定 ID | 检查项 | PASS/FAIL | 分类 | 风险等级 | 来源 ID | 影响 | 建议 |
|---|---|---|---|---|---|---|---|
| PERSONA-GATE-01 | ... | PASS / FAIL | information_integrity | low | PERSONA-basic | ... | ... |

## 建议动作

- Gate PASS：由主 Agent 展示报告，等待用户确认 v{N}。
- 仅 business_risk FAIL：由主 Agent 展示影响并提供 override 选项。
- 含 information_integrity FAIL：返回补问或修订；不提供 override。
```

## 授权边界

- 本 Skill 不决定 `render_authorized`，不决定 `confirmation_mode`，不写 `override_audit`。
- 输出 Gate 报告文件名使用 `modules/PERSONA-{slug}-gate-report-v{N}.md`；slug 不进入 `PERSONA-GATE-XX` 稳定 ID。
- 主 Agent 在用户已阅读报告并作出明确选择后，才将 `gate_recommendation`、用户确认和 override 审计写入 `state.persona.{slug}` 与确认包 §12。
- 本 Skill 不渲染 Canvas；正式渲染仍须由 `canvas-render` 在用户授权后执行。

## 质量红线

1. 每条报告记录必须有稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响与建议。
2. 不编造证据，不因版面完整而把未讨论内容写成通过。
3. `PERSONA-GATE-03 / 04` 之外的失败不得标记为可 override。
4. Gate 失败不自动改变状态；状态迁移由用户决策和主 Agent 完成。
