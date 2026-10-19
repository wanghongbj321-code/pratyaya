#!/usr/bin/env python3
"""pratyaya 专家包发布打包器。

把仓库源码筛成可安装的专家包 zip，输出至 dist/<name>-<version>.zip。

设计原则（见 internal/pratyaya-internal/docs/dev-plan/引擎迁移与发布打包执行计划）：
- 采用 **allowlist 语义**：仅白名单内路径进包，其余一律不打包。
- 版本与包名从 .codebuddy-plugin/plugin.json 读取，不写死。
- 打包前执行 L2 包内一致性断言，失败即中止、不产 zip。
- zip 顶层目录 = plugin.json.name，文件名 = <name>-<version>.zip。
- --dry-run 只打印将写入的文件清单与条数，不产 zip。

标准库 only，不依赖第三方包。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 白名单：进包的路径（相对仓库根）。其余一律不打包。
# ---------------------------------------------------------------------------
# 目录条目（末尾无斜杠表示整目录递归；有则按目录原样）：
ALLOWLIST = [
    ".codebuddy-plugin/plugin.json",
    "agents",
    "skills",
    "scripts/__init__.py",
    "scripts/engine",
    "avatars",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
]

# 通用排除：白名单目录内部仍要剔除的条目（按 basename / 后缀）。
GLOBAL_EXCLUDES = {
    "__pycache__",
    ".pyc",           # 后缀匹配（含散落 *.pyc）
    ".DS_Store",
    ".gitkeep",
    "Thumbs.db",
    ".pyo",
    ".render-trace.jsonl",   # 渲染性能插桩运行时 trace（不入库、不进包）
    ".in_use",               # 运行时标记（方法论 §1.4）
    ".created-by-session",   # 会话创建标记
}

# 需要目录存在时才纳入的条目（不存在则跳过，不报错）。
OPTIONAL_DIRS = {"avatars"}

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


class PackageError(Exception):
    """打包前置断言失败。"""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_plugin() -> dict:
    p = _repo_root() / ".codebuddy-plugin" / "plugin.json"
    if not p.is_file():
        raise PackageError(f"缺失 {p}（plugin.json 元数据入口）")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise PackageError(f"plugin.json 解析失败：{e}")


def _assert_preflight(plugin: dict, root: Path) -> None:
    """B3 打包前断言（L2 包内一致性）。任一失败即中止。"""
    name = plugin.get("name")
    plug = plugin.get("plugin")
    version = plugin.get("version")

    # 1. name/plugin/version
    if not isinstance(name, str) or not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", name):
        raise PackageError(f"plugin.json.name 非法：{name!r}")
    if name != plug:
        raise PackageError(f"name({name!r}) != plugin({plug!r})")
    if not isinstance(version, str) or not _SEMVER_RE.match(version):
        raise PackageError(f"plugin.json.version 非 SemVer：{version!r}")

    # 2. skills[] ↔ skills/ 顶层目录一一对应
    declared = {s.removeprefix("./skills/").removeprefix("skills/") for s in plugin.get("skills", [])}
    actual = {p.name for p in (root / "skills").iterdir() if p.is_dir()}
    if declared != actual:
        only_declared = declared - actual
        only_actual = actual - declared
        raise PackageError(
            "skills 声明与目录不一致："
            f"仅声明缺目录={sorted(only_declared)}，仅目录缺声明={sorted(only_actual)}"
        )

    # 3. agents[] 每个路径存在
    for a in plugin.get("agents", []):
        ap = root / a.removeprefix("./")
        if not ap.is_file():
            raise PackageError(f"agents[] 指向的文件不存在：{a}")

    # 4. avatar 声明文件存在
    avatar = plugin.get("avatar")
    if avatar:
        if not (root / avatar.removeprefix("./")).is_file():
            raise PackageError(f"avatar 文件不存在：{avatar}")

    # 5. 引擎随包完整性
    for engine_path in ("scripts/__init__.py", "scripts/engine/__init__.py"):
        if not (root / engine_path).is_file():
            raise PackageError(f"引擎文件缺失：{engine_path}")

    # 6. 每个 skills[] 路径下有 SKILL.md
    for s in plugin.get("skills", []):
        sk = root / s.removeprefix("./") / "SKILL.md"
        if not sk.is_file():
            raise PackageError(f"skill 缺 SKILL.md：{s}")


def _should_exclude(rel_path: Path) -> bool:
    """判断白名单内的单个条目是否命中通用排除。"""
    name = rel_path.name
    if name in GLOBAL_EXCLUDES:
        return True
    if name.endswith(".pyc") or name.endswith(".pyo"):
        return True
    return False


def _collect_files(root: Path) -> list[tuple[Path, str]]:
    """返回 [(绝对路径, 包内相对路径)]，按包内路径排序。"""
    collected: list[tuple[Path, str]] = []
    for entry in ALLOWLIST:
        p = root / entry
        if p.is_dir():
            if entry in OPTIONAL_DIRS and not p.exists():
                continue
            for f in sorted(p.rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(root)
                if _should_exclude(rel):
                    continue
                collected.append((f, rel.as_posix()))
        elif p.is_file():
            collected.append((p, entry))
        else:
            raise PackageError(f"白名单条目不存在：{entry}")
    collected.sort(key=lambda t: t[1])
    return collected


def _build_zip(files: list[tuple[Path, str]], name: str, version: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{name}-{version}.zip"
    # 固定时间戳，保证同源可复现
    fixed_dt = (2000, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for abs_path, rel in files:
            arc = f"{name}/{rel}"
            zi = zipfile.ZipInfo(arc, date_time=fixed_dt)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zf.writestr(zi, abs_path.read_bytes())
    return zip_path


def _archive_old(out_dir: Path, name: str, current_version: str) -> None:
    """把 dist/ 下既有（非当前版本）的 zip 移入 dist/archive/。"""
    archive = out_dir / "archive"
    for old in out_dir.glob(f"{name}-*.zip"):
        if old.name == f"{name}-{current_version}.zip":
            continue
        archive.mkdir(parents=True, exist_ok=True)
        old.rename(archive / old.name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="pratyaya 专家包发布打包器")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将写入的文件清单与条数，不产 zip",
    )
    args = parser.parse_args(argv)

    root = _repo_root()
    plugin = _read_plugin()
    _assert_preflight(plugin, root)

    name = plugin["name"]
    version = plugin["version"]
    files = _collect_files(root)
    out_dir = root / "dist"

    if args.dry_run:
        print(f"[dry-run] {name}-{version}.zip 将写入 {len(files)} 个文件：")
        for _, rel in files:
            print(f"  {rel}")
        return 0

    # 归档旧包，再出新包
    _archive_old(out_dir, name, version)
    zip_path = _build_zip(files, name, version, out_dir)

    print(f"已生成 {zip_path}（{len(files)} 个文件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
