# Canvas 视觉模式规范

本目录是 `canvas-render` 的视觉规格来源，所有画布类型（MVL、黄金圈等）均可复用。每个模式文件描述一种可供 Agent 实现为离线 HTML Canvas 的设计系统；模式文件不是业务事实源，也不是可直接交付给用户的 Canvas。

正式业务内容仍只能来自已确认且通过 Gate 的 `modules/Mx-v{N}.md`。HTML 的 DOM、锚点、共享结构、离线和版本约束以 `../references/render-contract.md` 为准。

## 文件发现

候选模式只通过以下规则发现：

```text
skills/canvas-render/visual-patterns/[0-9][0-9]-*.md
```

- `README.md` 不是候选。
- 当前基线必须恰好发现 10 个候选。
- 不读取仓库其他目录中的同名文件。
- 不使用集中 JSON 登记册。

## 文件命名

每个候选文件必须使用：

```text
NN-{id}.md
```

- `NN`：两位稳定序号，当前为 `01`–`10`。
- `{id}`：与 frontmatter 的 `id` 完全相同。
- 去掉 `NN-` 和 `.md` 后的文件名必须等于 `id`。
- 序号和 `id` 都必须在目录内唯一。
- 已发布模式的序号不得因新增、删除或排序而重排。

示例：

```text
01-blue-professional-balanced.md
```

其 frontmatter 必须包含：

```yaml
id: blue-professional-balanced
```

## Frontmatter

每个模式必须包含且只能以以下 7 个字段作为选择元数据：

```yaml
---
id: blue-professional-balanced
zh_name: 蓝色专业·均衡
visual_system: Blue Professional
layout: balanced
formality: medium-high
density: medium
best_for: 内部方案、管理层均衡总览
---
```

字段定义：

| 字段 | 含义 | 规则 |
|---|---|---|
| `id` | 模式稳定标识 | kebab-case；与文件名 `{id}` 一致 |
| `zh_name` | 中文展示名 | 简洁（4-8 字），用于模式选择时向用户展示；避免与 `id` 或 `visual_system` 重复 |
| `visual_system` | 视觉系统名称 | 一个输出只能使用一个视觉系统 |
| `layout` | 主要版式 | 当前使用 `balanced` 或 `flow` |
| `formality` | 正式度 | 当前使用 `medium-high` 或 `high` |
| `density` | 信息密度 | 当前使用 `medium`、`medium-high` 或 `high` |
| `best_for` | 推荐场景 | 简短说明适配的阅读者与任务 |

## 正文结构

每个模式正文固定使用以下 6 节，顺序不得调整：

1. `## 色板 token`
2. `## 字体`
3. `## 网格`
4. `## 组件库`
5. `## 适用场景`
6. `## 反例`

### 色板 token

列出实现视觉系统所需的核心颜色，包括：

- 页面背景
- Canvas 背景
- 区块背景
- 主色和深色
- 柔和强调色
- 主文字和辅助文字
- 边框
- 状态色

优先给出精确 hex 和建议 CSS 变量名。不得只写“蓝色”“低饱和灰”等模糊描述。

### 字体

至少说明：

- 系统字体栈
- Hero、Canvas 标题、section 标题、正文、表格的字号
- 主要字重
- 行高和字距

不得要求外部字体网络资源。

### 网格

至少说明：

- 页面最大宽度与外边距
- Canvas 内边距
- 主网格和次级网格
- gap
- 桌面、平板和窄屏断点
- flow 或 matrix 等专属布局

### 组件库

至少说明：

- Hero / Canvas 标题带
- 摘要
- section / card
- 表格
- 工作流节点
- 页脚
- 质量面板
- 本地批注
- 打印行为

模式只规定视觉语法，不重复 `render-contract.md` 的业务 DOM 映射。

### 适用场景

说明该模式适合的读者、任务和内容密度。推荐时应把这里的描述与当前 Canvas 内容特征一起展示给用户。

