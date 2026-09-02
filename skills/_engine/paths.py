"""路径与命名模板 —— 唯一拼接处。

所有产物 / 状态文件路径的唯一拼接点，避免在 agent md、references、各 Skill 之间出现
多份路径拼接逻辑（执行计划 §7.2「paths.py 是 `modules/{前缀}-{slug}-v{N}.md` 等的唯一拼接处」）。

本模块**零副作用**：只做字符串拼接，不做文件系统 IO。路径约定以 `agents/pratyaya.md`
「状态目录」「标准 8 步」「实例管理」为唯一事实源。
"""

from __future__ import annotations

from pathlib import Path

# 归档目录名：模块产物旧版归档到 `modules/{canvas_id}/archive/`。
ARCHIVE_DIR_NAME = "archive"

# 状态 / 元数据文件名。
STATE_FILENAME = "state.json"
TOPIC_META_FILENAME = "topic_meta.json"
GROUP_META_FILENAME = "group_meta.json"
MANIFEST_FILENAME = "manifest.json"


def resolve_file_prefix(file_prefix: str, module: str | None = None) -> str:
    """把含 `{N}` 的前缀模板替换为具体模块号（仅 mvl 需要）。"""
    if "{N}" in file_prefix:
        if not module:
            raise ValueError("file_prefix 含 {N} 时必须提供 module（如 M1）")
        return file_prefix.replace("{N}", module)
    return file_prefix


def topic_dir(workshop_root: str | Path, project_slug: str, group_id: str, topic_slug: str) -> Path:
    """`workshop/{project_slug}/{group_id}/{topic_slug}/`。"""
    return Path(workshop_root) / project_slug / group_id / topic_slug


def group_dir(workshop_root: str | Path, project_slug: str, group_id: str) -> Path:
    """`workshop/{project_slug}/{group_id}/`。"""
    return Path(workshop_root) / project_slug / group_id


def project_dir(workshop_root: str | Path, project_slug: str) -> Path:
    """`workshop/{project_slug}/`。"""
    return Path(workshop_root) / project_slug


def state_file(topic: str | Path) -> Path:
    """`{topic}/state.json`。"""
    return Path(topic) / STATE_FILENAME


def topic_meta_file(topic: str | Path) -> Path:
    """`{topic}/topic_meta.json`。"""
    return Path(topic) / TOPIC_META_FILENAME


def group_meta_file(group: str | Path) -> Path:
    """`{group}/group_meta.json`。"""
    return Path(group) / GROUP_META_FILENAME


def group_manifest_file(group: str | Path) -> Path:
    """`{group}/manifest.json`。"""
    return Path(group) / MANIFEST_FILENAME


def project_manifest_file(project: str | Path) -> Path:
    """`{project}/manifest.json`。"""
    return Path(project) / MANIFEST_FILENAME


def transcript_file(topic: str | Path, canvas_label: str, index: int) -> Path:
    """`transcripts/{canvas_label}-T{index:02d}-raw.md`。"""
    return Path(topic) / "transcripts" / f"{canvas_label}-T{index:02d}-raw.md"


def keypoints_file(topic: str | Path, file_prefix: str, slug: str) -> Path:
    """`modules/{文件前缀}-{slug}-keypoints.md`。"""
    return Path(topic) / "modules" / f"{file_prefix}-{slug}-keypoints.md"


def confirm_file(topic: str | Path, file_prefix: str, slug: str, version: int) -> Path:
    """`modules/{文件前缀}-{slug}-v{N}.md`（确认包）。"""
    return Path(topic) / "modules" / f"{file_prefix}-{slug}-v{version}.md"


def gaps_file(topic: str | Path, file_prefix: str, slug: str) -> Path:
    """`modules/{文件前缀}-{slug}-gaps.md`。"""
    return Path(topic) / "modules" / f"{file_prefix}-{slug}-gaps.md"


def gate_report_file(topic: str | Path, file_prefix: str, slug: str, version: int) -> Path:
    """`modules/{文件前缀}-{slug}-gate-report-v{N}.md`。"""
    return Path(topic) / "modules" / f"{file_prefix}-{slug}-gate-report-v{version}.md"


def html_file(topic: str | Path, output_prefix: str, slug: str) -> Path:
    """`output/{输出前缀}-canvas-{slug}.html`。"""
    return Path(topic) / "output" / f"{output_prefix}-canvas-{slug}.html"


def index_file(topic: str | Path, output_prefix: str) -> Path:
    """`output/{输出前缀}-canvas.html`（索引页）。"""
    return Path(topic) / "output" / f"{output_prefix}-canvas.html"


def archive_dir(topic: str | Path, canvas_id: str) -> Path:
    """`modules/{canvas_id}/archive/`（旧版确认包归档目录）。"""
    return Path(topic) / "modules" / canvas_id / ARCHIVE_DIR_NAME
