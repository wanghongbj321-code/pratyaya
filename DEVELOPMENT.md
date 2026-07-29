# 维护者文档

> 面向维护专家包的人和运行时的 AI 助教。**不面向**工作坊用户（用户文档见 [docs/user-guide.md](./docs/user-guide.md)）。

## 1. 文档定位

本文件说明维护专家包所需的命令、流程约束和工具链。完整架构与不变量见 [DESIGN.md](./DESIGN.md)；工作坊用户使用流程见 [docs/user-guide.md](./docs/user-guide.md)；专家包元数据以 `.codebuddy-plugin/plugin.json` 为权威。

## 2. 质量闸门（LLM 自检）

v2.0 起，模块结论闸门（Gate）由 LLM 评估替代 v1.x 的 Python 脚本（`check_gate.py` 已删除）。执行流程：

1. LLM 读取 `modules/Mx-v{N}.md`（确认包 Markdown）
2. 对照 `skills/module-conclusion-gate/SKILL.md` 的判定规则
3. 输出 Markdown 判定报告 `gate-policy/Mx-gate.md`，含 `render_allowed` 字段

详细规则、缺口等级、推断术语、版本绑定的完整定义见 [skills/module-conclusion-gate/SKILL.md](./skills/module-conclusion-gate/SKILL.md)。

## 3. HTML 渲染（LLM 自检）

v2.0 起，HTML 渲染审计由 LLM 自检替代 v1.x 的 Python 脚本（`audit_canvas_html.py` 已删除）。正式交付前 7 项检查清单：

1. 数据源一致（HTML 内嵌 `canvas-data` 与 `Mx-v{N}.md` 同版本）
2. DOM 结构（对照 `render-contract.md` 章节 A/B）
3. 共享结构（`quality-panel` / `alignment-section` / `local-notes`）
4. 离线安全（无 `fetch("file...")`、无 iframe、无外部网络资源）
5. 打印规则（`@media print` 隐藏编辑控件）
6. 草稿标记（草稿模式顶部与打印版含"草稿/未确认"字样）
7. 视觉系统单一（仅一种 `visual_system`，不混搭）

详细自检依据、DOM 映射表、共享结构、离线约束、数据完整性见 [skills/canvas-render/SKILL.md](./skills/canvas-render/SKILL.md) 与 [skills/canvas-render/references/render-contract.md](./skills/canvas-render/references/render-contract.md)。

## 4. 模块工作流

四阶段管线（数据源与闸门）：

```text
Key Points (Mx-keypoints.md) → 提炼 (Mx-v{N}.md) → Gate (Mx-gate.md) → 渲染 (HTML)
```

每个阶段的输入/输出/状态变化由对应 Skill 定义，详见 [skills/mvl-distill/SKILL.md](./skills/mvl-distill/SKILL.md) / [skills/module-conclusion-gate/SKILL.md](./skills/module-conclusion-gate/SKILL.md) / [skills/canvas-render/SKILL.md](./skills/canvas-render/SKILL.md)。

## 5. 版本与发布

专家包版本号遵循 SemVer（语义化版本），定义在 `.codebuddy-plugin/plugin.json` 的 `version` 字段：

- **MAJOR**：破坏性变更（数据源切换、状态机调整、Skill 重写等）
- **MINOR**：新增功能（新增 Skill 子任务、新增文档章节等）
- **PATCH**：Bug 修复、措辞调整

当前版本：v2.0.0。

发布流程（按 workbuddy 指导第十节"修改已有专家"5 步）：

1. **定位** — 确认改动范围（在哪个文件、影响哪些 Skill/Agent/模板）
2. **确认范围** — 评估是否需要同步 docs/、DEVELOPMENT.md、DESIGN.md
3. **执行修改** — 改完代码与文档
4. **校验** — `python3 -c "import json; json.load(open('.codebuddy-plugin/plugin.json'))"` 验证 plugin.json 是合法 JSON；运行 `scripts/validate_expert.py`（如存在）
5. **重新注册** — WorkBuddy 重启加载（详见 [docs/installation.md §4](./docs/installation.md#4-安装后必须重启)）

严禁修改（按 workbuddy 指导）：`name` 字段（kebab-case 唯一标识）、`agentName` 字段、专家目录名、agents/ 下的 .md 文件名。这些字段的修改会导致专家丢失。

## 6. 命令速查

| 命令 | 用途 |
|---|---|
| `git log --oneline` | 查看 commit 历史 |
| `git diff` | 查看当前未提交变更 |
| `python3 -c "import json; json.load(open('.codebuddy-plugin/plugin.json'))"` | 验证 plugin.json 合法 |
| `python3 -c "import json; json.load(open('html-templates/index.json'))"` | 验证 templates 合法 |
| `grep -rn "check_gate.py\|audit_canvas_html.py" .` | 检查旧脚本引用残留 |
| `grep -rn "module-N\.json" .` | 检查旧 JSON 引用残留 |
| `wc -l README.md DEVELOPMENT.md DESIGN.md docs/*.md` | 检查文档行数是否符合 v2.0 约束 |

---

**版本**：v2.0.0
**配套文档**：[DESIGN.md](./DESIGN.md) / [docs/installation.md](./docs/installation.md) / [docs/user-guide.md](./docs/user-guide.md)
