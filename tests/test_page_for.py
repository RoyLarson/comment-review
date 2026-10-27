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
from conftest import SAMPLE, build, by_cue, cue, docket_from

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
from comment_review.reading.lexer import LexicalRead
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.python.records import PythonRead
from comment_review.reading.series import Kind
from comment_review.reading.source import CodeLine, DocPlace


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
    assert [
        page.read.source.slice(payload.statement) for payload in page.read.payloads
    ] == ['"module"', '"a\\n" "b"']
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
    assert page.read.source.slice(page.read.payloads[0].statement) == ('"module"')
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


def test_a_margin_holds_what_follows_its_anchor_on_the_line():
    no_break_space = chr(0xA0)
    text = "struct S {\n" + no_break_space + "\n    x: i32,\n}\n"
    page = build(text, "m.rs")
    margin = next(p for p in page if p.anchor == no_break_space and p.kind == "margin")
    assert margin.raw_lines == [""]


@pytest.mark.parametrize("name", ["m.rs", "m.py", "m.js"])
@pytest.mark.parametrize("rest", ["x = 1\n", "# Licence\nx = 1\n"])
def test_a_page_opening_with_a_line_holding_only_a_byte_order_mark_sets_back(
    name, rest
):
    from comment_review.results.compositor import set_page

    if name != "m.py":
        rest = rest.replace("# ", "// ").replace("x = 1", "fn main() {}")
    text = chr(0xFEFF) + "\n" + rest
    page = build(text, name)
    assert set_page(page) == text


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
    monkeypatch.setattr(readers, "read_lexical", forbidden)
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

    monkeypatch.setattr(PythonRead, "paragraphs", forbidden)
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

    monkeypatch.setattr(page_mod, "cue", unexpected_places)
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

    monkeypatch.setattr(page_mod, "cue", forbidden)
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


@pytest.mark.parametrize(
    ("anchor", "place"),
    [("<eof>", "a1"), ("", "a0")],
    ids=["closing-at-eof", "opening-at-a0"],
)
def test_module_documentation_takes_the_a_its_anchor_names(monkeypatch, anchor, place):
    from comment_review.results.compositor import set_page

    text = "x;\n/** d */\n" if anchor else "/** d */\nx;\n"
    line = 2 if anchor else 1
    doc = Paragraph("m.c", line, line, Kind.DOCSTRING, anchor=anchor)
    doc.raw_lines = ["/** d */"]
    code = CodeLine(1 if anchor else 2, "x;", None)

    def read(*args, **kwargs):
        return LexicalRead([doc], [code], True, True)

    monkeypatch.setattr(page_mod, "read_source", read)
    page = page_for_mod.page_of(Path("m.c"), source=Source(text, "held"))
    assert isinstance(page, Page)
    assert (by_cue(page)[place].kind, by_cue(page)[place].raw_lines) == (
        Kind.DOCSTRING,
        ["/** d */"],
    )
    assert set_page(page) == text


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
    monkeypatch.setattr(page_mod, "cue", lambda *args, **kwargs: cues)
    result = page_for_mod.page_of(Path("m.c"), source=Source("", "held"))
    assert isinstance(result, LocatedReadFailure)
    assert result.diagnostics == (
        ReadDiagnostic(
            ReadStage.PLACE,
            "unsupported-placement",
            message,
        ),
    )


GO_DOCUMENTED = "// Package m.\npackage m\n// F.\nfunc F() {}\n"


def page_over_read(monkeypatch, found: list[Paragraph]) -> Page | ReadFailure:
    """`page_for` over GO_DOCUMENTED, handed these paragraphs and its code lines."""
    reading = build("", "m.go").reading
    lines = [
        CodeLine(2, "package m", None),
        CodeLine(4, "func F() {}", DocPlace(4, True)),
    ]
    read = LexicalRead(found, lines, True, True)
    monkeypatch.setattr(page_mod, "read_source", lambda *args, **kwargs: read)
    return page_for(
        Path("m.go"), GO_DOCUMENTED, rel="m.go", sha="held", reading=reading
    )


