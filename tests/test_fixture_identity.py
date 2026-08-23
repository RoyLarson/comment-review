"""One fixture per language, and the identity run over every one of them.

!! THE CORPORA ARE ALL PYTHON, which is what these fixtures answer. Nine pinned
repositories supply tens of thousands of Python files and a handful of anything
else -- `TODO/corpora-are-all-python.md` has the tally -- so the identity, the
only check that can disagree with a real file, had no material to run on for
most of the seventeen rows. Roy, 2026-08-22: *"round trips on languages we don't
have even short examples are handy."*

! A fixture here is SHORT AND ORDINARY on purpose. It is not an edge-case
collection: it is the shape of a normal file in that language -- front matter, a
declaration carrying documentation, a gap, a trailing comment, and whichever
literal form the row calls out. An edge case belongs in the test that argues
about it; this file argues only that the model does not lose the ordinary case.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / "plugins/comment-review/skills/comment-review/scripts"
    ),
)

import compositor  # noqa: E402
import language  # noqa: E402
import page as page_mod  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"

# !! EVERY FIXTURE PUTS THIS INSIDE A STRING LITERAL, never inside a comment.
# It is the one word whose position is a whole classification claim: a literal
# holding `//`, `#` or `--` is read as prose the moment its delimiter is not
# understood, and every such row this branch fixed failed exactly here first.
IN_A_LITERAL = "not-a-comment"

# !! ONE SENTENCE PER ROW THAT MUST BE READ AS PROSE, and it is deliberately the
# sentence sitting behind that language's LEAST ordinary comment marker -- INI's
# semicolon, Lua's levelled long bracket, Ruby's `=begin`. A row that loses its
# second marker still passes every check above: the paragraph is filed as code,
# the file still sets back to itself byte-for-byte, and the literal test finds
# nothing because nothing leaked. MEASURED 2026-08-22 -- both the `toml`/`ini`
# split and Lua's missing levels were invisible to the other three classes here.
MUST_BE_PROSE = {
    "c": "one small translation unit",
    "cpp": "raw string literal takes no escapes",
    "csharp": "verbatim string takes no escapes",
    "go": "RAW string holds the same marker",
    "ini": "semicolon is INI's original comment marker",
    "java": "Small arithmetic helpers",
    "javascript": "template literal crosses lines",
    "kotlin": "soft keyword",
    "lua": "levelled long comment exists",
    "python": "Add two numbers",
    "ruby": "block comment spanning",
    "rust": "ordinary comment inside the body",
    "shell": "Prints the sum of two integers",
    "sql": "SQL has no docstring practice",
    "swift": "Returns the sum of a and b",
    "toml": "TOML takes",
    "typescript": "type alias carries documentation",
    "yaml": "YAML has no docstring practice",
}


def fixtures_for(lang: language.Language) -> list[Path]:
    """Every fixture file whose suffix this language row claims."""
    return sorted(p for p in FIXTURES.iterdir() if p.suffix in lang.extensions)


def prose_of(path: Path) -> list[str]:
    """The text of every paragraph on this page that holds any."""
    lang = language.language_for(path)
    page = page_mod.page_for(path, path.read_text(encoding="utf-8"), lang)
    return [b.text for b in page.paragraphs if b.text.strip()]


class TestEveryLanguageHasAFixture(unittest.TestCase):
    """A row with no fixture has no round-trip coverage at all.

    ! This is the half that keeps the other half honest. Adding a language is a
    data row, so it costs nothing to add one -- and a row nothing exercises
    reports the same green as a row proved over a real file.
    """

    def test_every_language_row_has_at_least_one_fixture(self):
        missing = [lang.name for lang in language.LANGUAGES if not fixtures_for(lang)]
        self.assertEqual(missing, [])


class TestEveryFixtureSetsBackToItself(unittest.TestCase):
    """`set_page(page_for(text)) == text`, for each language's ordinary file.

    !! IT PROVES LOSSLESSNESS AND NOT CLASSIFICATION, and the difference is
    measurable rather than theoretical. MEASURED 2026-08-22: a Lua file opening
    `--[===[` -- one level past what the row declares -- sets back IDENTICAL,
    because prose read as code still reassembles as the same bytes. The identity
    cannot see a misfiled paragraph; it can only see a lost one. ! So this class
    is necessary and is not sufficient, and the two below are what cover the
    other half.
    """

    def test_every_fixture_sets_back_to_itself(self):
        broken = {}
        for lang in language.LANGUAGES:
            for path in fixtures_for(lang):
                why = compositor.identity(path)
                if why is not None:
                    broken[f"{lang.name}:{path.name}"] = why
        self.assertEqual(broken, {})


class TestEveryFixtureIsReadAsProseSomewhere(unittest.TestCase):
    """A row whose comment markers are wrong yields a page with no prose at all.

    ! The cheapest possible check on a new language row, and the one the `ini`
    split would have wanted: a file that is visibly half commentary censusing to
    zero paragraphs of prose is a row that does not know the language.
    """

    def test_every_fixture_has_prose(self):
        empty = [
            path.name
            for lang in language.LANGUAGES
            for path in fixtures_for(lang)
            if not prose_of(path)
        ]
        self.assertEqual(empty, [])


class TestAStringLiteralIsNeverProse(unittest.TestCase):
    """The classification half, over every language at once.

    !! THIS IS THE PROPERTY EVERY SPANNING-QUOTE DEFECT BROKE FIRST. A literal
    holding the language's own comment marker is read as a comment the moment
    its delimiter is not understood, and the paragraph is then handed to four
    reviewers as prose they may rewrite -- into the middle of a string. MEASURED
    2026-08-22 on Go's backtick: `` `http://example.com/a` `` censused as a
    trailing comment, and the `return` line dropped out of `code_lines` and
    renumbered every address below it.
    """

    def test_no_fixture_reads_a_literal_as_prose(self):
        leaked = {
            f"{lang.name}:{path.name}": [t for t in prose_of(path) if IN_A_LITERAL in t]
            for lang in language.LANGUAGES
            for path in fixtures_for(lang)
            if any(IN_A_LITERAL in t for t in prose_of(path))
        }
        self.assertEqual(leaked, {})

    def test_the_marker_is_actually_present_in_every_fixture(self):
        """Otherwise the test above passes by having nothing to find."""
        without = [
            path.name
            for lang in language.LANGUAGES
            for path in fixtures_for(lang)
            if IN_A_LITERAL not in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(without, [])


class TestTheAwkwardMarkerIsReadAsProse(unittest.TestCase):
    """Each row's least ordinary comment form still produces a paragraph.

    !! THIS IS THE ONLY CLASS HERE THAT CATCHES A MISFILED PARAGRAPH. The
    identity cannot (prose read as code reassembles identically), the prose count
    cannot (one surviving marker is enough), and the literal test cannot (nothing
    leaks). What is left is naming the sentence and asking where it went.
    """

    def test_every_language_names_a_sentence_that_must_be_prose(self):
        """A row added without an entry here gets no classification check."""
        self.assertEqual(
            sorted(lang.name for lang in language.LANGUAGES),
            sorted(MUST_BE_PROSE),
        )

    def test_the_awkward_marker_is_read_as_prose(self):
        lost = {}
        for lang in language.LANGUAGES:
            needle = MUST_BE_PROSE[lang.name]
            for path in fixtures_for(lang):
                if needle not in path.read_text(encoding="utf-8"):
                    lost[f"{lang.name}:{path.name}"] = "not in the fixture at all"
                elif not any(needle in text for text in prose_of(path)):
                    lost[f"{lang.name}:{path.name}"] = "in the file, but not as prose"
        self.assertEqual(lost, {})
