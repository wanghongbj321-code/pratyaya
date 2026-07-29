# html-slides 能力的 Canvas 适配

本参考只吸收 `html-slides` 中能提升 Canvas 交付质量的能力。它不改变 MVL 的模块定义、结论闸门或事实来源，也不把 Canvas 变成幻灯片。

## 可使用的能力

1. **策展模板选择**：从 `../../../html-templates/index.json` 选择一个与已确认用途匹配的模板外壳。
2. **视觉系统继承**：继承模板的字体层级、色板、网格、间距、边框、图标语法和组件密度。
3. **同语法扩展**：模板缺少当前 Canvas 小模块时，在同一设计语言中补布局，不引入另一套风格。
4. **浏览器预览**：在桌面、窄屏和打印视图中检查阅读顺序、溢出、遮挡、链接和编辑功能。
5. **离线交付**：CSS、JavaScript、数据和必要图标保留在单个 HTML 内，本地双击即可打开。
6. **结构自检**：正式交付前 LLM 按 `SKILL.md` 的"渲染自检"清单逐项确认（已替代阶段一移除的 `scripts/audit_canvas_html.py`）。

## 可选外壳清单

`html-templates/index.json` 当前登记 9 个模板，覆盖 7 种视觉系统 × 2 种版式（balanced / flow）。完整字段见 index.json 的 `templates` 数组，本表是速查：

| 模板 ID | 视觉系统 | 版式 | 正式度 | 信息密度 |
|---|---|---|---|---|
| `blue-professional-balanced` | Blue Professional | balanced | medium-high | medium |
| `blue-professional-flow` | Blue Professional | flow | medium-high | medium-high |
| `signal-balanced` | Signal | balanced | high | medium-high |
| `signal-flow` | Signal | flow | high | high |
| `mckinsey-blue-conclusion` | McKinsey Blue | balanced | high | medium |
| `accenture-red-grey-institutional` | Accenture Red-Grey | balanced | high | medium-high |
| `bain-red-action` | Bain Red | balanced | high | medium |
| `bcg-green-matrix` | BCG Green | balanced | high | medium |
| `roland-berger-orange` | Roland Berger Orange | balanced | high | medium |

每个模板的 `best_for` 字段（见 index.json）描述适用场景。模板选择由主 agent 步骤 7 的 LLM 自行决定推荐 1-2 个候选，再由用户拍板；**本 skill 不自动选择**。一个输出必须保持单一视觉系统，不混搭 Blue Professional 与 Signal，也不混搭咨询公司模板的强品牌色。

## 模板只是视觉外壳

- 不得复制模板示例内容，包括标题、品牌、角色、数字、指标、结论和敏感信息。
- 所有业务内容只能来自本次已确认、同版本的 `modules/Mx-v{N}.md`。
- 必须用当前规范的完整大模块、小模块、质量元数据和稳定锚点替换模板结构。
- 模板没有的区块可以新增，但必须沿用所选模板的设计语法。
- `模块化智能体画布-3个脱敏模板.html` 是历史组合预览，不属于可选模板，不得作为正式输出的起点。

## 明确排除的幻灯片行为

- 不要求每次先展示三个候选标题页。
- 不使用幻灯片分页、键盘翻页或演示运行时。
- 不以页数替代 Canvas 的完整模块覆盖。
- 不因视觉适配改变工作坊映射、结论状态或质量闸门。

## 浏览器预览清单

1. 桌面宽屏下，六大模块、质量状态和下钻入口的阅读顺序清晰。
2. 窄屏下，卡片按合理顺序堆叠，表格可横向滚动，不出现文字裁切。
3. 打印视图包含结论、版本、确认信息和风险状态，并隐藏非必要编辑控件。
4. 本地 `file://` 双击打开时不请求网络、不调用 `fetch()`、不嵌入 iframe。
5. 编辑只写入明确标记的"本地批注"，不覆盖已确认事实。
6. 按 `SKILL.md` 的"渲染自检"清单逐项确认（数据源 / DOM / 共享结构 / 离线安全 / 打印 / 草稿标记 / 视觉系统 7 项）。

自检通过仍不替代人工视觉检查；二者都完成后才可交付正式 HTML。
