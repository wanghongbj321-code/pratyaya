# 两阶段正式渲染与产物身份（v3.6.0）

本契约适用于 MAAU transcript-direct 与 Phase 2 全局页；正式画布的文件身份规则也适用于模块详情及单画布实例。本文为运行时规则，不读取 internal 设计文件。

## 2. 两阶段编排与提交规则

### 2.1 通用流程

```text
确认当前来源版本 + Gate/用户授权 + 视觉模式
    ↓
第一阶段：canvas-render 从确认包生成无图候选 HTML
    ↓
L1（预期 noflow）+ L2 双视口 + 按条件触发 L3
    ↓ 全部通过
提交无图正式文件 → 交付 → 询问是否需要 Workflow 图
    ├─ 不需要：结束
    └─ 需要：重新核对当前版本与授权
          ↓
       确认包 → workflow 拓扑 → 文本布局图或临时 HTML 预览
          ↓ 用户确认布局
       官方布局器生成最终 SVG + 几何自检
          ↓ 自检通过
       canvas-render 从同版本确认包生成有图候选 HTML，嵌入 SVG
          ↓
       L1（预期 workflow）+ L2 双视口 + 按条件触发 L3
          ↓ 全部通过
       提交有图正式文件 → 交付两份链接
```

两阶段是独立正式渲染动作，各自从确认包取数、各自验收。布局请求、版本及预期输出身份是本次操作上下文，不增加 state 字段。视觉模式沿用用户本次已确认选择；用户改选时重新确认，宿主页面仍使用该模式的 token。

第一阶段的文本五字段、完成条件、治理与 caveat 必须完整。第二阶段不得只凭“第一阶段已 rendered”跳过版本或授权检查。

### 2.2 transcript-direct 状态

使用 `state.maau.{slug}`。首次成功由 `confirmed → rendered`；同版本后续成功为 `rendered → rendered`，`output_file` 更新为最近一次成功提交的正式路径。

| 情况 | 状态与产物处理 |
|---|---|
| 首次渲染失败，尚无本版本成功产物 | 保持 `confirmed`；不写失败文件到 `output_file` |
| 无图已成功，有图布局/审计失败或用户取消 | 保持 `rendered`、原 `output_file` 和成功文件 |
| 已有有图成功文件，同版本重试失败 | 保持原文件内容与指针；失败候选不替换正式文件 |
| 重试全部验收成功 | 可替换同一实例、同一形态、同一版本的旧成功文件，再更新指针；两形态互不覆盖 |
| 业务内容变化/确认包升版 | 走现有升版重置、Gate 和用户授权；旧版文件保留，不继承旧布局确认 |

不得为第二阶段失败执行 `rendered → confirmed`。同步修订 Skill、DEVELOPMENT 和 Agent 中笼统的“失败保持 confirmed”，将其限定为首次渲染；不修改引擎普通跃迁表。

### 2.3 候选文件与正式提交

- HTML 候选和预览写入本 topic 的临时工作区，不占用正式路径，不被索引引用。
- 审计候选时传入独立的**目标正式路径**，校验其文件身份，不能因候选随机文件名跳过版本/实例核对。
- 全部适用验收通过后，提交前再次核对来源版本、授权与预期目标身份未变。期间发生升版即废弃候选，重新进入当前版本流程。
- 正式文件在同一文件系统内通过完整文件替换发布；同目标已有文件须核对实例、形态、版本身份。身份不同或无法识别时阻断，保留原文件并报告冲突。
- 提交顺序为正式文件成功写入后再更新实例 state，最后重建依赖的索引。文件提交失败不动 state；state 更新失败不宣称本次提交完成，保留候选上下文供重新核对后重试。文件与 state 并非跨文件原子事务，不承诺进程中断时同时落盘。
- 对同一 topic 的提交顺序执行；并发写入必须检测来源/目标变化并阻断冲突，不在本轮新增复杂锁系统。

### 2.4 Phase 2 的独立规则

Phase 2 继续只读汇总六个最新 `rendered` 模块，执行跨模块一致性、caveat 和对齐检查；**不写六模块状态，不改模块 `output_file`，不虚构全局页实例 state**。

两阶段均冻结并复核六模块版本组合；任何模块升版都需重新核对汇总与布局确认。文件名见 §6.1，版本表达采用页面内六模块版本及渲染时间，不取最大版本、不引入全局计数器。页面原有元数据格式不借文件版本化之名改成新的字段类型。

有图失败保留已成功无图页及原有有图页；若两页对应不同模块版本组合，交付时明确各自来源，旧页不得被称为本次最新成果。通过对话交付两份链接，不为全局页增加“最近文件”state。下钻始终读取六模块各自的 `output_file`，不得推算文件名。

## 3. 两形态契约与审计预期

