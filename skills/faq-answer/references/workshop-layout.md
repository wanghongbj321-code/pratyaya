# 工作坊目录结构与文件语义

> 本文件由主 Agent（`agents/pratyaya.md`）下沉而来，是目录树与文件语义的**完整版事实源**。
> 主 Agent 只保留骨架 + 3 条不变式；需要完整清单时（如排查路径问题）读取本文件。

## 状态目录

```text
workshop/{project_slug}/
├── manifest.json                   # project 级派生视图：groups + topics 嵌套（从各 topic state.json 重建）
└── {group_id}/                     # group 目录；kebab-case ASCII
    ├── group_meta.json              # group 显示元数据（group_name / group_lead / contact / created_at / created_by）
    ├── manifest.json                # group 级派生视图：当前 group 的 topics 汇总（从 */state.json 重建）
    └── {topic_slug}/               # 当前 topic 工作目录；kebab-case ASCII
        ├── topic_meta.json          # topic 显示元数据（topic_name / topic_owner / contact / created_at / created_by）
        ├── state.json               # topic 状态（project_slug / group_id / topic_slug 与目录名一致）
        ├── transcripts/
        │   ├── manifest.json
        │   ├── module-1-T01-raw.md
        │   ├── module-1-T02-raw.md
        │   ├── gc-T01-raw.md            # 黄金圈转写
        │   ├── gc-T02-raw.md
        │   ├── hmw-T01-raw.md           # HMW 转写
        │   ├── persona-T01-raw.md       # Persona 转写
        │   ├── journey-T01-raw.md       # Journey 转写
        │   ├── maau-{slug}-raw.md       # MAAU 一次性综合逐字稿存档
        │   ├── v2c-vac-{slug}-raw.md    # V2C VAC transcript-direct 逐字稿 / 会议材料存档
        │   └── 5w-{slug}-raw.md         # 5W 转写存档
        ├── modules/
        │   ├── M1-keypoints.md          # MVL 第 1 轮 Key Points
        │   ├── M1-v1.md                 # MVL 确认包 v1（含第 12 节治理元数据）
        │   ├── M1-v2.md                 # MVL 确认包 v2（升版后）
        │   ├── M1-gaps.md               # MVL 补问清单
        │   ├── GC-{slug}-keypoints.md   # GC 第 1 轮 Key Points
        │   ├── GC-{slug}-v1.md          # GC 确认包
        │   ├── GC-{slug}-gaps.md        # GC 补问清单
        │   ├── HMW-{slug}-keypoints.md  # HMW Key Points
        │   ├── HMW-{slug}-v1.md         # HMW 确认包
        │   ├── HMW-{slug}-gaps.md       # HMW 补问清单
        │   ├── PERSONA-{slug}-keypoints.md # Persona Key Points
        │   ├── PERSONA-{slug}-v1.md     # Persona 确认包
        │   ├── PERSONA-{slug}-gaps.md   # Persona 补问清单
        │   ├── JOURNEY-{slug}-keypoints.md # Journey Key Points
        │   ├── JOURNEY-{slug}-v1.md     # Journey 确认包
        │   ├── JOURNEY-{slug}-gaps.md   # Journey 补问清单
        │   ├── MAAU-{slug}-v{N}.md      # MAAU 六板块源包（transcript-direct，唯一事实源）
        │   ├── MAAU-{slug}-gaps.md      # MAAU 补问清单
        │   ├── MAAU-{slug}-gate-report-v{N}.md # MAAU Gate 报告
        │   ├── V2C-VAC-{slug}-keypoints.md # V2C VAC Key Points
        │   ├── V2C-VAC-{slug}-{stage}.md   # V2C VAC pipeline 阶段草稿
        │   ├── V2C-VAC-{slug}-v{N}.md      # V2C VAC 确认包（唯一事实源）
        │   ├── V2C-VAC-{slug}-gaps.md      # V2C VAC 补问清单
        │   ├── V2C-VAC-{slug}-gate-report-v{N}.md # V2C VAC Gate 报告
        │   ├── 5W-{slug}-keypoints.md      # 5W Key Points（Stage 1，讨论地图）
        │   ├── 5W-{slug}-v{N}.md           # 5W 确认包（唯一事实源）
        │   ├── 5W-{slug}-gaps.md           # 5W 补问清单
        │   ├── 5W-{slug}-gate-report-v{N}.md # 5W Gate 报告
        │   ├── hmw/archive/
        │   ├── journey/archive/
        │   ├── maau/archive/            # MAAU 源包旧版归档
        │   ├── v2c-vac/archive/         # V2C VAC 确认包旧版归档
        │   ├── 5w/archive/              # 5W 确认包旧版归档
        │   └── ...
        └── output/
            ├── module-1-canvas.html
            ├── maau-global-canvas.html          # Phase 2 全局页 或 MAAU 实例索引页（二选一，不混用）
            ├── maau-global-canvas-{slug}--noflow-v{N}.html   # MAAU transcript-direct 实例输出
            ├── mvl-final-report.html
            ├── gc-canvas.html           # 黄金圈索引页
            ├── gc-canvas-{slug}--v{N}.html    # 黄金圈 instance 输出
            ├── hmw-canvas.html          # HMW 索引页
            ├── hmw-canvas-{slug}--v{N}.html   # HMW instance 输出
            ├── persona-canvas.html      # Persona 索引页
            ├── persona-canvas-{slug}--v{N}.html # Persona instance 输出
            ├── journey-canvas.html      # Journey 索引页
            ├── journey-canvas-{slug}--v{N}.html # Journey instance 输出
            ├── v2c-vac-canvas.html      # V2C VAC 索引页
            ├── v2c-vac-canvas-{slug}--v{N}.html # V2C VAC instance 输出
            ├── 5w-canvas.html           # 5W 索引页
            └── 5w-canvas-{slug}--v{N}.html    # 5W instance 输出
```

