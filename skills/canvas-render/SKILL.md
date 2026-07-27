---
name: canvas-render
description: 把已通过结论闸门的 MVL 模块 JSON 渲染为可编辑、可追溯、离线可打开的 HTML Canvas，并在六模块完成后生成可下钻的全局 Canvas。用户要求生成模块画布、全局画布或管理层汇报页面时使用。
---

# Canvas 渲染

这个 Skill 是展示层，不是分析层。只把已确认的结构化事实源转成 HTML，不从转写直接提炼，也不为了填满页面新增、润色或补齐业务结论。

渲染前读取 `../mvl-distill/references/workshop-canvas-map.md` 和 `../mvl-distill/references/mvl-canvas-spec.md`。它们定义唯一允许的全局 Canvas 大/小模块及模块详情产出。

同时读取 `references/html-slides-adaptation.md` 和仓库 `html-templates/index.json`。前者把 `html-slides` 中适用于 Canvas 的能力收敛为模板选择、设计系统继承、浏览器预览、打印和离线交付规则；后者只登记四个批准使用的视觉外壳。

## 正式渲染前置条件

1. 读取 `modules/module-N.json`，不要以 Markdown 预览或聊天上下文作为事实源。
2. 运行：

   ```bash
   python ../module-conclusion-gate/scripts/check_gate.py modules/module-N.json
   ```

3. 仅当退出码为 `0` 且输出 `render_allowed=true` 时生成正式 Canvas。
4. 模块记录的 `approval.version`、当前 `version` 和输出元数据版本必须一致。
5. 条件不满足时返回阻断原因，不得生成没有水印的正式页面。

## 三种模式

### 正式模式（全局 Canvas）

- 输入只能是 `confirmed` 状态或已通过闸门的同版本数据。
- 输出 `output/maau-global-canvas.html`，完成后状态改为 `rendered`。
- 展示六大板块（Intent / User / Agent Team / Workflow / Context / Validation）的汇总视图。
- 页面显示版本、确认人/时间、证据覆盖、剩余 minor 缺口和最后更新时间。
- 保留证据引用和结论 ID，支持从结论下钻到证据摘要。
- 通过 `<a href="./module-N-canvas.html">` 链接下钻到各模块详情 Canvas。

### 模块详情模式（单模块产物）

- **每个模块确认后必须立即生成**，不是等全局汇总时才出。
- 输入只能是该模块 `confirmed` 状态或已通过闸门的同版本数据。
- 输出 `output/module-N-canvas.html`，完成后该模块状态改为 `rendered`。
- 展示该模块的**全部讨论产出**，不是全局 Canvas 的子板块：
  - M1：目标 / 价值 / 指标 / 证据 / 边界 / 项目分组 / 对齐状态
  - M2：用户 / 需求 / 痛点 / 流程 / 优先级 / 对齐状态
  - M3：HMW / 闭环目标 / 方案方向 / Workflow 草案 / 三类节点 / 验证维度 / 对齐状态
  - M4：Agent Team / 冻结工作流 / Context / 两轮原型 / 对齐状态
  - M5：三轮验证记录 / 能否执行 / 能否创造价值 / 信任风控 / 对齐状态
  - M6：最终方案 / 三维对比 / 演示结论 / 能力边界 / 资产 / 后续计划
- 页面显示版本、确认人/时间、证据覆盖、剩余 minor 缺口和最后更新时间。
- 保留证据引用和结论 ID，支持从结论下钻到证据摘要。
- 用户说"查看 Mx 产物"或"生成 Mx 模块画布"时，应该生成/展示这个页面。

### 草稿模式

- 仅在用户明确要求"用草稿辅助继续讨论"时生成。
- 页面顶部和打印版都必须显示"草稿 / 未确认 / 禁止用于管理层决策"。
- 空字段显示"未讨论"或"待确认"，不得自动补写。
- 草稿不得进入全局 Canvas、演示报告或领导汇报。

## 内容与数据契约

- 页面数据来自模块 JSON；不得把业务内容硬编码进组件逻辑。
- 全局页面只能使用映射文件规定的六个大模块及其小模块，不得增加其他方法板块。
- Workflow 必须呈现 AI 应用的完整流向，并分别展示自动化节点（Agent 执行）、人工操作/确认节点、人审 + Agent 执行节点；不能把普通业务流程直接当成最终 Workflow。
- 模块详情页展示该次日程的固定产出；全局页不塞入 HMW、原型记录、验证明细等过程材料，只提供下钻入口。
- 在 HTML 中嵌入 `<script type="application/json" id="canvas-data">` 保存同版本结构化数据，或引用同目录 JSON。
- 每个模块和结论使用稳定锚点，如 `module-M1`、`conclusion-M1-C01`。
- 必须保留事实、决策、假设、建议的视觉区分；推断不能伪装成已确认事实。
- 无外部网络依赖，双击 `file://` 即可打开；不要用 `fetch()` 读取本地文件，不要用 iframe 串联本地 HTML。
- 详细实现契约见 `references/render-contract.md`。

## 视觉外壳适配

1. 用户已经指定模板或风格时直接使用；没有指定时按用途选择，默认 `blue-professional-balanced`。
2. 可选视觉系统只有 **Blue Professional** 与 **Signal**，每个输出必须保持单一视觉系统。
3. 只继承模板的层级、色板、网格、间距和组件语法；不得复制模板示例内容。
4. 模板缺少当前规范的小模块时，在所选视觉系统中补齐，而不是删减正式 Canvas 的结构。
5. HTML 完成后必须做浏览器预览，检查桌面、窄屏和打印视图。
6. 正式交付前运行：

   ```powershell
   python skills/canvas-render/scripts/audit_canvas_html.py output/module-1-canvas.html
   ```

   只有 `audit_canvas_html.py` 返回退出码 `0`，并且人工预览没有裁切、溢出和交互故障时，才可交付。

## 全局 Canvas

全局汇总前：

1. M1-M6 全部是 `rendered`，并且指向各自最新确认版本。
2. 按结论闸门的全局一致性清单检查目标、用户、流程、能力、数据和验证是否闭合。
3. 若有冲突，回到对应模块升版、重新确认并重新渲染。
4. 全局页面通过普通 `<a href="./module-N-canvas.html#module-MN">` 下钻，不用 iframe。
5. 管理层摘要只呈现已确认结论；未知项与风险单独列出。
6. 标题统一使用“MVL Canvas”；页面明确“模拟环境概念验证原型，非生产级系统”。

## 视觉要求

采用专业商务风，蓝色或低饱和机构色为主，避免大面积高反差色块。信息优先级为：

1. 核心结论与价值判断；
2. 验证状态与关键指标；
3. 决策边界、风险和缺口；
4. 证据与追溯详情。

可以参考仓库 `html-templates/` 的布局和组件，但必须遵守事实源、闸门和离线打开约束。完整适配边界见 `references/html-slides-adaptation.md`。
