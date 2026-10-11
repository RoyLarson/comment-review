# Lexical readers

## Purpose

Read programming-language source into the existing comment and address system
without depending on the grammar understood by the Python interpreter running
the tool. Identify editable prose accurately, retain the source needed to set
it, and use the same reading rules to prove that prose changes preserve the
executable content at each address and its order.

The current reader loses string state between physical lines and searches for
comments in text that has been separately masked. This can turn literal data
into editable comments. The current executable comparison also removes blank
lines and trailing whitespace that can belong to literals. Language-owned
readers and one source-preserving contract address these failures together.

This document describes the proposed design for review. The implementation plan
will assign the work and its checks to the existing task owners.

## Scope

The programming-language readers cover these existing suffixes:

| Language | Suffixes |
| --- | --- |
| Python | `.py`, `.pyi` |
| Rust | `.rs` |
| Go | `.go` |
| C | `.c`, `.h` |
| C++ | `.cpp`, `.hpp`, `.cc`, `.cxx` |
| Java | `.java` |
| C# | `.cs` |
| Swift | `.swift` |
| Kotlin | `.kt`, `.kts` |
| JavaScript | `.js`, `.jsx`, `.mjs`, `.cjs` |
| TypeScript | `.ts`, `.tsx`, `.mts`, `.cts` |
| Ruby | `.rb` |
| Shell | `.sh`, `.bash`, `.zsh` |
| SQL | `.sql` |
| Lua | `.lua` |

Config and data files, including TOML, INI, YAML, JSON and JSONL, await their own
addressing. The code-reader registry and its advertised coverage will reflect
that boundary. Documents such as Markdown, reStructuredText and plain text also
await their own addressing.

HTML, CSS and standalone templates need their own classifiers and address
systems. JSX and TSX remain part of the programming-language scope. Their
readers recognize transitions between code and markup and preserve markup text
and attributes as protected source. Addressing visible markup prose belongs to
the future markup work.

## Responsibilities

Each language has a module owning its lexical rules, literal forms, comment
forms, contextual distinctions and declaration recognition. Small shared
helpers support source positions, bounded lookahead, delimiter matching and
diagnostics. A common contract lets callers consume each reader consistently.

The reading package owns these contracts and language facts. It supplies the
existing paragraph and declaration machinery with source ranges and placement
facts. The existing addresser continues to assign the `a`, `b`, `c` and `f`
series. Reading and writing consumers use this shared leaf without importing
one another's containers.

Language modules determine which constructs are documentable and where their
documentation belongs. Existing documentable categories remain the starting
point; recognition must distinguish actual declarations from identifiers that
also serve as contextual keywords. Languages currently without declaration
places retain that policy.

Both proof entry points use the same lexical preservation operation. Approval
checking remains the responsibility of `proof` and its alterations.

## Source contract

A reader receives the exact decoded source, the selected language and the
applicable dialect. It returns ordered source regions, declaration and
documentation relationships, and diagnostics.

Source regions cover the input completely, without gaps or overlap. Their
boundaries use half-open character offsets into that exact input. Line and
column coordinates are derived from those offsets. Byte offsets, display
columns and character offsets are kept distinct at I/O boundaries.

The representation retains code, literal payloads, comment forms, whitespace,
line endings and delimiters. Slicing and concatenating its regions reproduces
the input exactly. Empty source is a successful empty read. An incomplete read
has an explicit diagnostic and cannot be used for a successful proof.

Source regions and normalized prose serve different purposes. Decoded prose
maps back to its raw payload spans, including escapes and adjacent literals.
Comment rendering and snippet removal use that mapping and the binder's
`raw_text`. They do not require another copy of the original source to recover
the comment form.

The lexer and addresser establish each paragraph's form and placement. A
paragraph retains one comment form. Source layouts that the existing places
cannot represent receive a placement diagnostic; the reader retains the exact
source and does not combine incompatible forms into one editable paragraph.

Input decoding, newline handling and output encoding preserve the source
contract end to end. Existing encoding support is retained. Unsupported input
encodings produce a read diagnostic instead of replacement characters.

## Language recognition

Recognition follows source order and maintains state across physical lines.
Closing a comment or literal resumes scanning at the next source character,
including when more code or another comment follows on the same line.

Each reader handles its own literal prefixes, escaping, dynamic delimiters,
nesting and interpolation. Interpolation expressions receive the language's
code rules while surrounding literal content remains protected. Comments in
embedded expressions receive editable places only where the existing
addressing and setting machinery can represent them accurately.

Coverage includes the following distinguishing cases:

