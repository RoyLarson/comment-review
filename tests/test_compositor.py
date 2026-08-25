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
from conftest import SAMPLE, build, by_cue

from comment_review.machine import exceptions
from comment_review.results.compositor import line_endings, set_page

#: Every shape worth putting through it. Each is a file some checkout really
#: has; none has front matter below line 1.
FORMS = {
    "bare statement": ("m.py", "x = 1\n"),
    "no final newline": ("m.py", "x = 1"),
    "module docstring": ("m.py", '"""Doc."""\nx = 1\n'),
    "docstring then code": ("m.py", '"""Doc."""\n\n\nx = 1\n'),
    "comment above code": ("m.py", "# note\nx = 1\n"),
    "two comments": ("m.py", "# one\n# two\nx = 1\n"),
    "trailing comment": ("m.py", "x = 1  # beside\n"),
    "comment and trailing": ("m.py", "# above\nx = 1  # beside\n"),
    "blank between": ("m.py", "x = 1\n\n\ny = 2\n"),
    "leading blanks": ("m.py", "\n\nx = 1\n"),
    "trailing blanks": ("m.py", "x = 1\n\n\n"),
    "blanks both ends": ("m.py", "\n\nx = 1\n\n\n"),
    "shebang": ("m.py", "#!/usr/bin/env python\nx = 1\n"),
    "coding line": ("m.py", "# -*- coding: utf-8 -*-\nx = 1\n"),
    "shebang and docstring": ("m.py", '#!/usr/bin/env python\n"""D."""\nx = 1\n'),
    "function": ("m.py", 'def f():\n    """D."""\n    return 1\n'),
    "function no doc": ("m.py", "def f():\n    return 1\n"),
    "two functions": ("m.py", "def f():\n    return 1\n\n\ndef g():\n    return 2\n"),
    "nested def": ("m.py", "def f():\n    def g():\n        return 1\n    return g\n"),
    "class": ("m.py", 'class A:\n    """D."""\n\n    x = 1\n'),
    "class with method": ("m.py", "class A:\n    def m(self):\n        return 1\n"),
    "decorator": ("m.py", "@dec\ndef f():\n    return 1\n"),
    "only comments": ("m.py", "# one\n# two\n"),
    "only blanks": ("m.py", "\n\n\n"),
    "one blank": ("m.py", "\n"),
    "empty file": ("m.py", ""),
    "CRLF": ("m.py", "x = 1\r\ny = 2\r\n"),
    "CRLF with comment": ("m.py", "# note\r\nx = 1\r\n"),
    "CRLF no final": ("m.py", "x = 1\r\ny = 2"),
    "tabs": ("m.py", "def f():\n\treturn 1\n"),
    "unicode prose": ("m.py", "# caf\u00e9 na\u00efve \u2014 dash\nx = 1\n"),
    "long code run": ("m.py", "".join(f"x{i} = {i}\n" for i in range(20))),
    "deep indent": (
        "m.py",
        "def f():\n    if x:\n        if y:\n            return 1\n",
    ),
    "string with hash": ("m.py", 'x = "# not a comment"\n'),
    "C block": ("m.c", "/* head */\nint a;\n"),
    "C line comment": ("m.c", "// note\nint a;\n"),
    "C both": ("m.c", "/* one */\n// two\nint a;\n"),
    "cpp": ("m.cpp", "// note\nint a = 1;\n"),
    "rust doc": ("m.rs", "/// Doc.\npub fn f() {}\n"),
    "rust inner doc": ("m.rs", "//! Module doc.\npub fn f() {}\n"),
    "go": ("m.go", "// Doc.\nfunc f() {}\n"),
    "java": ("m.java", "/** Doc. */\npublic void f() {}\n"),
    "cs": ("m.cs", "/// <summary>D</summary>\npublic void F() {}\n"),
    "kotlin": ("m.kt", "/** Doc. */\nfun f() {}\n"),
    "swift": ("m.swift", "/// Doc.\nfunc f() {}\n"),
    "ts": ("m.ts", "/** Doc. */\nfunction f(): void {}\n"),
    "js": ("m.js", "// note\nlet a = 1;\n"),
    "ruby": ("m.rb", "# Doc.\ndef f\nend\n"),
    "lua": ("m.lua", "--- Doc.\nlocal function f() end\n"),
    "shell": ("m.sh", "#!/bin/sh\n# note\necho hi\n"),
    "toml": ("m.toml", "# note\nkey = 1\n"),
    "yaml": ("m.yaml", "# note\nkey: 1\n"),
    "ini": ("m.ini", "; note\n[a]\nb = 1\n"),
    "sql": ("m.sql", "-- note\nSELECT 1;\n"),
}
FORM_CASES = pytest.mark.parametrize(
    ("name", "text"),
    [pytest.param(n, t, id=k) for k, (n, t) in FORMS.items()],
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

    def test_the_composed_file_re_reads_with_the_text_AT_ITS_CUE(self, sample):
        """! `any` OVER THE PAGE WAS THE ASSERTION UNTIL 2026-08-25, so text
        landing at the WRONG cue passed. The cue is the whole claim."""
        from comment_review.results.galley import reset

        cue = next(
            c
            for c, b in by_cue(sample).items()
            if c.startswith("b") and any(x.strip() for x in b.raw_lines)
        )
        reset(sample, {cue: "# REPLACED"})
        again = build(set_page(sample))
        assert by_cue(again)[cue].raw_lines == ["# REPLACED"]

    def test_an_edited_page_is_still_a_fixed_point(self, sample):
        from comment_review.results.galley import reset

        reset(sample, {next(iter(by_cue(sample))): None})
        out = set_page(sample)
        assert set_page(build(out)) == out

    def test_the_sample_itself_round_trips_before_any_edit(self):
        assert set_page(build(SAMPLE)) == SAMPLE
