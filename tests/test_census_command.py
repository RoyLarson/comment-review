"""`commands/census.py`: what the census DOES with a file it cannot read.

!! THE CONTRACT IS `CLAUDE.md`'S, AND IT IS ONE SENTENCE -- *"every file handed
in is censused or the run stops."* So the only question here is whether a file
that produced no paragraphs makes the run stop, and it is asked the same way of
every kind of failure a file can have.

!! THE DEFECT THIS FILE WAS WRITTEN FOR IS AN ASYMMETRY, not a single case.
MEASURED 2026-08-29: a file the reader could not DECODE (latin-1 bytes, a
UTF-16 BOM) exited 1, while a file it could not PARSE (a syntax error, a NUL
byte, an unterminated string, a UTF-8 BOM) censused **0 paragraphs at exit 0**.
Both produce nothing; only one stopped. A file mid-refactor with a real syntax
error is the common case, and its prose reached no reviewer while stdout
reported a complete census.

! SO THE ASSERTIONS BELOW COMPARE THE TWO HALVES AGAINST EACH OTHER rather than
against a number this module produced. What "correct" means is that the two
agree -- which is checkable without knowing what either prints.

! Inputs are BYTES, written to a real file, because four of the six cases are
not expressible as text: the point of each is a byte sequence the reader
chokes on.
"""

import argparse
import io
from contextlib import redirect_stderr, redirect_stdout

import pytest

from comment_review.commands.census import _report

#: An ordinary nine-line Python page, and the CONTROL every case below is a
#: corruption of. It carries a module docstring, a comment, a declaration with
#: a docstring and a trailing comment -- so a run that reads it produces
#: paragraphs in several series and a run that does not produces none.
CONTROL = (
    '"""Module doc."""\n'
    "\n"
    "import os\n"
    "\n"
    "\n"
    "# a note\n"
    "def f(x):\n"
    '    """Doc."""\n'
    "    return x + 1  # beside\n"
)

#: The reader never gets a string at all -- `read_source` raises and the file
#: is refused upstream of any parse. These were ALREADY loud, and are here as
#: the half the other half must match.
CANNOT_DECODE = {
    "latin-1 bytes": CONTROL.encode("utf-8") + "\n# caf\xe9\n".encode("latin-1"),
    "a UTF-16 BOM": b"\xff\xfe" + CONTROL.encode("utf-16-le"),
}

#: The reader decodes the file and then cannot parse it. `paragraphs_stdlib`
#: CATCHES the failure and returns one `unparsed` paragraph rather than raising,
#: so the command's own `except` never fires -- and `page_for` gives that page
#: no addresses, so `carried` drops even the paragraph reporting the refusal.
CANNOT_PARSE = {
    "a syntax error": CONTROL.encode("utf-8") + b"\ndef broken(:\n    pass\n",
    "a NUL byte": CONTROL.encode("utf-8") + b"\nx = 'a\x00b'\n",
    "an unterminated string": CONTROL.encode("utf-8") + b'\ny = """open\n',
    # ! Its own TODO -- `bom-is-read-as-source.md` -- and this asserts only that
    # it is LOUD, not that the BOM is handled. A run that reports the file by
    # name and stops is a different thing from one that reads it correctly.
    "a UTF-8 BOM": b"\xef\xbb\xbf" + CONTROL.encode("utf-8"),
}


def _run(tmp_path, data: bytes, *, as_json: bool) -> tuple[int, str]:
    """One census over one file, and what it exited with.

    ! BOTH STREAMS, because the two paths refuse on different ones: the text
    path prints its refusal to stdout beside the listing a person reads, and
    the `--json` path prints to stderr so the refusal cannot land inside the
    document stage 5 parses. Asking only one stream would let a path go
    silent and still pass.
    """
    target = tmp_path / "m.py"
    target.write_bytes(data)
    args = argparse.Namespace(
        paths=[str(target)],
        repo=str(tmp_path),
        revise=0,
        census_only=False,
        json=as_json,
        filtered=False,
        include_matter=False,
        include_absent=False,
        out=None,
        languages=False,
    )
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = _report(args)
    return code, out.getvalue() + err.getvalue()


AS_JSON = pytest.mark.parametrize("as_json", [False, True], ids=["text", "json"])
UNREADABLE = pytest.mark.parametrize(
    ("why", "data"),
    [pytest.param(w, d, id=w) for w, d in {**CANNOT_DECODE, **CANNOT_PARSE}.items()],
)


@AS_JSON
def test_the_control_is_censused_and_the_run_succeeds(tmp_path, as_json):
    """The case has to be able to pass, or every refusal below proves nothing:
    this same file, uncorrupted, must census and exit 0."""
    code, printed = _run(tmp_path, CONTROL.encode("utf-8"), as_json=as_json)
    assert code == 0, printed
    assert "0 paragraphs" not in printed


@AS_JSON
@UNREADABLE
def test_a_file_that_produced_no_paragraphs_stops_the_run(tmp_path, why, data, as_json):
    """`CLAUDE.md`: *every file handed in is censused or the run stops.*

    ! Neither half of this may pass on its own. A run that exits 1 without
    naming the file leaves the caller unable to act, and a run that names it at
    exit 0 is read as a success by everything downstream.
    """
    code, printed = _run(tmp_path, data, as_json=as_json)
    assert code != 0, f"{why}: censused nothing and reported success\n{printed}"


@AS_JSON
@UNREADABLE
def test_the_file_that_stopped_the_run_is_NAMED(tmp_path, why, data, as_json):
    """Exit 1 over a run of many files says nothing about WHICH one to fix."""
    _, printed = _run(tmp_path, data, as_json=as_json)
    assert "m.py" in printed, f"{why}: not named\n{printed}"


@AS_JSON
def test_a_parse_failure_is_AS_LOUD_AS_a_decode_failure(tmp_path, as_json):
    """The measured defect, stated as the property that forbids it.

    ! It compares the two halves to EACH OTHER, so it holds whatever exit code
    the command settles on -- what it forbids is the two disagreeing.
    """
    def codes(cases: dict[str, bytes]) -> dict[str, int]:
        return {w: _run(tmp_path, d, as_json=as_json)[0] for w, d in cases.items()}

    decode, parse = codes(CANNOT_DECODE), codes(CANNOT_PARSE)
    assert set(decode.values()) == set(parse.values()), (
        "a file the reader cannot DECODE and a file it cannot PARSE both produce"
        f" no paragraphs, so both must land the same way: {decode} vs {parse}"
    )
