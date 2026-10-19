"""文件级 gate：产物存在性 / 版本一致性 / 旧 HTML 过期标记。

红线：本模块**不做渲染**。升版后旧 HTML 通过写 sidecar 标记文件（`*.html.stale`）标记
过期，不修改 HTML 内容（HTML 由 canvas-render 生成，本引擎禁止写 HTML）。

依赖：paths（零副作用）+ 标准库。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import paths


def keypoints_exists(topic: str | Path, file_prefix: str, slug: str) -> bool:
    return paths.keypoints_file(topic, file_prefix, slug).exists()


def confirm_exists(topic: str | Path, file_prefix: str, slug: str, version: int) -> bool:
    return paths.confirm_file(topic, file_prefix, slug, version).exists()


def gaps_exists(topic: str | Path, file_prefix: str, slug: str) -> bool:
    return paths.gaps_file(topic, file_prefix, slug).exists()


def gate_report_exists(topic: str | Path, file_prefix: str, slug: str, version: int) -> bool:
    return paths.gate_report_file(topic, file_prefix, slug, version).exists()


def html_exists(topic: str | Path, output_prefix: str, slug: str, **identity) -> bool:
    return paths.html_file(topic, output_prefix, slug, **identity).exists()


def index_exists(topic: str | Path, output_prefix: str) -> bool:
    return paths.index_file(topic, output_prefix).exists()


def list_confirm_versions(topic: str | Path, file_prefix: str, slug: str) -> list[int]:
    """枚举 `modules/` 下 `{file_prefix}-{slug}-v{N}.md` 的版本号（升序）。"""
    modules_dir = Path(topic) / "modules"
    if not modules_dir.is_dir():
        return []
    pattern = re.compile(rf"^{re.escape(file_prefix)}-{re.escape(slug)}-v(\d+)\.md$")
    versions: list[int] = []
    for p in modules_dir.iterdir():
        m = pattern.match(p.name)
        if m:
            versions.append(int(m.group(1)))
    return sorted(versions)


def html_stale_marker(topic: str | Path, output_prefix: str, slug: str, **identity) -> Path:
    """旧 HTML 过期标记文件路径：`{html}.stale`。"""
    return paths.html_file(topic, output_prefix, slug, **identity).with_suffix(".html.stale")


def mark_html_stale(topic: str | Path, output_prefix: str, slug: str, *, stale_version: int, **identity) -> Path:
    """写 sidecar 标记文件，标记旧 HTML 过期（不修改 HTML 内容）。"""
    marker = html_stale_marker(topic, output_prefix, slug, **identity)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps({"stale": True, "version": stale_version}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return marker


def is_html_stale(topic: str | Path, output_prefix: str, slug: str, **identity) -> bool:
    return html_stale_marker(topic, output_prefix, slug, **identity).exists()


def clear_html_stale(topic: str | Path, output_prefix: str, slug: str, **identity) -> None:
    marker = html_stale_marker(topic, output_prefix, slug, **identity)
    if marker.exists():
        marker.unlink()
