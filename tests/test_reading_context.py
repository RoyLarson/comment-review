from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
from inspect import signature
from typing import Any

import pytest

from comment_review.reading import context as context_module
from comment_review.reading.context import ReadingContext, compatible_contexts
from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.registry import LanguageRegistry


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


def identity(value: LanguageDefinition, **revisions: str) -> str:
    return context_module.compatibility_identity(
        value,
        reader_revision=revisions.get("reader_revision", "reader-1"),
        placement_revision=revisions.get("placement_revision", "placement-1"),
        grammar_identity=revisions.get("grammar_identity", "grammar-1"),
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
