"""page -> compositor: what goes in comes out, wherever that can be identified.

!! THIS IS THE INSTRUMENT THAT COULD NOT FAIL, ONCE. It scored 699 of 699 on its
first run while 157 addresses were held by two paragraphs each, because it
rebuilt each file from the line positions it had just read out of that file. It
began finding things when it was made to set from the CUES instead. So a case
here is only worth having if a broken compositor would fail it.

! THE FRONT-MATTER/`b` COLLISION IS OUT OF SCOPE -- a file whose front matter is
not on line 1. It is a ruled normalisation, and a test over it would pin the
sacrifice rather than the property.
"""

import pytest
from conftest import REPLACEMENT, SAMPLE, build, by_cue, cue
from helpers import FORMS

from comment_review import exceptions
from comment_review.results import compositor, galley
from comment_review.results.compositor import line_endings, set_page


def test_failed_page_is_reported_before_setting(tmp_path, monkeypatch):
    from comment_review.flows.compositor import round_trip
    from comment_review.reading.diagnostics import ReadFailure

    path = tmp_path / "broken.c"
    path.write_text("/* open", encoding="utf-8")

    def unexpected_set(page):
        raise AssertionError("failed page reached the setter")

    monkeypatch.setattr(compositor, "set_page", unexpected_set)
    result = round_trip(path)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].message == (
        "Comment has no closing delimiter before end of source"
    )


def test_unexpected_page_exception_propagates(tmp_path, monkeypatch):
    from comment_review.flows import compositor as flow

    path = tmp_path / "sample.py"
    path.write_text("value = 1\n", encoding="utf-8")

    def broken_page(*args, **kwargs):
        raise exceptions.Refused("unexpected page error")

    monkeypatch.setattr(flow, "page_of", broken_page)
    with pytest.raises(exceptions.Refused, match="unexpected page error"):
        flow.round_trip(path)


@pytest.mark.parametrize(
    "original,rendered",
    [("a\r\n", "a\n"), ("a\n", "a"), ("\ufeffa\n", "a\n"), ("a\nb\n", "b\na\n")],
)
def test_identity_compares_literal_bytes(original, rendered):
    assert compositor.identity(original, rendered) is not None


@pytest.mark.parametrize("separator", ["\u2028", "\u2029", "\x85", "\x0b", "\x0c"])
@pytest.mark.parametrize("ending", ["\r\n", "\r", "\n"])
def test_identity_reports_physical_lines_with_literal_separators(separator, ending):
    original = f"s = '{separator}'{ending}x = 1{ending}"
    rendered = f"s = '{separator}'{ending}x = 2{ending}"
    expected = {
        "\r\n": "line 2: was 'x = 1\\r\\n', set 'x = 2\\r\\n'",
        "\r": "line 2: was 'x = 1\\r', set 'x = 2\\r'",
        "\n": "line 2: was 'x = 1\\n', set 'x = 2\\n'",
    }
    assert compositor.identity(original, rendered) == expected[ending]


@pytest.mark.parametrize(
    "original,rendered,expected",
    [
        ("a\r\n", "a\n", "line 1: was 'a\\r\\n', set 'a\\n'"),
        ("a\r", "a\n", "line 1: was 'a\\r', set 'a\\n'"),
        ("a\n", "a", "line 1: was 'a\\n', set 'a'"),
        ("a\n", "a\nb\n", "1 lines in, 2 out"),
        ("", "a\n", "0 lines in, 1 out"),
    ],
)
def test_identity_retains_line_endings_in_diagnostics(original, rendered, expected):
    assert compositor.identity(original, rendered) == expected


def test_retained_lines_are_weaker_than_identity():
    assert compositor.lossless("a\r\nb\n", "b\na\n") is None
    assert compositor.lossless("a\na\n", "a\n") == "line lost: 'a'"


def test_identity_requires_strict_utf8():
    with pytest.raises(UnicodeEncodeError):
        compositor.identity("\ud800", "\ud800")


