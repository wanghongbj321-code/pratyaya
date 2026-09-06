# 两阶段正式渲染与产物身份（v3.6.0 引入；v3.6.1 起 Workflow SVG 由 LLM 直出）

本契约适用于 MAAU transcript-direct 与 Phase 2 全局页；正式画布的文件身份规则也适用于模块详情及单画布实例。本文为运行时规则，不读取 internal 设计文件。

## 2. 两阶段编排与提交规则

### 2.1 通用流程

```text
确认当前来源版本 + Gate/用户授权 + 视觉模式
    ↓
第一阶段：canvas-render 从确认包生成无图候选 HTML
    ↓
L1（预期 noflow，必跑）+ L2/L3（仅用户明确要求时运行）
    ↓ 通过
提交无图正式文件 → 交付（附视觉反馈提示话术，见 §3.4）→ 询问是否需要 Workflow 图
    ├─ 不需要：结束
    └─ 需要：重新核对当前版本与授权
          ↓
       LLM 从确认包 Workflow section 派生 §A1.5 workflow 拓扑
          ↓
       文本轨道图 / 临时 HTML 预览（可选，供用户确认布局）
          ↓ 用户确认布局
       LLM 按 §A1 直接静态生成内联 SVG（轨道带/正交 M/H/V/dashed gutter）
          ↓
       canvas-render 从同版本确认包生成有图候选 HTML，装配 SVG
          ↓
       L1（预期 workflow，必跑）+ L2/L3（仅用户明确要求时运行）
          ↓ 通过
       提交有图正式文件 → 交付两份链接（附视觉反馈提示话术，见 §3.4）
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

新正式 global 渲染的 L1 命令必须传入 `--workflow-variant noflow|workflow`，其值来自本次渲染请求。**不得通过待检 HTML 中是否有拓扑或 SVG 推断预期形态**，也不新增形态 state 字段。L1 缺少预期参数时阻断新正式 global 交付；L2/L3 仅用户明确要求时运行，运行时必须与 L1 使用同一预期形态参数。

L1 核对目标文件身份与请求一致；L2/L3（按用户要求运行时）使用同一请求参数。模块详情和其他画布不适用 global 形态参数，仍使用各自签名配置。

| 预期形态 | 拓扑 | Workflow DOM | 结果 |
|---|---|---|---|
| noflow | 无 | 无 | 检查其余完整性，通过才 PASS |
| noflow | 有或残留图形签名 | 任意 | FAIL |
| workflow | 有效 | 完整并与拓扑一致 | 继续执行全部 §A1 断言 |
| workflow | 缺失/非法 | 任意 | FAIL |
| workflow | 任意 | 缺失/残缺 | FAIL |

有图版同时缺失拓扑和 SVG 仍 FAIL。无图版不豁免六板块、文字内容、授权、caveat、离线、版本及治理面板检查。两形态均不得以删除失败结构换取降级通过。

### 3.3 L1/L2 命令模板（一次传对全部参数）

新正式 global 渲染按形态取用下表命令，禁止分两次试跑补参数（L1 必跑；L2/L3 仅用户明确要求时运行，运行时同用本模板一次传齐）：

```bash
# L1 静态审计（MAAU transcript-direct；候选阶段加 --target-output <正式目标路径>）
python3 skills/canvas-render/scripts/audit_canvas_html.py <候选或正式HTML> \
  --source modules/MAAU-{slug}-v{N}.md --state state.json \
  --type mvl --page-type global --instance {slug} \
  --generation-path transcript-direct --workflow-variant noflow|workflow

# L2 DOM 度量断言（仅用户明确要求时运行；与 L1 同一预期形态，一次传齐）
node skills/canvas-render/scripts/canvas-smoke.mjs <候选或正式HTML> \
  --type mvl --page-type global --workflow-variant noflow|workflow
