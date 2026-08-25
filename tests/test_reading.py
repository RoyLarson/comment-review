"""Reading a file into a page: what must hold of every page, for every file.

Derived from `binder/page.py` and `reading/lexer.py` by reading them and by
running them over real sources.
"""

from pathlib import Path

import pytest
from conftest import SAMPLE, build, by_cue, occupied

from comment_review.binder.page import page_for
from comment_review.machine.repo import sha_of
from comment_review.reading.lexer import language_for
from comment_review.reading.series import ADDRESSED, Kind, Series

#: Sources chosen to reach a different shape each, across the tiers and
#: languages the reader claims to handle.
SOURCES = {
    "bare statement": ("m.py", "x = 1\n"),
    "no final newline": ("m.py", "x = 1"),
    "module docstring": ("m.py", '"""Doc."""\nx = 1\n'),
    "comment above code": ("m.py", "# note\nx = 1\n"),
    "trailing comment": ("m.py", "x = 1  # beside\n"),
    "blanks between": ("m.py", "x = 1\n\n\ny = 2\n"),
    "leading blanks": ("m.py", "\n\nx = 1\n"),
    "trailing blanks": ("m.py", "x = 1\n\n\n"),
    "shebang": ("m.py", "#!/usr/bin/env python\nx = 1\n"),
    "function": ("m.py", 'def f():\n    """D."""\n    return 1\n'),
    "nested": ("m.py", "def f():\n    def g():\n        return 1\n    return g\n"),
    "class": ("m.py", 'class A:\n    """D."""\n\n    x = 1\n'),
    "only comments": ("m.py", "# one\n# two\n"),
    "only blanks": ("m.py", "\n\n\n"),
    "C block": ("m.c", "/* head */\nint a;\n"),
    "rust": ("m.rs", "/// Doc.\npub fn f() {}\n"),
    "go": ("m.go", "// Doc.\nfunc f() {}\n"),
    "toml": ("m.toml", "# note\nkey = 1\n"),
    "shell": ("m.sh", "#!/bin/sh\necho hi\n"),
    "js": ("m.js", "// note\nlet a = 1;\n"),
    "unicode": ("m.py", "# caf\u00e9\nx = 1\n"),
    "tabs": ("m.py", "def f():\n\treturn 1\n"),
}
CASES = pytest.mark.parametrize(
    ("name", "text"),
    [pytest.param(n, t, id=k) for k, (n, t) in SOURCES.items()],
)


@CASES
def test_every_line_of_the_file_is_covered_exactly_once(name, text):
    """The paragraphs PARTITION the file's lines -- no gap, no overlap.

    This is the property the whole scheme rests on. `addresser` states it: a
    cue is an ordinal over a complete enumeration, so *"a code line missed
    anywhere above a place SHIFTS ITS NAME"* -- silently, because a partial
    enumeration does not fail, it renumbers.
    """
    page = build(text, name)
    spans = occupied(page)
    lines = len(text.splitlines())
    covered = []
    for start, end in spans:
        covered.extend(range(start, end + 1))
    assert covered == sorted(covered), "spans are out of order"
    assert len(covered) == len(set(covered)), "two paragraphs claim one line"
    assert set(covered) == set(range(1, lines + 1))


@CASES
def test_no_two_paragraphs_share_an_address(name, text):
    """An address identifies ONE paragraph, or a replacement is ambiguous.

    `galley.reset` refuses an edit whose place holds more than one paragraph,
    so a page that breaks this cannot be edited at all.
    """
    addresses = [b.address for b in build(text, name).paragraphs if b.address]
    assert len(addresses) == len(set(addresses))


@CASES
def test_every_place_is_reachable_from_the_reading_order(name, text):
    """`cues.reading` is what the compositor walks, so a place missing from it
    is a place that cannot be set back."""
    page = build(text, name)
    assert set(by_cue(page)) == set(page.cues.reading)


@CASES
def test_a_paragraph_carries_an_ADDRESS_or_a_SYMBOL_and_never_both(name, text):
    """A fence names no place and is found by symbol; every other paragraph is
    the reverse. Nothing is both, and nothing is neither."""
    for b in build(text, name).paragraphs:
        assert bool(b.address) != bool(b.symbol), (b.address, b.symbol, b.kind)


@CASES
def test_only_a_fence_lacks_an_address(name, text):
    """`d` is the one series that takes no address -- `reading/series.py` says
    so by giving it no `absent`."""
    for b in build(text, name).paragraphs:
        if not b.address:
            assert b.kind == Kind.LEADING


@CASES
def test_every_cue_names_a_series_that_can_be_cited(name, text):
    """A cue's letter is one of the ADDRESSED series -- never `d`."""
    for c in by_cue(build(text, name)):
        assert c[:1] in ADDRESSED
        assert c[1:].isdigit(), f"a cue is a letter and an ordinal: {c!r}"


