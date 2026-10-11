from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
from inspect import signature
from pathlib import Path
from typing import Any

import pytest

from comment_review.flows import reading_context as flow_context
from comment_review.flows.compositor import round_trip
from comment_review.flows.gather import gather
from comment_review.reading import context as context_module
from comment_review.reading.context import ReadingContext, compatible_contexts
from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.registry import LanguageRegistry


@pytest.mark.parametrize(
    "fault", ["compatible", "digest", "settings", "malformed", "duplicate"]
)
def test_direct_copy_metadata_is_admitted_without_trusting_annotations(fault):
    from comment_review.desk.proof.edit_copy import EditCopy
    from comment_review.desk.proof.sheet import Sheet

    saved = flow_context.context_for(Path("m.py"), {})
    assert isinstance(saved, ReadingContext)
    if fault == "digest":
        saved = replace(saved, compatibility="0" * 64)
    elif fault == "settings":
        saved = replace(saved, settings=(("unknown", "on"),))
    elif fault == "duplicate":
        object.__setattr__(saved, "settings", (("a", "on"), ("a", "off")))
    sheet = Sheet("m.py", "unchanged-sha", (), saved)
    if fault == "malformed":
        object.__setattr__(sheet, "reading", [])
    copy = EditCopy("block-context", {"root": ".", "revise": 0}, (sheet,))
    before = repr(copy)
    problems = flow_context.copy_reading_problems(copy)
    if fault == "compatible":
        assert problems == []
    else:
        assert problems and "regather" in " ".join(problems)
        assert "block-context" in " ".join(problems)
    assert repr(copy) == before


def test_direct_context_duplicate_supported_settings_cannot_collapse(monkeypatch):
    from types import SimpleNamespace

    from comment_review.desk.proof.edit_copy import EditCopy
    from comment_review.desk.proof.sheet import Sheet

    binding = SimpleNamespace(revision="reader-1", grammar_identity="grammar-1")
    monkeypatch.setattr(flow_context, "reader_for", lambda _: (definition(), binding))
    saved = flow_context.context_for(Path("m.ix"), {"mode": "wide"})
    assert isinstance(saved, ReadingContext)
    object.__setattr__(saved, "settings", (("mode", ""), ("mode", "wide")))
    copy = EditCopy(
        "block-context", {"root": ".", "revise": 0}, (Sheet("m.ix", "sha", (), saved),)
    )
    before = repr(copy)
    assert "regather" in " ".join(flow_context.copy_reading_problems(copy))
    assert repr(copy) == before


def test_direct_proof_saved_context_is_admitted_against_installed_identity():
    from comment_review.desk.proof.master_proof import MasterProof

    saved = flow_context.context_for(Path("m.py"), {})
    assert isinstance(saved, ReadingContext)
    proof = MasterProof("4c", {}, (), {"m.py": saved}, page_shas={"m.py": "sha"})
    assert flow_context.proof_reading_problems(proof) == []
    proof.page_readings["m.py"] = replace(saved, compatibility="0" * 64)
    assert "regather" in " ".join(flow_context.proof_reading_problems(proof))


@pytest.mark.parametrize(
    "path, sha",
    [("m.py", None), ("m.py", ""), ("m.py", " "), ("m.py", 3), ("", "sha"), (7, "sha")],
)
def test_direct_extra_page_proof_refuses_invalid_sha_metadata(path, sha):
    from comment_review.desk.proof.master_proof import MasterProof

    saved = flow_context.context_for(Path("m.py"), {})
    assert isinstance(saved, ReadingContext)
    proof = MasterProof("4c", {}, (), {"m.py": saved}, page_shas={path: sha})
    problems = flow_context.proof_reading_problems(proof)
    assert any("page_shas" in reason and "regather" in reason for reason in problems)


def test_direct_proof_malformed_settings_returns_refusal_before_conversion():
    from comment_review.desk.proof.master_proof import MasterProof

    saved = flow_context.context_for(Path("m.py"), {})
    assert isinstance(saved, ReadingContext)
    object.__setattr__(saved, "settings", (("x",),))
    proof = MasterProof("4c", {}, (), {"m.py": saved}, page_shas={"m.py": "sha"})
    problems = flow_context.proof_reading_problems(proof)
    assert problems == ["master_proof: m.py: malformed reading context; regather"]


