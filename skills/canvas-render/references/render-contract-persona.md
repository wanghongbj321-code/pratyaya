# Persona Canvas 渲染契约

本契约定义 Persona Canvas HTML 的结构、锚点、数据映射与审计规则。LLM 读取 `PERSONA-{slug}-v{N}.md` 确认包后，按本契约将内容映射到 HTML 锚点。`{slug}` 必须等于 `state.json.persona.{slug}.slug`，正式输出为 `output/persona-canvas-{slug}.html`；`output/persona-canvas.html` 仅作为多 instance 索引页。

---

## 1. 页面结构

```html
<body data-mode="formal" data-page-type="persona" data-version="1" data-instance="{slug}">
  <header id="canvas-header">
    <h1>用户画像画布</h1>
    <div id="canvas-headline">一句话结论</div>
  </header>
  <main>
    <section id="persona-basic">
      <h2>基本信息</h2>
      <div id="persona-name">姓名</div>
      <div id="persona-gender">性别</div>
      <div id="persona-age">年龄</div>
      <div id="persona-location">所在地</div>
      <div id="persona-education">学历</div>
      <div id="persona-job-title">职位</div>
      <div id="persona-industry">行业</div>
      <div id="persona-family-status">家庭状况</div>
      <div id="persona-income">收入</div>
    </section>
    <section id="persona-grid6">
      <h2>六宫格</h2>
      <div id="persona-description">人物描述</div>
      <div id="persona-goals-needs">目标与需求</div>
      <div id="persona-behaviors">行为</div>
      <div id="persona-pain-points">痛点</div>
      <div id="persona-motivation">动机</div>
      <div id="persona-decision-factors">决策因素</div>
    </section>
    <section id="persona-quality">
      <h2>质量鉴别</h2>
      <div id="persona-quality-evidence">有证据</div>
      <div id="persona-quality-concrete">具体</div>
      <div id="persona-quality-voice">用户原话</div>
      <div id="persona-quality-representative">代表性</div>
    </section>
  </main>
  <aside id="quality-panel">
    <h3>质量与对齐</h3>
    <div id="quality-version">v{N}</div>
    <div id="quality-approval">
      <!-- gate_recommendation / render_authorized / confirmation_mode -->
    </div>
    <div id="quality-gaps">缺口摘要</div>
    <div id="quality-risks">风险摘要</div>
    <div id="quality-caveat" hidden>
      <!-- 仅 override 时显示 -->
    </div>
  </aside>
  <section id="local-notes" contenteditable="true">...</section>
  <script type="application/json" id="canvas-data">
    {
      "version": "v{N}",
      "instance": "{slug}",
      "canvas_type": "persona",
      "sections": { ...确认包 section 映射... },
      "auth": {
        "gate_recommendation": "pass | fail",
        "render_authorized": true,
        "confirmation_mode": "gate_pass | override",
        "override_audit": { ... }
      }
    }
  </script>
</body>
```

---

## 2. 锚点映射表

| HTML 锚点 | 确认包 section | 说明 |
|---|---|---|
| `canvas-headline` | 第 1 节：一句话结论 | 画像核心主张 |
| `persona-name` | 第 6 节：name | 姓名 |
| `persona-gender` | 第 6 节：gender | 性别 |
| `persona-age` | 第 6 节：age | 年龄 |
| `persona-location` | 第 6 节：location | 所在地 |
| `persona-education` | 第 6 节：education | 学历 |
| `persona-job-title` | 第 6 节：job_title | 职位 |
| `persona-industry` | 第 6 节：industry | 行业 |
| `persona-family-status` | 第 6 节：family_status | 家庭状况 |
| `persona-income` | 第 6 节：income | 收入 |
| `persona-description` | 第 6 节：description | 人物描述 |
| `persona-goals-needs` | 第 6 节：goals_needs | 目标与需求 |
| `persona-behaviors` | 第 6 节：behaviors | 行为 |
| `persona-pain-points` | 第 6 节：pain_points | 痛点 |
| `persona-motivation` | 第 6 节：motivation | 动机 |
| `persona-decision-factors` | 第 6 节：decision_factors | 决策因素 |
| `persona-quality-evidence` | 第 6a 节：evidence_based | 有证据 |
| `persona-quality-concrete` | 第 6a 节：concrete | 具体 |
| `persona-quality-voice` | 第 6a 节：pain_in_voice | 用户原话 |
| `persona-quality-representative` | 第 6a 节：representative | 代表性 |
| `quality-panel` | 第 12 节：治理元数据 | 质量与对齐面板 |
| `local-notes` | — | 本地批注（用户编辑） |
| `canvas-data` | — | 内嵌 JSON 数据 |

---

## 3. 数据映射规则

### 3.1 基本信息与六宫格

