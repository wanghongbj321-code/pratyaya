# MVL Canvas 内容与视觉规范

MVL Canvas 是六次工作坊已确认结论的完整展示层。正式页面只能读取通过结论闸门的模块 JSON。内容范围以 `workshop-canvas-map.md` 为准。

## 顶部

- MVL 名称
- 一句话概括：通过什么，为谁实现什么
- 阶段说明：模拟环境概念验证原型，非生产级系统

## 1. Intent（意图）

- 目标（Goal）
- 价值（Value）
- 成功指标（Success Metrics）：指标、基线、目标、衡量方式

## 2. User（用户）

- 用户
- 需求
- 痛点
- 最重要的结果

可以有一个或多个用户，数量由讨论决定，不预设固定用户层数。

## 3. Agent Team（人 + Agent）

- 角色
- 职责
- 是否 Agent
- 决策边界
- 协作模式

“是否 Agent”只按“人 / Agent / 人与 Agent 协作”表达，不额外引入其他角色分层术语。

## 4. Workflow（工作流）

- 流程步骤
- 自动化节点（Agent 执行）
- 人工操作/确认节点
- 人审 + Agent 执行节点
- 关键规则

这是本次 MVL 的 AI 应用工作流，不是普通业务流程复述。流程必须标明触发、完成和流向，并明确 AI 在每个相关节点做什么、由谁审核或确认；具体步骤数量由已确认内容决定。三类节点必须分别呈现，缺失时进入缺口，不能为了出图自动补写。

## 5. Context（上下文）

- 知识库
- 数据源
- 工具与技能

只列讨论确认的项目，并说明可获得性；不得按常见做法自动补全。

## 6. Validation（闭环验证）

- 能否执行：三轮验证中关于自治流程、交互和落地条件的结论与证据
- 能否创造价值：成功指标的目标值、实测值和衡量方式
- 能否持续进化：已实际形成或明确计划形成的 Prompt、Workflow、SOP、Knowledge、Agent、Template、Best Practice、数据资产

如果某类资产未讨论或未形成，就显示缺口，不自动生成资产名称。

## 底部

- 一句话总结：本次 MVL 在模拟环境中证明了什么
- 能力边界与关键未决项

## 六次模块的渐进填充

| 模块 | 填充范围 |
|---|---|
| M1 | Intent |
| M2 | User；Workflow 现状流程素材 |
| M3 | Intent 回填；Workflow 草案 |
| M4 | Workflow 冻结版；Agent Team；Context |
| M5 | Validation：能否执行、能否创造价值；信任与风险控制 |
| M6 | Validation：能否持续进化；顶部和底部总结 |

模块详情页同时展示该次日程的中间产出，具体映射见 `workshop-canvas-map.md`。

## 事实源与版本

- 唯一业务事实源：`modules/module-N.json`
- 正式渲染要求：`gate.render_allowed=true`
- 页面版本、模块版本和 `approval.version` 必须一致
- 内容修改必须先回写 JSON、升版和重新确认
- 缺失字段不得补写；草稿显示“未讨论/待确认”，正式版由闸门阻断

## HTML 与本地打开

- 单文件、内联 CSS/JS、系统字体、无网络依赖
- 数据内嵌在 `<script type="application/json" id="canvas-data">`
- 不用 `fetch()` 读取本地 JSON，不用 iframe 嵌套本地 HTML
- 全局 Canvas 使用普通相对链接进入模块详情
- 支持本地双击、打印和导出 PDF
- 本地编辑只能保存批注，不能覆盖已确认事实

## 视觉要求

- 专业商务风，深蓝或低饱和机构色为主，白底卡片
- 完整保留六个大模块及其固定小模块，不新增第七个大模块
- 核心结论和关键指标优先，详情证据下钻查看
- 草稿页显示“草稿 / 未确认 / 禁止用于管理层决策”
- 正式页面不得出现未关闭的 blocker/major
- A3/A4 横向打印保持可读

完整 HTML 实现约束见 `../../canvas-render/references/render-contract.md`。
