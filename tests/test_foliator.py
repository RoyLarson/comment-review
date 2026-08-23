"""Three foliators, each holding its own counter AND the places it emitted.

!! WHAT A FOLIATOR IS. Roy, 2026-08-19: *"the foliator gets an anchor and emits
an address and should add the address and the anchor to an internal list or
dict"*, and *"a b and c all get foliators."* None was one before this: `a` read
a census field, `b` was `sum(1 for n in code if n < at) + 1` and `c` was
`code.index(start) + 1` -- three expressions over LINE NUMBERS, in the module
whose purpose is to stop line positions naming places.

! The rules differ per series and are MEASURED, not chosen. `a` and `b` emit at
the module; `c` steps past it without emitting, which is why its first line of
code is `c1`. `a` does not step at a trigger it cannot emit for -- Roy: *"a
foliator doesn't fire ever on things that can't get a doc string"* -- so its
numbers count documentable declarations and nothing else.
"""

import unittest  # noqa: I001  -- path shim below must import before foliation

from _paths import SCRIPTS  # noqa: F401
import foliator

# Roy's `python_edge_cases.md`, as the walk sees it: the ordered mapping from
# each line to the code on it, and which of them declare something
# documentable. ! The line POSITIONS the trigger; it never numbers it.
EDGE_CODE = {
    2: "N = 0",
    3: "def wrapper(fn):",
    4: "    def counter(*args, **kwargs):",
    5: "        global N",
    6: "        N+=1",
    7: "        return fn(*args, **kwargs)",
    8: "    return counter",
}
# wrapper and counter, by index into EDGE_CODE -> `(the line their doc would go
# on, the code index it is SET BEFORE)`. ! NOT `declaring line + 1`: the line is
# the first statement of the body, which `lexer.declarations` states because only
# a parser knows it.
#
# !! THE SECOND HALF ARRIVED 2026-08-21 and is what the WALK reads. Roy: *"how do
# I get you to stop thinking in line numbers?"* Handing the walk a line made it
# compare `insert <= n` to decide where a docstring falls -- arithmetic in the
# one module that must not do any. `page.documentable` resolves the language's
# rule into an ordinal AND A SIDE, and the walk only places it. Here both docs
# sit BELOW their declaring line -- Python -- so each is set before the GAP of
# the next code there is: `wrapper`'s before index 2 (`def counter`) and
# `counter`'s before index 3. An above-doc language files against the `c`
# instead, which puts the doc between the gap and the code.
EDGE_DOCUMENTABLE = {1: (4, 2, "b"), 2: (5, 3, "b")}


class TestAFoliatorHoldsItsOwnSteps(unittest.TestCase):
    """It is a thing with a counter, not an expression evaluated where needed."""

    def test_it_emits_from_its_own_counter(self):
        f = foliator.Foliator("b")
        self.assertEqual(f.emit("<module>", 0), "b0")
        self.assertEqual(f.emit("N = 0", 1), "b1")

    def test_a_SKIPPED_trigger_takes_no_number(self):
        """!! A SERIES THAT DOES NOT EMIT FOR A TRIGGER DOES NOT ADVANCE EITHER.

        Roy, 2026-08-20: *"the foliations own their own rules on what is skipped
        ... they each decide to record and increment independently."* Skipping
        used to increment, which burned `b0` and made the first line of code
        `c1`. ! There is no `skip()` to call: a foliator is only ever handed the
        triggers it emits for, so this asserts the counter by its absence.
        """
        f = foliator.Foliator("c")
        self.assertFalse(hasattr(f, "skip"))
        self.assertEqual(f.emit("N = 0", 1), "c0")

    def test_it_records_the_anchor_it_emitted_against(self):
        f = foliator.Foliator("a")
        f.emit("<module>", 0)
        f.emit("def wrapper(fn):", 1)
        self.assertEqual(f.places, {"a0": "<module>", "a1": "def wrapper(fn):"})

    def test_two_foliators_do_not_share_a_counter(self):
        a, b = foliator.Foliator("a"), foliator.Foliator("b")
        b.emit("<module>", 0)
        b.emit("N = 0", 1)
        self.assertEqual(a.emit("<module>", 0), "a0")


