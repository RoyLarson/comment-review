"""`no_harvester`: what the name corpus reports about a file it cannot harvest."""

from pathlib import Path

from comment_review.concordance.code_names import NO_HARVESTER, no_harvester


def test_a_freeform_file_is_a_known_gap_named_as_freeform():
    assert no_harvester(Path("b.js")) == f"b.js ({NO_HARVESTER} a freeform file)"


def test_a_language_with_a_reader_is_named():
    assert no_harvester(Path("b.rs")) == f"b.rs ({NO_HARVESTER} rust)"


def test_a_file_neither_read_nor_source_stays_unknown():
    assert no_harvester(Path("b.md")) == f"b.md ({NO_HARVESTER} unknown)"


def test_a_python_file_is_harvested():
    assert no_harvester(Path("b.py")) is None
