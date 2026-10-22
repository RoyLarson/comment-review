"""Validate the explicit Python grammar without acquiring definition files."""

from collections.abc import Mapping

from comment_review.reading.definition_checks import (
    require_array,
    require_scalar,
    require_table,
)
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
        require_scalar(getattr(value, field), field, expected)
    require_array(value.suffixes, "suffixes", (".py", ".pyi"))
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
        raise ValueError("defaults and choices: Python implements no settings")


def _grammar(rules: Mapping[str, object]) -> None:
    require_table(
        rules,
        "rules",
        "language_version comments literals layout declarations documentation "
        "directives",
    )
    require_scalar(rules["language_version"], "rules.language_version", "3.15")
    comments = require_table(
        rules["comments"], "rules.comments", "marker paragraph_markers sections"
    )
    require_scalar(comments["marker"], "rules.comments.marker", "#")
    require_array(comments["paragraph_markers"], "rules.comments.paragraph_markers", ())
    require_scalar(
        comments["sections"], "rules.comments.sections", "same-form-across-blanks"
    )
    _literals(rules["literals"])
    _layout(rules["layout"])
    _declarations(rules["declarations"])
    _documentation(rules["documentation"])
    _directives(rules["directives"])


def _literals(value: object) -> None:
    path = "rules.literals"
    table = require_table(
        value,
        path,
        "short_quotes triple_quotes case_insensitive_prefixes escape_marker "
        "interpolation_open interpolation_close doubled_braces prefixes decoding",
    )
    quotes = ("'", '"')
    require_array(table["short_quotes"], f"{path}.short_quotes", quotes)
    require_array(
        table["triple_quotes"], f"{path}.triple_quotes", tuple(q * 3 for q in quotes)
    )
    require_scalar(
        table["case_insensitive_prefixes"], f"{path}.case_insensitive_prefixes", True
    )
    require_scalar(table["escape_marker"], f"{path}.escape_marker", "\\")
    require_scalar(table["interpolation_open"], f"{path}.interpolation_open", "{")
    require_scalar(table["interpolation_close"], f"{path}.interpolation_close", "}")
    require_scalar(table["doubled_braces"], f"{path}.doubled_braces", True)
    prefixes = require_table(
        table["prefixes"],
        f"{path}.prefixes",
        "plain raw bytes raw_bytes formatted raw_formatted template raw_template",
    )
    require_array(prefixes["plain"], f"{path}.prefixes.plain", ("", "u"))
    require_array(prefixes["raw"], f"{path}.prefixes.raw", ("r",))
    for group, prefix in (("bytes", "b"), ("formatted", "f"), ("template", "t")):
        require_array(prefixes[group], f"{path}.prefixes.{group}", (prefix,))
        require_array(
            prefixes[f"raw_{group}"],
            f"{path}.prefixes.raw_{group}",
            (prefix + "r", "r" + prefix),
        )
    _decoding(table["decoding"], quotes)


def _decoding(value: object, quotes: tuple[str, ...]) -> None:
    path = "rules.literals.decoding"
    table = require_table(
        value,
        path,
        "simple_escapes octal_max_digits hex_digits unicode_short_digits "
        "unicode_long_digits named_unicode unknown_escape escaped_newline raw_escape",
    )
    require_array(
        table["simple_escapes"], f"{path}.simple_escapes", ("\\", *quotes, *"abfnrtv")
    )
    require_scalar(table["octal_max_digits"], f"{path}.octal_max_digits", 3)
    for key, digits in (
        ("hex_digits", 2),
        ("unicode_short_digits", 4),
        ("unicode_long_digits", 8),
    ):
        require_scalar(table[key], f"{path}.{key}", digits)
    require_scalar(table["named_unicode"], f"{path}.named_unicode", True)
    require_scalar(table["unknown_escape"], f"{path}.unknown_escape", "preserve")
    require_scalar(table["escaped_newline"], f"{path}.escaped_newline", "remove")
    require_scalar(table["raw_escape"], f"{path}.raw_escape", "preserve")


def _layout(value: object) -> None:
    path = "rules.layout"
    table = require_table(
        value,
        path,
        "significant_indentation tab_width formfeed explicit_join implicit_pairs "
        "statement_separator suite_delimiter",
    )
    require_scalar(
        table["significant_indentation"], f"{path}.significant_indentation", True
    )
    require_scalar(table["tab_width"], f"{path}.tab_width", 8)
    require_scalar(table["formfeed"], f"{path}.formfeed", "reset-leading")
    require_scalar(table["explicit_join"], f"{path}.explicit_join", "\\")
    require_array(
        table["implicit_pairs"],
        f"{path}.implicit_pairs",
        (("(", ")"), ("[", "]"), ("{", "}")),
    )
    require_scalar(table["statement_separator"], f"{path}.statement_separator", ";")
    require_scalar(table["suite_delimiter"], f"{path}.suite_delimiter", ":")


def _declarations(value: object) -> None:
    path = "rules.declarations"
    table = require_table(
        value,
        path,
        "keywords async_keyword decorator type_parameters multiline_headers",
    )
    require_array(table["keywords"], f"{path}.keywords", ("def", "class"))
    require_scalar(table["async_keyword"], f"{path}.async_keyword", "async")
    require_scalar(table["decorator"], f"{path}.decorator", "@")
    require_array(table["type_parameters"], f"{path}.type_parameters", ("[", "]"))
    require_scalar(table["multiline_headers"], f"{path}.multiline_headers", True)


def _documentation(value: object) -> None:
    path = "rules.documentation"
    table = require_table(
        value, path, "owners position literal_groups adjacent parenthesized assigned"
    )
    require_array(
        table["owners"],
        f"{path}.owners",
        ("module", "class", "function", "async-function"),
    )
    require_scalar(table["position"], f"{path}.position", "first-statement")
    require_array(table["literal_groups"], f"{path}.literal_groups", ("plain", "raw"))
    require_scalar(table["adjacent"], f"{path}.adjacent", True)
    require_scalar(table["parenthesized"], f"{path}.parenthesized", True)
    require_scalar(table["assigned"], f"{path}.assigned", False)


def _directives(value: object) -> None:
    path = "rules.directives"
    table = require_table(
        value,
        path,
        "shebang shebang_line shebang_column encoding_markers encoding_lines "
        "encoding_second_line encoding_own_line type_marker type_position",
    )
    require_scalar(table["shebang"], f"{path}.shebang", "#!")
    require_scalar(table["shebang_line"], f"{path}.shebang_line", 1)
    require_scalar(table["shebang_column"], f"{path}.shebang_column", 0)
    require_array(
        table["encoding_markers"], f"{path}.encoding_markers", ("coding:", "coding=")
    )
    require_array(table["encoding_lines"], f"{path}.encoding_lines", (1, 2))
    require_scalar(
        table["encoding_second_line"],
        f"{path}.encoding_second_line",
        "comment-or-blank-first-line",
    )
    require_scalar(table["encoding_own_line"], f"{path}.encoding_own_line", True)
    require_scalar(table["type_marker"], f"{path}.type_marker", "type:")
    require_scalar(
        table["type_position"],
        f"{path}.type_position",
        "comment-start-after-whitespace",
    )
