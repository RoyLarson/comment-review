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
paragraph retains one comment form. Same-type comments between code lines form
one section, including intervening blank lines. Each `a` place holds one
documentation section, each `b` place one section in its code gap, and each `c`
place one section beside its code line. Blank lines provide formatting within
the section; they supply no code anchor for another address. Line-control
requirements apply to the whole section.

Source layouts that the existing places
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

Declaration facts include the declared identifier and its nesting, where the
reader recognizes a documentable declaration. Referrer discovery consumes those
facts for top-level declaration names, replacing its separate Python AST read
while retaining its path-derived search terms.

Full name harvesting remains separately owned. Its current result includes
references, attributes, arguments, aliases and selected string values as well
as declarations; substituting declaration names would lose that coverage.
Reader integration makes unavailable harvesting explicit on source newer than
the runtime grammar. An unavailable result cannot turn a successful lexical
read into a failed page or appear to be a complete empty result.

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
- Same-type comments separated by blank lines remain one section at their
  existing `a`, `b` or `c` place, with line controls applied to the whole section.
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

## Open TODO coverage

The inventory review covered every open task reported by `job-board todo list`
and the corresponding `todo show` results: 168 TODO files containing 930 open
tasks, including work underway and tasks awaiting a decision. The mappings below
identify the relevant tasks; unlisted tasks remain outside this design.

These are proposed scope and closure criteria, not completion claims. A task
closes only after its behavior and completion check have been verified. Several
open tasks describe code that has already moved or been replaced. Establish
their current behavior before attributing a repair to this implementation.
Already-satisfied tasks need reconciliation with their existing evidence.

An old task whose prescribed mechanism or check conflicts with this design
needs supersession through the board, retaining its valid behavioral goal in
a replacement task. Partial coverage needs separate delivered and remaining
goals. This specification changes no TODO status or plan ownership.

### Goals covered by the readers and proof

| TODO tasks | Required result and closure boundary |
| --- | --- |
| [lexical-code-identity](../../../TODO/lexical-code-identity.md) T1, T2 | Both proof boundaries use lexical preservation, agree on docstring additions and removals, and detect literal whitespace changes. This covers all currently open goals in this TODO. |
| [python-cannot-read-python](../../../TODO/python-cannot-read-python.md) T32, T33, T34, T36, T37, T38, T39 | Owned Python reading, discovered docstrings, supported newer syntax on the pinned runtime, exact reconstruction and accurate proof claims. All open goals are covered; the obsolete checks and physical-line promise require the replacements described below. |
| [lexer-and-language-findings](../../../TODO/lexer-and-language-findings.md) T3, T4, T13-T19, T22-T25, T27, T28, T32-T35 | Preserve matter ownership; distinguish shell expansion from comments and contextual keywords from declarations; recognize multiline and dynamic literals; resume scanning in source order; classify and set same-line, inner and outer documentation correctly. Each language case needs an expected-discovery fixture as well as reconstruction. |
| [a-doc-comment-is-cued-a-and-typed-b](../../../TODO/a-doc-comment-is-cued-a-and-typed-b.md) T1-T4 | Placement and the language's documentation rules determine kind and ownership together. Go, Ruby and Lua kinds must agree with their places. Remove expected failures only when the assertions pass. Go and Ruby depend on the adjacency decisions below. |
| [matter-misses-two-languages](../../../TODO/matter-misses-two-languages.md) T2 | An ordinary Rust opening comment remains matter instead of becoming a declaration's documentation. The TypeScript classifier question in this TODO is separate. |
| [block-comment-markers-survive-into-the-prose](../../../TODO/block-comment-markers-survive-into-the-prose.md) T1, T2, T7-T10 | Prose excludes openers, closers and actual continuation markers; form recovery reconstructs them. Invented fixtures cover multiline Javadoc, Ruby and Lua under their own rules. Delimiter removal does not authorize deleting payload characters or relative indentation. |
| [doc-on-the-declaring-line](../../../TODO/doc-on-the-declaring-line.md) T3, T4 | A same-line Python docstring receives the declared documentation place and can be set without losing surrounding code. |
| [closing-line-deletes-code](../../../TODO/closing-line-deletes-code.md) T4, T7, T8 | The proposed resolution is to preserve executable prefixes and suffixes, refusing before writing when the place cannot represent the edit. An invented C fixture demonstrates preservation or refusal. Record the outstanding ruling through the owning task before closing it. |
| [a-comment-inside-a-line-makes-the-file-unprovable](../../../TODO/a-comment-inside-a-line-makes-the-file-unprovable.md) T2, T3, T5, T6 | Source spans distinguish editable comment payload from code on the same line. Changed surrounding code fails proof, and unsupported placement has a named, located diagnostic. The old field and refusal-count prescriptions are superseded below. |
| [bom-is-read-as-source](../../../TODO/bom-is-read-as-source.md) T1, T2; [census-degrades-silently](../../../TODO/census-degrades-silently.md) T7 | BOM-bearing source yields the expected places and retains its original byte representation when unchanged. Replace the obsolete read-site prescriptions with checks at the current I/O boundary; dropping a BOM before computing identity is insufficient. |
| [prove-unchanged-line-endings-follow-a-sibling](../../../TODO/prove-unchanged-line-endings-follow-a-sibling.md) T1, T2 | Compare each file with its own original bytes. A CRLF file beside an LF file must retain its own endings. This covers both open tasks. |
| [the-cue-legend-and-its-round-trip](../../../TODO/the-cue-legend-and-its-round-trip.md) T2-T5 | Reread set output and compare the intended prose at corresponding places, including matter. Detect prose relocated to a neighboring place; demonstrate that disabling the refusal makes the test fail. |
| [the-code-check-refuses-add-and-drop-on-a-docstring](../../../TODO/the-code-check-refuses-add-and-drop-on-a-docstring.md) T4 | Additions and removals of supported documentation comments pass the same preservation contract as Python docstrings. |
| [prove-refuses-a-doc](../../../TODO/prove-refuses-a-doc.md) T4, T5 | Report excluded file categories separately from unsupported programming languages. Neither result is a successful executable proof. The document write-chain work in T2 and T3 remains separate. |

