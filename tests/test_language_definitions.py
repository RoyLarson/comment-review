"""Public validation and immutability of language configuration."""

from dataclasses import FrozenInstanceError
from datetime import date
from importlib import import_module
from pathlib import Path
from typing import Any

import pytest

from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage

WIRE = """format = 1
language = "Invented MIX"
suffixes = [".IX", ".invented"]
reader = "invented-reader"
revision = "r2"
capabilities = ["comments", "strings"]
defaults = { style = "" }
choices = { style = ["", "wide"] }
rules = { tokens = ["", 2, true, false, { end = [] }], empty = {} }
"""


def decode(text: str) -> Any:
    return import_module("comment_review.reading.definitions").decode_definition(text)


def failure(message: str) -> ReadFailure:
    return ReadFailure(
        (ReadDiagnostic(ReadStage.SELECT, "invalid-language-definition", message),)
    )


def load(paths: list[Path]) -> Any:
    return import_module("comment_review.flows.language_definitions").load_definitions(
        paths
    )


def test_load_empty_input_returns_empty_tuple() -> None:
    assert load([]) == ()


def test_load_files_preserves_input_order_and_nested_values(tmp_path: Path) -> None:
    first = tmp_path / "first.toml"
    second = tmp_path / "second.toml"
    first.write_text(WIRE, encoding="utf-8")
    second.write_text(WIRE.replace("Invented MIX", "Other Invented"), encoding="utf-8")

    values = load([second, first])

    assert isinstance(values, tuple)
    assert tuple(value.language for value in values) == (
        "Other Invented",
        "Invented MIX",
    )
    assert values[0].rules == {
        "tokens": ("", 2, True, False, {"end": ()}),
        "empty": {},
    }
    assert values[1].choices == {"style": ("", "wide")}


def test_load_missing_file_retains_acquisition_diagnostic(tmp_path: Path) -> None:
    path = tmp_path / "missing.toml"

    result = load([path])

    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.ACQUIRE
    assert diagnostic.code == "io-error"
    assert str(path) in diagnostic.message
    assert diagnostic.byte_offset is None


def test_load_invalid_utf8_retains_decode_byte_offset(tmp_path: Path) -> None:
    path = tmp_path / "bad-bytes.toml"
    path.write_bytes(b"format = 1\n\xff")

    result = load([path])

    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.DECODE
    assert diagnostic.code == "invalid-utf8"
    assert str(path) in diagnostic.message
    assert "invalid start byte" in diagnostic.message
    assert diagnostic.byte_offset == 11


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("", "missing fields:"),
        ("format = [", "Invalid value"),
        (WIRE.replace("format = 1", "format = 2"), "format must be integer 1"),
    ],
)
def test_load_invalid_definition_retains_selection_failure(
    tmp_path: Path, text: str, reason: str
) -> None:
    path = tmp_path / "invalid.toml"
    path.write_text(text, encoding="utf-8")

    result = load([path])

    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.SELECT
    assert diagnostic.code == "invalid-language-definition"
    assert str(path) in diagnostic.message
    assert reason in diagnostic.message
    assert diagnostic.byte_offset is None


def test_load_later_file_failure_does_not_publish_partial_tuple(tmp_path: Path) -> None:
    good = tmp_path / "good.toml"
    bad = tmp_path / "bad.toml"
    good.write_text(WIRE, encoding="utf-8")
    bad.write_text("", encoding="utf-8")

    result = load([good, bad])

    assert isinstance(result, ReadFailure)
    assert str(bad) in result.diagnostics[0].message


def test_load_decodes_held_text_without_another_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = import_module("comment_review.flows.language_definitions")
    source = import_module("comment_review.flows.source")
    path = tmp_path / "held.toml"
    path.write_text(WIRE, encoding="utf-8")

    def acquire_then_remove(acquired_path: Path) -> Any:
        value = source.source_of(acquired_path)
        acquired_path.unlink()
        return value

    monkeypatch.setattr(module, "source_of", acquire_then_remove)

    values = load([path])

    assert isinstance(values, tuple)
    assert len(values) == 1
    assert values[0].language == "Invented MIX"
    assert values[0].rules["tokens"] == ("", 2, True, False, {"end": ()})


