"""会话定位与三元一致校验。

规则源（`agents/pratyaya.md`「每次对话开始」/「实例管理」）：
- topic 目录 `workshop/{project_slug}/{group_id}/{topic_slug}/`；
- `project_slug` / `group_id` / `topic_slug` 为 kebab-case ASCII 目录键；
- `default` 仅作 legacy 迁移占位，新建禁止使用；
- 读取 state 后校验三元一致（project_slug / group_id / topic_slug），不一致即阻断。
"""

from __future__ import annotations

import re
from typing import Any

# kebab-case ASCII：小写字母/数字，以连字符分隔，不以连字符开头/结尾。
_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

RESERVED_SLUGS: frozenset[str] = frozenset({"default"})


class SessionError(ValueError):
    """三元不一致 / 非法 slug。"""


def is_valid_slug(slug: Any) -> bool:
    return isinstance(slug, str) and bool(_SLUG_RE.match(slug)) and slug not in RESERVED_SLUGS


def assert_valid_slug(slug: Any, *, what: str = "slug") -> None:
    if not is_valid_slug(slug):
        raise SessionError(
            f"非法 {what}：{slug!r}（须为 kebab-case ASCII，且不得为 default）"
        )


def validate_three_way_consistency(
    state: dict[str, Any],
    project_slug: str,
    group_id: str,
    topic_slug: str,
) -> list[str]:
    """校验 state 与目录路径的三元一致，返回问题列表（空 = 通过）。"""
    problems: list[str] = []
    if state.get("project_slug") != project_slug:
        problems.append(
            f"project_slug 不一致：state={state.get('project_slug')!r} vs 目录={project_slug!r}"
        )
    if state.get("group_id") != group_id:
        problems.append(
            f"group_id 不一致：state={state.get('group_id')!r} vs 目录={group_id!r}"
        )
    if state.get("topic_slug") != topic_slug:
        problems.append(
            f"topic_slug 不一致：state={state.get('topic_slug')!r} vs 目录={topic_slug!r}"
        )
    return problems


def validate_group_meta(group_meta: dict[str, Any], group_id: str) -> list[str]:
    if group_meta.get("group_id") != group_id:
        return [f"group_meta.group_id 不一致：{group_meta.get('group_id')!r} vs {group_id!r}"]
    return []


def validate_topic_meta(topic_meta: dict[str, Any], topic_slug: str) -> list[str]:
    if topic_meta.get("topic_slug") != topic_slug:
        return [
            f"topic_meta.topic_slug 不一致：{topic_meta.get('topic_slug')!r} vs {topic_slug!r}"
        ]
    return []