### Adjacent work included

These additions share a representation or integration boundary already being
changed. Their completion remains independently checkable.

| TODO tasks | Why include them and what must become true |
| --- | --- |
| [computed-and-never-read](../../../TODO/computed-and-never-read.md) T6; [page-and-addresser-scans](../../../TODO/page-and-addresser-scans.md) T5 | Produce code regions and declaration facts once per page read and share the result. Do not reconstruct equivalent facts independently for addressing and proof. Other addresser performance tasks remain separate. |
| [name-corpus-sees-one-language](../../../TODO/name-corpus-sees-one-language.md) T1, T5 | Declaration recognition already needs identifiers and nesting. Supply those facts to referrer discovery, preserving path terms and recognized top-level names without a second runtime-parser dependency. This does not complete T2-T4. |
| [galley-and-compositor-write-path](../../../TODO/galley-and-compositor-write-path.md) T5-T10; [no-step-produces-a-page](../../../TODO/no-step-produces-a-page.md) T3 | Share the source acquisition and page-building work used by reconstruction checks. Retain successful empty input as distinct from unreadable input; verify BOMs and line endings at the byte boundary. Supersede old function-location prescriptions where necessary. |
| [only-a-flow-reaches-the-machine](../../../TODO/only-a-flow-reaches-the-machine.md) T3, T4, T10 | Flows obtain source and base revisions; the reader and proof comparison consume supplied values. Complete the affected compositor and proof I/O separation while replacing those consumers. This does not authorize the broader command and concordance I/O sweep. |
| [the-flow-lives-in-the-command](../../../TODO/the-flow-lives-in-the-command.md) T8 | Carry an explicit read failure and its reason through page acquisition to gather. Do not reconstruct failure from an empty page or an exception swallowed by a caller. Reconcile the old return-shape prescription with the shared diagnostic result. |
| [lexer-and-language-findings](../../../TODO/lexer-and-language-findings.md) T6, T8, T9 | Remove obsolete citations and duplicate opener/stamp logic as the old readers are replaced. Current consumers must obtain the same language facts and diagnostics from their shared owner. |
| [fixtures-do-not-test-the-shape](../../../TODO/fixtures-do-not-test-the-shape.md) T2, T3, T5; [assertions-that-gate-a-substring](../../../TODO/assertions-that-gate-a-substring.md) T3, T8 | State what each supported language fixture exercises. Assert full source extents and real declaration recognition, including negative cases. Replace the historical language-count check with the supported programming-language registry. |
| [b-addresser-uninitialised](../../../TODO/b-addresser-uninitialised.md) T16-T18 | Assert that addresses identify the expected anchors, rather than merely existing after a reader change. Use invented fixtures and current address rules. |
| [smoke-fixture-defects](../../../TODO/smoke-fixture-defects.md) T1 | Reconcile wrapped-drop expectations with paragraph rewrapping and run the full command smoke. Treat this as a baseline repair if it already fails before the reader change. |
| [doc-does-not-fill-its-a](../../../TODO/doc-does-not-fill-its-a.md) T6; [census-degrades-silently](../../../TODO/census-degrades-silently.md) T5 | Make the compact reference describe the actual unresolved or unreadable cases produced by the new readers. Remove descriptions of retired fallback behavior. |
| [the-anchor-claims-are-inverted](../../../TODO/the-anchor-claims-are-inverted.md) T1-T4; [docstrings-need-their-own-address-series](../../../TODO/docstrings-need-their-own-address-series.md) T8, T9; [the-cue-legend-was-never-written](../../../TODO/the-cue-legend-was-never-written.md) T1, T2 | Align the affected agent references with the existing four series, their anchors and the declared coverage of each reader. Provide the legend in one maintained location. This does not change admission, review obligations or the policy for requesting absent places. |