def test_load_unexpected_acquisition_defect_propagates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = import_module("comment_review.flows.language_definitions")

    def broken_acquisition(path: Path) -> Any:
        raise RuntimeError("programming error")

    monkeypatch.setattr(module, "source_of", broken_acquisition)
    with pytest.raises(RuntimeError, match="programming error"):
        load([tmp_path / "example.toml"])


def test_decode_exact_definition_and_ordered_nested_rules() -> None:
    value = decode(WIRE)
    assert value == definition(
        language="Invented MIX",
        suffixes=(".IX", ".invented"),
        reader="invented-reader",
        revision="r2",
        capabilities=("comments", "strings"),
        defaults={"style": ""},
        choices={"style": ("", "wide")},
        rules={"tokens": ("", 2, True, False, {"end": ()}), "empty": {}},
    )
    assert type(value.rules["tokens"][1]) is int
    assert type(value.rules["tokens"][2]) is bool


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("format = [", "Invalid value (at end of document)"),
        ("format = 1\nformat = 1", "Cannot overwrite a value (at end of document)"),
    ],
)
def test_decode_reports_specific_toml_syntax_errors(text: str, reason: str) -> None:
    assert decode(text) == failure(reason)


@pytest.mark.parametrize("raw", ['"1"', "true", "2", "1.0", "[]", "{}"])
def test_decode_refuses_wrong_and_future_formats(raw: str) -> None:
    assert decode(WIRE.replace("format = 1", f"format = {raw}")) == failure(
        "format must be integer 1"
    )


@pytest.mark.parametrize(
    "field",
    [
        "format",
        "language",
        "suffixes",
        "reader",
        "revision",
        "capabilities",
        "defaults",
        "choices",
        "rules",
    ],
)
def test_decode_requires_every_wire_field(field: str) -> None:
    text = "\n".join(line for line in WIRE.splitlines() if not line.startswith(field))
    assert decode(text) == failure(f"missing fields: {field}")


def test_decode_refuses_unknown_wire_fields() -> None:
    assert decode(WIRE + "extra = 1\n") == failure("unknown fields: extra")


@pytest.mark.parametrize(
    ("field", "raw", "reason"),
    [
        ("language", "1", "language must be a nonempty string"),
        ("reader", "[]", "reader must be a nonempty string"),
        ("revision", "{}", "revision must be a nonempty string"),
        ("language", '""', "language must be a nonempty string"),
        ("suffixes", '".ix"', "suffixes must be an array of strings"),
        ("suffixes", "{}", "suffixes must be an array of strings"),
        ("suffixes", "[1]", "suffixes must contain nonempty strings"),
        ("suffixes", '["ix"]', "suffixes must start with a dot"),
        ("suffixes", '[".ix", ".IX"]', "suffixes must be unique after lowercasing"),
        ("capabilities", '"comments"', "capabilities must be an array of strings"),
        ("capabilities", "{}", "capabilities must be an array of strings"),
        ("capabilities", "[false]", "capabilities must contain nonempty strings"),
        ("defaults", "[]", "defaults must be a mapping"),
        ("choices", "[]", "choices must be a mapping"),
        ("rules", "[]", "rules must be a mapping"),
        (
            "defaults",
            "{ style = 1 }",
            "defaults.style must be a declared string choice",
        ),
        (
            "defaults",
            '{ style = "absent" }',
            "defaults.style must be a declared string choice",
        ),
        ("defaults", "{}", "defaults and choices must have the same settings keys"),
        ("choices", '{ style = "wide" }', "choices.style must be an array of strings"),
        ("choices", "{ style = {} }", "choices.style must be an array of strings"),
        ("choices", "{ style = [] }", "choices.style must be nonempty"),
        ("choices", "{ style = [1] }", "choices.style must contain strings"),
        (
            "choices",
            '{ style = ["", ""] }',
            "choices.style must contain unique strings",
        ),
        (
            "rules",
            "{ nested = [1.5] }",
            "rules.nested[0] contains unsupported rule value float",
        ),
        (
            "rules",
            "{ nested = [2000-01-01] }",
            "rules.nested[0] contains unsupported rule value date",
        ),
        (
            "rules",
            "{ nested = [2000-01-01T00:00:00] }",
            "rules.nested[0] contains unsupported rule value datetime",
        ),
    ],
)
def test_decode_retains_field_validation_reasons(
    field: str, raw: str, reason: str
) -> None:
    text = "\n".join(
        f"{field} = {raw}" if line.startswith(f"{field} = ") else line
        for line in WIRE.splitlines()
    )
    assert decode(text) == failure(reason)


