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
        assert reset(sample, {cue: REPLACEMENT[series]}) == []
        assert by_cue(sample)[cue].raw_lines == [REPLACEMENT[series]]

    @pytest.mark.parametrize("series", SERIES)
    def test_NOTHING_ELSE_on_the_page_moves(self, sample, series):
        cue = FILLED[series]
        before = lines_by_cue(build(SAMPLE))
        reset(sample, {cue: REPLACEMENT[series]})
        after = lines_by_cue(sample)
        assert {c for c in after if after[c] != before[c]} == {cue}

    @pytest.mark.parametrize("series", SERIES)
    def test_no_fence_moves(self, sample, series):
        before = leading_by_symbol(build(SAMPLE))
        reset(sample, {FILLED[series]: REPLACEMENT[series]})
        assert leading_by_symbol(sample) == before

    @pytest.mark.parametrize("series", SERIES)
    def test_the_new_text_reaches_the_composed_file(self, sample, series):
        reset(sample, {FILLED[series]: REPLACEMENT[series]})
        assert "REPLACED" in set_page(sample)

    def test_a_multi_line_replacement_does_not_eat_the_line_below(self, sample):
        """A paragraph hands back its lines and the next place is set NEXT, so
        growing one moves nothing -- the property that made the line-arithmetic
        splice unnecessary."""
        cue = FILLED["b"]
        reset(sample, {cue: "# one\n# two\n# three"})
        out = set_page(sample)
        assert "# one\n# two\n# three\n" in out
        assert "def f(x):" in out


class TestDrop:
    """`None` is the ONLY vacation -- `galley.reset` refuses any other value,
    including an empty string, because a `""` from a failed serialisation
    upstream would otherwise be indistinguishable from a deliberate
    deletion."""

    @pytest.mark.parametrize("series", SERIES)
    def test_the_place_is_emptied(self, sample, series):
        cue = FILLED[series]
        assert reset(sample, {cue: None}) == []
        assert by_cue(sample)[cue].raw_lines == []

    @pytest.mark.parametrize("series", SERIES)
    def test_the_place_still_EXISTS_and_keeps_its_address(self, sample, series):
        """Places are involatile. Roy: *"having an empty sentinel is the key,
        not that the place disappears."* An `add` can fill what a `drop`
        emptied, which needs the place to still be citable."""
        cue = FILLED[series]
        before = by_cue(sample)[cue]
        anchor, address = before.anchor, before.address
        reset(sample, {cue: None})
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
        cue = FILLED["c"]
        before = leading_by_symbol(build(SAMPLE))
        reset(sample, {cue: None})
        assert leading_by_symbol(sample) == before

    @pytest.mark.parametrize("series", SERIES)
    def test_the_prose_is_gone_from_the_composed_file(self, sample, series):
        cue = FILLED[series]
        was = "\n".join(by_cue(build(SAMPLE))[cue].raw_lines).strip()
        reset(sample, {cue: None})
        assert was
        assert was not in set_page(sample)


class TestAddToAnAbsentPlace:
    """The reason every place is addressed, filled or not: an `add` cites the
    place where prose BELONGS and does not yet exist."""

    @pytest.mark.parametrize("series", SERIES)
    def test_the_absent_place_takes_the_text(self, sample, series):
        cue = ABSENT[series]
        assert reset(sample, {cue: REPLACEMENT[series]}) == []
        assert by_cue(sample)[cue].raw_lines == [REPLACEMENT[series]]

    @pytest.mark.parametrize("series", SERIES)
    def test_NOTHING_ELSE_on_the_page_moves(self, sample, series):
        cue = ABSENT[series]
        before = lines_by_cue(build(SAMPLE))
        reset(sample, {cue: REPLACEMENT[series]})
        after = lines_by_cue(sample)
        assert {c for c in after if after[c] != before[c]} == {cue}

    @pytest.mark.parametrize("series", SERIES)
    def test_the_added_prose_reaches_the_composed_file(self, sample, series):
        cue = ABSENT[series]
        before = set_page(build(SAMPLE))
        reset(sample, {cue: REPLACEMENT[series]})
        after = set_page(sample)
        assert "REPLACED" in after
        assert after != before

    @pytest.mark.parametrize("series", SERIES)
    def test_the_file_grows_by_exactly_what_was_added(self, sample, series):
        """An `a`, `b` or `f` adds its own line; a `c` joins the code line that
        is already there, so it adds none."""
        cue = ABSENT[series]
        before = len(set_page(build(SAMPLE)).splitlines())
        reset(sample, {cue: REPLACEMENT[series]})
        after = len(set_page(sample).splitlines())
        assert after - before == (0 if series == "c" else 1)


