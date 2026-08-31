"""reading -> binder: what an agent is handed, and what it is not.

The first of the two chains. Nothing here goes near the galley -- Roy,
2026-08-25: *"The binder is not going through the galley."*
"""

import json

import pytest
from conftest import PKG, READ_FROM, SAMPLE, build, by_cue, cue

from comment_review.binder.binder import VERSION, Binder, bind
from comment_review.binder.page import _place
from comment_review.flows.census import carried
from comment_review.machine.json_object import object_of

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


@pytest.fixture
def wire(binder):
    """The binder as it goes to disk.

    !! THE WIRE AND THE CONTAINER ARE ASKED SEPARATELY, since 2026-08-31.
    A test that the row carries exactly five fields is a claim about the
    SERIALIZED form -- it is what an agent receives -- and a test that a row
    holds its paragraph's lines is a claim about the container. They were
    one assertion while `bind` returned a dict, and `Process: #67` split
    them. ! Reading both off `serialize()` would stop the container's own
    fields from being checked at all.
    """
    return binder.serialize()


def read(text: str):
    """The load and the deserialize, as a command performs them.

    ! IT IS A TEST HELPER AND NOT AN API. `binder.read` was one function
    and is now two steps in the FLOW -- `Process: #67` -- so a test that
    wants the pair spells the pair. What it must not do is hide the split:
    each half is asked for separately below.
    """
    loaded, why = object_of(text, "binder")
    if why:
        return None, why
    got, problems = Binder.deserialize("m.py", loaded)
    return got, "; ".join(problems)


def test_the_binder_names_its_own_version(binder):
    """A reader can say WHICH shape it refused, not only that it refused one."""
    assert binder.version == VERSION


def test_a_page_carries_its_path_and_its_identity(binder, wire):
    """The file is named ONCE per page, and the sha is what lets a later step
    ask whether the file moved under it."""
    (page,) = binder.pages
    assert page.path == "m.py"
    assert page.sha
    # ! THE FIELD SET IS A WIRE CLAIM -- what a page is ON DISK.
    assert set(wire["pages"][0]) == {"path", "sha", "rows"}


def test_every_row_carries_exactly_the_ruled_fields(wire):
    """Not a superset. The row was `vars(paragraph)` until 2026-08-24, which
    made the dataclass's internals the wire format -- so a field added for one
    module's convenience reached four reviewers."""
    for row in wire["pages"][0]["rows"]:
        assert set(row) == ROW_FIELDS


def test_the_path_is_not_repeated_on_every_row(wire):
    """It is the page's. Repeating it is the same string as many times as the
    file has paragraphs."""
    for row in wire["pages"][0]["rows"]:
        assert "path" not in row


def test_no_fence_is_carried(binder):
    """A fence divides two places and is not one. Roy: *"The leading is not
    something that will be passed to the agents ... It is for white space."*

    ! ASKED OF THE CUE, because the row no longer carries a kind -- and `d` is
    the one series a cue can never name, asked for or not.
    """
    for row in binder.paragraphs:
        assert cue(row)[:1] != "d"


def test_every_row_names_a_place(binder):
    """A row with no cue could not be cited, and would reach a reviewer as a
    question about nowhere."""
    for row in binder.paragraphs:
        assert cue(row)


def test_the_prose_leaves_as_ONE_STRING(binder):
    """Roy: *"LLMs and the token parsers read this as a complete and coherent
    statement. They do not read this as the same thing: ['LLMs and the token',
    'parsers read this as a', ...]"*. The four reviewers ARE token parsers."""
    for row in binder.paragraphs:
        assert isinstance(row.raw_text, str)


def test_a_row_holds_every_line_its_paragraph_held(binder):
    """Stamping the page onto each row is the only transformation here, so
    nothing may be lost in it."""
    page = build(SAMPLE)
    rows = {cue(b): b for b in binder.paragraphs}
    for c, paragraph in by_cue(page).items():
        if c in rows:
            assert rows[c].raw_text == "\n".join(paragraph.raw_lines)


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
    assert {cue(b) for b in binder.paragraphs} == holding


def test_an_absent_place_is_carried_WHEN_ASKED_FOR():
    """It is dropped by default, not made unreachable."""
    page = build(SAMPLE)
    asked = {cue(b) for b in bind([page], read_from=READ_FROM, absent=True).paragraphs}
    assert asked == set(by_cue(page))
    assert len(asked) > len(bind([page], read_from=READ_FROM).paragraphs)


def test_a_file_with_no_prose_at_all_carries_NO_ROWS():
    """Nothing to rule on is an empty page, not an error -- and not a page of
    empty places either."""
    binder = bind([build("x = 1\ny = 2\n")], read_from=READ_FROM)
    assert binder.pages[0].paragraphs == []
    assert binder.pages[0].path


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


