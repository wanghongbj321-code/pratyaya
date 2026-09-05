# layout_override 配置说明（L1 布局配置层，3.5.0+）

> 定位：`layout_override` 是**渲染输入侧可选参数**（渲染回合传给布局器，**不进 `canvas-data`**，
> 不改变业务事实 / 授权元数据）。只调节**几何常量**，不改变节点 / 边集合、轨道结构与任何审计契约。
> 设计：`全局画布Workflow确定性布局器设计方案-20260905.md` §3.3 / §4（L1）。

## 用法（布局器 CLI）

```bash
# 显式 JSON 文件
python3 skills/canvas-render/scripts/workflow_layout/workflow_layout.py \
  <topo.json> --override layout_override.example.json

# 或内联 JSON / 预置
python3 .../workflow_layout.py <topo.json> --override-json '{"row_h": 84}'
python3 .../workflow_layout.py <topo.json> --preset compact
```

## 可配置键（白名单，其余键忽略并告警）

| 键 | 类型 | 默认 | 含义 |
|---|---|---|---|
| `card_h` | number | 58.0 | 任务卡片高度 |
| `card_w_min` | number | 150.0 | 任务卡片最小宽 |
| `card_w_max` | number | 260.0 | 任务卡片最大宽（防超宽） |
| `row_h` | number | 96.0 | 轨道内行中心距（紧凑/宽松） |
| `track_gap` | number | 60.0 | 相邻轨道带间距 |
| `track_pad_top` | number | 44.0 | 轨道标签行高（首行起始 y） |
| `margin_x` | number | 60.0 | 左边缘 / 列起点 |
| `gutter_w` | number | 70.0 | 左 gutter 走廊宽（跨轨 / 回流绕行） |
| `max_per_row` | integer | 6 | 每行最大节点数（超则折返第二行） |
| `max_page_w` | number | 1400.0 | 整页宽度预算（A3 打印可读上限，供测试断言） |

## 预置（preset）

- `compact`：行距/间距/边距收紧、卡宽上限降低（高密度）；
- `roomy`：行距/间距/边距放宽（低密度展示）。

## 可配 / 不可配对照清单（L1 边界）

**可配（几何）：** 上表全部键 + 上述两个 preset。

**不可配（语义 / 契约，禁止在 L1 改）：**
- 节点集合与边集合（Q3：几何降级，节点一个不少）；
- 轨道结构、`track` 归属与轨道顺序；
- 节点类型 / actor / label 语义（业务事实）；
- `#workflow-flow` 锚点、DOM 结构、audit 断言、离线/单文件约束（§A1 契约）；
- 视觉 token 中由 CSS/母版固定的部分（actor 徽章样式、序号徽标、事件符号、图例结构）。

**需要 L2 分叉（超出配置能力）才处理的情形**（显式触发 + 探针自检 + 溯源）：母版形态之外的整图结构级改造（如新增第三类边、特殊折返模式）。

## 能力边界（基线 0.2.0；L2 分叉与 L0 演进的参考基线）

- **形态覆盖**：轨道 ≤3、节点 ≤ ~20、轨道内蛇形折返多行横流、gateway 分支 / 多入汇合 / timer / message / data_store / 单轨 `main` 均支持；跨轨边与 dashed 回流边均渲染。
- **路由走廊（当前简化，审查记录项）**：跨轨边与 **dashed 回流一律走左侧 gutter 走廊**（宽 `gutter_w`）；母版的双侧 gutter（右 gutter / 竖排 label）、多入汇合槽位错位、线-线避让为 **L0 演进项**，当前不覆盖。形态超界时先 L1 调参（`compact` / `row_h` / `track_gap` / `max_per_row`），仍不可表达再按 L2 分叉并记录 `layout_meta.changed`。
- **输出契约（几何层定位）**：产物 = 节点坐标 / 连线路径（正交 `M/H/V`、dashed 标虚 + 走 gutter）/ 几何自检报告（重叠 / 正交 / 穿节点 / 端点落边界中点 / dashed 走 gutter / track 归属 / 边全集不丢）/ 坐标表；`--svg` 为**目检预览页，非 §A1 最终 DOM**；`--fragment <new.svg>` 输出最终 SVG 内部结构（节点/actor/序号/轨道/边），HTML 外层、图例、完成条件仍由 canvas-render 负责。
- **仅几何降级（Q3）**：节点 / 边全集一个不少；文本折行上限 ≤3 行（超出以省略号截断）；超页宽（`max_page_w`）仅报告并提示 preset，不主动截断节点。

最终 SVG 使用 `--fragment <全新目标.svg>`，单输入、exit 0 才可嵌入；旧 `--svg` 保留目检预览。分叉也必须通过 fragment 结构/转义及宿主 L1/L2/L3 回归。