### Approaches superseded by this design

The replacement named in each row preserves the useful goal. Retiring an old
implementation mechanism is not evidence that its replacement works.

| TODO tasks | Proposed replacement |
| --- | --- |
| [python-cannot-read-python](../../../TODO/python-cannot-read-python.md) T33, T34, T36, T37 | Replace frozen corpus totals, an external source example and a retired test runner with invented newer-syntax fixtures, current pytest checks and measured reconstruction results. Describe preserved executable content, order and meaningful boundaries; physical line numbers may change with prose. Optional corpus measurements still report their actual population. |
| [lexer-and-language-findings](../../../TODO/lexer-and-language-findings.md) T2, T7, T10, T11, T21, T26, T29 | Replace per-paragraph unterminated stamps with explicit incomplete-read diagnostics; the fixed importer count with shared-leaf boundaries; old scan optimizations and accumulators with the ordered read result; the predicted address-migration history with actual address fixtures; the `inner_doc` field prescription with language-owned relationships; and the empty-Python-result description with the implemented documentation contract. |
| [doc-is-structural-means-two-things](../../../TODO/doc-is-structural-means-two-things.md) T1-T3 | Replace the overloaded flag and old helper documentation with explicit literal/comment form and documentation ownership. A form round trip proves that marker handling still works when documentation is recognized by placement. |
| [language-rows-in-toml](../../../TODO/language-rows-in-toml.md) T1-T5, T12, T13, T15, T16 | Replace a generic two-tier reader and an exhaustive static grammar table with a reader registry and language modules. Static metadata may remain data. Preserve tests for delimiter precedence, explicit capabilities and registry dispatch; remove independent Python suffix lists in the integrated consumers. T14's full name-harvester capability work remains separate. |
| [a-series-never-fills-outside-python](../../../TODO/a-series-never-fills-outside-python.md) T18; [one-stem-four-jobs](../../../TODO/one-stem-four-jobs.md) T2, T3 | Replace keyword-anywhere matching and renaming its table/helper with context-aware declaration recognition. Identifiers inside literals, comments or expressions cannot mint declaration places. This does not add C or C++ declaration places. |
| [lexer-does-not-lex](../../../TODO/lexer-does-not-lex.md) T8-T10 | Retain the term lexer for the actual lexical readers. A blanket module/vocabulary rename to describe the old behavior is unnecessary. Record this proposed naming resolution before retiring the decision task. |
| [a-comment-inside-a-line-makes-the-file-unprovable](../../../TODO/a-comment-inside-a-line-makes-the-file-unprovable.md) T2-T5 | Replace fixed refusal-site counts with current CLI-reachable diagnostic cases, and the paragraph column-field prescription with the shared character-span contract. Corpus frequency is useful measurement but is no longer a prerequisite to preserving code beside comments. |
| [census-degrades-silently](../../../TODO/census-degrades-silently.md) T6 | Replace blanket refusal of same-line documentation additions with correct declared placement, or a specific refusal when that layout cannot be represented. |
| [block-comment-markers-survive-into-the-prose](../../../TODO/block-comment-markers-survive-into-the-prose.md) T3 | Replace synchronization of two named legacy helpers with one form/payload mapping consumed by reading and rendering, verified in the same change. |
| [the-lexer-reads-no-files](../../../TODO/the-lexer-reads-no-files.md) T9-T20 | Replace the proposal to put source acquisition inside the lexer with flow-owned I/O and readers over supplied source. Preserve the byte-identity, BOM and CRLF goals from T17 and T18. Verify end-to-end behavior instead of requiring the old fixed READ and WRITE lists. This does not pull console I/O or every repository read into this effort. |
| [7a-can-prove-the-change-by-applying-it-to-a-copy](../../../TODO/7a-can-prove-the-change-by-applying-it-to-a-copy.md) T5-T7 | Reread edited source to establish its actual lexical boundaries and places. Splice line deltas alone cannot replace that check. |
| [the-code-check-refuses-add-and-drop-on-a-docstring](../../../TODO/the-code-check-refuses-add-and-drop-on-a-docstring.md) T2, T3 | Replace a special failure explanation and separate presence-delta output with normal prose alterations, the presented diff and the unified preservation result. |
| [two-live-runs-proposed-fifteen-changes](../../../TODO/two-live-runs-proposed-fifteen-changes.md) T15 | Replace mandatory parsing after every write with the agreed agent instruction: after successful `prove_unchanged`, run applicable local compilation or syntax validation when available and report it separately. |
| [exception-hierarchy](../../../TODO/exception-hierarchy.md) T4 | Remove obsolete tokenizer-error handling with the tokenizer dependency. Exercise owned-reader diagnostics instead. The general exception-hierarchy redesign remains separate. |

