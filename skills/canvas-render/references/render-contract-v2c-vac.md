# V2C VAC Canvas HTML 实现契约

本契约定义 V2C Value Attribution Canvas（VAC，价值归因画布）正式 HTML 的结构、锚点、数据映射与审计规则。LLM 读取 `modules/V2C-VAC-{slug}-v{N}.md` 确认包后，按本契约将内容映射到 HTML 锚点。`{slug}` 必须等于 `state.json.v2c_vac.{slug}.slug`。

V2C VAC 的思路来源于王鸿的 V2C FDE 工作方法论。Canvas 展示的是 Value-to-Capability 主线在具体业务观察场景中的价值归因假设，不是价值证明页。

正式输出为 `output/v2c-vac-canvas-{slug}--v{N}.html`；索引页为 `output/v2c-vac-canvas.html`，`page_type = v2c-vac-index`。

## 1. 页面结构

```html
<body data-mode="formal" data-page-type="v2c-vac" data-version="v{N}" data-instance="{slug}">
  <header id="canvas-header">
    <h1>V2C Value Attribution Canvas</h1>
    <div id="v2c-vac-headline">一句话归因假设</div>
    <div id="v2c-vac-summary">主链摘要</div>
  </header>
  <main id="v2c-vac-canvas">
    <section id="v2c-vac-attribution-chain">
      <div id="v2c-vac-scenario">Scenario</div>
      <div id="v2c-vac-capability">Capability</div>
      <div id="v2c-vac-change">Change</div>
      <div id="v2c-vac-business-impact">Business Impact</div>
      <div id="v2c-vac-value">Value</div>
    </section>
    <section id="v2c-vac-attribution-gaps">Attribution Assumptions & Gaps</section>
    <section id="v2c-vac-quality-check">Attribution Quality Check</section>
    <section id="v2c-vac-inferences">推断表</section>
  </main>
  <aside id="quality-panel">
    <div id="quality-version">v{N}</div>
    <div id="quality-approval">gate / auth</div>
    <div id="quality-gaps">缺口摘要</div>
    <div id="quality-risks">风险摘要</div>
    <div id="quality-caveat" hidden>override caveat</div>
  </aside>
  <section id="local-notes" contenteditable="true">本地批注</section>
  <script type="application/json" id="canvas-data">
    {
      "version": "v{N}",
      "instance": "{slug}",
      "canvas_type": "v2c-vac",
      "page_type": "v2c-vac",
      "generation_path": "pipeline | transcript-direct",
      "source_file": "modules/V2C-VAC-{slug}-v{N}.md",
      "sections": {},
      "auth": {
        "gate_recommendation": "pass | fail",
        "render_authorized": true,
        "confirmation_mode": "gate_pass | override",
        "override_audit": {}
      }
    }
  </script>
</body>
```

## 2. 锚点映射表

| HTML 锚点 | 确认包 section | 说明 |
|---|---|---|
| `v2c-vac-headline` | 必展项 1：一句话归因假设 | 必须使用“可能贡献于”等谨慎归因表达 |
| `v2c-vac-summary` | 必展项 2：主链摘要 | Scenario / Primary Capability / Primary Change / Business Impact / Value |
| `v2c-vac-key-gaps` | 必展项 3：关键断点速览 | 关键 `V2C-AGxx` 与验证计划 |
| `v2c-vac-next-step` | 必展项 4：下一步建议 | Proceed / Explore / Defer / Stop + 理由 |
| `v2c-vac-scenario` | 第 5 节：Scenario | 关键用户 / 角色、工作情境、当前事实、范围边界 |
| `v2c-vac-capability` | 第 6 节：Capability | Primary AI-enabled Capability 与 Secondary Capabilities |
| `v2c-vac-primary-capability` | 第 6 节：Primary Capability | 主能力定义、作用对象、可用标准 |
| `v2c-vac-secondary-capabilities` | 第 6 节：Secondary Capabilities | 有明确作用假设的辅助能力 |
| `v2c-vac-change` | 第 7 节：Change | Primary Change 与 Other Observed Changes |
| `v2c-vac-primary-change` | 第 7 节：Primary Change | 进入主链的唯一 Primary Change |
| `v2c-vac-other-changes` | 第 7 节：Other Observed Changes | 记录但默认不连入主链 |
| `v2c-vac-business-impact` | 第 8 节：Business Impact Chain | 从 Primary Change 出发的一条业务影响链 |
| `v2c-vac-impact-chain` | 第 8 节：Impact 节点 | 近端影响、Value Driver、指标候选 |
| `v2c-vac-value` | 第 9 节：Value | Primary Value Anchor、Outcome Metric、Baseline、Actual、Confounders |
| `v2c-vac-value-anchor` | 第 9 节：Primary Value Anchor | 最终经营价值锚点 |
| `v2c-vac-measurement` | 第 9 节：指标 / Baseline / Actual | KPI 只作为测量证据，不作为因果节点 |
| `v2c-vac-attribution-gaps` | 第 10 节：Attribution Assumptions & Gaps | 全量归因断点 |
| `v2c-vac-gap-V2C-AG01` ... `v2c-vac-gap-V2C-AG06` | 第 10 节默认 Attribution Gap | 默认六类断点；若确认包无对应项，显示“未登记”并触发审计风险 |
| `v2c-vac-quality-check` | 第 11 节：Attribution Quality Check | semantics / honesty / verifiability / next_step |
| `v2c-vac-quality-semantics` | 第 11 节：semantics | 语义分层是否正确 |
| `v2c-vac-quality-honesty` | 第 11 节：honesty | 是否保留未知关系 |
| `v2c-vac-quality-verifiability` | 第 11 节：verifiability | 是否可验证 |
| `v2c-vac-quality-next-step` | 第 11 节：next_step | 下一步投入判断 |
| `v2c-vac-inferences` | 第 12 节：推断表 | `V2C-Infxx` 推断 |
| `quality-panel` | 第 13 节：Gate 与用户决策 + state | 治理面板 |
| `quality-version` | 第 13 节 + state | 当前确认包版本 |
| `quality-approval` | 第 13 节 + state | gate_recommendation / render_authorized / confirmation_mode |
| `quality-gaps` | 第 10 / 13 节 | blocker / major / minor 缺口摘要 |
| `quality-risks` | 第 13 节 | Gate 风险摘要 |
| `quality-caveat` | 第 13 节：Override 审计 | 仅 `confirmation_mode=override` 时显示 |
| `local-notes` | — | 本地批注，不得覆盖确认包 |
| `canvas-data` | — | 内嵌 JSON 数据 |

