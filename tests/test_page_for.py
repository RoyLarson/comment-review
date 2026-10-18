"""`flows/page_for.py`: the read-and-build step, and the refusals its own
docstring promises.

Moved from `tests/test_proof_setter.py` 2026-08-26, where sitting in the write
chain's own file credited `proof_setter` with a contract that is `page_for`'s.
"""

import subprocess
import sys
from importlib import import_module
from pathlib import Path

import pytest
from conftest import SAMPLE, build, cue, docket_from

from comment_review.binder import page as page_mod
from comment_review.binder.binder import bind
from comment_review.binder.page import Page, page_for
from comment_review.flows import page_for as page_for_mod
from comment_review.flows import proof_setter
from comment_review.flows.language_definitions import installed_registry
from comment_review.flows.read_diagnostics import LocatedReadFailure, format_failure
from comment_review.machine.repo import Source
from comment_review.reading.addresser import Cues
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.records import PythonRead


def test_python_page_retains_complete_structured_read():
    text = '"module"\nx = 1\ndef f[T]():\n    "a\\n" "b"\n    return 1\n'
    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert isinstance(page.read, PythonRead)
    assert page.read.source.text is text
    assert [section.form for section in page.read.source.sections] == [
        "docstring",
        "docstring",
    ]
    assert [payload.text for payload in page.read.payloads] == ["module", "a\nb"]
    assert [owner.declaration for owner in page.read.source.documentation] == [
        None,
        0,
    ]
    assert page.reading.reader == "python-lexical"
    assert {b.address.rsplit("@", 1)[-1] for b in page.prose} == {"a0", "a1"}
    assert any("x = 1" in b.anchor for b in page)
    assert any("return 1" in b.anchor for b in page)


def test_python_page_bom_and_effective_cookie_preserve_exact_bytes():
    raw = b'\xef\xbb\xbf# coding: utf-8\r\n"module"\r\nx=1\r\n'
    text = raw.decode("utf-8")
    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert isinstance(page.read, PythonRead)
    assert page.read.source.reconstruct().encode("utf-8") == raw
    assert page.read.payloads[0].text == "module"
    assert [item.kind for item in page.read.protected] == ["encoding"]


@pytest.mark.parametrize("bom", ["", "\ufeff"])
@pytest.mark.parametrize("ending", ["\n", "\r\n"])
def test_python_page_contiguous_header_keeps_one_matter_place(bom, ending):
    from comment_review.reading.series import Kind
    from comment_review.results.compositor import set_page

    text = ending.join([bom + "# first", "# second", "x=1", ""])
    page = build(text)
    composed = set_page(page)
    assert composed.encode("utf-8") == text.encode("utf-8")
    for current in (page, build(composed)):
        filled = {cue(p): p for p in current if p.raw_text.strip()}
        assert set(filled) == {"f0"}
        assert filled["f0"].kind == Kind.MATTER
        assert filled["f0"].raw_lines == [bom + "# first", "# second"]
        assert isinstance(current.read, PythonRead)
        assert len(current.read.source.sections) == 1
        assert current.read.source.reconstruct() == text


def test_python_page_whole_comments_and_matter_boundaries():
    text = "# front\n\n# before\nx=1\n# a\n\n# b\ny=2\n# after\n\n# back\n"
    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert isinstance(page.read, PythonRead)
    assert len(page.read.source.sections) == 3
    prose = {p.address.rsplit("@", 1)[-1]: p.raw_text for p in page if p.raw_text}
    assert prose["f0"] == "# front"
    assert "# a\n\n# b" in prose.values()
    assert prose["f1"] == "# back"


@pytest.mark.parametrize(
    "text, doc_cue, raw",
    [
        ('"doc" # note\n', "a0", '"doc" # note'),
        ('def f():\n    "doc" # note\n', "a1", '    "doc" # note'),
        ('"""doc\ncontinued""" # note\n', "a0", '"""doc\ncontinued""" # note'),
        (
            'def f():\n    """doc\n    continued""" # note\n',
            "a1",
            '    """doc\n    continued""" # note',
        ),
    ],
)
def test_python_page_documentation_closing_comment_keeps_one_wire_owner(
    text, doc_cue, raw
):
    from comment_review.flows.gather import carried

    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert isinstance(page.read, PythonRead)
    doc = next(p for p in page if p.kind == "docstring")
    assert cue(doc) == doc_cue
    assert doc.raw_text == raw
    assert doc.text == ("doc continued" if "continued" in text else "doc")
    assert not any(p.kind == "trailing-comment" and p.raw_text.strip() for p in page)
    assert {p.address for p in carried(page) if p.raw_text.strip()} == {doc.address}
    wire = {row["cue"]: row for row in page.serialize()["rows"]}
    assert wire[doc_cue]["raw_text"] == doc.raw_text
    sections = page.read.source.sections
    assert [section.form for section in sections] == ["docstring"]
    assert page.read.source.slice(sections[0].span).endswith("# note")
    assert page.read.source.reconstruct() == text