### 反例

明确：

- 不应混搭的视觉系统
- 不适合的内容密度或任务
- 不得复制的示例内容
- 会破坏该视觉系统的实现方式

## Agent 读取流程

1. 扫描候选路径。
2. 读取全部候选的 frontmatter。
3. 校验目录数量、序号、ID、文件名和 7 个字段。
4. 基于 `visual_system / layout / formality / density / best_for` 推荐 1–2 个候选。
5. 用户选定后，主 Agent 向 `canvas-render` 传递完整仓库相对路径。
6. `canvas-render` 读取该文件的 6 节正文，并按其中 token 实现 HTML。
7. HTML 的业务内容、DOM 和状态仍分别服从确认包与 `render-contract.md`。

不得把 `id` 拼成猜测路径。例如用户选择 `blue-professional-balanced` 时，必须传递：

```text
skills/canvas-render/visual-patterns/01-blue-professional-balanced.md
```

不得猜测为：

```text
visual-patterns/blue-professional-balanced.md
```

## 阻断条件

出现以下任一情况必须阻断推荐或渲染，并输出具体错误：

- 目录不存在
- 候选数量不是当前基线要求的 10 个
- frontmatter 缺字段
- `id` 或序号重复
- 文件名 `{id}` 与 frontmatter `id` 不一致
- 用户选定的完整路径不存在
- 路径不在本目录内
- 模式正文缺少固定 6 节

不得静默回退到另一模式，不得重新读取旧 HTML 模板。

## 写作原则

- **Agent 主读源**：用结构化、可直接实现的语言写作。
- **Token 优先**：优先记录稳定设计 token 和布局行为，不追逐无影响的微调。
- **差异明确**：保留模式专属字体、组件和布局，不为统一格式抹平风格。
- **反例明确**：直接说明不能做什么。
- **无业务示例**：不得写入真实项目、品牌、组织、指标或结论。
- **单一视觉系统**：一个模式只描述一种 `visual_system`。
- **离线优先**：只使用内联 CSS/JS、系统字体和本地图标语法。

## 新增模式

新增视觉模式前必须先由用户确认设计范围和 SemVer 影响，然后：

1. 分配新的稳定两位序号。
2. 创建满足 `NN-{id}.md` 的文件。
3. 填写 7 个 frontmatter 字段和 6 节正文。
4. 校验发现、ID 和文件名规则。
5. 使用统一代表数据完成桌面、窄屏和打印验证。
6. 更新本目录的当前基线数量及相关现行文档。

参考实现：`01-blue-professional-balanced.md`。

## 默认模式

`10-black-gray-professional`（zh_name: 黑灰专业·打印版）是 pratyaya 的**默认配色方案**。在模式选择阶段，若无明确的画布类型或内容特征指向其他模式，Agent 应优先推荐此模式。使用场景包括：

- 需正式打印的管理层报告
- 学术场景输出
- 黑白设备展示
- 不确定用户偏好的默认回退