## 3. 数据映射规则

### 3.1 内容来源

- 正式页面内容只能来自 `modules/V2C-VAC-{slug}-v{N}.md`。
- 不读取逐字稿、Key Points 或阶段产物作为正式页面事实源。
- 未讨论字段显示“未讨论”或“待确认”，并标 `data-state="gap"`。
- 不为了视觉完整补齐因果链。

### 3.2 证据状态

V2C VAC 必须外显 `F / H / ? / E`：

| 状态 | 展示规则 |
|---|---|
| `F` | 标记为 Fact，有当前项目来源线索 |
| `H` | 标记为 Hypothesis，并显示验证计划或风险说明 |
| `?` | 标记为 Gap，必须关联 `V2C-AGxx` 或推断表 |
| `E` | 标记为 Evidence-supported，必须有 Pilot / 数据 / 观察 / 对照验证说明 |

估算、行业基准或外部材料若未在当前项目验证，不得标为 `E`。

### 3.3 归因链展示

- 视觉主链必须按 `Scenario -> Capability -> Change -> Business Impact -> Value` 排布。
- 允许多个 Capability 汇聚到一个 Primary Change。
- 允许多个 Other Observed Changes 被记录，但不得连入主 Business Impact Chain。
- 一张 V2C VAC 只允许一个 Primary Change 进入一条 Business Impact Chain。
- KPI / Measure 附着在 Change / Impact / Value 节点旁，只作为测量证据，不作为因果节点。

### 3.4 治理面板

- `canvas-data.auth` 必须与 `state.json.v2c_vac.{slug}` 一致。
- `confirmation_mode=gate_pass`：显示“已确认”。
- `confirmation_mode=override`：显示“已确认 · 带保留意见”，`quality-caveat` 必须可见。
- `override_audit.items[].assessment_id` 必须匹配 `^V2C-GATE-[0-9]+$`，且 `category=business_risk`。
- `V2C-AGxx` 只能作为来源 ID 或缺口 ID，不得作为 `override_audit.assessment_id`。

## 4. 页面与输出

### 4.1 正式详情页

- `canvas_type = v2c-vac`
- `data-page-type="v2c-vac"`
- `canvas-data.canvas_type = "v2c-vac"`
- `canvas-data.page_type = "v2c-vac"`
- 输出：`output/v2c-vac-canvas-{slug}--v{N}.html`
- 示例模板：`skills/canvas-render/examples/v2c-value-attribution-canvas.html`

### 4.2 索引页

- `page_type = v2c-vac-index`
- `data-page-type="v2c-vac-index"`
- `canvas-data.canvas_type = "v2c-vac"`
- `canvas-data.page_type = "v2c-vac-index"`
- 输出：`output/v2c-vac-canvas.html`
- 输入为 `state.v2c_vac` 的全部 instance map，不读取转写，不重新渲染详情页。
- 按 slug 字典序列出每个 instance 的 slug、version、status、gate_recommendation、updated_at 与详情页链接 `output/v2c-vac-canvas-{slug}--v{N}.html`。

## 5. 一级模块顺序（Template Gate）

```text
canvas-header
  -> v2c-vac-canvas
  -> v2c-vac-attribution-chain
  -> v2c-vac-attribution-gaps
  -> v2c-vac-quality-check
  -> v2c-vac-inferences
  -> quality-panel
  -> local-notes
  -> canvas-data
```

任一一级模块缺失、重复或相对顺序偏离，Template Gate FAIL。

## 6. 稳定锚点集合（Template Gate）

