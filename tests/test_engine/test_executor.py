"""标准 8 步推进/回退与轮次版本映射测试（§8）。"""

import pytest

from skills._engine.executor import (
    ExecutorError,
    assert_advance,
    assert_valid_step,
    branch_to_status,
    can_advance,
    is_valid_step,
    round_to_version,
)


@pytest.mark.parametrize(
    "from_step,to_step,ok",
    [
        (0, 1, True),
        (1, 2, True),
        (1, 3, True),
        (1, 4, True),
        (2, 5, True),
        (3, 1, True),   # 补问回步骤 1
        (4, 2, True),   # 先看个样子仍可提炼
        (4, 3, True),
        (5, 6, True),
        (6, 7, True),
        (7, 8, True),
        (0, 2, False),
        (2, 6, False),
        (5, 7, False),
        (6, 8, False),
        (8, 7, False),
        (3, 5, False),
    ],
)
def test_can_advance(from_step, to_step, ok):
    assert can_advance(from_step, to_step) is ok


def test_assert_advance_raises():
    with pytest.raises(ExecutorError):
        assert_advance(2, 6)


def test_invalid_step():
    assert not is_valid_step(9)
    assert not is_valid_step(-1)
    with pytest.raises(ExecutorError):
        assert_valid_step(9)


@pytest.mark.parametrize("round_num,expected", [(1, 1), (2, 2), (6, 6)])
def test_round_to_version(round_num, expected):
    assert round_to_version(round_num) == expected


@pytest.mark.parametrize("round_num", [0, -1, 1.5, "1", True, None])
def test_round_to_version_invalid(round_num):
    with pytest.raises(ExecutorError):
        round_to_version(round_num)


@pytest.mark.parametrize(
    "branch,expected",
    [("refine", "review_ready"), ("supplement", "gaps_open"), ("preview", None)],
)
def test_branch_to_status(branch, expected):
    assert branch_to_status(branch) == expected


def test_branch_invalid():
    with pytest.raises(ExecutorError):
        branch_to_status("other")
