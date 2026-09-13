# SWOT Canvas HTML 实现契约

本契约定义 SWOT/TOWS（态势分析与策略推导）Canvas 页面的 HTML 结构。

数据源是 `modules/SWOT-{slug}-v{N}.md`（确认包，Markdown）；LLM 读取后按本章的 section 映射表，把内容映射到 HTML 锚点。映射的字段名沿用确认包 Markdown 的 section 标题。`{slug}` 必须等于 `state.json.swot.{slug}.slug`，正式输出为 `output/swot-canvas-{slug}--v{N}.html`；`output/swot-canvas.html` 仅作为多 instance 索引页。

## A. SWOT Canvas 页面结构

```html
<body data-mode="formal" data-page-type="swot" data-version="1" data-instance="{slug}">
  <header id="canvas-header">
    <h1>SWOT/TOWS 分析与策略画布</h1>
    <div id="canvas-headline">一句话结论</div>
  </header>
  <main>
    <section id="swot-topic-summary">
      <h2>课题与结论摘要</h2>
      <div id="swot-topic">分析主体、决策问题与目标、业务边界、时间范围</div>
      <div id="swot-conclusion">当前结论及关键限制</div>
    </section>
    <section id="swot-quadrants">
      <h2>SWOT 四象限</h2>
      <div id="swot-quadrant-s">
        <h3>优势（Strengths）</h3>
        <!-- 因素列表：编号、陈述、重要性、判断性质；展开查看证据与局限 -->
      </div>
      <div id="swot-quadrant-w">
        <h3>劣势（Weaknesses）</h3>
        <!-- 因素列表 -->
      </div>
      <div id="swot-quadrant-o">
        <h3>机会（Opportunities）</h3>
        <!-- 因素列表 -->
      </div>
      <div id="swot-quadrant-t">
        <h3>威胁（Threats）</h3>
        <!-- 因素列表 -->
      </div>
    </section>
    <section id="swot-tows">
      <h2>TOWS 策略</h2>
      <div id="swot-tows-so">
        <h3>SO 策略（利用优势抓住机会）</h3>
        <!-- 策略列表：编号、名称、关联因素、作用机制、成立条件 -->
      </div>
      <div id="swot-tows-st">
        <h3>ST 策略（利用优势应对威胁）</h3>
        <!-- 策略列表 -->
      </div>
      <div id="swot-tows-wo">
        <h3>WO 策略（克服劣势抓住机会）</h3>
        <!-- 策略列表 -->
      </div>
      <div id="swot-tows-wt">
        <h3>WT 策略（克服劣势应对威胁）</h3>
        <!-- 策略列表 -->
      </div>
    </section>
    <section id="swot-comparison">
      <h2>选项比较与取舍</h2>
      <div id="swot-comparison-table">
        <!-- 比较表：代价、风险、AI 推荐、用户决定及理由 -->
      </div>
    </section>
    <section id="swot-handover">
      <h2>最小交接与复审</h2>
      <div id="swot-handover-items">
        <!-- 交接事项：下一步、承接角色、时间或触发条件、预期交付与判断标准 -->
      </div>
    </section>
    <section id="swot-supplementary">
      <h2>补充记录</h2>
      <div id="swot-uncategorized">
        <h3>待分类候选</h3>
        <!-- 归属未明的因素 -->
      </div>
      <div id="swot-excluded">
        <h3>被排除因素</h3>
        <!-- 被排除的因素及原因 -->
      </div>
      <div id="swot-evidence-detail">
        <h3>详细证据</h3>
        <!-- 详细证据与其他候选内容 -->
      </div>
    </section>
  </main>
  <aside id="quality-panel">
    <h3>质量与治理</h3>
    <div id="quality-version">v{N}</div>
    <div id="quality-approval">
      <!-- gate_recommendation / render_authorized / confirmation_mode -->
    </div>
    <div id="quality-gaps">缺口摘要</div>
    <div id="quality-risks">风险摘要</div>
    <div id="quality-caveat" hidden>
      <!-- 仅 override 时显示，含 Gate 建议、override 项数量、高风险项数量、风险详情 -->
    </div>
  </aside>
  <section id="local-notes" contenteditable="true">...</section>
  <script type="application/json" id="canvas-data">
    {
      "version": "v{N}",
      "instance": "{slug}",
      "canvas_type": "swot",
      "sections": { ...确认包 section 映射... },
      "auth": {
        "gate_recommendation": "pass | fail",
        "render_authorized": true,
        "confirmation_mode": "gate_pass | override",
        "override_audit": { ...完整 override_audit 数据，仅 override 时存在... }
      }
    }
  </script>
</body>
```

