# Canvas HTML 实现契约

## 页面最小结构

```html
<body data-mode="formal" data-module="M1" data-version="3">
  <header id="canvas-header">...</header>
  <main>
    <section id="intent">
      <div id="intent-goal">...</div>
      <div id="intent-value">...</div>
      <div id="intent-success-metrics">...</div>
    </section>
    <section id="user">
      <div id="user-users">...</div>
      <div id="user-needs">...</div>
      <div id="user-pain-points">...</div>
      <div id="user-most-important-outcomes">...</div>
    </section>
    <section id="agent-team">
      <div id="agent-team-roles">...</div>
      <div id="agent-team-collaboration">...</div>
    </section>
    <section id="workflow">
      <div id="workflow-steps">...</div>
      <div id="workflow-automation">...</div>
      <div id="workflow-human-checkpoints">...</div>
      <div id="workflow-human-agent-nodes">...</div>
      <div id="workflow-rules">...</div>
    </section>
    <section id="context">
      <div id="context-knowledge">...</div>
      <div id="context-data-sources">...</div>
      <div id="context-tools-skills">...</div>
    </section>
    <section id="validation">
      <div id="validation-executable">...</div>
      <div id="validation-value">...</div>
      <div id="validation-evolution">...</div>
    </section>
  </main>
  <aside id="quality-panel">
    <h3>质量与对齐</h3>
    <div id="quality-version">...</div>
    <div id="quality-approval">...</div>
    <div id="quality-gaps">...</div>
    <div id="quality-risks">...</div>
    <section id="alignment-section">
      <h4>对齐状态</h4>
      <div id="alignment-consensus">...</div>
      <div id="alignment-divergences">...</div>
      <div id="alignment-decisions">...</div>
    </section>
  </aside>
  <section id="local-notes" contenteditable="true">...</section>
  <script type="application/json" id="canvas-data">...</script>
</body>
```

正式页面至少展示：

- 模块、项目和小组；
- 一句话结论；
- 当前版本、确认人、确认时间；
- 结论数量与证据覆盖；
- 未关闭 minor 缺口与已接受风险；
- 模块框架规定的业务字段；
- 可展开的结论登记表和证据摘要；
- “POC / 非生产建议”声明（如仍处验证阶段）。

## 本地离线约束

- CSS、JavaScript、图标和字体优先内联或使用系统字体。
- 禁止通过 `fetch("file.json")` 加载本地数据；浏览器会因 file origin 拦截。
- 禁止用 iframe 打开兄弟 HTML；使用普通相对链接。
- 所有交互在单文件内工作，无网络时仍可展开、筛选、打印和编辑。
- 可编辑字段保存到浏览器 `localStorage` 时，必须标记为“本地批注”，不能覆盖已确认事实源。

## 数据完整性

- 输出页的 `data-version` 必须等于模块记录版本。
- 页面内嵌数据必须来自同一次读取，不允许手工复制后再改写。
- HTML 中的结论 ID、缺口 ID、证据引用与 JSON 保持一致。
- 内容变更后必须升版，并把状态退回 `draft` 或 `gaps_open`；旧 HTML 视为过期。

## 全局下钻

全局 Canvas 的板块使用普通链接，例如：

```html
<a href="./module-1-canvas.html#conclusion-M1-C01">查看 M1 依据</a>
```

不要使用 iframe。这样既避免 `file:` 唯一安全源问题，也允许用户本地双击打开。

## 打印与管理层阅读

- `@media print` 隐藏编辑控件，保留版本、确认和风险状态。
- 结论与关键指标优先，证据细节折叠但可打印附录。
- `blocker` 和 `major` 不应出现在正式页面；若历史记录需要展示，明确标记“已解决”及证据。

## 交付前审计

```powershell
python skills/canvas-render/scripts/audit_canvas_html.py output/module-1-canvas.html
```

审计必须确认：六大模块及规定小模块锚点齐全、质量面板与本地批注存在、同版本 JSON 已内嵌、包含打印规则，并且没有 iframe、`fetch()` 或外部网络资源。退出码 `0` 表示结构与离线安全检查通过；它不替代人工浏览器预览。