| Reader | Boundaries its fixtures exercise |
| --- | --- |
| Python | Indentation, logical lines, continued headers, string prefixes, adjacent literals, nested interpolation and first statements |
| Rust | Lifetimes, character literals, raw delimiters, multiline strings, nested comments and inner versus outer documentation |
| Go | Interpreted strings, raw strings, runes, package documentation and significant line breaks |
| C | Character and string literals, escaped physical newlines, preprocessing boundaries and comments beside code |
| C++ | C-style forms, raw strings with chosen delimiters and preprocessing boundaries |
| Java | Unicode translation before token recognition, character literals, strings, text blocks and contextual declaration keywords |
| C# | Regular, verbatim, raw and interpolated strings; character literals and documentation comments |
| Swift | Raw and multiline strings, interpolation, regex forms, nested comments and declaration modifiers |
| Kotlin | Regular and raw strings, interpolation, character literals, nested comments and contextual keywords |
| JavaScript | Regex versus division, regex character classes, template expressions, significant line breaks and JSX boundaries |
| TypeScript | JavaScript lexical forms, TypeScript declaration context and TSX boundaries |
| Ruby | Quoted and percent-delimited literals, regex context, interpolation, heredocs and block-comment placement |
| Shell | Quoting, escapes, substitutions, parameter expansion, arithmetic, heredocs and word-context comment recognition |
| SQL | The selected dialect's quoting, escaping, comment nesting, dollar-delimited forms and executable comment forms |
| Lua | Arbitrary long-bracket delimiter levels, short strings, long comments and documentation placement |