def test_documentation_lands_at_the_a_of_the_line_it_names(monkeypatch):
    page = page_over_read(
        monkeypatch,
        [
            Paragraph("m.go", 1, 1, Kind.DOCSTRING, raw_lines=["// Package m."]),
            Paragraph("m.go", 3, 3, Kind.DOCSTRING, anchor_line=4, raw_lines=["// F."]),
        ],
    )
    assert isinstance(page, Page)
    assert [
        (cue(p), p.anchor_line, p.anchor) for p in page if p.kind == Kind.DOCSTRING
    ] == [("a0", None, "<module>"), ("a1", 4, "func F() {}")]


@pytest.mark.parametrize("line", [2, 3], ids=["code-declaring-nothing", "no-code"])
def test_documentation_naming_no_declaring_line_is_refused(monkeypatch, line):
    found = [
        Paragraph("m.go", 3, 3, Kind.DOCSTRING, anchor_line=line, raw_lines=["// F."])
    ]
    result = page_over_read(monkeypatch, found)
    assert isinstance(result, ReadFailure)
    assert [d.code for d in result.diagnostics] == ["documentation-declares-nothing"]


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


RUST_ITEMS = (
    "//! Module doc.\n"
    "\n"
    "/// A point.\n"
    "#[derive(Debug)]\n"
    "pub struct Point {\n"
    "    /// The x.\n"
    "    pub x: i32,\n"
    "}\n"
    "\n"
    "fn helper() {} // trailing\n"
)


def _places(page) -> dict[str, tuple[str, str]]:
    """Each addressed place's cue -> (kind, anchor)."""
    return {cue(b): (b.kind, b.anchor) for b in page.paragraphs if b.address}


def test_rust_page_addresses_documented_items_fields_and_trailing_comments():
    page = build(RUST_ITEMS, "m.rs")
    places = _places(page)
    assert places["a0"] == ("docstring", "<module>")
    assert places["a1"] == ("docstring", "#[derive(Debug)]")
    assert places["a2"] == ("docstring", "    pub x: i32,")
    assert places["a3"] == ("undocumented", "fn helper() {}")
    assert sorted(c for c in places if c[0] == "a") == ["a0", "a1", "a2", "a3"]
    assert places["c4"] == ("trailing-comment", "fn helper() {}")
    assert [c for c in places if c[0] == "b"] == [f"b{n}" for n in range(6)]
    assert {c for c in places if c[0] == "f"} == {"f0", "f1"}


def test_rust_page_empty_a_sets_its_doc_above_the_attribute_line():
    from comment_review.results.compositor import set_page
    from comment_review.results.galley import reset

    text = "#[derive(Debug)]\npub struct S;\n"
    page = build(text, "m.rs")
    assert _places(page)["a1"] == ("undocumented", "#[derive(Debug)]")
    reset(page, {"a1": "/// Added."})
    assert set_page(page) == "/// Added.\n#[derive(Debug)]\npub struct S;\n"


def test_rust_page_item_on_line_one_sets_module_doc_then_item_doc():
    from comment_review.results.compositor import set_page
    from comment_review.results.galley import reset

    page = build("fn f() {}\n", "m.rs")
    places = _places(page)
    assert places["a0"][0] == places["a1"][0] == "undocumented"
    reset(page, {"a0": "//! Module.", "a1": "/// F."})
    assert set_page(page) == "//! Module.\n/// F.\nfn f() {}\n"


def test_rust_page_inner_doc_above_nothing_is_the_module_docstring():
    places = _places(build("//! Module.\n", "m.rs"))
    assert places["a0"] == ("docstring", "<module>")


def test_rust_page_outer_doc_above_nothing_is_a_comment():
    page = build("fn f() {\n    /// Orphan.\n}\n", "m.rs")
    orphan = next(b for b in page.prose if "Orphan" in b.text)
    assert orphan.kind == "comment"
    assert cue(orphan)[0] == "b"


def test_rust_page_opening_ordinary_comment_is_front_matter():
    places = _places(build("// Copyright 2026 Example\nfn main() {}\n", "m.rs"))
    assert places["f0"][0] == "matter"
    assert places["a1"] == ("undocumented", "fn main() {}")


