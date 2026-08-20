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

import unittest  # noqa: I001  -- path shim below must import before addresser

from _paths import SCRIPTS  # noqa: F401
import addresser

# Roy's `python_edge_cases.md`, as the walk sees it: the lines of code, and
# which of them declare something that can carry documentation.
EDGE_CODE = [
    "N = 0",
    "def wrapper(fn):",
    "    def counter(*args, **kwargs):",
    "        global N",
    "        N+=1",
    "        return fn(*args, **kwargs)",
    "    return counter",
]
EDGE_DOCUMENTABLE = {1, 2}  # wrapper and counter, by index into EDGE_CODE


class TestAFoliatorHoldsItsOwnSteps(unittest.TestCase):
    """It is a thing with a counter, not an expression evaluated where needed."""

    def test_it_emits_from_its_own_counter(self):
        f = addresser.Foliator("b")
        self.assertEqual(f.emit("<module>"), "b0")
        self.assertEqual(f.emit("N = 0"), "b1")

    def test_a_skipped_trigger_still_takes_a_number(self):
        # ! This is what makes `c`'s first line of code `c1` and not `c0`.
        f = addresser.Foliator("c")
        f.skip()
        self.assertEqual(f.emit("N = 0"), "c1")

    def test_it_records_the_anchor_it_emitted_against(self):
        f = addresser.Foliator("a")
        f.emit("<module>")
        f.emit("def wrapper(fn):")
        self.assertEqual(f.places, {"a0": "<module>", "a1": "def wrapper(fn):"})

    def test_two_foliators_do_not_share_a_counter(self):
        a, b = addresser.Foliator("a"), addresser.Foliator("b")
        b.emit("<module>")
        b.emit("N = 0")
        self.assertEqual(a.emit("<module>"), "a0")


class TestTheWalkOverRoysEdgeCase(unittest.TestCase):
    """The measurement this was built from -- `tests/fixtures/python_edge_cases.md`."""

    def setUp(self):
        self.places = addresser.foliate(EDGE_CODE, EDGE_DOCUMENTABLE)

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
        self.assertEqual(self.places["a0"], addresser.MODULE)
        self.assertEqual(self.places["b0"], addresser.MODULE)
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


class TestTheWalkOnDegenerateFiles(unittest.TestCase):
    """A file with no code, and one with no documentable declaration."""

    def test_a_file_with_no_code_still_has_a_module(self):
        places = addresser.foliate([], set())
        # ! `b0` is the file's own front matter and `b1` the gap that is the
        # whole file. Both exist before any line of code does.
        self.assertEqual(places["a0"], addresser.MODULE)
        self.assertEqual(places["b0"], addresser.MODULE)
        self.assertNotIn("c1", places)

    def test_a_file_with_no_declaration_has_only_a0(self):
        places = addresser.foliate(["N = 0"], set())
        self.assertEqual([f for f in places if f.startswith("a")], ["a0"])

    def test_the_module_never_takes_a_c(self):
        places = addresser.foliate(["N = 0"], set())
        self.assertNotIn("c0", places)