class TestEveryPlaceRecordsTheTriggerItFiredAt(unittest.TestCase):
    """`anchor_num` is READ from the walk, never reconstructed after it.

    !! THE WALK KNEW THIS AND THREW IT AWAY. Roy, 2026-08-22, on a consumer that
    trusted the reconstruction instead: *"you hardened the mistake that you were
    just fixing -- that the walk didn't emit ALL anchors, which caused the
    problem."* Three arithmetics stood in for it: `n + 1` for a gap,
    `len(code) + 1` for the file's foot, `code.index(anchor) + 1` for the rest.

    ! Driven by `foliate`, because the claim is about the WALK. A hand-built
    `Foliator` handed two numbers can only show that `emit` assigns them.
    """

    def setUp(self):
        self.foliation = foliator.foliate(EDGE_CODE, EDGE_DOCUMENTABLE)
        self.walk = foliator.triggers(list(EDGE_CODE))

    def test_the_walk_OPENS_on_the_module_and_CLOSES_on_eof(self):
        """!! THE TWO ENDS ARE THE WALK'S OWN, not something a file can supply.

        Every place's position indexes this list, so the list having exactly one
        head and one foot is what the position means. ! Roy, 2026-08-22: *"the
        only other test that has to be put in is that the walk starts and ends
        with those, and not by accident or injection."*

        ! BY ACCIDENT: on a file with NO code at all, the two sentinels are the
        whole walk, and they must still be one each and in that order.

        ! BY INJECTION: a sentinel is a STRING and a line is an INT, which is
        the only thing separating them. A file whose code literally reads
        `<eof>` supplies the text, never the trigger.
        """
        for name, code in (
            ("the edge case", EDGE_CODE),
            ("no code at all", {}),
            ("one line", {1: "x = 1"}),
            ("code that SPELLS a sentinel", {1: foliator.EOF, 2: foliator.MODULE}),
        ):
            with self.subTest(shape=name):
                walk = foliator.triggers(list(code))
                self.assertEqual(walk[0], foliator.MODULE)
                self.assertEqual(walk[-1], foliator.EOF)
                self.assertEqual(walk.count(foliator.MODULE), 1)
                self.assertEqual(walk.count(foliator.EOF), 1)
                # ! Everything between them is a LINE, which is what makes the
                # two sentinels unforgeable from a file's contents.
                self.assertTrue(all(isinstance(n, int) for n in walk[1:-1]))

    def test_indexing_the_walk_with_what_a_place_REPORTS_gives_its_trigger(self):
        """!! THE INVARIANT: `triggers()[anchor_num(folio)]` is the trigger that
        place was emitted at, for every place on the page.

        ! WHERE THAT TRIGGER IS A LINE OF CODE, IT IS THE PLACE'S OWN ANCHOR --
        which is what makes this a cross-check rather than a restatement. It
        would fail on any emit that named the wrong position, and it cannot be
        satisfied by re-deriving the number from the folio.

        !! THE TWO SENTINELS ARE THE CASES THE ANCHOR CANNOT ANSWER, and they
        are exactly the ones that needed arithmetic before. `MODULE` is `a0` and
        `f0`; `EOF` is the closing gap, whose anchor is `<eof>` --
        a different trigger's line, because it has none below it -- and the file
        foot, which answers `<module>` from the other end of the file.
        """
        places = self.foliation.places
        self.assertTrue(places)
        for folio in sorted(places):
            at = self.foliation.anchor_num(folio)
            with self.subTest(folio=folio):
                trigger = self.walk[at]
                if isinstance(trigger, int):
                    self.assertEqual(
                        EDGE_CODE[trigger], self.foliation.anchor_of(folio)
                    )
                else:
                    self.assertIn(trigger, (foliator.MODULE, foliator.EOF))