def test_rust_page_opening_comment_below_a_blank_line_one_is_a_comment():
    from comment_review.results.compositor import set_page

    text = "\n// Copyright\nfn main() {}\n"
    page = build(text, "m.rs")
    run = next(b for b in page.paragraphs if "Copyright" in b.text)
    assert run.kind == "comment"
    assert cue(run) == "b0"
    assert set_page(page) == text


def test_rust_page_comment_directly_below_a_shebang_joins_it_at_f0():
    from comment_review.results.compositor import set_page

    text = "#!/usr/bin/env rust-script\n// Copyright\nfn main() {}\n"
    page = build(text, "m.rs")
    matter = [b for b in page.paragraphs if b.raw_lines and "//" in b.raw_text]
    assert [(b.kind, cue(b)) for b in matter] == [("matter", "f0")]
    assert matter[0].raw_lines == ["#!/usr/bin/env rust-script", "// Copyright"]
    assert [text[s.start : s.end] for s in page.read.protected] == [
        "#!/usr/bin/env rust-script"
    ]
    assert set_page(page) == text


def test_rust_page_shebang_matter_runs_to_the_first_blank_whatever_the_forms():
    from comment_review.results.compositor import set_page
    from comment_review.results.galley import reset

    text = "#!/usr/bin/env rust-script\n// Copyright\n/// d\n// e\nfn f() {}\n"
    page = build(text, "m.rs")
    places = by_cue(page)
    assert places["f0"].raw_lines == [
        "#!/usr/bin/env rust-script",
        "// Copyright",
        "/// d",
        "// e",
    ]
    assert set_page(page) == text
    reset(page, {"a0": "//! Added."})
    assert set_page(page) == (
        "#!/usr/bin/env rust-script\n// Copyright\n/// d\n// e\n//! Added.\nfn f() {}\n"
    )


#: Comment sections of different written forms in one place, as
#: `(text, cue, kind, raw_lines)`.
RUST_JOINED = {
    "detached behind ordinary": (
        "fn g() {}\n\n/// Detached.\n// ordinary\nfn f() {}\n",
        "b1",
        "comment",
        ["/// Detached.", "// ordinary"],
    ),
    "doc block behind ordinary": (
        "/** Doc. */\n// c\nfn f() {}",
        "f0",
        "matter",
        ["/** Doc. */", "// c"],
    ),
    "doc split by a FIXME": (
        "/// a\n///\n// FIXME x\n/// b\nfn f() {}",
        "f0",
        "matter",
        ["/// a", "///", "// FIXME x"],
    ),
}


@pytest.mark.parametrize("case", sorted(RUST_JOINED))
def test_rust_page_sections_in_one_place_are_one_paragraph(case):
    from comment_review.results.compositor import set_page

    text, place, kind, raw = RUST_JOINED[case]
    page = build(text, "m.rs")
    joined = by_cue(page)[place]
    assert joined.kind == kind
    assert joined.raw_lines == raw
    addresses = [b.address for b in page.paragraphs if b.address]
    assert len(addresses) == len(set(addresses))
    assert set_page(page) == text


def test_rust_page_doc_split_by_a_fixme_keeps_the_last_run_as_the_item_doc():
    page = build(RUST_JOINED["doc split by a FIXME"][0], "m.rs")
    places = _places(page)
    assert places["a1"] == ("docstring", "fn f() {}")
    assert by_cue(page)["a1"].raw_lines == ["/// b"]


def test_rust_page_reworded_joined_paragraph_sets_in_place():
    from comment_review.results.compositor import set_page
    from comment_review.results.galley import reset

    text = RUST_JOINED["detached behind ordinary"][0]
    page = build(text, "m.rs")
    reset(page, {"b1": "/// Reworded.\n// still ordinary"})
    assert set_page(page) == (
        "fn g() {}\n\n/// Reworded.\n// still ordinary\nfn f() {}\n"
    )


