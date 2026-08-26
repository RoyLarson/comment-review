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
from conftest import REPLACEMENT, SAMPLE, build, by_cue

from comment_review.results.compositor import set_page
from comment_review.results.galley import reset


def places(page):
    """`(filled, absent)` -- EVERY cue of each series, in each state, discovered.

    ! DISCOVERED, NOT HARDCODED. A hardcoded cue is a fixture asserting what the
    walk emitted last time someone looked; this asks the page.

    !! IT KEPT ONE CUE PER SERIES UNTIL 2026-08-26, via `setdefault`, so 8 of
    the sample's 14 places were exercised and the other 6 were never set at all.
    Roy asked for every cue position on the page; what it picked for `b` was
    `b1`, which round trips, while `b0` -- the one that did not -- was never
    reached. A matrix that selects a representative can select past the defect.
    """
    filled: dict[str, list[str]] = {}
    absent: dict[str, list[str]] = {}
    for c, b in by_cue(page).items():
        table = filled if any(x.strip() for x in b.raw_lines) else absent
        table.setdefault(c[0], []).append(c)
    return filled, absent


def lines_by_cue(page) -> dict[str, list[str]]:
    return {c: list(b.raw_lines) for c, b in by_cue(page).items()}


def leading_by_symbol(page) -> dict[str, list[str]]:
    return {b.symbol: list(b.raw_lines) for b in page.paragraphs if b.symbol}


FILLED, ABSENT = places(build(SAMPLE))
SERIES = sorted(REPLACEMENT)
#: `(series, cue)` for every addressed place on the sample, so a case runs once
#: per PLACE rather than once per series. The series travels with the cue
#: because `REPLACEMENT` is what a legal edit for that series looks like.
FILLED_PLACES = [(s, c) for s in SERIES for c in FILLED.get(s, [])]
ABSENT_PLACES = [(s, c) for s in SERIES for c in ABSENT.get(s, [])]


def test_the_sample_offers_a_filled_and_an_absent_place_in_every_series():
    """Every case below is parametrised over these, so an empty one would make
    a whole column of the matrix vacuous."""
    assert set(FILLED) == set(SERIES)
    assert set(ABSENT) == set(SERIES)


def test_every_addressed_place_on_the_sample_is_under_test():
    """!! THE MATRIX IS COMPLETE, AND THIS IS WHAT SAYS SO. Without it, a
    narrowing of `places` would quietly shrink the matrix and every case below
    would still pass -- which is how `b0` went unexercised."""
    assert len(FILLED_PLACES) + len(ABSENT_PLACES) == len(by_cue(build(SAMPLE)))


class TestModify:
    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_the_place_takes_the_new_text(self, sample, series, cue):
        assert reset(sample, {cue: REPLACEMENT[series]}) == []
        assert by_cue(sample)[cue].raw_lines == [REPLACEMENT[series]]

    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_NOTHING_ELSE_on_the_page_moves(self, sample, series, cue):
        before = lines_by_cue(build(SAMPLE))
        reset(sample, {cue: REPLACEMENT[series]})
        after = lines_by_cue(sample)
        assert {c for c in after if after[c] != before[c]} == {cue}

    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_no_fence_moves(self, sample, series, cue):
        before = leading_by_symbol(build(SAMPLE))
        reset(sample, {cue: REPLACEMENT[series]})
        assert leading_by_symbol(sample) == before

    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_the_new_text_reaches_the_composed_file(self, sample, series, cue):
        reset(sample, {cue: REPLACEMENT[series]})
        assert "REPLACED" in set_page(sample)

    def test_a_multi_line_replacement_does_not_eat_the_line_below(self, sample):
        """A paragraph hands back its lines and the next place is set NEXT, so
        growing one moves nothing -- the property that made the line-arithmetic
        splice unnecessary."""
        cue = FILLED["b"][0]
        reset(sample, {cue: "# one\n# two\n# three"})
        out = set_page(sample)
        assert "# one\n# two\n# three\n" in out
        assert "def f(x):" in out


