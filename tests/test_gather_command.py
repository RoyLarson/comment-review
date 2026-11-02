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
import json
import re

import pytest
from conftest import run_command

from comment_review.commands import gather as gather_command


def test_languages_reports_validated_programming_coverage(monkeypatch, capsys):
    from comment_review.reading import readers
    from comment_review.reading.language import INSTALLED_REGISTRY

    registry = INSTALLED_REGISTRY

    status, output = run_command(monkeypatch, capsys, gather_command, "--languages")
    assert status == 0
    rows = [
        line.split()
        for line in output.splitlines()[1:]
        if line and not line.startswith("A suffix")
    ]
    assert rows == [[value.language, *value.suffixes] for value in registry.definitions]
    assert ["python", ".py", ".pyi"] in rows
    monkeypatch.setattr(readers, "INSTALLED_BINDINGS", {})
    status, output = run_command(monkeypatch, capsys, gather_command, "--languages")
    assert status == 0
    listed = {line.split()[0] for line in output.splitlines() if line}
    assert listed.isdisjoint(value.language for value in registry.definitions)


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

#: Decoded source whose incomplete or unsupported lexical state must refuse.
CANNOT_PARSE = {
    "a syntax error": CONTROL.encode("utf-8") + b"\ndef broken(:\n    pass\n",
    "a NUL byte": CONTROL.encode("utf-8") + b"\nx = 'a\x00b'\n",
    "an unterminated string": CONTROL.encode("utf-8") + b'\ny = """open\n',
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


def test_utf8_bom_source_is_gathered_with_its_documentation(
    tmp_path, monkeypatch, capsys
):
    raw = b"\xef\xbb\xbf" + CONTROL.encode("utf-8")
    code, printed = _run(tmp_path, monkeypatch, capsys, raw)
    assert code == 0, printed
    assert '"reader": "python-lexical"' in printed
    assert "Module doc." in printed
    assert (tmp_path / "m.py").read_bytes() == raw


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


def test_a_rust_file_whose_paragraphs_share_an_address_is_named_and_stops_the_run(
    tmp_path, monkeypatch, capsys
):
    """The refusal holds over a reader record."""
    from comment_review.reading.paragraph import Paragraph
    from comment_review.reading.rust.records import RustRead
    from comment_review.reading.series import Kind

    found = [
        Paragraph("m.rs", 3, 3, Kind.COMMENT, raw_lines=["// one"]),
        Paragraph("m.rs", 3, 3, Kind.COMMENT, raw_lines=["// two"]),
    ]
    monkeypatch.setattr(RustRead, "paragraphs", lambda self, path: list(found))
    target = tmp_path / "m.rs"
    target.write_text("//! Package m.\nm!();\n/// F.\nfn f() {}\n", encoding="utf-8")
    code, printed = run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(tmp_path),
        str(target),
        with_stderr=True,
    )
    assert code != 0, printed
    assert "m.rs" in printed
    assert "place/address-held-twice" in printed


#: A doc comment behind an ordinary comment: the place model cannot hold it as
#: `f`'s `a`, so the read notes it.
DETACHED_RUST = "fn g() {}\n\n/// Docs for f.\n// plain note\nfn f() {}\n"


def _run_rust(tmp_path, monkeypatch, capsys, source: str, *extra: str):
    target = tmp_path / "lib.rs"
    target.write_text(source, encoding="utf-8", newline="")
    return run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(tmp_path),
        str(target),
        *extra,
        with_stderr=True,
    )


def test_detached_documentation_is_warned_on_stderr_and_exits_zero(
    tmp_path, monkeypatch, capsys
):
    out = tmp_path / "binder.json"
    code, printed = _run_rust(
        tmp_path, monkeypatch, capsys, DETACHED_RUST, "--out", str(out)
    )
    assert code == 0, printed
    assert "warning: lib.rs:3: detached documentation (owner on line 5)\n" in printed
    assert printed.count("warning:") == 1
    assert "warning" not in out.read_text(encoding="utf-8")


def test_detached_module_documentation_names_the_module_as_its_owner(
    tmp_path, monkeypatch, capsys
):
    source = "#![no_std]\n//! Module docs.\nfn f() {}\n"
    code, printed = _run_rust(tmp_path, monkeypatch, capsys, source)
    assert code == 0, printed
    assert "warning: lib.rs:2: detached documentation (owner: module)\n" in printed


def test_two_detached_runs_in_one_gap_print_two_warnings_on_their_own_lines(
    tmp_path, monkeypatch, capsys
):
    source = "fn g() {}\n/// a\n// x\n/// b\n// y\nfn f() {}\n"
    code, printed = _run_rust(tmp_path, monkeypatch, capsys, source)
    assert code == 0, printed
    lines = [ln for ln in printed.splitlines() if ln.startswith("warning:")]
    assert lines == [
        "warning: lib.rs:2: detached documentation (owner on line 6)",
        "warning: lib.rs:4: detached documentation (owner on line 6)",
    ]