#: The file-head rule, as `(text, cue -> raw lines)`: the comments from line
#: 1, or from the line below the shebang, up to the first blank line are the
#: file's matter whatever their forms; what follows the blank is a comment.
RUST_OPENING = {
    "ordinary run across a blank": (
        "// Copyright\n\n// note on f\nfn f() {}\n",
        {"f0": ["// Copyright"], "b0": ["// note on f"]},
    ),
    "two blanks": (
        "// a\n// b\n\n// c\n\n// d\nfn f() {}\n",
        {"f0": ["// a", "// b"], "b0": ["// c", "", "// d"]},
    ),
    "shebang then a run across a blank": (
        "#!/usr/bin/env rust-script\n// Copyright\n\n// note\nfn f() {}\n",
        {"f0": ["#!/usr/bin/env rust-script", "// Copyright"], "b0": ["// note"]},
    ),
    "two forms then a blank": (
        "// a\n/* b */\n\n// c\nfn f() {}\n",
        {"f0": ["// a", "/* b */"], "b0": ["// c"]},
    ),
    "codeless, a blank between": (
        "// a\n\n// b\n",
        {"f0": ["// a"], "f1": ["// b"]},
    ),
}


@pytest.mark.parametrize("case", sorted(RUST_OPENING))
def test_rust_page_opening_comments_follow_one_rule_whatever_their_forms(case):
    from comment_review.results.compositor import set_page

    text, expected = RUST_OPENING[case]
    page = build(text, "m.rs")
    held = {cue(b): b.raw_lines for b in page.paragraphs if b.address and b.raw_text}
    assert held == expected
    assert set_page(page) == text


def test_rust_page_added_module_doc_is_set_below_the_opening_matter():
    from comment_review.results.compositor import set_page
    from comment_review.results.galley import reset

    page = build("// Copyright\n\n// note on f\nfn f() {}\n", "m.rs")
    reset(page, {"a0": "//! Added."})
    assert set_page(page) == "// Copyright\n\n//! Added.\n// note on f\nfn f() {}\n"


@pytest.mark.parametrize(
    "text",
    [
        "// Copyright\n//! m\nfn f() {}\n",
        "#!/usr/bin/env rust-script\n// Copyright\n//! m\nfn f() {}\n",
    ],
    ids=["plain", "shebang"],
)
def test_rust_page_module_doc_behind_front_matter_is_attached(text):
    from comment_review.results.compositor import set_page

    page = build(text, "m.rs")
    places = by_cue(page)
    assert places["f0"].kind == "matter"
    assert places["f0"].raw_lines[-1] == "// Copyright"
    assert (places["a0"].kind, places["a0"].raw_lines) == ("docstring", ["//! m"])
    assert set_page(page) == text


def test_rust_page_module_doc_behind_a_trailing_comment_is_detached():
    from comment_review.results.compositor import set_page

    text = "#![allow(x)] // c\n//! m\nfn f() {}\n"
    page = build(text, "m.rs")
    places = by_cue(page)
    assert (places["c0"].kind, places["c0"].raw_lines) == (
        "trailing-comment",
        [" // c"],
    )
    assert (places["b1"].kind, places["b1"].raw_lines) == ("comment", ["//! m"])
    assert places["a0"].kind == "undocumented"
    assert set_page(page) == text


