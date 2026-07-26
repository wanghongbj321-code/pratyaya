# MVL Workshop Facilitator

用于三天 AI 原生 MVL（Minimum Verifiable Loop）工作坊的单专家插件。一个“闭环助教”统一调度三个 Skill，把逐字稿变成可追溯、可确认、可迭代的模块资产，并在质量闸门通过后生成 HTML Canvas。

## 在 WorkBuddy 中安装

### 安装前准备

先让 WorkBuddy 能访问这个完整的专家包。可以提供以下任意一种来源：

- 本机文件夹路径；
- 已下载到本机的 ZIP 压缩包路径；
- WorkBuddy 可以访问的 Git 仓库地址。

专家包根目录必须直接包含：

```text
.codebuddy-plugin/plugin.json
agents/
skills/
schemas/
html-templates/
```

不要只发送某一个 `SKILL.md`。这个项目是“一个专家 + 三个 Skill”的完整插件包，缺少其中任何一部分都会造成安装不完整。

### 给 WorkBuddy 的一键安装提示词

把下面整段文字复制给 WorkBuddy，并把【专家包来源】替换为实际路径、ZIP 路径或仓库地址：

```text
我要安装一个 WorkBuddy 专家，请你直接完成安装，不要只告诉我手动安装步骤。

专家显示名称：AEI原生MVL工作坊助教
专家技术名称：mvl-workshop-facilitator
专家包来源：【在这里填写本地文件夹、ZIP 文件或 Git 仓库地址】

请执行：
1. 读取专家包根目录的 .codebuddy-plugin/plugin.json。
2. 使用 WorkBuddy 的本地专家安装机制，安装整个 mvl-workshop-facilitator 专家包。
3. 注册主专家 agents/mvl-workshop-facilitator.md。
4. 确认以下三个 Skill 已随专家一起安装：
   - mvl-distill
   - module-conclusion-gate
   - canvas-render
5. 确认 html-templates/index.json 及索引中的四个 HTML 模板已随专家包安装。
6. 验证安装后的插件名称为 mvl-workshop-facilitator，版本不低于 1.4.0。
7. 安装完成后向我报告：安装是否成功、实际安装位置、插件版本、已注册的专家和 Skill、模板资产是否齐全。
8. 最后明确提醒我完全退出并重新启动 WorkBuddy，使新专家生效。

如果你无法访问专家包来源，或任何文件安装失败，请明确告诉我阻塞原因，不要把“已读取文件”当成“安装成功”。
```

例如，这个项目位于本机默认开发目录时，可以填写：

```text
D:\AI\AI原生MVL工作坊\mvl-workshop-facilitator
```

收到这段提示词后，WorkBuddy 应直接执行安装。用户不需要手动拆分或分别安装三个 Skill。

## 安装完成后必须重启

安装成功后，WorkBuddy 通常会提醒重新启动。请注意：

1. 保存当前对话或工作内容；
2. 完全退出 WorkBuddy 桌面应用；
3. 重新打开 WorkBuddy；
4. 再按下一节检查专家是否出现。

只刷新当前对话或关闭聊天窗口不一定会重新加载专家配置。更新了这个专家包后，也应重新安装或覆盖安装，并再次重启。

## 如何找到并验证专家

重启 WorkBuddy 后，可以用以下两种方式找到“闭环助教”。

### 方式一：从“我的专家”进入

1. 打开 WorkBuddy 的“专家技能链接”菜单；
2. 选择“专家”；
3. 进入“我的专家”列表；
4. 找到“闭环助教”；
5. 点击进入并开始对话。

### 方式二：用“+”号召唤

1. 在 WorkBuddy 对话界面点击“+”号；
2. 选择添加或召唤“专家”；
3. 从“我的专家”中选择“闭环助教”；
4. 确认后，该专家会进入当前对话。

### 验证是否安装正确

召唤“闭环助教”后发送：

```text
请报告你的专家技术名称、版本、当前可调用的 Skill，以及模块完整状态机。先不要创建任何项目文件。
```

正确安装时，回答中应至少出现：

- 专家技术名称：`mvl-workshop-facilitator`
- 插件版本：`1.4.0` 或更高
- 三个 Skill：`mvl-distill`、`module-conclusion-gate`、`canvas-render`
- 状态机：`not_started → ingested → extracted → draft → gaps_open ↔ review_ready → confirmed → rendered`

如果“我的专家”中没有出现“闭环助教”：

1. 确认已经完全退出并重启 WorkBuddy；
2. 确认安装的是专家包根目录，而不是多套了一层同名文件夹；
3. 确认根目录存在 `.codebuddy-plugin/plugin.json`；
4. 把上面的一键安装提示词重新发给 WorkBuddy，并要求它报告实际安装位置和错误信息；
5. 若安装的是旧版本，要求覆盖安装 1.4.0 或更高版本后再次重启。

