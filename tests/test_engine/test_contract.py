"""确认包结构契约校验测试（§7.1 / §8）。"""

import pytest

from skills._engine.contract import (
    ContractError,
    assert_filename_consistent,
    gate_id_regex,
    parse_confirmation_filename,
    parse_mvl_filename,
    validate_gate_ids,
    validate_governance_sections,
    validate_version_marker,
)


def test_parse_confirmation_filename():
    assert parse_confirmation_filename("GC-acme-v1.md") == {"prefix": "GC", "slug": "acme", "version": 1}
    assert parse_confirmation_filename("V2C-VAC-mvp-v3.md") == {"prefix": "V2C-VAC", "slug": "mvp", "version": 3}
    assert parse_confirmation_filename("5W-root-cause-v2.md") == {"prefix": "5W", "slug": "root-cause", "version": 2}
    assert parse_confirmation_filename("M1-v1.md") is None  # MVL 用单独解析
    assert parse_confirmation_filename("noext") is None


def test_parse_mvl_filename():
    assert parse_mvl_filename("M3-v2.md") == {"module": "M3", "version": 2}
    assert parse_mvl_filename("GC-x-v1.md") is None


def test_gate_id_regex():
    assert gate_id_regex("mvl").match("M1-GATE-01")
    assert not gate_id_regex("mvl").match("M1-GATE-1")   # 序号须两位
    assert not gate_id_regex("mvl").match("M7-GATE-01")  # 模块号越界
    assert gate_id_regex("gc").match("GC-GATE-03")
    assert gate_id_regex("5w").match("5W-GATE-04")
    with pytest.raises(ContractError):
        gate_id_regex("nope")


def test_validate_gate_ids():
    assert validate_gate_ids("GC-GATE-01 与 GC-GATE-02", "gc") == []
    assert validate_gate_ids("M1-GATE-01 M2-GATE-03", "mvl") == []
    assert validate_gate_ids("M1-GATE-1", "mvl") != []  # 一位序号被拦截
    # M7 不在 mvl 提取范围（M[1-6]），不产生格式问题（模块号合法性属语义，不越界）。
    assert validate_gate_ids("M7-GATE-01", "mvl") == []


def test_assert_filename_consistent():
    assert_filename_consistent("GC-acme-v2.md", canvas_id="gc", slug="acme", version=2)
    with pytest.raises(ContractError):
        assert_filename_consistent("GC-acme-v2.md", canvas_id="gc", slug="acme", version=3)
    with pytest.raises(ContractError):
        assert_filename_consistent("HMW-acme-v2.md", canvas_id="gc", slug="acme", version=2)
    with pytest.raises(ContractError):
        assert_filename_consistent("GC-other-v2.md", canvas_id="gc", slug="acme", version=2)


def test_assert_filename_consistent_mvl():
    assert_filename_consistent("M3-v2.md", canvas_id="mvl", slug="M3", version=2)
    with pytest.raises(ContractError):
        assert_filename_consistent("M3-v2.md", canvas_id="mvl", slug="M3", version=4)


def test_validate_version_marker():
    assert validate_version_marker("正文 v3 版本", 3) == []
    assert validate_version_marker("正文", 3) != []


def test_validate_governance_sections():
    assert validate_governance_sections("12.1 x\n12.2 y\n12.3 z") == []
    assert len(validate_governance_sections("12.1 x")) == 2