def definition() -> LanguageDefinition:
    return LanguageDefinition(
        "Invented",
        (".ix",),
        "invented-reader",
        "definition-1",
        ("comments",),
        {"mode": ""},
        {"mode": ("", "wide")},
        {"nested": {"tokens": ["\u03bb", True, 1]}},
    )


def resolve(settings):
    return context_module.resolve_context(
        definition(),
        settings,
        reader_revision="reader-1",
        placement_revision="placement-1",
        grammar_identity="grammar-1",
        digest=lambda data: sha256(data).hexdigest(),
    )


def test_resolve_explicit_default_and_independent_override():
    default = resolve({})
    override = resolve({"mode": "wide"})
    assert isinstance(default, ReadingContext)
    assert isinstance(override, ReadingContext)
    assert default.settings == (("mode", ""),)
    assert override.settings == (("mode", "wide"),)
    assert (
        default.compatibility
        == "cefc5dc0563af6a3a811daa0bd6e7babbd224ca9ee1a3150c97e81adfc9be1fa"
    )


@pytest.mark.parametrize(
    "settings",
    [[], {"unknown": "wide"}, {"mode": "bad"}, {"mode": 1}, {1: "wide"}, {"": ""}],
)
def test_resolve_rejects_malformed_or_unsupported_settings(settings):
    assert isinstance(resolve(settings), ReadFailure)


@pytest.mark.parametrize(
    "text",
    [
        "[]",
        "{",
        '{"x.py":{},"x.py":{}}',
        '{"x.py":{"mode":"a","mode":"a"}}',
        '{"/x.py":{}}',
        '{"C:x.py":{}}',
        '{"\\\\\\\\host\\\\x.py":{}}',
        '{"":{}}',
        '{".":{}}',
        '{"../x.py":{}}',
        '{"x.py":[]}',
        '{"x.py":{"mode":1}}',
        '{"x.py":{"":"a"}}',
        '{"x.py":{},"./x.py":{"mode":"a"}}',
    ],
)
def test_settings_json_refuses_bad_shapes_paths_and_duplicates(tmp_path, text):
    settings = tmp_path / "settings.json"
    settings.write_text(text, encoding="utf-8")
    loaded, problems = flow_context.load_settings(settings, tmp_path)
    assert loaded == {}
    assert problems and str(settings) in problems[0]


def test_settings_normalize_without_discovering_source(tmp_path, monkeypatch):
    from comment_review.reading.readers import ReaderBinding

    binding = ReaderBinding(
        "invented-reader",
        "reader-1",
        ("comments",),
        "grammar-1",
        lambda *_: [],
        lambda _: None,
    )
    monkeypatch.setattr(flow_context, "reader_for", lambda _: (definition(), binding))
    settings = tmp_path / "settings.json"
    settings.write_text(
        '{"dir/../x.ix":{"mode":"wide"},"./x.ix":{"mode":"wide"},"other\\\\y.ix":{}}',
        encoding="utf-8",
    )
    loaded, problems = flow_context.load_settings(settings, tmp_path)
    assert problems == []
    assert loaded == {
        tmp_path / "x.ix": {"mode": "wide"},
        tmp_path / "other" / "y.ix": {},
    }
    assert not (tmp_path / "x.ix").exists()


def test_unused_json_entry_is_validated_without_source_acquisition(
    tmp_path, monkeypatch
):
    import importlib

    source = importlib.import_module("comment_review.flows.source")

    def forbidden(_):
        pytest.fail("settings loader acquired source")

    monkeypatch.setattr(source, "source_of", forbidden)
    settings = tmp_path / "settings.json"
    settings.write_text('{"missing.py":{"invented":"yes"}}', encoding="utf-8")
    loaded, problems = flow_context.load_settings(settings, tmp_path)
    assert loaded == {}
    assert problems and "missing.py" in problems[0] and "unknown setting" in problems[0]
    settings.write_text('{"missing.py":{}}', encoding="utf-8")
    assert flow_context.load_settings(settings, tmp_path) == (
        {tmp_path / "missing.py": {}},
        [],
    )
    assert not (tmp_path / "missing.py").exists()


