"""Language grammar: the shipped definition files and the lexical rows.

A language with its own definition file is read from it:
`references/languages/*.toml` is loaded at import, one file per language, into
`SHIPPED_DEFINITIONS`. Python and Rust are defined that way.

The other code languages are still rows in `LANGUAGES`, and installed
definitions materialize grammar from each row `READER_METADATA` names -- every
row but TOML, INI and YAML. Validation requires complete grammar with the
language's expected value shapes. Shared reader metadata supplies identities,
revisions, capabilities and coverage tiers for registration, dispatch and
reporting.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from importlib.resources import files
from pathlib import Path
from types import MappingProxyType
from typing import Any, cast

from comment_review import constants
from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.registry import LanguageRegistry


@dataclass(frozen=True)
class Language:
    """What the LEXICAL tier needs to find prose in a language it only lexes.

    A row is installed by its `READER_METADATA` entry. A row with no entry is
    not: `language_for` returns None for TOML, INI and YAML.

    Attributes:
        doc_line: line-comment openers that mean DOC rather than ordinary
            comment (Rust `///`, `//!`). Empty when the language marks docs
            some other way.
        doc_block: paragraph openers that mean DOC (`/**`). Same idea.
        quotes: string delimiters, so a marker inside a literal is skipped.
        char_quotes: delimiters that hold exactly ONE character in this
            language -- `'a'`, or one escape. !! IT IS PER LANGUAGE AND CANNOT BE ONE
            RULE: `'x'` is a character in Rust, C, C++, Go, Java, C# and
            Kotlin, and `'a string'` is prose in Python, JS, Ruby, Lua, shell
            and SQL. ! What it buys is that a `'` which does NOT close within a
            character's width is ORDINARY TEXT rather than an open quote --
            which is what a Rust lifetime is. Without it, `pub fn
            name(&self) -> &'static str { 1 } // the display name` gathers
            zero prose paragraphs, because `'static` opens a literal that
            never closes and blanks the comment with the rest of the line.
        spanning_quotes: delimiters whose literal may cross LINES -- a JS
            template literal, a Java text block. ! `_strip_strings` is per-line
            and carries no open-quote state, so a comment marker INSIDE one of
            these reads as a comment; `prove_unchanged` refuses such a file
            rather than proving it. Empty where a language has none.
        declares: the KEYWORDS this language uses to introduce something that
            can carry documentation. Empty, the language still has an `a`
            series when it has doc markers -- see `a_series`.
        nests_comments: an opener INSIDE a paragraph comment adds a LAYER, so the
            run closes only when every one of them does. Rust, Swift and Kotlin;
            C, C++, Java, C#, JS, TS, Go and SQL do NOT, and there the first
            closer wins. ! Lua nests only through its `--[==[` long-bracket
            form, which is a different opener, so it is False.
        doc_inside: the documentation is the first thing INSIDE the body, not
            the run ABOVE the declaration. No row sets it: the language that
            documents this way, Python, states it in its own definition file.
        shebang: what line 1 opens with when it is an interpreter line the
            language does not read as a comment (`#!`). The line is the file's own
            matter, and the matter rule opens on the line below it. Empty
            where the language has none, or reads it as a comment.
    """

    name: str
    extensions: tuple[str, ...]
    line_comment: tuple[str, ...]
    block_comment: tuple[tuple[str, str], ...] = ()
    doc_line: tuple[str, ...] = ()
    doc_block: tuple[str, ...] = ()
    quotes: tuple[str, ...] = ('"', "'")
    char_quotes: tuple[str, ...] = ()
    nests_comments: bool = False
    spanning_quotes: tuple[str, ...] = ()
    declares: tuple[str, ...] = ()
    doc_inside: bool = False
    shebang: tuple[str, ...] = ()

    @property
    def a_series(self) -> bool:
        """Whether the row declares a documentation practice: doc markers or keywords.

        A language with neither, such as YAML or TOML, has no `a` series at all
        -- not an empty one -- since an `a0` there could never be filled.
        """
        return bool(self.doc_line or self.doc_block or self.declares)

    @property
    def closing_docstring(self) -> bool:
        """Whether the module's documentation can sit at the file's foot: a doc marker.

        A run after the last line of code documents the module only when it is
        doc-marked, so a row with no doc marker, such as Go or Ruby, has no
        closing docstring, and a comment written there is back matter.
        """
        return bool(self.doc_line or self.doc_block)

    def interpreter_line(self, lines: Sequence[str]) -> str | None:
        """The file's first line when it opens with `shebang`, exactly, or None.

        `lines` is the file's lines, as `constants.text_lines` gives them. A
        byte-order mark before the shebang is part of the line returned, and
        not part of what is matched.
        """
        if lines and lines[0].removeprefix(constants.BYTE_ORDER_MARK).startswith(
            self.shebang
        ):
            return lines[0]
        return None


# ! Line-comment openers are matched longest-first whatever order a row
# lists them in, so `///` is tried before `//` and a Rust doc line keeps
# its slashes. Block-comment pairs are not sorted at every match site, so
# a row lists the longer of two overlapping openers first.
#
# ! A TWO-WORD `declares` ENTRY IS MACHINERY THIS FILE OFFERS EVERY ROW,
# not a technique one language takes from another. What goes IN it comes
# from the grammar of that row's language and nowhere else -- Kotlin says
# `data class` because Kotlin's grammar does; Lua says `local function`
# because Lua's does. Neither is evidence about the other, and a row that
# reasoned from a neighbour would be assembling one definition out of two.
LANGUAGES: tuple[Language, ...] = (
    Language(
        "go",
        (".go",),
        ("//",),
        (("/*", "*/"),),
        # ! A rune literal is one character.
        char_quotes=("'",),
        # !! THE BACKTICK IS A STRING DELIMITER AND MUST BE BLANKED. Leaving it
        # out on the ground that a raw string takes no escapes was reasoning
        # about the wrong cost: `return `http://example.com/a`` then read as
        # a TRAILING COMMENT carrying the URL as prose, the `return` line left
        # `return `http:` and dropped out of `code_text`, and every `b`/`c`
        # below it renumbered.
        # ! This blanking is imperfect here: `_strip_strings` honours a
        # backslash, and a raw string ending in one (`` `C:\` ``) runs past its
        # closer. That shape is rarer than a URL by a wide margin.
        quotes=('"', "'", "`"),
        # !! AND IT CROSSES LINES, which is a separate claim with a separate
        # consumer: `prove_unchanged` REFUSES a file holding one rather than
        # trusting a per-line read of it.
        spanning_quotes=("`",),
        # ! `package` is NOT here: Go's package comment IS the file's own
        # documentation, which is `a0`. Naming it gave the same prose two
        # places, `a0` and `a1`.
        declares=("func", "type", "var", "const"),
    ),
    # !! C AND C++ DECLARE NO KEYWORDS, so no declaration gets an `a`. A C
    # function is introduced by its RETURN TYPE -- `size_t f(void)`, `MyRec
    # f(void)` -- and `_declares_here` reads only a line's first two words, so
    # no keyword list can reach the name. Their doc marker still gives the
    # module its `a0` and `<eof>` `a` -- see `Language.a_series`.
    # ! A wrong `a` is worse than no `a`: a spurious match renumbers every `a`
    # below it, and an instruction is then invited on something that cannot hold one.
    Language(
        "c",
        (".c", ".h"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        char_quotes=("'",),
        quotes=('"', "'"),
    ),
    Language(
        "cpp",
        (".cpp", ".hpp", ".cc", ".cxx"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        char_quotes=("'",),
        # !! A RAW STRING LITERAL CROSSES LINES. `R"(...)"` takes no escapes and
        # ends only at its matching delimiter, so a line inside one beginning
        # `//` is read as a comment and deleted from BOTH fingerprints. The
        # prefix is declared rather than the bare quote because `R"` is
        # distinctive: `LR"`, `u8R"` and `uR"` all contain it, and ordinary C++
        # strings do not.
        spanning_quotes=('R"',),
        quotes=('"', "'"),
    ),
    Language(
        "java",
        (".java",),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        char_quotes=("'",),
        # ! A member declaration opens with a MODIFIER or a type. `final` is
        # left out because it also opens a local; `static` never does in Java.
        # A package-private member opening with its type is missed, and a
        # reviewer reading the file is what supplies it.
        declares=(
            "public",
            "protected",
            "private",
            "static",
            "abstract",
            "synchronized",
            "native",
            "strictfp",
            "class",
            "interface",
            "enum",
            # !! `record` IS A SOFT KEYWORD AND THIS ROW CANNOT YET SAY SO.
            # `record = lookup()` is a legal assignment and mints a spurious `a`
            # place.
            #
            # ! JAVA'S SECOND WORD IS THE RECORD'S NAME AND VARIES, so a two-word
            # entry has no fixed pair to match and `record Point(int x)` would
            # stop being found. That is a fact about Java's grammar, not about
            # whether the two-word form is available -- it is, to every row.
            #
            # ! SO JAVA NEEDS A DEFINITION OF ITS OWN. Filed on
            # `lexer-and-language-findings`; `record` stays here so the real
            # declaration is still found.
            "record",
        ),
        # ! A Java TEXT BLOCK spans lines the same way, and a `//` inside one is
        # not a comment.
        spanning_quotes=('"""',),
        quotes=('"', "'"),
    ),
    Language(
        "csharp",
        (".cs",),
        # ! `///` IS LISTED, and the lexer tries the longest opener first. Naming
        # only `//` cut two of the three slashes and left the third in the prose:
        # `/ <summary>The one doc.</summary>`.
        ("///", "//"),
        (("/*", "*/"),),
        doc_line=("///",),
        doc_block=("/**",),
        char_quotes=("'",),
        # ! `var` is left out: it opens a local and nothing else.
        declares=(
            "public",
            "protected",
            "private",
            "internal",
            "static",
            "abstract",
            "virtual",
            "override",
            "sealed",
            "partial",
            "unsafe",
            "class",
            "interface",
            "enum",
            "struct",
            "record",
            "delegate",
            "namespace",
        ),
        # !! TWO SHAPES CROSS LINES HERE, and both are declared.
        # `"""` is the C# 11 raw string; `@"..."` is the VERBATIM string and has
        # been in the language since 1.0, so it is the one a real file holds. A
        # `//` inside either is read as a comment. ! `$@"` and `@$"` both
        # contain `@"`.
        spanning_quotes=('"""', '@"'),
        quotes=('"', "'"),
    ),
    Language(
        "swift",
        (".swift",),
        # ! `///` IS LISTED, for the reason C#'s is.
        ("///", "//"),
        (("/*", "*/"),),
        doc_line=("///",),
        doc_block=("/**",),
        # ! Swift nests its paragraph comments.
        nests_comments=True,
        # ! `let` and `var` are left out: they open a local as readily as a
        # property, so including them would declare every local binding.
        declares=(
            "func",
            "class",
            "struct",
            "enum",
            "protocol",
            "extension",
            "actor",
            "typealias",
            "init",
            "deinit",
            "subscript",
            "public",
            "private",
            "fileprivate",
            "internal",
            "open",
            "static",
            "override",
            "convenience",
            "required",
        ),
        spanning_quotes=('"""',),
        quotes=('"',),
    ),
    Language(
        "kotlin",
        (".kt", ".kts"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        char_quotes=("'",),
        # ! Kotlin nests its paragraph comments.
        nests_comments=True,
        # ! `val` and `var` are left out: they open a local as readily as a property.
        declares=(
            "fun",
            "class",
            "interface",
            "object",
            "enum",
            # !! KOTLIN'S SOFT KEYWORDS DECLARE ONLY BEFORE A FIXED SECOND WORD,
            # which is a fact about KOTLIN. `data`, `sealed` and `open` are
            # ordinary identifiers, and `_declares_here` matches a listed first word
            # on its own -- so a bare `data` entry would mint an `a` place for the
            # assignment `data = load()`.
            "data class",
            "sealed class",
            "sealed interface",
            "open class",
            "annotation",
            "typealias",
            "companion",
            "abstract",
            "internal",
            "public",
            "protected",
            "private",
            "override",
            "suspend",
        ),
        spanning_quotes=('"""',),
        quotes=('"', "'"),
    ),
    Language(
        "javascript",
        (".js", ".jsx", ".mjs", ".cjs"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        # ! `const`, `let` and `var` are left out: at module scope one may hold
        # a documented function, and inside a body every one of them is a local.
        declares=("function", "class", "export", "async"),
        quotes=('"', "'", "`"),
        spanning_quotes=("`",),
        # ! Node and the ECMAScript hashbang grammar read `#!` on line 1 as an
        # interpreter line, not as code and not as a comment.
        shebang=("#!",),
    ),
    Language(
        "typescript",
        (".ts", ".tsx", ".mts", ".cts"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        # ! JavaScript's list plus what TypeScript adds. DUPLICATED ON PURPOSE:
        # one shared list would make a TypeScript release change JavaScript's
        # answer.
        declares=(
            "function",
            "class",
            "export",
            "async",
            "interface",
            "type",
            "enum",
            "namespace",
            "declare",
            "abstract",
        ),
        quotes=('"', "'", "`"),
        spanning_quotes=("`",),
        # ! TypeScript's scanner reads `#!` on line 1 as an interpreter line
        # and emits it unchanged.
        shebang=("#!",),
    ),
    Language(
        "ruby",
        (".rb",),
        ("#",),
        (("=begin", "=end"),),
        declares=("def", "class", "module"),
        # ! A HEREDOC CROSSES LINES BY DEFINITION. Declared so a file holding
        # one is refused rather than having a line inside it stripped as a
        # comment.
        spanning_quotes=("<<~", "<<-"),
        quotes=('"', "'"),
    ),
    Language(
        "shell",
        (".sh", ".bash", ".zsh"),
        ("#",),
        declares=("function",),
        # ! A HEREDOC CROSSES LINES, and in shell `<<` is one almost always -- the
        # only other reading is an arithmetic left shift inside `$(( ))`. A `#`
        # line inside a heredoc body is DATA, and reading it as a comment would
        # delete it from both fingerprints. ! `<<<` (herestring) and `<<-` both
        # contain `<<`.
        spanning_quotes=("<<",),
        quotes=('"', "'"),
    ),
    Language(
        "sql",
        (".sql",),
        ("--",),
        (("/*", "*/"),),
        quotes=("'", '"'),
    ),
    Language(
        "lua",
        (".lua",),
        # !! `---` IS LUA'S DOC COMMENT AND THIS ROW DOES NOT SAY SO, which
        # makes every documented declaration read as `undocumented`.
        #
        # ! THE ONE-LINE FIX IS WRONG, AND THE IDENTITY SAID SO. Adding `---` to
        # this field and to `doc_line` turned 0 differing files into 8: LuaLS
        # writes `--- @class` and `--- @field` runs that document NO declaration
        # -- whole type-stub files are nothing else -- and a docstring tied to a
        # declaration that is not there cannot be set back where it was read.
        # ! So `---` is a doc marker AND a standalone type declaration in the
        # same language, which no field here can currently express. Filed in
        # `lexer-and-language-findings`.
        ("--",),
        # ! No opener here begins another -- `--[[` is not in `--[==[` -- so their
        # order decides nothing; each level is listed so it closes on its own closer.
        (("--[==[", "]==]"), ("--[=[", "]=]"), ("--[[", "]]")),
        # ! `local function` is TWO WORDS on purpose: bare `local` opens a
        # variable, so matching it alone would declare every one of them.
        declares=("function", "local function"),
        # ! A LONG STRING `[[ ... ]]` crosses lines. Declared so the file is
        # refused rather than a line inside the literal stripped.
        # !! THE LEVELLED FORMS ARE THE SAME CONSTRUCT. Lua writes `[=[`,
        # `[==[` and so on when the body itself holds brackets, and the comment
        # form takes the level too. Without them `--[==[ ... ]==]` reads as ONE
        # `matter` paragraph whose whole text is `[==[`, with the real prose
        # below it counted as executable code.
        # ! THE LEVEL IS UNBOUNDED AND THIS LIST IS NOT -- it stops at two `=`,
        # which is every level the wild uses. A deeper one is read as it was
        # before this row changed, so the bound costs nothing it was not already
        # costing; it is stated because a silent bound reads as completeness.
        spanning_quotes=("[[", "[=[", "[==["),
        quotes=('"', "'"),
    ),
    # !! TOML AND INI ARE TWO LANGUAGES AND TWO ROWS. They share `#` and
    # nothing else: INI also takes `;`, and TOML's multi-line strings do not
    # exist in INI at all, so one row could not state either language's
    # grammar. A row serving two languages is wrong for at least one.
    Language(
        "toml",
        (".toml",),
        ("#",),
        # ! `"""` and `'''` are TOML's multi-line strings. Nothing reads them:
        # TOML has no `READER_METADATA` entry, so `language_for` answers None and
        # every `.toml` file is refused before this field is consulted.
        spanning_quotes=('"""', "'''"),
        quotes=('"', "'"),
    ),
    # ! `;` is INI's original comment marker and `#` the later convention; both
    # are live, so both are listed. There is no multi-line string in INI.
    Language(
        "ini",
        (".ini", ".cfg"),
        ("#", ";"),
        quotes=(),
    ),
    Language(
        "yaml",
        (".yaml", ".yml"),
        ("#",),
        quotes=('"', "'"),
    ),
)


@dataclass(frozen=True)
class ReaderMetadata:
    """Reader identity, semantic revision and implemented capabilities."""

    reader: str
    revision: str
    capabilities: tuple[str, ...]

    @property
    def tier(self) -> str:
        """Return the coverage tier declared in the reader capabilities.

        The tier is the last entry, so every reader lists its tier last.
        """
        return self.capabilities[-1]


READER_METADATA = MappingProxyType(
    {
        "go": ReaderMetadata("go-lexical", "1", ("comments", "lexical")),
        "c": ReaderMetadata("c-lexical", "1", ("comments", "lexical")),
        "cpp": ReaderMetadata("cpp-lexical", "1", ("comments", "lexical")),
        "java": ReaderMetadata("java-lexical", "1", ("comments", "lexical")),
        "csharp": ReaderMetadata("csharp-lexical", "1", ("comments", "lexical")),
        "swift": ReaderMetadata("swift-lexical", "1", ("comments", "lexical")),
        "kotlin": ReaderMetadata("kotlin-lexical", "1", ("comments", "lexical")),
        "javascript": ReaderMetadata(
            "javascript-lexical", "1", ("comments", "lexical")
        ),
        "typescript": ReaderMetadata(
            "typescript-lexical", "1", ("comments", "lexical")
        ),
        "ruby": ReaderMetadata("ruby-lexical", "1", ("comments", "lexical")),
        "shell": ReaderMetadata("shell-lexical", "1", ("comments", "lexical")),
        "sql": ReaderMetadata("sql-lexical", "1", ("comments", "lexical")),
        "lua": ReaderMetadata("lua-lexical", "1", ("comments", "lexical")),
    }
)

INSTALLED_DEFINITIONS = tuple(
    LanguageDefinition(
        language=lang.name,
        suffixes=lang.extensions,
        reader=READER_METADATA[lang.name].reader,
        revision=READER_METADATA[lang.name].revision,
        capabilities=READER_METADATA[lang.name].capabilities,
        defaults={},
        choices={},
        rules={
            field.name: getattr(lang, field.name)
            for field in fields(lang)
            if field.name not in {"name", "extensions"}
        },
    )
    for lang in LANGUAGES
    if lang.name in READER_METADATA
)


def _shipped_definitions() -> tuple[LanguageDefinition, ...]:
    """Every definition file under `references/languages/`, in name order.

    Raises:
        ValueError: a shipped file does not decode; the message names the file.
    """
    folder = files("comment_review").joinpath("references", "languages")
    decoded = []
    for entry in sorted(folder.iterdir(), key=lambda item: item.name):
        if not entry.name.endswith(".toml"):
            continue
        definition = decode_definition(entry.read_text(encoding="utf-8"))
        if isinstance(definition, ReadFailure):
            raise ValueError(f"{entry.name}: {definition.diagnostics[0].message}")
        decoded.append(definition)
    return tuple(decoded)


#: The languages defined by a file of their own, which the lexical rows above
#: do not describe.
SHIPPED_DEFINITIONS = _shipped_definitions()
INSTALLED_REGISTRY = LanguageRegistry((*SHIPPED_DEFINITIONS, *INSTALLED_DEFINITIONS))


def validate_language_definition(
    language_name: str, definition: LanguageDefinition
) -> ReadFailure | None:
    """Require the complete grammar owned by one installed language."""
    installed = INSTALLED_REGISTRY.for_language(language_name)
    reason = ""
    if installed is None or definition.language != language_name:
        reason = "Definition does not belong to this language"
    elif definition.reader != installed.reader:
        reason = "Definition does not belong to this reader"
    elif definition.defaults or definition.choices:
        reason = "This reader implements no settings"
    elif definition.rules.keys() != installed.rules.keys():
        reason = "Grammar must contain exactly the required language keys"
    else:
        for key, value in definition.rules.items():
            expected = installed.rules[key]
            if isinstance(expected, bool):
                valid = type(value) is bool
            elif key == "block_comment":
                valid = isinstance(value, tuple) and all(
                    isinstance(pair, tuple)
                    and len(pair) == 2
                    and all(isinstance(token, str) and token for token in pair)
                    for pair in value
                )
            else:
                valid = isinstance(value, tuple) and all(
                    isinstance(token, str) and token for token in value
                )
            if not valid:
                reason = f"Invalid grammar value for {key}"
                break
    if reason:
        return ReadFailure(
            (ReadDiagnostic(ReadStage.SELECT, "invalid-language-definition", reason),)
        )
    return None


def language_from_definition(definition: LanguageDefinition) -> Language:
    """Materialize validated grammar without supplying missing field defaults.

    Raises:
        ValueError: `definition` fails `validate_language_definition`; the
            message is its first diagnostic.
    """
    failure = validate_language_definition(definition.language, definition)
    if failure is not None:
        raise ValueError(failure.diagnostics[0].message)
    return Language(
        name=definition.language,
        extensions=definition.suffixes,
        **cast(dict[str, Any], dict(definition.rules)),
    )


BY_EXT = MappingProxyType(
    {
        suffix.lower(): language_from_definition(value)
        for value in INSTALLED_DEFINITIONS
        for suffix in value.suffixes
    }
)


def language_for(path: Path) -> Language | None:
    """The lexical grammar for a path, built from its installed row.

    None for a path no row covers: a language defined by its own file, such as
    Python or Rust, and the non-code rows TOML, INI and YAML.
    """
    value = INSTALLED_REGISTRY.for_path(path)
    if value is None or value.language not in READER_METADATA:
        return None
    return language_from_definition(value)


def line_comment_markers(path: Path) -> tuple[str, ...]:
    """The markers that open a line comment in the path's language.

    A lexical row lists them as `line_comment`; Python's definition file states
    its one `marker` under `comments`. Empty when neither does: a language whose
    reader scans its own comments, as Rust's does, is split by that reader.
    """
    lang = language_for(path)
    if lang is not None:
        return lang.line_comment
    value = INSTALLED_REGISTRY.for_path(path)
    comments = value.rules.get("comments") if value is not None else None
    if not isinstance(comments, Mapping):
        return ()
    marker = comments.get("marker")
    return (marker,) if isinstance(marker, str) and marker else ()


def documents_in_literals(path: Path) -> bool:
    """Whether the path's language documents in the first statement of a body.

    That documentation is a string literal, not a comment, and its definition
    states the position as `first-statement` -- as Python's does.
    """
    value = INSTALLED_REGISTRY.for_path(path)
    if value is None:
        return False
    documentation = value.rules.get("documentation")
    return (
        isinstance(documentation, Mapping)
        and documentation.get("position") == "first-statement"
    )
