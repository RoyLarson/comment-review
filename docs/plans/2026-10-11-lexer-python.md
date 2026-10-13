# Python lexical reader implementation

```
Status:   in-progress
Progress: 2 of 12 TODO tasks closed
Plan-tasks: 7 of 26 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-11 (founded by move-t from 2026-10-11-lexical-readers)
```

## Objective

Implement the approved Python specification at
docs/superpowers/specs/2026-10-11-python-lexical-reader-design.md. Branch:
feat/lexer-python, based on feat/lexical-readers. Complete the Python gather,
address, set, reread and preservation workflow. Return by no-ff merge after
verification and Roy's integration choice.

Execution: preserve the chosen subagent-driven method. The controller reads this
plan and the spec. Executors receive only the requirements, interfaces, allowed
runtime/test files and checks for their assigned task; no internal plans, specs,
TODOs, decision logs or development history. Approval here records the plan;
implementation starts when requested. Use a failing behavioral test, verify RED,
implement, verify GREEN, then independent task review. Commit work, close its
owning board boxes against that commit, and commit the closure before the next
unit. Runtime examples are invented and task-facing.

Constraints: Python 3.11 host; Python 3.11-3.15 source fixtures;
standard-library runtime only. No AST/tokenizer/eval/compile for reading,
documentation decoding or preservation. One Python definition without family
inheritance. Keep whole same-form a/b/c sections between code boundaries across
blanks, existing f placement, exact source bytes and raw_text. Do not add an
original-text copy. Local compilation is separate from lexical preservation.
Formatting follows prose-only proof and receives its own diff; its output
inherits no proof. Other languages retain their current readers.
Config/data/documents/standalone markup, generated output, full name harvesting,
operational instruction changes, external corpora, release assembly and the
occupied setter-output backlog are outside this subplan.

Architecture and files: create reading/python/{__init__,definition,records,
scanner,interpolation,structure,documentation,directives,projection,rendering,
preservation}.py under src/comment_review, plus
src/comment_review/references/languages/python.toml. File lists below are
relative to src/comment_review unless they start tests/. Create
tests/reading/test_python.py, tests/test_lexical_preservation.py and
tests/test_referrers.py; extend the named existing integration suites. reading
owns pure interpretation; flows acquire source/definitions and admit saved
contexts; page/addresser assign places; compositor applies alterations. Do not
install a partially implemented reader as supported coverage.

Immutable interfaces in reading/python/records.py:
- PythonToken(kind: str, span: SourceSpan): exact spelling comes from source.
- ProtectedSource(span: SourceSpan, kind: str, attachment: SourceSpan | None):
  protection plus effective attachment, compared by structural correspondence.
- PythonScan(text: str, regions: tuple[SourceRegion, ...],
  tokens: tuple[PythonToken, ...], protected: tuple[ProtectedSource, ...]):
  scanner-stage source owner; final SourceStructure reuses the same text.
- InterpolationScan(end: int, regions: tuple[SourceRegion, ...],
  tokens: tuple[PythonToken, ...], protected: tuple[ProtectedSource, ...]):
  events over the interpolation span, used by the enclosing scanner.
- LogicalLine(span: SourceSpan, tokens: tuple[int, ...], indent: int):
  token indices and established logical boundary; separators stay in tokens.
- PythonStatement(span: SourceSpan, tokens: tuple[int, ...], suite: int):
  simple or compound statement membership in its containing suite.
- PythonSuite(span: SourceSpan, parent: int | None, header: SourceSpan | None,
  statements: tuple[int, ...], kind: str): module has no parent/header;
  empty post-removal suites retain a bounded insertion point.
- DeclarationFacts(declaration: int, name: str, parent: int | None,
  suite: int, insertion: int): SourceDeclaration index, enclosing declaration
  index, owned suite index and documentation insertion offset.
- PythonStructure(declarations: tuple[SourceDeclaration, ...],
  facts: tuple[DeclarationFacts, ...], suites: tuple[PythonSuite, ...],
  statements: tuple[PythonStatement, ...]): structural-stage facts.
- DocumentationExpression(statement: SourceSpan, components:
  tuple[SourceSpan, ...], declaration: int | None): complete doc statement,
  each literal component, and owner (None denotes module).
- PayloadPiece(decoded: SourceSpan, raw: tuple[SourceSpan, ...]): decoded
  offsets and contributing raw source spans; zero-output escapes are retained.