def test_decode_accepts_explicit_empty_arrays_and_tables() -> None:
    text = """format = 1
language = "Empty"
suffixes = []
reader = "empty-reader"
revision = "1"
capabilities = []
defaults = {}
choices = {}
rules = {}
"""
    assert decode(text) == definition(
        language="Empty",
        suffixes=(),
        reader="empty-reader",
        revision="1",
        capabilities=(),
        defaults={},
        choices={},
        rules={},
    )


def test_decode_does_not_catch_unexpected_programming_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = import_module("comment_review.reading.definitions")

    def broken_definition(**values: Any) -> None:
        raise RuntimeError("programming error")

    monkeypatch.setattr(module, "LanguageDefinition", broken_definition)
    with pytest.raises(RuntimeError, match="programming error"):
        decode(WIRE)


def configuration(**changes: Any) -> dict[str, Any]:
    values = {
        "language": "Example",
        "suffixes": (".ex",),
        "reader": "example-reader",
        "revision": "1",
        "capabilities": ("comments",),
        "defaults": {"style": ""},
        "choices": {"style": ("", "wide")},
        "rules": {},
    }
    values.update(changes)
    return values


def definition(**values: Any) -> Any:
    cls = import_module("comment_review.reading.definitions").LanguageDefinition
    return cls(**values)


def binding(**changes: Any) -> Any:
    values = {
        "reader": "example-reader",
        "revision": "1",
        "capabilities": ("comments",),
        "grammar_identity": "",
        "read": lambda path, text, lang: [],
        "validate": lambda value: None,
    }
    values.update(changes)
    return import_module("comment_review.reading.readers").ReaderBinding(**values)


def bind(value: Any, bindings: Any) -> Any:
    return import_module("comment_review.reading.readers").bind_reader(value, bindings)


@pytest.mark.parametrize("identifier", ["unknown", "os.system"])
def test_binding_unknown_identifier_never_invokes_validator(
    identifier: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    import builtins

    def forbidden(value: Any) -> Any:
        pytest.fail("Unknown readers must not invoke installed callables")

    installed = binding(validate=forbidden, read=forbidden)
    value = definition(**configuration(reader=identifier))
    bind_reader = import_module("comment_review.reading.readers").bind_reader
    with monkeypatch.context() as patch:
        patch.setattr(builtins, "__import__", forbidden)
        result = bind_reader(value, {installed.reader: installed})
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.SELECT
    assert result.diagnostics[0].code == "unavailable-reader"


@pytest.mark.parametrize("claims", [("strings",), ("comments", "strings")])
def test_binding_unsupported_capability_refuses_before_validation(claims: Any) -> None:
    def forbidden(value: Any) -> Any:
        pytest.fail("Unsupported capabilities must refuse before validation")

    result = bind(
        definition(**configuration(capabilities=claims)),
        {"example-reader": binding(validate=forbidden)},
    )
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].code == "unavailable-reader"


def test_binding_key_and_identifier_must_agree() -> None:
    result = bind(
        definition(**configuration()), {"example-reader": binding(reader="other")}
    )
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].code == "unavailable-reader"


@pytest.mark.parametrize("rules", [{}, {"tokens": 1}, {"tokens": ()}])
def test_binding_validator_distinguishes_missing_invalid_and_empty_grammar(
    rules: Any,
) -> None:
    def validate(value: Any) -> ReadFailure | None:
        if "tokens" not in value.rules or not isinstance(value.rules["tokens"], tuple):
            return failure("tokens must be present as an array")
        return None

    def forbidden(path: Path, text: str, lang: Any) -> Any:
        pytest.fail("Binding must validate grammar before recognition")

    installed = binding(validate=validate, read=forbidden)
    result = bind(
        definition(**configuration(rules=rules)), {installed.reader: installed}
    )
    if rules == {"tokens": ()}:
        assert result is installed
    else:
        assert result == failure("tokens must be present as an array")


