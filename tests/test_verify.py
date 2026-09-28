"""`flows/verify.py`: what a returned copy is wrong about against the pages.

! INPUTS ARE REAL -- binders from `bind`-shaped helpers, copies from the real
`seed`, marks built through the instruction rows. A literal appears only where
malformed is the input.

The cases here came from `tests/test_collate.py`, which drove them through the
old fold. They drive the four functions directly now: the fold is not their
subject, and the bus runs all four before it opens one.
"""

import pytest
from helpers import (
    _keeping_only,
    _without_sheet,
    a_binder_over,
    a_clean,
    a_move,
    a_real_binder_over,
    a_small_real_tree,
    binder_of,
    copies_over,
    pages_of,
    returned,
    seed,
)

from comment_review.desk.collator import Cache, known_addresses, verify_report
from comment_review.desk.proof.mark import Mark
from comment_review.desk.stages import Kind, Stage
from comment_review.flows.page_for import page_of
from comment_review.flows.verify import (
    coverage_problems,
    resolution_problems,
    texts_at,
)
from comment_review.reading.addresser import address_for

BASE = "# one\n# two\n# three\n"

#: The comment `a_real_binder_over` sets at a page's `b1` for the quote check.
QUOTED = "# one\n# two\n# three"


def _resolution(wire, binder, root):
    """`resolution_problems` over one wire copy, with a cache of its own."""
    paths = [page.path for page in binder.pages]
    return resolution_problems(returned(wire), paths, root, {})


def _quote_problems(wire, binder, root):
    """The quote check over one wire copy, reading its texts from the pages."""
    copy = returned(wire)
    paths = [page.path for page in binder.pages]
    cache: Cache = {}
    return verify_report(copy, texts_at(copy, paths, root, {}), root, cache)