class TestDropThenAddIsAFullCycle:
    """The two halves compose: a place emptied is a place that can be filled
    again, which is what makes `move` two edits rather than a special case."""

    @pytest.mark.parametrize("series", SERIES)
    def test_a_dropped_place_can_be_filled_again(self, sample, series):
        cue = FILLED[series]
        reset(sample, {cue: None})
        assert reset(sample, {cue: REPLACEMENT[series]}) == []
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
        problems = reset(sample, {FILLED["b"]: value})
        assert len(problems) == 1
        if isinstance(value, str):
            assert "not a delete" in problems[0]
        else:
            assert "must be text" in problems[0]

    @pytest.mark.parametrize("value", [0, 123, [], {}, ""])
    def test_a_refused_replacement_changes_NOTHING(self, sample, value):
        before = lines_by_cue(build(SAMPLE))
        reset(sample, {FILLED["b"]: value})
        assert lines_by_cue(sample) == before

    def test_one_bad_edit_does_not_stop_a_good_one(self, sample):
        """Each edit is placed on its own; the return value names what could
        not be placed rather than abandoning the batch."""
        problems = reset(
            sample,
            {"b99": "# nowhere", FILLED["b"]: "# REPLACED"},
        )
        assert len(problems) == 1
        assert by_cue(sample)[FILLED["b"]].raw_lines == ["# REPLACED"]


class TestSeveralEditsAtOnce:
    def test_every_series_can_be_edited_in_one_pass(self, sample):
        edits = {FILLED[s]: REPLACEMENT[s] for s in SERIES}
        assert reset(sample, edits) == []
        for s in SERIES:
            assert by_cue(sample)[FILLED[s]].raw_lines == [REPLACEMENT[s]]

    def test_editing_every_place_leaves_the_page_still_composable(self, sample):
        edits = {FILLED[s]: REPLACEMENT[s] for s in SERIES}
        edits |= {ABSENT[s]: REPLACEMENT[s] for s in SERIES}
        assert reset(sample, edits) == []
        out = set_page(sample)
        assert out.count("REPLACED") == len(edits)


class TestTheCommandRefusesAStaleFile:
    """CRITICAL, measured 2026-08-25: `commands/galley.py` asked NOTHING about
    staleness. The `drifted` mechanism that used to ask it, paragraph by
    paragraph, went with the line arithmetic and nothing replaced it HERE --
    the replacement is the recorded-sha comparison in `flows/proof_setter.py`,
    which this command never calls. So a census taken before `def f():` was
    renamed still placed every edit by cue, wrote the galley and printed
    `1 page(s) set, 0 edit(s) refused` at exit 0.

    ! `SKILL.md` still wires stage 7a to this command, so it is live."""

    def _run(self, tmp_path, monkeypatch, capsys, source: str, edits_text=None):
        """Census `SAMPLE`, put `source` on disk, then run the command."""
        import json

        from comment_review.binder.binder import bind
        from comment_review.commands import galley as cmd

        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "m.py").write_text(source, encoding="utf-8", newline="")
        census = tmp_path / "census.json"
        census.write_text(
            json.dumps(bind([build(SAMPLE)])), encoding="utf-8", newline=""
        )
        edits = tmp_path / "edits.json"
        edits.write_text(
            json.dumps({f"m.py@{FILLED['b']}": "# REPLACED"})
            if edits_text is None
            else edits_text,
            encoding="utf-8",
            newline="",
        )
        monkeypatch.setattr(
            "sys.argv",
            [
                "galley",
                "--repo",
                str(repo),
                "--census",
                str(census),
                "--edits",
                str(edits),
                "--out",
                str(tmp_path / "out"),
            ],
        )
        return cmd.main(), capsys.readouterr().out

    def test_a_RENAMED_DECLARATION_since_the_census_is_REFUSED(
        self, tmp_path, monkeypatch, capsys
    ):
        renamed = SAMPLE.replace("def f(x):", "def RENAMED(x):")
        assert renamed != SAMPLE
        code, out = self._run(tmp_path, monkeypatch, capsys, renamed)
        assert code == 1
        assert "REFUSED" in out
        assert "changed since it was censused" in out
        assert "0 page(s) set" in out

    def test_NO_GALLEY_is_written_for_a_stale_file(self, tmp_path, monkeypatch, capsys):
        renamed = SAMPLE.replace("def f(x):", "def RENAMED(x):")
        self._run(tmp_path, monkeypatch, capsys, renamed)
        assert not (tmp_path / "out" / "m.py").exists()

    def test_a_STALE_file_that_ALSO_TRIPS_Refused_is_refused_not_raised(
        self, tmp_path, monkeypatch, capsys
    ):
        """IMPORTANT, measured 2026-08-26: the sha comparison sat BELOW
        `page_for`, which raises `exceptions.Refused` and has no handler in this
        command -- so a file that was BOTH stale and unpageable died as a
        traceback before reaching the comparison that would have refused it with
        a reason. `read_source` already supplied the sha, so nothing had to be
        parsed to ask the question."""
        from comment_review.commands import galley as cmd
        from comment_review.machine import exceptions

        def refusing_page_for(*args, **kwargs):
            raise exceptions.Refused("b0: a `c` place whose anchor has no line")

        monkeypatch.setattr(cmd, "page_for", refusing_page_for)
        renamed = SAMPLE.replace("def f(x):", "def RENAMED(x):")
        assert renamed != SAMPLE
        code, out = self._run(tmp_path, monkeypatch, capsys, renamed)
        assert code == 1
        assert "changed since it was censused" in out

    def test_an_UNCHANGED_file_still_sets(self, tmp_path, monkeypatch, capsys):
        """! The other half: a check that refused everything would pass the
        two cases above and be worth nothing."""
        code, out = self._run(tmp_path, monkeypatch, capsys, SAMPLE)
        assert code == 0
        assert "1 page(s) set, 0 edit(s) refused" in out
        assert "# REPLACED" in (tmp_path / "out" / "m.py").read_text(encoding="utf-8")