def test_identical_literal_text_passes_both_comparisons():
    text = "\ufeffa\r\nb\n"
    assert compositor.identity(text, text) is None
    assert compositor.lossless(text, text) is None


@pytest.mark.parametrize("raw", [b"", b"x = 1\r\n"])
def test_command_sets_actual_empty_and_crlf_files(tmp_path, capsys, raw):
    from comment_review.commands.compositor import main

    path = tmp_path / "sample.py"
    path.write_bytes(raw)
    assert main([str(path)]) == 0
    assert "1 identical, 0 normalised, 0 LOSSY" in capsys.readouterr().out


def test_command_acquires_admits_and_sets_once(tmp_path, monkeypatch):
    from comment_review.commands.compositor import main
    from comment_review.flows import compositor as flow

    path = tmp_path / "sample.py"
    path.write_bytes(b"x = 1\r\n")
    calls = []
    for name, module in [
        ("source_of", flow),
        ("page_of", flow),
        ("set_page", compositor),
    ]:
        original = getattr(module, name)

        def counted(*args, _name=name, _original=original, **kwargs):
            calls.append(_name)
            return _original(*args, **kwargs)

        monkeypatch.setattr(module, name, counted)
    assert main([str(path)]) == 0
    assert calls == ["source_of", "page_of", "set_page"]


def test_rendering_refusal_retains_context(tmp_path, monkeypatch, capsys):
    from comment_review.commands.compositor import main
    from comment_review.flows.compositor import round_trip
    from comment_review.flows.read_diagnostics import LocatedReadFailure

    path = tmp_path / "sample.py"
    path.write_bytes(b"x = 1\r\n")

    def refused(page):
        raise exceptions.Refused("cannot set these places")

    monkeypatch.setattr(compositor, "set_page", refused)
    result = round_trip(path)
    assert isinstance(result, LocatedReadFailure)
    assert result.text == "x = 1\r\n"
    assert result.path == path.as_posix()
    assert result.language == "python"
    assert result.diagnostics[0].span is None
    assert main([str(path)]) == 1
    assert "place/unsupported-placement" in capsys.readouterr().out


def test_read_failure_reports_retained_location(tmp_path, capsys):
    from comment_review.commands.compositor import main

    path = tmp_path / "sample.c"
    path.write_bytes(b"int x;\r\n/* open")
    assert main([str(path)]) == 1
    output = capsys.readouterr().out
    assert "lex/unterminated-comment" in output
    assert "line 2, one-based; column 0, zero-based" in output


def test_python_bom_is_preserved_exactly(tmp_path, capsys):
    from comment_review.commands.compositor import main
    from comment_review.flows.compositor import RoundTrip, round_trip

    path = tmp_path / "sample.py"
    original = b"\xef\xbb\xbfx = 1\n"
    path.write_bytes(original)
    result = round_trip(path)
    assert isinstance(result, RoundTrip)
    assert result.original.encode("utf-8") == original
    assert result.rendered.encode("utf-8") == original
    assert main([str(path)]) == 0
    output = capsys.readouterr().out
    assert "1 identical, 0 normalised, 0 LOSSY" in output
    assert path.read_bytes() == original


def test_mixed_endings_set_as_crlf(tmp_path, capsys):
    from comment_review.commands.compositor import main
    from comment_review.flows.compositor import RoundTrip, round_trip

    path = tmp_path / "sample.py"
    path.write_bytes(b"x = 1\r\ny = 2\n")
    result = round_trip(path)
    assert isinstance(result, RoundTrip)
    assert result.original.encode("utf-8") == b"x = 1\r\ny = 2\n"
    assert result.rendered.encode("utf-8") == b"x = 1\r\ny = 2\r\n"
    assert main([str(path)]) == 0
    assert "0 identical, 1 normalised, 0 LOSSY" in capsys.readouterr().out


#: Every addressed place on the sample, and the subset holding prose. Discovered
#: from the page rather than listed, so a change to the walk is visible here as
#: a change in how many cases run.
ALL_CUES = list(by_cue(build(SAMPLE)))
FILLED_CUES = [
    c for c, b in by_cue(build(SAMPLE)).items() if any(x.strip() for x in b.raw_lines)
]