def test_mixed_contexts_derive_independent_installed_binding_metadata(monkeypatch):
    from comment_review.reading.readers import ReaderBinding

    binding = ReaderBinding(
        "invented-reader",
        "reader-1",
        ("comments",),
        "grammar-1",
        lambda *_: [],
        lambda _: None,
    )
    monkeypatch.setattr(flow_context, "reader_for", lambda _: (definition(), binding))
    first = flow_context.context_for(Path("a.ix"), {})
    second = flow_context.context_for(Path("b.ix"), {"mode": "wide"})
    assert isinstance(first, ReadingContext)
    assert isinstance(second, ReadingContext)
    assert first.settings == (("mode", ""),)
    assert second.settings == (("mode", "wide"),)
    assert first.compatibility == second.compatibility
    assert flow_context.reading_problems(
        {Path("a.ix"): first}, {Path("a.ix"): second}
    ) == ["a.ix: reading context differs from saved context"]
    assert flow_context.reading_problems({Path("a.ix"): first}, {}) == [
        "a.ix: current reading context is missing"
    ]


def test_fresh_flows_reject_settings_before_source_acquisition(tmp_path, monkeypatch):
    import importlib

    gather_module = importlib.import_module("comment_review.flows.gather")
    compositor_module = importlib.import_module("comment_review.flows.compositor")
    path = tmp_path / "x.py"
    path.write_text("# prose\n", encoding="utf-8")

    def forbidden(_):
        pytest.fail("source acquired before unsupported setting refusal")

    monkeypatch.setattr(gather_module, "source_of", forbidden)
    monkeypatch.setattr(compositor_module, "source_of", forbidden)
    got = gather(tmp_path, [path], 0, settings={path: {"invented": "yes"}})
    assert got.unreadable and "unknown setting" in got.unreadable[0]
    assert isinstance(round_trip(path, settings={"invented": "yes"}), ReadFailure)


@pytest.mark.parametrize("command", ["gather", "compositor", "prove_unchanged"])
def test_cli_settings_reach_actual_fresh_flow(tmp_path, monkeypatch, capsys, command):
    import importlib
    import sys

    module = importlib.import_module(f"comment_review.commands.{command}")
    path = tmp_path / "x.py"
    path.write_text("# prose\n", encoding="utf-8")
    settings = tmp_path / "settings.json"
    settings.write_text('{"./x.py":{"invented":"yes"}}', encoding="utf-8")
    argv = [
        command,
        str(path),
        "--repo",
        str(tmp_path),
        "--reading-settings",
        str(settings),
    ]
    if command == "prove_unchanged":
        argv += ["--base", "HEAD"]
    monkeypatch.setattr(sys, "argv", argv)
    assert module.main() == 2
    captured = capsys.readouterr()
    assert "unknown setting 'invented'" in captured.out + captured.err
    settings.write_text('{"x.py":{},"x.py":{}}', encoding="utf-8")
    assert module.main() == 2
    captured = capsys.readouterr()
    assert "duplicate raw key" in captured.out + captured.err
    from comment_review.reading.readers import ReaderBinding

    binding = ReaderBinding(
        "invented-reader",
        "reader-1",
        ("comments",),
        "grammar-1",
        lambda *_: [],
        lambda _: None,
    )
    monkeypatch.setattr(flow_context, "reader_for", lambda _: (definition(), binding))
    entry = {"gather": "gather", "compositor": "round_trip", "prove_unchanged": "run"}[
        command
    ]
    actual = getattr(module, entry)
    received = []

    def capture(*args, **kwargs):
        received.append(kwargs["settings"])
        return actual(*args, **kwargs)

    monkeypatch.setattr(module, entry, capture)
    settings.write_text('{"x.py":{"mode":"wide"}}', encoding="utf-8")
    assert module.main() == (1 if command == "prove_unchanged" else 0)
    assert received == (
        [{"mode": "wide"}] if command == "compositor" else [{path: {"mode": "wide"}}]
    )


def test_default_contexts_are_retained_in_fresh_results(tmp_path):
    path = tmp_path / "x.py"
    path.write_text("# prose\n", encoding="utf-8")
    gathering = gather(tmp_path, [path], 0)
    assert gathering.reading_contexts[path].language == "python"
    result = round_trip(path)
    assert not isinstance(result, ReadFailure)
    assert isinstance(result.reading_context, ReadingContext)
    assert result.reading_context.settings == ()


def identity(value: LanguageDefinition, **revisions: str) -> str:
    return context_module.compatibility_identity(
        value,
        reader_revision=revisions.get("reader_revision", "reader-1"),
        placement_revision=revisions.get("placement_revision", "placement-1"),
        grammar_identity=revisions.get("grammar_identity", "grammar-1"),
        digest=lambda data: sha256(data).hexdigest(),
    )