class TestDrop:
    """`None` is the ONLY vacation -- `galley.reset` refuses any other value,
    including an empty string, because a `""` from a failed serialisation
    upstream would otherwise be indistinguishable from a deliberate
    deletion."""

    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_the_place_is_emptied(self, sample, series, cue):
        assert reset(sample, {cue: None}) == []
        assert by_cue(sample)[cue].raw_lines == []

    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_the_place_still_EXISTS_and_keeps_its_address(self, sample, series, cue):
        """Places are involatile. Roy: *"having an empty sentinel is the key,
        not that the place disappears."* An `add` can fill what a `drop`
        emptied, which needs the place to still be citable."""
        before = by_cue(sample)[cue]
        anchor, address = before.anchor, before.address
        reset(sample, {cue: None})
        after = by_cue(sample)[cue]
        assert after.address == address
        assert after.anchor == anchor
        assert cue in sample.cues.reading

    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_only_the_place_and_the_fence_it_OWNS_change(self, sample, series, cue):
        """The blank below a dropped paragraph goes with it -- otherwise the
        space it introduced stands over whatever follows.

        ! A `c` OWNS NONE. It sits beside code, so the blank below separates
        that CODE from what follows and was never the comment's to lose.
        """
        fresh = build(SAMPLE)
        before, before_d = lines_by_cue(fresh), leading_by_symbol(fresh)
        reset(sample, {cue: None})
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
        cue = FILLED["c"][0]
        before = leading_by_symbol(build(SAMPLE))
        reset(sample, {cue: None})
        assert leading_by_symbol(sample) == before

    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_the_prose_is_gone_from_the_composed_file(self, sample, series, cue):
        was = "\n".join(by_cue(build(SAMPLE))[cue].raw_lines).strip()
        reset(sample, {cue: None})
        assert was
        assert was not in set_page(sample)


class TestAddToAnAbsentPlace:
    """The reason every place is addressed, filled or not: an `add` cites the
    place where prose BELONGS and does not yet exist."""

    @pytest.mark.parametrize("series,cue", ABSENT_PLACES)
    def test_the_absent_place_takes_the_text(self, sample, series, cue):
        assert reset(sample, {cue: REPLACEMENT[series]}) == []
        assert by_cue(sample)[cue].raw_lines == [REPLACEMENT[series]]

    @pytest.mark.parametrize("series,cue", ABSENT_PLACES)
    def test_NOTHING_ELSE_on_the_page_moves(self, sample, series, cue):
        before = lines_by_cue(build(SAMPLE))
        reset(sample, {cue: REPLACEMENT[series]})
        after = lines_by_cue(sample)
        assert {c for c in after if after[c] != before[c]} == {cue}

    @pytest.mark.parametrize("series,cue", ABSENT_PLACES)
    def test_the_added_prose_reaches_the_composed_file(self, sample, series, cue):
        before = set_page(build(SAMPLE))
        reset(sample, {cue: REPLACEMENT[series]})
        after = set_page(sample)
        assert "REPLACED" in after
        assert after != before

    @pytest.mark.parametrize("series,cue", ABSENT_PLACES)
    def test_nothing_that_was_on_the_page_is_lost(self, sample, series, cue):
        """An `a` or `f` adds its own line and a `c` joins the code line already
        there, so the file never SHRINKS and every original line survives.

        ! THE EXACT GROWTH IS NOT ASSERTED HERE, and that is deliberate. A `b`
        may also bring a leading -- see the round trip below -- and stating when
        would mean writing `compositor.set_page`'s condition a second time, in
        the one place that is supposed to be able to disagree with it.
        """
        before = set_page(build(SAMPLE)).splitlines()
        reset(sample, {cue: REPLACEMENT[series]})
        after = set_page(sample).splitlines()
        assert len(after) >= len(before)
        # ! TAKEN BACK OUT RATHER THAN FILTERED. A `c` is APPENDED to its code
        # line, so dropping every line that mentions the replacement deletes
        # `    return y` along with it and reports the code as lost.
        kept = [
            stripped
            for line in after
            if (stripped := line.replace(REPLACEMENT[series], "").rstrip()).strip()
        ]
        assert [line for line in before if line.strip()] == kept

    @pytest.mark.parametrize("series,cue", ABSENT_PLACES)
    def test_the_added_prose_RE_READS_at_the_cue_it_was_added_to(
        self, sample, series, cue
    ):
        """!! THE PROPERTY THE WHOLE LEADING RULE EXISTS FOR. An `add` is only
        real if the place it cited is the place that gives the prose back --
        otherwise the write chain refuses its own draft at `reread`, which is
        how `b0` was found.

        ! `b4` IS THE KNOWN EXCEPTION and is xfailed rather than asserted: the
        closing gap and `f1` are emitted at the same `<eof>` trigger, so prose
        set at either comes back at `f1`. That is
        `TODO/foot-of-file-two-places.md` -- backend, awaiting a ruling -- and
        no leading can separate them, because back matter is the run AFTER the
        last blank.
        """
        if cue == "b4":
            pytest.xfail("foot-of-file-two-places.md: b4 and f1 share <eof>")
        reset(sample, {cue: REPLACEMENT[series]})
        reread = by_cue(build(set_page(sample)))
        assert cue in reread
        assert any("REPLACED" in line for line in reread[cue].raw_lines)


