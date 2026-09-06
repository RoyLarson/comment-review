"""`commands/gather.py`: what the gather DOES with a file it cannot read, and
that the command builds no page of its own.

!! THE CONTRACT IS `CLAUDE.md`'S, AND IT IS ONE SENTENCE -- *"every file handed
in is gathered or the run stops."* So the only question here is whether a file
that produced no paragraphs makes the run stop, and it is asked the same way of
every kind of failure a file can have.

!! THE DEFECT THIS FILE WAS WRITTEN FOR IS AN ASYMMETRY, not a single case.
MEASURED 2026-08-29: a file the reader could not DECODE (latin-1 bytes, a
UTF-16 BOM) exited 1, while a file it could not PARSE (a syntax error, a NUL
byte, an unterminated string, a UTF-8 BOM) gathered **0 paragraphs at exit 0**.
Both produce nothing; only one stopped. A file mid-refactor with a real syntax
error is the common case, and its prose reached no reviewer while stdout
reported a complete gather.

! SO THE ASSERTIONS BELOW COMPARE THE TWO HALVES AGAINST EACH OTHER rather than
against a number this module produced. What "correct" means is that the two
agree -- which is checkable without knowing what either prints.

! Inputs are BYTES, written to a real file, because four of the six cases are
not expressible as text: the point of each is a byte sequence the reader
chokes on.
"""

import inspect
import re

import pytest
from conftest import run_command

from comment_review.commands import gather as gather_command

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


def _run(tmp_path, monkeypatch, capsys, data: bytes) -> tuple[int, str]:
    """One gather over one file, through `main()` and argv, and what it exited with.

    ! BOTH STREAMS. A refusal prints to stderr so it cannot land inside the
    binder stage 5 parses; asking only stdout would let the run go silent and
    still pass.
    """
    target = tmp_path / "m.py"
    target.write_bytes(data)
    return run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(tmp_path),
        str(target),
        with_stderr=True,
    )


UNREADABLE = pytest.mark.parametrize(
    ("why", "data"),
    [pytest.param(w, d, id=w) for w, d in {**CANNOT_DECODE, **CANNOT_PARSE}.items()],
)


def test_the_control_is_gathered_and_the_run_succeeds(tmp_path, monkeypatch, capsys):
    """The case has to be able to pass, or every refusal below proves nothing:
    this same file, uncorrupted, must gather and exit 0."""
    code, printed = _run(tmp_path, monkeypatch, capsys, CONTROL.encode("utf-8"))
    assert code == 0, printed
    assert "0 paragraphs" not in printed


@UNREADABLE
def test_a_file_that_produced_no_paragraphs_stops_the_run(
    tmp_path, monkeypatch, capsys, why, data
):
    """`CLAUDE.md`: *every file handed in is gathered or the run stops.*

    ! Neither half of this may pass on its own. A run that exits 1 without
    naming the file leaves the caller unable to act, and a run that names it at
    exit 0 is read as a success by everything downstream.
    """
    code, printed = _run(tmp_path, monkeypatch, capsys, data)
    assert code != 0, f"{why}: gathered nothing and reported success\n{printed}"


@UNREADABLE
def test_the_file_that_stopped_the_run_is_NAMED(
    tmp_path, monkeypatch, capsys, why, data
):
    """Exit 1 over a run of many files says nothing about WHICH one to fix."""
    _, printed = _run(tmp_path, monkeypatch, capsys, data)
    assert "m.py" in printed, f"{why}: not named\n{printed}"


def test_a_parse_failure_is_AS_LOUD_AS_a_decode_failure(tmp_path, monkeypatch, capsys):
    """The measured defect, stated as the property that forbids it.

    ! It compares the two halves to EACH OTHER, so it holds whatever exit code
    the command settles on -- what it forbids is the two disagreeing.
    """

    def codes(cases: dict[str, bytes]) -> dict[str, int]:
        return {w: _run(tmp_path, monkeypatch, capsys, d)[0] for w, d in cases.items()}

    decode, parse = codes(CANNOT_DECODE), codes(CANNOT_PARSE)
    assert set(decode.values()) == set(parse.values()), (
        "a file the reader cannot DECODE and a file it cannot PARSE both produce"
        f" no paragraphs, so both must land the same way: {decode} vs {parse}"
    )


def test_the_command_builds_no_page_and_resolves_no_annotation():
    """`TODO/completed/census-should-be-a-chain-of-producers.md` T3, verify text
    word for word: *it calls page_for nowhere*. And `annotate` nowhere, for the
    same reason -- both are the flow's steps, and a command exposes a flow.

    ! READ OFF THE MODULE'S SOURCE, so a name reached through a different
    import spelling is caught the same as a direct one."""
    source = inspect.getsource(gather_command)
    assert not re.search(r"\bpage_for\b", source)
    assert not re.search(r"\bannotate\b", source)
    assert "gather(" in source, "the command has to call the flow it exposes"
