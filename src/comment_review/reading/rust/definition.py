"""Validate the explicit Rust grammar without acquiring definition files."""

from collections.abc import Mapping
from typing import cast

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage


def validate_rust(definition: LanguageDefinition) -> ReadFailure | None:
    """Require complete, supported Rust grammar and empty settings."""
    try:
        _identity(definition)
        _grammar(definition.rules)
    except ValueError as error:
        return ReadFailure(
            (
                ReadDiagnostic(
                    ReadStage.SELECT, "invalid-language-definition", str(error)
                ),
            )
        )
    return None


def _identity(value: LanguageDefinition) -> None:
    for field, expected in (
        ("language", "rust"),
        ("reader", "rust-lexical"),
        ("revision", "2"),
    ):
        _scalar(getattr(value, field), field, expected)
    _array(value.suffixes, "suffixes", (".rs",))
    _array(
        value.capabilities,
        "capabilities",
        (
            "comments",
            "strings",
            "declarations",
            "documentation",
            "protected-directives",
            "lexical",
        ),
    )
    if value.defaults or value.choices:
        raise ValueError("defaults and choices: Rust implements no settings")


def _table(value: object, path: str, keys: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a table")
    table = cast(Mapping[str, object], value)
    required = set(keys.split())
    missing = required - table.keys()
    unknown = table.keys() - required
    if missing:
        raise ValueError(f"{path}.{sorted(missing)[0]} is required")
    if unknown:
        raise ValueError(f"{path}.{sorted(unknown)[0]} is unknown")
    return table


def _scalar(value: object, path: str, supported: str | bool | int) -> None:
    kind = (
        "boolean"
        if isinstance(supported, bool)
        else "string"
        if isinstance(supported, str)
        else "integer"
    )
    if type(value) is not type(supported):
        raise ValueError(f"{path} must be a {kind}")
    if value != supported:
        raise ValueError(f"{path} has unsupported value {value!r}")


def _array(value: object, path: str, supported: tuple[object, ...]) -> None:
    if not isinstance(value, tuple):
        raise ValueError(f"{path} must be an array")
    if len(value) != len(supported):
        raise ValueError(f"{path} has unsupported items")
    for item, expected in zip(value, supported, strict=True):
        if type(item) is not type(expected):
            raise ValueError(f"{path} contains an ill-typed item")
        if item != expected:
            raise ValueError(f"{path} has unsupported item {item!r}")


def _section(
    rules: Mapping[str, object], name: str, supported: Mapping[str, object]
) -> None:
    """Require exactly `supported`'s keys under `rules[name]`, each with its value."""
    path = f"rules.{name}"
    table = _table(rules[name], path, " ".join(supported))
    for key, expected in supported.items():
        if isinstance(expected, tuple):
            _array(table[key], f"{path}.{key}", expected)
        else:
            _scalar(table[key], f"{path}.{key}", cast(str | bool | int, expected))


def _grammar(rules: Mapping[str, object]) -> None:
    _table(
        rules,
        "rules",
        "comments literals attributes declarations documentation directives",
    )
    _section(
        rules,
        "comments",
        {
            "line": "//",
            "outer_doc_line": "///",
            "inner_doc_line": "//!",
            "block_comment": ("/*", "*/"),
            "outer_doc_block": "/**",
            "inner_doc_block": "/*!",
            "nests": True,
            "doc_marker_repeated_is_ordinary": True,
            "empty_block_comment": "/**/",
            "sections": "same-form-across-blanks",
        },
    )
    _section(
        rules,
        "literals",
        {
            "string_quote": '"',
            "string_prefixes": ("b", "c"),
            "raw_prefixes": ("r", "br", "cr"),
            "raw_guard": "#",
            "char_quote": "'",
            "char_prefixes": ("b",),
            "escape_marker": "\\",
            "unicode_escape": ("\\u{", "}"),
            "raw_lifetime_prefix": "r#",
        },
    )
    _section(
        rules,
        "attributes",
        {"outer_open": "#[", "inner_open": "#![", "close": "]"},
    )
    _section(
        rules,
        "declarations",
        {
            "visibility": "pub",
            "visibility_scopes": ("crate", "super", "self", "in"),
            "qualifiers": (
                "default",
                "const",
                "async",
                "unsafe",
                "safe",
                "extern",
                "auto",
            ),
            "keywords": (
                "fn",
                "struct",
                "enum",
                "union",
                "trait",
                "impl",
                "mod",
                "type",
                "const",
                "static",
                "use",
                "extern",
                "macro_rules!",
            ),
            "contextual": ("union", "auto", "safe", "default", "macro_rules!"),
            "item_containers": ("mod", "impl", "trait", "extern"),
            "member_lists": ("struct", "union"),
            "variant_lists": ("enum",),
            "function_bodies": ("fn",),
        },
    )
    _section(
        rules,
        "documentation",
        {
            "owners": (
                "module",
                "item",
                "associated-item",
                "field",
                "variant",
                "nested-item",
            ),
            "position": "above-head",
            "added_outer": "///",
            "added_inner": "//!",
            "detached": "ordinary-comment-with-warning",
        },
    )
    _section(
        rules,
        "directives",
        {"shebang": "#!", "shebang_line": 1, "inner_attribute_follows": "["},
    )
