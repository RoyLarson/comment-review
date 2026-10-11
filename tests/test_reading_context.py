from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from comment_review.reading.context import ReadingContext, compatible_contexts


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