- 页面：`data-page-type="v2c-vac"`。
- 头部：`canvas-header` / `v2c-vac-headline` / `v2c-vac-summary` / `v2c-vac-key-gaps` / `v2c-vac-next-step`。
- 主链：`v2c-vac-attribution-chain` / `v2c-vac-scenario` / `v2c-vac-capability` / `v2c-vac-primary-capability` / `v2c-vac-secondary-capabilities` / `v2c-vac-change` / `v2c-vac-primary-change` / `v2c-vac-other-changes` / `v2c-vac-business-impact` / `v2c-vac-impact-chain` / `v2c-vac-value` / `v2c-vac-value-anchor` / `v2c-vac-measurement`。
- 缺口：`v2c-vac-attribution-gaps` / `v2c-vac-gap-V2C-AG01` / `v2c-vac-gap-V2C-AG02` / `v2c-vac-gap-V2C-AG03` / `v2c-vac-gap-V2C-AG04` / `v2c-vac-gap-V2C-AG05` / `v2c-vac-gap-V2C-AG06`。
- 质量：`v2c-vac-quality-check` / `v2c-vac-quality-semantics` / `v2c-vac-quality-honesty` / `v2c-vac-quality-verifiability` / `v2c-vac-quality-next-step`。
- 推断：`v2c-vac-inferences`。
- 治理：`quality-panel` 含 `quality-version` / `quality-approval` / `quality-gaps` / `quality-risks` / `quality-caveat`。
- 批注与数据：`local-notes` / `canvas-data`。

## 7. Template Gate 稳定规则

| ID | 检查项 |
|---|---|
| `V2C-VAC-TPL-GATE-01` | 页面 `data-page-type="v2c-vac"` 且 `canvas-data.canvas_type="v2c-vac"` |
| `V2C-VAC-TPL-GATE-02` | 一级模块存在且唯一 |
| `V2C-VAC-TPL-GATE-03` | 一级模块顺序符合本契约 §5 |
| `V2C-VAC-TPL-GATE-04` | 主链五层锚点完整，且稳定锚点使用 `v2c-vac-*` 前缀 |
| `V2C-VAC-TPL-GATE-05` | 默认六类 Attribution Gap 锚点完整 |
| `V2C-VAC-TPL-GATE-06` | 治理面板、批注区与 `canvas-data` 完整 |
| `V2C-VAC-TPL-GATE-07` | 正式产物单文件自包含，无外部 CSS / JS / 字体 / fetch / iframe |
| `V2C-VAC-TPL-GATE-08` | A3 landscape 基准与黑灰视觉结构保留 |

以上规则不可 override。

## 8. 隐藏检测

以下模块不得隐藏：

- `v2c-vac-attribution-chain`
- `v2c-vac-attribution-gaps`
- `v2c-vac-quality-check`
- `v2c-vac-inferences`
- `quality-panel`

四种隐藏方式任一命中即 FAIL：

1. `hidden` HTML 属性
2. `style="display:none"`
3. `style="visibility:hidden"`
4. `class="hidden"`

`quality-caveat` 是唯一允许默认 `hidden` 的治理插槽；当 `confirmation_mode=override` 时必须可见。

## 9. 本地离线约束

- CSS、JavaScript、图标和字体必须内联或使用系统字体。
- 正式产物禁止依赖本地相对路径外链 CSS。
- 禁止通过 `fetch("file.json")` 加载本地数据。
- 禁止用 iframe 打开兄弟 HTML。
- 成品 HTML 必须单文件自包含，独立传播时无需任何伴随文件。
- 无网络时仍可打印、展开和编辑本地批注。

## 10. 数据完整性

- `data-version` 必须等于确认包版本 `v{N}`。
- `body[data-instance]`、`canvas-data.instance`、确认包文件名 `{slug}` 与 `state.json.v2c_vac.{slug}.slug` 必须一致。
- `canvas-data.source_file` 必须指向同版本确认包。
- `canvas-data.generation_path` 必须为 `pipeline` 或 `transcript-direct`。
- `canvas-data.auth` 必须与 `state.json.v2c_vac.{slug}` 一致。
- 结论 ID、缺口 ID、推断 ID 与确认包 Markdown 保持一致。

## 11. 参考样例

- `internal/pratyaya-internal/docs/refs/V2C-Value-Attribution-Canvas-template-v1.2.html`：内部静态 worksheet（设计参考，仅作视觉/语义映射参考，非运行时模板事实源）。
- `examples/v2c-value-attribution-canvas.html`：V2C VAC 一等公民版面与签名视觉事实源。

## 12. 交付前自检

```bash
python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/v2c-vac-canvas-{slug}--v{N}.html \
  --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/V2C-VAC-{slug}-v{N}.md \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json \
  --type v2c-vac \
  --instance {slug} \
  --template skills/canvas-render/examples/v2c-value-attribution-canvas.html
```

Python 静态审计 + 浏览器视觉验收都通过后，主 Agent 才能把当前 instance 状态标记为 `rendered`。任一阶段失败时，状态保持 `confirmed`。
