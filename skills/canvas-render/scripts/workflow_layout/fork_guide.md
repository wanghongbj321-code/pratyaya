# L2 布局分叉向导（fork_guide，3.5.0+）

> 定位：`L2` 是三层定制（L0/L1/L2）中的**最后手段**——只有 `L1 layout_override`
> 无法表达的形态（整图结构级改造）才允许分叉，且**必须显式触发**（用户要求）。
> 默认路径永远用 L0 基线布局器 + L1 配置。
> 设计：`全局画布Workflow确定性布局器设计方案-20260905.md` §4（L1 不可配清单 → L2）。

## 触发条件（全满足才进入 L2）

1. 用户**显式**要求使用定制布局；
2. 形态确实超出 L1 配置能力（对照 `layout_override.schema.md`「不可配清单」）；
3. 已确认采用当前基线版本 `VERSION`（本目录）。

## 拷贝协议（首次分叉才物化）

```bash
cp skills/canvas-render/scripts/workflow_layout/workflow_layout.py <topic>/.layout/workflow_layout.py
cp skills/canvas-render/scripts/workflow_layout/VERSION            <topic>/.layout/VERSION
# 不拷贝 __pycache__；VERSION 必须与副本同行（副本读取 __file__ 旁 VERSION）
```

分叉后写 `layout_meta.json`（topic 布局目录）：

```json
{
  "fork_id": "group-x-haier-price-fork-01",
  "derived_from": {
    "baseline_version": "0.2.0",
    "baseline_sha": "<基线 workflow_layout.py 的 git sha>"
  },
  "layout_model": "track-inner-flow",
  "changed": ["MAX_PER_ROW 默认 6→4", "折返行起点右移 40px"]
}
```

## 改造边界（违反即退回）

- **只允许几何 / 形态级小范围修改**；不得改变节点 / 边全集（Q3 几何降级）、不得改写业务 label / actor / track 语义；
- 不得削弱布局器输出契约（轨道分行堆叠 / 正交 / 不穿节点 / gutter 绕行 / 无泳道色块对齐母版）；
- 当前基线能力边界（单左 gutter、无右 gutter / 线-线避让 / 汇合槽位）见 `layout_override.schema.md`「能力边界」；分叉扩出边界（如新增右 gutter 分流）必须写入 `layout_meta.changed` 并经自检 + L1/L2 验收；
- 复用的 `selfcheck()` 几何断言必须保留且为唯一可信出口。

## 验收门（L2 产物必须全部通过）

1. **几何自检 0 问题**：`python3 <topic>/.layout/workflow_layout.py <topo.json>` 输出「自检问题: 0」；
2. **L1 静态审计**与 **L2 DOM 断言**按常规跑（分叉不豁免）；
3. **溯源记录**：产物 HTML 的 `canvas-data.workflow.layout` 写入
   `{"engine": "workflow_layout", "baseline_version": "<0.2.0>", "fork_id": "<fork_id>"}`
   （用模块函数 `workflow_layout.layout_trace(fork_id)` 生成）；
4. 渲染自检报告记录分叉与通过结果。

## 漂移治理

- 每次基线升级（专家包发布新 `VERSION`）时，对 topic 已分叉副本提示
  `derived_from.baseline_version` 落后 → 由用户决定"升级合并 / 保持分叉"；
- 未分叉 topic 不产生副本（零配置即 L0 基线）。

## 演示（端到端 smoke）

```bash
mkdir -p tmp/fork-demo/.layout
cp skills/canvas-render/scripts/workflow_layout/workflow_layout.py tmp/fork-demo/.layout/
cp skills/canvas-render/scripts/workflow_layout/VERSION tmp/fork-demo/.layout/
cd tmp/fork-demo/.layout
python3 workflow_layout.py ../../../../tests/fixtures/workflow_layout/workflow_hotel_revenue_new.json --version
```
若副本能加载并自检 0 问题，即证明"分叉 + 自检门"链路可用。

最终 SVG 使用 `--fragment <全新目标.svg>`，单输入、exit 0 才可嵌入；旧 `--svg` 保留目检预览。分叉也必须通过 fragment 结构/转义及宿主 L1/L2/L3 回归。