- DocumentationPayload(expression: DocumentationExpression, text: str,
  mapping: tuple[PayloadPiece, ...]): complete decoded prose and reversible
  payload mapping; delimiters/prefixes remain in component source spans.
- PythonRead(source: SourceStructure, tokens: tuple[PythonToken, ...],
  suites: tuple[PythonSuite, ...], statements: tuple[PythonStatement, ...],
  declarations: tuple[DeclarationFacts, ...],
  payloads: tuple[DocumentationPayload, ...],
  protected: tuple[ProtectedSource, ...]): sole retained completed read.
- PreservationResult(unchanged: bool, diagnostics:
  tuple[ReadDiagnostic, ...]): false carries a reason; true carries none.

Use existing SourceSpan/SourceRegion/SourceSection/SourceDeclaration and
DocumentationOwner, rather than replacement coordinate or ownership classes.
Validate indices, spans, acyclic nesting and payload coverage. No private record
contains another original-source copy. Diagnostic codes identify the failed
lexical, ownership, placement or preservation condition; attach source spans
wherever available. Reading returns ReadFailure, never partial success.

read_python(text, definition) composes scan, logical structure, declarations,
documentation, directives and sections. ReaderBinding adapts that result to
paragraphs while Page retains the admitted PythonRead for proofs and setting.
The existing paragraph-only implementation remains the adapter for other
languages. Python places must use the retained declarations and executable
boundaries rather than calling declarations(text) or re-scanning delimiters.
Pure entry points accept the installed definition; flows own acquisition.
Broader page/adapter changes are limited to carrying these facts.

Comparison is paired: compare_python(before, after), never two independent
docstring-erasing fingerprints. Match executable context and ownership before
allowing doc presence changes. Every original ordinary string remains an
executable statement even when an earlier documentation expression disappears.
Setter approval/expected-text checks are separate from this preservation result.

Review focus (tests belong to the indicated tasks):
- Nested editable expressions inside protected debug/template source: 7, 20.
- Doc removal promotes an identical-looking ordinary string: 21, 22.
- Adjacent literals followed immediately by another comment: 12, 17, 19.
- Repeated declaration names in different suites defeat ordinal matching: 9, 21.
- BOM/mixed endings/no final newline survive saved setting: 18, 24, 26.

Dependency order: 1-5 establish definition, records and basic scanning; 6-7
extend scanner state; 8-12 establish structural ownership and payloads; 13-15
establish protected/placed sections; 16 installs the complete read route; 17-19
consume it for setting; 20-22 implement paired proof; 23-25 complete
consumer/compatibility migration; 26 verifies the complete workflow. Tasks are
review units, not independent parallel writes. Failures belong in the owning
task before dependent work begins.

Task details follow. For each task, add test functions whose names contain its
selector and assert the stated behavior with invented inputs. Run the listed
focused command before implementation and confirm the expected behavioral
failure; afterward it must pass. A missing test selection is not success.

Task 1: Install Python-owned grammar metadata Files:
references/languages/python.toml; reading/python/definition.py;
reading/language.py; tests/test_language_definitions.py. Interface and
implementation: validate_python(definition: LanguageDefinition) -> ReadFailure |
None. Define explicit Python 3.15 rules and .py/.pyi suffixes, empty
defaults/choices, no inherited rules. Load through existing flow acquisition;
install the new callable only when task 16 is ready. Expected evidence: Assert
accepted complete rules, rejected missing/unknown rules, no settings, and
unchanged other-language definitions. RED/GREEN command: uv run pytest -q
tests/test_language_definitions.py -k python_definition

Task 2: Represent a validated structured Python read Files:
reading/python/records.py; tests/reading/test_python.py. Interface and
implementation: Define the immutable records listed below and their
referential/span validation. PythonRead retains the sole source text in
SourceStructure; tokens and mappings reference its offsets. Expected evidence:
Assert valid reconstruction; reject overlapping or out-of-bounds partitions,
invalid suite/declaration references and payload mappings. RED/GREEN command: uv
run pytest -q tests/reading/test_python.py -k records