### 3.1 示例与完成条件

| 形态 | `skills/canvas-render/examples/mvl-canvas/` 示例 | 页面要求 |
|---|---|---|
| noflow | 新增 `maau-global-canvas-noflow.html` | 六板块完整；无 `#workflow-flow`、SVG 图形签名及 `canvas-data.workflow` |
| workflow | 维护 `maau-global-canvas.html` | 六板块及完整 §A1 流程图、拓扑一一对应 |

示例负责版面，render-contract 负责锚点和映射，visual-patterns 负责 token。完成条件的正文在两形态均保留；`#workflow-done` 仅在有完成条件时出现且全页唯一：无图版位于 Workflow 文本区域之后，有图版位于 `#workflow-flow` 内、SVG 外。无内容不生成空骨架。

### 3.2 形态判定

新正式 global 渲染的 L1、L2 命令均要求传入 `--workflow-variant noflow|workflow`，其值来自本次渲染请求。**不得通过待检 HTML 中是否有拓扑或 SVG 推断预期形态**，也不新增形态 state 字段。L1 与 L2 缺少预期参数时阻断新正式 global 交付。

L1 核对目标文件身份与请求一致，L2 使用同一请求参数。模块详情和其他画布不适用 global 形态参数，仍使用各自签名配置。

| 预期形态 | 拓扑 | Workflow DOM | 结果 |
|---|---|---|---|
| noflow | 无 | 无 | 检查其余完整性，通过才 PASS |
| noflow | 有或残留图形签名 | 任意 | FAIL |
| workflow | 有效 | 完整并与拓扑一致 | 继续执行全部 §A1 断言 |
| workflow | 缺失/非法 | 任意 | FAIL |
| workflow | 任意 | 缺失/残缺 | FAIL |

有图版同时缺失拓扑和 SVG 仍 FAIL。无图版不豁免六板块、文字内容、授权、caveat、离线、版本及治理面板检查。两形态均不得以删除失败结构换取降级通过。

## 4. 布局器 SVG 直出边界

### 4.1 输入与输出

新增 `--fragment <output.svg>`，输入仍是 §A1.5 workflow 拓扑。保留 `--svg` 原有目检预览语义，避免改变既有 CLI 调用的产物类型；新增模式才用于正式嵌入。

最终片段是单个 `<svg class="bpmn-flow" ...>`，只包含 SVG 命名空间内的元素：轨道、节点、事件、网关、序号和 actor 徽章、输入已有的标签/note、正交边、回流边、箭头 marker。不得从拓扑补写业务事实。文本与属性值必须正确转义，长中文标签及特殊字符需纳入验收。

**不输出** HTML `#workflow-flow` 外容器、标题、横滚包装、HTML 图例和 `#workflow-done`。这些由 canvas-render 按契约生成，完成条件直接来自确认包，不从 End 标签推断。渲染回合可以装配外层 HTML，但不得重写 SVG 内部几何或业务标签。

片段不携带页面级 CSS；结构 class 与几何属性由布局器提供，视觉 token 由宿主内联 CSS 提供。SVG 内部结构符合 §A1 不等于完整页面已验收；必须嵌入宿主后执行 L1/L2 及所需 L3。

### 4.2 几何自检与兼容

L0 几何、L1 `layout_override`、L2 fork 与溯源能力沿用；`layout_override` 不进业务拓扑。布局器 VERSION 0.2.0，`--version`、`layout_trace`、fork 文档同步。

CLI 退出码沿用 0/1/2：0 为几何自检通过；1 为几何自检失败；2 为输入或参数非法。失败不得产出可误用的本次最终 SVG；每次使用独立临时目标，调用方不得在失败后读取旧文件当本次结果。

几何自检应继续覆盖节点不重叠、边正交、不穿节点、端点、回流 gutter 和边全集；新增徽章/标签后还需检查实际文本布局。几何 PASS 不替代宿主 CSS 下的 L2/L3。

### 4.3 AGENTS.md 规则 3 边界

官方 `skills/canvas-render/scripts/workflow_layout/` 可执行“几何展开 + §A1 SVG 内部结构生成”，产出可嵌入 `#workflow-flow` 的最终 `<svg>`；**仍不承担业务内容撰写或整页 HTML 渲染**。整页渲染统一通过 canvas-render，禁止新增独立内容渲染脚本。

此边界与 Skill/契约自 v3.6.0 同步生效。

## 5. 布局方案确认与预览

