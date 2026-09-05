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