## B. 稳定锚点映射

| HTML 锚点 | 确认包 section |
|---|---|
| `canvas-headline` | 必展项 → 一句话结论 |
| `swot-topic` | 2：课题卡（分析主体、决策问题与目标、业务边界、时间范围） |
| `swot-conclusion` | 1：必展项 → 当前结论及关键限制 |
| `swot-quadrant-s` | 3：SWOT 四象限 → 优势（Strengths） |
| `swot-quadrant-w` | 3：SWOT 四象限 → 劣势（Weaknesses） |
| `swot-quadrant-o` | 3：SWOT 四象限 → 机会（Opportunities） |
| `swot-quadrant-t` | 3：SWOT 四象限 → 威胁（Threats） |
| `swot-tows-so` | 6：TOWS 策略 → SO 策略 |
| `swot-tows-st` | 6：TOWS 策略 → ST 策略 |
| `swot-tows-wo` | 6：TOWS 策略 → WO 策略 |
| `swot-tows-wt` | 6：TOWS 策略 → WT 策略 |
| `swot-comparison-table` | 7：选项比较与取舍 |
| `swot-handover-items` | 8：最小交接与复审 |
| `swot-uncategorized` | 4：待分类候选 |
| `swot-excluded` | 5：被排除因素 |
| `swot-evidence-detail` | 11：证据与推断登记 → 关键证据引用（详细证据） |

**关键规则**：

- 已讨论的字段正常展示内容；未讨论的字段显示"未讨论"并标为缺口。
- 四象限允许空象限，但必须说明原因（`data-state="empty"` + 原因说明）。
- TOWS 四组允许空组，但必须说明原因。
- 因素编号（SWOT-F-S01/SWOT-F-W01/SWOT-F-O01/SWOT-F-T01）不随象限调整而改变。
- TOWS 策略必须关联具体因素编号，点击可定位。
- SWOT Canvas 是独立一等公民画布；同一 group 可有多个 instance，不存在子模块详情页和全局汇总页。

## C. 七区结构与阅读顺序

SWOT Canvas 采用七区综合页面结构，按以下顺序阅读：

| 区域 | 核心锚点 | 必需性 |
|---|---|---|
| 课题与结论摘要 | `swot-topic-summary`（含 `swot-topic`、`swot-conclusion`） | 必需 |
| SWOT 四象限 | `swot-quadrants`（含 `swot-quadrant-s/w/o/t`） | 必需（允许空象限 + 原因说明） |
| TOWS 策略 | `swot-tows`（含 `swot-tows-so/st/wo/wt`） | 必需（允许空组 + 原因说明） |
| 选项比较与取舍 | `swot-comparison`（含 `swot-comparison-table`） | 必需 |
| 最小交接与复审 | `swot-handover`（含 `swot-handover-items`） | 必需 |
| 质量与治理 | `quality-panel`（含 `quality-version`、`quality-approval`、`quality-gaps`、`quality-risks`、`quality-caveat`） | 必需，复用共享治理 ID |
| 补充记录 | `swot-supplementary`（含 `swot-uncategorized`、`swot-excluded`、`swot-evidence-detail`） | 必需 |

## 共享结构

与 MVL / GC / HMW Canvas 共享 quality-panel、local-notes、canvas-data 结构（见 `render-contract.md`）。差异：

- `data-page-type` 为 `swot`（非 `global` / `module-detail` / `golden-circle` / `hmw`）。
- 无 `data-module` 属性。
- `canvas-data.module` 字段替换为 `canvas-data.canvas_type: "swot"`。
- `canvas-data.auth` 字段对应 `state.json.swot.{slug}`，且 `canvas-data.instance` 必须等于同一 `{slug}`。
- SWOT 不生成全局 Canvas、不扫描跨模块 caveat。

### Caveat 状态标识

与 MVL / GC / HMW 一致：
- `confirmation_mode=gate_pass`：显示"已确认"。
- `confirmation_mode=override`：显示"**已确认 · 带保留意见**"。

## 本地离线约束

- **CSS、JavaScript、图标和字体必须内联或使用系统字体；正式产物禁止依赖本地相对路径外链 CSS**（如 `<link rel="stylesheet" href="shared/canvas-theme.css">`）。方案 A（2026-08-09）已把示例模板主题内联，成品须与其一致。
- 禁止通过 `fetch("file.json")` 加载本地数据。
- 禁止用 iframe 打开兄弟 HTML；使用普通相对链接。
- **成品 HTML 必须单文件自包含（CSS 内联），独立传播时无需任何伴随文件**；无网络时仍可展开、筛选、打印和编辑。
- 支持打印：打印时展开证据与条件，允许多页，避免强压成一页而难以阅读。