@CASES
def test_each_series_numbers_itself_from_zero_without_gaps(name, text):
    """Every series starts at 0 and counts up. `addresser`: a series that does
    not emit for a trigger takes no number for it either."""
    seen: dict[str, list[int]] = {}
    for c in by_cue(build(text, name)):
        seen.setdefault(c[0], []).append(int(c[1:]))
    for letter, numbers in seen.items():
        assert sorted(numbers) == list(range(len(numbers))), letter


@CASES
def test_a_paragraph_that_stands_on_lines_holds_BOTH_ends(name, text):
    """The two are set as a pair -- one without the other is a half-built
    paragraph, and arithmetic on it fails on `None`."""
    for b in build(text, name).paragraphs:
        assert (b.original_start is None) == (b.original_end is None)
        if b.original_start is not None:
            assert b.original_start <= b.original_end


@CASES
def test_an_empty_place_stands_on_no_line(name, text):
    """An absence is a place the walk emitted and nothing filled, so it has a
    position in the order and no position in the file.

    ! A `c` IS THE EXCEPTION AND NOT ONE: an empty `c` is the room beside a
    line of code, so it stands on that line and holds an empty string.
    """
    for c, b in by_cue(build(text, name)).items():
        if Kind.occupies_no_lines(b.kind) and not c.startswith("c"):
            assert b.original_start is None
            assert b.raw_lines == []


#: The three languages whose doc marker IS an ordinary line-comment marker.
#: MEASURED 2026-08-25 across thirteen languages: `go` (`//`), `ruby` (`#`) and
#: `lua` (`--`) place a declaration's documentation at an `a` cue and type it
#: `comment`, which is the `b` series' kind. Rust, Java, C#, Kotlin, Swift, TS
#: and JS all answer `docstring`, and they are the ones with a DISTINCT doc
#: marker -- `///`, `/** */`.
KIND_DISAGREES = {"go", "ruby doc", "lua doc"}


@pytest.mark.parametrize(
    ("name", "text"),
    [
        pytest.param(
            n,
            t,
            id=k,
            marks=pytest.mark.xfail(
                strict=True,
                reason="the doc marker is an ordinary comment marker, so the "
                "lexer types it `comment` while the walk cues it `a`",
            )
            if k in KIND_DISAGREES
            else (),
        )
        for k, (n, t) in {
            **SOURCES,
            "ruby doc": ("m.rb", "# Doc.\ndef f\nend\n"),
            "lua doc": ("m.lua", "--- Doc.\nlocal function f() end\n"),
        }.items()
    ],
)
def test_the_kind_agrees_with_the_series_the_cue_names(name, text):
    """A row states its series TWICE and the two must agree.

    The cue's letter names the series; the kind names which half of that
    series' pair -- `b` is `comment` or `interval`, never `docstring`. A place
    cued `a` holding a `comment` is one row making two different claims about
    itself, and every consumer that pairs them sees a contradiction:
    `record.prose_paragraphs` filters on the KIND while `series_of` reads the
    CUE.

    !! THREE LANGUAGES BREAK THIS TODAY and the xfail says which. It is the
    defect `Kind`'s own docstring describes -- *"the two halves were set in
    different modules and nothing tied them"* -- still live where the doc marker
    cannot be told from a comment marker by the token alone.
    """
    for c, b in by_cue(build(text, name)).items():
        definition = Series.of(c)
        assert definition is not None, c
        assert b.kind in (definition.value.present, definition.value.absent), (
            f"{c} is series {definition.name} but holds kind {b.kind}"
        )


@CASES
def test_leading_is_keyed_by_the_place_it_follows(name, text):
    """`Page.leading` is an EDGE map -- cue -> the symbol of the `d` below it --
    so both halves must resolve on the page."""
    page = build(text, name)
    symbols = {b.symbol for b in page.paragraphs if b.symbol}
    for before, symbol in page.leading.items():
        assert before in by_cue(page), before
        assert symbol in symbols, symbol


def test_a_file_with_every_series_filled_reads_them_all():
    """The sample is only useful if it really carries one of each."""
    filled = {
        c[0]
        for c, b in by_cue(build(SAMPLE)).items()
        if any(x.strip() for x in b.raw_lines)
    }
    assert filled == {"a", "b", "c", "f"}


class TestAPageCarriesTheShaItWasGiven:
    """The page RECEIVES a sha. Roy, 2026-08-25: *"It is information received by
    page and binder, not something requested by page/binder."*"""

    def test_the_page_carries_it(self):
        page = build(SAMPLE)
        assert page.sha == sha_of(SAMPLE)

    def test_page_for_computes_no_sha_of_its_own(self):
        # A page built with a sha that does not describe its text keeps the sha
        # it was HANDED. If page.py hashed anything, this would disagree.
        path = Path("m.py")
        page = page_for(path, SAMPLE, language_for(path), rel="m.py", sha="deadbeef")
        assert page.sha == "deadbeef"

    def test_the_sha_is_required(self):
        path = Path("m.py")
        with pytest.raises(TypeError):
            page_for(path, SAMPLE, language_for(path), rel="m.py")