FORM_CASES = pytest.mark.parametrize(
    ("name", "text"),
    [
        pytest.param(
            n,
            t,
            id=k,
        )
        for k, (n, t) in FORMS.items()
    ],
)


@FORM_CASES
def test_what_goes_in_comes_out(name, text):
    """The identity. Every other property here is a way of narrowing WHY this
    might fail; this is the property itself."""
    assert set_page(build(text, name)) == text


@FORM_CASES
def test_setting_twice_changes_nothing_further(name, text):
    """Idempotence. A normalisation that happened on the first pass and again
    on the second would mean the output is not a fixed point -- so a file
    edited twice would drift without any edit saying so."""
    once = set_page(build(text, name))
    assert set_page(build(once, name)) == once


@FORM_CASES
def test_the_line_ending_is_the_FILE_S(name, text):
    """Nothing a paragraph says can state whether the file used CRLF, so a
    compositor that guessed would rewrite every line of a Windows checkout."""
    out = set_page(build(text, name))
    if "\r\n" in text:
        assert "\r\n" in out
        assert "\n" not in out.replace("\r\n", "")
    else:
        assert "\r" not in out


@FORM_CASES
def test_the_trailing_newline_is_the_FILE_S(name, text):
    """The reader drops it, so no paragraph can state it. A file that ended in
    one is set with one; a file that did not is not."""
    assert set_page(build(text, name)).endswith("\n") == text.endswith("\n")


@FORM_CASES
def test_no_line_is_invented_or_lost(name, text):
    """A weaker check than the identity, and it isolates the failure: a
    mismatch here is a COUNT problem rather than a content one."""
    assert len(set_page(build(text, name)).splitlines()) == len(text.splitlines())


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("// a\nlet x;\n\n// b\n// c\nlet y; // d\n", {"b1": (4, 5), "c1": (6, 6)}),
        ("/* f\n */\nlet x;\n", {"f0": (1, 2)}),
        ("", {}),
    ],
    ids=["gap-and-margin", "matter", "empty"],
)
def test_spans_name_the_lines_each_place_is_set_on(text, expected):
    page = build(text, "m.js")
    spans = compositor.spans(page)
    assert {c: spans[c] for c in expected} == expected
    lines = text.splitlines()
    for first, last in spans.values():
        assert 1 <= first <= last <= len(lines)
    assert set_page(page) == text


def test_spans_follow_a_place_that_grew():
    page = build("let w;\n// a\nlet x;\n// b\nlet y;\n", "m.js")
    gaps = [c for c, b in by_cue(page).items() if b.raw_lines == ["// a"]]
    below = [c for c, b in by_cue(page).items() if b.raw_lines == ["// b"]]
    assert compositor.spans(page)[below[0]] == (4, 4)
    galley.reset(page, {gaps[0]: "// a\n// more"})
    assert compositor.spans(page)[below[0]] == (5, 5)


class TestLineEndings:
    def test_a_file_with_no_ending_at_all_answers_LF(self):
        assert line_endings("x = 1") == "\n"

    def test_one_CRLF_anywhere_makes_the_file_CRLF(self):
        """The FIRST ending wins and mixed files are normalised -- a file
        holding both is already inconsistent, and picking per line would
        preserve a defect the author cannot see."""
        assert line_endings("a\nb\r\nc\n") == "\r\n"

    def test_an_explicit_ending_overrides_the_page(self):
        page = build("x = 1\ny = 2\n")
        assert "\r\n" in set_page(page, newline="\r\n")


class TestAPageThatWasNeverBuilt:
    def test_text_with_no_places_is_REFUSED_not_emptied(self):
        """MEASURED 2026-08-21 on a real file the floor interpreter cannot
        parse: 884 lines in, 0 characters out, silently. `draft()` writes what
        this returns, and an empty draft approved by anyone not reading the
        diff is a deleted file."""
        page = build("x = 1\n")
        page.cues.reading.clear()
        with pytest.raises(exceptions.Refused):
            set_page(page)

    def test_an_EMPTY_file_is_empty_text_and_not_a_refusal(self):
        """The one case where no places is the right answer."""
        assert set_page(build("")) == ""