def test_binding_read_once_with_exact_source_and_retains_refusal() -> None:
    from comment_review.reading.language import LANGUAGES

    calls = []
    refused = ReadFailure(
        (
            ReadDiagnostic(ReadStage.LEX, "first", "one"),
            ReadDiagnostic(ReadStage.LEX, "second", "two"),
        )
    )

    def read(path: Path, text: str, lang: Any) -> ReadFailure:
        calls.append((path, text, lang))
        return refused

    installed = binding(read=read)
    path, text, lang = Path("source.py"), "# exact\r\n", LANGUAGES[0]
    registered = registry((definition(**configuration(suffixes=(".py",))),))
    selected = bind(registered.for_path(path), {installed.reader: installed})
    assert selected.read(path, text, lang) is refused
    assert calls == [(path, text, lang)]
    assert installed.grammar_identity == ""
    with pytest.raises(FrozenInstanceError):
        installed.revision = "2"


@pytest.mark.parametrize(
    "field,value",
    [
        ("reader", ""),
        ("revision", ""),
        ("capabilities", ["comments"]),
        ("capabilities", ("comments", "comments")),
        ("capabilities", (1,)),
        ("grammar_identity", None),
        ("read", None),
        ("validate", None),
    ],
)
def test_binding_rejects_invalid_constructor_fields(field: str, value: Any) -> None:
    with pytest.raises(ValueError, match=field):
        binding(**{field: value})


@pytest.mark.parametrize("missing", tuple(configuration()))
def test_every_field_is_required(missing: str) -> None:
    values = configuration()
    del values[missing]
    with pytest.raises(TypeError, match=missing):
        definition(**values)


def test_explicit_empty_configuration_is_valid() -> None:
    value = definition(
        **configuration(suffixes=(), capabilities=(), defaults={}, choices={}, rules={})
    )
    assert value.language == "Example"
    assert value.suffixes == ()
    assert value.capabilities == ()
    assert value.defaults == value.choices == value.rules == {}


@pytest.mark.parametrize("field", ["language", "reader", "revision"])
@pytest.mark.parametrize("invalid", ["", None, 1, [], {}])
def test_identity_fields_require_nonempty_strings(field: str, invalid: Any) -> None:
    with pytest.raises(ValueError, match=field):
        definition(**configuration(**{field: invalid}))


def test_identity_and_suffix_spelling_are_preserved() -> None:
    value = definition(**configuration(language="Example MIX", suffixes=(".EX",)))
    assert value.language == "Example MIX"
    assert value.suffixes == (".EX",)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("suffixes", [".ex"]),
        ("suffixes", ".ex"),
        ("suffixes", ("",)),
        ("suffixes", (1,)),
        ("suffixes", ("ex",)),
        ("suffixes", (".ex", ".EX")),
        ("capabilities", ["comments"]),
        ("capabilities", "comments"),
        ("capabilities", ("",)),
        ("capabilities", (None,)),
        ("capabilities", ("comments", "comments")),
    ],
)
def test_tuple_fields_reject_invalid_values(field: str, invalid: Any) -> None:
    with pytest.raises(ValueError, match=field):
        definition(**configuration(**{field: invalid}))


@pytest.mark.parametrize(
    "changes",
    [
        {"defaults": []},
        {"choices": []},
        {"defaults": {"": ""}, "choices": {"": ("",)}},
        {"defaults": {1: ""}, "choices": {1: ("",)}},
        {"defaults": {"style": 1}},
        {"defaults": {"style": "missing"}},
        {"defaults": {}},
        {"choices": {}},
        {"choices": {"style": []}},
        {"choices": {"style": "wide"}},
        {"choices": {"style": ()}},
        {"choices": {"style": ("", "")}},
        {"choices": {"style": ("", 1)}},
        {"choices": {"style": ("wide",)}},
    ],
)
def test_settings_require_matching_keys_and_declared_choices(changes: Any) -> None:
    with pytest.raises(ValueError, match="defaults|choices|setting"):
        definition(**configuration(**changes))