Task 3: Scan basic Python tokens Files: reading/python/scanner.py;
tests/reading/test_python.py. Interface and implementation: scan_python(text:
str, definition: LanguageDefinition) -> PythonScan | ReadFailure. Recognize
exact names, numeric forms, longest-match operators, comments and whitespace
without host grammar calls. Expected evidence: Assert independently expected
tokens/regions for empty input, Unicode names, numeric forms, operators and a
final comment without newline. RED/GREEN command: uv run pytest -q
tests/reading/test_python.py -k tokens

Task 4: Scan ordinary Python literals Files: reading/python/scanner.py;
tests/reading/test_python.py. Interface and implementation: Extend scan_python
with short/triple strings, legal prefix combinations, raw escape boundaries and
escaped physical newlines. Retain exact literal spans. Expected evidence: Assert
markers and blank/trailing spaces remain literal data; test escaped delimiters,
empty strings, EOF closers and comments after a literal; truncate each form and
require located failure. RED/GREEN command: uv run pytest -q
tests/reading/test_python.py -k literals

Task 5: Recognize logical lines and indentation Files:
reading/python/structure.py; tests/reading/test_python.py. Interface and
implementation: logical_lines(scan: PythonScan) -> tuple[LogicalLine, ...] |
ReadFailure. Track bracket/explicit continuation, semicolons and indentation
transitions; use physical source offsets without normalizing literals. Expected
evidence: Assert logical boundaries for bracket joins, backslashes, tabs and
form feeds; inconsistent indentation, mismatched brackets and unfinished
continuation refuse. RED/GREEN command: uv run pytest -q
tests/reading/test_python.py -k logical_lines

Task 6: Scan nested formatted-string expressions Files:
reading/python/interpolation.py; reading/python/scanner.py;
tests/reading/test_python.py. Interface and implementation:
scan_interpolation(text: str, start: int, definition: LanguageDefinition) ->
InterpolationScan | ReadFailure. Return end offset, region/token events and
protected spans; scanner resumes at that end. Expected evidence: Assert quote
reuse, nested strings/comments, conversions and nested format fields.
Distinguish expression colons from format boundaries; unfinished replacements
refuse. RED/GREEN command: uv run pytest -q tests/reading/test_python.py -k
fstrings

Task 7: Protect observable interpolation source Files:
reading/python/interpolation.py; tests/reading/test_python.py. Interface and
implementation: Extend InterpolationScan for debug f-string source and t-string
expression text. Protected spans propagate through nested fields; t-string
components remain executable and never documentation. Expected evidence: Assert
exact exposed expression span including whitespace/comments; nested ordinary
f-expression inside protected template/debug expression remains protected.
RED/GREEN command: uv run pytest -q tests/reading/test_python.py -k
observable_source

Task 8: Recognize Python statements and suites Files:
reading/python/structure.py; tests/reading/test_python.py. Interface and
implementation: recognize_structure(scan: PythonScan, lines: tuple[LogicalLine,
...]) -> PythonStructure | ReadFailure. Represent statement spans and parent
suite indices, including module, inline, indented and control suites. Expected
evidence: Assert nested control suites, chained clauses and semicolon
statements. Comments/blanks do not consume first-statement position; doc-only
suites may become empty after a permitted drop. RED/GREEN command: uv run pytest
-q tests/reading/test_python.py -k suites

Task 9: Recognize declaration names and ownership Files:
reading/python/structure.py; tests/reading/test_python.py. Interface and
implementation: Populate SourceDeclaration and DeclarationFacts from headers and
suites. Preserve decorators, async spelling, names, parent declaration indices
and body insertion boundaries; type aliases/lambdas create no declaration place.
Expected evidence: Assert exact owners/anchors for decorated nested
class/async/function definitions, multiline annotations/defaults and colons
within expressions. RED/GREEN command: uv run pytest -q
tests/reading/test_python.py -k declarations

Task 10: Recognize modern Python structural boundaries Files:
reading/python/scanner.py; reading/python/structure.py;
tests/reading/test_python.py. Interface and implementation: Extend owned
recognition for the specified 3.11-3.15 baseline: type parameter lists/defaults,
contextual type/lazy/match/case spellings, unpacking comprehensions and modern
interpolation. Expected evidence: Run invented source strings on host 3.11;
assert comments, tokens and declarations, including soft-keyword spellings used
as ordinary identifiers. RED/GREEN command: uv run pytest -q
tests/reading/test_python.py -k modern_syntax