## 数据完整性

- 输出页的 `data-version` 必须等于确认包版本 `v{N}`。
- 页面内嵌数据必须来自同一次读取。
- 因素编号、策略编号、缺口 ID 与确认包 Markdown 保持一致。
- `canvas-data` 的 `auth` 字段必须与 `state.json.swot.{slug}` 完全一致。
- `body[data-instance]`、`canvas-data.instance`、确认包文件名 `{slug}` 与 `state.json.swot.{slug}.slug` 必须一致。

## 模板结构 Profile（Template Gate 判定依据）

Template Gate（`audit_canvas_html.py --template skills/canvas-render/examples/swot-canvas.html --type swot --instance {slug}`）以本 profile 为判定依据，比较成品与模板的一级模块、稳定锚点与相对 DOM 顺序。**不比较**占位文本、业务文案、动态版本值或 CSS 逐字符内容。

### 一级模块必需性与 DOM 相对顺序（强制）

```text
canvas-header
  → swot-topic-summary
  → swot-quadrants
  → swot-tows
  → swot-comparison
  → swot-handover
  → quality-panel
  → swot-supplementary
  → local-notes
  → canvas-data
```

> **顺序依据**：以 `examples/swot-canvas.html` 模板实际 DOM 顺序为准。Template Gate 以本 profile 与模板为比对基准。

任一一级模块缺失、重复或相对顺序偏离本 profile，Template Gate FAIL（`SWOT-TPL-GATE-02` / `SWOT-TPL-GATE-03`）。

### 稳定锚点集合（Template Gate 校验）

- 页面：`data-page-type="swot"`（`SWOT-TPL-GATE-01`）
- 课题与结论：`swot-topic-summary`（含 `swot-topic`、`swot-conclusion`）（`SWOT-TPL-GATE-04`）
- 四象限：`swot-quadrant-s` / `swot-quadrant-w` / `swot-quadrant-o` / `swot-quadrant-t`（允许空象限 `data-state="empty"` + 原因说明）（`SWOT-TPL-GATE-04`）
- TOWS 四组：`swot-tows-so` / `swot-tows-st` / `swot-tows-wo` / `swot-tows-wt`（允许空组 `data-state="empty"` + 原因说明）（`SWOT-TPL-GATE-04`）
- 比较与取舍：`swot-comparison`（含 `swot-comparison-table`）（`SWOT-TPL-GATE-04`）
- 交接与复审：`swot-handover`（含 `swot-handover-items`）（`SWOT-TPL-GATE-04`）
- 补充记录：`swot-supplementary`（含 `swot-uncategorized`、`swot-excluded`、`swot-evidence-detail`）（`SWOT-TPL-GATE-04`）
- 治理面板：`quality-panel` 含 `quality-version` / `quality-approval` / `quality-gaps` / `quality-risks` / `quality-caveat` 插槽（`SWOT-TPL-GATE-05`）
- 批注与数据：`local-notes`、`canvas-data`（`SWOT-TPL-GATE-02`）
- 共享主题（**内联 `<style>` 或本地 `<link>` 均可，正式产物须内联、禁止依赖本地相对路径外链 CSS**）/ 窄屏布局，无外部网络依赖（`SWOT-TPL-GATE-06`）

### 隐藏检测（Template Gate 与内容/授权 Gate 共用）

治理面板（`quality-panel`）与关键限制（`swot-conclusion`）不得以任何方式隐藏。四种隐藏方式任一命中即 FAIL：

1. `hidden` HTML 属性（`hidden` 属性存在）
2. `style="display:none"` 或计算后 `display` 为 `none`
3. `style="visibility:hidden"` 或计算后 `visibility` 为 `hidden`
4. `class="hidden"`（约定 `.hidden { display:none; }`）

### 参考样例

- `examples/swot-canvas.html`：SWOT 一等公民**版面与签名视觉事实源**（Template Gate 的比对模板）。

## 交付前自检

同 MVL / GC / HMW：Python 静态审计（`skills/canvas-render/scripts/audit_canvas_html.py --type swot --instance {slug}`，正式交付追加 `--template skills/canvas-render/examples/swot-canvas.html` 触发双 Gate）+ 浏览器视觉验收。两阶段都通过后才把当前 instance 状态改为 `rendered`。