@pytest.mark.parametrize("invalid", [None, 1.5, date(2000, 1, 1), set(), object()])
def test_rules_reject_unsupported_nested_values(invalid: Any) -> None:
    with pytest.raises(ValueError, match="rules"):
        definition(**configuration(rules={"nested": [invalid]}))


@pytest.mark.parametrize("invalid", [[], None, {1: "token"}, {"nested": {1: "x"}}])
def test_rules_require_string_keyed_mappings(invalid: Any) -> None:
    with pytest.raises(ValueError, match="rules"):
        definition(**configuration(rules=invalid))


def test_rule_values_preserve_types_order_and_empty_tables() -> None:
    value = definition(
        **configuration(rules={"tokens": ["", 2, True, False, {"end": ()}], "x": {}})
    )
    tokens = value.rules["tokens"]
    assert tokens == ("", 2, True, False, {"end": ()})
    assert type(tokens[1]) is int
    assert type(tokens[2]) is bool
    assert value.rules["x"] == {}


def test_attributes_and_all_mapping_levels_are_immutable() -> None:
    value = definition(**configuration(rules={"nested": [{"token": "end"}]}))
    with pytest.raises(FrozenInstanceError):
        value.language = "Other"
    for mapping in (
        value.defaults,
        value.choices,
        value.rules,
        value.rules["nested"][0],
    ):
        with pytest.raises(TypeError):
            mapping["new"] = "other"
    with pytest.raises(TypeError):
        value.rules["nested"][0] = {}


def test_mutating_caller_inputs_does_not_change_definition() -> None:
    defaults = {"style": ""}
    choices = {"style": ("", "wide")}
    table = {"token": "end"}
    array = [table]
    rules = {"nested": array}
    value = definition(**configuration(defaults=defaults, choices=choices, rules=rules))
    defaults["style"] = "wide"
    choices["style"] = ("wide",)
    table["token"] = "changed"
    array.append({})
    rules.clear()
    assert value.defaults == {"style": ""}
    assert value.choices == {"style": ("", "wide")}
    assert value.rules == {"nested": ({"token": "end"},)}


def registry(values: Any) -> Any:
    return import_module("comment_review.reading.registry").LanguageRegistry(values)


def select_registry(values: Any) -> Any:
    return import_module("comment_review.reading.registry").registry_for(values)


@pytest.mark.parametrize("reverse", [False, True])
def test_registry_selection_is_independent_of_registration_order(reverse: bool) -> None:
    demo = definition(**configuration(language="Demo MIX", suffixes=(".DEMO",)))
    other = definition(**configuration(language="Other", suffixes=(".jsx", ".tsx")))
    values = (other, demo) if reverse else (demo, other)
    value = registry(values)
    assert value.for_path(Path("nested/name.DeMo")) is demo
    assert value.for_path(Path("component.JSX")) is other
    assert value.for_path(Path("component.tsx")) is other
    assert value.for_language("Demo MIX") is demo
    assert value.for_language("demo mix") is None
    assert value.for_language("Other") is other
    assert value.for_path(Path("unknown.py")) is None
    assert value.for_path(Path("extensionless")) is None
    assert select_registry(values) == value


def test_empty_registry_has_no_matches() -> None:
    value = registry(())
    assert value.for_path(Path("name.demo")) is None
    assert value.for_language("Demo") is None
    assert select_registry(()) == value


def test_registry_and_registered_definitions_are_immutable() -> None:
    demo = definition(**configuration(suffixes=(".demo",)))
    value = registry((demo,))
    registered = value.definitions
    with pytest.raises(FrozenInstanceError):
        value.definitions = ()
    with pytest.raises(TypeError):
        registered[0] = demo
    with pytest.raises(FrozenInstanceError):
        registered[0].suffixes = (".changed",)
    assert value.for_path(Path("name.demo")) is demo