class TestAnEditedPageStillComposes:
    """The write path end to end: read, change, set -- then read the result and
    confirm the change is where it was put."""

    @pytest.mark.parametrize("cue", FILLED_CUES)
    def test_the_composed_file_re_reads_with_the_text_AT_ITS_CUE(self, sample, cue):
        """! `any` OVER THE PAGE WAS THE ASSERTION UNTIL 2026-08-25, so text
        landing at the WRONG cue passed. The cue is the whole claim.

        !! AND IT RAN ON ONE CUE UNTIL 2026-08-26 -- `next(...)` over the filled
        `b` places, so ONE of the sample's fourteen was ever set back. Roy asked
        for every cue position; a case that picks a representative can pick past
        the one that is broken.
        """
        from comment_review.results.galley import reset

        # !! THE INDENT IS THE PLACE'S, NOT THE SERIES'. One literal for the
        # whole `a` series re-reads as a syntax error wherever it guesses wrong:
        # measured 2026-08-26, the four-space `REPLACEMENT["a"]` put at `a0`
        # made the composed file unparseable and EVERY cue disappeared. A module
        # docstring sits at column 0 and a method's at four or eight. ! The same
        # fact an alteration has to carry --
        # `TODO/a-alteration-carries-its-own-indentation.md`.
        first = by_cue(sample)[cue].raw_lines[0]
        pad = first[: len(first) - len(first.lstrip())]
        new = pad + REPLACEMENT["a"].lstrip() if cue[0] == "a" else REPLACEMENT[cue[0]]

        reset(sample, {cue: new})
        again = by_cue(build(set_page(sample)))
        assert cue in again
        assert any("REPLACED" in line for line in again[cue].raw_lines)

    @pytest.mark.parametrize("cue", ALL_CUES)
    def test_an_edited_page_is_still_a_fixed_point(self, sample, cue):
        """Set, read back, set again -- the second pass must change nothing,
        whichever place was emptied."""
        from comment_review.results.galley import reset

        reset(sample, {cue: None})
        out = set_page(sample)
        assert set_page(build(out)) == out

    def test_the_sample_itself_round_trips_before_any_edit(self):
        assert set_page(build(SAMPLE)) == SAMPLE

    def test_a_vacated_place_loses_its_leading(self, sample):
        """`Addressing: #22` -- the compositor derives a fence from the
        place's kind, so a place a `drop` vacated does not stand over
        whatever follows it. `a0` is the sample's one FILLED place whose
        edge owns a leading (`page.leading == {"a0": "d0", "c1": "d1"}`).
        """
        from comment_review.results.galley import reset

        reset(sample, {"a0": None})
        out = set_page(sample)
        assert "#!/usr/bin/env python\n# note\n" in out
        assert '"""Doc."""' not in out

    def test_a_vacated_gap_loses_its_leading(self):
        """The same rule at a `b`, on a page with no `a` at all, so a rule
        that fired only at `a0` fails here. `b1` owns the blank below it
        (`page.leading == {"c0": "d0", "b1": "d1"}`); dropped, the two
        statements keep the one blank `c0` owns, not both."""
        from comment_review.results.galley import reset

        page = build("x = 1\n\n# note\n\ny = 2\n")
        reset(page, {"b1": None})
        assert set_page(page) == "x = 1\n\ny = 2\n"

    def test_a_dropped_c_does_not_lose_the_blank_below_its_code(self, sample):
        """A `c` sets its line of code whether or not anything sits beside
        it, so dropping the comment on it vacates nothing the code did not
        already occupy -- `c1` keeps its owned leading (`d1`)."""
        from comment_review.results.galley import reset

        reset(sample, {"c1": None})
        out = set_page(sample)
        assert "return x + 1\n\n\ndef g(y):" in out