class TestDropThenAddIsAFullCycle:
    """The two halves compose: a place emptied is a place that can be filled
    again, which is what makes `move` two edits rather than a special case."""

    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_a_dropped_place_can_be_filled_again(self, sample, series, cue):
        reset(sample, {cue: None})
        assert reset(sample, {cue: REPLACEMENT[series]}) == []
        assert by_cue(sample)[cue].raw_lines == [REPLACEMENT[series]]

    @pytest.mark.parametrize("series,cue", FILLED_PLACES)
    def test_restoring_the_ORIGINAL_text_restores_the_file(self, sample, series, cue):
        """The strongest form: out and back leaves the page where it started.

        ! `c` AND ANY OWNER OF A FENCE ARE EXCLUDED FROM THE FILE COMPARISON --
        a drop vacates the fence too, and putting the prose back does not put
        the blank back. That is the ruled behaviour, not a defect, so the
        assertion here is about the PLACE rather than the whole file.
        """
        original = list(by_cue(build(SAMPLE))[cue].raw_lines)
        reset(sample, {cue: None})
        reset(sample, {cue: "\n".join(original)})
        assert by_cue(sample)[cue].raw_lines == original


class TestWhatTheGalleyRefuses:
    def test_an_address_the_page_does_not_carry(self, sample):
        problems = reset(sample, {"b99": "# nowhere"})
        assert len(problems) == 1
        assert "no such place" in problems[0]

    @pytest.mark.parametrize("value", [0, 123, [], {}, ["# a line"], True, ""])
    def test_a_replacement_that_is_not_TEXT(self, sample, value):
        """Only `None` is a drop. A `""` arriving from a key that failed to
        serialise would otherwise be read as a deletion, at exit 0."""
        problems = reset(sample, {FILLED["b"][0]: value})
        assert len(problems) == 1
        if isinstance(value, str):
            assert "not a delete" in problems[0]
        else:
            assert "must be text" in problems[0]

    @pytest.mark.parametrize("value", [0, 123, [], {}, ""])
    def test_a_refused_replacement_changes_NOTHING(self, sample, value):
        before = lines_by_cue(build(SAMPLE))
        reset(sample, {FILLED["b"][0]: value})
        assert lines_by_cue(sample) == before

    def test_one_bad_edit_does_not_stop_a_good_one(self, sample):
        """Each edit is placed on its own; the return value names what could
        not be placed rather than abandoning the batch."""
        problems = reset(
            sample,
            {"b99": "# nowhere", FILLED["b"][0]: "# REPLACED"},
        )
        assert len(problems) == 1
        assert by_cue(sample)[FILLED["b"][0]].raw_lines == ["# REPLACED"]


class TestSeveralEditsAtOnce:
    def test_every_FILLED_place_can_be_edited_in_one_pass(self, sample):
        edits = {c: REPLACEMENT[s] for s, c in FILLED_PLACES}
        assert reset(sample, edits) == []
        for _, c in FILLED_PLACES:
            assert by_cue(sample)[c].raw_lines == [REPLACEMENT[c[0]]]

    def test_editing_EVERY_place_leaves_the_page_still_composable(self, sample):
        """Every one of the sample's places, filled and absent alike, set in a
        single pass -- the widest thing the galley is asked to do."""
        edits = {c: REPLACEMENT[s] for s, c in FILLED_PLACES}
        edits |= {c: REPLACEMENT[s] for s, c in ABSENT_PLACES}
        assert reset(sample, edits) == []
        out = set_page(sample)
        assert out.count("REPLACED") == len(edits)
