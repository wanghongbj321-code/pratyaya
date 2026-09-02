# 5W Canvas HTML 实现契约

本契约定义 5W（Five Whys，根因分析）Canvas 页面的 HTML 结构。

数据源是 `modules/5W-{slug}-v{N}.md`（确认包，Markdown）；LLM 读取后按本章的 section 映射表，把内容映射到 HTML 锚点。映射的字段名沿用确认包 Markdown 的 section 标题。`{slug}` 必须等于 `state.json.five_whys.{slug}.slug`，正式输出为 `output/5w-canvas-{slug}.html`；`output/5w-canvas.html` 仅作为多 instance 索引页。

## A. 5W Canvas 页面结构

```html
<body data-mode="formal" data-page-type="5w" data-version="1" data-instance="{slug}">
  <header id="canvas-header">
    <h1>5W 五个为什么 Five Whys Canvas</h1>
    <div id="canvas-headline">一句话结论</div>
  </header>
  <main>
    <section id="5w-problem">
      <h2>① 问题陈述</h2>
      <div id="5w-problem-statement">事实陈述（一句话，非结论）</div>
      <div id="5w-problem-meta">发生日期 / 影响频次 / 参与者</div>
    </section>
    <section id="5w-chain">
      <h2>② 五层因果链（三层面：直接原因 → 漏检缺口 → 系统缺陷）</h2>
      <div id="5w-why-1">Why 1：追问句式 + 答案 + 证据 + 合格检查点</div>
      <div id="5w-why-2">Why 2：…</div>
      <div id="5w-why-3">Why 3：…</div>
      <div id="5w-why-4">Why 4：…</div>
      <div id="5w-why-5">Why 5：…</div>
    </section>
    <section id="5w-root">
      <h2>③ 根本原因</h2>
      <div id="5w-root-cause">根本原因</div>
      <div id="5w-root-check">停止准则「因此」检验</div>
    </section>
    <section id="5w-countermeasures">
      <h2>④ 对策与行动</h2>
      <div id="5w-countermeasure">对策（预防性回应）</div>
      <div id="5w-owner">负责人</div>
      <div id="5w-due">截止日期</div>
      <div id="5w-verify">如何验证有效</div>
    </section>
    <section id="5w-branches">
      <h2>⑤ 其他原因分支</h2>
      <div id="5w-branches-list">未追踪分支（复发时首选线索）</div>
    </section>
    <section id="5w-rubric">
      <h2>⑥ 判别记录（坏答案 vs 好答案）</h2>
      <div id="5w-rubric-table">工作坊实际判别的坏答案 / 好答案对照</div>
    </section>
  </main>
  <aside id="quality-panel">
    <h3>质量与对齐</h3>
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
      "instance": "{slug}",
      "canvas_type": "5w",
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
| `5w-problem-statement` | 6：statement（事实陈述） |
| `5w-problem-meta` | 6：occurred_at / impact_frequency / participants |
| `5w-why-1` … `5w-why-5` | 7：因果链五层（每层含层面 / 追问对象 / 答案 / 证据 / 检查点） |
| `5w-root-cause` | 8：root_cause |
| `5w-root-check` | 8：so_therefore（"因此"检验链）+ stop_check |
| `5w-countermeasure` | 9：countermeasure |
| `5w-owner` | 9：owner |
| `5w-due` | 9：due_date |
| `5w-verify` | 9：verify |
| `5w-branches-list` | 10：其他原因分支 |
| `5w-rubric-table` | 11：判别记录 |

**关键规则**：

- 已讨论的字段正常展示内容；未讨论的字段显示"未讨论"并标为缺口。
- `5w-why-*` 的数据源为 `5W-{slug}-v{N}.md` 第 7 节，不由 canvas-render 推断。
- 五层锚点 `5w-why-1` … `5w-why-5` **必须全部存在**（对齐 5 层固定结构，层数弹性暂不支持）；未讨论层渲染为占位（显示"未讨论"或空卡片），但**锚点必须存在**。
- 版面签名视觉：A3 横版 + 黑灰单配色 + 1–5 卡片横向并排 + 层间 `→` 箭头，以 `examples/5w-canvas.html` 为准。
- 5W Canvas 是独立一等公民画布；同一 group 可有多个 instance，不存在子模块详情页和全局汇总页。

## 共享结构

与 MVL / GC Canvas 共享 quality-panel、local-notes、canvas-data 结构（见 `render-contract.md`）。差异：

- `data-page-type` 为 `5w`（非 `global` / `module-detail` / `golden-circle`）。
- 无 `data-module` 属性。
- `canvas-data.module` 字段替换为 `canvas-data.canvas_type: "5w"`。
- `canvas-data.auth` 字段对应 `state.json.five_whys.{slug}`，且 `canvas-data.instance` 必须等于同一 `{slug}`。

### Caveat 状态标识

与 MVL / GC 一致：
- `confirmation_mode=gate_pass`：显示"已确认"。
- `confirmation_mode=override`：显示"**已确认 · 带保留意见**"。

## 本地离线约束

- **CSS、JavaScript、图标和字体必须内联或使用系统字体；正式产物禁止依赖本地相对路径外链 CSS**（如 `<link rel="stylesheet" href="shared/canvas-theme.css">`）。方案 A（2026-08-09）已把示例模板主题内联，成品须与其一致。
- 禁止通过 `fetch("file.json")` 加载本地数据。
- 禁止用 iframe 打开兄弟 HTML；使用普通相对链接。
- **成品 HTML 必须单文件自包含（CSS 内联），独立传播时无需任何伴随文件**；无网络时仍可展开、筛选、打印和编辑。

## 数据完整性

- 输出页的 `data-version` 必须等于确认包版本 `v{N}`。
- 页面内嵌数据必须来自同一次读取。
- 结论 ID、缺口 ID 与确认包 Markdown 保持一致。
- `canvas-data` 的 `auth` 字段必须与 `state.json.five_whys.{slug}` 完全一致。
- `body[data-instance]`、`canvas-data.instance`、确认包文件名 `{slug}` 与 `state.json.five_whys.{slug}.slug` 必须一致。

## 模板结构 Profile（Template Gate 判定依据）

Template Gate（`audit_canvas_html.py --template skills/canvas-render/examples/5w-canvas.html --type 5w --instance {slug}`）以本 profile 为判定依据，比较成品与模板的一级模块、稳定锚点与相对 DOM 顺序。**不比较**占位文本、业务文案、动态版本值或 CSS 逐字符内容。

### 一级模块必需性与 DOM 相对顺序（强制）

```text
canvas-header
  → 5w-problem
  → 5w-chain
  → 5w-root
  → 5w-countermeasures
  → 5w-branches
  → 5w-rubric
  → quality-panel
  → local-notes
  → canvas-data