1. 从当前已授权确认包生成派生拓扑，优先展示文本轨道图，表达轨道、主链、跨轨和回流。
2. 需要 HTML 预览时，**允许确认前调用布局器**生成临时 SVG，由 canvas-render 构成临时预览；预览明确标注用途，不提交正式路径、不改 state。
3. 用户确认布局后才允许正式提交。输入拓扑、布局参数、版本和宿主模式未变时可复用已通过自检的预览 SVG，但最终 HTML 仍须完整验收；任何影响布局的修改均重新呈现确认。
4. 轨道分组、间距、流向展示可调整；执行责任、业务分支条件或确认事实的改变必须回源包升版与 Gate。不得把“谁执行/谁确认”的业务变化一概视为展示层调整。
5. 布局确认仅绑定当前对话内的版本、拓扑及参数，不新增持久化档案。上下文缺失时重新确认，不能推定已授权。

## 6. 正式输出命名、身份与兼容

### 6.1 新命名

使用 `--` 作为机器后缀分隔符。合法 kebab-case slug 不含连续连字符，因此后缀不会被误解析为 slug。版本依然是确认包版本，**不是渲染次数**。

| 产物 | v3.6.0 新正式路径 |
|---|---|
| M1–M6 模块详情 | `output/module-{n}-canvas--v{N}.html` |
| MAAU transcript-direct 无图 | `output/maau-global-canvas-{slug}--noflow-v{N}.html` |
| MAAU transcript-direct 有图 | `output/maau-global-canvas-{slug}--workflow-v{N}.html` |
| GC/HMW/Persona/Journey/V2C VAC/5W 实例 | `output/{canvas}-canvas-{slug}--v{N}.html` |
| Phase 2 无图聚合页 | `output/maau-global-canvas.html` |
| Phase 2 有图聚合页 | `output/maau-global-canvas--workflow.html` |
| 各画布索引页 | `output/{canvas}-canvas.html`，不变 |
| 最终报告 | `output/mvl-final-report.html`，不变 |

其中 `{canvas}` 沿用 `gc/hmw/persona/journey/v2c-vac/5w` 现行文件前缀，不直接使用 state 键。

例如 `sales` 有图版为 `maau-global-canvas-sales--workflow-v1.html`；`sales-workflow` 无图版为 `maau-global-canvas-sales-workflow--noflow-v1.html`，不再碰撞。其他画布也使用 `--v{N}`，防止新版本名与历史合法 slug（如 `sales-v1`）的无版本文件碰撞。

两种形态及不同确认包版本始终并存。**同版本、同形态成功重渲染可以替换同身份文件**，不引入渲染修订计数器；失败替换保护见 §2.3。

### 6.2 身份校验

新增正式目标路径校验，责任位于现有审计层。新正式审计使用 `--artifact-policy current`（默认），候选文件使用 `--target-output <正式目标路径>`；已位于正式路径时可直接用输入路径。

- 对绑定确认包的页面，核对解析出的类型/模块、slug、版本以及适用的形态，与请求、source、state、body 和 canvas-data 中适用的身份字段一致。
- 输出文件名版本校验是**新增能力**，不能把现行 body/JSON/source/state 校验视作已经覆盖。
- 新正式命名不得因缺少版本或形态而自动降级为历史兼容。
- Phase 2、索引和报告只按明确的产物种类与固定路径豁免文件版本；不能凭“文件名没版本”自动豁免，也不能用聚合页豁免绕过实例授权。
- L1 参数名称及说明同步进入正式审计命令；L2 至少接收相同 page type 和预期形态，禁止两层各自猜测。

### 6.3 历史文件与 Phase 2 豁免

采用原 F-a：Phase 2 无独立版本号，保持聚合页语义；不采用最大模块版本，也不新增 state 计数器。

历史文件不追溯改名。只读历史复查显式使用 `--artifact-policy legacy`，允许历史无版本文件名，但仍执行原适用的结构、来源和授权检查；旧 global 页按原有图契约检查。历史模式不能用于 v3.6.0 新渲染提交，pipeline 固定使用 current。

原 Phase 2 `maau-global-canvas.html` 是固定聚合入口，同身份新无图聚合页验收成功后可替换它；这属于聚合视图刷新，不承诺保存每次聚合快照。若用户需要保留旧快照，另行指定归档任务，本轮不自动改名历史文件。

### 6.4 链接与 state

实例 `output_file` 指向最近一次成功提交的正式文件；不新增清单字段。索引生成、全局下钻及相关审计必须使用实际 `output_file`，并验证目标存在和身份一致，不假设旧固定路径。保留旧文件不改变当前链接指向。

Phase 2 两份文件的交付由 §2.4 规定，不写入任一模块 `output_file`。迁移工具仍表达历史输出，不改写成未实际生成的新版本路径。


版本化文件工具：`skills._engine.paths.html_file(..., version=N)`；MAAU 的 output_prefix 为 `maau-global` 且需 workflow_variant。files 的存在性/过期 sidecar 工具传入同样的 version/variant；升版时两形态逐份标记。省略 version 只兼容历史路径；当前索引和下钻优先读实际 output_file。
