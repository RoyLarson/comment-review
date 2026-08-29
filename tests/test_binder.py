"""reading -> binder: what an agent is handed, and what it is not.

The first of the two chains. Nothing here goes near the galley -- Roy,
2026-08-25: *"The binder is not going through the galley."*
"""

import json

import pytest
from conftest import PKG, READ_FROM, SAMPLE, build, by_cue

from comment_review.binder.binder import VERSION, bind, page_row, read, rows_of
from comment_review.flows.census import carried

#: The fields ruled onto a row -- FIVE, after three rulings.
#: `Addressing: #12` cut eleven of nineteen. `#14` put `kind` back, and `#15`
#: took it away again: once ABSENT places stopped being sent, every row holds
#: prose, so its kind is its series' `present` and the cue letter states it
#: after all. `anchor_num` went with it -- nothing read it from a row, and the
#: write path reloads the page.
ROW_FIELDS = {
    "cue",
    "anchor",
    "original_start",
    "original_end",
    "raw_text",
}


@pytest.fixture
def binder():
    return bind([build(SAMPLE)], read_from=READ_FROM)


def test_the_binder_names_its_own_version(binder):
    """A reader can say WHICH shape it refused, not only that it refused one."""
    assert binder["version"] == VERSION


def test_a_page_carries_its_path_and_its_identity(binder):
    """The file is named ONCE per page, and the sha is what lets a later step
    ask whether the file moved under it."""
    (page,) = binder["pages"]
    assert page["path"] == "m.py"
    assert page["sha"]
    assert set(page) == {"path", "sha", "rows"}


def test_every_row_carries_exactly_the_ruled_fields(binder):
    """Not a superset. The row was `vars(paragraph)` until 2026-08-24, which
    made the dataclass's internals the wire format -- so a field added for one
    module's convenience reached four reviewers."""
    for row in binder["pages"][0]["rows"]:
        assert set(row) == ROW_FIELDS


def test_the_path_is_not_repeated_on_every_row(binder):
    """It is the page's. Repeating it is the same string as many times as the
    file has paragraphs."""
    for row in binder["pages"][0]["rows"]:
        assert "path" not in row


def test_no_fence_is_carried(binder):
    """A fence divides two places and is not one. Roy: *"The leading is not
    something that will be passed to the agents ... It is for white space."*

    ! ASKED OF THE CUE, because the row no longer carries a kind -- and `d` is
    the one series a cue can never name, asked for or not.
    """
    for row in binder["pages"][0]["rows"]:
        assert row["cue"][:1] != "d"


def test_every_row_names_a_place(binder):
    """A row with no cue could not be cited, and would reach a reviewer as a
    question about nowhere."""
    for row in binder["pages"][0]["rows"]:
        assert row["cue"]


def test_the_prose_leaves_as_ONE_STRING(binder):
    """Roy: *"LLMs and the token parsers read this as a complete and coherent
    statement. They do not read this as the same thing: ['LLMs and the token',
    'parsers read this as a', ...]"*. The four reviewers ARE token parsers."""
    for row in binder["pages"][0]["rows"]:
        assert isinstance(row["raw_text"], str)


def test_a_row_holds_every_line_its_paragraph_held(binder):
    """Stamping the page onto each row is the only transformation here, so
        nothing may be lost in it."""
    page = build(SAMPLE)
    rows = {r["cue"]: r for r in binder["pages"][0]["rows"]}
    for c, paragraph in by_cue(page).items():
        if c in rows:
            assert rows[c]["raw_text"] == "\n".join(paragraph.raw_lines)


def test_the_binder_carries_ONLY_the_places_holding_prose(binder):
    """Roy, 2026-08-25: *"The absent kinds are not supposed to be sent to the
    agents unless specifically asked for."*

    !! MEASURED over this repo before the cut: 5,201 of 5,685 rows -- 91% --
    held no prose, and 2 of those were `undocumented`. The rest were one empty
    place per line of code.
    """
    page = build(SAMPLE)
    holding = {
        c for c, b in by_cue(page).items() if any(x.strip() for x in b.raw_lines)
    }
    assert {r["cue"] for r in binder["pages"][0]["rows"]} == holding


def test_an_absent_place_is_carried_WHEN_ASKED_FOR():
    """It is dropped by default, not made unreachable."""
    page = build(SAMPLE)
    asked = {
        r["cue"]
        for r in bind([page], read_from=READ_FROM, absent=True)["pages"][0]["rows"]
    }
    assert asked == set(by_cue(page))
    assert len(asked) > len(bind([page], read_from=READ_FROM)["pages"][0]["rows"])


def test_a_file_with_no_prose_at_all_carries_NO_ROWS():
    """Nothing to rule on is an empty page, not an error -- and not a page of
    empty places either."""
    binder = bind([build("x = 1\ny = 2\n")], read_from=READ_FROM)
    assert binder["pages"][0]["rows"] == []
    assert binder["pages"][0]["path"]