class TestAnAddressMustResolveAgainstAPage:
    """`collator-defects` T40: the binder is redacted to the places holding
    prose, so a real empty place is one it rightly lacks (`Process: #97`).
    The check asks the real page instead, over a real checkout so an invented
    cue and a real empty place can be told apart."""

    def test_an_invented_cue_is_reported(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        wire = seed(binder, "block-context")
        sheet = next(s for s in wire["sheets"] if s["path"] == "mark.py")
        sheet["marks"].append(a_clean("mark.py@b9999"))
        problems = _resolution(wire, binder, repo)
        found = [p for p in problems if p.address == "mark.py@b9999"]
        assert found, problems
        assert found[0].role == "block-context"

    def test_a_real_empty_place_is_not_reported(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        absent = _an_empty_place_on_mark_py(repo, binder)
        wire = seed(binder, "block-context")
        sheet = next(s for s in wire["sheets"] if s["path"] == "mark.py")
        sheet["marks"].append(a_clean(absent))
        carried = [m.address for s in returned(wire).sheets for m in s.marks]
        assert absent in carried, "the copy must really carry the empty place"
        assert [p for p in _resolution(wire, binder, repo) if p.address == absent] == []

    def test_a_file_this_checkout_does_not_hold_is_reported(self, tmp_path):
        """`decision-log.md Process: #122`: an address whose page cannot be
        read resolves against nothing, and is reported as an invented cue is."""
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        wire = seed(binder, "block-context")
        sheet = next(s for s in wire["sheets"] if s["path"] == "mark.py")
        sheet["marks"].append(a_clean("gone.py@b1"))
        found = [
            p for p in _resolution(wire, binder, repo) if p.address == "gone.py@b1"
        ]
        assert found
        assert found[0].role == "block-context"

    @pytest.mark.parametrize(
        "destination",
        [
            pytest.param("mark.py@b9999", id="an-invented-cue"),
            pytest.param("gone.py@b1", id="a-file-this-checkout-does-not-hold"),
        ],
    )
    def test_a_moves_unresolved_destination_is_reported(self, tmp_path, destination):
        """`decision-log.md Process: #111`: a `move`'s `claim.to` is an
        address, and resolves against its page as the mark's own address does.
        The problem is the mover's, at the move's own address."""
        repo = a_small_real_tree(tmp_path)
        binder, wire, origin = _a_move_on_mark_py(repo, destination)
        found = [p for p in _resolution(wire, binder, repo) if p.address == origin]
        assert found
        assert found[0].role == "block-context"
        assert "`claim.to`" in found[0].message

    def test_a_move_to_a_real_empty_place_is_not_reported(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        absent = _an_empty_place_on_mark_py(repo, binder_of(repo, 0))
        binder, wire, origin = _a_move_on_mark_py(repo, absent)
        moved = [
            m for s in returned(wire).sheets for m in s.marks if m.address == origin
        ]
        assert [m.claim.get("to") for m in moved] == [absent]
        assert [p for p in _resolution(wire, binder, repo) if p.address == origin] == []


class TestAnAddressIsHeldToThePrintedSpelling:
    """An address resolves only as the binder, or the page it names, prints it.

    A role copies an address from the binder, and one it retypes can differ
    from every printed address in the case of its path or in whitespace. A
    file system that ignores case still opens the page, so a case slip read
    as resolving and reached the docket as a second page. Each misspelling is
    refused here, naming the spelling the page prints.
    """

    PLACES = {"m.py@b1": QUOTED, "m.py@b5": "# dest para."}

    def _problems(self, root, *entries):
        """`resolution_problems` over block-context's copy, `entries` appended
        to its sheet beside a `clean` on every seeded slot."""
        binder = a_real_binder_over(root, self.PLACES)
        wire = seed(binder, "block-context")
        for slot in wire["sheets"][0]["marks"]:
            slot.update(a_clean(slot["address"]))
        wire["sheets"][0]["marks"].extend(entries)
        return _resolution(wire, binder, root)

    def test_an_own_address_in_another_case_is_refused(self, tmp_path):
        problems = self._problems(tmp_path, a_clean("M.py@b1"))
        assert [(p.address, p.message) for p in problems] == [
            (
                "M.py@b1",
                "resolves against no page -- it is spelled otherwise than the"
                " page prints it, 'm.py@b1'",
            )
        ]

    @pytest.mark.parametrize("spelled", ["m.py@b5 ", " m.py@b5", "M.py@b5"])
    def test_a_destination_spelled_otherwise_is_refused(self, tmp_path, spelled):
        move = a_move("m.py@b1", spelled, change="# two", reads="# dest para. two")
        problems = self._problems(tmp_path, move)
        assert [(p.address, p.message) for p in problems] == [
            (
                "m.py@b1",
                f"`claim.to` {spelled!r} resolves against no page -- it is spelled"
                " otherwise than the page prints it, 'm.py@b5'",
            )
        ]

    def test_a_page_the_binder_lacks_is_held_to_the_checkouts_spelling(self, tmp_path):
        (tmp_path / "n.py").write_text(
            "v0 = 0\n# seven\nv1 = 1\n", encoding="utf-8", newline="\n"
        )
        move = a_move("m.py@b1", "N.py@b1", change="# two", reads="# seven\n# two")
        problems = self._problems(tmp_path, move)
        assert [p.message for p in problems] == [
            "`claim.to` 'N.py@b1' resolves against no page -- it is spelled"
            " otherwise than the page prints it, 'n.py@b1'"
        ]

    def test_a_page_the_binder_lacks_resolves_as_that_page_prints_it(self, tmp_path):
        (tmp_path / "n.py").write_text(
            "v0 = 0\n# seven\nv1 = 1\n", encoding="utf-8", newline="\n"
        )
        move = a_move("m.py@b1", "n.py@b1", change="# two", reads="# seven\n# two")
        assert self._problems(tmp_path, move) == []

    def test_a_bare_cue_is_refused_on_a_clean(self, tmp_path):
        """A `clean` is the one row the parse lets carry an address that is
        not `path@cue`, so resolution is what names it."""
        problems = self._problems(tmp_path, a_clean("b1"))
        assert [(p.address, p.message) for p in problems] == [
            ("b1", "resolves against no page -- it is not a `path@cue` address")
        ]


class TestAnAddressOutsideTheCheckoutIsNotRead:
    """`collate-flow-defects` T14.

    A mark's address is written by a role, and the page cache joins its path
    to the root. An absolute path discards the root when joined and a `..`
    climbs out of it, so an address naming either is reported as resolving
    against no page, and no file outside the root is opened -- the guard
    `desk.collator.source_problems` keeps for a cited path.
    """

    @pytest.mark.parametrize("form", ["climbs", "absolute"])
    def test_it_is_unresolved_and_nothing_outside_the_root_is_read(
        self, tmp_path, monkeypatch, form
    ):
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": QUOTED})
        outside = tmp_path / "outside.py"
        outside.write_bytes((root / "m.py").read_bytes())
        path = "../outside.py" if form == "climbs" else outside.as_posix()
        address = f"{path}@b1"
        wire = seed(binder, "block-context")
        wire["sheets"][0]["marks"][0].update(a_clean("m.py@b1"))
        correct = {
            **Mark.seed(address, "", ""),
            "instruction": "correct",
            "claim": {"false": "# two", "true": "# 2"},
            "reason": "written for the containment check",
            "sources": [{"cite": "m.py:1", "verbatim": "v0 = 0"}],
            "change": "# one\n# 2\n# three",
        }
        wire["sheets"].append({"path": path, "sha": "", "marks": [correct]})
        read = []

        def recording(page_path, *args, **kwargs):
            read.append(page_path.resolve())
            return page_of(page_path, *args, **kwargs)

        monkeypatch.setattr("comment_review.flows.on_the_page.page_of", recording)
        copy = returned(wire)
        paths = [page.path for page in binder.pages]
        cache: dict = {}
        problems = resolution_problems(copy, paths, root, cache)
        texts_at(copy, paths, root, cache)
        unresolved = [p.message for p in problems if p.address == address]
        assert unresolved, problems
        assert read, "the page inside the root is read, so the record sees reads"
        assert all(p.is_relative_to(root.resolve()) for p in read), read


class TestAQuoteIsCheckedAgainstThePage:
    """`decision-log.md Process: #119`.

    A quoted clause is checked against the text at the mark's own address,
    read from the page whether or not the binder holds that place or its
    file. Where no page can be read the quote is checked against nothing, so
    it is refused.
    """

    def _elsewhere(self, root, false: str, written: bool = True):
        """One copy seeded from a binder holding `a.py` alone, carrying a
        `correct` at `b.py@b1` that quotes `false`. `b.py` is a copy of
        `a.py`, holding `QUOTED` at `b1`, unless `written` is False.
        """
        binder = a_real_binder_over(root, {"a.py@b1": QUOTED})
        if written:
            (root / "b.py").write_bytes((root / "a.py").read_bytes())
        wire = seed(binder, "block-context")
        wire["sheets"][0]["marks"][0].update(a_clean("a.py@b1"))
        correct = {
            **Mark.seed("b.py@b1", "", ""),
            "instruction": "correct",
            "claim": {"false": false, "true": "# 2"},
            "reason": "written for the quote check",
            "sources": [{"cite": "a.py:1", "verbatim": "v0 = 0"}],
            "change": "# one\n# 2\n# three",
        }
        wire["sheets"].append({"path": "b.py", "sha": "", "marks": [correct]})
        return [
            p.message
            for p in _quote_problems(wire, binder, root)
            if p.address == "b.py@b1" and "is not in the paragraph" in p.message
        ]

    def test_a_quote_at_a_place_the_binder_lacks_passes_when_on_the_page(
        self, tmp_path
    ):
        assert self._elsewhere(tmp_path, "# two") == []

    def test_that_quote_is_refused_when_it_is_not_on_the_page(self, tmp_path):
        assert self._elsewhere(tmp_path, "# four") != []

    def test_a_quote_where_no_page_can_be_read_is_refused(self, tmp_path):
        assert self._elsewhere(tmp_path, "# two", written=False) != []


class TestShardCoverage:
    """`containers-and-verification-are-unwired` T6.

    !! `flows.fan_out.fan` REFUSES AN UNCOVERED PAGE AT THE DISPATCH; NOTHING
    READ THE RETURN. A partitioned role that answered for three of four files
    in its shard was invisible.

    !! THE UNIT IS THE ADDRESS, NOT THE PAGE. A dropped page is a dropped
    address set, so the address check answers both; a page check answers only
    the file case, and misses a copy that kept 1 of its 4 seeded slots.
    """

    def test_a_role_that_answered_for_part_of_its_shard_is_named(self):
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        short = [returned(_without_sheet(copies[0], "m.py"))]
        found = coverage_problems(short, binder)
        assert [p.role for p in found] == ["block-context"]
        assert "m.py@b1" in found[0].message

    def test_a_copy_that_kept_one_of_its_four_seeded_slots_is_named(self):
        binder = a_binder_over({f"m.py@b{n}": BASE for n in (1, 2, 3, 4)})
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        kept = returned(_keeping_only(copies[0], ["m.py@b1"]))
        found = coverage_problems([kept], binder)
        assert [p.role for p in found] == ["block-context"]
        for missing in ("m.py@b2", "m.py@b3", "m.py@b4"):
            assert missing in found[0].message

    def test_the_count_does_not_include_an_address_the_binder_never_held(self):
        """!! MEASURED 2026-08-31: a role that dropped one place and invented
        another reported *"answered for 2 of 2 places -- missing m.py@b5"* --
        a sentence contradicting itself. `carried` holds everything returned;
        the number the sentence means is the intersection with the binder's."""
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        short = _keeping_only(copies[0], ["m.py@b1"])
        short["sheets"][0]["marks"].append(
            {**a_clean("m.py@b9"), "address": "m.py@b9", "raw_text": BASE}
        )
        found = coverage_problems([returned(short)], binder)
        assert [p.role for p in found] == ["block-context"]
        assert "answered for 1 of 2 places" in found[0].message
        assert "missing m.py@b5" in found[0].message

    def test_the_coverage_line_OPENS_with_the_missing_addresses(self):
        """Roy, 2026-09-01: *"That way the potential address comes as soon as
        possible."*

        !! THE ORDER WAS UNPINNED, WHICH IS WHY THIS EXISTS. Both assertions
        above use `in`, so reversing the sentence changed no test -- and this is
        the one line in the report whose `address` field is empty, so the places
        it names live only in the message. A reader scanning for somewhere to
        look had to read past a count to reach them.
        """
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        kept = returned(_keeping_only(copies[0], ["m.py@b1"]))
        message = coverage_problems([kept], binder)[0].message
        assert message.startswith("missing m.py@b5"), message
        assert message.index("missing") < message.index("answered for"), message

    def test_coverage_follows_what_the_stage_dealt(self):
        """`decision-log.md Process: #193`, Roy: only the places over the
        length limit are touched, and all the others are automatically clean
        for this role. So a copy holding the dealt place alone is complete,
        and it is measured against the deal rather than against every place
        the binder carries -- which is what this asked before the stage could
        narrow it.
        """
        stage = Stage(
            name="6", kind=Kind.EDITORIAL, cap=2, series=("b",), admits=("patch",)
        )
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": "# short"})
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        dealt = returned(_keeping_only(copies[0], ["m.py@b1"]))
        assert coverage_problems([dealt], binder, stage) == []
        # And it still bites inside the deal: a role that dropped a place the
        # stage did deal is as short as it ever was.
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        short = returned(_keeping_only(copies[0], ["m.py@b1"]))
        found = coverage_problems([short], binder, stage)
        assert [p.role for p in found] == ["block-context"]
        assert "m.py@b5" in found[0].message

    def test_two_shards_of_one_role_cover_the_binder_between_them(self):
        """!! COMPARED PER COPY THIS REPORTS EVERY FAN-OUT SHARD AS INCOMPLETE.
        The union across a role's copies is what keeps a correctly partitioned
        role from being reported short of its own shard."""
        binder = a_binder_over({"one.py@b1": BASE, "two.py@b1": BASE})
        halves = [
            returned({**seed(binder, "block-context"), "sheets": [sheet]})
            for sheet in seed(binder, "block-context")["sheets"]
        ]
        assert len(halves) == 2
        assert coverage_problems(halves, binder) == []


def _an_empty_place_on_mark_py(repo, binder) -> str:
    """A place `mark.py` really has that the binder does not carry."""
    known = known_addresses(binder)
    page = next(p for p in pages_of(repo) if p.path == "mark.py")
    return next(
        address_for(page.path, c)
        for c in page.cues.places
        if address_for(page.path, c) not in known
    )


def _a_move_on_mark_py(repo, destination: str):
    """block-context's copy over `repo`, its first slot on `mark.py` a `move`
    to `destination`.

    The move cites the first line of `repo`'s own `mark.py`, so its source
    resolves and any problem at its address is the address check's.

    Returns:
        `(binder, the wire copy, the move's own address)`.
    """
    binder = binder_of(repo, 0)
    wire = seed(binder, "block-context")
    sheet = next(s for s in wire["sheets"] if s["path"] == "mark.py")
    slot = sheet["marks"][0]
    first = (repo / "mark.py").read_text(encoding="utf-8").splitlines()[0]
    slot.update(
        {
            **a_move(slot["address"], destination),
            "sources": [{"cite": "mark.py:1", "verbatim": first}],
        }
    )
    return binder, wire, slot["address"]