### Decisions exposed by the inventory

The blank-line question in
[a-comment-run-merges-across-blanks](../../../TODO/a-comment-run-merges-across-blanks.md)
T5 is settled by the existing address rule stated in the source contract:
same-type comments between code lines stay together. Its stale decision task
must not be treated as an alternative design choice.

These questions affect expected reader output. They need explicit answers in
the owning tasks before their dependent implementation is finalized.

| TODO tasks | Boundary still to settle |
| --- | --- |
| [doc-does-not-fill-its-a](../../../TODO/doc-does-not-fill-its-a.md) T7, T8 | Go and Ruby documentation adjacency, each considered independently: touching its declaration or allowing intervening blank lines. This determines the expected ownership fixtures. |
| [a-comment-run-merges-across-blanks](../../../TODO/a-comment-run-merges-across-blanks.md) T6; [lexer-and-language-findings](../../../TODO/lexer-and-language-findings.md) T12 | Whether `Paragraph.lines` remains a stored field. Prefer deriving any display count from source spans; settle what the count means before retaining or removing the field. |

The TypeScript doc-shaped header question in
[matter-misses-two-languages](../../../TODO/matter-misses-two-languages.md) T3
and T5 remains assigned to the future prose classifier. Its dependent fixture in
[fixtures-do-not-test-the-shape](../../../TODO/fixtures-do-not-test-the-shape.md)
T1 cannot be counted as fixed by recognizing `/**` correctly. Reader fixtures
must distinguish recognition from the existing header-classification policy.

### Related work that stays separate

| TODO tasks or area | Reason it is not absorbed |
| --- | --- |
| [name-corpus-sees-one-language](../../../TODO/name-corpus-sees-one-language.md) T2-T4; [concordance-gaps-stated-twice](../../../TODO/concordance-gaps-stated-twice.md) | Full identifier harvesting and concordance completeness require a wider consumer contract. Declaration discovery alone cannot establish them. |
| [a-series-never-fills-outside-python](../../../TODO/a-series-never-fills-outside-python.md) T19, T20 | New C and C++ declaration places extend address coverage beyond the retained policy. Correct lexical reading does not imply this extension. |
| [strip-and-fill-the-markers](../../../TODO/strip-and-fill-the-markers.md) | The source contract shares its goals of reversible form handling and preserved payload indentation, but does not decide the proposed agent-visible marker stripping or change the binder's `raw_text` contract. Its mixed tasks need splitting before any partial closure; the whole TODO remains open. |
| [versioning-at-v1](../../../TODO/versioning-at-v1.md) | Reader compatibility addresses the narrower changed-meaning hazard also described by T8 and T9. The TODO explicitly defers its system-wide versioning work until v1; this design does not lift that deferral or claim those tasks complete. |
| [block-comment-markers-survive-into-the-prose](../../../TODO/block-comment-markers-survive-into-the-prose.md) T4-T6; [corpora-are-all-python](../../../TODO/corpora-are-all-python.md); [the-lexer-reads-no-files](../../../TODO/the-lexer-reads-no-files.md) T21, T22 | External corpus acquisition, published population measurements and corrections to an older investigation remain separate. Invented language fixtures are required here; they do not satisfy corpus-measurement tasks. |
| [brief-says-three-series](../../../TODO/brief-says-three-series.md) | Reader documentation must remain consistent with current series semantics. The open questions about what roles may rule on and how matter corrections receive human approval are workflow policy, not lexical classification. |
| [mark-defects](../../../TODO/mark-defects.md); [the-parser-merges-across-boundaries-it-cannot-read](../../../TODO/the-parser-merges-across-boundaries-it-cannot-read.md) | Mark composition, conflicting corrections and prose alignment require their own fixes. Better source spans do not resolve competing edits or establish a mark-merging algorithm. Preserve structured prose in reader/setter fixtures without claiming the composition tasks closed. |
| Remaining middle, dispatch, evidence-input, external-address and review-measurement tasks | They change review workflow or mark handling rather than source recognition. Their existing scope and any explicit deferrals remain in force. |

`lexical-code-identity` T1 and `smoke-fixture-defects` T1 already belong to
`0.2.4-the-middle-rebuilt`; `the-flow-lives-in-the-command` T8 belongs to
`0.2.4-what-a-reviewer-is-handed`. The implementation plan must preserve that
ownership or transfer it through the board rather than schedule a task twice.
The full name-harvesting, matter-approval and middle-stage plans do not become
dependencies merely because this specification mentions them.