@pytest.mark.parametrize(
    "text",
    [
        RUST_ITEMS,
        *(case[0] for case in RUST_JOINED.values()),
        "#!/usr/bin/env rust-script\n// Copyright\n/// d\n// e\nfn f() {}\n",
        "// c\n/// d\n// e\nfn f() {}\n",
        "fn f() {} // t\n// a\n/* b */\n//! c\n/// d\n",
        "fn f() {\n    // a\n    /// b\n    let x = 1; // c\n    /* d */\n}\n",
        "fn f() {\n    // a\n    //! inner\n}\n",
        "fn f() {\n    // a\n    //! inner\n    // b\n    let x = 1;\n}\n",
        "fn f() {\n    /* a */\n    //! inner\n    /* b */\n    let x = 1;\n}\n",
        "fn f() { //! same line\n}\n",
        "fn f() {\n    //! first\n    // after\n    let x = 1;\n}\n",
        "fn f() {}\n/// a\n// b\n",
        "fn f() {}\n// a\n\n// b\n/// c\n",
        "\n// a\n//! m\n// c\nfn f() {}\n",
        "#![allow(x)]\n// a\n//! m\n/* c */\nfn f() {}\n",
        "#![allow(x)] // c\n//! m\nfn f() {}\n",
        "/// d\n//! m\nfn f() {}\n",
        "// Copyright\n//! m\n// c\nfn f() {}\n",
        "// a\n// b\n\n// c\n\n// d\nfn f() {}\n",
        "//! a\n#![allow(x)]\n//! b\n\n//! c\n",
        # A module doc with an inner attribute before it.
        "#![no_std]\n//! Docs.\nfn f() {}\n",
        "#![no_std]\n//! Docs.\n\n/// F.\nfn f() {}\n",
        # A module doc behind a comment below the opening matter.
        "// Copyright\n\n// note\n\n//! Docs.\n\nfn f() {}\n",
        "// Copyright\n\n// note\n//! Docs.\nfn f() {}\n",
        # A blank or whitespace-only line inside a literal.
        'fn f() {\n    let s = "a\n\nb";\n}\n',
        'fn f() {\n    let s = "a\n\nb"; // c\n}\n',
        'const S: &str = "x\n\ny";\n',
        'fn f() {\n    let s = r"a\n   \nb";\n}\n',
        # Comments sharing a line.
        "/// a\n\n/// b\n// c\nfn f() {}\n",
        "fn f() {}\n/** a */ // b\nfn g() {}\n",
        "fn f() {}\n/** a */ /* b */\nfn g() {}\n",
        "fn f() {}\n/* a */ // b\nfn g() {}\n",
        "fn f() {} /** a */ // b\nfn g() {}\n",
        "/* c */ /** d */\nfn g() {}\n",
        "fn f() {} /* a\n b */ /* c */\nfn g() {}\n",
        "/** a */ /*! b */ /* c */\nfn f() {}\n",
        # An inner doc with a comment after it on its line.
        "/*! a */ /* b */\nfn f() {}\n",
        "fn f() {\n    /*! a */ /* b */\n    let x = 1;\n}\n",
        "mod m {\n    /*! a */ /* b */\n    fn g() {}\n}\n",
        "fn f() {}\n/*! a */ /** b */\nfn g() {}\n",
        "/*! a */ /** b */\nfn f() {}\n",
        "#![no_std]\n/*! a */ // b\nfn f() {}\n",
    ],
)
def test_rust_page_no_two_paragraphs_share_a_place(text):
    from comment_review.results.compositor import set_page

    page = build(text, "m.rs")
    addresses = [b.address for b in page.paragraphs if b.address]
    assert len(addresses) == len(set(addresses))
    assert set_page(page) == text


def test_rust_page_module_doc_after_an_inner_attribute_is_detached():
    from comment_review.results.compositor import set_page

    text = "#![no_std]\n//! Docs.\nfn f() {}\n"
    page = build(text, "m.rs")
    places = by_cue(page)
    assert places["a0"].kind == "undocumented"
    assert (places["b1"].kind, places["b1"].raw_lines) == ("comment", ["//! Docs."])
    assert set_page(page) == text


def test_rust_page_module_doc_behind_a_comment_below_the_opening_matter_is_detached():
    from comment_review.results.compositor import set_page

    text = "// Copyright\n\n// note\n\n//! Docs.\n\nfn f() {}\n"
    page = build(text, "m.rs")
    places = by_cue(page)
    assert (places["f0"].kind, places["f0"].raw_lines) == ("matter", ["// Copyright"])
    assert places["a0"].kind == "undocumented"
    assert (places["b0"].kind, places["b0"].raw_lines) == (
        "comment",
        ["// note", "", "//! Docs."],
    )
    assert set_page(page) == text


