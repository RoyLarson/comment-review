# Python lexical reader

## Purpose and scope

Read maintained Python source, expose its editable comments and docstrings at
the existing places, and prove that approved prose edits preserve executable
content and order. The implementation runs on Python 3.11 with the standard
library. Reading, documentation reconstruction and preservation comparison use
project-owned recognition, independently of the host's AST and tokenizer.

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

Use a stateful scanner followed by a structural recognizer for statements,
headers and suites. Both operate on the same retained source and spans.
The scanner identifies literal, comment, directive, code and whitespace regions;
the structural recognizer identifies documentation ownership and the boundaries
needed for preservation. This is the recommended approach because it supplies
the facts the address and proof systems need without implementing evaluation.

A complete Python grammar would add substantial compiler-validation work that
the independent local validation already performs. A scanner with delimiter
matching alone cannot distinguish first statements or establish suite ownership.
Neither alternative satisfies this scope as directly as the two cooperating
stages.

Reuse `SourceStructure`, `SourceSpan`, `SourceDeclaration`, `SourceSection`,
`DocumentationOwner` and explicit `ReadFailure` outcomes. Character offsets
remain half-open offsets into the exact decoded source. Regions cover every
character once, in order; reconstruction is identical to the input.

The read result also needs ordered token boundaries, logical separators,
suite relationships, declaration names/nesting and mappings from decoded prose
to raw spans. The implementation plan must give those facts explicit immutable
owners alongside the existing source records. Consumers receive those facts;
they do not independently rediscover them with AST calls, tokenization or
delimiter searches. Payload mappings may refer to several source spans.

Flows acquire source and select the installed definition. Reading owns pure
recognition and interpretation. Existing page/address components consume the
result. Both preservation paths consume one Python comparison contract. The
existing paragraph callback must adapt through the structured read; successful
paragraph extraction alone is insufficient evidence for executable proof.

## Lexical boundaries

The scanner carries its state across physical lines and resumes immediately
after each closing delimiter. It retains exact spelling and source spans for
identifiers, operators, numbers and literal components. It never normalizes
ordinary literal whitespace or discards blank lines inside literals.

Recognize short and triple-quoted literals, legal prefix combinations,
raw escaping, escaped quotes, escaped physical newlines, and adjacent literals.
String-like payloads containing comment markers remain literal data. Include
empty literals, delimiters ending at EOF, and a real comment following a
literal on the same physical line. Literal concatenation is represented by
ordered component spans, not by selecting the first token.