## 核心架构

```text
闭环助教
├── mvl-distill              转写 → 证据、结论候选、缺口、推断
├── module-conclusion-gate   核心价值审核 → 人工版本确认 → 放行/阻断
└── canvas-render            已确认 JSON → 视觉适配 → 模块/全局 HTML → 离线审计
```

关键原则：HTML 是展示层，不是结论生成器。

`canvas-render` 已内置从 `html-slides` 收敛出的 Canvas 能力：从四个批准模板中选择视觉外壳、保持单一设计系统、补齐规范小模块、完成桌面/窄屏/打印预览，并对单文件离线 HTML 做自动审计。它不会引入幻灯片的分页和演示流程，也不会复制模板中的示例业务内容。

Canvas 的 Workflow 是本次 MVL 要验证的 AI 应用工作流。M3 形成草案，M4 结合两轮原型完成冻结；正式结果必须分别呈现自动化节点（Agent 执行）、人工操作/确认节点、人审 + Agent 执行节点，以及触发、完成、流向和关键规则。普通业务流程不能直接代替这项产出。

## 模块生命周期

```text
not_started → ingested → extracted → draft → gaps_open ↔ review_ready → confirmed → rendered
```

只有同时满足以下条件，才允许生成正式 Canvas：

- 关键结论都有 `evidence_refs`；
- blocker/major 缺口已关闭；
- minor 缺口已解决或由确认人接受风险；
- 核心推断已接受或拒绝；
- 人工确认与当前模块版本一致；
- `check_gate.py` 返回 `render_allowed=true`。

## 项目结构

```text
.codebuddy-plugin/plugin.json
agents/mvl-workshop-facilitator.md
schemas/
  module-record.schema.json
  state.schema.json
skills/
  mvl-distill/
  module-conclusion-gate/
  canvas-render/
examples/
tests/
html-templates/
  index.json
  01-蓝色专业-均衡总览版.html
  02-蓝色专业-流程决策版.html
  03-机构信号-均衡总览版.html
  04-机构信号-流程决策版.html
```

## 安装后的首次使用

找到并召唤“闭环助教”后，可以发送：

```text
我们是第 3 组，项目名称是【项目名称】，业务场景是【场景说明】。
请从 M1 开始工作坊。先给出本模块的核心价值、讨论目标和引导问题，不要直接生成 Canvas。
```

完成讨论后，再提交逐字稿：

```text
这是 M1 的讨论逐字稿。
请先存档和提炼，然后审核本模块是否完成核心价值。
请输出结论登记表、证据引用、缺口等级、缺失影响、最少补问和推断清单。
在我确认具体版本之前，不要生成正式 Canvas。

【在这里粘贴逐字稿或提供文件路径】
```

当结论、证据和缺口都核对完成后，再明确确认版本：

```text
我以业务负责人的身份确认 M1 v2。请运行结论闸门；只有 render_allowed=true 时，才生成正式 Canvas。
```

## 三天工作坊使用流程

1. “我们是第 3 组，项目是 XX，从 M1 开始。”
2. 按助教问题完成讨论并提交逐字稿。
3. 助教输出结论登记表、证据、缺口影响、补问和推断。
4. 补齐关键缺口，确认准确的模块版本和确认人角色。
5. 闸门通过后，再说“生成正式画布”。
6. M1-M6 都完成且跨模块一致性通过后，生成全局 Canvas 和领导报告。

如果只想边讨论边看版式，可以要求草稿 Canvas；草稿会带“未确认，禁止用于管理层决策”水印，不能进入全局成果。

## 闸门命令

```powershell
python skills/module-conclusion-gate/scripts/check_gate.py examples/module-record-ready.json
```

退出码：

- `0`：允许正式渲染
- `2`：业务质量闸门未通过
- `1`：输入文件无效

## 验证

```powershell
python -m unittest discover -s tests -v
```

示例：

- `examples/module-record-ready.json`：已确认、可放行
- `examples/module-record-blocked.json`：有 blocker、核心推断和缺失确认，必须阻断

## 本地 HTML 约束

生成的 HTML 应单文件离线可用。不要通过 `fetch()` 读取本地 JSON，也不要用 iframe 嵌套兄弟 HTML；全局 Canvas 使用普通相对链接进入模块详情，避免浏览器的 `file:` 唯一安全源错误。

生成后运行：

```powershell
python skills/canvas-render/scripts/audit_canvas_html.py output/module-1-canvas.html
```

四个模板只提供布局与视觉语法，正式内容必须来自通过闸门的同版本 JSON。
