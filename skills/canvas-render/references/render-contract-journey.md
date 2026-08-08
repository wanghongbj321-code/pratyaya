# User Journey Canvas HTML 实现契约

本契约定义 User Journey（用户旅程）一等公民 Canvas 页面的 HTML 结构。

> **v2.3.2 PATCH**：将 5 行主表第 4 / 5 行文本重命名为「痛点 / 机会」，将 6b 节标题重命名为「痛点与机会」，将 6a 质量维度键 / 6b 锚点 / 5 行 DOM 子锚点 / stage data 字段统一为新字段体系（旧字段体系已退场）。
> 字段映射说明见文末"v2.3.0 → v2.3.2 字段映射"表。

数据源是 `modules/JOURNEY-v{N}.md`（确认包，Markdown）；`canvas-render` 读取后按本契约把确认包内容映射到稳定 HTML 锚点。渲染层只做展示映射，不重新判断质量、不生成新结论、不补写确认包中不存在的业务判断。

## A. Journey Canvas 页面结构

```html
<body data-mode="formal" data-page-type="journey" data-version="1">
  <header id="canvas-header">
    <h1>User Journey 用户旅程画布</h1>
    <div id="canvas-headline">一句话结论</div>
  </header>
  <main>
    <section id="journey-map">
      <article id="journey-stage-1">
        <div id="journey-stage-1-action">行动</div>
        <div id="journey-stage-1-touchpoint-system">触点与系统</div>
        <div id="journey-stage-1-emotion">情绪</div>
        <div id="journey-stage-1-pain-point">痛点</div>
        <div id="journey-stage-1-opportunity">机会</div>
      </article>
      <!-- journey-stage-{n} 根据确认包第 6 节动态生成 -->
    </section>
    <section id="journey-pain-opportunities">
      <div id="journey-pain-opportunity-summary">痛点与机会</div>
    </section>
    <section id="journey-quality">
      <div id="journey-quality-user-perspective">用户视角判定</div>
      <div id="journey-quality-business-outcome">到达业务结果判定</div>
      <div id="journey-quality-pain-opportunity-visible">痛点与机会可见判定</div>
      <div id="journey-quality-no-solution-bias">未预设方案判定</div>
    </section>
  </main>
  <aside id="quality-panel">
    <div id="quality-version">v{N}</div>
    <div id="quality-approval"><!-- gate_recommendation / render_authorized / confirmation_mode --></div>
    <div id="quality-gaps">缺口摘要</div>
    <div id="quality-risks">风险摘要</div>
    <div id="quality-caveat" hidden><!-- 仅 override 时显示 --></div>
  </aside>
  <section id="local-notes" contenteditable="true">...</section>
  <script type="application/json" id="canvas-data">
    {
      "version": "v{N}",
      "canvas_type": "journey",
      "sections": { ...确认包 section 映射... },
      "stages": [
        {
          "stage_index": 1,
          "stage_name": "...",
          "action": "...",
          "touchpoint_system": "...",
          "emotion": "...",
          "pain_point": "...",
          "opportunity": "..."
        }
      ],
      "quality": {
        "user_perspective": "通过 | 不通过 | 未判定",
        "business_outcome": "通过 | 不通过 | 未判定",
        "pain_opportunity_visible": "通过 | 不通过 | 未判定",
        "no_solution_bias": "通过 | 不通过 | 未判定"
      },
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
| `journey-map` | 6：阶段地图 |
| `journey-stage-{n}` | 6：第 n 个阶段 |
| `journey-stage-{n}-action` | 6：第 n 个阶段的行动 |
| `journey-stage-{n}-touchpoint-system` | 6：第 n 个阶段的触点与系统 |
| `journey-stage-{n}-emotion` | 6：第 n 个阶段的情绪 |
| `journey-stage-{n}-pain-point` | 6：第 n 个阶段的痛点 |
| `journey-stage-{n}-opportunity` | 6：第 n 个阶段的机会 |
| `journey-pain-opportunities` | 6b：痛点与机会 |
| `journey-pain-opportunity-summary` | 6b：痛点与机会摘要 |
| `journey-quality` | 6a：质量鉴别 |
| `journey-quality-user-perspective` | 6a：user_perspective（用户视角） |
| `journey-quality-business-outcome` | 6a：business_outcome（到达业务结果） |
| `journey-quality-pain-opportunity-visible` | 6a：pain_opportunity_visible（痛点与机会可见） |
| `journey-quality-no-solution-bias` | 6a：no_solution_bias（未预设方案） |

**关键规则**：

- Journey 主表忠实保留 5 行合并结构：行动 / 触点与系统 / 情绪 / 痛点 / 机会。
- 阶段根据确认包第 6 节动态生成，不固定 7 个槽位。
- 不得新增第 6 行承载质量鉴别；质量鉴别是正式画布外显治理区块。
- `journey-quality-*` 的数据源为 `JOURNEY-v{N}.md` 第 6a 节，不由 `canvas-render` 推断。
- `journey-pain-opportunity-summary` 的数据源为 `JOURNEY-v{N}.md` 第 6b 节，不由 `canvas-render` 推断。
- Journey Canvas 是单画布，不存在子模块详情页和全局汇总页，不扫描 MVL 跨模块 caveat。

## C. 动态阶段规则

1. 阶段编号从 1 开始连续递增。
2. 阶段数量不少于 3。
3. 每个阶段必须包含 5 个子锚点。
4. 每个阶段内子锚点 DOM 相对顺序固定为：

```text
action → touchpoint-system → emotion → pain-point → opportunity
```

5. 阶段数量与 `canvas-data.stages.length` 一致。
6. `canvas-data.stages[]` 每项必须包含：
   - `stage_index`
   - `stage_name`
   - `action`
   - `touchpoint_system`
   - `emotion`
   - `pain_point`
   - `opportunity`
7. 阶段顺序与 `JOURNEY-v{N}.md` 第 6 节表格行顺序一致。

## 共享结构

与 MVL / GC / HMW Canvas 共享 `quality-panel`、`local-notes`、`canvas-data` 结构（见 `render-contract.md`）。差异：

- `data-page-type` 为 `journey`。
- 无 `data-module` 属性。
- `canvas-data.module` 字段替换为 `canvas-data.canvas_type: "journey"`。
- `canvas-data.auth` 字段对应 `state.json.journey`。

### Caveat 状态标识

与 MVL / GC / HMW 一致：

- `confirmation_mode=gate_pass`：显示"已确认"。
- `confirmation_mode=override`：显示"**已确认 · 带保留意见**"，`quality-caveat` 必须可见，并列出被接受的 business_risk Gate 项。

## 本地离线约束

- CSS、JavaScript、图标和字体优先内联或使用系统字体。
- 禁止通过 `fetch("file.json")` 加载本地数据。
- 禁止用 iframe 打开兄弟 HTML；使用普通相对链接。
- 所有交互在单文件内工作，无网络时仍可展开、筛选、打印和编辑。

## 数据完整性

- 输出页的 `data-version` 必须等于确认包版本 `v{N}`。
- 页面内嵌数据必须来自同一次读取。
- 结论 ID、缺口 ID、推断 ID 与确认包 Markdown 保持一致。
- `canvas-data` 的 `auth` 字段必须与 `state.json.journey` 完全一致。
- `canvas-data.quality` 必须包含 4 个质量维度：`user_perspective` / `business_outcome` / `pain_opportunity_visible` / `no_solution_bias`。

## 打印与管理层阅读

- `@media print` 隐藏编辑控件，保留版本、确认、风险状态、阶段地图、质量鉴别、痛点与机会摘要和 override caveat。
- 阶段地图在打印版保留 5 行结构，不得改写为七要素列表。
- override 画布必须保留 caveat 标识与风险详情。

## 模板结构 Profile（Template Gate 判定依据）

Template Gate（`audit_canvas_html.py --template skills/canvas-render/examples/user-journey-canvas.html --type journey`）以本 profile 为判定依据，比较成品与模板的一级模块、稳定锚点、动态阶段锚点规则与相对 DOM 顺序。**不比较**占位文本、业务文案、动态版本值或 CSS 逐字符内容。

### 一级模块必需性与 DOM 相对顺序（强制）

```text
canvas-header
  → journey-map
  → journey-pain-opportunities
  → journey-quality
  → quality-panel
  → local-notes
  → canvas-data