def test_compatibility_has_independent_canonical_digest():
    canonical = (
        '{"definition":{"capabilities":["comments"],'
        '"choices":{"mode":["","wide"]},"defaults":{"mode":""},'
        '"language":"Invented","reader":"invented-reader",'
        '"revision":"definition-1","rules":{"nested":{"tokens":["\u03bb",true,1]}},'
        '"suffixes":[".ix"]},"grammar_identity":"grammar-1",'
        '"placement_revision":"placement-1","reader_revision":"reader-1"}'
    )
    expected = "cefc5dc0563af6a3a811daa0bd6e7babbd224ca9ee1a3150c97e81adfc9be1fa"
    assert sha256(canonical.encode("utf-8")).hexdigest() == expected
    assert identity(definition()) == expected


@pytest.mark.parametrize(
    "change",
    [
        {"language": "Other"},
        {"reader": "other-reader"},
        {"revision": "definition-2"},
        {"suffixes": (".other",)},
        {"capabilities": ("strings",)},
        {"defaults": {"mode": "wide"}},
        {"choices": {"mode": ("wide", "")}},
        {"choices": {"mode": ("", "wide", "extra")}},
        {"rules": {"nested": {"tokens": [1, True, "\u03bb"]}}},
        {"rules": {"nested": {"tokens": ["\u03bb", False, 1]}}},
        {"rules": {"nested": {"tokens": ["\u03bb", 1, 1]}}},
        {"rules": {"nested": {"tokens": ["\u03bb", True, "1"]}}},
    ],
)
def test_complete_definition_changes_invalidate_identity(change):
    original = definition()
    assert identity(replace(original, **change)) != identity(original)


@pytest.mark.parametrize(
    "field",
    [
        "reader_revision",
        "placement_revision",
        "grammar_identity",
    ],
)
def test_runtime_revisions_invalidate_identity(field):
    assert identity(definition(), **{field: "changed"}) != identity(definition())


@pytest.mark.parametrize("field", ["reader_revision", "placement_revision"])
@pytest.mark.parametrize("invalid", ["", None, 1, True])
def test_required_runtime_revisions_are_validated(field, invalid):
    with pytest.raises(ValueError):
        identity(definition(), **{field: invalid})


def test_empty_grammar_identity_is_valid():
    assert len(identity(definition(), grammar_identity="")) == 64


@pytest.mark.parametrize("invalid", [None, 1, True, ()])
def test_grammar_identity_must_be_a_string(invalid):
    with pytest.raises(ValueError):
        identity(definition(), grammar_identity=invalid)


@pytest.mark.parametrize("field", ["suffixes", "capabilities"])
def test_definition_arrays_preserve_order(field):
    values = (".ix", ".other") if field == "suffixes" else ("comments", "strings")
    original = replace(definition(), **{field: values})
    reordered = replace(original, **{field: tuple(reversed(values))})
    assert identity(original) != identity(reordered)


def test_settings_table_key_order_is_insignificant():
    original = replace(
        definition(),
        defaults={"mode": "", "other": "on"},
        choices={"mode": ("", "wide"), "other": ("on", "off")},
    )
    reordered = replace(
        original,
        defaults={"other": "on", "mode": ""},
        choices={"other": ("on", "off"), "mode": ("", "wide")},
    )
    assert identity(original) == identity(reordered)


def test_mapping_order_and_equivalent_toml_layout_do_not_change_identity():
    header = """format = 1
language = "Invented"
suffixes = [".ix"]
reader = "invented-reader"
revision = "definition-1"
capabilities = ["comments"]
"""
    first = decode_definition(
        header
        + """defaults = { mode = "" }
choices = { mode = ["", "wide"] }
rules = { z = {}, nested = { tokens = ["\u03bb", true, 1], a = "" } }
"""
    )
    second = decode_definition(
        header
        + """# Different layout and table ordering.
[rules.nested]
a = ""
tokens = ["\u03bb", true, 1]
[rules.z]
[choices]
mode = ["", "wide"]
[defaults]
mode = ""
"""
    )
    assert isinstance(first, LanguageDefinition)
    assert isinstance(second, LanguageDefinition)
    assert identity(first) == identity(second)


def test_compatibility_accepts_only_definition_and_relevant_revisions():
    assert tuple(signature(context_module.compatibility_identity).parameters) == (
        "definition",
        "reader_revision",
        "placement_revision",
        "grammar_identity",
        "digest",
    )
    original = definition()
    before = identity(original)
    unrelated = replace(original, language="Other", suffixes=(".other",))
    registry = LanguageRegistry((original, unrelated))
    selected = registry.for_language("Invented")
    assert isinstance(selected, LanguageDefinition)
    assert identity(selected) == before