class TestTheWalkOverRoysEdgeCase(unittest.TestCase):
    """The measurement this was built from -- `tests/fixtures/python_edge_cases.md`."""

    def setUp(self):
        self.foliation = foliator.foliate(EDGE_CODE, EDGE_DOCUMENTABLE)
        self.places = self.foliation.places

    def _series(self, letter):
        return sorted(
            (f for f in self.places if f.startswith(letter)),
            key=lambda f: int(f[1:]),
        )

    def test_a_counts_documentable_declarations_and_nothing_else(self):
        # ! `N = 0` is a line of code and is not documentable, so `a` does not
        # step past it: wrapper is `a1`, not `a2`.
        self.assertEqual(self._series("a"), ["a0", "a1", "a2"])

    def test_b_SKIPS_the_module_and_emits_above_every_line_of_code(self):
        # ! Eight places for seven lines: one above each line of code, and
        # one for the gap after the last. ! The module is not `b`'s trigger,
        # and skipping it takes no number, so the first gap is `b0`.
        self.assertEqual(
            self._series("b"), ["b0", "b1", "b2", "b3", "b4", "b5", "b6", "b7"]
        )

    def test_f0_AND_b0_BOTH_EXIST(self):
        """!! The defect this walk was written for.

        Measured over five file shapes before it: `b0` and `b1` never coexisted
        -- the gap above the first line of code was `b1` on a file with no
        licence header and `b0` on a file with one, so adding a module docstring
        renamed it mid-run. Roy: *"b1 isn't able to be swallowed by b0."*

        ! The two are `f0` and `b0` since 2026-08-20, when every series was
        ruled to start at 0. What the test holds is that they COEXIST, which
        is what the numbering was never allowed to collapse.
        """
        self.assertIn("f0", self.places)
        self.assertIn("b0", self.places)

    def test_c_skips_the_module_and_emits_for_every_line_of_code(self):
        self.assertEqual(self._series("c"), ["c0", "c1", "c2", "c3", "c4", "c5", "c6"])

    def test_every_place_carries_the_line_of_code_it_is_attached_to(self):
        self.assertEqual(self.places["a0"], foliator.MODULE)
        self.assertEqual(self.places["f0"], foliator.MODULE)
        self.assertEqual(self.places["a1"], "def wrapper(fn):")
        # ! A `b` is anchored to the line BELOW the gap -- the statement its
        # prose introduces.
        self.assertEqual(self.places["b0"], "N = 0")
        self.assertEqual(self.places["b1"], "def wrapper(fn):")
        # !! THE GAP AT THE END IS ANCHORED TO THE TRIGGER IT WAS EMITTED AT,
        # since 2026-08-22. It took the line ABOVE it until then -- the previous
        # trigger's -- which is the special case Roy's 2026-08-21 ruling made
        # EOF a trigger to remove.
        self.assertEqual(self.places["b7"], foliator.EOF)
        self.assertEqual(self.places["c0"], "N = 0")

    def test_no_folio_is_emitted_twice(self):
        self.assertEqual(len(self.places), len(set(self.places)))


class TestReadingTheFoliationBack(unittest.TestCase):
    """!! WHICH ADDRESS DOES THIS LINE BELONG TO RIGHT NOW.

    Roy, 2026-08-19, on why the foliation owns both directions: it *"helps the
    agents understand what they are looking at right now in the code -- they
    need to search it anyways."*

    ! Every answer is a LOOKUP into what the walk emitted, never a recount. A
    recount is what `gap_step` did, and it is how the number came to depend on
    whether a licence header happened to exist.
    """

    def setUp(self):
        self.foliation = foliator.foliate(EDGE_CODE, EDGE_DOCUMENTABLE)

    def test_a_gap_answers_with_the_b_the_walk_emitted_there(self):
        # Line 4 is `def counter`, so a paragraph inserting there is in the gap
        # ABOVE it -- the third gap, `b3`.
        self.assertEqual(self.foliation.above(4), "b2")

    def test_above_the_first_line_of_code_is_b0(self):
        # !! `f0` is the file's own front matter and is not a gap between two
        # lines of code. Conflating them is what made the two exclusive.
        self.assertEqual(self.foliation.above(1), "b0")

    def test_past_the_last_line_is_the_closing_gap(self):
        self.assertEqual(self.foliation.above(99), "b7")

    def test_a_line_of_code_answers_with_its_own_c(self):
        self.assertEqual(self.foliation.beside(3), "c1")

    def test_a_line_holding_no_code_has_no_c(self):
        self.assertEqual(self.foliation.beside(1), "")

    def test_a_declaration_answers_by_its_ORDINAL_not_its_line(self):
        self.assertEqual(self.foliation.documents(0), "a0")
        self.assertEqual(self.foliation.documents(1), "a1")
        self.assertEqual(self.foliation.documents(2), "a2")

    def test_a_declaration_the_file_does_not_have_answers_nothing(self):
        self.assertEqual(self.foliation.documents(9), "")


