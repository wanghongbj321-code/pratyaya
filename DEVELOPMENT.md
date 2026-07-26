# 开发者与维护者指南（DEVELOPMENT）

本文件面向**维护专家包的人**和**运行时的 AI 助教**，不面向工作坊助教。工作坊助教的使用说明见 `README.md`。

## 质量闸门命令

对某一个模块的记录运行确定性闸门：

```powershell
python skills/module-conclusion-gate/scripts/check_gate.py examples/module-record-ready.json
```

退出码：

- `0`：允许正式渲染（`render_allowed=true`）
- `2`：业务质量闸门未通过（`render_allowed=false`，`reasons` 列出阻断项）
- `1`：输入文件无效（无法解析或不符合 Schema）

闸门检查项（详见 `skills/module-conclusion-gate/references/gate-policy.md`）：

- 关键结论都有 `evidence_refs`；
- blocker / major 缺口已关闭；
- minor 缺口已解决或由确认人接受风险（`accepted_risk`）；
- 核心推断已接受或拒绝；
- 人工确认版本与当前模块版本一致；
- **对齐闸门**：无 `open` 的 blocker / major 分歧；如分歧以 `accepted_risk` 关闭，接受人必须出现在 `approval` 中；
- 对齐对象 `alignment` 为必填，且 `consensus` / `divergences` / `decisions` 均按要求填写。

## 回归验证

仓库**不发布 `tests/` 目录**（回归测试依赖本地 Python 环境，仅用于维护期）。在本地克隆或开发副本上运行：

```powershell
python -m unittest discover -s tests -v
```

示例记录：

- `examples/module-record-ready.json`：已确认、可放行（闸门返回 `0`）
- `examples/module-record-blocked.json`：含 blocker、核心推断和缺失确认，必须阻断（闸门返回 `2`）

## 本地 HTML 约束（渲染层）

生成的 HTML 必须单文件离线可用。约束（详见 `skills/canvas-render/references/render-contract.md`）：

- 不要通过 `fetch()` 读取本地 JSON；
- 不要用 `iframe` 嵌套兄弟 HTML；
- 全局 Canvas 使用普通相对链接进入模块详情，避免浏览器的 `file:` 唯一安全源错误；
- 四个模板只提供布局与视觉语法，正式内容必须来自通过闸门的同版本 JSON。

生成后运行离线审计：

```powershell
python skills/canvas-render/scripts/audit_canvas_html.py output/module-1-canvas.html
```

审计检查单文件离线结构（六大画布锚点、质量面板内的对齐锚点、本地批注、JSON 数据块等）。缺失必要结构或存在不安全引用时返回非零退出码。

## 版本与发布

- 任何影响闸门、Schema、渲染契约或行为的改动，需升级 `plugins/mvl-workshop-facilitator` 的 `plugin.json` 版本号后再覆盖安装；
- 升级后需在 WorkBuddy 中覆盖安装并完全重启，使新专家生效。