**文件语义**：

- `state.json`：当前 topic 的项目元数据（`project_slug` / `project_name` / `group_id` / `topic_slug` / `topic_name`）+ MVL 各模块 / GC / HMW / Persona / Journey / V2C VAC / 5W 当前 `version` / `status` / `generation_path`（V2C VAC / MAAU）/ `pipeline_stage`（V2C VAC）/ `gate_recommendation` / `render_authorized` / `confirmation_mode` / `override_audit`。
- `topic_meta.json`：当前 topic 的人类友好元数据；`topic_slug` 必须与目录名一致。
- `group_meta.json`：当前 group 的人类友好元数据；`group_id` 必须与目录名一致。
- group `manifest.json`：group 级派生视图，可从当前 group 各 topic 的 `state.json` 重建，不作为业务真相源。
- project `manifest.json`：project 级派生视图（groups + topics 嵌套），可从各 `{group_id}/{topic_slug}/state.json` 重建，不作为业务真相源。
- `transcripts/*.md`：原始逐字稿存档（不可信数据，仅供回溯）。
- `modules/Mx-keypoints.md`：MVL Key Points 概览（**非事实源**，是讨论地图）。
- `modules/Mx-v{N}.md`：MVL 确认包（**唯一事实源**）。
- `modules/GC-{slug}-keypoints.md`：GC Key Points 概览。
- `modules/GC-{slug}-v{N}.md`：GC 确认包（**唯一事实源**）。
- `modules/HMW-{slug}-keypoints.md`：HMW Key Points 概览。
- `modules/HMW-{slug}-v{N}.md`：HMW 确认包（**唯一事实源**）。
- `modules/PERSONA-{slug}-keypoints.md`：Persona Key Points 概览。
- `modules/PERSONA-{slug}-v{N}.md`：Persona 确认包（**唯一事实源**）。
- `modules/JOURNEY-{slug}-keypoints.md`：Journey Key Points 概览。
- `modules/JOURNEY-{slug}-v{N}.md`：Journey 确认包（**唯一事实源**）。
- `modules/MAAU-{slug}-v{N}.md`：MAAU 六板块源包（transcript-direct，**唯一事实源**）。
- `modules/V2C-VAC-{slug}-v{N}.md`：V2C VAC 确认包（pipeline 或 transcript-direct 收敛后的**唯一事实源**）。
- `modules/5W-{slug}-v{N}.md`：5W 确认包（**唯一事实源**）。
- `output/maau-global-canvas-{slug}--noflow-v{N}.html`：MAAU transcript-direct 实例 Canvas。
- `output/v2c-vac-canvas-{slug}--v{N}.html`：V2C VAC instance Canvas。
- `output/module-{n}-canvas--v{N}.html`：MVL 模块 Canvas。
- `output/{gc|hmw|persona|journey|v2c-vac|5w}-canvas.html`：非 MVL instance 索引页。
- `output/{gc|hmw|persona|journey|v2c-vac|5w}-canvas-{slug}.html`：非 MVL instance Canvas。

`state.json` 每次状态变化后立即写入，并同步 patch group 级与 project 级 `manifest.json`。Markdown 确认包是业务事实源，HTML 是同版本展示物，两者不可互相代替。

