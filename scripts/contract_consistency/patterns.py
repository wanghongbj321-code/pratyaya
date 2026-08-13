"""Visual pattern, local link, and deprecated-term checks."""

from __future__ import annotations

from .models import *  # noqa: F403


def _iter_pattern_files(ctx: CheckContext) -> list[Path]:
    base = ctx.root / VISUAL_PATTERNS_DIR
    if not base.is_dir():
        return []
    return sorted(
        p
        for p in base.glob("*.md")
        if p.is_file() and p.name != "README.md"
    )


def check_pattern_count(ctx: CheckContext) -> list[Finding]:
    base = ctx.root / VISUAL_PATTERNS_DIR
    if not base.is_dir():
        return [
            Finding(
                code="PATTERN_COUNT",
                level="error",
                where=VISUAL_PATTERNS_DIR,
                message="缺少 visual-patterns 目录",
                hint="需在 skills/canvas-render/visual-patterns/ 下放 10 个模式文件 + README",
            )
        ]
    readme = base / "README.md"
    if not readme.is_file():
        return [
            Finding(
                code="PATTERN_COUNT",
                level="error",
                where=VISUAL_PATTERNS_README,
                message="缺少 visual-patterns/README.md",
                hint="补齐 visual-patterns 目录说明",
            )
        ]
    files = _iter_pattern_files(ctx)
    if len(files) != EXPECTED_VISUAL_PATTERN_COUNT:
        return [
            Finding(
                code="PATTERN_COUNT",
                level="error",
                where=VISUAL_PATTERNS_DIR,
                message=f"模式文件 {len(files)} 个 ≠ 期望 {EXPECTED_VISUAL_PATTERN_COUNT}",
                hint="按 visual-patterns/README.md 当前基线维护 10 个模式",
            )
        ]
    return []