def test_a_rust_file_without_detached_documentation_prints_no_detached_warning(
    tmp_path, monkeypatch, capsys
):
    code, printed = _run_rust(
        tmp_path, monkeypatch, capsys, "/// Docs for f.\nfn f() {}\n"
    )
    assert code == 0, printed
    assert "warning:" not in printed


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


def _gather(tmp_path, monkeypatch, capsys, *targets):
    """One gather through argv, its binder as written, and its exit and stderr."""
    out = tmp_path / "binder.json"
    code, printed = run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(tmp_path),
        "--out",
        str(out),
        *[str(t) for t in targets],
        with_stderr=True,
    )
    return code, printed, out


def _binder(out) -> dict:
    return json.loads(out.read_text(encoding="utf-8"))


def test_a_named_js_file_is_freeform_and_gather_exits_0(tmp_path, monkeypatch, capsys):
    page = tmp_path / "a.py"
    page.write_text(CONTROL, encoding="utf-8")
    # Bytes no reader could decode: a freeform file is listed, never opened.
    (tmp_path / "b.js").write_bytes(b"\xff\xfe\x00")
    code, printed, out = _gather(tmp_path, monkeypatch, capsys, page, tmp_path / "b.js")
    assert code == 0, printed
    wire = _binder(out)
    assert [p["path"] for p in wire["pages"]] == ["a.py"]
    assert wire["freeform"] == ["b.js"]
    assert "FREEFORM -- 1 file(s)" in printed


def test_a_binary_in_a_walked_directory_stays_passed_over(
    tmp_path, monkeypatch, capsys
):
    (tmp_path / "a.py").write_text(CONTROL, encoding="utf-8")
    (tmp_path / "b.js").write_text("// b\n", encoding="utf-8")
    (tmp_path / "logo.png").write_bytes(b"\x89PNG\x00")
    (tmp_path / "uv.lock").write_text("lock\n", encoding="utf-8")
    code, printed, out = _gather(tmp_path, monkeypatch, capsys, tmp_path)
    assert code == 0, printed
    assert _binder(out)["freeform"] == ["b.js"]
    assert "PASSED OVER --" in printed
    assert "logo.png" in printed and "uv.lock" in printed


def test_a_named_file_that_is_neither_read_nor_source_stops_the_gather(
    tmp_path, monkeypatch, capsys
):
    target = tmp_path / "logo.png"
    target.write_bytes(b"\x89PNG\x00")
    code, printed, _ = _gather(tmp_path, monkeypatch, capsys, target)
    assert code == 1, printed
    assert "logo.png" in printed


def test_a_python_file_that_fails_to_read_still_stops_the_gather(
    tmp_path, monkeypatch, capsys
):
    page = tmp_path / "a.py"
    page.write_bytes(b"\xff\xfe not utf-8\n")
    (tmp_path / "b.js").write_text("// b\n", encoding="utf-8")
    code, printed, _ = _gather(tmp_path, monkeypatch, capsys, page, tmp_path / "b.js")
    assert code == 1, printed
    assert "a.py" in printed
    assert "1 of 2 files handed in" in printed


def test_freeform_paths_are_sorted_repo_relative_and_listed_once(
    tmp_path, monkeypatch, capsys
):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "z.js").write_text("// z\n", encoding="utf-8")
    (tmp_path / "a.js").write_text("// a\n", encoding="utf-8")
    (tmp_path / "c.JS").write_text("// c\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    code, printed, out = _gather(
        tmp_path,
        monkeypatch,
        capsys,
        tmp_path / "src" / "z.js",
        "src/z.js",
        "a.js",
        "c.JS",
    )
    assert code == 0, printed
    assert _binder(out)["freeform"] == ["a.js", "c.JS", "src/z.js"]


@pytest.mark.parametrize("spelled", ["absolute", "dotted", "from_above"])
def test_a_freeform_file_outside_the_repo_stops_the_gather(
    tmp_path, monkeypatch, capsys, spelled
):
    repo = tmp_path / "repo"
    repo.mkdir()
    (tmp_path / "other").mkdir()
    outside = tmp_path / "other" / "x.js"
    outside.write_text("// x\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path if spelled == "from_above" else repo)
    target = {
        "absolute": outside,
        "dotted": "../other/x.js",
        "from_above": "other/x.js",
    }[spelled]
    code, printed, _ = _gather(repo, monkeypatch, capsys, target)
    assert code == 1, printed
    assert "x.js (outside the repository)" in printed
    assert "1 of 1 files handed in" in printed