Task 11: Identify documentation expressions and owners Files:
reading/python/documentation.py; tests/reading/test_python.py. Interface and
implementation: documentation_in(scan: PythonScan, structure: PythonStructure)
-> tuple[DocumentationExpression, ...] | ReadFailure. Select only complete first
plain-string expression statements at module/class/function/async scope.
Expected evidence: Assert parentheses and adjacent literals qualify; tuples,
calls, operators, bytes/f/t strings, later strings and first strings in control
suites remain ordinary code. RED/GREEN command: uv run pytest -q
tests/reading/test_python.py -k doc_ownership

Task 12: Decode complete documentation payloads Files:
reading/python/documentation.py; tests/reading/test_python.py. Interface and
implementation: decode_documentation(scan: PythonScan, expression:
DocumentationExpression) -> DocumentationPayload | ReadFailure. Own escape
decoding, ordered concatenation and raw-to-decoded spans, including zero-output
continuations and empty components. Expected evidence: Assert full
adjacent-literal prose, raw/escaped content, unknown escapes and reversible
component mappings; unavailable Unicode names give located diagnostics.
RED/GREEN command: uv run pytest -q tests/reading/test_python.py -k payloads

Task 13: Protect Python directives and attachment Files:
reading/python/directives.py; tests/reading/test_python.py. Interface and
implementation: directives_in(scan: PythonScan) -> tuple[ProtectedSource, ...] |
ReadFailure. Identify effective shebang, encoding cookie, type comments and
type-ignore; attach to effective line/statement rather than merely matching
text. Expected evidence: Assert valid-position cookies, incompatible encoding
refusal, directive-only protection and literal lookalikes; moving a directive
away from its effective attachment is observable. RED/GREEN command: uv run
pytest -q tests/reading/test_python.py -k directives

Task 14: Project whole Python comment sections Files:
reading/python/projection.py; tests/reading/test_python.py;
tests/test_page_for.py. Interface and implementation: sections_for(scan:
PythonScan, structure: PythonStructure, documentation:
tuple[DocumentationPayload, ...]) -> PythonRead | ReadFailure. Build
SourceSections and owners; retain whole same-form runs between code boundaries
across blanks. Expected evidence: Assert exact a/b/c/f placement inputs,
raw_text and form; no split at blank lines, no combined forms, and complete
section line-control extent. RED/GREEN command: uv run pytest -q
tests/reading/test_python.py tests/test_page_for.py -k sections

Task 15: Admit expression comments at existing places Files:
reading/python/projection.py; reading/addresser.py;
tests/reading/test_python.py; tests/test_page_for.py. Interface and
implementation: Project non-protected interpolation comments through the
existing address contract. If a comment cannot be independently placed and set
without losing expression boundaries, return a PLACE diagnostic. Expected
evidence: Assert a representable comment receives its existing-series place;
unrepresentable editable comments refuse the page explicitly; protected comments
remain recognized but uneditable. RED/GREEN command: uv run pytest -q
tests/reading/test_python.py tests/test_page_for.py -k expression_comments

Task 16: Integrate Python reads into page construction Files:
reading/python/__init__.py; reading/python/projection.py; reading/readers.py;
reading/language.py; binder/page.py; flows/page_for.py; tests/test_page_for.py.
Interface and implementation: read_python(text: str, definition:
LanguageDefinition) -> PythonRead | ReadFailure orchestrates the pure stages.
paragraphs_for(path: Path, read: PythonRead) -> list[Paragraph] | ReadFailure
adapts the result. Page construction retains that read for downstream consumers
and derives declaration/place inputs from it. Expected evidence: Assert one
structured recognition per source/context, consistent forms/declarations/places,
no partial page on failure, and unchanged non-Python page fixtures. RED/GREEN
command: uv run pytest -q tests/test_page_for.py -k python_page

Task 17: Render Python documentation from payload records Files:
reading/python/rendering.py; results/compositor.py;
tests/test_comment_wrapping.py. Interface and implementation:
render_documentation(read: PythonRead, declaration: int | None, prose: str) ->
str | ReadFailure returns replacement documentation source for the selected
owner. Existing compositor owns splicing; preservation uses the original
component/statement spans. Expected evidence: Assert escaped prose, adjacent
literals and parentheses reread correctly; retain code prefixes/suffixes and a
comment immediately following the literal. RED/GREEN command: uv run pytest -q
tests/test_comment_wrapping.py -k python_render