def test_effective_settings_invalidate_context_with_same_derived_digest():
    digest = identity(definition())
    saved = ReadingContext("Invented", "invented-reader", digest, (("mode", ""),))
    current = replace(saved, settings=(("mode", "wide"),))
    assert not compatible_contexts(saved, current)


def test_exact_context_equality():
    saved = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    current = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    assert saved == current
    assert compatible_contexts(saved, current)


@pytest.mark.parametrize(
    "language,reader,digest,settings",
    [
        ("other", "reader-one", "a1" * 32, (("mode", "on"),)),
        ("invented", "reader-two", "a1" * 32, (("mode", "on"),)),
        ("invented", "reader-one", "b2" * 32, (("mode", "on"),)),
        ("invented", "reader-one", "a1" * 32, (("mode", "off"),)),
        ("invented", "reader-one", "a1" * 32, ()),
    ],
)
def test_each_context_field_must_match(language, reader, digest, settings):
    saved = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    current = ReadingContext(language, reader, digest, settings)
    assert not compatible_contexts(saved, current)
    assert not compatible_contexts(current, saved)


def test_settings_are_sorted_and_empty_values_are_preserved():
    saved = ReadingContext(
        "invented", "reader-one", "a1" * 32, (("z", "yes"), ("a", ""))
    )
    assert saved.settings == (("a", ""), ("z", "yes"))
    current = ReadingContext(
        "invented", "reader-one", "a1" * 32, (("a", ""), ("z", "yes"))
    )
    assert compatible_contexts(saved, current)


def test_empty_settings_are_valid():
    context = ReadingContext("invented", "reader-one", "0" * 64, ())
    assert context.settings == ()


@pytest.mark.parametrize("field", ["language", "reader"])
@pytest.mark.parametrize("invalid", ["", None, 1, True, [], (), {}])
def test_invalid_identity_is_rejected(field, invalid):
    values: dict[str, Any] = {
        "language": "invented",
        "reader": "reader-one",
        "compatibility": "a1" * 32,
        "settings": (),
    }
    values[field] = invalid
    with pytest.raises(ValueError):
        ReadingContext(**values)


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        1,
        True,
        [],
        (),
        "",
        "a" * 63,
        "a" * 65,
        "A" * 64,
        "g" * 64,
        "a" * 64 + "\n",
        " " + "a" * 63,
    ],
)
def test_invalid_digest_is_rejected(invalid):
    with pytest.raises(ValueError):
        ReadingContext("invented", "reader-one", invalid, ())


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        "mode",
        1,
        True,
        [],
        {},
        [("mode", "on")],
        ("mode",),
        (["mode", "on"],),
        (None,),
        ((),),
        (("mode",),),
        (("mode", "on", "extra"),),
        (("", "on"),),
        ((None, "on"),),
        ((1, "on"),),
        ((True, "on"),),
        (([], "on"),),
        (("mode", None),),
        (("mode", 1),),
        (("mode", True),),
        (("mode", []),),
        (("mode", {}),),
        (("mode", "on"), ("mode", "off")),
        (("mode", "on"), ("mode", "on")),
    ],
)
def test_invalid_settings_are_rejected(invalid):
    with pytest.raises(ValueError):
        ReadingContext("invented", "reader-one", "a1" * 32, invalid)


@pytest.mark.parametrize("field", ["language", "reader", "compatibility", "settings"])
def test_context_fields_cannot_be_reassigned(field):
    context = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    with pytest.raises(FrozenInstanceError):
        setattr(context, field, "replacement")


def test_nested_settings_cannot_be_mutated():
    context = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    with pytest.raises(TypeError):
        context.settings[0][1] = "off"  # ty: ignore[invalid-assignment]


def wire_context() -> dict[str, Any]:
    return {
        "format": 1,
        "language": "uninstalled-language",
        "reader": "uninstalled-reader",
        "compatibility": "ab" * 32,
        "settings": {"z": "on", "a": ""},
    }


def test_context_wire_decodes_literal_and_normalizes_settings():
    from comment_review.reading.context_io import context_from_wire

    decoded, problems = context_from_wire("input.json:context", wire_context())
    assert problems == []
    assert decoded == ReadingContext(
        "uninstalled-language",
        "uninstalled-reader",
        "ab" * 32,
        (("a", ""), ("z", "on")),
    )


