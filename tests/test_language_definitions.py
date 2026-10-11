"""Public validation and immutability of language configuration."""

from dataclasses import FrozenInstanceError
from datetime import date
from importlib import import_module
from typing import Any

import pytest


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