class TestAWrappedTrailingCommentIsONEPlace:
    """!! THE SHAPE THAT SETTLED `original_column` -- `decision-log.md Process:
    #69`. Roy, 2026-08-31: those fields *"don't have a way to identify how to
    build or use a wrapped trailing comment. The Series/Cue system handles that
    case piece-of-cake."*

        int x = 1; /* this comment
                      wraps onto a second line
                      and a third */

    ! IT WAS IN NO TEST IN THIS SUITE UNTIL 2026-08-31. Every block-comment case
    above puts the comment on its OWN line, and the one fixture holding code
    before an opener (`tests/test_proof_setter.py`) never reaches `page_for` --
    it is a fingerprint input for an UNPROVABLE file. So the field's own
    justifying case was untested, which is why nothing could notice it had
    stopped being needed.
    """

    WRAPPED = (
        "m.c",
        "int x = 1; /* this comment\n"
        "              wraps onto a second line\n"
        "              and a third */\n"
        "int y = 2;\n",
    )

    def test_the_whole_run_is_ONE_c_place(self):
        """The cue names the place; how many lines it spans is the place's own
        business. A per-line field would have to say something about each."""
        name, text = self.WRAPPED
        page = build(text, name)
        trailing = [b for b in page if b.kind == "trailing-comment"]
        assert len(trailing) == 1
        (place,) = trailing
        assert by_cue(page)[cue(place)] is place
        assert cue(place).startswith("c")
        assert len(place.raw_lines) == 3

    def test_the_lines_after_the_first_own_themselves_WHOLE(self):
        """What a single column cannot express: line 1 begins after code, and
        lines 2..N are entire lines of the file."""
        name, text = self.WRAPPED
        (place,) = [b for b in build(text, name) if b.kind == "trailing-comment"]
        lines = text.split("\n")
        assert place.raw_lines[0] != lines[0]
        assert place.raw_lines[0] in lines[0]
        assert place.raw_lines[1:] == lines[1:3]

    def test_the_SETTER_reconstructs_it_from_the_place_alone(self):
        """! THE NECESSITY TEST, and it can fail: break the place's own lines
        and the identity goes. What it proves is that the setter needs the
        place and its lines, and nothing about where the first one started."""
        name, text = self.WRAPPED
        assert set_page(build(text, name)) == text

        broken = build(text, name)
        (place,) = [b for b in broken if b.kind == "trailing-comment"]
        place.raw_lines = place.raw_lines[:1]
        assert set_page(broken) != text


SHARED_LINES = pytest.mark.parametrize(
    ("shared", "broken"),
    [
        ('def fn(): "doc"; y = 42\n', 'def fn():\n    "doc"\n    y = 42\n'),
        ('def fn(): "doc"\n', 'def fn():\n    "doc"\n'),
        (
            'class C:\n  def m(self): "doc"; y = 42  # note\n',
            'class C:\n  def m(self):\n    "doc"\n    y = 42  # note\n',
        ),
        ('def f():\n\t"""Doc."""; y = 42\n', 'def f():\n\t"""Doc."""\n\ty = 42\n'),
        ('"""Mod."""; y = 42\n', '"""Mod."""\ny = 42\n'),
        (
            'def f():\r\n    """Doc.""" ; y = 42\r\n',
            'def f():\r\n    """Doc."""\r\n    y = 42\r\n',
        ),
    ],
)


class TestADocstringSharingItsLineIsSetBroken:
    """The read breaks the line, so the page sets the broken source."""

    @SHARED_LINES
    def test_the_unedited_page_sets_the_broken_source(self, shared, broken):
        assert set_page(build(shared)) == broken

    @SHARED_LINES
    def test_a_docstring_grown_to_a_template_keeps_every_other_place(
        self, shared, broken
    ):
        from comment_review.results.galley import reset

        page = build(shared)
        doc = next(b for b in page if b.kind == "docstring")
        first = doc.raw_lines[0]
        pad = first[: len(first) - len(first.lstrip())]
        template = f'{pad}"""Summary.\n\n{pad}Returns:\n{pad}    A value.\n{pad}"""'
        assert reset(page, {cue(doc): template}) == []
        out = set_page(page)
        compile(out, "m.py", "exec")
        again = build(out)
        assert {cue(b) for b in again} == {cue(b) for b in build(broken)}
        assert by_cue(again)[cue(doc)].text == "Summary. Returns: A value."
        assert [
            (b.address, b.raw_text, b.anchor) for b in again if b.kind != "docstring"
        ] == [
            (b.address, b.raw_text, b.anchor)
            for b in build(broken)
            if b.kind != "docstring"
        ]