Task 18: Set Python additions rewrites and removals Files:
results/compositor.py; flows/proof_setter.py; tests/test_compositor.py;
tests/test_proof_setter.py. Interface and implementation: Consume PythonRead and
render_documentation for existing Alterations. Use source spans and insertion
boundaries; reread under saved context. Do not insert pass when removing a sole
docstring. Expected evidence: Assert add/rewrite/drop at module and nested
declarations, same-line suites and whole comment sections; exact no-op bytes,
intended prose and neighboring code survive. RED/GREEN command: uv run pytest -q
tests/test_compositor.py tests/test_proof_setter.py -k python_alterations

Task 19: Match moves against complete decoded prose Files:
results/compositor.py; reading/python/documentation.py;
tests/test_comment_wrapping.py; tests/test_proof_setter.py. Interface and
implementation: Use DocumentationPayload.text and its component maps in existing
ordered-word move matching. Preserve the existing atomic move approval and
destination identity checks. Expected evidence: Assert a snippet spanning
adjacent literals moves once; absent/repeated matches refuse; both ends preserve
neighboring comments and executable text. RED/GREEN command: uv run pytest -q
tests/test_comment_wrapping.py tests/test_proof_setter.py -k python_moves

Task 20: Compare Python executable structure Files:
reading/python/preservation.py; results/prove_unchanged.py;
tests/test_lexical_preservation.py. Interface and implementation:
compare_python(before: PythonRead, after: PythonRead) -> PreservationResult.
Compare ordered exact tokens/literals, suite/statement relations, significant
separators and protected source attachment. Ignore only proved editable prose
and insignificant spacing. Expected evidence: Assert
code/operator/order/indentation/separator/literal-space mutations refuse while
comment rewrites pass; directive movement and observable interpolation edits
refuse. RED/GREEN command: uv run pytest -q tests/test_lexical_preservation.py
-k python_preservation

Task 21: Match documentation ownership across reads Files:
reading/python/preservation.py; tests/test_lexical_preservation.py. Interface
and implementation: Complete compare_python with paired
declaration/executable-context correspondence before masking documentation.
Preserve original ordinary literal statements even when promoted to first
position; refuse ambiguous correspondence. Expected evidence: Assert doc
add/drop/rewrite pass; editing a promoted identical-looking ordinary string
fails; inserted docs cannot hide old literals; repeated declaration names in
different suites cannot match by ordinal alone. RED/GREEN command: uv run pytest
-q tests/test_lexical_preservation.py -k python_correspondence

Task 22: Use one Python comparison at both proof gates Files:
flows/proof_setter.py; flows/prove_unchanged.py; results/prove_unchanged.py;
tests/test_proof_setter.py; tests/test_proof_command.py. Interface and
implementation: Route both gates through compare_python on admitted reads.
Setter retains approval and intended-alteration checks separately; standalone
comparison does not require approvals. Propagate located read failures. Expected
evidence: Assert matching preservation decisions at both gates for prose
changes, doc add/drop, same-line relocation and mutations; setter still refuses
an unapproved/intended-text mismatch. RED/GREEN command: uv run pytest -q
tests/test_proof_setter.py tests/test_proof_command.py -k python_proof_routes

Task 23: Supply lexical declaration facts to referrers Files:
concordance/referrers.py; reading/python/records.py; tests/test_referrers.py.
Interface and implementation: Consume DeclarationFacts names/nesting from
PythonRead for declared-name discovery. Keep existing path-term matching;
preserve full name harvesting as a separate result that explicitly reports
unavailable host analysis. Expected evidence: Assert newer-syntax declarations
remain discoverable, nested names are accurate, path matches remain, and
unavailable wider analysis is neither false-empty success nor failed lexical
reading. RED/GREEN command: uv run pytest -q tests/test_referrers.py -k
python_referrers

Task 24: Retain compatible Python reads through saved work Files:
reading/readers.py; reading/context.py; flows/reading_context.py;
tests/test_page_reading_context.py; tests/test_proof_io.py. Interface and
implementation: Give the new binding its own reader revision and definition
identity; replace host parser identity with explicitly used Unicode data
version. Keep admitted context through saved review and draft rereads without
changing other languages' identities. Expected evidence: Assert
implementation/definition/data changes require regather, parser host version
alone does not, other-language contexts remain stable, and resumed work uses the
recorded context. RED/GREEN command: uv run pytest -q
tests/test_page_reading_context.py tests/test_proof_io.py -k python_context

