"""page -> galley: every cue type, every operation, and what must NOT change.

The second chain, and it starts from a PAGE read fresh -- never from a binder.
Roy, 2026-08-25: the workflow *"will take something and determine that and then
roll forward re getting the page because it needs the full page."*

!! COMPLETENESS IS THE HALF THAT IS EASY TO MISS. "The edit landed" is half an
assertion; the other half is that NOTHING ELSE MOVED. Every case below states
the exact set of places allowed to differ, so a change that also disturbed a
neighbour fails even though its own place is right.
"""

import pytest
from conftest import SAMPLE, build, by_cue

from comment_review.results.compositor import set_page
from comment_review.results.galley import reset

#: A replacement that is legal in each series. A `c` carries its own separator
#: -- the compositor joins it to the code -- and an `a` carries its indentation.
REPLACEMENT = {
    "a": '    """REPLACED."""',
    "b": "# REPLACED",
    "c": "  # REPLACED",
    "f": "#!/usr/bin/env REPLACED",
}


def places(page):
    """`(filled, absent)` -- one cue per series in each state, discovered.

    ! DISCOVERED, NOT HARDCODED. A hardcoded cue is a fixture asserting what the
    walk emitted last time someone looked; this asks the page.
    """
    filled: dict[str, str] = {}
    absent: dict[str, str] = {}
    for c, b in by_cue(page).items():
        table = filled if any(x.strip() for x in b.raw_lines) else absent
        table.setdefault(c[0], c)
    return filled, absent


def lines_by_cue(page) -> dict[str, list[str]]:
    return {c: list(b.raw_lines) for c, b in by_cue(page).items()}


def leading_by_symbol(page) -> dict[str, list[str]]:
    return {b.symbol: list(b.raw_lines) for b in page.paragraphs if b.symbol}


FILLED, ABSENT = places(build(SAMPLE))
SERIES = sorted(REPLACEMENT)


def test_the_sample_offers_a_filled_and_an_absent_place_in_every_series():
    """Every case below is parametrised over these, so an empty one would make
    a whole column of the matrix vacuous."""
    assert set(FILLED) == set(SERIES)
    assert set(ABSENT) == set(SERIES)


class TestModify:
    @pytest.mark.parametrize("series", SERIES)
    def test_the_place_takes_the_new_text(self, sample, series):
        cue = FILLED[series]
        assert reset(sample, {f"m.py@{cue}": REPLACEMENT[series]}) == []
        assert by_cue(sample)[cue].raw_lines == [REPLACEMENT[series]]

    @pytest.mark.parametrize("series", SERIES)
    def test_NOTHING_ELSE_on_the_page_moves(self, sample, series):
        cue = FILLED[series]
        before = lines_by_cue(build(SAMPLE))
        reset(sample, {f"m.py@{cue}": REPLACEMENT[series]})
        after = lines_by_cue(sample)
        assert {c for c in after if after[c] != before[c]} == {cue}

    @pytest.mark.parametrize("series", SERIES)
    def test_no_fence_moves(self, sample, series):
        before = leading_by_symbol(build(SAMPLE))
        reset(sample, {f"m.py@{FILLED[series]}": REPLACEMENT[series]})
        assert leading_by_symbol(sample) == before

    @pytest.mark.parametrize("series", SERIES)
    def test_the_new_text_reaches_the_composed_file(self, sample, series):
        reset(sample, {f"m.py@{FILLED[series]}": REPLACEMENT[series]})
        assert "REPLACED" in set_page(sample)

    def test_a_multi_line_replacement_does_not_eat_the_line_below(self, sample):
        """A paragraph hands back its lines and the next place is set NEXT, so
        growing one moves nothing -- the property that made the line-arithmetic
        splice unnecessary."""
        cue = FILLED["b"]
        reset(sample, {f"m.py@{cue}": "# one\n# two\n# three"})
        out = set_page(sample)
        assert "# one\n# two\n# three\n" in out
        assert "def f(x):" in out