@pytest.mark.parametrize(
    "text",
    [
        "#![no_std]\n//! Docs.\n\n/// F.\nfn f() {}\n",
        "// Copyright\n\n// note\n\n//! Docs.\n\n/// F.\nfn f() {}\n",
    ],
    ids=["after-inner-attribute", "below-the-opening-matter"],
)
def test_rust_page_prose_edit_elsewhere_leaves_a_detached_module_doc_in_place(text):
    from comment_review.reading.readers import read_source
    from comment_review.reading.rust.records import RustRead
    from comment_review.results.compositor import set_page
    from comment_review.results.galley import reset

    page = build(text, "m.rs")
    reset(page, {"a1": "/// Reworded."})
    out = set_page(page)
    assert out == text.replace("/// F.", "/// Reworded.")
    before = read_source(Path("m.rs"), text)
    after = read_source(Path("m.rs"), out)
    assert isinstance(before, RustRead) and isinstance(after, RustRead)
    assert before.preserved(after).unchanged


def test_rust_page_doc_sharing_its_line_with_a_comment_is_a_comment():
    from comment_review.results.compositor import set_page
    from comment_review.results.galley import reset

    text = "fn f() {}\n/** a */ // b\nfn g() {}\n"
    page = build(text, "m.rs")
    places = by_cue(page)
    assert (places["b1"].kind, places["b1"].raw_lines) == ("comment", ["/** a */ // b"])
    assert places["b1"].text == "a b"
    assert places["a2"].kind == "undocumented"
    assert set_page(page) == text
    reset(page, {"a2": "/// Added."})
    out = set_page(page)
    assert out == "fn f() {}\n/** a */ // b\n/// Added.\nfn g() {}\n"


@pytest.mark.parametrize(
    ("text", "place", "kind", "raw", "owner"),
    [
        ("/*! a */ /* b */\nfn f() {}\n", "f0", "matter", ["/*! a */ /* b */"], "a0"),
        (
            "fn f() {\n    /*! a */ /* b */\n    let x = 1;\n}\n",
            "b1",
            "comment",
            ["    /*! a */ /* b */"],
            "a1",
        ),
        (
            "mod m {\n    /*! a */ /* b */\n    fn g() {}\n}\n",
            "b1",
            "comment",
            ["    /*! a */ /* b */"],
            "a1",
        ),
        (
            "fn f() {}\n/*! a */ /** b */\nfn g() {}\n",
            "b1",
            "comment",
            ["/*! a */ /** b */"],
            "a2",
        ),
    ],
    ids=["file-head", "fn-body", "mod-body", "inner-then-outer-above-an-item"],
)
def test_rust_page_inner_doc_with_a_comment_after_it_is_detached(
    text, place, kind, raw, owner
):
    from comment_review.results.compositor import set_page

    page = build(text, "m.rs")
    places = by_cue(page)
    assert (places[place].kind, places[place].raw_lines) == (kind, raw)
    assert places[place].text == "a b"
    assert places[owner].kind == "undocumented"
    assert set_page(page) == text


def test_rust_page_doc_trailing_code_with_a_comment_after_it_is_one_trailing():
    from comment_review.results.compositor import set_page

    text = "fn f() {} /** a */ // b\nfn g() {}\n"
    page = build(text, "m.rs")
    places = by_cue(page)
    assert (places["c0"].kind, places["c0"].raw_lines) == (
        "trailing-comment",
        [" /** a */ // b"],
    )
    assert places["c0"].anchor == "fn f() {}"
    assert places["c0"].text == "a b"
    assert set_page(page) == text


RUST_SHEBANG = "#!/usr/bin/env rust-script\nfn main() {}\n"


def test_rust_page_shebang_keeps_its_f_placement_and_round_trips():
    from comment_review.results.compositor import set_page

    page = build(RUST_SHEBANG, "m.rs")
    shebang = next(b for b in page.paragraphs if cue(b) == "f0")
    assert shebang.kind == "matter"
    assert shebang.raw_lines == ["#!/usr/bin/env rust-script"]
    assert set_page(page) == RUST_SHEBANG


def test_rust_page_added_module_doc_is_set_after_the_shebang():
    from comment_review.results.compositor import set_page
    from comment_review.results.galley import reset

    page = build(RUST_SHEBANG, "m.rs")
    reset(page, {"a0": "//! Added."})
    assert set_page(page) == ("#!/usr/bin/env rust-script\n//! Added.\nfn main() {}\n")


