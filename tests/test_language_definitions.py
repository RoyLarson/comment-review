"""Public validation and immutability of language configuration."""

from dataclasses import FrozenInstanceError
from datetime import date
from importlib import import_module
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
