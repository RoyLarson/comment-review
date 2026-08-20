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

# Roy's `python_edge_cases.md`, as the walk sees it: each line of code with the
# line it sits on, and which of them declare something documentable. ! The line
# POSITIONS the trigger; it never numbers it.
EDGE_CODE = [
    (2, "N = 0"),
    (3, "def wrapper(fn):"),
    (4, "    def counter(*args, **kwargs):"),
    (5, "        global N"),
    (6, "        N+=1"),
    (7, "        return fn(*args, **kwargs)"),
    (8, "    return counter"),
]
EDGE_DOCUMENTABLE = {1, 2}  # wrapper and counter, by index into EDGE_CODE


class TestAFoliatorHoldsItsOwnSteps(unittest.TestCase):
    """It is a thing with a counter, not an expression evaluated where needed."""

    def test_it_emits_from_its_own_counter(self):
        f = foliator.Foliator("b")
        self.assertEqual(f.emit("<module>"), "b0")
        self.assertEqual(f.emit("N = 0"), "b1")

    def test_a_skipped_trigger_still_takes_a_number(self):
        # ! This is what makes `c`'s first line of code `c1` and not `c0`.
        f = foliator.Foliator("c")
        f.skip()
        self.assertEqual(f.emit("N = 0"), "c1")

    def test_it_records_the_anchor_it_emitted_against(self):
        f = foliator.Foliator("a")
        f.emit("<module>")
        f.emit("def wrapper(fn):")
        self.assertEqual(f.places, {"a0": "<module>", "a1": "def wrapper(fn):"})

    def test_two_foliators_do_not_share_a_counter(self):
        a, b = foliator.Foliator("a"), foliator.Foliator("b")
        b.emit("<module>")
        b.emit("N = 0")
        self.assertEqual(a.emit("<module>"), "a0")


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

    def test_b_emits_at_the_module_and_above_every_line_of_code(self):
        # ! Nine places for seven lines: `b0` at the module, one above each
        # line, and one for the gap after the last.
        self.assertEqual(
            self._series("b"), ["b0", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"]
        )

    def test_b0_AND_b1_BOTH_EXIST(self):
        """!! The defect this walk was written for.

        Measured over five file shapes before it: `b0` and `b1` never coexisted
        -- the gap above the first line of code was `b1` on a file with no
        licence header and `b0` on a file with one, so adding a module docstring
        renamed it mid-run. Roy: *"b1 isn't able to be swallowed by b0."*
        """
        self.assertIn("b0", self.places)
        self.assertIn("b1", self.places)

    def test_c_skips_the_module_and_emits_for_every_line_of_code(self):
        self.assertEqual(self._series("c"), ["c1", "c2", "c3", "c4", "c5", "c6", "c7"])

    def test_every_place_carries_the_line_of_code_it_is_attached_to(self):
        self.assertEqual(self.places["a0"], foliator.MODULE)
        self.assertEqual(self.places["b0"], foliator.MODULE)
        self.assertEqual(self.places["a1"], "def wrapper(fn):")
        # ! A `b` is anchored to the line BELOW the gap -- the statement its
        # prose introduces.
        self.assertEqual(self.places["b1"], "N = 0")
        self.assertEqual(self.places["b2"], "def wrapper(fn):")
        # ! The gap at the end of the file has no line below it and takes the
        # one above, because a gap is bounded by code and that is the bound.
        self.assertEqual(self.places["b8"], "    return counter")
        self.assertEqual(self.places["c1"], "N = 0")

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
        self.assertEqual(self.foliation.above(4), "b3")

    def test_above_the_first_line_of_code_is_b1_not_b0(self):
        # !! `b0` is the file's own front matter and is not a gap between two
        # lines of code. Conflating them is what made the two exclusive.
        self.assertEqual(self.foliation.above(1), "b1")

    def test_past_the_last_line_is_the_closing_gap(self):
        self.assertEqual(self.foliation.above(99), "b8")

    def test_a_line_of_code_answers_with_its_own_c(self):
        self.assertEqual(self.foliation.beside(3), "c2")

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
        places = foliator.foliate([], set()).places
        # ! `b0` is the file's own front matter and `b1` the gap that is the
        # whole file. Both exist before any line of code does.
        self.assertEqual(places["a0"], foliator.MODULE)
        self.assertEqual(places["b0"], foliator.MODULE)
        self.assertNotIn("c1", places)

    def test_a_file_with_no_declaration_has_only_a0(self):
        places = foliator.foliate([(1, "N = 0")], set()).places
        self.assertEqual([f for f in places if f.startswith("a")], ["a0"])

    def test_the_module_never_takes_a_c(self):
        places = foliator.foliate([(1, "N = 0")], set()).places
        self.assertNotIn("c0", places)
