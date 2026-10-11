"""`flows/page_for.py`: the read-and-build step, and the refusals its own
docstring promises.

Moved from `tests/test_proof_setter.py` 2026-08-26, where sitting in the write
chain's own file credited `proof_setter` with a contract that is `page_for`'s.
"""

import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SAMPLE, build, cue, docket_from

from comment_review.binder import page as page_mod
from comment_review.binder.binder import bind
from comment_review.binder.page import Page, page_for
from comment_review.flows import page_for as page_for_mod
from comment_review.flows import proof_setter
from comment_review.flows.read_diagnostics import LocatedReadFailure, format_failure
from comment_review.machine.repo import Source
from comment_review.reading.addresser import Cues
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.lexer import language_for


def test_empty_source_is_a_complete_page():
    lang = language_for(Path("empty.py"))
    assert lang is not None
    page = page_for(Path("empty.py"), "", lang, sha="empty")
    assert isinstance(page, Page)
    assert page.text == ""
    assert page.sha == "empty"


def test_malformed_python_is_a_read_failure():
    lang = language_for(Path("bad.py"))
    assert lang is not None
    page = page_for(Path("bad.py"), "def broken(:\n", lang, sha="bad")
    assert isinstance(page, ReadFailure)
    assert page.diagnostics[0].stage.value == "lex"


def test_snapshot_is_retained_without_acquisition(monkeypatch):
    def unexpected_read(path):
        raise AssertionError("snapshot was acquired twice")

    monkeypatch.setattr(page_for_mod, "source_of", unexpected_read)
    failure = page_for_mod.page_of(Path("broken.c"), source=Source("/* open", "held"))
    assert isinstance(failure, LocatedReadFailure)
    assert failure.path == "broken.c"
    assert failure.language == "c"
    assert failure.text == "/* open"


def test_supplied_successful_snapshot_keeps_text_and_hash(monkeypatch):
    def unexpected_read(path):
        raise AssertionError("snapshot was acquired twice")

    monkeypatch.setattr(page_for_mod, "source_of", unexpected_read)
    snapshot = Source("v = 1\r\n", "supplied-hash")
    page = page_for_mod.page_of(Path("m.py"), source=snapshot)
    assert isinstance(page, Page)
    assert page.text == "v = 1\r\n"
    assert page.sha == "supplied-hash"


def test_unknown_language_is_selection_failure():
    failure = page_for_mod.page_of(Path("file.unknown"), source=Source("data", "held"))
    assert isinstance(failure, ReadFailure)
    assert failure.diagnostics[0].stage.value == "select"
    assert failure.diagnostics[0].code == "unsupported-language"


def test_failed_reader_never_assigns_places(monkeypatch):
    def unexpected_places(*args):
        raise AssertionError("failed input reached placement")

    monkeypatch.setattr(page_mod, "places_on", unexpected_places)
    result = page_for_mod.page_of(
        Path("bad.py"), source=Source("def broken(:\n", "bad")
    )
    assert isinstance(result, ReadFailure)


def test_unavailable_binding_is_never_invoked_or_addressed(monkeypatch):
    from dataclasses import replace

    from comment_review.reading import readers

    selected = readers.reader_for(Path("m.py"))
    assert selected is not None and not isinstance(selected, ReadFailure)
    definition, binding = selected

    def forbidden(*args):
        pytest.fail("An unavailable binding must not read or assign places")

    monkeypatch.setattr(page_mod, "places_on", forbidden)
    monkeypatch.setattr(
        readers,
        "INSTALLED_BINDINGS",
        {
            definition.reader: replace(
                binding, capabilities=("comments",), read=forbidden
            )
        },
    )
    result = page_for_mod.page_of(Path("m.PY"), source=Source("x = 1\n", "held"))
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].code == "unavailable-reader"


def test_unexpected_reader_exception_propagates(monkeypatch):
    def broken_reader(*args):
        raise RuntimeError("reader bug")

    monkeypatch.setattr(page_mod, "read_paragraphs", broken_reader)
    with pytest.raises(RuntimeError, match="reader bug"):
        page_for_mod.page_of(Path("m.py"), source=Source("v = 1\n", "held"))


def test_located_error_renders_after_file_is_removed(tmp_path):
    path = tmp_path / "m.c"
    path.write_text("int v;\n/* open", encoding="utf-8", newline="")
    failure = page_for_mod.page_of(path, rel="m.c")
    assert isinstance(failure, LocatedReadFailure)
    path.unlink()
    assert format_failure(failure, path="m.c") == (
        "m.c [c] lex/unterminated-comment: Comment has no closing delimiter before "
        "end of source (line 2, one-based; column 0, zero-based)"
    )


@pytest.mark.parametrize(
    ("series", "cue_name", "message"),
    [
        ("c", "c0", "c0: a `c` place whose anchor has no line"),
        (
            "a",
            "z0",
            "no rule for the series of 'z0' -- every series in"
            " `addresser.SERIES` needs a branch here",
        ),
    ],
)
def test_known_placement_refusal_is_an_outcome(monkeypatch, series, cue_name, message):
    cues = Cues()
    cues.addressers[series].places[cue_name] = "<module>"
    monkeypatch.setattr(page_mod, "places_on", lambda *args: cues)
    result = page_for_mod.page_of(Path("m.py"), source=Source("", "held"))
    assert isinstance(result, LocatedReadFailure)
    assert result.diagnostics == (
        ReadDiagnostic(
            ReadStage.PLACE,
            "unsupported-placement",
            message,
        ),
    )