Language transformations that precede comment recognition retain mappings to
raw source. In particular, C line continuation and Java Unicode translation
cannot be approximated by searching the original physical lines for markers.
The language references describe this ordering in
[C initial processing](https://gcc.gnu.org/onlinedocs/cpp/Initial-processing.html)
and [Java lexical translations](https://docs.oracle.com/javase/specs/jls/se20/html/jls-3.html#jls-3.2).

Each reader's supported syntax is documented and demonstrated by fixtures.
Independence from the running Python version means that supported newer source
syntax can be read on the pinned runtime; it does not claim knowledge of future
grammar changes.

## Dialects

SQL uses the dialect declared by the project. When the project does not
identify it, the run accepts an explicit dialect setting. Conflicting or
unsupported declarations produce a diagnostic requiring a supported selection.
There is no silent choice based on whichever interpretation finds a comment.

The task agent resolves the project declaration into the reader's explicit
dialect input. The reader operates on that input rather than searching project
files or querying a database. The selected dialect and lexical modes that
affect recognition travel with the saved page context, so gathering, setting
and proof use the same rules. Mixed-dialect projects select them per file.

Shell suffixes and interpreter declarations inform the shell dialect. Where
they leave a boundary ambiguous, project context supplies the selection.
Dialect implementations share scanning mechanics where appropriate while
retaining their own grammar decisions.

## Python documentation

Python source reading uses an owned scanner and enough structural recognition
to locate declarations, headers, suites and first statements. Neither source
reading, docstring reconstruction nor executable proof depends on runtime AST
or tokenizer parsing.

A documentation string is identified by its statement shape and placement.
The reader distinguishes it from assigned strings, later string expressions,
byte strings and interpolated strings. It handles decorators, asynchronous
definitions, multiline signatures, nested declarations, same-line suites,
parenthesized strings and adjacent literal concatenation.

Adding, changing or removing a docstring is a prose alteration. The reader
reestablishes documentation ownership after setting, and proof retains every
ordinary literal that existed before the edit. Removing a docstring therefore
cannot silently authorize changing a following string that becomes the new
first statement.

Setting retains executable prefixes and suffixes beside a docstring. Supported
same-line documentation can move to its declared documentation position using
the existing placement rule. The comparison admits that specific placement
while retaining the other tokens, their order and their structural context.

Removing a sole documentation statement does not authorize inventing an
executable replacement statement. Local compilation or syntax validation is
responsible for checking the resulting program's validity. The reader reports
structural uncertainty wherever it prevents reliable classification.

## Executable preservation

`prove_unchanged` uses the reader and existing address system to compare the
executable content associated with the places before and after the edit. It
preserves executable token spelling and order, literal contents, structural
relationships and meaningful separators. Moving a code operation, changing a
literal or changing a significant boundary fails this comparison.

Physical line numbers can move when prose is inserted or removed. Address
correspondence follows the existing code and declaration places, with the
source context needed to establish that correspondence. Equality of a freshly
assigned ordinal alone is insufficient evidence of unchanged code.

The comparison retains token boundaries where comments separate code. It also
retains the grammatical effect of line terminators, including line terminators
inside comments. Adding a line break while wrapping a JavaScript block comment,
for example, must not change how the surrounding operation is parsed.
The [ECMAScript comment rules](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html#sec-comments)
give these line terminators grammatical significance.

Literal whitespace remains part of the executable comparison. Normalized prose,
trimmed code lines and a concatenation of characters left after deleting
comments are insufficient representations for this check.

Language-recognized directives expressed as comments retain their protected
meaning and placement. Executable SQL comments, compilation directives and
encoding declarations cannot be edited as ordinary prose without the proof
detecting the change. Mixed prose and directive comments need explicit payload
boundaries where a language supports them.

`proof` verifies the exact approved alterations and uses this preservation
check. `prove_unchanged` independently checks executable preservation, including
the same treatment of docstring additions and removals. It does not require an
approval record. Both commands agree on preservation for the same source pair
and reading context.

## Formatting and local validation

Prose-only proof precedes formatting. Formatting happens before presentation.
The evidence from a proof applies to the exact text checked; a later formatter
result is a separate output and does not inherit an unchanged-code claim.
The final presented diff includes any formatting changes.

The skill and agent documentation will carry this instruction:

> After `prove_unchanged` succeeds, check whether the project's local tools
> support compilation or syntax validation. If available, run the applicable
> check on the edited result and report the outcome.

The agents decide which local tools apply and whether they can run them.
Compilation or syntax validation is an agent action following lexical proof,
not a new program-enforced gate. The two results are reported separately:
lexical preservation establishes unchanged executable content and order;
local validation establishes what the selected project tools checked.

The write-stage instructions currently place compilation before
`prove_unchanged`. Their ordering and completion claims need to follow the
instruction above, together with the skill and the applicable agent references.

## Diagnostics and saved artifacts

Diagnostics identify the language, source location and the boundary or context
the reader could not establish. Unterminated literals, comments and embedded
contexts remain visible in the read result. A refusal preserves the source and
does not produce a successful proof from partial regions.

Reader compatibility is distinct from source identity and serialization format.
A source hash can remain unchanged while corrected recognition changes its
places. Saved review artifacts carry the reading compatibility identity and
the language settings required to interpret those places consistently.

Gathering records that context, and distribution, folding, drafting and resumed
runs preserve it. Admission refuses incompatible reading contexts before using
saved addresses. Older artifacts without a compatible identity require
regathering for the rebuilt reader; their originating tool version can still
read them under its own rules.

## Integration

The registry selects a reader and advertises its actual coverage. Page reading,
comment-form recovery, declaration placement, compositor rereading and both
executable comparisons consume the shared results. The per-line masking path
and delimiter-presence refusals are replaced as the corresponding readers
become complete.

Name harvesting and referrer discovery have separate consumers of Python AST
parsing. Their existing work remains separately owned. Reader integration must
make their availability explicit on source newer than the runtime grammar;
their inability to parse must not turn a successful lexical read into a failed
page or silently represent an unavailable result as a complete empty result.

Operational instructions describe only the task, inputs, tools and checks the
agents need. Internal design documents, plans and investigation history remain
development material.

## Verification

Invented fixtures establish expected discovery as well as reconstruction.
An unchanged round trip alone cannot detect prose the reader failed to find.
Each language's fixtures exercise its claimed forms and difficult boundaries.

The shared checks demonstrate:

- Complete, ordered source coverage and exact reconstruction, including mixed
  endings, missing final newlines, non-ASCII text and literal whitespace.
- Expected prose, forms, declaration relationships and `a`, `b`, `c`, `f`
  addresses, including empty places and comments beside executable source.
- Recognition of real comments after literals and block comments, with markers
  inside literal payloads retained as data.
- Successful add, rewrite, drop and move of supported prose, followed by
  rereading at the intended places.
- Refusal of executable-token changes, moved operations, changed literal
  contents, altered directives and changed significant separators.
- Consistent preservation results from `proof` and `prove_unchanged` for
  equivalent source pairs, with approval independently checked by `proof`.
- Accurate handling of adjacent docstring literals, executable suffixes,
  documentation ownership changes and same-line documentation placement.
- Useful diagnostics for incomplete or unsupported recognition and incompatible
  saved reading contexts.
- Supported Python syntax newer than the pinned runtime, exercised through
  gather, setting and proof without runtime AST or tokenizer dependence.
- Dialect selection retained across saved runs and applied consistently by
  both proof entry points.
- Agent instructions placing available local compilation or syntax validation
  after `prove_unchanged`, with its result reported separately.

Existing addressing and setting tests continue to cover the shared contract.
Language-specific expected results and mutation checks provide independent
evidence alongside the common reader invariants.