def check_pattern_filename(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    pattern_re = re.compile(r"^(\d{2})-(.+)\.md$")
    for path in _iter_pattern_files(ctx):
        match = pattern_re.match(path.name)
        if not match:
            findings.append(
                Finding(
                    code="PATTERN_FILENAME",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"文件名 {path.name!r} 不符合 NN-id.md 规范",
                    hint="文件名必须为 NN-id.md（两位序号 + kebab-case id）",
                )
            )
    return findings


def check_pattern_sequence(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    nn_seen: list[str] = []
    pattern_re = re.compile(r"^(\d{2})-(.+)\.md$")
    for path in _iter_pattern_files(ctx):
        match = pattern_re.match(path.name)
        if not match:
            continue
        nn_seen.append(match.group(1))
    nn_sorted = sorted(set(nn_seen))
    if nn_sorted != list(EXPECTED_VISUAL_PATTERN_NN_RANGE):
        findings.append(
            Finding(
                code="PATTERN_SEQUENCE",
                level="error",
                where=VISUAL_PATTERNS_DIR,
                message=f"模式序号集合 {nn_sorted} ≠ 期望 {list(EXPECTED_VISUAL_PATTERN_NN_RANGE)}",
                hint="必须使用 01..10；不得跳号或重排已发布序号",
            )
        )
    if len(nn_seen) != len(set(nn_seen)):
        duplicates = sorted({n for n, c in Counter(nn_seen).items() if c > 1})
        findings.append(
            Finding(
                code="PATTERN_SEQUENCE",
                level="error",
                where=VISUAL_PATTERNS_DIR,
                message=f"模式序号重复：{duplicates}",
                hint="每个 NN 只能被一个模式占用",
            )
        )
    return findings


def check_pattern_id(ctx: CheckContext) -> list[Finding]:
    """frontmatter id 必须等于去掉 NN- 和 .md 后的文件名。"""
    findings: list[Finding] = []
    pattern_re = re.compile(r"^(\d{2})-(.+)\.md$")
    for path in _iter_pattern_files(ctx):
        match = pattern_re.match(path.name)
        if not match:
            continue
        expected_id = match.group(2)
        text = read_text(path)
        fm, _ = parse_frontmatter(text)
        actual_id = fm.get("id", "")
        if not actual_id:
            findings.append(
                Finding(
                    code="PATTERN_ID",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message="frontmatter 缺 id 字段",
                    hint="每个模式必须声明 id 且与文件名 {id} 一致",
                )
            )
            continue
        if actual_id != expected_id:
            findings.append(
                Finding(
                    code="PATTERN_ID",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"frontmatter id={actual_id!r} 与文件名 {expected_id!r} 不一致",
                    hint="id 字段必须等于去掉 NN- 和 .md 的文件名",
                )
            )
    return findings


def check_pattern_metadata(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_pattern_files(ctx):
        text = read_text(path)
        fm, _ = parse_frontmatter(text)
        missing = [k for k in EXPECTED_VISUAL_PATTERN_METADATA if k not in fm]
        if missing:
            findings.append(
                Finding(
                    code="PATTERN_METADATA",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"frontmatter 缺字段 {missing}",
                    hint=f"frontmatter 必须包含 {EXPECTED_VISUAL_PATTERN_METADATA}",
                )
            )
    return findings


def check_pattern_enum(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_pattern_files(ctx):
        text = read_text(path)
        fm, _ = parse_frontmatter(text)
        if fm.get("layout") not in PATTERN_LAYOUT_ENUM:
            findings.append(
                Finding(
                    code="PATTERN_ENUM",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"layout={fm.get('layout')!r} 不在 {sorted(PATTERN_LAYOUT_ENUM)} 内",
                    hint="layout 必须为 balanced 或 flow",
                )
            )
        if fm.get("formality") not in PATTERN_FORMALITY_ENUM:
            findings.append(
                Finding(
                    code="PATTERN_ENUM",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"formality={fm.get('formality')!r} 不在 {sorted(PATTERN_FORMALITY_ENUM)} 内",
                    hint="formality 必须为 medium-high 或 high",
                )
            )
        if fm.get("density") not in PATTERN_DENSITY_ENUM:
            findings.append(
                Finding(
                    code="PATTERN_ENUM",
                    level="error",
                    where=str(path.relative_to(ctx.root)),
                    message=f"density={fm.get('density')!r} 不在 {sorted(PATTERN_DENSITY_ENUM)} 内",
                    hint="density 必须为 medium / medium-high / high",
                )
            )
    return findings


# ---- 本地 Markdown 链接 ---------------------------------------------------


def check_local_link(ctx: CheckContext) -> list[Finding]:
    """扫描 Markdown 文件中形如 ``./xxx.md`` 或 ``../xxx.md`` 的本地链接。

    仅在目标像路径（含 ``.md`` / ``.html`` / 含 ``/``）时检查；纯数字锚点或单字符引用忽略。
    """
    findings: list[Finding] = []
    candidates: list[Path] = []
    for sub in (
        "README.md",
        "DEVELOPMENT.md",
        "DESIGN.md",
        "CHANGELOG.md",
        "AGENTS.md",
        "docs",
        "skills",
        "agents",
        "examples",
        "schemas",
    ):
        path = ctx.root / sub
        if path.is_file():
            candidates.append(path)
        elif path.is_dir():
            candidates.extend(p for p in path.rglob("*.md") if p.is_file())
    for path in candidates:
        text = read_text(path)
        for _, target, lineno in split_md_links(text):
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            # 只检查路径形态的目标（至少含 / 或文件后缀），避免误报纯数字锚点
            if "/" not in clean and "." not in clean:
                continue
            link_path = (path.parent / clean).resolve()
            if not _is_within(link_path, ctx.root.resolve()):
                findings.append(
                    Finding(
                        code="LOCAL_LINK",
                        level="error",
                        where=f"{path.relative_to(ctx.root)}:{lineno}",
                        message=f"链接 {target!r} 跳出仓库根目录",
                        hint="若非有意指向其他仓库，请改用仓库内相对路径（一般 1–2 个 ../）",
                    )
                )
                continue
            if not link_path.exists():
                findings.append(
                    Finding(
                        code="LOCAL_LINK",
                        level="error",
                        where=f"{path.relative_to(ctx.root)}:{lineno}",
                        message=f"链接 {target!r} 解析为不存在的路径 {link_path.relative_to(ctx.root)}",
                        hint="修正为目标文件真实路径",
                    )
                )
    return findings


# ---- 废弃术语 -------------------------------------------------------------


def check_deprecated_term(ctx: CheckContext) -> list[Finding]:
    """在权威文档中检查废弃术语（仅扫描关键目录，避免对所有 Markdown 误报）。"""
    findings: list[Finding] = []
    scan_paths = [
        "README.md",
        "DEVELOPMENT.md",
        "DESIGN.md",
        "docs",
        "skills",
        "agents",
        "schemas",
        ".codebuddy-plugin",
    ]
    for sub in scan_paths:
        path = ctx.root / sub
        if path.is_file():
            files = [path]
        elif path.is_dir():
            files = [p for p in path.rglob("*") if p.is_file()]
        else:
            continue
        for f in files:
            if f.suffix not in {".md", ".json", ".yaml", ".yml"}:
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            for term, explanation in DEPRECATED_TERMS.items():
                if term not in text:
                    continue
                # README/DESIGN/DEVELOPMENT 等"显式说明废弃"的上下文不视为违规。
                # 扩大上下文窗口到 6 行（前后各 3），覆盖 schema 注释和文档说明。
                lines = text.splitlines()
                for lineno, line in enumerate(lines, 1):
                    if term not in line:
                        continue
                    start = max(0, lineno - 4)
                    window = "\n".join(lines[start : lineno + 2])
                    if any(
                        kw in window
                        for kw in (
                            "已弃用",
                            "已删除",
                            "deprecated",
                            "不推荐",
                            "不得再",
                            "删除",
                            "不再使用",
                            "不作为当前",
                            "非强制参考",
                            "旧",
                        )
                    ):
                        continue
                    findings.append(
                        Finding(
                            code="DEPRECATED_TERM",
                            level="error",
                            where=f"{f.relative_to(ctx.root)}:{lineno}",
                            message=f"出现废弃术语 {term!r}",
                            hint=explanation,
                        )
                    )
    return findings


# ---------------------------------------------------------------------------
# Phase B 规则：跨契约结构比较
# ---------------------------------------------------------------------------


