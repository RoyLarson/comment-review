"""Roy's `python_edge_cases.md`, run as a test rather than read as a document.

!! IT IS THE FIXTURE THAT FOUND THE FOLIATOR BUG. Twelve `add` marks over every
series at every nesting level -- module, a closure, the function inside it -- and
eleven of the twelve land correctly. The twelfth is `b0`, which does not exist on
a file that has no front matter, because the `b` foliator never takes a step at
the `<module>` trigger. See `TODO/b-foliator-uninitialised.md`.

! The document is the SOURCE, not a copy of one: the original and the addresses
its marks name are read out of the fenced blocks below, so the two cannot drift.
A prose edit to the document changes what this test asserts, which is the point.
"""

import ast  # noqa: I001  -- path shim below must import before census
import re
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import page

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "python_edge_cases.md"

# ```python ... ``` -- the ORIGINAL is the first such block in the document.
BLOCK = re.compile(r"```python\n(.*?)```", re.S)
# `verdict address b1 add "..."` -- only the address is read; the prose is the
# author's and this test does not rule on wording.
MARK = re.compile(r"^verdict\s+address\s+([abc]\d+)\b", re.M)


def _original() -> str:
    """The `## Original` source, verbatim from the document."""
    blocks = BLOCK.findall(FIXTURE.read_text(encoding="utf-8"))
    assert blocks, "the fixture carries no ```python block"
    return blocks[0].lstrip("\n")


def _marked() -> list[str]:
    """Every folio the document's marks name, in document order."""
    return MARK.findall(FIXTURE.read_text(encoding="utf-8"))


class TestTheFixtureIsReadable(unittest.TestCase):
    """The document parses, so a failure below is about the census and not this."""

    def test_the_original_is_python(self):
        ast.parse(_original())

    def test_every_series_is_exercised(self):
        series = {f[0] for f in _marked()}
        self.assertEqual(series, {"a", "b", "c"}, "the case must cover all three")

    def test_the_marks_are_all_read(self):
        # ! Guards the parser: a regex that matches nothing would make every
        # assertion below vacuously true.
        self.assertGreaterEqual(len(_marked()), 12)


class TestEveryMarkedAddressExists(unittest.TestCase):
    """!! An `add` can only cite a place the census carries.

    Roy, 2026-08-19: *"all of the addresses exist by definition"* and *"b1 isn't
    able to be swallowed by b0"*.
    """

    def setUp(self):
        path = Path("m.py")
        text = _original()
        paragraphs = page.page_for(path, text, page.language_for(path))
        # ! The census addresses itself now, so this reads what it stamped
        # rather than re-deriving it -- which is the property under test.
        self.folios = {
            b.address.split("@")[1] for b in paragraphs if "@" in (b.address or "")
        }

    def test_every_a_and_c_the_marks_name_exists(self):
        for folio in sorted(f for f in _marked() if not f.startswith("b")):
            with self.subTest(folio=folio):
                self.assertIn(folio, self.folios)

    def test_b1_is_the_gap_above_the_first_line_of_code(self):
        # ! It is where the author put a comment introducing the first
        # statement, and it must not depend on whether front matter exists.
        self.assertIn("b1", self.folios)

    @unittest.expectedFailure
    def test_b0_exists_on_a_file_with_no_front_matter(self):
        """!! KNOWN DEFECT -- `TODO/b-foliator-uninitialised.md`.

        `b0` is emitted only when `mark_front_matter` has already stamped prose
        that exists, so a file with no licence header has nowhere to put one.
        Measured over five file shapes: `b0` and `b1` never coexist.

        ! `expectedFailure` rather than a skip, so unittest reports an
        UNEXPECTED SUCCESS the moment the foliator is fixed -- which is what
        makes the box on that TODO impossible to leave unticked.
        """
        self.assertIn("b0", self.folios)
