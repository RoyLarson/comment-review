"""The brief states `ran` and the library-citation rule, and states each once.

! `ran` is the field the 2026-08-27 experiment ADDED -- an undescribed field is
an empty one, since no role has ever been told it exists. A `source` may cite
any place in the LIBRARY -- `docs/the-mark.md`, `docs/vocabulary.md` and
`decision-log.md Vocabulary: #15` are the source; this gate checks only that
the brief PUBLISHES it, and publishes it exactly once across `plugins/`.

    uv run pytest -q tests/gates/test_brief_states_the_rules.py
"""

from conftest import ROOT

BRIEF_PATH = (
    ROOT
    / "plugins"
    / "comment-review"
    / "skills"
    / "comment-review"
    / "references"
    / "reviewer-brief.md"
)


def test_the_brief_names_ran_and_says_what_it_is_for():
    brief = BRIEF_PATH.read_text(encoding="utf-8")
    assert "`ran`" in brief
    assert "library" in brief


def test_the_library_rule_is_stated_once():
    hits = [
        p
        for p in (ROOT / "plugins").rglob("*.md")
        if "may cite any place in the library" in p.read_text(encoding="utf-8").lower()
    ]
    assert len(hits) == 1, [str(p) for p in hits]
