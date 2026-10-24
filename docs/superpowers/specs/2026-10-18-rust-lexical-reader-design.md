# Rust lexical reader

## Purpose and scope

Read maintained Rust source, expose its editable comments and documentation at
the existing places, and prove that approved prose edits preserve executable
content and order. The reader runs on Python 3.11 with the standard library.
It classifies source for the existing addresser and writer. Code text is
retained as source; it is not interpreted into identifiers, types or
operations.

This is the Rust-specific specification under the shared
[lexical-reader design](2026-10-11-lexical-readers-design.md). It covers the
Rust reader and its complete gather, set, reread and proof workflow, ending in
a real review run over a Rust crate. The implementation branch is
`feat/lexer-rust`, cut from `feat/lexical-readers` and merged back with no-ff.

The syntax baseline is the current stable
[Rust Reference](https://doc.rust-lang.org/stable/reference/). The reader reads
every edition with the same rules and advertises no edition mode. For valid
source, the edition does not move a comment or literal boundary that this
reader records; editions reserve spellings, which makes formerly valid code
invalid rather than changing where a comment begins. Compiler validation of
the edited crate belongs to the project's own tools, here `cargo check`.

## The boundary of this work

**This is a reading change.** It is made in `src/comment_review/reading/`, in
`src/comment_review/references/languages/rust.toml`, and in tests.

**Anything reaching past `reading/` needs Roy's approval, with a written
justification, before the change is made.** The changes this specification
already expects are listed under *Changes outside reading*, each with its
justification; Roy approved all five on 2026-10-22. A need discovered during implementation that is not on that list stops
the dependent work: name the file, the change, why reading alone cannot
supply it, and ask. The addresser, `cue`, `documentable`, the binder wire, the
edit copies, the master proof, the docket, the galley, the compositor and the
writer are expected to stay unchanged.

## Which places can take documentation

`decision-log.md Addressing: #28` rules that a construct is a documentation
owner, with its own `a` place, exactly when the language's standard
implementation attaches documentation to it. For Rust the standard is the
Reference's attribute rule: an outer doc comment is a `doc` attribute and
"must appear before something that accepts an outer attribute"
([comments](https://doc.rust-lang.org/stable/reference/comments.html)), and
rustdoc is what uses it.

| Owner | Documented by | Notes |
| --- | --- | --- |
| The file's module or crate | `//!`, `/*! */` at the head of the file | The file's `a0` |
| Items: `fn`, `struct`, `enum`, `union`, `trait`, `impl`, `mod`, `type`, `const`, `static`, `extern crate`, `use`, `extern` blocks, `macro_rules!` | `///`, `/** */` before the item | Inline `mod x { //! ... }` documents that module |
| Associated items in `impl` and `trait`; items in `extern` blocks | `///`, `/** */` before the item | |
| Struct and union fields, tuple-struct fields, enum variants, fields of a struct-like variant | `///`, `/** */` before the field or variant | [allowed positions](https://doc.rust-lang.org/stable/reference/attributes.html) |
| Items declared inside a function or block body | `///`, `/** */` before the item | **My call**, below |

Statements, expressions, match arms, function parameters, generic parameters
and macro invocations get no documentation place: the Reference accepts
attributes on several of them, but rustdoc does not use a doc there and rustc
warns with `unused_doc_comments`. Places are numbered in source order under the
existing `a` rules; this work adds no address series.

**My call:** an item declared inside a function or block body is an owner. It
is an item, the compiler accepts its doc without `unused_doc_comments`, and
#28 asks whether the construct is able to take a doc, not whether rustdoc
renders it.

**My call:** an owner gets a place only when its head is the first code on its
line: the code before it ends on an earlier line, measured at the last
character of that code. That covers the second and later members on one line
(`enum Dir { N, S }`), a first member on its parent's header line
(`struct P(i32, i32);`, `struct P { x: i32,`), and any item that follows other
code on its line (`fn a() {} fn b() {}`). The existing writer sets one `a` per
declaring line, from the `(line, insert, above)` positions the read supplies,
and cannot represent two insertions on one line. They remain code in the
anchor.

## How an owner is recognized

Recognition reads tokens the scanner already produced; it never re-reads
characters. It keeps a stack of open `{`, `(` and `[` delimiters, each tagged
with the kind of body it opened:

| Body kind | Opened by | Owners inside it |
| --- | --- | --- |
| item container | the file, `mod x {`, `impl ... {`, `trait ... {`, `extern ... {` | items |
| function or block body | a `fn` body, any other `{` in code | items only; a `let` or expression is not an owner |
| member list | `struct`/`union`/struct-like variant `{`, tuple-struct `(` | fields |
| variant list | `enum ... {` | variants |
| opaque | `macro_rules! x {`, a macro invocation's delimiters, `#[`, other `(` and `[` | none |

An item starts at an optional visibility (`pub`, `pub(crate)`, `pub(super)`,
`pub(self)`, `pub(in path)`), then optional qualifiers in the Reference's
order (`default`, `const`, `async`, `unsafe`, `safe`, `extern` with an optional
ABI string, `auto`), then a keyword from the definition's list. `const` and
`extern` are a qualifier when an item keyword follows them and the keyword
otherwise; `union`, `auto`, `safe`, `default` and `macro_rules` are contextual
and count only where an item can begin, as the Reference states. A field or
variant is the first token of each comma-separated member at the list's own
depth. The tokens between members are never parsed: the reader needs only
where each member begins.

**The declaring line is the head's first line.** `decision-log.md Addressing:
#30`. Each owner has a head: its outer attributes, then the line its keyword
or member opens on. The reader reports the declaration as opening on the
head's first line: its first outer attribute where it has one, its keyword
line otherwise. Everything outside reading consumes that line as it consumes
any above-the-line declaration today: the `a` is set above it, the doc run
directly above it is the `a`, and the `a`'s anchor is that line's code. On an
attributed owner the anchor is the attribute line, such as `#[derive(Debug)]`,
which several places may share; the address identifies the place.

An outer attribute is `#[` to its matching `]`, across lines, with literals
inside it read as literals; `#[derive(...)]`, `#[cfg(...)]`, `#[test]`,
attribute macros and `#[doc = "..."]` are all this one form. The scanner
records each attribute's extent as a token; an unclosed `#[` is a located
read failure. Classification walks up from each owner through the attribute
tokens directly above it, so an attribute on a statement, match arm,
parameter or expression is never visited and stays code. A macro invocation
above an item is an item of its own, not part of the head, and takes no place.

## Recognition and lexical boundaries

The scanner carries state across physical lines and resumes immediately after
each closing delimiter, including when more code or a comment follows on the
same line. It follows Rust's
[tokens](https://doc.rust-lang.org/stable/reference/tokens.html) and
[input format](https://doc.rust-lang.org/stable/reference/input-format.html):
CRLF reads as one line break.

| State | Recognition and transition |
| --- | --- |
| Code | Recognize a comment opener, a string or character opener, a raw-string opener, a lifetime, `#[`/`#![`, and the delimiters `{ } ( ) [ ]`. Other code keeps its spelling. |
| Line comment | To the line break or EOF. `///` and `//!` are documentation; `////` and longer are ordinary. |
| Block comment | Nests: each `/*` inside adds a layer and the comment closes when every layer does. `/**` and `/*!` are documentation; `/***` and `/**/` are ordinary. |
| String | `"..."`, `b"..."`, `c"..."` with backslash escapes, crossing lines freely. An escaped line break is literal content. |
| Raw string | `r"..."`, `r#"..."#` and `br`/`cr` forms; closes only at a quote followed by the same number of `#`. No escapes. |
| Character | `'x'`, `'\n'`, `'\u{10FFFF}'`, `b'x'`. |
| Lifetime | `'a`, `'static`, `'_`, `'r#a`: a quote that does not close as a character and is followed by an identifier is code. |

Comment markers inside any literal are literal data. A raw identifier (`r#fn`)
is one code word. A literal prefix is
recognized only at a token boundary: the character before it is not an
identifier character, so the `r` ending `bar"` cannot open a raw string. An
unterminated block comment, string, raw string or attribute is a located read
failure with its opening span; a partial read never produces a page. NUL in
the source refuses, as it does for Python.

The scan's regions partition the source: each character belongs to exactly
one code, comment or literal region, in order, and their concatenation equals
the input. Each comment region records its form: `line`, `outer-doc-line`,
`inner-doc-line`, `block`, `outer-doc-block` or `inner-doc-block`.

The scan also records each comment's prose: the text inside its markers, one
piece per physical line. A delimited doc's continuation lines are decorated
when every one of them opens, after an indent of one width, with
`[rules.documentation].delimited_decoration`; the indent and decoration are
then not prose. Otherwise all of the line is.

**My call:** isolated CR inside a doc comment, which the Reference forbids, is
not checked; it is the compiler's to refuse.

## Documentation attachment

An outer doc section directly above an owner's head's first line, with only
blank lines between, is that owner's `a`. A doc section with no following
owner (before `}`, before a statement, at EOF) attaches to nothing and is
classified as an ordinary comment section, which is what
`lexer-and-language-findings` T27's check expects.

An inner doc section at the head of a file is the file's `a0`. Rust lets inner
attributes (`#![...]`) and inner doc comments interleave there; the place model
holds only an inner doc that comes before them, and a later one is detached.

An inner doc inside a body -- an inline module, function, impl, trait or block
-- documents no owner (`decision-log.md Addressing: #33`). It is an ordinary
comment at the `b` place its position gives it, or the `c` place when it trails
code, annotated `detached-documentation`, with one warning whose owner is the
innermost item whose body holds it. The owner's `a` stays empty, and under
`#31` the inner doc shares one paragraph with any comment in the same place.
Documentation is held at an `a` only where Rust normally puts it, above the
item, and the roles correct a comment whose kind is ambiguous. Roy expects to
revisit this if another language's reader meets documentation held inside the
body it documents.

**Placement of a doc the run adds.** An added doc lands above the head's first
line, which is above the attributes, per the
[Rust Style Guide](https://doc.rust-lang.org/style-guide/): "Put doc comments
before attributes." It is written as `///` lines ("Prefer line comments (`///`)
to block comments"). An added `a0` is written as `//!` lines and is set where the
page sets `a0`: after the front matter, before the first line of code
(`decision-log.md Addressing: #30`). A file-level inner doc after an inner
attribute cannot be held there and is detached (`#32`), so the module entry of the
declarations the read hands the page carries no position the page reads. Every
other owner inserts at its head's first line; an `add` at the empty `a` of an
owner with a body inner doc sets `///` lines above its head, and the inner doc
stays detached in its body.

**Documentation a place cannot hold.** `decision-log.md Addressing: #29`.
Permitted layouts attach in Rust and are not held by the `a`:

- an outer doc run separated from its head by an ordinary comment;
- an outer doc run between an attribute and the item, or on the head's own line;
- an outer doc run that trails code on its line;
- a second doc run for one owner, the module included;
- every inner doc inside a body (`#33`);
- a file-level inner doc after an inner attribute at the head of the file (an
  inner doc after an item is refused by the compiler, and the reader reads it as
  an ordinary comment with no warning);
- a file-level `//!` behind an ordinary comment that is not front matter.

Each such run is read as an ordinary comment at the place its position gives
it, annotated `detached-documentation`, and the read carries a warning naming
its line and its owner. It is not a read failure. Moving the detached run to
the `a` is an ordinary placement change, which both comparisons pass. Gather
prints one `warning:` line per detached run, so two runs at one place print two
lines; how the warning reaches gather's output is outside reading, see
*Changes outside reading*.

## Sections, directives and addresses

Existing address assignment remains authoritative. A same-form comment section
extends between its surrounding code boundaries and remains whole across blank
lines; the existing `a`, `b`, `c` and `f` rules place it. A place holds one
paragraph (`decision-log.md Addressing: #31`): sections of different forms that
fall in one place make one paragraph there. That paragraph keeps the
`detached-documentation` annotation and its warning when any part of it is
detached. An attached doc has its own `a` place and never shares one, so the
forms never merge into one paragraph where each has a place of its own.

Opening and closing matter follow the same rule as the other readers. The
opening run starts on line 1, or directly below the shebang, and ends at the
first blank line; it is `f0` matter whatever its comment forms, and is not
claimed as a declaration's documentation (`matter-misses-two-languages` T2).
The closing run follows the Python projection's closing rule, whatever the
comment form: the whole-line comments after the last code line, when the last
of them ends on the file's last line, and those after the run's last blank line
are the foot's `f` matter.

An anchor contains every code portion of its physical line, in source order.
Code on both sides of a block comment remains code. A delimited comment
followed on its line by anything other than whitespace is part of that line's
code: it is no section and documents nothing (`docs/addressing.md`, *An
INTERMEDIATE comment is not censused*).

The one protected directive is the
[shebang](https://doc.rust-lang.org/stable/reference/input-format.html#shebang-removal):
`#!` on the first line, unless the next token after it, skipping whitespace
and comments, is `[`, which makes it an inner attribute. The shebang is `f0`
matter, and an opening comment run directly below it joins it at `f0`. It
remains protected source, compared exactly, and adds no code trigger. `#![...]`
and `#[doc = "..."]` are code; their strings are protected literals, not
prose.

**My call:** comments inside a `macro_rules!` body or a macro invocation's
delimiters are read as ordinary comment sections at their `b` and `c` places,
and those bodies create no declaration places.

## The definition file

`src/comment_review/references/languages/rust.toml` holds every Rust fact the
reader uses, and the reader reads its rules from it rather than from
constants. It inherits nothing; where a value matches Python's, it is stated
again.

```toml
format = 1
language = "rust"
suffixes = [".rs"]
reader = "rust-lexical"
revision = "2"
capabilities = ["comments", "strings", "declarations", "documentation", "protected-directives", "lexical"]
defaults = {}
choices = {}

[rules.comments]
line = "//"
outer_doc_line = "///"
inner_doc_line = "//!"
block_comment = ["/*", "*/"]
outer_doc_block = "/**"
inner_doc_block = "/*!"
nests = true
empty_block_comment = "/**/"

[rules.literals]
string_quote = '"'
string_prefixes = ["b", "c"]
raw_prefixes = ["r", "br", "cr"]
raw_guard = "#"
char_quote = "'"
char_prefixes = ["b"]
escape_marker = '\'
raw_lifetime_prefix = "r#"
raw_identifier_prefix = "r#"

[rules.attributes]
outer_open = "#["
inner_open = "#!["
open = "["
close = "]"

[rules.declarations]
visibility = "pub"
visibility_scopes = ["crate", "super", "self", "in"]
qualifiers = ["default", "const", "async", "unsafe", "safe", "extern", "auto"]
keywords = ["fn", "struct", "enum", "union", "trait", "impl", "mod", "type", "const", "static", "use", "extern", "macro_rules!"]
contextual = ["union", "auto", "safe", "default", "macro_rules!"]
item_containers = ["mod", "impl", "trait", "extern"]
member_lists = ["struct", "union"]
variant_lists = ["enum"]
function_bodies = ["fn"]
associated_containers = ["impl", "trait"]
macro_definitions = ["macro_rules!"]
abi_qualifier = "extern"
macro_marker = "!"
body_open = "{"
generics_open = "<"
generics_close = ">"
arrow = "->"
terminator = ";"
separator = ","

[rules.documentation]
owners = ["module", "item", "associated-item", "field", "variant", "nested-item"]
delimited_decoration = "*"

[rules.directives]
shebang = "#!"
shebang_line = 1
inner_attribute_follows = "["
```

Two constraints are fixed: every value the reader consults is in this file, and
`reading/rust/definition.py`'s `validate_rust` checks the identity and every
rules value by exact comparison and type, as `validate_python` does
(`reading/python/definition.py:10`). The one exception is
`[rules.documentation].owners`, which must be a nonempty list of distinct owner
kinds from the grammar's set, so a definition may narrow which kinds take
documentation. Revision `2` replaces the shared row's
`rust-lexical` revision `1`, so saved Rust reading contexts refuse with
`reading-context-mismatch` and are regathered.

## The reader's modules

`src/comment_review/reading/rust/`, mirroring the final shape of
`reading/python/` (scan, then classify, then project):

| Module | Provides | Built on |
| --- | --- | --- |
| `definition.py` | `validate_rust(definition) -> ReadFailure \| None` | `LanguageDefinition` |
| `records.py` | `RustToken(kind, span)`, `RustScan(text, regions, tokens, prose)`, `RustPlacement(declarations, insertions, detached)`, `DetachedRun(span, owner)`, `RustDocumentation(sections, owners, placement, warnings)`, `RustRead` | `SourceStructure`, `SourceSpan`, `SourceSection`, `SourceDeclaration`, `DocumentationOwner` from `reading/source.py` |
| `scanner.py` | `scan_rust(text, definition) -> RustScan \| ReadFailure`: the state table above | `ReadDiagnostic` at `LEX` |
| `structure.py` | `place_declarations(scan, definition) -> RustPlacement \| ReadFailure`: the body-kind stack, owners, heads, the same-line rule, macro opacity | the scan's tokens only |
| `documentation.py` | `documentation_in(scan, placement, definition)`: attaches doc sections to owners, finds detached runs, the module's `a0` and its insertion line | the scan and placement |
| `directives.py` | `directives_in(scan, definition)`: the shebang | the scan |
| `projection.py` | `sections_for(...) -> RustRead`, `paragraphs_for(path, read)`, `code_for(read)`, `declarations_for(read)` | `Paragraph`, `Kind` |
| `preservation.py` | `compare_preservation(before, after) -> PreservationResult` | `reading/proof.py` |
| `__init__.py` | `read_rust(text, definition) -> RustRead \| ReadFailure` | the above, in order |

`RustRead` holds `source: SourceStructure`, `protected` (the shebang),
`insertions` (the module's, then one per declaration), `warnings:
tuple[ReadDiagnostic, ...]` for detached documentation, at stage `PLACE`, code
`detached-documentation`, with the detached run's span, `detached` (the runs,
each with its owner's declaration index or `None` for the module) and `prose`
(the scan's prose pieces). `warning_owners` gives each warning's owner. It
validates in `__post_init__` as `PythonRead` does: regions partition the text,
one insertion per declaration plus the module, warnings inside the text.

`projection.py` follows the Python projection's contract
(`reading/python/projection.py:107-257`):

- `paragraphs_for` gives an attached doc section `Kind.DOCSTRING` with address
  `a{n}` (`a0` the module), stamped by the reader as Python's are, and gives
  other comment groups `TRAILING`, `COMMENT` or `MATTER` with their anchor and
  raw lines. A detached run is `COMMENT` or `TRAILING` with the
  `detached-documentation` annotation.
- `code_for` gives line number -> the code on that line.
- `declarations_for` gives `(0, 1, True)` for the module, then
  `(head first line, head first line, True)` per owner with a place: every
  declaration's insertion is its anchor line, an owner with a body inner doc
  included (`decision-log.md Addressing: #33`). `above` is `True` for every
  entry: the doc goes above the line, and `documentable`
  (`binder/page.py:568`) handles that side unchanged.

`preservation.py` compares the two reads' code as logical lines with every
prose comment removed and each removal kept as a fragment boundary, so
`a/* x */b` compares as `a`, `b` and never as `ab`. A comment in no section is
code and compares as code. Literal and attribute text compares exactly, and
indentation and the whitespace between code on a line are compared; blank
lines, comment-only lines and the line-break style are not. The shebang is
compared first, as protected source. Codes are the Python
comparison's where they mean the same thing: `code-changed`,
`protected-source-changed`. `RustRead.preserved(after, *, documented=None)`
accepts `documented` and ignores it, as `StrippedRead` does
(`reading/stripped.py:148-179`).

**My call:** every comment, ordinary or documentation, is prose to the
comparison. Unlike a Python docstring, a Rust doc comment holds no executable
token, so an `add` at an empty `a`, a `drop`, and a move from a `b` to an `a`
all pass, as an approved prose change must. A doc left with no owner, such as
one moved before a `}`, is a compile error, and the end-to-end `cargo check`
is what catches it.

Helpers both readers need may move into a shared module under `reading/`
without changing the Python reader's results; the Python suite is the check.
Neither reader imports the other's package.

## Changes inside reading, outside the new package

These are within `reading/` and need no further approval:

| File | Change | Why |
| --- | --- | --- |
| `reading/language.py` | Remove the `"rust"` row from `LANGUAGES` and `READER_METADATA` | `language.py:561` builds `INSTALLED_REGISTRY` directly, and a second `rust` raises `duplicate-language` (`registry.py:54-58`) |
| `reading/language.py` | `line_comment_markers` and the paragraph-comment lookup answer Rust from `rust.toml` | they read the row today (`language.py:651-654`) |
| `reading/lexer.py` | `comment_form` (`:130`, `:203`) answers Rust from the definition | `desk/marks/rules.py:37` calls it to split a mark's comment from its markers; without the row it returns the raw text whole |
| `reading/stripped.py` | No change: a Rust page's read is the `RustRead`, so `StrippedRead` is no longer built for `.rs` | `stripped.py:62` needs `language_for`, which answers `None` once the row goes |
| `reading/readers.py` | A `rust-lexical` `ReaderBinding` with `read_rust`, `validate_rust`, grammar identity `"Rust Reference lexical"`; `SourceReader` and `read_source` return a reader record rather than naming `PythonRead`; `read_paragraphs` asks the record for its paragraphs | `readers.py:34-36`, `:93-102` name `PythonRead` |
| `reading/proof.py` | A `ReaderRecord` `Protocol` beside `SourceRead`: `source`, `paragraphs(path)`, `code()`, `declarations()`, `warnings`, `warning_owners`, plus `SourceRead`'s `proof` and `preserved`. `PythonRead` and `RustRead` both satisfy it | one interface for `page_for` to ask, so no consumer names a reader |

## Changes outside reading -- approved

Each was proposed with its justification. Roy, 2026-10-22: *"All of O1-O5"*.
Anything outside reading not in this table still needs his approval first.

| # | File | Change | Justification |
| --- | --- | --- | --- |
| O1 | `binder/page.py`, `page_for` (`:857-925`) | Replace `isinstance(result, PythonRead)` and the `reading.python.projection` imports (`:69-78`) with the `ReaderRecord` protocol: take the page text, paragraphs, `code()` and `declarations()` from the record, pass `code` to `fill_the_gaps` (`:910`) for any record, and set `read=` to the record (`:923`). The lexical-row branch (`:877-881`) stays for the remaining rows | A Rust record falls into the lexical branch today: its `assert` (`:878`) fails because `language_for(.rs)` is `None`, and `got` is not a list. No change inside reading can make `page_for` accept a second record type. About fifteen lines; no address or wire change |
| O2 | `binder/page.py`, `Page` | Carry the record's `warnings`, each turned into the cue of the paragraph its span falls in, as a `warnings` field not written to the binder wire | `#29` requires a warning. Only the page knows a paragraph's cue, and the binder wire stays `cue, anchor, original_start, original_end, raw_text` (`page.py:83,228-236`) |
| O3 | `flows/gather.py`, `commands/gather.py` | Print each page warning to stderr as `warning: <path>@<cue>: detached documentation for <owner cue>`; the exit code is unchanged | No non-fatal channel exists: `ReadFailure` always fails the file (`diagnostics.py:55`), and gather prints only `unreadable`, unaddressed, `unread` and `no_record` (`commands/gather.py:131-201`) |
| O4 | `src/plugin/skills/comment-review/SKILL.md`, stage 2 | Ask the human about each detached-documentation warning, record the answer, and proceed | `#29`. The `agents` lane owns it: this work files an `agents` TODO and does not edit the file |
| O5 | `references/vocabulary.toml`, `docs/vocabulary.md` | Add `detached documentation` | Shared by no lane; a new term is added on both sides in the same change (`docs/conventions.md`, *The vocabulary is shared*). `detached documentation` is defined in `docs/vocabulary.md`; its move to `vocabulary.toml` is filed in `TODO/stage-two-detached-warnings.md` T2 |

These are checked and need no change: `flows/prove_unchanged.py:120-122` and
`flows/proof_setter.py:695,713` use only `proof` and `preserved`;
`flows/reading_context.py:174` and `flows/page_for.py:54-71` select the reader
through `reader_for`; `commands/gather.py:109` prints `capabilities[-1]`;
`concordance/code_names.py:69-77` and `concordance/referrers.py:54` treat a
non-Python file as having no harvester, unchanged by this work.

## Order of work

Each step ends with its tests green and the full suite green.

1. **Definition and binding.** `rust.toml`, `validate_rust`, the `rust-lexical`
   binding, and the row removed from `language.py`. `comment_form` and
   `line_comment_markers` answer from the definition. Until step 6, `read_rust`
   may return a `ReadFailure` naming the unfinished reader; the check is that
   `INSTALLED_REGISTRY.for_path("x.rs")` is `rust.toml` with reader
   `rust-lexical` and no `rust` row remains.
2. **Scanner.** `scan_rust` and its fixtures: every row of the state table,
   regions partitioning the source, located failures.
3. **Structure.** `place_declarations`: owners by body kind, heads, the
   same-line rule, macro opacity.
4. **Documentation and directives.** Attachment, detached runs and their
   warnings, the module `a0` and its insertion line, the shebang.
5. **Projection and records.** `RustRead`, `paragraphs_for`, `code_for`,
   `declarations_for`, the `ReaderRecord` protocol satisfied by both records.
6. **Page integration.** O1 and O2: `page_for` over a `.rs`
   source gives the expected addresses through `tests/conftest.py:77`'s
   `build(text, name="m.rs")`.
7. **Preservation.** `compare_preservation` and both comparison paths.
8. **Gather warning.** O3; the O4 `agents` TODO filed; O5 made.
9. **End-to-end run**, below.

## Diagnostics and compatibility

Changing the Rust definition or reader changes its compatibility identity
(`reading/context.py:21-52`), and older Rust review artifacts require
regathering. Unterminated comments, literals and attributes return located
diagnostics. Ordinary code is not rejected because it would fail to compile.
The existing input-decoding policy and source-NUL refusal are kept.

## Acceptance evidence

Invented fixtures in `tests/reading/test_rust.py`, staged like
`tests/reading/test_python.py`: a `rust_definition` fixture decoding the
shipped `rust.toml` through `importlib.resources`, helpers that run each stage
on its own, and page-level cases through `tests/conftest.py`'s `build`.
Integration cases go in the affected page, setter, proof and command suites
(`test_page_for`, `test_lexical_preservation`, `test_proof_setter`,
`test_proof_command`, `test_gather_command`, `test_language_definitions`,
`test_reading_context`). Each fixture states its expected regions, prose,
owners, forms, addresses and code independently. No fixture copies code from
another project. Existing Rust cases in `test_comment_wrapping`,
`test_compositor`, `test_reading` and `test_language_definitions` are kept
passing, or superseded case by case where they assert the old row's behavior.

| Fixture group | Required evidence |
| --- | --- |
| Exact source | Empty input, BOM, CRLF and LF, missing final newline reconstruct exactly |
| Comments | Nested `/* /* */ */`; `////` and `/***` and `/**/` ordinary; `//!` and `/*!` inner; a comment after a closing delimiter on the same line |
| Literals | Strings across lines, escaped quotes, raw strings with zero and several `#`, byte and C strings, markers inside every literal kind, `bar"` not opening a raw string |
| Quotes | `'a'`, `'\u{10FFFF}'`, `b'x'` against `'a`, `'static`, `'_`, `'r#a`; an apostrophe inside a string; a trailing comment after each |
| Owners | Every owner in the table gets its place; statements, match arms, parameters and macro invocations get none; same-line members get none; `const fn` and `const X`, `extern crate`, `extern "C" fn` and `extern "C" {` each resolve once |
| Heads | Single and multi-line attributes, attributes holding strings with `]`, and an attribute on the item's own line give the head's first line; attributes on a `let`, a match arm and a parameter create no place; an unclosed `#[` refuses with a location |
| Attachment | Doc above multi-line attributes and across blank lines attaches; a doc before `}` or EOF is an ordinary comment |
| Placement | An added doc sets above the first attribute as `///`; an added `a0` sets after the shebang and matter as `//!` |
| Detached docs | A doc behind an ordinary comment, a doc between attribute and item, a second doc run, an inner doc inside a body (`#33`), and a file-level `//!` behind an ordinary comment that is not front matter read as annotated ordinary comments with a warning and exit 0; gather prints one `warning:` line per run, two lines for two runs at one place; sections of different forms in one place make one paragraph that keeps the annotation; moving one to the `a` passes both comparisons |
| Matter | An opening `// Copyright` run is `f0` matter with an empty `a1`; a closing run follows the Python closing rule whatever its form; a delimited comment followed by code on its line is code |
| Directives | The shebang is `f0` matter and an opening run directly below it joins it; `#![` at the head is code |
| Macros | `fn` inside a `macro_rules!` body creates no place |
| Preservation | Code, order, literal, attribute and separator mutations fail; joining fragments fails; prose changes, doc adds, drops and `b`-to-`a` moves pass both comparisons |
| Failures | Unterminated forms give located diagnostics and no partial page |
| Saved workflow | Gather, distribute, collate, docket and drafting preserve the Rust context; `page_of` refuses an old Rust context (revision 1, or the earlier generic lexical row's) with `reading-context-mismatch`; the saved-artifact path refuses it with its "regather" message |
| Independence | The Python suite passes unchanged; neither reader imports the other's package |

**End-to-end run.** On a git worktree of a small edition-2021 binary crate on
this machine, named when the run is made and recorded nowhere in this repo:

1. `git worktree add` the crate's current `HEAD` into the session scratchpad.
2. `cargo check` passes on the unedited worktree.
3. A full `/comment-review` over all of the crate's `src/*.rs`, gather through
   write and stage 8, completes with every file read by `rust-lexical`.
4. `prove_unchanged` against the pre-edit ref exits 0.
5. `cargo check` passes on the written worktree.
6. The worktree is removed by hand, never by a script. The evidence kept here
   is the commands, their exit codes and the counts of places raised and
   written.

All existing full-suite, lint, format, typing, shipped-syntax and vocabulary
gates remain required.

## Parent-plan completion boundaries

This subplan is intended to complete parent P9 and P10, and supplies Rust's
part of P53. It carries the Rust-and-Python share of P38 and P44 named above;
those stay open for the other languages. The intended TODO goals are
`lexer-and-language-findings` T16, T27, T32 and T49,
`matter-misses-two-languages` T2 and `fixtures-do-not-test-the-shape` T2, moved
from the parent with `plan move-t`. Fetching the public Rust corpus
(`corpora-are-all-python` T6) is not in this scope.