@pytest.mark.parametrize(
    "text, expected",
    [
        ("x=1\n# first\n\n# second\ny=2\n", {"b1": 3}),
        ("x=1 # first\n\n# second\ny=2\n", {"c0": 1, "b1": 1}),
        (
            "# front\n\n# first\n\n# second\nx=1\n# after\n\n# back\n",
            {"f0": 1, "b0": 3, "b1": 1, "f1": 1},
        ),
    ],
)
def test_python_page_complete_comment_line_counts_preserve_wire_cap_eligibility(
    text, expected
):
    from comment_review.binder.page import RedactedPage
    from comment_review.desk.stages import Kind, Stage, deals

    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    restored, problems = RedactedPage.deserialize("fixture", page.serialize())
    assert problems == []
    assert restored is not None
    fresh = {cue(p): p for p in page if p.raw_text.strip()}
    saved = {cue(p): p for p in restored.paragraphs if p.raw_text.strip()}
    assert {key: p.lines for key, p in fresh.items()} == expected
    assert {key: p.lines for key, p in saved.items()} == expected
    for key, count in expected.items():
        assert fresh[key].raw_text == saved[key].raw_text
        assert fresh[key].lines == len(fresh[key].raw_lines)
        for cap in (1, 2, 3):
            stage = Stage("cap", Kind.EDITORIAL, cap=cap)
            assert deals(stage, fresh[key]) == deals(stage, saved[key]) == (count > cap)


def test_python_page_recognizes_once_and_retains_object_and_definition(monkeypatch):
    from comment_review.flows import reading_context
    from comment_review.reading import readers

    text = '"module"\ndef f():\n    "doc"\n    pass\n'
    registry = installed_registry()
    assert not isinstance(registry, ReadFailure)
    definition = registry.for_path(Path("m.py"))
    acquired = []
    recognized = []
    contexts = []
    original_read = readers.read_python
    original_resolve = reading_context.resolve_context

    def acquire():
        acquired.append(True)
        return registry

    def recognize(source, grammar):
        assert grammar is definition
        result = original_read(source, grammar)
        recognized.append(result)
        return result

    def resolve(grammar, *args, **kwargs):
        contexts.append(grammar)
        return original_resolve(grammar, *args, **kwargs)

    def forbidden(*args, **kwargs):
        pytest.fail("Python page rediscovered source interpretation")

    monkeypatch.setattr(page_for_mod, "installed_registry", acquire)
    monkeypatch.setattr(readers, "read_python", recognize)
    monkeypatch.setattr(reading_context, "resolve_context", resolve)
    monkeypatch.setattr(page_mod, "declarations", forbidden)
    monkeypatch.setattr(page_mod, "code_lines", forbidden)
    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert acquired == [True]
    assert contexts == [definition]
    assert len(recognized) == 1
    assert page.read is recognized[0]
    assert page.read.source.text is page.text is text
    assert set(page.serialize()) == {"path", "sha", "reading", "rows"}


