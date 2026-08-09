# Pratyaya Schemas（非强制参考）

本目录下的 JSON Schema 仅作为非强制参考。**模块产物的唯一中间格式是 Markdown**（MVL 为 `modules/Mx-keypoints.md`、`modules/Mx-v{N}.md`；非 MVL 一等公民画布为 `modules/{GC|HMW|PERSONA|JOURNEY}-{slug}-keypoints.md`、`modules/{GC|HMW|PERSONA|JOURNEY}-{slug}-v{N}.md`），运行时不强制执行 JSON Schema 校验。

## 文件说明

### `state.schema.json`（v2.3）

- **用途**：描述 `state.json` 的项目状态、模块版本、状态与审批结构，支持 MVL、黄金圈（Golden Circle）、HMW（How Might We）、Persona（用户画像）和 Journey（用户旅程）画布类型。
- **v2.4 路径分层约束（schema_version 仍为 2.3）**：
  - 新增顶层 `project_slug`，作为 `workshop/{project_slug}/{group_id}/` 的项目目录键；`project_name` 保留为人类显示名，可中文。
  - `group_id` 从任意非空字符串收紧为 kebab-case ASCII 短名，必须与 group 目录名一致。
  - 项目级 `manifest.json` 是可重建缓存，真相源仍为各 group 的 `state.json`。
- **v2.7 topic 层约束（schema_version 仍为 2.3）**：
  - 新增顶层 `topic_slug`（kebab-case ASCII，maxLength 64）与 `topic_name`（string，minLength 1）为 `required`。
  - `state.json` 下沉为 topic 级状态，目录为 `workshop/{project_slug}/{group_id}/{topic_slug}/`；`topic_slug` 必须与 topic 目录名一致。
  - `topic_slug` 不替代画布 `instance_slug`：topic 是工作坊议题边界，instance 是同一 topic 内的 GC/HMW/Persona/Journey/MAAU 画布实例边界，二者不得混用。
- **v2.6 instance map 约束（schema_version 仍为 2.3）**：
  - `golden_circle` / `hmw` / `persona` / `journey` 由单对象升级为 `map: slug → instance_state`，路径为 `state.{state_key}.{slug}`。
  - 每个 instance 必须包含 `slug`，且运行时校验 `instance.slug == map key`；JSON Schema 负责 slug 格式，动态键一致性由迁移脚本 / audit / 测试补充校验。
  - 新建 instance 禁止使用 `default`；legacy 单字段迁移可生成 `default` 并触发 `force_consent=true`。
  - 派生子版本写入 `_meta.instance_map_schema_version = "2.6-instance-map-1"`。
- **v2.7 MAAU 综合路径约束（schema_version 仍为 2.3）**：
  - 新增顶层 `maau` 区块：`map: slug → maau_instance_state`，路径为 `state.maau.{slug}`，表示「一次性逐字稿 → MAAU 六板块源包」的默认综合路径实例。
  - `maau_instance_map.propertyNames` 用 kebab-case ASCII + `not: { const: "default" }` 显式禁词（MAAU 不走 legacy default，新建 slug 必须语义化命名）。
  - 每个 instance 必须包含 `slug` 与 `generation_path`；`generation_path` 固定为 `const: "transcript-direct"`，不得使用其他值。
  - 继承 `single_canvas_state_base` 5 态字段（version / status / gate_recommendation / render_authorized / confirmation_mode）+ 可选 `override_audit`。
  - override 审计项 `assessment_id` 限定为 `^MAAU-GATE-[0-9]+$`，`category` 仅允许 `business_risk`。
  - 与 M1-M6 Phase 2 全局汇总互斥隔离：同一 group 的 MAAU 输出只能二选一（transcript-direct 或 M1-M6 Phase 2），`maau` 区块为可选，无 `maau` 的旧 state 不阻断其他流程（懒加载）。
- **v2.3 变更**：
  - `schema_version` 从 `"2.1"` 升级到 `"2.3"`（MINOR：承接 v2.2 Persona 可选区块，并新增 **Journey 可选区块**）。
  - 新增顶层 `journey` 对象，字段结构与 `golden_circle` / `hmw` 同构（`status` / `version` / `gate_recommendation` / `render_authorized` / `confirmation_mode` / `override_audit`）。
  - Journey override 审计项 `assessment_id` 限定为 `^JOURNEY-GATE-[0-9]+$`，`category` 仅允许 `business_risk`。
- **v2.2 变更**：
  - 新增顶层 `persona` 对象，字段结构与 `golden_circle` / `hmw` 同构。
  - Persona override 审计项 `assessment_id` 限定为 `^PERSONA-GATE-[0-9]+$`，`category` 仅允许 `business_risk`。
- **v2.1 变更**：
  - `schema_version` 从 `"2.0"` 升级到 `"2.1"`（MINOR：新增**可选** `hmw` 顶层区块，无破坏性变更）。
  - 新增顶层 `hmw` 对象，字段结构与 `golden_circle` 完全一致。
- **v2.0 变更（历史）**：
  - `current_module` 和 `modules` 从顶层 `required` 降为可选字段（仅 MVL 画布需要）。
  - 新增顶层 `golden_circle` 对象。
- **向后兼容**：旧 MVL-only / GC-only / HMW / Persona state.json（无 `journey` 区块）在目录迁移后仍可使用；迁移会补入 `project_slug` 并规范化 `group_id`。未迁移的 raw legacy state 可能无法直接通过 v2.4 路径分层后的 schema 校验。`hmw` / `persona` / `journey` 均为可选区块，不强制存在。
- **当前状态**：保留作为**非强制参考**；LLM 不强制调用校验器。