@pytest.mark.parametrize("invalid", [None, [], {}, "demo", (None,), ("demo",)])
def test_registry_rejects_wrong_constructor_input(invalid: Any) -> None:
    with pytest.raises(ValueError, match="definitions"):
        registry(invalid)
    result = select_registry(invalid)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.SELECT
    assert result.diagnostics[0].code == "invalid-language-definition"


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    ("names", "suffixes", "code"),
    [
        (("Same", "Same"), ((".one",), (".two",)), "duplicate-language"),
        (("First", "Second"), ((".demo",), (".demo",)), "ambiguous-language"),
        (("First", "Second"), ((".DEMO",), (".demo",)), "ambiguous-language"),
    ],
)
def test_registry_refuses_collisions_in_both_orders(
    reverse: bool, names: tuple[str, str], suffixes: Any, code: str
) -> None:
    values = tuple(
        definition(**configuration(language=name, suffixes=claimed))
        for name, claimed in zip(names, suffixes, strict=True)
    )
    if reverse:
        values = tuple(reversed(values))
    with pytest.raises(ValueError):
        registry(values)
    result = select_registry(values)
    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.SELECT
    assert diagnostic.code == code
    assert all(name in diagnostic.message for name in names)


def test_registry_preserves_distinct_exact_language_identities() -> None:
    upper = definition(**configuration(language="Demo", suffixes=(".one",)))
    lower = definition(**configuration(language="demo", suffixes=(".two",)))
    value = registry((upper, lower))
    assert value.for_language("Demo") is upper
    assert value.for_language("demo") is lower


@pytest.mark.parametrize(
    "suffix",
    [
        ".toml",
        ".ini",
        ".yaml",
        ".yml",
        ".json",
        ".jsonl",
        ".md",
        ".markdown",
        ".rst",
        ".txt",
        ".html",
        ".htm",
        ".css",
    ],
)
@pytest.mark.parametrize("uppercase", [False, True])
def test_registry_refuses_non_code_suffixes(suffix: str, uppercase: bool) -> None:
    claim = suffix.upper() if uppercase else suffix
    values = (definition(**configuration(language="Excluded", suffixes=(claim,))),)
    with pytest.raises(ValueError, match="Excluded"):
        registry(values)
    result = select_registry(values)
    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.SELECT
    assert diagnostic.code == "invalid-language-definition"
    assert "Excluded" in diagnostic.message
    assert claim in diagnostic.message


def test_installed_code_definitions_have_exact_suffixes_and_independent_rules() -> None:
    from dataclasses import fields

    from comment_review.reading.language import INSTALLED_DEFINITIONS, LANGUAGES

    expected = {
        "python": (".py", ".pyi"),
        "rust": (".rs",),
        "go": (".go",),
        "c": (".c", ".h"),
        "cpp": (".cpp", ".hpp", ".cc", ".cxx"),
        "java": (".java",),
        "csharp": (".cs",),
        "swift": (".swift",),
        "kotlin": (".kt", ".kts"),
        "javascript": (".js", ".jsx", ".mjs", ".cjs"),
        "typescript": (".ts", ".tsx", ".mts", ".cts"),
        "ruby": (".rb",),
        "shell": (".sh", ".bash", ".zsh"),
        "sql": (".sql",),
        "lua": (".lua",),
    }
    assert {
        value.language: value.suffixes for value in INSTALLED_DEFINITIONS
    } == expected
    rows = {row.name: row for row in LANGUAGES}
    for value in INSTALLED_DEFINITIONS:
        row = rows[value.language]
        assert value.defaults == value.choices == {}
        assert dict(value.rules) == {
            field.name: getattr(row, field.name)
            for field in fields(row)
            if field.name not in {"name", "extensions"}
        }
    assert len({id(value.rules) for value in INSTALLED_DEFINITIONS}) == 15