@pytest.mark.parametrize("name", ["m.py", "m.lua", "m.rs"])
def test_codeless_matter_below_line_one_is_back_matter(name):
    from comment_review.results.compositor import set_page

    marker = {"m.py": "#", "m.lua": "--", "m.rs": "//"}[name]
    text = f"\n\n{marker} x\n"
    page = build(text, name)
    matter = next(b for b in page.paragraphs if b.kind == "matter")
    assert cue(matter) == "f1"
    assert set_page(page) == text


RUST_SHAPES = (
    "mod shapes {\n"
    "    //! Shapes on the board.\n"
    "\n"
    "    fn area() -> i32 {\n"
    "        4\n"
    "    }\n"
    "}\n"
)

#: An inner doc inside a body, as `(text, its b place, that place's raw lines)`.
#: Each is an ordinary comment in the gap it sits in.
RUST_INNER_DOCS = {
    "mod": (RUST_SHAPES, "b1", ["    //! Shapes on the board."]),
    "fn": ("fn f() {\n    //! inner\n}\n", "b1", ["    //! inner"]),
    "impl": ("impl S {\n    //! inner\n    fn g() {}\n}\n", "b1", ["    //! inner"]),
    "after an inner attribute": (
        "mod m {\n    #![allow(x)]\n    //! late\n    fn f() {}\n}\n",
        "b2",
        ["    //! late"],
    ),
}


@pytest.mark.parametrize("kind", sorted(RUST_INNER_DOCS))
def test_rust_page_inner_doc_in_a_body_is_detached_at_its_b_place(kind):
    from comment_review.results.compositor import set_page

    text, place, raw = RUST_INNER_DOCS[kind]
    page = build(text, "m.rs")
    places = by_cue(page)
    assert (places[place].kind, places[place].raw_lines) == ("comment", raw)
    assert places["a1"].kind == "undocumented"
    assert set_page(page) == text


def test_rust_page_added_doc_on_a_module_with_a_body_inner_doc_is_set_above_it():
    from comment_review.results.compositor import set_page
    from comment_review.results.galley import reset

    page = build(RUST_SHAPES, "m.rs")
    reset(page, {"a1": "/// Added."})
    out = set_page(page)
    assert out == "/// Added.\n" + RUST_SHAPES


#: An inner doc that is not first in its body, or shares its head's line, is
#: detached: `(text, the detached paragraph's cue and kind, its raw lines)`.
RUST_INNER_DETACHED = {
    "behind a comment": (
        "fn f() {\n    // a\n    //! inner\n}\n",
        ("b1", "comment"),
        ["    // a", "    //! inner"],
    ),
    "between comments": (
        "fn f() {\n    // a\n    //! inner\n    // b\n    let x = 1;\n}\n",
        ("b1", "comment"),
        ["    // a", "    //! inner", "    // b"],
    ),
    "between delimited comments": (
        "fn f() {\n    /* a */\n    //! inner\n    /* b */\n    let x = 1;\n}\n",
        ("b1", "comment"),
        ["    /* a */", "    //! inner", "    /* b */"],
    ),
    "on the head's line": (
        "fn f() { //! same line\n}\n",
        ("c0", "trailing-comment"),
        [" //! same line"],
    ),
}


@pytest.mark.parametrize("case", sorted(RUST_INNER_DETACHED))
def test_rust_page_inner_doc_not_first_in_its_body_is_detached(case):
    from comment_review.results.compositor import set_page

    text, (place, kind), raw = RUST_INNER_DETACHED[case]
    page = build(text, "m.rs")
    detached = by_cue(page)[place]
    assert (detached.kind, detached.raw_lines) == (kind, raw)
    assert _places(page)["a1"][0] == "undocumented"
    addresses = [b.address for b in page.paragraphs if b.address]
    assert len(addresses) == len(set(addresses))
    assert set_page(page) == text


def test_rust_page_inner_doc_first_in_its_body_shares_the_gap_with_a_comment():
    from comment_review.results.compositor import set_page

    text = "fn f() {\n    //! first\n    // after\n    let x = 1;\n}\n"
    page = build(text, "m.rs")
    places = by_cue(page)
    assert places["a1"].kind == "undocumented"
    assert (places["b1"].kind, places["b1"].raw_lines) == (
        "comment",
        ["    //! first", "    // after"],
    )
    assert set_page(page) == text