Task 25: Retire replaced Python interpretation paths Files: reading/lexer.py;
reading/readers.py; results/prove_unchanged.py; binder/page.py;
tests/test_reading.py; tests/reading/test_python.py. Interface and
implementation: Remove the replaced Python AST/tokenizer branches and duplicate
declaration/form interpretation, retaining other-language implementations.
Update touched runtime prose to current behavior without internal-history
references. Expected evidence: Exercise actual Python read, reconstruction and
both proof routes with ast.parse, ast.literal_eval and tokenizer entry points
forbidden; assert new syntax still reads and unsafe edits refuse. RED/GREEN
command: uv run pytest -q tests/test_reading.py tests/reading/test_python.py -k
python_independence

Task 26: Verify the complete Python review workflow Files:
tests/reading/test_python.py; tests/test_proof_command.py;
tests/test_proof_io.py; tests/test_proof_setter.py;
tests/test_page_reading_context.py. Interface and implementation: Exercise
gather, distribution, marks, collation, saved resume, docket, setting and reread
using invented fixtures and both .py/.pyi paths. Perform full regression and
unchanged dependency gates; no release assembly. Expected evidence: Assert exact
BOM/mixed-ending/no-final-newline no-op bytes, accepted intended changes and
located failures with unchanged originals. Run the completion commands below.
RED/GREEN command: uv run pytest -q tests/reading/test_python.py
tests/test_proof_command.py tests/test_proof_io.py tests/test_proof_setter.py
tests/test_page_reading_context.py -k python_workflow

Completion commands: uv run pytest -q; uv run ruff check .; uv run ruff format
--check .; uv run ty check; uv run python scripts/check_shipped_syntax.py; uv
run python scripts/check_vocabulary.py. Use the existing cleanup procedure if
formatting/lint changes are required, then rerun affected checks. Keep the
shipped-import gate unchanged. Optional local newer-interpreter compilation is
separate evidence, not a substitute for deterministic fixtures on 3.11. Compare
unexpected failures with the baseline under equivalent conditions.

Completion ownership: this child completes parent P7, P8 and P37. It supplies
Python's contribution to P38-P44 and P53; do not close their broader claims.
Split/supersede mixed claims through job-board before recording partial
completion. Python-only replacement TODOs preserve the behavioral goals of
python-cannot-read-python T32-T34, T36-T39 while replacing obsolete corpus,
runner and stripped-proof prescriptions. lexical-code-identity T1 belongs here;
its T2 remains with the parent for other-language literal whitespace.
Documentation-form/inline-comment goals close only when their entire claim is
demonstrated; otherwise retain their owning parent work. No runtime work is
complete merely because this plan or its interfaces are approved.

## TODO tasks this plan closes

### A - [lexical-code-identity](../../TODO/lexical-code-identity.md)

- [ ] T1 | Replace Python AST identity checks with lexical comparison; verify
      docstring add and removal agree at both gates

### B - [python-cannot-read-python](../../TODO/python-cannot-read-python.md)

- [ ] T38 | Rebuild `prove_unchanged` to prove code unchanged with no `ast`
      branch. Verify: an edited docstring proves, a moved token does not
- [ ] T40 | Read Python with owned lexical recognition independent of the host
      AST and tokenizer
- [ ] T41 | Preserve exact Python round trips over invented boundary fixtures
- [ ] T42 | Read supported newer Python syntax on the pinned Python 3.11 runtime
- [ ] T43 | Reject executable Python mutations at both lexical proof gates
- [ ] T44 | Document the Python preservation contract beside its comparison
- [ ] T45 | Expose complete Python docstrings with their lexical owners

### C - [2026-10-12-python-numeric-keyword-boundaries](../../TODO/completed/2026-10-12-python-numeric-keyword-boundaries.md)

- [x] T1 | Read numeric keyword boundaries; tokens tests accept 1if and 1jand
      while malformed numeric suffixes refuse.

### D - [2026-10-12-python-continuation-eof](../../TODO/completed/2026-10-12-python-continuation-eof.md)

- [x] T1 | Accept joined final whitespace at EOF; logical_lines tests still
      refuse an immediately unfinished continuation.

### E - [2026-10-12-python-reader-vocabulary](../../TODO/2026-10-12-python-reader-vocabulary.md)

- [ ] T1 | Replace retired Python reader terms