class TestTheCommandReadsItsEditsTheWayTheFlowDoes:
    """!! `--edits` WAS A BARE `json.loads` AND ASKED NOTHING, while
    `flows/proof_setter.run` reads the same shape through `desk.notations.read`,
    which type-checks every value and refuses an empty file by name. Two
    readers of one format, one of which validated nothing.

    ! WHAT `notations.read` DOES NOT REFUSE IS `null`, by ruling -- Roy,
    2026-08-25, *"None is explicit enough"* -- so this command deletes on a
    `null` exactly as the flow does. That the two now AGREE is the point; that
    a serialisation failure upstream and an approved `drop` are the same bytes
    is a question about the sentinel, not about this command."""

    def _run(self, tmp_path, monkeypatch, capsys, edits_text: str):
        return TestTheCommandRefusesAStaleFile()._run(
            tmp_path, monkeypatch, capsys, SAMPLE, edits_text=edits_text
        )

    def test_an_edits_file_THAT_IS_NOT_AN_OBJECT_prints_a_reason(
        self, tmp_path, monkeypatch, capsys
    ):
        """Measured 2026-08-25: `edits.items()` over a JSON list left the
        command as an `AttributeError` traceback."""
        code, out = self._run(tmp_path, monkeypatch, capsys, "[]")
        assert code == 2
        assert "not a notations file" in out
        assert not (tmp_path / "out").exists()

    def test_an_EMPTY_edits_file_is_refused_by_name(
        self, tmp_path, monkeypatch, capsys
    ):
        """Measured 2026-08-25: `{}` printed `0 page(s) set, 0 edit(s) refused`
        at exit 0 -- the empty-reads-as-success shape `notations.read`'s own
        docstring forbids."""
        code, out = self._run(tmp_path, monkeypatch, capsys, "{}")
        assert code == 2
        assert "no notations" in out

    def test_a_NON_TEXT_replacement_is_refused_BEFORE_any_page_is_read(
        self, tmp_path, monkeypatch, capsys
    ):
        """! The flow refuses this at exit 2 with the offending address named;
        this command used to reach `galley.reset`, which reports it per-edit
        after the file has been read and hashed."""
        code, out = self._run(tmp_path, monkeypatch, capsys, '{"m.py@b0": 7}')
        assert code == 2
        assert "must be text or null, not int" in out

    def test_an_EMPTY_STRING_is_not_a_delete(self, tmp_path, monkeypatch, capsys):
        code, out = self._run(tmp_path, monkeypatch, capsys, '{"m.py@b0": ""}')
        assert code == 2
        assert "an empty string is not a delete" in out

    def test_A_VALID_EDITS_FILE_STILL_SETS(self, tmp_path, monkeypatch, capsys):
        """! The other half: a reader that refused everything would pass the
        four cases above and be worth nothing."""
        import json

        code, out = self._run(
            tmp_path, monkeypatch, capsys, json.dumps({"m.py@b0": "# REPLACED"})
        )
        assert code == 0
        assert "1 page(s) set, 0 edit(s) refused" in out
