"""THE LANGUAGES: one record per language, and nothing else.

!! A LEAF, AND THE ONLY PLACE POSITIONING IS STATED. Roy, 2026-08-21: *"All
framing about positioning should come from the language and should be only in
either the language definition file, or a reference to the language definition
file in lexer and compositor. The language definition file should be a leaf
separate from everything else and imported only by lexer and compositor."*

!! TWO IMPORTERS, AND `scripts/check_language_leaf.py` HOLDS IT. The LEXER reads
a file into paragraphs and the COMPOSITOR sets a page back into one; they are
the only two modules that touch a file at all, so they are the only two that may
ask a language anything. Everything between them carries what those two state.

! IT CAME OUT OF `lexer.py`, where the rows sat beside the lexing. Nothing about
the split is cosmetic: while they shared a module, four more modules imported the
records through it -- `census`, `desk`, `page` and `prove_unchanged` -- and each
one that holds a `Language` is a place a positioning rule can be written a second
time and drift from the first.

!! ADDING A LANGUAGE IS A ROW, NOT CODE. That is the whole design, and the rows
are DUPLICATED ON PURPOSE where they look shareable. Roy, 2026-08-20: *"don't try
to make the list generic -- that is a failure of the single responsibility
principle. Each language could change on a new version invalidating the list for
all of them."* The `c-family` and `js-family` rows were split for exactly that.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Language:
    """What the LEXICAL tier needs to find prose in a language it only lexes.

    Adding a language is this record -- data, no code.

    Attributes:
        doc_line: line-comment openers that mean DOC rather than ordinary
            comment (Rust `///`, `//!`). Empty when the language marks docs
            some other way.
        doc_block: paragraph openers that mean DOC (`/**`). Same idea.
        doc_is_structural: the doc is a string in a declaration's body (Python)
            or the run above a declaration (Go). Both need structure to decide,
            so this tier reports `comment` and annotates the paragraph.
        quotes: string delimiters, so a marker inside a literal is skipped.
        char_quotes: delimiters that hold exactly ONE character in this
            language -- `'a'`, or one escape. !! IT IS PER LANGUAGE AND CANNOT BE ONE
            RULE: `'x'` is a character in Rust, C, C++, Go, Java, C# and
            Kotlin, and `'a string'` is prose in Python, JS, Ruby, Lua, shell
            and SQL. ! What it buys is that a `'` which does NOT close within a
            character's width is ORDINARY TEXT rather than an open quote --
            which is what a Rust lifetime is. Measured 2026-08-20: `pub fn
            name(&self) -> &'static str { 1 } // the display name` censused
            zero prose paragraphs, because `'static` opened a literal that
            never closed and blanked the comment with the rest of the line.
        spanning_quotes: delimiters whose literal may cross LINES -- a JS
            template literal, a Java text paragraph. ! `_strip_strings` is per-line
            and carries no open-quote state, so a comment marker INSIDE one of
            these reads as a comment; `prove_unchanged` refuses such a file
            rather than proving it. Empty where a language has none.
        declares: the KEYWORDS this language uses to introduce something that
            can carry documentation. !! EMPTY MEANS THE LANGUAGE HAS NO `a`
            SERIES AT ALL -- not "none found in this file". Roy, 2026-08-20:
            *"we need to be able to distinguish `a` foliations for as many
            languages as there are `a` possible foliations. yaml, toml are not
            ones."* A YAML file was given an `a0` it can never fill.
        nests_comments: an opener INSIDE a paragraph comment adds a LAYER, so the
            run closes only when every one of them does. Rust, Swift and Kotlin;
            C, C++, Java, C#, JS, TS, Go and SQL do NOT, and there the first
            closer wins. ! Lua nests only through its `--[==[` long-bracket
            form, which is a different opener, so it is False.
        doc_inside: the documentation is the first thing INSIDE the body, not
            the run ABOVE the declaration. Python alone, and it is why Python
            needs a parser where a keyword match is enough elsewhere: `///`
            goes on the declaring line's own line, a docstring goes wherever
            the body starts, which a wrapped signature moves.
    """

    name: str
    extensions: tuple[str, ...]
    line_comment: tuple[str, ...]
    block_comment: tuple[tuple[str, str], ...] = ()
    doc_line: tuple[str, ...] = ()
    doc_block: tuple[str, ...] = ()
    doc_is_structural: bool = False
    quotes: tuple[str, ...] = ('"', "'")
    char_quotes: tuple[str, ...] = ()
    nests_comments: bool = False
    spanning_quotes: tuple[str, ...] = ()
    declares: tuple[str, ...] = ()
    doc_inside: bool = False


# ! Ordering inside a field is significant: openers are matched longest-first,
# so `///` must precede `//` or every Rust doc line loses one slash into the
# prose and the annotations then run over corrupted text.
LANGUAGES: tuple[Language, ...] = (
    Language(
        "python",
        (".py", ".pyi"),
        ("#",),
        declares=("def", "class", "async def"),
        # !! THE DOC IS INSIDE THE BODY, which is why Python is the one
        # language here that needs a parser: `a1`'s prose goes wherever
        # the body starts, and a wrapped signature moves that. Every
        # other language puts the doc on the declaring line's own line.
        doc_inside=True,
        doc_is_structural=True,
        # !! A triple quote spans lines, and Python reaches the LEXICAL
        # path whenever `ast.parse` fails -- syntax newer than the floor,
        # a file mid-edit. Declaring nothing here left the same fail-open
        # that was closed for JS the same day: two files differing only
        # in a `#` line INSIDE a triple-quoted literal fingerprinted
        # identically and the proof reported PROVEN.
        spanning_quotes=('"""', "'''"),
    ),
    Language(
        "rust",
        (".rs",),
        ("///", "//!", "//"),
        (("/*", "*/"),),
        doc_line=("///", "//!"),
        # ! Rust nests its paragraph comments.
        nests_comments=True,
        # !! AND A LIFETIME IS NOT A LITERAL. `&'static str` opens a `'` that
        # never closes, so reading it as a quote blanked the rest of the line --
        # comment included. `char_quotes` is what tells the two apart.
        char_quotes=("'",),
        # ! `pub` opens an item and `let` opens a binding, so one is in and
        # the other is not.
        declares=(
            "pub",
            "fn",
            "struct",
            "enum",
            "trait",
            "impl",
            "mod",
            "type",
            "union",
            "const",
            "static",
            "macro_rules!",
        ),
    ),
    Language(
        "go",
        (".go",),
        ("//",),
        (("/*", "*/"),),
        doc_is_structural=True,
        # ! A rune literal is one character.
        char_quotes=("'",),
        # !! THE BACKTICK IS A STRING DELIMITER AND MUST BE BLANKED. Leaving it
        # out on the ground that a raw string takes no escapes was reasoning
        # about the wrong cost: `return `http://example.com/a`` then censused as
        # a TRAILING COMMENT carrying the URL as prose, the `return` line left
        # `return `http:` and dropped out of `code_lines`, and every `b`/`c`
        # below it renumbered. MEASURED 2026-08-22 on that exact line.
        # ! What the old note got right is that this blanking is imperfect here:
        # `_strip_strings` honours a backslash, and a raw string ending in one
        # (`` `C:\` ``) runs past its closer. That shape is rarer than a URL by
        # a wide margin, and both are subsumed when the reader becomes stateful
        # -- `TODO/python-cannot-read-python.md`.
        quotes=('"', "'", "`"),
        # !! AND IT CROSSES LINES, which is a separate claim with a separate
        # consumer: `prove_unchanged` REFUSES a file holding one rather than
        # trusting a per-line read of it -- MEASURED 2026-08-22 on the same
        # shape in Rust, where a payload edited INSIDE a literal reported
        # PROVEN at exit 0.
        spanning_quotes=("`",),
        # ! `package` is NOT here: Go's package comment IS the file's own
        # documentation, which is `a0`. Listing it gave the same prose two
        # places, `a0` and `a1`.
        declares=("func", "type", "var", "const"),
    ),
    # !! C AND C++ GET NO `a`, AND THAT IS A RULING. Roy, 2026-08-20: *"leave
    # it out because it is ambiguous in every way. Let the agents figure out how
    # to put the b and c paragraphs together correctly."* A C function is
    # introduced by its RETURN TYPE -- `size_t f(void)`, `MyRec f(void)` -- and
    # completing that list would mean knowing every type the program defines.
    # ! A wrong `a` is worse than no `a`: a spurious match renumbers every `a`
    # below it, and a verdict is then invited on something that cannot hold one.
    Language(
        "c",
        (".c", ".h"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        char_quotes=("'",),
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
        # `//` is censused as a comment and deleted from BOTH fingerprints --
        # the fail-open measured on Rust 2026-08-22. The prefix is declared
        # rather than the bare quote because `R"` is distinctive: `LR"`, `u8R"`
        # and `uR"` all contain it, and ordinary C++ strings do not.
        spanning_quotes=('R"',),
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
            # ! JAVA'S SECOND WORD IS THE RECORD'S NAME AND VARIES, so a
            # two-word entry has no fixed pair to match and `record Point(int x)`
            # would stop being found. That is a fact about Java's grammar, not
            # about whether the two-word form is available -- it is, to every
            # row. MEASURED 2026-08-22 by trying it: the real declaration broke.
            #
            # ! SO JAVA NEEDS A DEFINITION OF ITS OWN. Roy, 2026-08-22: *"every
            # language gets all of the definitions necessary to parse it
            # specifically, because anything else is failing the SRP rules."*
            # Filed on `lexer-and-language-findings`; `record` stays here so the
            # real declaration is still found.
            "record",
        ),
        # ! A Java TEXT BLOCK spans lines the same way, and a `//` inside one is
        # not a comment.
        spanning_quotes=('"""',),
    ),
    Language(
        "csharp",
        (".cs",),
        # ! `///` FIRST -- see the note above the table. Listing only `//` cut
        # two of the three slashes and left the third in the prose:
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
        # !! TWO SHAPES CROSS LINES HERE, and only the newer one was declared.
        # `"""` is the C# 11 raw string; `@"..."` is the VERBATIM string and has
        # been in the language since 1.0, so it is the one a real file holds. A
        # `//` inside either is censused as a comment -- the fail-open measured
        # on Rust 2026-08-22. ! `$@"` and `@$"` both contain `@"`.
        spanning_quotes=('"""', '@"'),
    ),
    Language(
        "swift",
        (".swift",),
        # ! `///` FIRST, for the reason C#'s is.
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
        # ! `val` and `var` are left out, for the reason Swift's are.
        declares=(
            "fun",
            "class",
            "interface",
            "object",
            "enum",
            # !! KOTLIN'S SOFT KEYWORDS DECLARE ONLY BEFORE A FIXED SECOND WORD,
            # which is a fact about KOTLIN. `data`, `sealed` and `open` are
            # ordinary identifiers, and `_declares_here` matches the FIRST word
            # -- so `data = load()` minted an `a` place for an assignment.
            # MEASURED 2026-08-22: two lines of plain assignment produced a
            # spurious `a1`.
            #
            # ! A TWO-WORD ENTRY IS MACHINERY THIS FILE OFFERS EVERY ROW, not a
            # technique one language takes from another. What goes IN it comes
            # from the grammar of this language and nowhere else -- Kotlin says
            # `data class` because Kotlin's grammar does; Lua says
            # `local function` because Lua's does. Neither is evidence about the
            # other, and a row that reasoned from a neighbour would be assembling
            # one definition out of two.
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
    ),
    Language(
        "ruby",
        (".rb",),
        ("#",),
        (("=begin", "=end"),),
        doc_is_structural=True,
        declares=("def", "class", "module"),
        # ! A HEREDOC CROSSES LINES BY DEFINITION. Declared so a file holding
        # one is refused rather than having a line inside it stripped as a
        # comment -- see `prove_unchanged`, which refuses on PRESENCE because
        # parity is what a per-line reader cannot compute.
        spanning_quotes=("<<~", "<<-"),
    ),
    # ! A HEREDOC CROSSES LINES, and in shell `<<` is one almost always -- the
    # only other reading is an arithmetic left shift inside `$(( ))`. A `#` line
    # inside a heredoc body is DATA, and reading it as a comment deleted it from
    # both fingerprints; the same fail-open measured on Rust 2026-08-22.
    # ! `<<<` (herestring) and `<<-` both contain `<<`.
    Language(
        "shell",
        (".sh", ".bash", ".zsh"),
        ("#",),
        declares=("function",),
        spanning_quotes=("<<",),
    ),
    Language("sql", (".sql",), ("--",), (("/*", "*/"),)),
    # ! `local function` is TWO WORDS on purpose: bare `local` opens a
    # variable, so matching it alone would declare every one of them.
    Language(
        "lua",
        (".lua",),
        ("--",),
        # ! Longest-first, so `--[==[` is tried before `--[=[` before `--[[`;
        # matched the other way every level loses its `=` into the prose.
        (("--[==[", "]==]"), ("--[=[", "]=]"), ("--[[", "]]")),
        declares=("function", "local function"),
        # ! A LONG STRING `[[ ... ]]` crosses lines. Declared for the same
        # reason as Go's backtick and Ruby's heredoc -- refuse the file rather
        # than strip a line inside the literal.
        # !! THE LEVELLED FORMS ARE THE SAME CONSTRUCT AND WERE MISSING. Lua
        # writes `[=[`, `[==[` and so on when the body itself holds brackets,
        # and the comment form takes the level too. Without them `--[==[ ... ]==]`
        # censused as ONE `matter` paragraph whose whole text was `[==[`, with
        # the real prose below it counted as executable code. MEASURED 2026-08-22.
        # ! THE LEVEL IS UNBOUNDED AND THIS LIST IS NOT -- it stops at two `=`,
        # which is every level the wild uses. A deeper one is read as it was
        # before this row changed, so the bound costs nothing it was not already
        # costing; it is stated because a silent bound reads as completeness.
        spanning_quotes=("[[", "[=[", "[==["),
    ),
    # !! TOML AND INI ARE TWO LANGUAGES AND WERE ONE ROW. They share `#` and
    # nothing else: INI has ALSO always taken `;`, so every semicolon comment in
    # a `.ini` was invisible and counted as executable code -- and TOML's
    # multi-line strings do not exist in INI at all, so the joint row refused
    # `.ini` files for a syntax they cannot hold. MEASURED 2026-08-22.
    # ! Split rather than merged, per the rule the `c-family` and `js-family`
    # rows were split under: *"every language gets all of the definitions
    # necessary to parse it specifically, because anything else is failing the
    # SRP rules."* A row serving two languages is wrong for at least one.
    # ! `"""` and `'''` are TOML's multi-line strings, declared so a file
    # holding one is refused rather than proved through it.
    Language(
        "toml",
        (".toml",),
        ("#",),
        spanning_quotes=('"""', "'''"),
    ),
    # ! `;` is INI's original comment marker and `#` the later convention; both
    # are live, so both are listed. There is no multi-line string in INI.
    Language(
        "ini",
        (".ini", ".cfg"),
        ("#", ";"),
    ),
    Language("yaml", (".yaml", ".yml"), ("#",)),
)

BY_EXT = {ext: lang for lang in LANGUAGES for ext in lang.extensions}

# The ladder is named by the QUESTION each rung answers, not by the library
# that happens to answer it. Only the top rung knows which declaration a paragraph
# belongs to.
TIER_ANSWERS = {
    "tokenized": "paragraphs, annotations, and DOCSTRING anchors",
    "lexical": "paragraphs and annotations only",
}


def language_for(path: Path) -> Language | None:
    """The language record for a path, or None when the suffix is unknown."""
    return BY_EXT.get(path.suffix.lower())


def tier_for(lang: Language) -> str:
    """The highest rung reachable for this language, here and now.

    One definition, read by the dispatcher and by `--languages`, so the listing
    and the run report the same tier.
    """
    return "tokenized" if lang.name == "python" else "lexical"