默认模式同时也是所有 10 模式的 [Pan-Mode Invariants](#pan-mode-invariants-跨模式通用规则) 锚定基准。

## Pan-Mode Invariants（跨模式通用规则）

> 自 v2.3.5 起，所有 10 个视觉模式共享以下 13 条不变量（跨模式通用规则）。任何新模式或现有模式的实现层落地都应以此为最低约定。每条不变量下注明**例外清单**（当前仅 §10 默认模式与 §03/04 Signal 例外，其他 7 模式无例外）。

### 13 条不变量

1. **Hero 永远白纸底**（无大面积主色 / 渐变作为 hero 背景）。例外：03 / 04 Signal 使用灰棕纸张主题底（Signal 视觉标识）；05 / 09 使用品牌色 1px 极细底线（视觉差异保留）。
2. **Hero 标题色 = 本模式主色 token**（不放品牌色块作背景；不放 `--brand-pale`）。
3. **Hero eyebrow = 10px / 700 / `.2em` 字距 / 主色 token / 大写**（统一字号字距；不与 h1 同色块）。
4. **Hero 规则线粗细统一**：默认 4px 主色实线。例外：05 McKinsey 6px（咨询结论的厚重感）、09 Roland Berger 1px（极致克制）。
5. **行动摘要位置 = hero 与 canvas 之间**（嵌 header 内合理，保留 DOM 一级模块顺序 canvas-header → ... 不变）。
6. **行动摘要配色公式**：`<本模式 pale 色>` 背景 + `5px <本模式主色>` 左边框 + 黑文字 + 主色实底白字 action tag（位于 hero 与第一个 section 之间）。
7. **Section 标题标识统一公式**：`<主色 token> 文字 + 3px 主色左线 + 大写 + 透明背景`（不整片染色；不依赖位置）。
8. **Section / Card 卡背景永不变色**：永远白纸底（或本模式专属纸张底如 Signal 灰棕），仅头部 3px 左线作信号；不使用品牌色作为 section 背景填充。
9. **表格三段式统一**：`pale 色表头 + 主色文字 + 2px 主色底线`；正文保持黑色 / 主文字色，避免整表染色。
10. **页脚主色实底白字**：唯一允许"整片染主色"的位置。footer 视觉权重控制 ≤ 5–7% 页面面积（按模式语气）；页脚内部 `<footer-tag>` 用深色 token（`--dark`）提供二级对比。
11. **禁用视觉滥用**：禁用 `box-shadow`、禁用复杂 `linear-gradient`（品牌视觉标识除外，如 06 Accenture top bar）、禁用 "圆润胶囊" 按钮（Bain Red §反例 第 2 条）。
12. **质量判定仅靠字重 + 下划线 + 灰度**：不引入彩色 PASS 绿 / FAIL 红（10 模式统一）；失败判定用 `<del> 或 underline wavy <主色>`。
13. **SVG / emoji 不作信号**：状态图标、判定、风险等级只通过字重 / 下划线 / 灰度区分。

### 例外清单（当前 10 模式中已批准的）

| 模式 | 例外维度 | 例外值 | 理由 |
|---|---|---|---|
| 03 Signal Balanced / 04 Signal Flow | Hero 底色 | 灰棕纸张 `#d9d6cf` | Signal 视觉标识（机构档案感）；非"主色整片染色" |
| 05 McKinsey Blue Conclusion | Hero 规则线粗细 | 6px | 咨询结论的厚重感 |
| 09 Roland Berger Dark Blue Gray | Hero 规则线粗细 | 1px | 极致克制（视觉哲学即克制） |
| 10 Black Gray Professional | 全维度 | 全部不变量 | 锚定基准模式，本身即正确答案 |

### 反例（违反任一即视为该模式实现不正确）

- 在 hero 整片铺主色 / 渐变 / 大面积伪深色——视觉 token 反用为容器底色
- section / card 卡背景染品牌色——触发 §反例 第 1 条
- 表格 / 状态使用彩色 PASS 绿 / FAIL 红——违反 Invariant #12
- 模式规格 §Hero 段没有约束"#cc0000 等主色整片染色"——视为 spec 不完整
- 示例库 `<body>` 无 `data-visual-mode` 属性——视为示例库元数据缺失

## 新增 Pan-Mode Invariants 段

新增 Pan-Mode Invariants 段之前，必须由用户确认设计范围、是否影响既有 9 模式规格、再按以下流程：

1. 在 `visual-patterns/README.md` 维护这 13 条不变量。
2. 对每个模式的 §组件库 · Hero 段补一行 `Pan-Mode Invariants (v2.3.5+): ...` 锚定本模式适用例外的版本时间戳。
3. 不引入新模式时不增不变量；变更既有不变量需用户拍板（变更 → PATCH 升级）。
4. 验证：跑 §7 静态审计 + 浏览器视觉验证。