def test_a_docstring_continued_by_a_backslash_is_set_back_with_its_continuation():
    from comment_review.results.galley import reset

    page = build('def f():\n    """D.""" \\\n    \n    return 1\n')
    doc = next(b for b in page if b.kind == "docstring")
    assert reset(page, {cue(doc): '    """New doc.""" \\'}) == []
    out = set_page(page)
    assert out == 'def f():\n    """New doc.""" \\\n    \n    return 1\n'
    compile(out, "m.py", "exec")


@pytest.mark.parametrize("name", ["m.js", "m.ts"])
@pytest.mark.parametrize(
    ("place", "prose", "expected"),
    [
        (
            "f0",
            "#!/usr/bin/env node\n// Licence.",
            "#!/usr/bin/env node\n// Licence.\nfunction main() {}\n",
        ),
        (
            "a0",
            "/** Module. */",
            "#!/usr/bin/env node\n/** Module. */\nfunction main() {}\n",
        ),
    ],
    ids=["f0", "a0"],
)
def test_filling_the_head_of_a_shebang_file_keeps_the_shebang_on_line_one(
    name, place, prose, expected
):
    from comment_review.results.galley import reset

    page = build("#!/usr/bin/env node\nfunction main() {}\n", name)
    assert reset(page, {place: prose}) == []
    assert set_page(page) == expected


@pytest.mark.parametrize(
    ("text", "places", "expected"),
    [
        ("/** One. */\n", {"a1": "/** Two. */"}, "/** One. */\n/** Two. */\n"),
        ("/** One. */\n", {"a0": None, "a1": "/** Two. */"}, "/** Two. */\n"),
        (
            "// Licence.\n\n/** Doc. */\n",
            {"b0": "// Note.", "a1": "/** End. */"},
            "// Licence.\n\n/** Doc. */\n// Note.\n/** End. */\n",
        ),
        ("class A {}\n", {"a2": "/** Two. */"}, "class A {}\n/** Two. */\n"),
        (
            "class A {}\n",
            {"b1": "// Gap.", "a2": "/** End. */"},
            "class A {}\n// Gap.\n/** End. */\n",
        ),
        (
            "class A {}\n/** End. */\n",
            {"b1": "// Gap."},
            "class A {}\n// Gap.\n/** End. */\n",
        ),
    ],
    ids=[
        "below-a0",
        "a0-empty",
        "gap-and-closing",
        "below-code",
        "gap-and-closing-below-code",
        "gap-above-a-held-closing",
    ],
)
def test_an_added_closing_docstring_is_set_in_reading_order_and_nothing_more(
    text, places, expected
):
    # The places are set f0 a0 b0 a1 f1, and no line is set that no place
    # holds.
    from comment_review.results.galley import reset

    page = build(text, "m.js")
    assert reset(page, places) == []
    assert set_page(page) == expected


