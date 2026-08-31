"""`carry`: making the binder hold a place `bind()` dropped.

The three lookups Roy named on 2026-08-26 -- *"look up by anchor_num, line_num,
and cue"* -- plus what each refuses.

! THE PLACES ARE DISCOVERED FROM THE PAGE, never written as literals: a
hardcoded cue asserts what the walk emitted last time someone looked.
"""

import json

import pytest
from conftest import SAMPLE, build, by_cue

from comment_review.binder.binder import bind
from comment_review.flows.carry import carry


def _tree(tmp_path):
    """A one-file repo, its binder, and the page."""
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    return repo, bind([page], read_from={"root": str(repo), "revise": 0}), page


def empty_cues(page) -> list[str]:
    return [
        c for c, b in by_cue(page).items() if not any(x.strip() for x in b.raw_lines)
    ]


def filled_cues(page) -> list[str]:
    return [c for c, b in by_cue(page).items() if any(x.strip() for x in b.raw_lines)]


def test_the_sample_HAS_places_the_binder_drops(tmp_path):
    """!! THE WHOLE PREMISE, and it would be vacuous if the sample had none.
    `bind()` cuts every place holding no prose -- 5,201 of 5,685 rows, 91%,
    measured -- so a reviewer never sees them and an `add` has nothing to
    cite."""
    _, binder, page = _tree(tmp_path)
    carried = {str(r["cue"]) for r in binder["pages"][0]["rows"]}
    assert empty_cues(page)
    assert not (set(empty_cues(page)) & carried)


