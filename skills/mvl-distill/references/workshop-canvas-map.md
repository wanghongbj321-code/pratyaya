# 3 天日程与 MVL Canvas 唯一映射

本文件是三个 Skill 共用的内容边界。只采用两类输入：

1. 三天工作坊正式日程；
2. 已确认样图中的 Canvas 大模块与小模块。

不得把其他方法、术语或通用咨询框架自动变成必填 section。用户在讨论中主动采用的其他方法，只按原话留在模块详情中，不能因此改变全局 Canvas 结构，也不能成为放行条件。

## 统一术语

- 全程使用 **MVL（Minimum Verifiable Loop，最小可验证自治闭环）**。
- 样图仅作为 Canvas 结构参考；标题统一写"MVL Canvas"。
- 最终交付是**模拟环境概念验证原型**，属于**非生产级系统**。

## 全局 Canvas 固定结构

- 顶部：MVL 名称 / 一句话概括
- Intent：目标 / 价值 / 成功指标
- User：用户 / 需求 / 痛点 / 最重要的结果
- Agent Team：角色 / 职责 / 是否 Agent / 决策边界 / 协作模式
- Workflow：流程步骤 / 自动化节点（Agent 执行） / 人工操作/确认节点 / 人审 + Agent 执行节点 / 关键规则
- Context：知识库 / 数据源 / 工具与技能
- Validation：能否执行 / 能否创造价值 / 能否持续进化
- 底部：一句话总结

全局 Canvas 只展示上述固定结构。每次工作坊产生的证据、HMW、原型迭代记录、验证记录和复盘材料进入对应模块详情页，并通过全局 Canvas 下钻查看。

## 六次工作坊的固定产出

| 模块 | 日程主题 | 必须形成的模块详情产出 | 对全局 Canvas 的贡献 |
|---|---|---|---|
| M1 | 战略对齐、项目分组与闭环证据准备 | 核心业务目标与价值；业务数据、用户案例、现有流程痛点等证据；成功指标；校验标准；边界；项目分组 | Intent：目标、价值、成功指标 |
| M2 | 需求发现、用户与真实流程拆解 | 用户；核心诉求；使用场景和行为链路；需求；痛点；最重要结果；真实现状流程；AI 刚需/增值需求及优先级 | User；为 Workflow 提供现状流程 |
| M3 | 闭环目标定义、HMW 拆解与方案方向锁定 | HMW；闭环目标；能力指标；验收标准；边界；AI 方案方向；从触发到结果的 AI 应用工作流草案；三类节点；分层验证维度 | 回填 Intent；形成 Workflow 草案 |
| M4 | 闭环冻结、原型两轮迭代与开发筹备 | 冻结 AI 应用工作流、能力范围、功能边界和验收标准；明确三类节点、流向和规则；两轮原型及修改；人和 Agent 的角色职责、决策边界与协作模式；知识、数据、工具；开发、场景测试、用户验证准备；团队分工和迭代节奏 | Workflow 冻结版；Agent Team；Context |
| M5 | 三轮验证、交互优化与信任控制校验 | 第一轮自治流程可用性；第二轮交互优化和用户习惯适配；第三轮信任与风险控制；每轮方法、发现、修改、结果；问题整改 | Validation：能否执行、能否创造价值；信任与风险控制 |
| M6 | 终极打磨、方案择优、成果演示与闭环总结 | 最终方案；多方案三维对比；演示结论；三轮验证数据、问题整改和经验复盘；能力边界；适配场景；优化空间；可复用资产；后续迭代、规模化复制、生产化建议与推进计划；两句总结 | Validation：能否持续进化；顶部一句话概括；底部一句话总结 |

## 模块 Markdown 必填 section

以下 section 写入 `modules/Mx-v{N}.md` 确认包，名称必须固定：

| 模块 | 必填 section |
|---|---|
| M1 | `goal`、`value`、`success_metrics`、`evidence`、`boundary`、`acceptance`、`grouping` |
| M2 | `users`、`needs`、`pain_points`、`most_important_outcomes`、`current_workflow`、`requirements` |
| M3 | `hmw`、`loop_goal`、`capability_metrics`、`acceptance`、`boundary`、`solution_direction`、`workflow_draft`、`validation_dimensions` |
| M4 | `agent_team`、`collaboration_mode`、`workflow_final`、`knowledge`、`data_sources`、`tools_skills`、`prototype_rounds`、`delivery_preparation` |
| M5 | `validation_rounds`、`can_execute`、`can_create_value`、`trust_risk_controls`、`issues_corrections` |
| M6 | `final_solution`、`solution_comparison`、`demo_summary`、`validation_review`、`capability_boundary`、`applicable_scenarios`、`optimization_space`、`evolution_assets`、`next_step_plan`、`headline`、`takeaway` |

section 没有讨论到时，不得补写。将它标为缺口并说明对本次模块产出和最终 Canvas 的影响。

## AI 工作流结构契约

Canvas 第 4 板块不是普通业务流程记录，而是本次 MVL 要验证的 **AI 应用工作流**。M3 的 `workflow_draft` 与 M4 的 `workflow_final` 使用同一结构（写入确认包 Markdown，使用以下固定小节）：

```markdown
## workflow_draft / workflow_final

- **触发条件（trigger）**：闭环触发条件
- **步骤（steps）**：按流向排列的步骤（列表）
- **完成条件（completion_condition）**：闭环完成条件
- **Agent 执行节点（agent_execution_nodes）**：自动化节点（Agent 执行）
- **人工操作/确认节点（human_operation_confirmation_nodes）**：人工操作/确认节点
- **人审 + Agent 执行节点（human_review_agent_execution_nodes）**：人审后由 Agent 执行，或人审与 Agent 联合执行的节点
- **关键规则（rules）**：决定流向、升级、停止或回退的关键规则
```

三类节点都必须由讨论形成且至少有一项。每个节点应能在 `steps` 中定位，并明确输入、输出和流向。若缺少任一类节点，或工作流没有体现 AI 如何参与，就不能形成正式 Workflow；不得拿现状业务流程或通用流程图代替。

## 不得自动引入

- 不得强制固定年限的愿景、固定权重评分或固定用户层数。
- 不得强制特定头脑风暴、角色分层、攻击分类或旅程方法。
- 不得因为模板有空间而补充新角色、新指标、新系统、新风险或新资产。
- 不得把"可复用""规模化""生产化"扩写为日程没有讨论的实施方案。