### F - [2026-10-12-python-soft-keyword-annotations](../../TODO/2026-10-12-python-soft-keyword-annotations.md)

- [ ] T1 | Read subscript annotations headed by match

## Plan Tasks

- [x] P1 | Python definition validates; 216 tests and focused static checks pass; review approved | f23a9e18 | Install
      Python-owned grammar metadata; verify task 1 evidence with its RED/GREEN
      command
        > 2026-10-12 Roy authorized subagent-driven implementation
- [x] P2 | 32 record and 284 source tests pass; independent review clean | 7b6ea2bd | Represent
      a validated structured Python read; verify task 2 evidence with its
      RED/GREEN command
- [x] P3 | 158 reader tests pass; numeric repair review clean | d9f6ee81 | Scan
      basic Python tokens; verify task 3 evidence with its RED/GREEN command
        > 2026-10-12 Repair numeric-keyword boundary refusal from task review.
- [x] P4 | 583 literal and 733 reader cases pass; review clean | cada9c0e | Scan
      ordinary Python literals; verify task 4 evidence with its RED/GREEN
      command
- [x] P5 | 769 reader cases pass; EOF boundary repair reviewed | cd5635f0 | Recognize
      logical lines and indentation; verify task 5 evidence with its RED/GREEN
      command
        > 2026-10-12 Pass definition explicitly to keep layout rules Python-owned.
        > 2026-10-12 Repair joined final-whitespace refusal found in task review.
- [x] P6 | 801 reader tests pass; nested fields reviewed | 008b46f0 | Scan
      nested formatted-string expressions; verify task 6 evidence with its
      RED/GREEN command
        > 2026-10-12 Include structure.py to consume interpolation boundary events.
- [x] P7 | 856 reader tests pass; observable spans reviewed | a6622eb5 | Protect
      observable interpolation source; verify task 7 evidence with its RED/GREEN
      command
- [~] P8 | Recognize Python statements and suites; verify task 8 evidence with
      its RED/GREEN command
        > 2026-10-12 Pass definition explicitly for configured structural boundaries.
        > 2026-10-12 Cover soft-keyword subscript annotations before completion.
- [ ] P9 | Recognize declaration names and ownership; verify task 9 evidence
      with its RED/GREEN command
- [ ] P10 | Recognize modern Python structural boundaries; verify task 10
      evidence with its RED/GREEN command
- [ ] P11 | Identify documentation expressions and owners; verify task 11
      evidence with its RED/GREEN command
- [ ] P12 | Decode complete documentation payloads; verify task 12 evidence with
      its RED/GREEN command
- [ ] P13 | Protect Python directives and attachment; verify task 13 evidence
      with its RED/GREEN command
- [ ] P14 | Project whole Python comment sections; verify task 14 evidence with
      its RED/GREEN command
- [ ] P15 | Admit expression comments at existing places; verify task 15
      evidence with its RED/GREEN command
- [ ] P16 | Integrate Python reads into page construction; verify task 16
      evidence with its RED/GREEN command
- [ ] P17 | Render Python documentation from payload records; verify task 17
      evidence with its RED/GREEN command
- [ ] P18 | Set Python additions rewrites and removals; verify task 18 evidence
      with its RED/GREEN command
        > 2026-10-12 After P20/P21; paired proof is needed for sole-doc removal.
- [ ] P19 | Match moves against complete decoded prose; verify task 19 evidence
      with its RED/GREEN command
- [ ] P20 | Compare Python executable structure; verify task 20 evidence with
      its RED/GREEN command
        > 2026-10-12 Execute after P17 so setting can consume paired comparison.
- [ ] P21 | Match documentation ownership across reads; verify task 21 evidence
      with its RED/GREEN command
- [ ] P22 | Use one Python comparison at both proof gates; verify task 22
      evidence with its RED/GREEN command
- [ ] P23 | Supply lexical declaration facts to referrers; verify task 23
      evidence with its RED/GREEN command
- [ ] P24 | Retain compatible Python reads through saved work; verify task 24
      evidence with its RED/GREEN command
- [ ] P25 | Retire replaced Python interpretation paths; verify task 25 evidence
      with its RED/GREEN command
        > 2026-10-12 Include definition/scanner/structure/TOML vocabulary repairs.
- [ ] P26 | Verify the complete Python review workflow; verify task 26 evidence
      with its RED/GREEN command
