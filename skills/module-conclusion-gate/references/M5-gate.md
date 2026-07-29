# M5 闸门策略

> M5 模块（三轮验证、交互优化与信任控制校验）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

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

满足以下全部条件才可放行：

1. 5 个必填 section 全部有内容或显式标为缺口；
2. validation_rounds 至少 3 轮，目标分别为可用性 / 交互 / 信任；
3. 每轮验证含方法 / 发现 / 修改 / 结果；
4. can_create_value 至少一项与 M1 success_metrics 明确对应（含目标值 + 实测值 + 衡量方式）；
5. trust_risk_controls 至少 3 项具体控制（含控制对象 / 控制方式 / 触发条件）；
6. issues_corrections 中所有问题状态为 closed 或 accepted_risk。
