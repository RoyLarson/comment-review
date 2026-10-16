# Python lexical reader

Boundary scanning and classification are separate passes. The implementation
plan supersedes earlier tasks where they combine those responsibilities.

## Purpose and scope

Read maintained Python source, expose its editable comments and docstrings at
the existing places, and prove that approved prose edits preserve executable
content and order. The implementation runs on Python 3.11 with the standard
library. Reading, documentation reconstruction and preservation comparison use
project-owned recognition, independently of the host's AST and tokenizer.
The reader classifies source for the existing addresser and writer. Code text
is retained as source; it is not interpreted into identifiers or operations.

This is the Python-specific specification under the shared
[lexical-reader design](2026-10-11-lexical-readers-design.md). It covers the
Python reader and its complete gather, set, reread and proof workflow.
The implementation branch is `feat/lexer-python`.

The proposed syntax baseline is the published Python 3.15 language reference,
with fixtures spanning Python 3.11 through 3.15. This is a source-reading
baseline, not a target-interpreter compatibility checker. The scanner recognizes
supported newer constructs when hosted on 3.11. Local project validation checks
whether the edited program is valid for its intended interpreter.

Python owns `src/comment_review/references/languages/python.toml` and procedural
recognition in `src/comment_review/reading/python/`. Its definition supplies
suffixes `.py` and `.pyi`, literal forms, comment/directive recognition,
declaration rules, documentation rules and explicit capabilities. It inherits
no grammar or defaults from another language. Initial effective settings are
empty: the documented baseline has one interpretation. Version selection is
not advertised unless the implementation actually provides distinct modes.

## Approach and responsibilities

First scan the source for character boundaries between code and comments on
each physical line. Preserve the exact source and the start and end of each
span. Quoting, escapes, interpolation and comments retain state only where
needed to locate those boundaries, including across lines. Literal form stays
available for the subsequent documentation check. Indentation and declaration
keywords are read afterward, during classification.

Then classify the spans using Python's documentation markers and their placement
relative to module, class, def and async def source. Documentation receives A
classification first. An ordinary comment after code on its physical line is C;
comment-only lines between code are B. Existing F and D rules remain in force.
Group same-form comments between code boundaries as one section, including
intervening blank lines, and hand the result to the existing addresser.

The classifier reads any needed indentation from the preserved source. Code
such as if~ready:, case-1: and except*ValueError: remains opaque throughout this
work. Classification uses source placement and documentation cues. Compiler
validation belongs to the project's local tools.

Reuse `SourceStructure`, `SourceSpan`, `SourceDeclaration`, `SourceSection`,
`DocumentationOwner` and explicit `ReadFailure` outcomes. Character offsets
remain half-open offsets into the exact decoded source. Regions cover every
character once, in order; reconstruction is identical to the input.

The scan result supplies exact source regions and literal/comment forms.
Classification supplies documentation positions and sections. Reuse the
existing paragraph and declaration-position
interfaces. A declaration needs its source position and documentation position,
not its name, an enclosing-symbol relationship or a statement tree. Internal
scanner state remains inside the reader rather than becoming fields on Page.

Remove numeric validation, general identifier classification, clause-chain
validation and the retained statement/suite model. Remove decoded-character
maps whose purpose was the rejected Python renderer. Keep prose extraction
needed to carry editable prose separately from original raw text.

Flows acquire source and select the installed definition. Reading owns pure
recognition and interpretation. Existing page/address components consume the
result. Both preservation paths consume the same lexical classification.
The existing writer continues to consume places, anchors and raw_text.
Successful paragraph extraction alone is insufficient evidence for code proof;
the lexical regions must also preserve every code character and boundary.

## Python scanner prototype

Apply the shared scanner construction with Python-owned recognizers and state.
Use the original source directly as the recognition view. Escapes and explicit
line continuations are recognized where Python permits them, retaining their
original ranges. Each iteration consumes source under the active state.

```text
start with a code frame and the cursor at the beginning
while source remains:
    dispatch to the active frame's Python recognizer
    record the consumed source range and its lexical form
    advance the cursor
    apply the requested entry, exit or state change
finish the active states according to their EOF rules
return the recorded source boundaries

classify the preserved source and boundaries in a separate pass
```

