"""Validate the explicit Rust grammar without acquiring definition files."""

from collections.abc import Mapping
from typing import cast

from comment_review.reading.definition_checks import (
    require_array,
    require_scalar,
    require_table,
)
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
        require_scalar(getattr(value, field), field, expected)
    require_array(value.suffixes, "suffixes", (".rs",))
    require_array(
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


def _section(
    rules: Mapping[str, object], name: str, supported: Mapping[str, object]
) -> None:
    """Require exactly `supported`'s keys under `rules[name]`, each with its value."""
    path = f"rules.{name}"
    table = require_table(rules[name], path, " ".join(supported))
    for key, expected in supported.items():
        if isinstance(expected, tuple):
            require_array(table[key], f"{path}.{key}", expected)
        else:
            require_scalar(
                table[key], f"{path}.{key}", cast(str | bool | int, expected)
            )


def _grammar(rules: Mapping[str, object]) -> None:
    require_table(
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
