"""会话定位与三元一致 / slug 校验测试（§8）。"""

import pytest

from skills._engine.session import (
    SessionError,
    assert_valid_slug,
    is_valid_slug,
    validate_group_meta,
    validate_three_way_consistency,
    validate_topic_meta,
)


def test_valid_slugs():
    assert is_valid_slug("acme-corp")
    assert is_valid_slug("a1-b2")
    assert is_valid_slug("single")


@pytest.mark.parametrize(
    "slug",
    ["default", "Default", "A-B", "-abc", "abc-", "abc--def", "", "a_b", 123, None],
)
def test_invalid_slugs(slug):
    assert not is_valid_slug(slug)


def test_assert_valid_slug_raises():
    with pytest.raises(SessionError):
        assert_valid_slug("default")
    with pytest.raises(SessionError):
        assert_valid_slug("A-B")


def test_three_way_consistency_ok():
    state = {"project_slug": "p", "group_id": "g", "topic_slug": "t"}
    assert validate_three_way_consistency(state, "p", "g", "t") == []


def test_three_way_consistency_mismatch():
    state = {"project_slug": "p", "group_id": "g", "topic_slug": "t"}
    problems = validate_three_way_consistency(state, "x", "y", "z")
    assert len(problems) == 3
    assert any("project_slug" in p for p in problems)
    assert any("group_id" in p for p in problems)
    assert any("topic_slug" in p for p in problems)


def test_validate_group_meta():
    assert validate_group_meta({"group_id": "g"}, "g") == []
    assert validate_group_meta({"group_id": "x"}, "g") != []


def test_validate_topic_meta():
    assert validate_topic_meta({"topic_slug": "t"}, "t") == []
    assert validate_topic_meta({"topic_slug": "x"}, "t") != []
