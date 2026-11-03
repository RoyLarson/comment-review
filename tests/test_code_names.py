"""`code_names`: what the name corpus reports about a file it cannot harvest."""

from comment_review.concordance.code_names import NO_HARVESTER, code_names


def _gap_for(tmp_path, name: str) -> str:
    """The corpus's one gap row for a tree holding `name` alone."""
    target = tmp_path / name
    target.write_text("x\n", encoding="utf-8")
    _, unread = code_names([tmp_path], {target.resolve()})
    assert len(unread) == 1
    return unread[0]


def test_a_freeform_file_is_a_known_gap_named_as_freeform(tmp_path):
    row = _gap_for(tmp_path, "b.js")
    assert row.endswith(f"b.js ({NO_HARVESTER} a freeform file)")


def test_a_language_with_a_reader_is_named(tmp_path):
    assert _gap_for(tmp_path, "b.rs").endswith(f"b.rs ({NO_HARVESTER} rust)")


def test_a_file_neither_read_nor_source_stays_unknown(tmp_path):
    assert _gap_for(tmp_path, "b.md").endswith(f"b.md ({NO_HARVESTER} unknown)")