def test_installed_bindings_validate_rules_and_host_identity() -> None:
    import platform
    import sys
    from dataclasses import replace

    from comment_review.reading.language import INSTALLED_DEFINITIONS, READER_METADATA
    from comment_review.reading.readers import INSTALLED_BINDINGS

    for value in INSTALLED_DEFINITIONS:
        installed = INSTALLED_BINDINGS[value.reader]
        assert bind(value, INSTALLED_BINDINGS) is installed
        metadata = READER_METADATA[value.language]
        assert installed.revision == value.revision == metadata.revision
        assert installed.capabilities == value.capabilities == metadata.capabilities
        assert metadata.tier in installed.capabilities
        if value.language == "python":
            assert platform.python_implementation() in installed.grammar_identity
            assert platform.python_version() in installed.grammar_identity
            assert sys.version in installed.grammar_identity
        else:
            assert installed.grammar_identity == ""
        for rules in (
            {},
            {**value.rules, "unknown": ()},
            {**value.rules, "quotes": False},
            {**value.rules, "nests_comments": 1},
            {**value.rules, "block_comment": ("/*", "*/")},
            {**value.rules, "quotes": ("",)},
            *(
                {key: item for key, item in value.rules.items() if key != missing}
                for missing in value.rules
            ),
        ):
            assert isinstance(
                bind(replace(value, rules=rules), INSTALLED_BINDINGS), ReadFailure
            )
        empty = {
            key: False if isinstance(item, bool) else ()
            for key, item in value.rules.items()
        }
        assert bind(replace(value, rules=empty), INSTALLED_BINDINGS) is installed
        with pytest.raises(ValueError):
            from comment_review.reading.language import language_from_definition

            language_from_definition(replace(value, rules={}))
        assert isinstance(
            bind(replace(value, capabilities=("dialects",)), INSTALLED_BINDINGS),
            ReadFailure,
        )
        assert isinstance(
            bind(replace(value, reader="absent"), INSTALLED_BINDINGS), ReadFailure
        )
        assert isinstance(
            bind(replace(value, language="other"), INSTALLED_BINDINGS), ReadFailure
        )


def test_installed_bindings_invoke_existing_engines(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from comment_review.reading import readers
    from comment_review.reading.language import (
        INSTALLED_DEFINITIONS,
        language_from_definition,
    )

    calls = []
    monkeypatch.setattr(
        readers,
        "paragraphs_stdlib",
        lambda path, text: calls.append(("stdlib", path, text)) or [],
    )
    monkeypatch.setattr(
        readers,
        "paragraphs_lexical",
        lambda path, text, lang: calls.append((lang.name, path, text)) or [],
    )
    for value in INSTALLED_DEFINITIONS:
        path = Path("source" + value.suffixes[0])
        lang = language_from_definition(value)
        assert (
            readers.INSTALLED_BINDINGS[value.reader].read(path, "exact\r\n", lang) == []
        )
        assert calls[-1] == (
            "stdlib" if value.language == "python" else value.language,
            path,
            "exact\r\n",
        )


@pytest.mark.parametrize(
    "suffix",
    [".toml", ".ini", ".cfg", ".yaml", ".json", ".md", ".html", ".css", ".unknown"],
)
def test_installed_selection_excludes_non_code(suffix: str) -> None:
    from comment_review.reading.language import language_for
    from comment_review.reading.readers import reader_for

    assert language_for(Path("source" + suffix.upper())) is None
    assert reader_for(Path("source" + suffix.upper())) is None


def test_installed_selection_and_coverage_use_validated_bindings(monkeypatch) -> None:
    from dataclasses import replace

    from comment_review.reading import readers
    from comment_review.reading.language import INSTALLED_REGISTRY, language_for
    from comment_review.reading.readers import tier_for

    selected = readers.reader_for(Path("component.TSX"))
    assert selected is not None and not isinstance(selected, ReadFailure)
    value, installed = selected
    assert value is INSTALLED_REGISTRY.for_path(Path("component.tsx"))
    lang = language_for(Path("component.tsx"))
    assert lang is not None
    assert tier_for(lang) == "lexical"
    assert value in readers.supported_definitions()
    monkeypatch.setattr(readers, "INSTALLED_BINDINGS", {})
    assert tier_for(lang) == ""
    assert isinstance(readers.reader_for(Path("component.TSX")), ReadFailure)
    assert readers.supported_definitions() == ()
    monkeypatch.setattr(
        readers,
        "INSTALLED_BINDINGS",
        {value.reader: replace(installed, capabilities=("comments",))},
    )
    assert isinstance(readers.reader_for(Path("component.TSX")), ReadFailure)
    assert readers.supported_definitions() == ()