class TestAPlaceKnowsThePageThatHoldsIt:
    """The page stores its path ONCE and each paragraph carries it.

    ! IT WAS `rows_of` THAT REJOINED THEM, then an invented `BinderRow` for
    three hours on 2026-08-31, and is now the `Paragraph` -- which had both
    fields all along. `decision-log.md Process: #68`. The question is unchanged:
    a consumer wants the path and the address per place, and the wire stores the
    path per page.
    """

    def test_the_path_comes_back_on_every_row(self, binder):
        assert all(b.path == "m.py" for b in binder.paragraphs)

    def test_the_address_is_composed_not_stored(self, binder, wire):
        """`address_for` joins the halves and flattens the path -- the
        compositor was measured disagreeing with itself for re-deriving it."""
        page = build(SAMPLE)
        got = {b.address for b in binder.paragraphs}
        holding = {
            b.address
            for b in page.paragraphs
            if b.address and any(x.strip() for x in b.raw_lines)
        }
        assert got == holding
        # ! COMPOSED, NOT STORED: it is on no row of the wire.
        assert all("address" not in row for row in wire["pages"][0]["rows"])

    def test_a_row_with_no_cue_is_REFUSED_not_given_an_empty_address(self):
        """!! THIS REVERSED ON 2026-08-31, AND THE OLD BEHAVIOUR WAS THE DEFECT.

        It read `test_a_row_with_no_cue_composes_no_address` and asserted
        `rows_of(...)[0]["address"] == ""` -- pinning as correct a row that
        names no place. Such a row reaches a reviewer as a question about
        nowhere, and `commands/addresser.py` printed it as `UNPLACED` rather
        than refusing the file.

        ! `Process: #67` puts the refusal at the boundary: the cue is what
        makes a row addressable, so a row without one is not a row.
        """
        got, why = read(
            json.dumps(
                {
                    "version": VERSION,
                    "read_from": READ_FROM,
                    "pages": [{"path": "m.py", "sha": "", "rows": [{"cue": ""}]}],
                }
            )
        )
        assert got is None
        assert "needs the `cue` of the place it holds" in why

    def test_rows_from_several_pages_keep_their_own_paths(self):
        binder = bind(
            [build("# one\nx = 1\n", "a.py"), build("# two\ny = 2\n", "b/c.py")],
            read_from=READ_FROM,
        )
        assert {b.path for b in binder.paragraphs} == {"a.py", "b/c.py"}