@pytest.mark.parametrize(
    ("name", "text", "place", "prose", "replaced"),
    [
        (
            "m.js",
            "y = 0;\n/* a\n b */ x = 1;\n// c\nfunction g() {}\n",
            "a1",
            "/** G */",
            "// c",
        ),
        (
            "m.js",
            "function f() {}\n/** a\n b */ x = 1;\n/** D */\nfunction g() {}\n",
            "a2",
            "/** G */",
            "/** D */",
        ),
        (
            "m.js",
            "/** a\n b */ x = 1;\n/** D */\nfunction g() {}\n",
            "a1",
            "/** G */",
            "/** D */",
        ),
        (
            "m.lua",
            "local a = 1\n--[[ a\n b ]] x = 1\n-- c\nlocal function g() end\n",
            "a1",
            "--- G",
            "-- c",
        ),
        (
            "m.js",
            "function f() {}\n/* a\n b */ x = 1;\n\n// c\nfunction g() {}\n",
            "a2",
            "/** G */",
            "// c",
        ),
    ],
    ids=["plain-facing", "doc-facing", "doc-facing-head", "lua", "blank-between"],
)
def test_filling_the_a_below_a_closing_line_with_code_keeps_that_line(
    name, text, place, prose, replaced
):
    # The `a` holds only its own run's lines, so the closing line and its
    # statement above it are set back as they were.
    from comment_review.results.galley import reset

    page = build(text, name)
    assert reset(page, {place: prose}) == []
    assert set_page(page) == text.replace(replaced, prose)


@pytest.mark.parametrize(
    ("name", "text", "places", "expected"),
    [
        ("m.js", "/** Doc. */\n", {"f0": "// licence"}, "// licence\n/** Doc. */\n"),
        ("m.js", "// licence\n", {"a0": "/** Doc. */"}, "// licence\n/** Doc. */\n"),
        (
            "m.js",
            "let x = 1;\n",
            {"f0": "// licence", "a0": "/** Doc. */"},
            "// licence\n/** Doc. */\nlet x = 1;\n",
        ),
        (
            "m.js",
            "#!/usr/bin/env node\nlet x = 1;\n",
            {"f0": "#!/usr/bin/env node\n// licence", "a0": "/** Doc. */"},
            "#!/usr/bin/env node\n// licence\n/** Doc. */\nlet x = 1;\n",
        ),
        (
            "m.py",
            "x = 1\n",
            {"f0": "# licence", "a0": '"""Doc."""'},
            '# licence\n"""Doc."""\nx = 1\n',
        ),
    ],
    ids=["doc-only", "matter-only", "code-only", "shebang", "python"],
)
def test_the_head_places_are_filled_and_set_back_in_reading_order(
    name, text, places, expected
):
    # f0 then a0, each set where it was filled. That the written text is read
    # back at the same places is the page's, in `tests/test_page_for.py`.
    from comment_review.results.galley import reset

    page = build(text, name)
    assert reset(page, places) == []
    assert set_page(page) == expected


@pytest.mark.parametrize("ending", ["\n", "\r\n"])
@pytest.mark.parametrize(
    ("text", "places"),
    [
        ('x=f"{value # note\n}"; after()\n', ("c0",)),
        ('x=f"""{\n    # note\n    value\n}"""; after()\n', ("b1",)),
        ('x=f"""{value # first\n\n    # second\n}"""; after()\n', ("c0", "b1")),
        ('x=f"""{\n    # first\n\n    # second\n    value\n}"""; after()\n', ("b1",)),
        ('x=f"""{f\'{\n    # note\n    value\n}\'}"""; after()\n', ("b1",)),
        ('x=f"{before}{value # note\n}{after}"; work()\n', ("c0",)),
        ('x=f"{value:{width # note\n}}"; work()\n', ("c0",)),
        ('x=f"{value # note } f\' x\n}"; after()\n', ("c0",)),
    ],
)
def test_a_comment_inside_an_expression_is_set_and_edited_around_the_expression(
    ending, text, places
):
    from comment_review.results.galley import reset

    text = text.replace("\n", ending)
    assert set_page(build(text)) == text
    for place in places:
        own = ending.join(by_cue(build(text))[place].raw_lines) + ending
        start = text.index(own)
        end = start + len(own)
        replacement = own.replace("# note", "# edited").replace("# first", "# edited")
        replacement += "    # added" + ending
        page = build(text)
        assert reset(page, {place: replacement}) == []
        assert set_page(page) == text[:start] + replacement + text[end:]
        page = build(text)
        assert reset(page, {place: None}) == []
        vacated = ending if place.startswith("c") else ""
        assert set_page(page) == text[:start] + vacated + text[end:]
