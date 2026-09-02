"""文件级 gate：产物存在性 / 版本一致性 / 旧 HTML 过期标记测试（§8）。"""

from skills._engine import files


def test_confirm_exists_and_list_versions(tmp_path):
    (tmp_path / "modules").mkdir()
    (tmp_path / "modules" / "GC-acme-v1.md").write_text("x")
    (tmp_path / "modules" / "GC-acme-v2.md").write_text("x")
    (tmp_path / "modules" / "GC-acme-gaps.md").write_text("x")

    assert files.confirm_exists(tmp_path, "GC", "acme", 2) is True
    assert files.confirm_exists(tmp_path, "GC", "acme", 3) is False
    assert files.gaps_exists(tmp_path, "GC", "acme") is True
    assert files.list_confirm_versions(tmp_path, "GC", "acme") == [1, 2]


def test_list_confirm_versions_ignores_other_slugs(tmp_path):
    (tmp_path / "modules").mkdir()
    (tmp_path / "modules" / "GC-acme-v1.md").write_text("x")
    (tmp_path / "modules" / "GC-other-v1.md").write_text("x")
    assert files.list_confirm_versions(tmp_path, "GC", "acme") == [1]


def test_html_exists(tmp_path):
    assert files.html_exists(tmp_path, "gc", "acme") is False
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "gc-canvas-acme.html").write_text("<html></html>")
    assert files.html_exists(tmp_path, "gc", "acme") is True
    assert files.index_exists(tmp_path, "gc") is False


def test_html_stale_marker_roundtrip(tmp_path):
    marker = files.mark_html_stale(tmp_path, "gc", "acme", stale_version=1)
    assert marker.exists()
    assert marker.name == "gc-canvas-acme.html.stale"
    assert files.is_html_stale(tmp_path, "gc", "acme") is True

    files.clear_html_stale(tmp_path, "gc", "acme")
    assert files.is_html_stale(tmp_path, "gc", "acme") is False