```

任一一级模块缺失、重复或相对顺序偏离本 profile，Template Gate FAIL（`JOURNEY-TPL-GATE-02` / `JOURNEY-TPL-GATE-03`）。

### 稳定锚点集合（Template Gate 校验）

- 页面：`data-page-type="journey"`（`JOURNEY-TPL-GATE-01`）
- 主表：`journey-map`、动态 `journey-stage-{n}` 与每阶段 5 子锚点（`JOURNEY-TPL-GATE-04`）
- 痛点与机会摘要：`journey-pain-opportunities`、`journey-pain-opportunity-summary`（`JOURNEY-TPL-GATE-04`）
- 质量 4 维度：`journey-quality-user-perspective` / `journey-quality-business-outcome` / `journey-quality-pain-opportunity-visible` / `journey-quality-no-solution-bias`（`JOURNEY-TPL-GATE-04`）
- 治理面板：`quality-panel` 含 `quality-version` / `quality-approval` / `quality-gaps` / `quality-risks` / `quality-caveat` 插槽（`JOURNEY-TPL-GATE-05`）
- 批注与数据：`local-notes`、`canvas-data`（`JOURNEY-TPL-GATE-02`）
- 共享主题 / 横向滚动 / 窄屏布局 / `@media print` 钩子存在，无外部网络依赖（`JOURNEY-TPL-GATE-06`）

### 隐藏检测（Template Gate 与内容/授权 Gate 共用）

阶段地图（`journey-map`）、痛点与机会摘要（`journey-pain-opportunities`）、质量鉴别（`journey-quality`）与治理面板（`quality-panel`）不得以任何方式隐藏。四种隐藏方式任一命中即 FAIL：

1. `hidden` HTML 属性（`hidden` 属性存在）
2. `style="display:none"` 或计算后 `display` 为 `none`
3. `style="visibility:hidden"` 或计算后 `visibility` 为 `hidden`
4. `class="hidden"`（约定 `.hidden { display:none; }`）

## v2.3.0 → v2.3.2 字段映射

以下字段在 v2.3.2 PATCH 重构中已经被同名语义替换，仅供迁移期阅读 v2.3.1 历史产物使用。新契约产物必须使用 v2.3.2 字段。

| 概念 / 类别 | v2.3.0 → v2.3.2 走向 | 说明 |
|---|---|---|
| 阶段 5 行主表的第 4 行文本 | 等待与返工 → 痛点 | 表头文本 |
| 阶段 5 行主表的第 5 行文本 | 风险节点 → 机会 | 表头文本 |
| 6b 节标题文本 | 关键断点与机会 → 痛点与机会 | 节标题 |
| 6a 质量维度英文键（旧） | 现键 = `pain_opportunity_visible`（统一应用） | quality data 字段 |
| 6a 质量维度中文标签（旧） | 现标签 = 痛点与机会可见（统一应用） | 标签文本 |
| 6b section id 类别（旧） | 现类别 = pain-opportunity 系列（统一应用） | section id |
| 6b 摘要锚点类别（旧） | 现类别 = pain-opportunity-summary 概念（统一应用） | 摘要锚点 |
| 阶段 5 行 DOM 子锚点类别（旧） | 现类别 = pain-point / opportunity 概念（统一应用） | DOM 子锚点 |
| stage data snake_case 字段（旧） | 现字段 = `pain_point` / `opportunity`（统一应用） | stage data 字段 |

> **迁移提示**：v2.3.1 历史渲染产物在阅读或迁移时使用对应的新字段名读写；在 audit 中 v2.3.0 字段不属于 v2.3.2 必填集合。

## 兼容性边界（v2.3.2 起）

> **核心规则**：旧 HTML 不做就地兼容；如需新语义，必须用新确认包重渲染。

### 明确不兼容旧产物

1. **旧 Journey HTML**：v2.3.1（含）之前的 `output/journey-canvas.html` 与 `user-journey-canvas.html` 不能直接复用为 v2.3.2 的渲染产物。旧 HTML 仍可阅读，但不应再通过 audit 必填检查。
2. **旧 JOURNEY-v{N}.md 确认包**：不得直接按新契约渲染；必须迁移为新版本或重新提炼（见 §迁移映射说明）。
3. **旧 JOURNEY-keypoints.md**：可作为背景输入，但 Stage 2（原子提炼）必须按新列头生成确认包。
4. **旧 canvas-data.stages[]**：`wait_rework` / `risk` 不再是 v2.3.2 必填字段；audit 一旦发现产物只含旧字段，将报 `JOURNEY-TPL-GATE-04` 并 FAIL。
5. **audit 脚本与契约一致性测试**：必须拒绝只含旧字段的 Journey HTML / canvas-data。已在 `tests/fixtures/journey/fault-cases.json` 中新增 `legacy_dom_anchors_rejected` / `legacy_quality_dimension_rejected` 两个 fixture 固化覆盖。

### 迁移映射说明（v2.3.1 → v2.3.2）

> 表中所有概念在 v2.3.2 PATCH 重构中已统一替换为同义的新概念；为防止审计反向白名单冲突，本节只描述"概念类别的走向"而不包含旧 anchor 字串。要查阅字串等价映射，使用代码级 anchor 列表（请读 audit `JOURNEY_*_FORBIDDEN_LIST` 等价的反向寄存器）。

| 概念 / 类别 | v2.3.1 → v2.3.2 走向 | 迁移要求 |
|---|---|---|
| 阶段 5 行主表第 4 行 | "等待与返工"文本 → "痛点" 文本 | 改写为"期望与现实落差导致的痛点"；保留行位置不变 |
| 阶段 5 行主表第 5 行 | "风险节点"文本 → "机会" 文本 | 只有从痛点导出改进方向时才写入；推断型机会登记 `JOURNEY-Infxx` |
| 6a 质量维度英文键（旧） | 现键 = `pain_opportunity_visible`（统一应用） | 维度名称变更；判定方法不变（基于 6b 痛点 / 机会条目是否被识别） |
| 6a 质量维度中文标签（旧） | 现标签 = "痛点与机会可见"（统一应用） | 标签沿用判定方法 |
| 6b section id 类别（旧） | 现类别 = pain-opportunity 系列（统一应用） | v2.3.2 起 6b 节属于 pain-opportunity 类别 |
| 6b 摘要锚点类别（旧） | 现类别 = pain-opportunity-summary 概念（统一应用） | 同上 |
| 6a 质量维度锚点（旧） | 现类 = pain-opportunity-visible 概念（统一应用） | 同上 |
| Gate 来源 ID（旧） | 现类 = `JOURNEY-pain-opportunity` | Journey Gate 的来源字段 |
| 阶段 DOM 子锚点（旧） | 现类 = pain-point / opportunity 概念（统一应用） | v2.3.2 期 HTML 内不出现旧子锚点即视为新契约 |
| stage data snake_case 字段（旧） | 现字段 = `pain_point` / `opportunity`（统一应用） | v2.3.2 起 audit 必填字段 |
| `JOURNEY-Fxx`（旧含义：断点 / 机会条目） | `JOURNEY-Fxx`（新含义：痛点 / 机会条目） | **ID 前缀保留**；其内部含义已切换，但迁移期不需要替换该前缀 |

### 验收：迁移后必须重新跑 journey-gate

> **不得沿用旧 Gate 结论**。迁移后的确认包必须重新跑：
> `python scripts/check_contract_consistency.py` 与 audit 必填检查，且 `journey-gate` 的 6 条放行条件（`JOURNEY-GATE-01` 至 `JOURNEY-GATE-06`）PASS 后方可视为新契约产物。

### 不在迁移范围内

- **`JOURNEY-Fxx` ID 前缀**：含义切换但前缀本身保留。
- **`state.schema.json` `schema_version`**：保持 2.3；现有 MVL / GC / HMW / Persona 业务结论无需迁移。
- **`plugin.json` `version` 之后字段**：v2.3.2 PATCH 已落，下次升 MINOR/MAJOR 时本节再行更新。
- **离线工作表 `internal/.../02-用户旅程画布.html`**：文案已切到新字段，但 worksheet 仍属设计参考，不进入运行时模板事实源；不参与 audit。

## 参考样例

- `internal/pratyaya-internal/docs/refs/canvas-templates/02-用户旅程画布.html`：内部静态 worksheet（设计参考，仅作视觉/语义映射参考，非运行时模板事实源）。
- `examples/user-journey-canvas.html`：User Journey 一等公民**版面与签名视觉事实源**（Template Gate 的比对模板）。

## 交付前自检

同 MVL / GC / HMW：Python 静态审计（`skills/canvas-render/scripts/audit_canvas_html.py --type journey`，正式交付追加 `--template skills/canvas-render/examples/user-journey-canvas.html` 触发双 Gate）+ 浏览器视觉验收。两阶段都通过后才把状态改为 `rendered`。