```

> **顺序依据**：以 `examples/5w-canvas.html` 模板实际 DOM 顺序为准（问题陈述 → 因果链 → 根因 → 对策 → 其他分支 → 判别记录，自上而下；治理面板与批注收尾）。Template Gate 以本 profile 与模板为比对基准。

任一一级模块缺失、重复或相对顺序偏离本 profile，Template Gate FAIL（`5W-TPL-GATE-02` / `5W-TPL-GATE-03`）。

### 稳定锚点集合（Template Gate 校验）

- 页面：`data-page-type="5w"`（`5W-TPL-GATE-01`）
- 问题陈述：`5w-problem-statement` / `5w-problem-meta`（`5W-TPL-GATE-04`）
- 因果链五层：`5w-why-1` / `5w-why-2` / `5w-why-3` / `5w-why-4` / `5w-why-5`（锚点不可缺失；未讨论层用 `data-state="placeholder"`）（`5W-TPL-GATE-04`）
- 根因：`5w-root-cause` / `5w-root-check`（`5W-TPL-GATE-04`）
- 对策四要素：`5w-countermeasure` / `5w-owner` / `5w-due` / `5w-verify`（`5W-TPL-GATE-04`）
- 其他分支：`5w-branches-list`（`5W-TPL-GATE-04`）
- 判别记录：`5w-rubric-table`（`5W-TPL-GATE-04`）
- 治理面板：`quality-panel` 含 `quality-version` / `quality-approval` / `quality-gaps` / `quality-risks` / `quality-caveat` 插槽（`5W-TPL-GATE-05`）
- 批注与数据：`local-notes`、`canvas-data`（`5W-TPL-GATE-02`）
- 共享主题（**内联 `<style>` 或本地 `<link>` 均可，正式产物须内联、禁止依赖本地相对路径外链 CSS**）/ 窄屏布局（5 卡片窄屏回退纵向），无外部网络依赖（`5W-TPL-GATE-06`）

### 隐藏检测（Template Gate 与内容/授权 Gate 共用）

判别记录（`5w-rubric`）与治理面板（`quality-panel`）不得以任何方式隐藏。四种隐藏方式任一命中即 FAIL：

1. `hidden` HTML 属性（`hidden` 属性存在）
2. `style="display:none"` 或计算后 `display` 为 `none`
3. `style="visibility:hidden"` 或计算后 `visibility` 为 `hidden`
4. `class="hidden"`（约定 `.hidden { display:none; }`）

> 例外：`quality-caveat` 治理插槽允许 `hidden`（仅 override 时显示），此为本契约显式豁免。

### 参考样例

- `internal/pratyaya-internal/docs/refs/canvas-templates/06-5W画布.html`：离线工作表原型（A3 横版 + 1–5 卡片横向并排 + 三层面标注 + 页脚三条红线；双产物模型的"离线工作表"，不走 audit 门禁，仅作视觉/语义映射参考，非运行时模板事实源）。
- `examples/5w-canvas.html`：5W 一等公民**版面与签名视觉事实源**（Template Gate 的比对模板，契约化自 06 原型）。

## 交付前自检

同 MVL / GC：Python 静态审计（`skills/canvas-render/scripts/audit_canvas_html.py --type 5w --instance {slug}`，正式交付追加 `--template skills/canvas-render/examples/5w-canvas.html` 触发双 Gate）+ 浏览器视觉验收。两阶段都通过后才把当前 instance 状态改为 `rendered`。

审计命令示例：

```bash
# 5W 正式画布审计（含 Template Gate，需 --template）
python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/5w-canvas-{slug}.html \
  --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/5W-{slug}-v{N}.md \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json \
  --type 5w \
  --instance {slug} \
  --template skills/canvas-render/examples/5w-canvas.html

# 5W 索引页审计
python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/5w-canvas.html \
  --type 5w --index \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json

# 5W 草稿审计（无正式授权元数据）
python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/5w-canvas-{slug}.html \
  --type 5w
```