```

参数要点：`--workflow-variant` 各层必须同值且与请求形态一致；模块详情页用 `--page-type module-detail`（无需 variant）；其他画布不传形态参数。noflow 形态 L2（如运行）会自动收紧为"无流程图结构 + 六板块存在"签名，无需额外参数。

### 3.4 分级验收语义（v3.6.2 起：L1 必跑，L2/L3 仅用户明确要求）

验收分级调整为：

| 层级 | 默认 | 内容 | 触发条件 |
|---|---|---|---|
| L1 静态审计 | **必跑** | 治理完整性（授权/版本/六板块/caveat/离线）+ **结构签名静态断言**（v3.6.2 新增：workflow 形态的 `quality-panel` 存在、`bpmn-legend` 恰好 1 个、`bpmn-flow` SVG 存在） | 每次正式渲染，无条件 |
| L2 DOM 度量断言 | 可选 | 双视口溢出/裁切/折叠断言（浏览器级） | **仅用户明确要求**（如严格验收、多端/移动端交付、打印适配检查） |
| L3 截图目检 | 可选 | AI 目检布局（压线/重叠） | 同 L2：**仅用户明确要求**；不得作为 L1 失败的兜底执行路径 |

决策依据（2026-09-06 归因实验 + 用户拍板）：L2 的 23s 中约 90% 是 `require("puppeteer-core")` 模块加载税（macOS 实测 20–22s，系统 Node 亦 11s，疑似 Gatekeeper 对 node_modules 大量小文件的每次扫描），真实断言仅 0.03s；而视觉质量的最终裁决者是用户（其工作流本身即精确视觉反馈迭代），移动端/打印检查仅在用户明确要求（如多端交付）时才有价值。结构签名的价值不放弃——下沉为 L1 静态断言（零依赖、<0.5s）。**未经用户明确要求，L2/L3 不允许执行**：执行者不得因 L1 FAIL、CSS/模板结构变更、无示例参照或自身观感存疑自行触发（L1 FAIL 时修订同版本 HTML 后重跑 L1）。

**交付话术模板（正式交付时固定附一句）**：

> 画布视觉如需调整（间距、颜色、布局、字号等），直接告诉我，我马上调；如需移动端/打印溢出等严格验收，可要求我跑一次 L2/L3。

L2 脚本与降级路径保留不动；`audit_l2` / `audit_l3` trace stage 枚举保留（§7），用户要求执行时照常落盘。

## 4. Workflow SVG 由 LLM 按 §A1 生成（v3.6.1 起）

### 4.1 生成边界

workflow 形态的 SVG 由渲染回合的 LLM 从同版本确认包按 §A1.1–A1.5 直接静态生成并嵌入宿主 `#workflow-flow`。最终 `<svg class="bpmn-flow" ...>` 含轨道、节点、事件、网关、序号与 actor 徽章、已有标签/note、正交边、回流边与箭头 marker；文本与属性值必须正确转义，长中文标签及特殊字符需纳入验收。**不得从拓扑补写业务事实、不新增分析**；LLM 只按确认包已有内容派生拓扑与几何。

**不输出** HTML `#workflow-flow` 外容器、标题、横滚包装、HTML 图例和 `#workflow-done`。这些由 canvas-render 按契约生成，完成条件直接来自确认包，不从 End 标签推断。渲染回合可以装配外层 HTML，但不得重写 SVG 内部几何或业务标签。

SVG 不携带页面级 CSS；结构 class 复用母版（`bpmn-flow` / `bpmn-track` / `bpmn-node` / `bpmn-sequence` 等），视觉 token 由宿主 CSS 单点提供。SVG 内部结构符合 §A1 不等于完整页面已验收；必须嵌入宿主后执行 L1（及用户明确要求的 L2/L3）验收。

### 4.2 几何与质量把关

无自动几何自检（v3.5.0–v3.6.0 布局器已回退删除）：几何与视觉靠 L1 结构断言（正交 `M/H/V` 禁 `C/Q/S/A`、节点/track/actor/dashed 一致性、结构签名静态断言）+ 用户视觉反馈兜底；浏览器级 L2 溢出断言与 L3 截图目检仅用户明确要求时运行（默认不执行，见 §3.4）。LLM 生成的 SVG 须复用母版 class 体系与已确认视觉 token，控制坐标漂移。

### 4.3 AGENTS.md 规则 3 边界

AGENTS.md 规则 3 已恢复 v3.4.1 原文：禁止新增或使用渲染脚本，渲染统一通过 canvas-render Skill；无官方几何工具，workflow SVG 由 LLM 经 Skill 静态生成。若未来确需自动化渲染入口，先按规则 2 提出设计变更，经用户确认后再实现。

## 5. 布局确认与预览