@pytest.mark.parametrize(
    "text, addresses",
    [
        ("", {"a0"}),
        ("def f():\n", {"a0", "a1"}),
        ("class C:\n    def f():\n", {"a0", "a1", "a2"}),
    ],
)
def test_python_page_empty_documentation_places(text, addresses):
    page = page_for_mod.page_of(Path("m.pyi"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert {
        p.address.rsplit("@", 1)[-1] for p in page if p.kind == "undocumented"
    } == addresses


def test_python_page_documentation_raw_text_uses_existing_line_convention():
    text = 'def f():\r\n    ("a\\n"\r\n     "b")\r\n    pass\r\n'
    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert isinstance(page.read, PythonRead)
    doc = next(p for p in page if p.kind == "docstring")
    assert doc.text == "a b"
    assert doc.raw_text == '    ("a\\n"\n     "b")'
    assert page.read.source.text.encode("utf-8") == text.encode("utf-8")


@pytest.mark.parametrize(
    "text, expected",
    [
        ('x=f"{value # first\n\n # second\n}"\n', ["c0", "b1"]),
        ('x=f"""{\n # first\n\n # second\n value\n}"""\n', ["b1"]),
    ],
)
def test_python_page_interpolation_comments_keep_whole_sections(text, expected):
    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert isinstance(page.read, PythonRead)
    assert len(page.read.source.sections) == len(expected)
    assert [p.address.rsplit("@", 1)[-1] for p in page.prose] == expected
    assert len(page.prose) == len(expected)
    assert [p.raw_text for p in page.prose] == (
        [" # first", " # second"] if len(expected) == 2 else [" # first\n\n # second"]
    )


def test_python_page_protected_directives_keep_comment_classification():
    text = "# coding: utf-8\nx=1 # type: int\ny=2 # type: ignore[attr]\n"
    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert isinstance(page.read, PythonRead)
    assert [section.form for section in page.read.source.sections] == ["#"] * 3
    assert [p.raw_text for p in page if p.raw_text.strip()] == [
        "# coding: utf-8",
        " # type: int",
        " # type: ignore[attr]",
    ]
    assert page.read.source.reconstruct() == text
    assert [item.kind for item in page.read.protected] == [
        "encoding",
        "type-comment",
        "type-ignore",
    ]


@pytest.mark.parametrize(
    "literal",
    [
        't"""{\n # protected\n value\n}"""',
        'f"""{value # protected\n =}"""',
    ],
)
def test_python_page_protected_interpolation_comments_remain_classified(literal):
    text = "x=" + literal + "\n"
    page = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert isinstance(page.read, PythonRead)
    assert len(page.read.source.sections) == len(page.prose) == 1
    assert page.read.source.sections[0].form == "#"
    assert page.prose[0].text == "protected"
    assert page.read.source.reconstruct() == text
    assert page.read.protected


@pytest.mark.parametrize(
    "text, stage",
    [
        ('x="unterminated', ReadStage.LEX),
        ("x='a\x00b'\n", ReadStage.LEX),
        ('"\\xQ0"\n', ReadStage.PLACE),
        ('# coding: latin-1\n"doc"\n', ReadStage.PLACE),
    ],
)
def test_python_page_failures_never_reach_paragraph_adaptation(
    monkeypatch, text, stage
):
    def forbidden(*args):
        pytest.fail("Incomplete recognition reached paragraph adaptation")

    monkeypatch.setattr(page_mod, "paragraphs_for", forbidden)
    result = page_for_mod.page_of(Path("m.py"), source=Source(text, "held"))
    assert isinstance(result, LocatedReadFailure)
    assert result.diagnostics[0].stage == stage
    assert result.text is text


def test_python_page_definition_acquisition_failure_is_located(monkeypatch):
    failure = ReadFailure(
        (ReadDiagnostic(ReadStage.ACQUIRE, "io-error", "grammar absent"),)
    )
    monkeypatch.setattr(page_for_mod, "installed_registry", lambda: failure)
    result = page_for_mod.page_of(Path("m.py"), source=Source("x=1\n", "held"))
    assert isinstance(result, LocatedReadFailure)
    assert result.path == "m.py"
    assert result.diagnostics == failure.diagnostics


@pytest.mark.parametrize(
    "path, text",
    [("m.c", "int x; // note\n")],
)
def test_python_sections_projection_is_not_used_for_other_languages(
    monkeypatch, path, text
):
    def forbidden(*args):
        pytest.fail("Foundational section projection is not a production reader yet")

    projection = import_module("comment_review.reading.python.projection")
    monkeypatch.setattr(projection, "sections_for", forbidden)
    result = page_for_mod.page_of(Path(path), source=Source(text, "held"))
    assert isinstance(result, Page)
    assert result.text == text
    assert any("note" in paragraph.raw_text for paragraph in result.prose)


def test_empty_source_is_a_complete_page():
    registry = installed_registry()
    assert not isinstance(registry, ReadFailure)
    page = page_for(
        Path("empty.py"),
        "",
        sha="empty",
        reading=build("").reading,
        registry=registry,
    )
    assert isinstance(page, Page)
    assert page.text == ""
    assert page.sha == "empty"


def test_malformed_python_is_a_read_failure():
    registry = installed_registry()
    assert not isinstance(registry, ReadFailure)
    page = page_for(
        Path("bad.py"),
        "def broken(:\n",
        sha="bad",
        reading=build("").reading,
        registry=registry,
    )
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

    registry = installed_registry()
    assert not isinstance(registry, ReadFailure)
    selected = readers.reader_for(Path("m.py"), registry)
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
    def broken_reader(*args, **kwargs):
        raise RuntimeError("reader bug")

    monkeypatch.setattr(page_mod, "read_source", broken_reader)
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
    result = page_for_mod.page_of(Path("m.c"), source=Source("", "held"))
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