def test_context_wire_serialization_is_exact_detached_and_round_trips():
    from comment_review.reading.context_io import context_from_wire, context_to_wire

    context = ReadingContext(
        "uninstalled-language",
        "uninstalled-reader",
        "ab" * 32,
        (("z", "on"), ("a", "")),
    )
    encoded = context_to_wire(context)
    assert encoded == wire_context()
    assert list(encoded["settings"]) == ["a", "z"]
    assert context_from_wire("context", encoded) == (context, [])
    again = context_to_wire(context)
    assert again is not encoded
    assert again["settings"] is not encoded["settings"]
    encoded["settings"]["a"] = "changed"
    encoded["language"] = "changed"
    assert context_to_wire(context) == wire_context()


@pytest.mark.parametrize("value", [None, [], (), "context", 1, True])
def test_context_wire_requires_object_with_regather_diagnostic(value):
    from comment_review.reading.context_io import context_from_wire

    decoded, problems = context_from_wire("input.json:context", value)
    assert decoded is None
    assert len(problems) == 1
    assert "input.json:context" in problems[0]
    assert "regather" in problems[0].lower()


@pytest.mark.parametrize("key", list(wire_context()))
def test_context_wire_requires_every_key(key):
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    del value[key]
    decoded, problems = context_from_wire("input.json:context", value)
    assert decoded is None
    assert "input.json:context" in problems[0]
    assert key in problems[0]
    assert "regather" in problems[0].lower()


@pytest.mark.parametrize("key", ["extra", 1, None])
def test_context_wire_rejects_unknown_keys(key):
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    value[key] = "extra"
    decoded, problems = context_from_wire("wire", value)
    assert decoded is None
    assert "wire" in problems[0]


@pytest.mark.parametrize("version", [2, 0, -1, True, False, 1.0, "1", None])
def test_context_wire_rejects_unsupported_and_noninteger_formats(version):
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    value["format"] = version
    decoded, problems = context_from_wire("wire", value)
    assert decoded is None
    assert "wire" in problems[0]
    assert "format" in problems[0]
    assert "regather" in problems[0].lower()


@pytest.mark.parametrize(
    "field,invalid",
    [
        ("language", ""),
        ("language", None),
        ("language", 1),
        ("reader", ""),
        ("reader", True),
        ("reader", []),
        ("compatibility", ""),
        ("compatibility", "A" * 64),
        ("compatibility", "a" * 63),
        ("compatibility", "g" * 64),
        ("compatibility", None),
        ("compatibility", 1),
        ("settings", None),
        ("settings", []),
        ("settings", (("a", "on"),)),
        ("settings", {"": "on"}),
        ("settings", {1: "on"}),
        ("settings", {None: "on"}),
        ("settings", {"a": None}),
        ("settings", {"a": 1}),
        ("settings", {"a": True}),
        ("settings", {"a": []}),
    ],
)
def test_context_wire_rejects_invalid_values_with_located_diagnostic(field, invalid):
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    value[field] = invalid
    decoded, problems = context_from_wire("input.json:context", value)
    assert decoded is None
    assert len(problems) == 1
    assert "input.json:context" in problems[0]
    assert "regather" in problems[0].lower()


def test_context_wire_settings_order_is_insignificant_and_empty_settings_valid():
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    reordered = {**value, "settings": {"a": "", "z": "on"}}
    assert context_from_wire("wire", value) == context_from_wire("wire", reordered)
    empty, problems = context_from_wire("wire", {**value, "settings": {}})
    assert problems == []
    assert isinstance(empty, ReadingContext)
    assert empty.settings == ()


def test_context_wire_requires_exact_dictionary_types():
    from comment_review.reading.context_io import context_from_wire

    class DictionarySubclass(dict):
        pass

    for value in (
        DictionarySubclass(wire_context()),
        {**wire_context(), "settings": DictionarySubclass(a="on")},
    ):
        decoded, problems = context_from_wire("wire", value)
        assert decoded is None
        assert "wire" in problems[0]


def test_context_wire_unexpected_constructor_defects_propagate(monkeypatch):
    from comment_review.reading import context_io

    def broken_context(*args):
        raise RuntimeError("unexpected defect")

    monkeypatch.setattr(context_io, "ReadingContext", broken_context)
    with pytest.raises(RuntimeError, match="unexpected defect"):
        context_io.context_from_wire("wire", wire_context())
