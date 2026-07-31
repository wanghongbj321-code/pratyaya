# M5 闸门策略

> M5 模块（三轮验证、交互优化与信任控制校验）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

> **v4.0.0 更新**：每条放行条件增加稳定 ID、分类（`information_integrity` / `business_risk`）和风险等级，供 Gate 报告与 override 审计引用。

## 必填 section

参见 `../../mvl-distill/references/workshop-canvas-map.md` 中"M5 必填 section"：

- `validation_rounds`（三轮验证记录：方法、发现、修改、结果）
- `can_execute`（能否执行：自治流程可用性结论与证据）
- `can_create_value`（能否创造价值：成功指标的目标值、实测值和衡量方式）
- `trust_risk_controls`（信任与风险控制：第三轮验证的结论与整改）
- `issues_corrections`（问题整改）

## 必须形成的结论

三轮验证分别完成可用性、交互、信任与风险控制校验，并记录修改和整改。

## 常见 blocker

- 三轮目标混淆（第一轮做交互、第二轮做信任——目标未分离）
- 缺轮次（只做了一轮或两轮验证就声明完成）
- 验证结论无证据（仅说"效果好"等无数据描述）
- 遗留漏洞被隐藏（发现问题未进入 issues_corrections）
- can_create_value 未与 M1 success_metrics 对齐（验证指标与成功指标无对应）
- 信任风控未覆盖（trust_risk_controls 为空或仅写"有风险"等无具体控制项）

## 评估要点

- 三轮验证是否目标分离（第一轮：自治流程可用性；第二轮：交互；第三轮：信任与风险）？
- 每轮验证是否含：方法 / 发现 / 修改 / 结果？
- can_create_value 是否与 M1 success_metrics 三要素（指标/基线/目标）对应？
- trust_risk_controls 是否含具体控制项（如权限边界、异常处理、人类兜底）？
- issues_corrections 是否完整记录每个发现的问题与对应整改？

## 放行条件

每条放行条件拥有稳定 ID、分类和风险等级，供 Gate 报告与 `override_audit.items` 引用。

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `M5-GATE-01` | 5 个必填 section 全部有内容或显式标为缺口 | `information_integrity` | low | M5 必填 section 表 |
| `M5-GATE-02` | validation_rounds 至少 3 轮，目标分别为可用性 / 交互 / 信任 | `information_integrity` | low | M5-validation_rounds |
| `M5-GATE-03` | 每轮验证含方法 / 发现 / 修改 / 结果 | `information_integrity` | low | M5-validation_rounds |
| `M5-GATE-04` | can_create_value 至少一项与 M1 success_metrics 明确对应（含目标值 + 实测值 + 衡量方式） | `business_risk` | high | M5-can_create_value, M1-success_metrics |
| `M5-GATE-05` | trust_risk_controls 至少 3 项具体控制（含控制对象 / 控制方式 / 触发条件） | `business_risk` | high | M5-trust_risk_controls |
| `M5-GATE-06` | issues_corrections 中所有问题状态为 closed 或 accepted_risk | `business_risk` | medium | M5-issues_corrections |

**详细说明**：

满足以下全部条件才可放行：

1. `M5-GATE-01`：5 个必填 section 全部有内容或显式标为缺口。
2. `M5-GATE-02`：validation_rounds 至少 3 轮，目标分别为可用性 / 交互 / 信任。
3. `M5-GATE-03`：每轮验证含方法 / 发现 / 修改 / 结果。
4. `M5-GATE-04`：can_create_value 至少一项与 M1 success_metrics 明确对应（含目标值 + 实测值 + 衡量方式）。
5. `M5-GATE-05`：trust_risk_controls 至少 3 项具体控制（含控制对象 / 控制方式 / 触发条件）。
6. `M5-GATE-06`：issues_corrections 中所有问题状态为 closed 或 accepted_risk。

> **分类说明**：
> - `M5-GATE-01` ~ `M5-GATE-03` 均为 `information_integrity`，FAIL 时不可 override。
> - `M5-GATE-04` ~ `M5-GATE-06` 均为 `business_risk`（实测值与目标值差距、未完全整改的信任控制、未完全关闭的问题是模拟环境下常见的业务风险），FAIL 时用户可显式 override 并填写理由；Gate 仍输出 `gate_recommendation=fail`，但 `override_eligible=true`。
> - `M5-GATE-04` / `M5-GATE-05` 风险等级为 `high`，override 时应慎重并提供详细补救措施。

## 来源 ID 约定

- `M5-{section}`：对应必填 section（如 `M5-validation_rounds`、`M5-can_create_value`）。
- `M5-Gxx`：本模块缺口 ID。
- `M5-Ixx`：本模块推断 ID。
- `M5-Cxx`：本模块结论 ID。