class TestTheWalkOnDegenerateFiles(unittest.TestCase):
    """A file with no code, and one with no documentable declaration."""

    def test_a_file_with_no_code_still_has_a_module(self):
        places = foliator.foliate({}, {}).places
        # ! `f0` is the file's own front matter and `b1` the gap that is the
        # whole file. Both exist before any line of code does.
        self.assertEqual(places["a0"], foliator.MODULE)
        self.assertEqual(places["f0"], foliator.MODULE)
        self.assertNotIn("c1", places)

    def test_a_file_with_no_declaration_has_only_a0(self):
        places = foliator.foliate({1: "N = 0"}, {}).places
        self.assertEqual([f for f in places if f.startswith("a")], ["a0"])

    def test_the_module_never_takes_a_c(self):
        # !! ASKED OF THE ANCHOR, NOT OF THE NUMBER. `c0` exists -- it is the
        # line of code, since skipping the module takes no number -- so the
        # property is that NO `c` is anchored to the module, which is what
        # `assertNotIn("c0", ...)` meant while `c` started at 1.
        places = foliator.foliate({1: "N = 0"}, {}).places
        self.assertEqual(places["c0"], "N = 0")
        self.assertNotIn(
            foliator.MODULE,
            [a for f, a in places.items() if f.startswith("c")],
        )


class TestAFifthSeriesWouldNotNeedFindingFourTimes(unittest.TestCase):
    """`SERIES` is the only list of them, and everything counts rather than names.

    !! THE FOURTH COST TWO BUGS AND A DEAD CLI FLAG. `foliate` merged three
    foliators' places and not the fourth, so `f0` had no anchor and no
    paragraph; `_series_of` inferred the series from two fields a fourth fits
    neither of, so front matter answered as a `b`; and `--series` refused `f`
    outright -- the one route a reviewer has to ask for the file's own place.

    ! Roy, 2026-08-20: *"we may find another specific type that doesn't match
    these four's purposes, so keep the code generic in how it picks it up even
    if we don't know the shape. That is how we got into the bind of trying to
    pick up the matter -- we kept trying to push it in instead of considering it
    was its own thing."*
    """

    def test_every_series_constant_is_in_the_list(self):
        for name in ("DECLARED", "GAP", "ON", "COVERS"):
            with self.subTest(series=name):
                self.assertIn(getattr(foliator, name), foliator.SERIES)

    def test_no_two_series_share_a_letter(self):
        self.assertEqual(len(set(foliator.SERIES)), len(foliator.SERIES))

    def test_the_CLI_offers_every_series_the_walk_can_emit(self):
        # ! The gap this closes: `--series` listed three of four, so the only
        # sanctioned way to ask for the file's own place was an argparse error.
        source = (SCRIPTS / "foliator.py").read_text(encoding="utf-8")
        self.assertIn("choices=SERIES,", source)

    def test_every_place_the_walk_emits_carries_an_anchor(self):
        # !! THE PROPERTY THAT BROKE. A place absent from `places` has no anchor
        # and gets no paragraph, so it is uncitable and invisible -- which is
        # what `f0` was for its first hour, while sitting in `bounds` all along.
        got = foliator.foliate({1: "N = 0", 2: "def f():"}, {1: (2, 1, "c")})
        self.assertTrue(got.places)
        for folio, anchor in got.places.items():
            with self.subTest(folio=folio):
                self.assertTrue(anchor, f"{folio} carries no anchor")
        # ! THE SECOND HALF OF THIS IS NOW STRUCTURAL. It read `for folio in
        # got.bounds: assertIn(folio, got.places)` -- a place could sit in one
        # registry and not the other, which is exactly what `f0` did. `bounds`
        # was deleted 2026-08-21 and is computed from the walk's own code lines,
        # so there is no second registry left to disagree with `places`.
        self.assertFalse(hasattr(got, "bounds"), "a second registry is back")

    def test_every_place_answers_with_the_line_its_anchor_sits_on(self):
        # !! IT WAS `declared_at` AND FILLED FOR `a` ALONE. The fact was never
        # about declaring -- it is the anchor's line, and every series has one.
        # Left per-series, a `b` and a `c` read 0, and an order built on it put
        # every one of them at the top.
        got = foliator.foliate({2: "N = 0", 3: "def f():"}, {1: (4, 2, "b")})
        self.assertEqual(got.anchor_line("c0"), 2)
        self.assertEqual(got.anchor_line("c1"), 3)
        # ! A `b` is anchored to the line BELOW its gap -- the statement its
        # prose introduces. ! `b` and `c` are ALIGNED: each pair shares an
        # anchor, because neither emits for the module and neither takes a
        # number there.
        self.assertEqual(got.anchor_line("b0"), 2)
        self.assertEqual(got.anchor_line("b1"), 3)
        # !! THE CLOSING GAP ANSWERS None, because it is anchored to `EOF` and a
        # sentinel sits on no line. It took the line ABOVE it until 2026-08-22,
        # borrowing the previous trigger's.
        self.assertIsNone(got.anchor_line("b2"))
        # ! AND IT IS STILL BOUNDED, which is what places it. `gap_bounds` reads
        # the walk either side of the trigger it fired at, never the anchor.
        self.assertEqual(got.gap_bounds("b2"), (3, 0))
        self.assertEqual(got.anchor_line("a1"), 3)

    def test_a_SENTINEL_answers_None_because_it_sits_on_no_line(self):
        # !! IT ANSWERED 0 FOR BOTH ENDS UNTIL 2026-08-22, and the two were not
        # the same fact. Line 0 is genuinely above line 1, so the head sorted
        # first and rendered at the top and both were right; the FOOT inherited
        # those behaviours and both were wrong. Roy: *"the end of file getting a
        # 0 is non-functional filling in for a missing value."*
        got = foliator.foliate({2: "N = 0"}, {})
        for folio in ("a0", "f0", "b1", "f1"):
            with self.subTest(folio=folio):
                self.assertIsNone(got.anchor_line(folio))
        # ! The place that DOES sit on a line still answers with it.
        self.assertEqual(got.anchor_line("c0"), 2)

    def test_the_series_of_a_place_is_READ_and_not_inferred(self):
        # ! Inferred from `declares`/`original_column`, a series that is neither
        # comes back `b`. Read off the address, a new one answers as itself.
        made_up = {"address": "m.py@z7", "declares": -1, "original_column": 0}
        self.assertEqual(foliator.series_of(made_up), "z")