class TestTheThreeLookups:
    def test_by_cue(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        want = empty_cues(page)[0]
        updated, added, why = carry(binder, page, "m.py", cue=want)
        assert why == ""
        assert added == want
        assert want in {str(r["cue"]) for r in updated["pages"][0]["rows"]}

    def test_by_line(self, tmp_path):
        """A `b` is the gap a line falls into -- `Cues.above`."""
        repo, binder, page = _tree(tmp_path)
        want = next(c for c in empty_cues(page) if c.startswith("b"))
        line = page.cues.anchor_line(want)
        assert line is not None
        updated, added, why = carry(binder, page, "m.py", line=line, series="b")
        assert why == ""
        assert added == want

    def test_by_anchor_num(self, tmp_path):
        """!! THE ORDINAL SURVIVES A PROSE EDIT WHERE A LINE DOES NOT. Roy,
        2026-08-21: *"a single shift on anchor_num and you know it is all trash
        after rereading."*"""
        repo, binder, page = _tree(tmp_path)
        want = empty_cues(page)[0]
        ordinal = page.cues.anchor_num(want)
        updated, added, why = carry(
            binder, page, "m.py", anchor_num=ordinal, series=want[0]
        )
        assert why == ""
        assert added == want

    def test_every_empty_place_can_be_carried_by_cue(self, tmp_path):
        """The matrix, not a representative -- picking one is how `b0` went
        unexercised in the galley suite for a month."""
        for want in empty_cues(build(SAMPLE)):
            repo, binder, page = _tree(tmp_path / want)
            _, added, why = carry(binder, page, "m.py", cue=want)
            assert why == "", f"{want}: {why}"
            assert added == want


class TestWhatItRefuses:
    def test_a_place_the_page_does_not_have(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        _, added, why = carry(binder, page, "m.py", cue="b99")
        assert added == ""
        assert "no such place" in why

    def test_a_place_that_ALREADY_HOLDS_PROSE(self, tmp_path):
        """!! IT IS NOT AN ABSENCE. The binder already carries it, and a second
        row would put two on one address -- the shape `galley.reset` refuses by
        name, 157 measured in one tree."""
        repo, binder, page = _tree(tmp_path)
        _, added, why = carry(binder, page, "m.py", cue=filled_cues(page)[0])
        assert added == ""
        assert "already carries this place" in why

    def test_a_page_the_binder_does_not_have(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        _, _, why = carry(binder, page, "nowhere.py", cue="b0")
        assert "carries no such page" in why

    def test_a_STALE_BINDER_is_refused_by_the_sha(self, tmp_path):
        """!! THE ROW IS BUILT FROM A PAGE READ NOW. If the file has moved on,
        its walk describes prose nobody reviewed and every cue below the edit
        may have shifted -- so the row would name a place in a file the binder
        does not describe."""
        repo, binder, page = _tree(tmp_path)
        binder["pages"][0]["sha"] = "something else entirely"
        _, added, why = carry(binder, page, "m.py", cue=empty_cues(page)[0])
        assert added == ""
        assert "re-run the census" in why

    def test_a_NULL_sha_is_shown_as_ABSENT_not_the_word_None(self, tmp_path):
        """!! A PRESENT `"sha": null` IS A DIFFERENT CASE FROM AN ABSENT KEY.
        `held.get("sha", "")` only defaults when the key is missing; a present
        `None` comes back as `None` itself, and `str(None)` is the
        four-character word "None" -- the same anti-pattern fixed at
        `desk.containers.parse_sheet`."""
        repo, binder, page = _tree(tmp_path)
        binder["pages"][0]["sha"] = None
        _, added, why = carry(binder, page, "m.py", cue=empty_cues(page)[0])
        assert added == ""
        assert "re-run the census" in why
        assert "None" not in why
        assert "<nothing>" in why

    @pytest.mark.parametrize(
        "lookup,fragment",
        [
            ({}, "give one of"),
            ({"line": 3}, "needs --series"),
            ({"anchor_num": 0}, "needs --series"),
            ({"line": 3, "series": "a"}, "use --anchor-num"),
            ({"anchor_num": 999, "series": "b"}, "no `b` place was emitted"),
        ],
    )
    def test_a_lookup_that_names_nothing(self, tmp_path, lookup, fragment):
        repo, binder, page = _tree(tmp_path)
        _, _, why = carry(binder, page, "m.py", **lookup)
        assert fragment in why


def test_the_row_is_inserted_IN_READING_ORDER(tmp_path):
    """!! NOT APPENDED. A binder's rows are the page top to bottom -- what a
    reviewer reads -- so a row on the end puts the file's first gap after its
    last comment."""
    repo, binder, page = _tree(tmp_path)
    want = next(c for c in empty_cues(page) if c.startswith("b"))
    updated, _, why = carry(binder, page, "m.py", cue=want)
    assert why == ""
    order = list(page.cues.reading)
    cues = [str(r["cue"]) for r in updated["pages"][0]["rows"]]
    assert cues == sorted(cues, key=order.index)


def test_the_carried_row_is_EMPTY_and_shaped_like_every_other(tmp_path):
    """It is a place, not prose: no lines, no span, and the same five fields
    `page_row` gives a filled one."""
    repo, binder, page = _tree(tmp_path)
    updated, added, _ = carry(binder, page, "m.py", cue=empty_cues(page)[0])
    rows = updated["pages"][0]["rows"]
    got = next(r for r in rows if str(r["cue"]) == added)
    assert set(got) == set(rows[0])
    assert got["raw_text"] == ""
    assert got["original_start"] is None and got["original_end"] is None
    assert got["anchor"]


class TestTheCommand:
    def test_it_writes_the_binder_and_exits_0(self, tmp_path, capsys, monkeypatch):
        from comment_review.commands import carry as cmd

        repo, binder, page = _tree(tmp_path)
        want = empty_cues(page)[0]
        (tmp_path / "b.json").write_text(json.dumps(binder), encoding="utf-8")
        monkeypatch.setattr(
            "sys.argv",
            [
                "carry",
                "--binder",
                str(tmp_path / "b.json"),
                "--repo",
                str(repo),
                "--path",
                "m.py",
                "--cue",
                want,
            ],
        )
        assert cmd.main() == 0
        assert want in capsys.readouterr().out
        written = json.loads((tmp_path / "b.json").read_text(encoding="utf-8"))
        assert want in {str(r["cue"]) for r in written["pages"][0]["rows"]}

    def test_a_refusal_writes_NOTHING(self, tmp_path, capsys, monkeypatch):
        from comment_review.commands import carry as cmd

        repo, binder, page = _tree(tmp_path)
        before = json.dumps(binder)
        (tmp_path / "b.json").write_text(before, encoding="utf-8")
        monkeypatch.setattr(
            "sys.argv",
            [
                "carry",
                "--binder",
                str(tmp_path / "b.json"),
                "--repo",
                str(repo),
                "--path",
                "m.py",
                "--cue",
                "b99",
            ],
        )
        assert cmd.main() == 1
        assert "REFUSED" in capsys.readouterr().out
        assert (tmp_path / "b.json").read_text(encoding="utf-8") == before

    def test_carry_is_a_named_command(self):
        from comment_review.__main__ import COMMANDS

        assert "carry" in COMMANDS