Use these state responsibilities:

| State | Recognition and transition |
| --- | --- |
| Code or replacement expression | Recognize a literal opener or hash comment. In a replacement expression, retain delimiter depth to identify its boundary and entry to a format specification. Other code retains its original spelling. |
| Ordinary literal | Retain the quote delimiter and raw/escape mode. Consume escapes according to that mode; only an applicable matching delimiter closes the literal. Hashes are literal content. |
| Interpolated literal text | Recognize the matching quote, doubled literal braces and replacement-field openers using Python's precedence. An opening field enters expression state. Hashes are literal content. |
| Format specification | Recognize nested replacement fields and the enclosing field's closing boundary. Other payload remains part of the literal form. |
| Hash comment | Consume to the physical newline or EOF. Quotes and braces are comment text. At a newline, retain its source range and return to the enclosing state. |

A Python literal entry holds its opening position, quote delimiter, prefix mode
and escape behavior. A replacement entry holds the delimiter context needed to
distinguish expression punctuation from its closing boundary and format entry.
Retain debug/template protection facts required by the preservation contract.
The scanner need not retain operands or compute expression values to make
these boundary decisions.

Implement opener matching from the language's literal prefixes and quote forms.
Overlapping forms, including short and triple quotes, need explicit precedence.
Recognizing a prefix must respect its boundary so letters within an ordinary
code name cannot begin a literal prefix. This is a boundary check rather than
an identifier record returned to consumers.

Documentation classification consumes the resulting literal and comment ranges
and reads placement cues from the preserved source. It recognizes the complete
docstring
expression, assigns its section, and includes a trailing closing-line comment
in that same section. It then supplies the existing paragraph fields and
documentation positions. The addresser receives every remaining code portion
of each line as its anchor source.

The three-hash fixture below exercises entry into an expression and return to
literal text. Its companion fixtures exercise escape precedence, nested states
and return to ordinary code. The closing-line fixtures exercise the separate
section-ownership step through the existing writer.

## Lexical boundaries

The scanner carries its state across physical lines and resumes immediately
after each closing delimiter. It retains code spelling without assigning names,
numbers or operators their own semantic records. Literal spelling, whitespace
and internal blank lines remain part of code. Delimiter recognition is scanning
state, not a request to parse or validate the enclosed expression.

Recognize short and triple-quoted literals, legal prefix combinations,
raw escaping, escaped quotes, escaped physical newlines, and adjacent literals.
String-like payloads containing comment markers remain literal data. Include
empty literals, delimiters ending at EOF, and a real comment following a
literal on the same physical line. Literal concatenation is represented by
ordered component spans, not by selecting the first token.

