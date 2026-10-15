"""Validate the explicit Python grammar without acquiring definition files."""

from collections.abc import Mapping
from typing import cast

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage


def validate_python(definition: LanguageDefinition) -> ReadFailure | None:
    """Require complete, supported Python 3.15 grammar and empty settings."""
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
        ("language", "python"),
        ("reader", "python-lexical"),
        ("revision", "1"),
    ):
        _scalar(getattr(value, field), field, expected)
    _array(value.suffixes, "suffixes", (".py", ".pyi"))
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
        raise ValueError("defaults and choices: Python implements no settings")


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


def _grammar(rules: Mapping[str, object]) -> None:
    _table(
        rules,
        "rules",
        "language_version comments literals layout declarations documentation "
        "directives",
    )
    _scalar(rules["language_version"], "rules.language_version", "3.15")
    comments = _table(
        rules["comments"], "rules.comments", "marker paragraph_markers sections"
    )
    _scalar(comments["marker"], "rules.comments.marker", "#")
    _array(comments["paragraph_markers"], "rules.comments.paragraph_markers", ())
    _scalar(comments["sections"], "rules.comments.sections", "same-form-across-blanks")
    _literals(rules["literals"])
    _layout(rules["layout"])
    _declarations(rules["declarations"])
    _documentation(rules["documentation"])
    _directives(rules["directives"])


def _literals(value: object) -> None:
    path = "rules.literals"
    table = _table(
        value,
        path,
        "short_quotes triple_quotes case_insensitive_prefixes escape_marker "
        "interpolation_open interpolation_close doubled_braces prefixes decoding",
    )
    quotes = ("'", '"')
    _array(table["short_quotes"], f"{path}.short_quotes", quotes)
    _array(
        table["triple_quotes"], f"{path}.triple_quotes", tuple(q * 3 for q in quotes)
    )
    _scalar(
        table["case_insensitive_prefixes"], f"{path}.case_insensitive_prefixes", True
    )
    _scalar(table["escape_marker"], f"{path}.escape_marker", "\\")
    _scalar(table["interpolation_open"], f"{path}.interpolation_open", "{")
    _scalar(table["interpolation_close"], f"{path}.interpolation_close", "}")
    _scalar(table["doubled_braces"], f"{path}.doubled_braces", True)
    prefixes = _table(
        table["prefixes"],
        f"{path}.prefixes",
        "plain raw bytes raw_bytes formatted raw_formatted template raw_template",
    )
    _array(prefixes["plain"], f"{path}.prefixes.plain", ("", "u"))
    _array(prefixes["raw"], f"{path}.prefixes.raw", ("r",))
    for group, prefix in (("bytes", "b"), ("formatted", "f"), ("template", "t")):
        _array(prefixes[group], f"{path}.prefixes.{group}", (prefix,))
        _array(
            prefixes[f"raw_{group}"],
            f"{path}.prefixes.raw_{group}",
            (prefix + "r", "r" + prefix),
        )
    _decoding(table["decoding"], quotes)


def _decoding(value: object, quotes: tuple[str, ...]) -> None:
    path = "rules.literals.decoding"
    table = _table(
        value,
        path,
        "simple_escapes octal_max_digits hex_digits unicode_short_digits "
        "unicode_long_digits named_unicode unknown_escape escaped_newline raw_escape",
    )
    _array(
        table["simple_escapes"], f"{path}.simple_escapes", ("\\", *quotes, *"abfnrtv")
    )
    _scalar(table["octal_max_digits"], f"{path}.octal_max_digits", 3)
    for key, digits in (
        ("hex_digits", 2),
        ("unicode_short_digits", 4),
        ("unicode_long_digits", 8),
    ):
        _scalar(table[key], f"{path}.{key}", digits)
    _scalar(table["named_unicode"], f"{path}.named_unicode", True)
    _scalar(table["unknown_escape"], f"{path}.unknown_escape", "preserve")
    _scalar(table["escaped_newline"], f"{path}.escaped_newline", "remove")
    _scalar(table["raw_escape"], f"{path}.raw_escape", "preserve")


def _layout(value: object) -> None:
    path = "rules.layout"
    table = _table(
        value,
        path,
        "significant_indentation tab_width formfeed explicit_join implicit_pairs "
        "statement_separator suite_delimiter",
    )
    _scalar(table["significant_indentation"], f"{path}.significant_indentation", True)
    _scalar(table["tab_width"], f"{path}.tab_width", 8)
    _scalar(table["formfeed"], f"{path}.formfeed", "reset-leading")
    _scalar(table["explicit_join"], f"{path}.explicit_join", "\\")
    _array(
        table["implicit_pairs"],
        f"{path}.implicit_pairs",
        (("(", ")"), ("[", "]"), ("{", "}")),
    )
    _scalar(table["statement_separator"], f"{path}.statement_separator", ";")
    _scalar(table["suite_delimiter"], f"{path}.suite_delimiter", ":")


def _declarations(value: object) -> None:
    path = "rules.declarations"
    table = _table(
        value,
        path,
        "keywords async_keyword decorator type_parameters multiline_headers",
    )
    _array(table["keywords"], f"{path}.keywords", ("def", "class"))
    _scalar(table["async_keyword"], f"{path}.async_keyword", "async")
    _scalar(table["decorator"], f"{path}.decorator", "@")
    _array(table["type_parameters"], f"{path}.type_parameters", ("[", "]"))
    _scalar(table["multiline_headers"], f"{path}.multiline_headers", True)


def _documentation(value: object) -> None:
    path = "rules.documentation"
    table = _table(
        value, path, "owners position literal_groups adjacent parenthesized assigned"
    )
    _array(
        table["owners"],
        f"{path}.owners",
        ("module", "class", "function", "async-function"),
    )
    _scalar(table["position"], f"{path}.position", "first-statement")
    _array(table["literal_groups"], f"{path}.literal_groups", ("plain", "raw"))
    _scalar(table["adjacent"], f"{path}.adjacent", True)
    _scalar(table["parenthesized"], f"{path}.parenthesized", True)
    _scalar(table["assigned"], f"{path}.assigned", False)


def _directives(value: object) -> None:
    path = "rules.directives"
    table = _table(
        value,
        path,
        "shebang shebang_line shebang_column encoding_markers encoding_lines "
        "encoding_second_line encoding_own_line type_marker type_position",
    )
    _scalar(table["shebang"], f"{path}.shebang", "#!")
    _scalar(table["shebang_line"], f"{path}.shebang_line", 1)
    _scalar(table["shebang_column"], f"{path}.shebang_column", 0)
    _array(
        table["encoding_markers"], f"{path}.encoding_markers", ("coding:", "coding=")
    )
    _array(table["encoding_lines"], f"{path}.encoding_lines", (1, 2))
    _scalar(
        table["encoding_second_line"],
        f"{path}.encoding_second_line",
        "comment-or-blank-first-line",
    )
    _scalar(table["encoding_own_line"], f"{path}.encoding_own_line", True)
    _scalar(table["type_marker"], f"{path}.type_marker", "type:")
    _scalar(
        table["type_position"],
        f"{path}.type_position",
        "comment-start-after-whitespace",
    )