def test_failed_acquisition_has_no_invented_context(tmp_path):
    result = page_for_mod.page_of(tmp_path / "absent.py")
    assert isinstance(result, LocatedReadFailure)
    assert result.language is None
    assert result.text is None
    assert result.diagnostics[0].stage == ReadStage.ACQUIRE


def test_render_script_reports_failed_page_through_normal_invocation(tmp_path):
    path = tmp_path / "broken.c"
    path.write_text("/* open", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts" / "render_page.py"
    result = subprocess.run(
        [sys.executable, str(script), str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "SKIP" in result.stdout
    assert "lex/unterminated-comment" in result.stdout
    assert result.stderr == ""


@pytest.mark.parametrize("show", ["margin", "prose"])
def test_render_script_renders_successful_page(tmp_path, show):
    path = tmp_path / "sample.py"
    path.write_text("# invented note\nvalue = 1\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts" / "render_page.py"
    result = subprocess.run(
        [sys.executable, str(script), "--show", show, str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "invented note" in result.stdout
    assert "SKIP" not in result.stdout
    assert result.stderr == ""


def address(binder, path: str, series: str = "b") -> str:
    """One address off the binder, in the FORM THE BINDER PUBLISHES.

    !! EVERY TEST HERE HAND-WROTE `f"{rel}@{cue}"` UNTIL 2026-08-25, and that
    is what hid the CRITICAL defect: an address carries the FLATTENED path --
    `pkg:a:util.py` -- and a hand-written one carries `/`. `by_page` splits
    whatever it is handed, so the tests fed the chain a form nothing produces
    and only repo-root files, whose flattened form is their path, agreed. The
    fixture could not disagree with the code because the fixture was written to
    match it.

    ! IT ASKS `Binder.paragraphs`, which is what a caller of this chain has.
    """
    for row in binder.paragraphs:
        if row.path == path and cue(row).startswith(series) and row.raw_text.strip():
            return row.address
    raise AssertionError(f"no filled {series} row for {path}")


def _tree(tmp_path):
    """A one-file repo, and the binder taken over it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    return repo, bind([page], read_from={"root": str(repo), "revise": 0}), page


class TestPageOfReturnsEveryRefusalItPromises:
    """Failed initial and draft reads refuse the write chain."""

    def test_a_Refused_comes_back_as_a_REASON(self, tmp_path, monkeypatch):
        def refusing_page_for(*args, **kwargs):
            return ReadFailure(
                (
                    ReadDiagnostic(
                        ReadStage.PLACE,
                        "unsupported-placement",
                        "c0: anchor has no line",
                    ),
                )
            )

        monkeypatch.setattr(page_for_mod, "page_for", refusing_page_for)
        path = tmp_path / "m.py"
        path.write_text(SAMPLE, encoding="utf-8", newline="")

        page = page_for_mod.page_of(path, rel="m.py")
        assert isinstance(page, ReadFailure)
        assert "anchor has no line" in page.diagnostics[0].message

    def test_a_Refused_REFUSES_THE_RUN_instead_of_escaping(self, tmp_path, monkeypatch):
        """! THE PATCH REACHES `_one`'s READ ONLY, because the run stops there.
        `_reread`'s own read is the case below."""
        repo, binder, _ = _tree(tmp_path)

        def refusing_page_for(*args, **kwargs):
            return ReadFailure(
                (
                    ReadDiagnostic(
                        ReadStage.PLACE,
                        "unsupported-placement",
                        "c0: anchor has no line",
                    ),
                )
            )

        monkeypatch.setattr(page_for_mod, "page_for", refusing_page_for)
        drafted, refused = proof_setter.run(
            docket_from({address(binder, "m.py"): "# REPLACED"}, binder),
            repo,
            tmp_path / "out",
        )
        assert drafted == []
        assert refused[0].step == "read"

    def test_a_Refused_ON_THE_DRAFT_refuses_at_reread(self, tmp_path, monkeypatch):
        """CRITICAL, measured 2026-08-26: `_reread` inlined `read_source`,
        `language_for` and `page_for` with NO handler for either
        `exceptions.Refused` or `READ_ERRORS`, so a draft tripping `page_for`'s
        raise escaped `run()` as a traceback -- past its documented
        `(drafted, []) or ([], refusals)`.

        ! THE CASE ABOVE COULD NOT SEE IT: it patches the name `page_of` reads,
        which the inlined copy never consulted, and `_one`'s read refuses first
        anyway. This one refuses the DRAFT alone, so the chain reaches the step
        under test."""
        repo, binder, _ = _tree(tmp_path)
        into = tmp_path / "out"
        real_page_for = page_for_mod.page_for

        def refusing_on_the_draft(path, *args, **kwargs):
            if Path(path).resolve().is_relative_to(into.resolve()):
                return ReadFailure(
                    (
                        ReadDiagnostic(
                            ReadStage.PLACE,
                            "unsupported-placement",
                            "c0: anchor has no line",
                        ),
                    )
                )
            return real_page_for(path, *args, **kwargs)

        monkeypatch.setattr(page_for_mod, "page_for", refusing_on_the_draft)
        drafted, refused = proof_setter.run(
            docket_from({address(binder, "m.py"): "# REPLACED"}, binder), repo, into
        )
        assert drafted == []
        assert [r.step for r in refused] == ["reread"]
        assert "anchor has no line" in refused[0].why
        assert list(into.iterdir()) == []