Explicit and implicit continuation, physical versus logical newlines,
indentation transitions, tabs, form feeds, brackets and semicolons establish
documentation positions. Comments and blank-only lines do not consume such a
position. An unresolved boundary that prevents classification produces a
located failure. These boundaries follow Python's
[lexical rules](https://docs.python.org/3.15/reference/lexical_analysis.html).

Read source containing type parameter lists and defaults, `type` statements,
modern interpolation, template strings, unpacking comprehensions and `lazy`
imports. Treat their code as source text; inspect only boundaries needed to
find documentation. Ordinary uses of keyword-like spellings must not create
documentation positions. See [compound statements](https://docs.python.org/3.15/reference/compound_stmts.html)
and [Python 3.15 syntax additions](https://docs.python.org/3.15/whatsnew/3.15.html).

## Interpolation and observable source text

Maintain a stack for literal payload, replacement expressions and format
specifications. Expression scanning follows Python code rules, including nested
literals, quote reuse, comments, conversions and nested replacements. Preserve
the distinction between an expression colon and a format-specification colon.
An apparent closer inside a string or comment cannot close its enclosing field.
Fixtures exercise the nesting guarantees in
[PEP 701](https://peps.python.org/pep-0701/).

### Literal and expression hash fixture

Use this invented Python 3.12-or-newer source to demonstrate why the scanner
retains literal and expression state across physical lines:

```python
message = f"""# This is literal output.
Total: {
    subtotal + tax  # This is a comment.
}
# This is also literal output.
"""
```

The first and last hashes belong to literal content and remain code. Only the
middle hash opens a comment, ending at the newline. The closing brace returns
the scanner to literal content; the closing triple quote returns it to ordinary
code. Retain the expression source without interpreting its operations.

The fixture asserts the exact comment range and all retained source ranges.
Their concatenation must equal the input. A line-by-line hash search would
incorrectly expose the two literal lines as comments; the assertions must catch
that error. Plan P28 carries this check under the owned-reading goal.

Companion boundary fixtures cover a quoted hash inside the replacement
expression, escaped quotes, doubled literal braces, nested replacement fields,
and braces or quotes inside a real comment. Add a comment after the actual
closing quote to check that ordinary comment recognition resumes there.

Ordinary f-string expressions can contain comments. An editable comment inside
an expression requires an existing place that can represent it and a setter
that preserves the expression boundary. An unrepresentable comment produces a
placement diagnostic; it is not silently omitted from a successful page.

Debug f-strings retain expression spelling in their output. Template-string
interpolations expose their expression text, including whitespace. Consequently,
the preservation contract protects the corresponding raw expression spans,
including comments within them. Such comments remain recognized source regions
but are protected from prose alteration. A comment edit there must be refused
as a change to observable content. Nested protected spans remain protected even
when they contain otherwise editable expressions. This policy follows the
[debug-expression rule](https://peps.python.org/pep-0701/#handling-of-f-string-debug-expressions)
and [template expression attribute](https://docs.python.org/3.15/library/string.templatelib.html#string.templatelib.Interpolation.expression).

Template strings remain executable literals and cannot become docstrings.
Their literal components, expressions and formatting information are preserved;
the reader never evaluates them. See [PEP 750](https://peps.python.org/pep-0750/).

## Declarations and documentation

Locate module, class, function and asynchronous-function documentation positions.
Keep decorators, nested declaration headers, annotations, defaults and type
parameters as complete code text. Quote and delimiter state distinguishes the
header-ending colon from a colon inside an expression. Track source depth and
whether a documentation position has been consumed; do not build a model of
control flow or validate which clauses may follow each other. Type aliases
and lambdas do not create declaration places under the existing address rules.

A docstring is a plain string expression in the first statement position of
the module or a documentable declaration's suite. Parentheses and adjacent
plain string literals may form that expression. A comma, operator, assignment,
call, byte literal, formatted literal or template literal prevents that shape
from being treated as a docstring. Later string expressions remain protected
ordinary literals. First statements in control-flow suites do not become module
docstrings. The attachment rule follows the
[Python documentation rule](https://docs.python.org/3.15/reference/compound_stmts.html#function-definitions).

Recognize the complete documentation form, including adjacent literal
components and parenthesized forms. Keep surrounding executable prefixes,
suffixes and separators as code. Return the original raw text in the existing
paragraph representation expected by the writer. Prose extraction may decode
supported documentation escapes with project-owned literal handling; do not
call `ast.literal_eval`, `eval` or `compile` to obtain prose. Preserve
unrecognized escapes according to the declared grammar.
Unicode-name lookup may use standard-library Unicode data, with that data's
version included in compatibility. An unavailable name receives a located
diagnostic instead of guessed or replaced text. Ordinary code containing
Unicode remains exact source. The reader does not normalize identifiers or
validate them against the host's Unicode identifier tables.

## Sections, directives and addresses

Existing address assignment remains authoritative. A same-type comment section
extends between its surrounding code boundaries and remains whole across blank
lines. Each existing `a`, `b` or `c` place holds its whole section; line controls
apply to that section. Preserve existing `f` matter placement and code anchors.
Interpolation, docstrings and directives cannot justify merging different forms
into one paragraph or creating replacement address series.

Lexical scanning identifies comment and literal forms; positional classification
supplies the existing kinds for A, B, C, D and F. D retains its existing meaning
as leading space rather than an editable prose place. The addresser numbers
the places and attaches them using the existing rules.

An anchor contains every code portion of its physical line, in source order,
including literal delimiters, literal contents, indexing and slicing notation.
Code on both sides of a comment remains code. Identifier names are not extracted
to construct an anchor. A documentation-only line does not become a code anchor
merely because a comment follows it.

Each Paragraph retains its original `raw_text` alongside extracted prose in
`text` and owns serialization of both under those same field names. Page contains
Paragraphs and delegates their serialization; Binder contains Pages. Neither
container duplicates the Paragraph's text fields. The middle edits supplied
prose. Setting obtains the original comment form from the verified source page,
without a second copy of original source in the docket. Changed code ordering
cannot be hidden by freshly matching ordinals.

Protect the shebang, a valid-position source encoding declaration and Python
type comments, including type-ignore directives, and `# noqa` directives.
Preserve their text and
attachment to source. Protection does not change a comment into code or remove
its raw text from the existing place representation. In particular, a shebang
at the file's head must keep its established F placement and must not add a C
code trigger. Where a directive and prose cannot be separated reliably, protect
the whole directive comment. Other comment text continues through ordinary
section classification; this specification does not claim to recognize every
external tool's directives.

Retain the existing exact source I/O and supported encoding policy. A source
cookie inconsistent with that decoding policy produces an explicit refusal;
the reader must not reinterpret already-decoded text using another encoding.
Shebangs and cookies must remain in their effective positions after setting.

## Prose through the middle and Python forms at setting

Follow the [comment-operation contract](2026-10-15-series-comment-operations-design.md).
The reader supplies Python documentation prose and its original raw source as
distinct values. Paragraph and edit-copy serialization retain that distinction.
Marks, moves, answer rewrites and chief rulings operate on prose. A move removes
its sentence before resolution, and its destination proposal supplies the whole
resulting prose. Intermediate prose is not parsed as a Python literal or flowed
into a comment.

When setting the docket, the flow constructs Python's formatting operations
from the acquired compatible definition and selects them by Series. They receive
approved prose and the original form identified on the verified source page.
They prepare source-formatted paragraph text for the existing galley and
compositor. The middle receives no language definition, scanner state or
formatting callable.

Reuse owned literal boundary and decoding rules when extracting prose and
rereading drafts. Python's setting operation supplies quoting, escaping and
wrapping, including plain/raw and adjacent literal forms. Preserve the complete
prose from a docstring and its immediately following closing-line comment in
their single documentation section. Neither portion may be silently lost.
The closing-line comment remains a hash comment outside the docstring, on its
closing line. In `"""Explain the cache."""  # noqa: D400`, a prose rewrite changes
the documentation while retaining `# noqa: D400` as a comment with the same
effective attachment. It must not become docstring content. Directive text is
protected from prose rewriting and reflow. Rewriting, moving or deleting this
section must preserve the directive and its attachment or refuse setting.
No decoded-character mapping is needed in the middle to subtract prose, and
none is added to Page or the documentation payload for that purpose.

Follow the shared specification's explicit field and artifact compatibility
changes. Saved-review resumes retain prose, while proof setting reconstructs
the formatting operations after context admission. Reading, setting and
rereading use owned Python rules without host AST, tokenizer or evaluation
calls. The existing absent/ambiguous-match and atomic-move rules remain in force.

## Setting and preservation

Reread every draft under its saved compatible Python context. Keep the existing
writer's output contract and established layout normalization. Reader source
regions reconstruct the input exactly; that fact does not promise that the
writer preserves mixed line endings, since it uses its existing newline policy.
Edited prose must appear at its intended place. Code before or after
documentation on the same line remains present and ordered. Test BOM and absent
final newline through the real workflow, without adding a second writing route.

Alterations hold approved prose or an explicit deletion. At proof setting, the
language operation prepares raw paragraph text before the existing galley and
compositor place it. This extends their input preparation without introducing
a separate source-span writer or Python-specific file-setting route. Prepared
paragraphs must meet their field contracts for raw line coverage, anchors,
indentation and documentation insertion positions. Test through the real writer.

Rereading compares extracted prose at the intended address with the alteration,
rather than comparing the alteration's prose to raw source lines. Any exact
raw-layout check uses the prepared setting result. Both prose agreement and
the independent executable-code comparison must pass.

Adjacent documentation literals must expose their complete prose. Preserve the
existing ordered-word move matching and absent/ambiguous-match refusals. Code
and comments following a documentation literal remain distinguishable, while
the raw representation retains what the existing writer requires to reproduce
the physical source. If an existing representation cannot express a supported
layout, report that concrete incompatibility before changing the writer.

The compatibility checks must distinguish two inline cases. A trailing comment
on a docstring's closing line belongs to that docstring's documentation section.
Keep the complete closing line in its raw representation, owned once. The
lexical comment boundary remains recognizable within that section; it does not
create a separate C place. Editing agents receive the combined raw text.

Plan P29 checks both a one-line docstring with a trailing comment and a multiline
docstring with a trailing comment on its closing line. For module and function
documentation, assert one owning documentation section, one copy of the closing
line, and stable placement through the existing writer and reread. A replacement
of the combined prose must retain its intended place and following code.

For `def f(): """Explain."""; return 1`, the older representation preserves the
line but suppresses its code trigger and can attach the docstring at B instead
of its proper place. That is not a successful addressing result. The existing
same-line documentation TODO owns this defect. Before claiming this layout is
supported, demonstrate its classification, complete code anchors, intended
documentation place and output through the unchanged writer together. Whole-line
identity alone does not establish those claims, and restoring the old reader's
field values alone does not finish this case. A failed demonstration remains
open; it does not authorize changing the writer or silently excluding the shape.

Both `proof` and `prove_unchanged` compare the code associated with the existing
places, using lexical regions to retain literal spelling/content, significant
separators, indentation and protected source. Compare code characters and their
order without decoding operations, names or a statement tree. Removing comments
must not join formerly separate code fragments. Whitespace inside literals
remains exact code. Any permitted spacing treatment must be explicit and must
not conceal a changed code boundary. `proof` additionally checks approval and
the intended alterations; standalone preservation needs no approval record.

Match source positions through unchanged code context before admitting docstring
addition, removal or the existing allowed same-line relocation. Preserve every
ordinary literal from the original source. In particular, removing a docstring
must not permit editing the following string merely because it becomes first.
An added docstring must not hide a preexisting ordinary string from comparison.
Refuse ambiguous correspondence. A blank line or space within an ordinary
literal remains executable data.

Removing a sole docstring does not authorize insertion of `pass` or another
executable statement. Lexical preservation and compilation remain distinct.
Report uncertain ownership as a read failure, and otherwise apply the approved
separate local validation requirement. Comment formation occurs while setting
the draft that is proved. Later whole-source formatting follows prose-only
proof; its output is presented with its own diff and does not inherit proof
of unchanged executable spelling.

## Compatibility, diagnostics and integration

Changing the Python implementation or definition changes its compatibility
identity. The new binding must cease depending on the host Python parser
version. Any remaining runtime data dependency, such as Unicode-name decoding,
is explicit and limited to the data actually used. Other language contexts
remain independent. Older Python review artifacts require regathering when
their recorded interpretation differs.

Unterminated literals, unfinished replacement fields, unresolved continuation
and uncertain documentation positions return diagnostics with source spans
where they prevent reliable classification. A partial read cannot produce a
successful page or proof. Ordinary code is not rejected merely because a number,
identifier or clause sequence would fail compilation. The local tools own that
check. Preserve the existing input-decoding policy and source-NUL refusal.

Python gathering, documentation placement, draft rereading and both comparisons
consume the lexical classification through the existing interfaces. Remove
the Page dependency on a Python-specific statement/suite/name model. Referrer
discovery and identifier harvesting remain separate from the lexer; their needs
do not add names or symbol relationships to its result. Remove the proposed
referrer migration from this implementation scope. A referrer limitation must
not turn a successfully classified page into an empty or failed lexical read.

Other languages keep their existing readers until their own subplans. Each
language needs compatible prose extraction and setting adapters before accepting
the new prose artifact contract. Shared adapters must preserve its content,
placement and proof guarantees. No runtime
dependencies, generated plugin refresh or release are part of this work.
Operational agent instructions receive only task-facing commands and checks;
internal design material stays outside their execution inputs.

## Acceptance evidence

Invented fixtures independently state expected regions, prose, owners, forms,
addresses and executable boundaries. Reconstruction alone does not demonstrate
that comments were discovered. Core fixtures run on the pinned Python 3.11
runtime and never require it to compile newer syntax.

| Fixture group | Required evidence |
| --- | --- |
| Exact source | Empty input, BOM, CRLF/LF/CR, mixed endings, Unicode and missing final newline reconstruct exactly |
| Literals | Multiline strings, raw endings, escaped delimiters, prefix combinations and markers inside payloads remain protected |
| Modern syntax | Type parameters/defaults, soft keywords, modern f-strings, t-strings, lazy imports and unpacking comprehensions read on 3.11 |
| Interpolation | Nested expressions and format fields close correctly; debug and template source-text changes fail proof |
| Placement | Module/class/async/function documentation positions, decorators, same-line bodies and nested source receive independently expected places |
| Concatenation | Parenthesized adjacent doc literals yield complete prose in the existing raw representation; tuples and computed expressions remain code |
| Sections | Same-type comments across blanks stay whole at existing places, with line controls covering the complete section |
| Directives | Text or attachment changes refuse; lookalike text inside literals is ordinary literal data |
| Alterations | Add, rewrite, drop and move reread at the intended places while retaining executable prefixes/suffixes |
| Reader compatibility | Protected shebang retains F placement; docstring-closing comments do not duplicate lines; inline documentation keeps its code trigger and correct place |
| Anchors | Every code fragment on a line, including string and slicing syntax, remains in its anchor with no identifier interpretation |
| Boundary scope | Opaque code with invalid numeric spelling or clause order still permits certain comment classification; an unclosed quote that makes classification uncertain refuses |
| Preservation | Code/order/indentation/separator/literal mutations fail; approved prose changes pass both comparison paths |
| Ownership changes | Removing the first docstring cannot authorize changing a promoted ordinary string; inserted docs cannot hide existing literals |
| Failures | Truncated or uncertain input yields located diagnostics, no successful partial proof and no modified originals |
| Saved workflow | Gather, distribute, mark, collate, saved resume, docket and drafting preserve context and original identities |
| Prose contract | Paragraph owns serialization of raw source and prose; Page contains Paragraphs and Binder contains Pages; moves and rewrites compose prose without language formatting; alterations are formatted only at setting |
| Setting comparison | Reread prose equals the approved prose at the intended place; quote escaping and wrapping may differ in raw source while executable-code proof remains independent |
| Independence | Real read/proof routes work with AST/tokenizer entry points forbidden; import and dependency gates remain intact |

Targeted tests live in `tests/reading/test_python.py`, with integration cases in
the affected page, wrapping, setter, proof and command suites.
Mutation cases must demonstrate why each proof refusal is necessary.
Where suitable local interpreters exist, separate syntax checks validate newer
fixtures; missing interpreters do not waive the scanner's deterministic tests.
All existing full-suite, lint, format, typing, shipped-syntax and vocabulary
gates remain required.

## Parent-plan completion boundaries

This subplan is intended to complete Python specification/implementation and
Python workflow integration: parent P7, P8 and P37. It supplies Python's part
of P53 and the shared adapters needed for that workflow. Parent P38-P44 and
P53 remain open wherever their claims include other languages or wider work.
The implementation plan must split or supersede mixed claims through job-board
before recording partial completion.

The intended Python goals include `python-cannot-read-python` T38 and T40-T45.
The rejected writer additions are removed under T49. Earlier task IDs that
these replace remain superseded. Python lexical identity belongs to
`lexical-code-identity` T1; literal-whitespace coverage in T2 remains open if
other-language paths still violate it. Documentation-form and inline-comment
goals may close only to the extent their complete claims are demonstrated.
Operational instruction ordering, other language readers, full name harvesting,
external corpus measurements and preexisting setter-output rollback remain in
their owning work.
