"""Validate the explicit Rust grammar without acquiring definition files."""

from collections.abc import Callable, Mapping
from typing import cast

from comment_review.reading.definition_checks import (
    require_array,
    require_scalar,
    require_table,
)
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage

# The owner kinds the Rust grammar defines. `[rules.documentation].owners`
# lists those that take documentation. The module is the file's own frame,
# whose documentation place is `a0`.
MODULE = "module"
ITEM = "item"
ASSOCIATED_ITEM = "associated-item"
NESTED_ITEM = "nested-item"
FIELD = "field"
VARIANT = "variant"
OWNER_KINDS = frozenset({MODULE, ITEM, ASSOCIATED_ITEM, NESTED_ITEM, FIELD, VARIANT})


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
    rules: Mapping[str, object],
    name: str,
    supported: Mapping[str, object],
    chosen: Mapping[str, Callable[[object, str], None]] | None = None,
) -> None:
    """Require exactly the keys of `supported` and `chosen` under `rules[name]`.

    Each key in `supported` must hold its value; each key in `chosen` is
    passed, with its path, to its own check.
    """
    path = f"rules.{name}"
    chosen = chosen or {}
    table = require_table(rules[name], path, " ".join([*supported, *chosen]))
    for key, check in chosen.items():
        check(table[key], f"{path}.{key}")
    for key, expected in supported.items():
        if isinstance(expected, tuple):
            require_array(table[key], f"{path}.{key}", expected)
        else:
            require_scalar(
                table[key], f"{path}.{key}", cast(str | bool | int, expected)
            )


def _owners(value: object, path: str) -> None:
    """Require a nonempty array of distinct owner kinds from OWNER_KINDS."""
    if not isinstance(value, tuple) or not value:
        raise ValueError(f"{path} must be a nonempty array")
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{path} contains an ill-typed item")
        if item not in OWNER_KINDS:
            raise ValueError(f"{path} has unsupported item {item!r}")
    if len(set(value)) != len(value):
        raise ValueError(f"{path} repeats an item")


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
            "raw_lifetime_prefix": "r#",
            "raw_identifier_prefix": "r#",
        },
    )
    _section(
        rules,
        "attributes",
        {"outer_open": "#[", "inner_open": "#![", "open": "[", "close": "]"},
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
            "associated_containers": ("impl", "trait"),
            "macro_definitions": ("macro_rules!",),
            "abi_qualifier": "extern",
            "macro_marker": "!",
            "body_open": "{",
            "generics_open": "<",
            "generics_close": ">",
            "arrow": "->",
            "terminator": ";",
            "separator": ",",
        },
    )
    _section(
        rules,
        "documentation",
        {
            "position": "above-head",
            "added_outer": "///",
            "added_inner": "//!",
            "detached": "ordinary-comment-with-warning",
        },
        {"owners": _owners},
    )
    _section(
        rules,
        "directives",
        {"shebang": "#!", "shebang_line": 1, "inner_attribute_follows": "["},
    )