def test_an_empty_place_is_still_ADDRESSED_on_the_page(binder):
    """What makes dropping it safe: the walk emits every place, so a reviewer
    that wants to `add` asks the addresser for the one it means."""
    page = build(SAMPLE)
    empty = [b for b in page.paragraphs if b.address and not b.raw_lines]
    assert empty
    assert all(b.address for b in empty)


def test_carried_drops_fences_and_keeps_everything_else():
    """`carried` is the one statement of what a census hands over."""
    page = build(SAMPLE)
    kept = carried(page)
    assert all(b.address for b in kept)
    assert len(kept) == len([b for b in page.paragraphs if b.address])


class TestRowsOfPutsBackWhatThePageEnvelopeTookOut:
    def test_the_path_comes_back_on_every_row(self, binder):
        assert all(r["path"] == "m.py" for r in rows_of(binder))

    def test_the_address_is_composed_not_stored(self, binder):
        """`address_for` joins the halves and flattens the path -- the
        compositor was measured disagreeing with itself for re-deriving it."""
        page = build(SAMPLE)
        got = {r["address"] for r in rows_of(binder)}
        holding = {
            b.address
            for b in page.paragraphs
            if b.address and any(x.strip() for x in b.raw_lines)
        }
        assert got == holding

    def test_a_row_with_no_cue_composes_no_address(self):
        """`address_for` answers "" when either half is missing, which is what
        an unaddressed row means."""
        binder = {
            "version": VERSION,
            "pages": [{"path": "m.py", "sha": "", "rows": [{"cue": ""}]}],
        }
        assert rows_of(binder)[0]["address"] == ""

    def test_rows_from_several_pages_keep_their_own_paths(self):
        binder = bind(
            [build("# one\nx = 1\n", "a.py"), build("# two\ny = 2\n", "b/c.py")],
            read_from=READ_FROM,
        )
        paths = {r["path"] for r in rows_of(binder)}
        assert paths == {"a.py", "b/c.py"}


class TestAReaderRefusesRatherThanCoping:
    """A guess that is wrong reads as an EMPTY binder, and downstream that is
    indistinguishable from a run with nothing to do."""

    def test_it_reads_what_bind_wrote(self, binder):
        got, why = read(json.dumps(binder))
        assert why == ""
        assert got == binder

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("not json at all", "not JSON"),
            ("[]", "not a binder"),
            ("[1, 2, 3]", "not a binder"),
            ('"a string"', "not a binder"),
            ("{}", "carries no `pages`"),
            ('{"version": "1"}', "carries no `pages`"),
        ],
    )
    def test_it_names_what_it_could_not_read(self, text, expected):
        got, why = read(text)
        assert got == {}
        assert expected in why

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ('{"pages": "oops"}', "`pages` is a JSON str"),
            ('{"pages": {"a": 1}}', "`pages` is a JSON dict"),
            ('{"pages": [1, 2]}', "page 0 is a JSON int"),
            ('{"pages": [{"rows": "oops"}]}', "page 0: `rows` is a JSON str"),
            ('{"pages": [{"rows": [7]}]}', "page 0, row 0 is a JSON int"),
        ],
    )
    def test_the_SHAPE_of_pages_is_read_and_not_only_its_presence(self, text, expected):
        """MEASURED 2026-08-25: `{"pages": "oops"}` read CLEAN, because the key
        was tested for presence alone. `commands/proof.py` then handed it to
        `proof_setter.run`, whose `str(page.get("path", ""))` raised
        `AttributeError: 'str' object has no attribute 'get'` -- a traceback
        past that command's own promise to print `CANNOT READ THE BINDER:
        {why}`, and past this class's own claim that a reader refuses rather
        than coping. ! The `rows` cases are the same defect one level down:
        `rows_of` calls `.get` on every row."""
        got, why = read(text)
        assert got == {}
        assert expected in why

    def test_a_bare_list_is_refused_by_name(self):
        """The shape the census emitted before the envelope. Three commands each
        guessed at it a different way and a fourth did not guess at all."""
        page = build(SAMPLE)
        old = json.dumps([page_row(b) for b in carried(page)])
        got, why = read(old)
        assert got == {}
        assert why


def test_the_binder_reports_the_page_s_sha_rather_than_taking_one():
    page = build(SAMPLE)
    page.sha = "notarealsha"
    assert bind([page], read_from=READ_FROM)["pages"][0]["sha"] == "notarealsha"


def test_only_machine_imports_hashlib():
    """! `machine/` OWNS THE QUERY. Roy, 2026-08-25: the querying of io/git
    software *"should not have left the machine/ modules."*"""
    offenders = [
        p.relative_to(PKG).as_posix()
        for p in PKG.rglob("*.py")
        if "hashlib" in p.read_text(encoding="utf-8") and p.parent.name != "machine"
    ]
    assert offenders == []
