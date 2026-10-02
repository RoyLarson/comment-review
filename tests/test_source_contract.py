import pytest
from helpers import a_correct, a_patch

from comment_review.desk.collator import cited_problems
from comment_review.desk.marks.rules import allowed
from comment_review.desk.proof.answer import read_answer
from comment_review.desk.proof.mark import read_mark
from comment_review.desk.proof.source import contract
from comment_review.flows.answers import contracts
from comment_review.flows.fill import quoted_sources

MALFORMED = [
    "m.py:1 | x = 1",
    {"verbatim": "x = 1"},
    {"cite": "m.py:1"},
    {"cite": " ", "verbatim": "x = 1"},
    {"cite": "m.py:1", "verbatim": " "},
    {"cite": 1, "verbatim": "x = 1"},
    {"cite": "m.py:1", "verbatim": 1},
]


@pytest.mark.parametrize("source", MALFORMED)
def test_answers_refuse_malformed_supplied_sources(source):
    answer, problems = read_answer(
        "m.py@b1",
        {
            "instruction": "correct",
            "question": "escalation",
            "address": "m.py@b1",
            "reason": "A correction.",
            "change": "# Changed.",
            "sources": [source],
        },
    )
    assert answer is None
    assert problems and all("source 1" in p for p in problems)


@pytest.mark.parametrize("source", MALFORMED)
def test_source_shape_is_refused_before_file_resolution(tmp_path, source):
    cache = {}
    problems = cited_problems("m.py@b1", [source], tmp_path, cache)
    assert problems and all("source 1" in p for p in problems)
    assert cache == {}


@pytest.mark.parametrize("source", MALFORMED)
def test_optional_mark_sources_still_require_complete_entries(source):
    wire = a_patch("m.py@b1", "Old.", "New.", "# New.")
    wire["sources"] = [source]
    mark, problems = read_mark("m.py@b1", wire)
    assert mark is None
    assert problems and all("source 1" in p for p in problems)


def test_source_presence_is_the_carrying_types_requirement():
    patch = a_patch("m.py@b1", "Old.", "New.", "# New.")
    patch.pop("sources", None)
    assert read_mark("m.py@b1", patch)[1] == []
    correct = a_correct("m.py@b1")
    correct.pop("sources", None)
    assert "at least one" in read_mark("m.py@b1", correct)[1][0]
    wire = dict(
        address="m.py@b1",
        instruction="correct",
        question="escalation",
        reason="A correction.",
        change="# Changed.",
    )
    assert read_answer("m.py@b1", wire)[1] == []


def test_mixed_entries_keep_positions_and_resolve_valid_evidence(tmp_path):
    (tmp_path / "m.py").write_text("x = 1\n", encoding="utf-8")
    valid = {"cite": "m.py:1", "verbatim": "x = 1", "ran": "a command"}
    cache = {}
    problems = cited_problems("m.py@b1", [valid, {}, valid], tmp_path, cache)
    assert problems and all("source 2" in p for p in problems)
    assert cache


def test_answer_roundtrip_needs_no_checkout_and_keeps_optional_fields():
    wire = dict(
        address="m.py@b1",
        instruction="correct",
        question="escalation",
        reason="A correction.",
        change="# Changed.",
        sources=[{"cite": "missing.py:1", "verbatim": "x", "ran": "cmd"}],
    )
    answer, problems = read_answer("m.py@b1", wire)
    assert answer is not None and not problems
    reread, problems = read_answer("m.py@b1", answer.serialize())
    assert reread == answer and not problems


def test_cite_only_completion_and_explicit_bad_quote_have_distinct_intakes(tmp_path):
    (tmp_path / "m.py").write_text("x = 1\n", encoding="utf-8")
    quoted, problems = quoted_sources(tmp_path, [{"cite": "m.py:1"}])
    assert quoted == [{"cite": "m.py:1", "verbatim": "x = 1"}] and not problems
    quoted, problems = quoted_sources(
        tmp_path, [{"cite": "missing.py:1", "verbatim": ""}]
    )
    assert quoted is None and "needs `verbatim`" in problems[0]


def test_contract_returns_independent_field_lists():
    published = contract()
    assert published == {"required": ["cite", "verbatim"], "optional": ["ran"]}
    published["required"].clear()
    assert contract()["required"] == ["cite", "verbatim"]


def test_mark_and_answer_contracts_publish_the_same_source_fields():
    assert allowed()["source_keys"] == contract()
    assert all(one["source_keys"] == contract() for one in contracts().values())


def test_mark_roundtrip_keeps_sources_without_resolving_the_checkout():
    wire = a_patch("m.py@b1", "Old.", "New.", "# New.")
    wire["sources"] = [{"cite": "missing.py:1", "verbatim": "x", "ran": "cmd"}]
    mark, problems = read_mark("m.py@b1", wire)
    assert mark is not None and not problems
    reread, problems = read_mark("m.py@b1", mark.serialize())
    assert reread == mark and not problems