class TestDrop:
    """An empty string is the ONLY vacation -- `galley.reset` refuses any other
    falsy value, because a `null` from a failed serialisation upstream would
    otherwise read as "the author asked to delete this"."""

    @pytest.mark.parametrize("series", SERIES)
    def test_the_place_is_emptied(self, sample, series):
        cue = FILLED[series]
        assert reset(sample, {f"m.py@{cue}": ""}) == []
        assert by_cue(sample)[cue].raw_lines == []

    @pytest.mark.parametrize("series", SERIES)
    def test_the_place_still_EXISTS_and_keeps_its_address(self, sample, series):
        """Places are involatile. Roy: *"having an empty sentinel is the key,
        not that the place disappears."* An `add` can fill what a `drop`
        emptied, which needs the place to still be citable."""
        cue = FILLED[series]
        before = by_cue(sample)[cue]
        anchor, address = before.anchor, before.address
        reset(sample, {f"m.py@{cue}": ""})
        after = by_cue(sample)[cue]
        assert after.address == address
        assert after.anchor == anchor
        assert cue in sample.cues.reading

    @pytest.mark.parametrize("series", SERIES)
    def test_only_the_place_and_the_fence_it_OWNS_change(self, sample, series):
        """The blank below a dropped paragraph goes with it -- otherwise the
        space it introduced stands over whatever follows.

        ! A `c` OWNS NONE. It sits beside code, so the blank below separates
        that CODE from what follows and was never the comment's to lose.
        """
        cue = FILLED[series]
        fresh = build(SAMPLE)
        before, before_d = lines_by_cue(fresh), leading_by_symbol(fresh)
        reset(sample, {f"m.py@{cue}": ""})
        after, after_d = lines_by_cue(sample), leading_by_symbol(sample)

        assert {c for c in after if after[c] != before[c]} == {cue}
        moved = {s for s in after_d if after_d[s] != before_d[s]}
        owned = sample.leading.get(cue, "")
        expected = {owned} if owned and not cue.startswith("c") else set()
        assert moved == expected

    def test_a_c_keeps_the_blank_below_its_code(self, sample):
        """Stated separately because `prove_unchanged` cannot see the
        difference -- the AST is identical either way -- so getting it wrong
        would land silently."""
        cue = FILLED["c"]
        before = leading_by_symbol(build(SAMPLE))
        reset(sample, {f"m.py@{cue}": ""})
        assert leading_by_symbol(sample) == before

    @pytest.mark.parametrize("series", SERIES)
    def test_the_prose_is_gone_from_the_composed_file(self, sample, series):
        cue = FILLED[series]
        was = "\n".join(by_cue(build(SAMPLE))[cue].raw_lines).strip()
        reset(sample, {f"m.py@{cue}": ""})
        assert was
        assert was not in set_page(sample)


class TestAddToAnAbsentPlace:
    """The reason every place is addressed, filled or not: an `add` cites the
    place where prose BELONGS and does not yet exist."""

    @pytest.mark.parametrize("series", SERIES)
    def test_the_absent_place_takes_the_text(self, sample, series):
        cue = ABSENT[series]
        assert reset(sample, {f"m.py@{cue}": REPLACEMENT[series]}) == []
        assert by_cue(sample)[cue].raw_lines == [REPLACEMENT[series]]

    @pytest.mark.parametrize("series", SERIES)
    def test_NOTHING_ELSE_on_the_page_moves(self, sample, series):
        cue = ABSENT[series]
        before = lines_by_cue(build(SAMPLE))
        reset(sample, {f"m.py@{cue}": REPLACEMENT[series]})
        after = lines_by_cue(sample)
        assert {c for c in after if after[c] != before[c]} == {cue}

    @pytest.mark.parametrize("series", SERIES)
    def test_the_added_prose_reaches_the_composed_file(self, sample, series):
        cue = ABSENT[series]
        before = set_page(build(SAMPLE))
        reset(sample, {f"m.py@{cue}": REPLACEMENT[series]})
        after = set_page(sample)
        assert "REPLACED" in after
        assert after != before

    @pytest.mark.parametrize("series", SERIES)
    def test_the_file_grows_by_exactly_what_was_added(self, sample, series):
        """An `a`, `b` or `f` adds its own line; a `c` joins the code line that
        is already there, so it adds none."""
        cue = ABSENT[series]
        before = len(set_page(build(SAMPLE)).splitlines())
        reset(sample, {f"m.py@{cue}": REPLACEMENT[series]})
        after = len(set_page(sample).splitlines())
        assert after - before == (0 if series == "c" else 1)


