"""Python proof uses acquired lexical records and preserves exact retained source."""

import ast
import builtins
import sys
import tokenize
import unicodedata
from dataclasses import replace
from pathlib import Path

import pytest
from conftest import build, by_cue, docket_from
from test_proof_command import proof_repository

from comment_review.binder import page as page_model
from comment_review.binder.binder import bind
from comment_review.flows import (
    page_for,
    proof_setter,
    prove_unchanged,
    reading_context,
)
from comment_review.machine.digests import sha256_hex
from comment_review.machine.repo import Source, sha_of
from comment_review.reading import readers
from comment_review.reading.context import ReadingContext, resolve_context
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure

MODERN_SOURCE = (
    "# Describe the envelope.\n"
    "type Envelope[T] = tuple[T, ...]\n"
    "def unpack[T](entry: T) -> T:\n"
    '    """Return the entry."""\n'
    '    label = f"{entry["tag"]}"\n'
    "    return entry\n"
)


def forbid_host_parsers(patch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Python proof invoked a host parser")

    for owner, names in (
        (ast, ("parse", "literal_eval", "dump")),
        (tokenize, ("tokenize", "generate_tokens")),
        (builtins, ("compile", "eval")),
    ):
        for name in names:
            patch.setattr(owner, name, forbidden)


def test_modern_python_read_and_proof_do_not_use_host_parsers(monkeypatch):
    after = MODERN_SOURCE.replace("Describe the envelope.", "Explain this envelope.")
    after = after.replace("Return the entry.", "Expose the enclosed entry.")
    with monkeypatch.context() as patch:
        forbid_host_parsers(patch)
        refusal = proof_setter._prove("m.py", MODERN_SOURCE, after, Path("m.py"))
    assert refusal is None


def test_admitted_proof_never_reacquires_python_records(monkeypatch):
    before = build(MODERN_SOURCE)
    after = build(MODERN_SOURCE.replace("Return the entry.", "Return its contents."))

    def forbidden(*args, **kwargs):
        raise AssertionError("Comparison reacquired an admitted Python read")

    with monkeypatch.context() as patch:
        forbid_host_parsers(patch)
        patch.setattr(proof_setter, "page_of", forbidden)
        patch.setattr(page_model, "read_source", forbidden)
        refusal = proof_setter._prove("m.py", before, after, Path("m.py"))
    assert refusal is None


def test_missing_python_records_refuse_without_host_fallback(monkeypatch):
    page = replace(build("value = 1\n"), python_read=None)
    with monkeypatch.context() as patch:
        forbid_host_parsers(patch)
        refusal = proof_setter._prove("m.py", page, page, Path("m.py"))
    assert refusal is not None and refusal.step == "prove"


@pytest.mark.parametrize(
    "before,after",
    [
        ("first = 1\nsecond = 2\n", "second = 2\nfirst = 1\n"),
        ("value = left + right\n", "value = left - right\n"),
        ('value = "sample"\n', "value = 'sample'\n"),
        ('value = """one\n\ntwo"""\n', 'value = """one\ntwo"""\n'),
        ('value = """one  \ntwo"""\n', 'value = """one\ntwo"""\n'),
        ("if ready:\n    emit()\n", "if ready:\n  emit()\n"),
        ("first(); second()\n", "first()\nsecond()\n"),
        ("value = 1  # type: ignore\n", "value = 1  # type: ignore[name]\n"),
        ("first()  # type: ignore\nsecond()\n", "first()\nsecond()  # type: ignore\n"),
    ],
    ids=[
        "order",
        "operator",
        "literal-spelling",
        "literal-blank",
        "literal-spaces",
        "indentation",
        "separator",
        "directive",
        "attachment",
    ],
)
def test_both_python_proof_gates_refuse_retained_source_mutations(
    tmp_path, before, after
):
    refusal = proof_setter._prove("m.py", before, after, Path("m.py"))
    assert refusal is not None and refusal.step == "prove"
    repo, target = proof_repository(tmp_path, before.replace("\n", "\r\n"), ".py")
    target.write_bytes(after.replace("\n", "\r\n").encode())
    report = prove_unchanged.run(repo, "HEAD", [target])
    assert report.failures == 1
    assert "PROVEN" not in " ".join(report.messages)


@pytest.mark.parametrize("owner", ["a0", "a1"])
@pytest.mark.parametrize("adding", [True, False], ids=["add", "drop"])
def test_standalone_and_approved_proof_allow_documentation_presence_changes(
    tmp_path, monkeypatch, owner, adding
):
    absent = "def carry[T](entry: T):\n    return entry\n"
    present = (
        '"""Carry an entry."""\n' + absent
        if owner == "a0"
        else absent.replace("    return", '    """Carry an entry."""\n    return')
    )
    before, after = (absent, present) if adding else (present, absent)
    was, now = build(before), build(after)
    assert proof_setter._prove("m.py", was, now, Path("m.py")) is not None
    repo, target = proof_repository(tmp_path, before.replace("\n", "\r\n"), ".py")
    target.write_bytes(after.replace("\n", "\r\n").encode())
    with monkeypatch.context() as patch:
        forbid_host_parsers(patch)
        refusal = proof_setter._prove(
            "m.py", was, now, Path("m.py"), [(by_cue(was)[owner], by_cue(now)[owner])]
        )
        report = prove_unchanged.run(repo, "HEAD", [target])
    assert refusal is None
    assert report.failures == 0, report.messages
    assert any("PROVEN" in message for message in report.messages)


@pytest.mark.parametrize("owner", ["a0", "a1"])
@pytest.mark.parametrize("mutation", [None, "changed", "removed"])
def test_both_gates_preserve_promoted_ordinary_literal(
    tmp_path, monkeypatch, owner, mutation
):
    indent = "" if owner == "a0" else "    "
    prefix = "" if owner == "a0" else "def carry():\n"
    documentation = indent + '"""Describe carrying."""\n'
    literal = indent + '"ordinary retained literal"\n'
    ending = "value = 3\n" if owner == "a0" else "    return 3\n"
    before = prefix + documentation + literal + ending
    after = prefix + literal + ending
    if mutation == "changed":
        after = after.replace("ordinary retained literal", "changed literal")
    elif mutation == "removed":
        after = after.replace(literal, "")
    was, now = build(before), build(after)
    repo, target = proof_repository(tmp_path, before.replace("\n", "\r\n"), ".py")
    target.write_bytes(after.replace("\n", "\r\n").encode())
    with monkeypatch.context() as patch:
        forbid_host_parsers(patch)
        refusal = proof_setter._prove(
            "m.py", was, now, Path("m.py"), [(by_cue(was)[owner], by_cue(now)[owner])]
        )
        report = prove_unchanged.run(repo, "HEAD", [target])
    if mutation is None:
        assert refusal is None
        assert report.failures == 0, report.messages
        assert any("PROVEN" in message for message in report.messages)
    else:
        assert refusal is not None and refusal.step == "prove"
        assert report.failures == 1
        assert "PROVEN" not in " ".join(report.messages)


@pytest.mark.parametrize(
    "forgery", ["position", "anchor", "owner", "missing", "ambiguous"]
)
def test_selected_owner_requires_unique_retained_correspondence(forgery):
    text = "def carry():\n    return 1\ndef carry():\n    return 1\n"
    was, now = build(text), build(text)
    original, current = by_cue(was)["a1"], by_cue(now)["a1"]
    if forgery == "position":
        assert current.anchor_line is not None
        current = replace(current, anchor_line=current.anchor_line + 1)
    elif forgery == "anchor":
        current = replace(current, anchor="def counterfeit():")
    elif forgery == "owner":
        current = by_cue(now)["a2"]
    elif forgery == "missing":
        current = replace(current, anchor_line=None)
    else:
        read = now.python_read
        assert read is not None
        declaration = read.source.declarations[0]
        source = replace(read.source, declarations=(declaration, declaration))
        now = replace(now, python_read=replace(read, source=source))
    refusal = proof_setter._prove("m.py", was, now, Path("m.py"), [(original, current)])
    assert refusal is not None and "identified" in refusal.why


def test_mutated_approved_places_cannot_select_a_different_retained_owner():
    text = "def carry():\n    return 1\ndef carry():\n    return 1\n"
    was, now = build(text), build(text)
    original, current = by_cue(was)["a1"], by_cue(now)["a1"]
    original.anchor_line = by_cue(was)["a2"].anchor_line
    current.anchor_line = by_cue(now)["a2"].anchor_line
    refusal = proof_setter._prove("m.py", was, now, Path("m.py"), [(original, current)])
    assert refusal is not None and "identified" in refusal.why


@pytest.mark.parametrize("adding", [True, False], ids=["add", "drop"])
@pytest.mark.parametrize("owner", ["a0", "a1"])
def test_real_python_draft_proves_selected_presence_without_host_parsing(
    tmp_path, monkeypatch, adding, owner
):
    absent = "def carry[T](entry: T):\n    return entry\n"
    documentation = '"""Carry the envelope."""'
    if owner == "a0":
        present = documentation + "\n" + absent
    else:
        documentation = "    " + documentation
        present = absent.replace("    return", documentation + "\n    return")
    before, after = (absent, present) if adding else (present, absent)
    repo = tmp_path / "repo"
    repo.mkdir()
    path = repo / "m.py"
    path.write_bytes(before.encode())
    page = page_for.page_of(path, rel="m.py")
    assert not isinstance(page, ReadFailure)
    binder = bind([page], read_from={"root": str(repo), "revise": 0})
    docket = docket_from({f"m.py@{owner}": documentation if adding else None}, binder)
    admitted = []
    actual = proof_setter.page_of

    def observe(*args, **kwargs):
        admitted.append(kwargs["reading_context"])
        return actual(*args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(proof_setter, "page_of", observe)
        forbid_host_parsers(patch)
        drafted, refused = proof_setter.run(docket, repo, tmp_path / "out")
    assert refused == [] and len(drafted) == 1
    assert drafted[0].draft.read_bytes() == after.encode()
    assert admitted == [docket.schedules[0].reading, docket.schedules[0].reading]
    assert admitted[0] is admitted[1]


def test_standalone_modern_python_uses_one_context_without_host_parsing(
    tmp_path, monkeypatch
):
    before = MODERN_SOURCE.replace("\n", "\r\n")
    repo, target = proof_repository(tmp_path, before, ".py")
    target.write_bytes(
        before.replace("Return the entry.", "Expose the entry.").encode()
    )
    admitted = []
    actual = prove_unchanged.page_of

    def observe(*args, **kwargs):
        admitted.append(kwargs["reading_context"])
        return actual(*args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(prove_unchanged, "page_of", observe)
        forbid_host_parsers(patch)
        report = prove_unchanged.run(repo, "HEAD", [target])
    assert report.failures == 0, report.messages
    assert len(admitted) == 2 and admitted[0] is admitted[1]
    assert report.reading_contexts[target] is admitted[0]


def test_python_unicode_database_change_invalidates_saved_context_only(monkeypatch):
    python = reading_context.context_for(Path("m.py"), {})
    javascript = reading_context.context_for(Path("m.js"), {})
    assert isinstance(python, ReadingContext)
    assert isinstance(javascript, ReadingContext)
    monkeypatch.setattr(unicodedata, "unidata_version", "99.0.0")
    changed = reading_context.context_for(Path("m.py"), {})
    assert isinstance(changed, ReadingContext) and changed != python
    assert reading_context.context_for(Path("m.js"), {}) == javascript
    failed = page_for.page_of(
        Path("m.py"), source=Source("value = 1\n", "sha"), reading_context=python
    )
    assert isinstance(failed, ReadFailure)
    assert failed.diagnostics[0].code == "reading-context-mismatch"


def test_python_context_identity_is_independent_of_host_parser_version(monkeypatch):
    before = reading_context.context_for(Path("m.py"), {})
    monkeypatch.setattr(sys, "version_info", (3, 99, 0, "final", 0))
    after = reading_context.context_for(Path("m.py"), {})
    assert isinstance(before, ReadingContext) and after == before


def test_previous_python_binding_context_refuses_before_reading(monkeypatch):
    registry = reading_context.installed_registry()
    assert not isinstance(registry, ReadFailure)
    selected = readers.reader_for(Path("m.py"), registry)
    assert isinstance(selected, tuple)
    definition, _ = selected
    assert isinstance(definition, LanguageDefinition)
    old = resolve_context(
        definition,
        {},
        reader_revision="1",
        placement_revision="1",
        grammar_identity="Python 3.15 lexical",
        digest=sha256_hex,
    )
    assert isinstance(old, ReadingContext)

    def forbidden(*args, **kwargs):
        raise AssertionError("Incompatible context reached source recognition")

    monkeypatch.setattr(page_model, "read_source", forbidden)
    text = "value = 1\n"
    failed = page_for.page_of(
        Path("m.py"), source=Source(text, sha_of(text)), reading_context=old
    )
    assert isinstance(failed, ReadFailure)
    assert failed.diagnostics[0].code == "reading-context-mismatch"