1. 从当前已授权确认包生成派生拓扑，优先展示文本轨道图，表达轨道、主链、跨轨和回流。
2. 需要 HTML 预览时，由 LLM 生成候选 SVG 并经 canvas-render 构成临时预览；预览明确标注用途，不提交正式路径、不改 state。
3. 用户确认布局后才允许正式提交。输入拓扑、视觉模式、版本和宿主模式未变时可复用已通过验收的 SVG，但最终 HTML 仍须完整验收；任何影响布局的修改均重新呈现确认。
4. 轨道分组、间距、流向展示可调整；执行责任、业务分支条件或确认事实的改变必须回源包升版与 Gate。不得把“谁执行/谁确认”的业务变化一概视为展示层调整。
5. 布局确认仅绑定当前对话内的版本、拓扑及参数，不新增持久化档案。上下文缺失时重新确认，不能推定已授权。

## 6. 正式输出命名、身份与兼容

### 6.1 新命名

使用 `--` 作为机器后缀分隔符。合法 kebab-case slug 不含连续连字符，因此后缀不会被误解析为 slug。版本依然是确认包版本，**不是渲染次数**。

| 产物 | 两阶段正式路径（v3.6.0 引入；v3.6.1 起 Workflow SVG 由 LLM 直出） |
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

历史文件不追溯改名。只读历史复查显式使用 `--artifact-policy legacy`，允许历史无版本文件名，但仍执行原适用的结构、来源和授权检查；旧 global 页按原有图契约检查。历史模式不能用于当前两阶段（v3.6.0+，含 v3.6.1）新渲染提交，pipeline 固定使用 current。

原 Phase 2 `maau-global-canvas.html` 是固定聚合入口，同身份新无图聚合页验收成功后可替换它；这属于聚合视图刷新，不承诺保存每次聚合快照。若用户需要保留旧快照，另行指定归档任务，本轮不自动改名历史文件。

### 6.4 链接与 state

实例 `output_file` 指向最近一次成功提交的正式文件；不新增清单字段。索引生成、全局下钻及相关审计必须使用实际 `output_file`，并验证目标存在和身份一致，不假设旧固定路径。保留旧文件不改变当前链接指向。

Phase 2 两份文件的交付由 §2.4 规定，不写入任一模块 `output_file`。迁移工具仍表达历史输出，不改写成未实际生成的新版本路径。


版本化文件工具：`skills._engine.paths.html_file(..., version=N)`；MAAU 的 output_prefix 为 `maau-global` 且需 workflow_variant。files 的存在性/过期 sidecar 工具传入同样的 version/variant；升版时两形态逐份标记。省略 version 只兼容历史路径；当前索引和下钻优先读实际 output_file。

## 7. 渲染计时插桩（render-trace.jsonl）

为支持渲染性能复盘（各阶段耗时归因），验收脚本与装配脚本按以下约定写 trace。trace 是**派生性能数据**：不参与审计校验、不写 state、不进索引，写入失败静默忽略，绝不让插桩反噬渲染主流程。

- **文件位置**：被检 HTML 同目录（正式产物即 `output/.render-trace.jsonl`；候选阶段在被检候选文件所在临时目录）。
- **记录 schema**（JSONL，每行一条）：`{"stage", "tool", "html", "exit_code", "status", "started_at", "ended_at", "duration_ms", ...meta}`；时间 ISO 8601。
- **stage 枚举与写入者**：

| stage | 写入者 | 说明 |
|---|---|---|
| `host_read` | 装配脚本（LLM 渲染回合编写） | 读取宿主/确认包/示例片段 |
| `svg_generate` | 装配脚本（LLM 渲染回合编写） | §A1 SVG 生成（LLM 侧仅记生成起止，推理耗时以轮次自报近似） |
| `assembly` | 装配脚本 | 候选 HTML 写盘 |
| `audit_l1` | `audit_canvas_html.py`（自动） | L1 静态审计 |
| `audit_l2` | `canvas-smoke.mjs`（自动） | L2 DOM 断言 |
| `audit_l3` | 截图脚本（按需） | L3 目检 |
| `commit` | 装配脚本/提交步骤 | 正式文件替换 + state 更新 |

- **装配脚本最小插桩**：渲染回合编写的装配脚本至少写 `assembly` 与 `commit` 两条（各 3 行代码量级），`host_read` / `svg_generate` 可选。
- LLM 推理轮次耗时不可自动测量：由渲染路径自报的"工具往返量级"近似补充，不写入 trace。