class TestOneCheckAnswersWhoIsUnaddressed(unittest.TestCase):
    """`foliator.unaddressed` is the ONE implementation, and two gates ask it.

    !! IT FAILED SILENTLY, WHICH IS WHY IT IS ASKED AT BOTH ENDS. `verdicts.py`
    builds accountability from the ADDRESSES, so a paragraph carrying none is
    not accountable -- and the run then reads as complete because there was
    nothing to be incomplete about. Measured 2026-08-20 on a 5-paragraph census
    with its addresses stripped and a report ruling on nothing: `0 findings ...
    over 0 prose paragraphs`, then "Every finding is admissible. Stage 5 may
    rule." at exit 0.

    ! ONE implementation because two would drift. Roy, 2026-08-20: *"one source
    of truth, else something will parse that something else will fail."*
    """

    def test_an_addressed_census_reports_nothing(self):
        self.assertEqual(
            foliator.unaddressed(
                [{"path": "a.py", "start": 1, "end": 1, "address": "a.py@b0"}]
            ),
            [],
        )

    def test_a_paragraph_with_no_address_is_NAMED_not_counted(self):
        # ! It names the file and the lines: a reader has to know WHICH one to
        # look at, and a count alone sends them through the whole census.
        got = foliator.unaddressed([{"path": "a.py", "start": 3, "end": 4}])
        self.assertEqual(len(got), 1)
        self.assertIn("a.py", got[0])
        self.assertIn("3-4", got[0])

    def test_an_EMPTY_address_counts_as_none(self):
        # ! `page_for` writes "" when `attach` places nothing, so the falsy case
        # is the one that actually occurs.
        self.assertEqual(
            len(foliator.unaddressed([{"path": "a.py", "start": 1, "address": ""}])), 1
        )

    def test_an_EMPTY_census_is_not_a_failure(self):
        # ! Nothing to address is not the same as failing to address something.
        self.assertEqual(foliator.unaddressed([]), [])