Explicit and implicit continuation, physical versus logical newlines,
indentation transitions, tabs, form feeds, brackets and semicolons contribute
to the structural read. Comments and blank-only lines do not consume a suite's
first statement. Ambiguous indentation or an unresolved delimiter produces a
located failure. These boundaries follow Python's
[lexical rules](https://docs.python.org/3.15/reference/lexical_analysis.html).

Support the structural shapes introduced since the runtime floor: type parameter
lists and defaults, `type` statements, modern interpolation, template strings,
unpacking comprehensions and `lazy` imports. Soft-keyword spellings remain names
outside their grammatical context. Boundary recognition does not evaluate
expressions. See [compound statements](https://docs.python.org/3.15/reference/compound_stmts.html)
and [Python 3.15 syntax additions](https://docs.python.org/3.15/whatsnew/3.15.html).

## Interpolation and observable source text

Maintain a stack for literal payload, replacement expressions and format
specifications. Expression scanning follows Python code rules, including nested
literals, quote reuse, comments, conversions and nested replacements. Preserve
the distinction between an expression colon and a format-specification colon.
An apparent closer inside a string or comment cannot close its enclosing field.
Fixtures exercise the nesting guarantees in
[PEP 701](https://peps.python.org/pep-0701/).

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

Recognize module, class, function and asynchronous-function ownership through
headers and suites. Retain decorators, nested declarations, multiline headers,
annotations, default expressions and type parameters as executable source.
Colons inside expressions do not end a declaration header. Control-flow suites
are recognized so that nested statements cannot be mistaken for an enclosing
owner's first statement. Type aliases and lambdas do not create new declaration
places under this specification.

A docstring is a plain string expression in the first statement position of
the module or a documentable declaration's suite. Parentheses and adjacent
plain string literals may form that expression. A comma, operator, assignment,
call, byte literal, formatted literal or template literal prevents that shape
from being treated as a docstring. Later string expressions remain protected
ordinary literals. First statements in control-flow suites do not become module
docstrings. The attachment rule follows the
[Python documentation rule](https://docs.python.org/3.15/reference/compound_stmts.html#function-definitions).

Retain the complete statement span and the exact raw-to-decoded mapping for
each documentation expression. Decode supported escapes with project-owned
literal handling; do not call `ast.literal_eval`, `eval` or `compile` to obtain
prose. Preserve unrecognized escapes according to the declared grammar.
Unicode-name lookup may use standard-library Unicode data, with that data's
version included in compatibility. An unavailable name receives a located
diagnostic instead of guessed or replaced text. Identifier boundary handling
must not reject otherwise supported newer source solely because the host's
Unicode identifier tables are older; exact spelling remains authoritative for
preservation, and local validation checks identifier legality.

## Sections, directives and addresses

Existing address assignment remains authoritative. A same-type comment section
extends between its surrounding code boundaries and remains whole across blank
lines. Each existing `a`, `b` or `c` place holds its whole section; line controls
apply to that section. Preserve existing `f` matter placement and code anchors.
Interpolation, docstrings and directives cannot justify merging different forms
into one paragraph or creating replacement address series.

Lexical scanning identifies comment and literal forms. The addresser assigns
their series and anchors. Form recovery and setting use those facts together
with binder `raw_text`; no separate copy of original comment text is required.
Changed executable ordering cannot be hidden by freshly matching ordinals.

Protect the shebang, a valid-position source encoding declaration and Python
type comments, including type-ignore directives. Preserve their text and
attachment to source. Directive-only records are not editable prose. Where a
directive and prose cannot be separated reliably, protect the whole directive
comment. Other comment text continues through ordinary section classification;
this specification does not claim to recognize every external tool's directives.

Retain the existing exact source I/O and supported encoding policy. A source
cookie inconsistent with that decoding policy produces an explicit refusal;
the reader must not reinterpret already-decoded text using another encoding.
Shebangs and cookies must remain in their effective positions after setting.

## Setting and preservation

Reread every draft under its saved compatible Python context. An unchanged
round trip preserves bytes, including BOM, mixed endings and absent final
newline. Edited prose must appear at its intended place. Code before or after
documentation on the same line remains present and ordered.

The raw payload mapping supports replacement, removal and move matching across
adjacent documentation literals. Ordered-word snippet matching must use the
complete decoded prose and refuse absent or ambiguous matches. A changed
docstring may be rendered in a valid Python string-literal form, provided the
requested prose and owner survive rereading and executable surroundings remain
unchanged. Do not consume a following comment as a literal suffix.

Both `proof` and `prove_unchanged` compare the ordered executable tokens,
literal spelling/content, suite relationships, significant separators and
protected directive or observable-source spans. Ignore only established editable
prose and insignificant spacing. `proof` additionally checks approval and the
intended alterations; standalone preservation needs no approval record.

Match declaration ownership and executable context before admitting docstring
addition, removal or the existing allowed same-line relocation. Preserve every
ordinary literal from the original source. In particular, removing a docstring
must not permit editing the following string merely because it becomes first.
An added docstring must not hide a preexisting ordinary string from comparison.
Refuse ambiguous correspondence. A blank line or space within an ordinary
literal remains executable data.

Removing a sole docstring does not authorize insertion of `pass` or another
executable statement. Lexical preservation and compilation remain distinct.
Report uncertain ownership as a read failure, and otherwise apply the approved
separate local validation requirement. Formatting follows prose-only proof;
formatted output is presented with its own diff and does not inherit proof
of unchanged executable spelling.

## Compatibility, diagnostics and integration

Changing the Python implementation or definition changes its compatibility
identity. The new binding must cease depending on the host Python parser
version. Any remaining runtime data dependency, such as Unicode-name decoding,
is explicit and limited to the data actually used. Other language contexts
remain independent. Older Python review artifacts require regathering when
their recorded interpretation differs.

Unterminated literals, unfinished replacement fields, unresolved continuation,
inconsistent structural boundaries and unrepresentable editable placement
return stage-specific diagnostics with source spans. A partial read cannot
produce successful addresses or proof. Unsupported future syntax is refused
where it prevents reliable classification; successful reading is not a claim
of complete compiler validation or knowledge of future grammar.

Python gathering, payload/form recovery, declaration placement, setting,
draft rereading and both comparisons consume the structured result. Referrer
discovery consumes declared names and nesting rather than a separate Python AST
read for those facts. Full name harvesting remains separately owned and reports
unavailability explicitly on source the host cannot analyze; it cannot turn
a valid lexical page into a failed or misleadingly empty result.

Other languages keep their existing implementations until their own subplans.
Shared adapters added for Python must preserve their current results. No runtime
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
| Ownership | Module/class/async/function first statements, decorators, same-line suites and nested control flow receive independent expected owners |
| Concatenation | Parenthesized adjacent doc literals yield complete prose and reversible component mappings; tuples and computed expressions remain code |
| Sections | Same-type comments across blanks stay whole at existing places, with line controls covering the complete section |
| Directives | Text or attachment changes refuse; lookalike text inside literals is ordinary literal data |
| Alterations | Add, rewrite, drop and move reread at the intended places while retaining executable prefixes/suffixes |
| Preservation | Token/operator/order/indentation/separator/literal mutations fail; approved prose changes pass both comparison paths |
| Ownership changes | Removing the first docstring cannot authorize changing a promoted ordinary string; inserted docs cannot hide existing literals |
| Failures | Truncated or uncertain input yields located diagnostics, no successful partial proof and no modified originals |
| Saved workflow | Gather, distribute, mark, collate, saved resume, docket and drafting preserve context and original identities |
| Independence | Real read/proof routes work with AST/tokenizer entry points forbidden; import and dependency gates remain intact |

Targeted tests live in `tests/reading/test_python.py`, with integration cases in
the affected page, wrapping, setter, proof, referrer and command suites.
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

The intended Python goals include `python-cannot-read-python` T32-T34 and
T36-T39, subject to the parent design's required replacement of obsolete corpus,
runner and proof prescriptions. Python lexical identity belongs to
`lexical-code-identity` T1; literal-whitespace coverage in T2 remains open if
other-language paths still violate it. Documentation-form and inline-comment
goals may close only to the extent their complete claims are demonstrated.
Operational instruction ordering, other language readers, full name harvesting,
external corpus measurements and preexisting setter-output rollback remain in
their owning work.
