# 模块核心价值闸门

只根据正式日程和 `../../mvl-distill/references/workshop-canvas-map.md` 判断模块是否完成。额外方法、固定分类或通用咨询框架不能成为缺口或 blocker。

## 六个模块的最低可用结论

| 模块 | 必须形成的结论 | 常见 blocker |
|---|---|---|
| M1 | 业务目标、价值、成功指标、核心证据、校验标准、边界和项目分组已明确 | 没有证据；指标缺基线/目标/衡量方式；边界或校验标准不清 |
| M2 | 用户、需求、痛点、最重要结果、真实流程和需求优先级已明确 | 用假想流程代替真实流程；痛点无依据；核心需求未排序 |
| M3 | HMW、闭环目标、指标、验收、边界、方案方向、业务链路、关键节点和验证维度已明确 | HMW 与核心问题无关；闭环无起止；方案方向或验收标准未锁定 |
| M4 | AI 应用 Workflow 已冻结，三类节点、流向和规则均明确；两轮原型有记录；Agent Team、Context、开发/测试/用户验证准备和迭代节奏已明确 | 只有普通业务流程、没有体现 AI；缺少任一节点类型；工作流无起止或流向；两轮原型无结果；角色决策边界不清；知识/数据/工具缺失；筹备责任不清 |
| M5 | 三轮验证分别完成可用性、交互、信任与风险控制校验，并记录修改和整改 | 三轮目标混淆或缺轮次；验证结论无证据；遗留漏洞被隐藏 |
| M6 | 最终方案、三维择优、演示结论、验证复盘、能力边界、适配场景、优化空间、资产和后续计划均已确认 | 把未验证内容写成成果；边界不清；总结与证据冲突；后续建议不是讨论结论 |

## 缺口等级

- `blocker`：使当前日程的核心产出或对应 Canvas 模块无法成立。
- `major`：会显著改变范围、方案或验证判断。
- `minor`：不改变核心结论，可后续补齐或明确接受风险。

每个缺口必须包含：缺什么、缺失影响、最少补问、状态，以及解决后的证据引用。

## 结论确认

| ID | 结论 | 类型 | 证据引用 | 置信度 | 审核状态 |
|---|---|---|---|---|---|
| M1-C01 | … | fact / decision / hypothesis / recommendation | M1-T01-P012 | high / medium / low / unknown | proposed / disputed / confirmed / validated / rejected |

确认时必须让用户看到：

1. 当前模块固定字段；
2. 结论及依据；
3. 缺口和缺失影响；
4. 推断；
5. 当前版本。

## 对齐闸门

每个模块在进入 `review_ready` 之前，必须完成对齐检查，并将结果写入 `modules/module-N.json` 的 `alignment` 字段。

对齐检查包含：

1. **角色识别**：列出参与讨论的所有角色（业务方、技术方、管理层等）
2. **分歧点提取**：识别各方在同一话题上的不同理解
3. **共识地图**：标注共识点、分歧点、决策留痕
4. **语言翻译**：检查业务语言和技术语言混用
5. **决策留痕**：记录关键决策由谁拍板、谁认可

对齐数据结构（符合 `schemas/module-record.schema.json`）：

- `consensus`：共识点数组，每项含 `id`、`statement`、`participants`（含 name+role）、`evidence_refs`
- `divergences`：分歧点数组，每项含 `id`、`topic`、`severity`、`impact`、`positions`（含 name+role+view）、`resolution_status`（open/resolved/accepted_risk）、`evidence_refs`；当 `resolution_status` 为 `accepted_risk` 时，`accepted_by` 必须出现在 `approval.confirmed_by` 中
- `decisions`：决策数组，每项含 `id`、`decision`、`decided_by`（含 name+role）、`decided_at`、`version`、`acknowledged_by`（含 name+role）

**状态跃迁规则**：

- 存在未解决的 blocker/major 分歧（`resolution_status=open` 且 `severity ∈ {blocker, major}`）→ 不得进入 `review_ready`
- 所有 blocker/major 分歧已 resolved 或 accepted_risk → 可进入 `review_ready`
- 闸门脚本 `check_gate.py` 会确定性检查以上条件

## 全局汇总附加闸门

全局汇总时，额外执行以下对齐检查：

- Intent 的成功指标是否在 Validation 中有对应验证结果；
- User 的最重要结果是否由冻结 Workflow 承接；
- Workflow 是否是从触发到结果的 AI 应用工作流，三类节点是否齐全，并有 Agent Team 和 Context 支撑；
- M4 两轮原型与 M5 三轮验证的修改是否进入最终方案；
- M6 的能力边界、适配场景和总结是否与验证证据一致；
- 六大模块名称、数字、边界和版本是否一致；
- 页面是否明确"模拟环境概念验证原型，非生产级系统"。
- **跨模块对齐检查**：业务方定义的"价值"（M1）是否在技术方的"验证结果"（M5）中得到证实？业务方的"用户痛点"（M2）是否在"冻结工作流"（M4）中被逐一承接？技术方的"Agent 决策边界"（M4）是否与业务方在 Workflow 各节点的期望一致？管理层关注的风险是否在 Validation（M5）和能力边界（M6）中有对应？

如果存在跨模块对齐冲突，必须回退相关模块升版和重审，不在全局页面中静默修正。