### `module-record.schema.json`

- **用途**：参考旧 `modules/module-N.json` 的模块字段结构（canvas_fields、conclusions、gaps、inferences、alignment、approval、gate）。
- **当前状态**：保留作为**非强制参考**。`modules/Mx-v{N}.md`（确认包 Markdown）是当前唯一事实源。

### `group_meta.schema.json`

- **用途**：描述 `workshop/{project_slug}/{group_id}/group_meta.json` 的 group 显示元数据。
- **字段边界**：`group_id` 必须为 kebab-case ASCII 并与目录名一致；`group_name` / `group_lead` / `contact` / `created_by` 为人类友好字段，可中文。
- **当前状态**：非强制参考；主 Agent 在创建 group 或迁移旧项目时写入。

### `project_manifest.schema.json`

- **用途**：描述 `workshop/{project_slug}/manifest.json` 的项目级 group + topic 嵌套汇总视图。
- **v2.7 变更（schema_version = 2.7-project-manifest-1）**：
  - topic 作为 group 下的目录层，`groups[].state_path` 升级为 `groups[].topics[].state_path`。
  - `groups[].topics[].state_path` 必须为 `{group_id}/{topic_slug}/state.json`；`groups[].topics[].topic_meta_path` 必须为 `{group_id}/{topic_slug}/topic_meta.json`。
  - 增加 `groups[].group_meta_path`（`{group_id}/group_meta.json`）。
  - 路径 pattern 禁止 `../`、绝对路径和跨 group / 跨 topic 路径；`state_path` 与 `group_id` / `topic_slug` 的相等关系由主 Agent / 测试一致性校验负责，JSON Schema 只检查路径形状。
- **当前状态**：派生 view / 缓存；缺失或陈旧时可从 `{group_id}/{topic_slug}/state.json` 重建，不作为业务真相源。

### `group_manifest.schema.json`

- **用途**：描述 `workshop/{project_slug}/{group_id}/manifest.json` 的 group 级 topic 汇总视图。
- **字段边界**：`group_id` 与 group 目录名一致；`topics[].state_path` 必须为 `{topic_slug}/state.json`；`topics[].topic_meta_path` 必须为 `{topic_slug}/topic_meta.json`；禁止 `../` 或跨 group / 跨 topic 路径。
- **当前状态**：派生 view / 缓存；缺失或陈旧时可从 `workshop/{project_slug}/{group_id}/*/state.json` 重建，不作为业务真相源。写失败不阻断当前 topic 的 state 写入。

### `topic_meta.schema.json`

- **用途**：描述 `workshop/{project_slug}/{group_id}/{topic_slug}/topic_meta.json` 的 topic 显示元数据。
- **字段边界**：`topic_slug` 必须为 kebab-case ASCII 并与 topic 目录名一致；`topic_name` / `topic_owner` / `contact` / `created_by` 为人类友好字段，可中文。
- **当前状态**：非强制参考；主 Agent 在创建 topic 或迁移旧 group 时写入。`default` 仅作为 legacy 迁移占位，新建 topic 禁止使用。

## 当前实际数据源

| 资产 | 当前实现 |
|---|---|
| 状态 | `workshop/{project_slug}/{group_id}/{topic_slug}/state.json`（参考 state.schema.json v2.3，不强制校验；MVL 存 `modules.M1`-`M6`，非 MVL 存 `golden_circle.{slug}` / `hmw.{slug}` / `persona.{slug}` / `journey.{slug}` / `maau.{slug}`） |
| group 级汇总 | `workshop/{project_slug}/{group_id}/manifest.json`（派生缓存，topic 列表；可重建） |
| 项目级汇总 | `workshop/{project_slug}/manifest.json`（派生缓存，groups + topics 嵌套；可重建） |
| 模块中间产物 | `modules/Mx-keypoints.md` + `modules/Mx-v{N}.md`（MVL）/ `modules/GC-{slug}-keypoints.md` + `modules/GC-{slug}-v{N}.md`（黄金圈）/ `modules/HMW-{slug}-keypoints.md` + `modules/HMW-{slug}-v{N}.md`（HMW）/ `modules/PERSONA-{slug}-keypoints.md` + `modules/PERSONA-{slug}-v{N}.md`（Persona）/ `modules/JOURNEY-{slug}-keypoints.md` + `modules/JOURNEY-{slug}-v{N}.md`（Journey）/ `modules/MAAU-{slug}-v{N}.md`（MAAU 一次性综合源包） |
| 闸门判定 | LLM 阅读确认包 + 对应 Gate 策略文件（MVL: `Mx-gate.md` / GC: `GC-gate.md` / HMW: `HMW-gate.md` / Persona: `PERSONA-gate.md` / Journey: `JOURNEY-gate.md` / MAAU: `MAAU-gate.md`），输出 Markdown 判定报告 |
| 事实源 | `Mx-v{N}.md` / `GC-{slug}-v{N}.md` / `HMW-{slug}-v{N}.md` / `PERSONA-{slug}-v{N}.md` / `JOURNEY-{slug}-v{N}.md` / `MAAU-{slug}-v{N}.md`（唯一事实源） |

## 后续评估

- 后续 MAJOR 版本可评估是否完全移除 `module-record.schema.json`。
- `state.schema.json` 视当前 5 态状态机与多画布类型的兼容需求再决定，无删除紧迫性。