class TestDropThenAddIsAFullCycle:
    """The two halves compose: a place emptied is a place that can be filled
    again, which is what makes `move` two edits rather than a special case."""

    @pytest.mark.parametrize("series", SERIES)
    def test_a_dropped_place_can_be_filled_again(self, sample, series):
        cue = FILLED[series]
        reset(sample, {f"m.py@{cue}": ""})
        assert reset(sample, {f"m.py@{cue}": REPLACEMENT[series]}) == []
        assert by_cue(sample)[cue].raw_lines == [REPLACEMENT[series]]

    @pytest.mark.parametrize("series", SERIES)
    def test_restoring_the_ORIGINAL_text_restores_the_file(self, sample, series):
        """The strongest form: out and back leaves the page where it started.

        ! `c` AND ANY OWNER OF A FENCE ARE EXCLUDED FROM THE FILE COMPARISON --
        a drop vacates the fence too, and putting the prose back does not put
        the blank back. That is the ruled behaviour, not a defect, so the
        assertion here is about the PLACE rather than the whole file.
        """
        cue = FILLED[series]
        original = list(by_cue(build(SAMPLE))[cue].raw_lines)
        reset(sample, {f"m.py@{cue}": ""})
        reset(sample, {f"m.py@{cue}": "\n".join(original)})
        assert by_cue(sample)[cue].raw_lines == original


class TestWhatTheGalleyRefuses:
    def test_an_address_the_page_does_not_carry(self, sample):
        problems = reset(sample, {"m.py@b99": "# nowhere"})
        assert len(problems) == 1
        assert "no such place" in problems[0]

    @pytest.mark.parametrize("value", [None, 0, 123, [], {}, ["# a line"], True])
    def test_a_replacement_that_is_not_TEXT(self, sample, value):
        """Only an empty string is a drop. A `null` arriving from a key that
        failed to serialise would otherwise be read as a deletion, at exit 0."""
        problems = reset(sample, {f"m.py@{FILLED['b']}": value})
        assert len(problems) == 1
        assert "must be text" in problems[0]

    @pytest.mark.parametrize("value", [None, 0, 123, [], {}])
    def test_a_refused_replacement_changes_NOTHING(self, sample, value):
        before = lines_by_cue(build(SAMPLE))
        reset(sample, {f"m.py@{FILLED['b']}": value})
        assert lines_by_cue(sample) == before

    def test_one_bad_edit_does_not_stop_a_good_one(self, sample):
        """Each edit is placed on its own; the return value names what could
        not be placed rather than abandoning the batch."""
        problems = reset(
            sample,
            {"m.py@b99": "# nowhere", f"m.py@{FILLED['b']}": "# REPLACED"},
        )
        assert len(problems) == 1
        assert by_cue(sample)[FILLED["b"]].raw_lines == ["# REPLACED"]


class TestSeveralEditsAtOnce:
    def test_every_series_can_be_edited_in_one_pass(self, sample):
        edits = {f"m.py@{FILLED[s]}": REPLACEMENT[s] for s in SERIES}
        assert reset(sample, edits) == []
        for s in SERIES:
            assert by_cue(sample)[FILLED[s]].raw_lines == [REPLACEMENT[s]]

    def test_editing_every_place_leaves_the_page_still_composable(self, sample):
        edits = {f"m.py@{FILLED[s]}": REPLACEMENT[s] for s in SERIES}
        edits |= {f"m.py@{ABSENT[s]}": REPLACEMENT[s] for s in SERIES}
        assert reset(sample, edits) == []
        out = set_page(sample)
        assert out.count("REPLACED") == len(edits)