#: The comments after the last code line, as `(text, cue -> raw lines)`: the
#: run after the last blank line is back matter, whatever its forms, and the
#: comments before that blank are the closing gap's one paragraph.
RUST_CLOSING = {
    "two ordinary forms": (
        "fn f() {}\n/* a */\n// b\n",
        {"f1": ["/* a */", "// b"]},
    ),
    "doc then ordinary": (
        "fn f() {}\n/// a\n// b\n",
        {"f1": ["/// a", "// b"]},
    ),
    "ordinary, blank, doc": (
        "fn f() {}\n// a\n\n/// b\n",
        {"b1": ["// a"], "f1": ["/// b"]},
    ),
    "doc, blank, ordinary": (
        "fn f() {}\n/// a\n\n// b\n",
        {"b1": ["/// a"], "f1": ["// b"]},
    ),
    "one form across the last blank": (
        "fn f() {}\n// a\n\n// b\n/// c\n",
        {"b1": ["// a"], "f1": ["// b", "/// c"]},
    ),
    "two forms before the last blank": (
        "fn f() {}\n/// a\n// b\n\n// c\n",
        {"b1": ["/// a", "// b"], "f1": ["// c"]},
    ),
}


@pytest.mark.parametrize("case", sorted(RUST_CLOSING))
def test_rust_page_closing_comments_follow_one_rule_whatever_their_forms(case):
    from comment_review.results.compositor import set_page

    text, expected = RUST_CLOSING[case]
    page = build(text, "m.rs")
    held = {cue(b): b.raw_lines for b in page.paragraphs if b.address and b.raw_text}
    assert held == expected
    assert set_page(page) == text


def test_rust_page_module_doc_behind_a_comment_that_is_not_matter_is_detached():
    """A `//!` behind an ordinary comment that is not front matter is
    detached, so the three comments in the gap are one paragraph."""
    from comment_review.results.compositor import set_page

    text = "\n// a\n//! m\n// c\nfn f() {}\n"
    page = build(text, "m.rs")
    places = by_cue(page)
    assert places["a0"].kind == "undocumented"
    assert (places["b0"].kind, places["b0"].raw_lines) == (
        "comment",
        ["// a", "//! m", "// c"],
    )
    addresses = [b.address for b in page.paragraphs if b.address]
    assert len(addresses) == len(set(addresses))
    assert set_page(page) == text


def test_rust_fixture_licence_header_is_front_matter_and_first_item_undocumented():
    fixture = Path(__file__).parent / "fixtures" / "licensed.rs"
    text = fixture.read_bytes().decode("utf-8")
    places = _places(build(text, "licensed.rs"))
    assert places["f0"][0] == "matter"
    assert places["a1"] == ("undocumented", "pub fn first() -> u32 {")
    assert places["a2"][0] == "docstring"


@pytest.mark.parametrize(
    ("name", "text", "places"),
    [
        (
            "m.js",
            "// licence\n/** Doc. */\n",
            {"f0": ["// licence"], "a0": ["/** Doc. */"]},
        ),
        (
            "m.js",
            "// licence\n/** Doc. */\nlet x = 1;\n",
            {"f0": ["// licence"], "a0": ["/** Doc. */"]},
        ),
        (
            "m.js",
            "#!/usr/bin/env node\n// licence\n/** Doc. */\nlet x = 1;\n",
            {"f0": ["#!/usr/bin/env node", "// licence"], "a0": ["/** Doc. */"]},
        ),
        (
            "m.py",
            '# licence\n"""Doc."""\nx = 1\n',
            {"f0": ["# licence"], "a0": ['"""Doc."""']},
        ),
    ],
    ids=["no-code", "code", "shebang", "python"],
)
def test_matter_then_a_doc_at_the_head_are_placed_at_f0_and_a0(name, text, places):
    found = by_cue(build(text, name))
    assert {place: found[place].raw_lines for place in places} == places