class TestAReaderRefusesRatherThanCoping:
    """A guess that is wrong reads as an EMPTY binder, and downstream that is
    indistinguishable from a run with nothing to do."""

    def test_the_ROUND_TRIP_IS_AN_IDENTITY_ON_WHAT_THE_WIRE_CARRIES(self, wire):
        """serialize -> dumps -> loads -> deserialize -> serialize is the same.

        !! IT IS NOT AN IDENTITY ON THE CONTAINERS, AND THAT IS WHAT REDACTED
        MEANS. For one commit this asserted `got == binder`, comparing the
        objects on the argument that two dicts can agree while both are wrong.
        **It fails, correctly**: a `Paragraph` carries `start`, `end`, `kind`,
        `lines`, `declares`, `symbol`, `annotations`, `notes` and
        `original_column`, and the wire carries five fields. `original_column`
        is the one that shows it -- 17 on the page, 0 on the way back.

        ! SO THE HONEST CLAIM IS THE ONE THE FORMAT MAKES: what survives is
        exactly what was written. A test asserting object equality would have
        forced the wire to grow fields nothing reads, which is the pressure
        `Addressing: #12` cut nineteen fields down to five to relieve.
        `decision-log.md Process: #68`.
        """
        got, why = read(json.dumps(wire))
        assert why == ""
        assert got is not None
        assert got.serialize() == wire

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
        assert got is None
        assert expected in why

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ('{"pages": "oops"}', "`pages`: a JSON str"),
            ('{"pages": {"a": 1}}', "`pages`: a JSON dict"),
            ('{"pages": [1, 2]}', "page 0: a JSON int"),
            ('{"pages": [{"path": "m.py", "rows": "oops"}]}', "`rows` is a JSON str"),
            ('{"pages": [{"path": "m.py", "rows": [7]}]}', "row 0: a JSON int"),
        ],
    )
    def test_the_SHAPE_of_pages_is_read_and_not_only_its_presence(self, text, expected):
        """MEASURED 2026-08-25: `{"pages": "oops"}` read CLEAN, because the key
        was tested for presence alone. `commands/proof.py` then handed it to
        `proof_setter.run`, whose `str(page.get("path", ""))` raised
        `AttributeError: 'str' object has no attribute 'get'` -- a traceback
        past that command's own promise to print `CANNOT READ THE BINDER:
        {why}`, and past this class's own claim that a reader refuses rather
        than coping. ! The `rows` cases are the same defect one level down.

        ! THE TWO `rows` CASES GAINED A `path` ON 2026-08-31. Without one the
        page is now refused for the missing path BEFORE its rows are read --
        a truthful refusal, and not the one these cases are about.
        """
        got, why = read(text)
        assert got is None
        assert expected in why

    @pytest.mark.parametrize(
        ("page", "expected"),
        [
            ({"sha": "a", "rows": []}, "a page needs the `path`"),
            ({"path": "  ", "rows": []}, "a page needs the `path`"),
            (
                {"path": "m.py", "rows": [{"anchor": "x", "raw_text": "y"}]},
                "a row needs the `cue`",
            ),
            (
                {"path": "m.py", "rows": [{"cue": "b1", "raw_text": "y"}]},
                "b1 needs a `anchor` string",
            ),
            (
                {
                    "path": "m.py",
                    "rows": [
                        {
                            "cue": "b1",
                            "anchor": "x",
                            "raw_text": "y",
                            "original_start": "seven",
                            "original_end": 7,
                        }
                    ],
                },
                "b1 needs an `original_start` line number or null",
            ),
        ],
    )
    def test_a_PARTIAL_binder_is_refused_by_name(self, page, expected):
        """!! THE BOUNDARY NOW ENSURES THE BINDER LOADED FULLY, NOT PARTIALLY.
        Roy, 2026-08-31, asking for the container: it *"would also allow the
        boundary to ensure it is loaded correctly not partially."*

        MEASURED before `Process: #67`: `binder.read` checked exactly two
        things -- that the JSON decoded, and that `pages` was a list of dicts
        of dicts. A page with no `path` and a row with no `cue` both read
        CLEAN, and every consumer re-derived them with `.get()` defaults.
        """
        got, why = read(
            json.dumps({"version": VERSION, "read_from": READ_FROM, "pages": [page]})
        )
        assert got is None
        assert expected in why

    def test_a_place_standing_on_NO_LINES_is_admitted(self):
        """!! NULL LINE NUMBERS ARE A REAL PLACE, NOT A PARTIAL ONE. An EMPTY
        place stands on nothing -- `Paragraph.__post_init__` spells that `None`
        -- and a `Page` written with `absent=True` carries exactly it. Refusing
        would refuse a shape `bind` itself produces.

        ! SO THE PAIR IS OPTIONAL AND THE `cue` IS NOT, which is the split
        `Process: #68` measured: the cue is what makes a place ADDRESSABLE, and
        the line numbers are read by one diagnostic message.
        """
        got, why = read(
            json.dumps(
                {
                    "version": VERSION,
                    "read_from": READ_FROM,
                    "pages": [
                        {
                            "path": "m.py",
                            "sha": "abc",
                            "rows": [
                                {
                                    "cue": "b1",
                                    "anchor": "x",
                                    "raw_text": "",
                                    "original_start": None,
                                    "original_end": None,
                                }
                            ],
                        }
                    ],
                }
            )
        )
        assert why == ""
        assert got is not None
        (place,) = got.paragraphs
        assert place.original_start is None
        assert place.address == "m.py@b1"

    def test_a_binder_with_no_read_from_is_refused(self):
        """The version "1" artifact. It is refused for `read_from` only AFTER
        the pages read, so a malformed-`pages` file is not blamed on a header
        it also happens to lack."""
        got, why = read('{"pages": []}')
        assert got is None
        assert "carries no `read_from`" in why

    def test_a_bare_list_is_refused_by_name(self):
        """The shape the census emitted before the envelope. Three commands each
        guessed at it a different way and a fourth did not guess at all."""
        page = build(SAMPLE)
        old = json.dumps([_place(b) for b in carried(page)])
        got, why = read(old)
        assert got is None
        assert why


def test_the_binder_reports_the_page_s_sha_rather_than_taking_one():
    page = build(SAMPLE)
    page.sha = "notarealsha"
    assert bind([page], read_from=READ_FROM).pages[0].sha == "notarealsha"


def test_only_machine_imports_hashlib():
    """! `machine/` OWNS THE QUERY. Roy, 2026-08-25: the querying of io/git
    software *"should not have left the machine/ modules."*"""
    offenders = [
        p.relative_to(PKG).as_posix()
        for p in PKG.rglob("*.py")
        if "hashlib" in p.read_text(encoding="utf-8") and p.parent.name != "machine"
    ]
    assert offenders == []
