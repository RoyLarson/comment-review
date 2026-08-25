"""Roy's `python_edge_cases.md`, run as a test rather than read as a document.

!! IT IS THE FIXTURE THAT FOUND THE ADDRESSER BUG. Twelve `add` marks over every
series at every nesting level -- module, a closure, the function inside it -- and
eleven of the twelve land correctly. The twelfth is `b0`, which does not exist on
a file that has no front matter, because the `b` addresser never takes a step at
the `<module>` trigger. See `TODO/b-addresser-uninitialised.md`.

! The document is the SOURCE, not a copy of one: the original and the addresses
its marks name are read out of the fenced blocks below, so the two cannot drift.
A prose edit to the document changes what this test asserts, which is the point.
"""

import ast  # noqa: I001  -- path shim below must import before census
import re
import unittest
from pathlib import Path

# ! `_paths` FIRST: importing it is what puts `src/` on the path.
from _paths import FIXTURES, PKG  # noqa: F401  -- puts `src/` on the path
from comment_review.reading import lexer
from comment_review.binder import page

FIXTURE = FIXTURES / "python_edge_cases.md"

# ```python ... ``` -- the ORIGINAL is the first such block in the document.
BLOCK = re.compile(r"```python\n(.*?)```", re.S)
# `verdict address b1 add "..."` -- only the address is read; the prose is the
# author's and this test does not rule on wording.
MARK = re.compile(r"^verdict\s+address\s+([abcf]\d+)\b", re.M)


def _original() -> str:
    """The `## Original` source, verbatim from the document."""
    blocks = BLOCK.findall(FIXTURE.read_text(encoding="utf-8"))
    assert blocks, "the fixture carries no ```python block"
    return blocks[0].lstrip("\n")


def _marked() -> list[str]:
    """Every cue the document's marks name, in document order."""
    return MARK.findall(FIXTURE.read_text(encoding="utf-8"))


class TestTheFixtureIsReadable(unittest.TestCase):
    """The document parses, so a failure below is about the census and not this."""

    def test_the_original_is_python(self):
        ast.parse(_original())

    def test_every_series_is_exercised(self):
        series = {f[0] for f in _marked()}
        # ! FOUR since 2026-08-20: front matter left the `b` series for its
        # own, so a case that covers every series has to reach `f` too.
        self.assertEqual(
            series, {"a", "b", "c", "f"}, "the case must cover every series"
        )

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
        paragraphs = page.page_for(path, text, lexer.language_for(path))
        # ! The census addresses itself now, so this reads what it stamped
        # rather than re-deriving it -- which is the property under test.
        self.cues = {
            b.address.split("@")[1] for b in paragraphs if "@" in (b.address or "")
        }

    def test_every_a_and_c_the_marks_name_exists(self):
        for cue in sorted(f for f in _marked() if not f.startswith("b")):
            with self.subTest(cue=cue):
                self.assertIn(cue, self.cues)

    def test_b1_is_the_gap_above_the_first_line_of_code(self):
        # ! It is where the author put a comment introducing the first
        # statement, and it must not depend on whether front matter exists.
        self.assertIn("b1", self.cues)

    def test_f0_exists_on_a_file_with_no_front_matter(self):
        """!! FIXED 2026-08-20, and this was the pin that reported it.

        `b0` used to be emitted only where `mark_matter` had already
        stamped prose that existed, so a file with no licence header had nowhere
        to put one -- measured over five file shapes, `b0` and `b1` never
        coexisted. The walk emits both now, and the page gives every place the
        walk emitted a paragraph.

        ! It was an `expectedFailure` rather than a skip, so unittest reported
        an UNEXPECTED SUCCESS the moment the collapse landed. That is what made
        the box impossible to leave ticked-or-not by anyone's judgement.
        """
        self.assertIn("f0", self.cues)

    def test_every_b_the_marks_name_exists(self):
        # ! The other half of the same defect: Roy's `b1` mark was unresolvable
        # on the finished file, because front matter had consumed the place.
        for cue in sorted(f for f in _marked() if f.startswith("b")):
            with self.subTest(cue=cue):
                self.assertIn(cue, self.cues)