- **已讨论**：正常展示内容
- **未讨论**：显示"未讨论"并标为缺口（`data-state="gap"`）

### 3.2 质量鉴别

- **通过**：显示"通过"+ 依据
- **不通过**：显示"不通过"+ 依据
- **未判定**：显示"未判定"并标为缺口

质量鉴别的判定与依据必须来自 `PERSONA-{slug}-v{N}.md` 第 6a 节，不由 canvas-render 推断。

### 3.3 治理面板

- `gate_recommendation`：pass / fail / pending
- `render_authorized`：true / false
- `confirmation_mode`：gate_pass / override
- `override_audit`：仅 override 时存在

### 3.4 Caveat 状态

- `confirmation_mode=gate_pass`：显示"已确认"
- `confirmation_mode=override`：显示"**已确认 · 带保留意见**"，`quality-caveat` 显示

---

## 4. 一级模块顺序（Template Gate）

```text
canvas-header
  → persona-basic
  → persona-grid6
  → persona-quality
  → quality-panel
  → local-notes
  → canvas-data
```

任一一级模块缺失、重复或顺序偏离，Template Gate FAIL。

---

## 5. 稳定锚点集合（Template Gate）

- 页面：`data-page-type="persona"`
- 基本信息 9 字段：`persona-name` / `persona-gender` / `persona-age` / `persona-location` / `persona-education` / `persona-job-title` / `persona-industry` / `persona-family-status` / `persona-income`
- 六宫格 6 区：`persona-description` / `persona-goals-needs` / `persona-behaviors` / `persona-pain-points` / `persona-motivation` / `persona-decision-factors`
- 质量 4 维度：`persona-quality-evidence` / `persona-quality-concrete` / `persona-quality-voice` / `persona-quality-representative`
- 治理面板：`quality-panel` 含 `quality-version` / `quality-approval` / `quality-gaps` / `quality-risks` / `quality-caveat`
- 批注与数据：`local-notes` / `canvas-data`

---

## 6. Template Gate 稳定规则

## 7. 隐藏检测

| ID | 检查项 |
|---|---|
| `PERSONA-TPL-GATE-01` | 页面 `data-page-type="persona"` 且与模板一致 |
| `PERSONA-TPL-GATE-02` | 一级模块存在且唯一 |
| `PERSONA-TPL-GATE-03` | 一级模块顺序符合本契约 §4 |
| `PERSONA-TPL-GATE-04` | 9 基本信息、6 宫格、4 质量锚点完整 |
| `PERSONA-TPL-GATE-05` | `quality-panel` 治理插槽完整 |
| `PERSONA-TPL-GATE-06` | 离线共享主题（正式产物须内联，禁止依赖本地相对路径外链 CSS）、窄屏、打印与关键模块可见 |

以上规则不可 override。

质量鉴别（`persona-quality`）与治理面板（`quality-panel`）不得隐藏。四种隐藏方式任一命中即 FAIL：

1. `hidden` HTML 属性
2. `style="display:none"`
3. `style="visibility:hidden"`
4. `class="hidden"`

---

## 8. 本地离线约束

- **CSS / JavaScript / 字体必须内联或使用系统字体；正式产物禁止依赖本地相对路径外链 CSS**（如 `<link rel="stylesheet" href="shared/canvas-theme.css">`）。方案 A（2026-08-09）已把示例模板主题内联，成品须与其一致
- 禁止通过 `fetch("file.json")` 加载本地数据
- 禁止用 iframe 打开兄弟 HTML
- **成品 HTML 必须单文件自包含（CSS 内联），独立传播时无需任何伴随文件**；无网络时仍可展开、筛选、打印和编辑

---

## 9. 数据完整性

- `data-version` 必须等于确认包版本 `v{N}`
- `canvas-data.auth` 必须与 `state.json.persona.{slug}` 一致
- `body[data-instance]`、`canvas-data.instance`、确认包文件名 `{slug}` 与 `state.json.persona.{slug}.slug` 必须一致
- 结论 ID（`PERSONA-Cxx`）、缺口 ID（`PERSONA-Gxx`）与确认包一致

---

## 10. 打印与管理层阅读

- `@media print` 隐藏编辑控件
- 保留版本、确认、风险状态、结论与 override caveat
- override 画布必须保留 caveat 标识

---

## 11. 参考样例

- `examples/user-persona-canvas.html`：Persona 一等公民版面与签名视觉事实源

---

## 12. 交付前自检

```bash
python skills/canvas-render/scripts/audit_canvas_html.py output/persona-canvas-{slug}.html \
  --source modules/PERSONA-{slug}-v{N}.md \
  --state state.json \
  --type persona \
  --instance {slug} \
  --template skills/canvas-render/examples/user-persona-canvas.html
```

Template Gate 通过后才可交付。
