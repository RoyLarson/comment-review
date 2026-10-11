# Source acquisition and read results

```
Status:   in-progress
Progress: 12 of 13 TODO tasks closed
Plan-tasks: 8 of 13 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-11 (founded by move-t from 2026-10-11-lexical-readers)
```

## Objective

Implement the approved specification
docs/superpowers/specs/2026-10-11-lexical-read-results-design.md on
feat/lexical-read-results, based on feat/lexical-readers. Return by no-ff merge
after verification and Roy's integration choice. This child implements parent P2
and the replacement for parent P3's artifact-I/O test prescription. The
controller reads the internal spec and plan; implementation agents receive only
task-specific interfaces, behavior, allowed files and checks. Writing this plan
does not start implementation. Use the execution method Roy selects after
reviewing it.

The goal is exact source acquisition and explicit failed-read admission. Module
paths below are relative to src/comment_review; test paths are relative to
tests. machine owns file and Git bytes; flows own acquisition and page/proof
orchestration; reading owns pure diagnostics and recognition; binder builds
pages from admitted facts; results sets and compares supplied values. Commands
present flow outcomes. Preserve Python 3.11 and standard-library-only runtime
dependencies. Retain strict UTF-8, the initial BOM character, exact physical
endings, Unicode, the current source hash algorithm, all existing a/b/c/f
address rules and whole sections. No new language definition, registry,
serialization identity, compiler gate, formatting policy or release assembly
belongs here.

Implementation order is P1-P2, P3-P4, P5-P6, P7-P8, then P9-P12. These
dependencies come from the interfaces below, not the numeric IDs. Each
behavior-changing unit adds its failing regression before implementation,
verifies that failure, implements the smallest correction, and reruns its
focused checks. Existing-behavior fixtures may begin passing when their mutation
or independent assertion demonstrates their purpose. Work and verification are
committed first; close only the owning goals that are fully achieved, cite that
work commit, refresh the affected plans and commit the closure separately. No
task is complete because a supporting interface exists while its required caller
behavior is still absent.

P1 interfaces and files: create reading/diagnostics.py under src/comment_review
and tests/test_reading_diagnostics.py. Define ReadStage(StrEnum) with
ACQUIRE='acquire', DECODE='decode', SELECT='select', LEX='lex', PLACE='place'.
Define frozen ReadDiagnostic(stage: ReadStage, code: str, message: str, span:
SourceSpan | None = None, byte_offset: int | None = None) and
ReadFailure(diagnostics: tuple[ReadDiagnostic, ...]). Export SourceRead =
SourceStructure | ReadFailure as a type alias. Reject non-enum stages, blank
code/message, mutable or empty diagnostic collections, wrong record types,
negative/noninteger/bool byte offsets and simultaneous character/byte locations
with ValueError. Require byte locations to describe DECODE failures; character
locations describe LEX or PLACE failures. Preserve valid values without
coercion. Use codes io-error, invalid-utf8, missing-revision-source,
unsupported-language, incomplete-read, unterminated-comment and
unsupported-placement for the corresponding current conditions. Test exact enum
values and each invalid-state boundary, including a SourceStructure over empty
text distinct from ReadFailure.

P2 interfaces and files: extract reusable coordinates into
reading/coordinates.py, moving SourcePosition there and re-exporting it from
reading/source.py so its existing import remains valid. coordinates.py must not
import source.py. Define frozen SourceCoordinates(text: str) with
position(offset: int) -> SourcePosition; cache physical line starts once.
SourceStructure delegates its existing position method to this shared
calculation. Diagnostic rendering in a new flows/read_diagnostics.py supplies
format_failure(failure: ReadFailure, *, path: str, language: str | None = None,
text: str | None = None) -> str. Render one diagnostic per line with path, known
language, stage/code, message and either one-based line plus zero-based
character column, or an explicitly labelled zero-based byte offset. Missing
locations remain absent. Character-located diagnostics require text and bounds
validation; acquisition/decode reports need no invented text. Validate decoding
offsets against the exception's input bytes before constructing them in P4.
Tests assert CRLF offsets both stay on the preceding line, EOF works, tabs and
combining characters count as characters, and UTF-8 byte offsets are not shown
as character columns. Keep source.py's public records and coordinate behavior
unchanged; update private-cache assertions to test the shared owner without
weakening the cache requirement.

P3 interfaces and files: extend machine/repo.py with source_from_bytes(raw:
bytes) -> Source and read_revision_source(repo: Path, ref: str, rel: str) ->
Source. source_from_bytes strictly decodes UTF-8 and pairs the text with
existing sha_of(text). read_source(path) acquires bytes once and calls that
operation; read_raw(path) returns its exact text. read_revision_source obtains
binary subprocess stdout using argument-based Git invocation and the existing
ref:./rel path semantics, timeout and cwd behavior. Preserve metadata Git calls
as text. Expected subprocess failure remains an exception for the acquisition
flow to translate; empty stdout on a successful blob read is a successful empty
Source. Do not cache snapshots across source versions. Test in
tests/test_source_io.py and tests/test_machine.py using actual literal bytes,
including BOM-only input, mixed endings and Unicode. A temporary Git repository
uses explicit blob creation or disabled autocrlf so Git cannot normalize the
fixture. Independently assert decoded text, text.encode('utf-8') ==
original_bytes, existing hash value and one filesystem read. Verify invalid
UTF-8 and UTF-16 BOM signatures raise decoding errors; valid UTF-8 bytes
containing NUL reach recognition unchanged.

P4 interfaces and files: retain write_raw(path: Path, text: str) -> Path in
machine/repo.py. Encode the entire string strictly before creating/opening a
write target; write the encoded bytes without newline translation, retaining
machine-owned parent-directory creation. Add acquisition operations to
flows/source.py: source_of(path: Path) -> Source | ReadFailure and
revision_source_of(repo: Path, ref: str, rel: str) -> Source | ReadFailure.
Expected OSError/subprocess/decode failures become the appropriate diagnostic
and code from P1. UnicodeDecodeError.start is a byte location validated against
its bytes object. Unexpected exceptions propagate. Move the existing source_of
implementation out of flows/page_for.py in the coordinated migration P6 rather
than leaving two permanent owners. Tests cover missing source, unavailable
ref/path, successful empty snapshot, decoding byte offset, unchanged BOM/newline
byte writes, parent creation, and a lone-surrogate output rejected without
truncating an existing target. Character decoding errors and expected system
errors have distinct stages; do not catch all ValueError as user input failure.

P5 interfaces and files: add read_paragraphs(path: Path, text: str, lang:
Language) -> list[Paragraph] | ReadFailure to reading/lexer.py as the single
boundary over the existing paragraph readers. Preserve their recognition and
documentation rules, but translate their explicit unparsed paragraphs and
unterminated-comment annotations into LEX failures before page construction. Use
original source spans where the signal identifies one; do not invent a location
or classify a previously unrecognized tail. Translate failures before subsequent
decoration passes can conceal them. Tests in tests/test_reading_diagnostics.py
and tests/test_reading.py exercise real malformed source and deterministic
returned failure records; both sides of that boundary matter. This is a
temporary integration seam until parent P44 removes the retired readers: it
never fabricates SourceStructure from legacy paragraphs. Runtime prose explains
the current function only; internal replacement history stays in this plan. The
full language-recognition goal of lexer-and-language-findings T2 remains with
the parent.

P6 interfaces and files: make binder/page.py page_for(path, text, lang,
rel=None, *, sha) -> Page | ReadFailure consume read_paragraphs and return a
failure before assigning places. Convert known placement refusals at their
producing boundary to PLACE diagnostics with spans where available; unexpected
programming errors propagate. Change flows/page_for.py page_of(path: Path, rel:
str | None = None, source: Source | None = None) -> Page | ReadFailure and have
it consume flows/source.py.source_of. Supplying a Source prevents another file
read. The selected reader must see the exact same text whose sha the page
carries. Selection failure is SELECT/unsupported-language. Adapt every
production caller atomically: flows/gather.py, proof_setter.py, revise.py,
on_the_page.py, fill.py; commands/carry.py, addresser.py, taken_in.py; and the
direct page_for consumers in results/compositor.py pending P7. Remove gather's
paragraph-kind scan and broad parse-error catch. Audit the callers found by the
actual changed signatures before committing, including test helpers. A failed
page must not be omitted and then treated as an empty successful binder;
revise's address comparison must refuse even when both sides fail identically.
Do not change established behavior for optional missing lookup targets where the
caller makes no successful-page claim. Tests cover complete empty pages,
unparsed input, unsupported language, known placement failure, no second
acquisition, and an unexpected injected exception propagating rather than
producing success.

P7 interfaces and files: move compositor file orchestration into
flows/compositor.py. Define frozen RoundTrip(original: str, rendered: str) and
round_trip(path: Path) -> RoundTrip | ReadFailure, using source_of, page_of with
the held snapshot, and results.compositor.set_page once. The existing rendering
refusal becomes a located PLACE failure when its location is available. Refactor
results/compositor.py lossless(original: str, rendered: str) -> str | None and
identity(original: str, rendered: str) -> str | None into pure comparisons.
Identity compares strict UTF-8 bytes including BOM and endings; lossless retains
the existing line-retention meaning. Update commands/compositor.py to call
round_trip once per file, present read failures as failures, and run both
comparisons over the same pair. Preserve the existing distinction between
identical, reordered/normalized and lossy outcomes. Migrate test_compositor.py
and any remaining callers of the old path-based helpers. No result function
imports a flow to reach I/O. Test spies establish one acquire, one page build
and one set for a combined command run; byte equality assertions establish
preservation independently. Real successfully read empty and CRLF fixtures
exercise the live path. BOM and mixed-ending acquisition/write cases remain
independently tested even if current language/setting support refuses them.

P8 interfaces and files: add flows/prove_unchanged.py with frozen
ProofReport(messages: tuple[str, ...], failures: int, unchecked: int) and
run(repo: Path, base: str, paths: Sequence[Path]) -> ProofReport. Move the
standalone command's per-path acquisition/check orchestration into this flow;
commands/prove_unchanged.py keeps argument parsing, output and existing exit
policy. Use source_of and revision_source_of for current and baseline snapshots
and page_of with those snapshots to require admission on both sides before
calling the existing fingerprint comparison. Retain repo-subdirectory path
handling, the existing sibling-ending check and explicit missing-baseline
behavior. Remove retired source-acquisition helpers from
results/prove_unchanged.py once their callers move; keep its comparison
algorithms pure and unchanged in purpose. In flows/proof_setter.py preserve
recorded-sha checking before parsing, consume structured acquisition/page
failures at initial read and reread, and ensure _prove cannot compare failed
readings. Both comparison paths must reject failure on either side, the same
failure twice, and unprovable/unknown fingerprints before equality. Reuse
successful pages already held where available; never re-open a source just to
build the same page. Preserve approval handling independently of read admission.
Add actual CLI/integration regressions in test_proof_command.py,
test_proof_setter.py and the existing standalone proof tests, plus injected
reader/placement failures. These checks do not replace the lexical comparison
algorithm owned by parent P41-P42.

P9 tests and boundaries: verify rollback in a two-file draft where the second
file fails acquisition, decoding, recognition or placement; compare all original
bytes and assert earlier drafts and created directories are removed. Verify an
unexpected exception still propagates after cleanup. Exercise revise address
checking with failed reads on both sides; equality of empty sets is not a pass.
Use existing test_proof_setter.py and test_revise.py and add focused tests only
where the existing file does not cover the behavior. In tests/test_areas.py and
existing import checks, verify the changed code respects machine/leaf/flow
ownership without adding new exceptions to the gate. Inspect only the call sites
introduced or replaced by this work; broader cross-area cleanup remains
separately owned. Update affected docstrings to current behavior and keep
internal history out of shipped prose.

Review focus and assigned fixtures: empty or BOM-only input is acquisition
success and does not imply recognition success (P3/P6); the same failed read on
both comparison sides is never proof (P8/P9); Git stdout and worktree reads
preserve independent mixed-newline expectations (P3/P8); invalid output encoding
cannot truncate a target (P4); failure after an earlier successful draft cleans
up that draft and preserves originals (P9). Negative tests must demonstrate the
expected refusal, not merely accept any exception. Tests of unchanged behavior
use literal expected bytes or labels rather than asserting only agreement
between two implementations.

P10-P12 completion gates: run uv run pytest -q tests/test_reading_diagnostics.py
tests/test_source_io.py tests/test_reading_source.py and the touched integration
suites, then uv run pytest -q for the full regression suite. Run uv run ruff
check ., uv run ruff format --check ., uv run ty check, uv run python
scripts/check_shipped_syntax.py and uv run python scripts/check_vocabulary.py.
Required checks must exit zero; report any established skips/xfails distinctly.
Independent review examines source admission, caller migration, byte fidelity
and import ownership. No gate is weakened to accept the change. Finish all child
T/P and parent P2/P51 against actual work commits only after their full criteria
pass; refresh both plans and close the child through job-board. Parent P3 is
superseded by P51 because its old prescribed test targets saved JSON rather than
source bytes.

The following remain open in the parent: language specifications and actual
recognition algorithms, registry dispatch, saved-context compatibility,
decoded-payload mapping, full BOM-bearing language setting behavior, address
integration, shared lexical proof replacement, formatting and operational
instructions. Only existing explicit read failures are normalized here. The old
broader io.py/lexer-owned-file-access prescriptions and console-I/O work are not
closed by this child. Lexer annotation recognition T2 remains open for the
language work; P44 owns removal of the temporary paragraph-reader boundary. No
runtime implementation is included in the plan-authoring commit.

## TODO tasks this plan closes

### A - [2026-10-11-source-reading-contract](../../TODO/2026-10-11-source-reading-contract.md)

- [x] T5 | Define immutable read diagnostics and failures; verify location
      units, field validation and successful empty input
- [~] T6 | Reject failed readings at page and proof admission; verify
      either-side failures, empty success and cleanup
- [x] T7 | Make unsupported-syntax fixtures interpreter-aware; verify valid
      newer Python syntax is not required to fail
- [x] T8 | Repair render_page package imports and page outcomes; verify its
      normal command on successful and refused source

### B - [the-lexer-reads-no-files](../../TODO/the-lexer-reads-no-files.md)

- [x] T23 | Acquire exact UTF-8 source from files and Git; verify BOM, line
      endings, Unicode, identity and named failures
- [x] T24 | Write exact UTF-8 bytes; verify unchanged round trips and encoding
      failure before target truncation
- [x] T25 | Classify Git repository acquisition errors as io-error; verify
      missing repository differs from an unavailable revision source

### C - [galley-and-compositor-write-path](../../TODO/galley-and-compositor-write-path.md)

- [x] T51 | Consolidate round-trip checks in a flow; verify one acquisition and
      setting per file and independent comparison outcomes
- [x] T52 | Verify source-byte preservation using invented BOM, newline and
      empty fixtures; detect normalization at the actual I/O boundary
- [x] T53 | Assert exact BOM and mixed-ending round-trip outcomes; verify
      expected diagnostic codes or rendered bytes and command status
- [x] T54 | Describe compositor command refusal exits accurately; verify the
      comment agrees with all nonzero paths
- [x] T55 | Describe lossless line retention separately from identity; verify
      prose agrees with newline and reorder cases
- [x] T56 | Align compositor command prose with its flow API; verify no retired
      path-based comparison examples remain

## Plan Tasks

- [x] P1 | Immutable diagnostics and empty-success distinction verified | 42752127 | Define
      immutable diagnostics and failed-read outcomes; verify stages, codes,
      invalid fields and empty-input success
        > 2026-10-11 uv run pytest -q tests/test_reading_diagnostics.py
- [x] P2 | Shared coordinate cache and located rendering verified | fc54847c | Share
      cached source coordinates and diagnostic rendering; verify CRLF, EOF,
      Unicode and distinct byte offsets
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py
        > 2026-10-11 Complete P13 here; formatter falls back to retained failure context
- [x] P3 | Exact filesystem and binary Git acquisition verified | 193b7d6c | Acquire
      exact filesystem and Git source snapshots; verify UTF-8 bytes, identities,
      failures and one read per snapshot
        > 2026-10-11 uv run pytest -q tests/test_source_io.py
- [x] P4 | Exact writes and located acquisition failures verified | 1c16426e | Encode
      before writing and expose acquisition outcomes; verify untouched targets
      on encoding errors and located decode failures
        > 2026-10-11 uv run pytest -q tests/test_source_io.py
- [x] P5 | Existing reader refusals normalized before decoration | 021149ab | Translate
      current reader refusal signals at one boundary; verify real malformed
      inputs and returned failure records
        > 2026-10-11 uv run pytest -q tests/test_reading_diagnostics.py
- [x] P6 | Page outcome callers migrated and full regression suite passed | a8b18c66 | Migrate
      page construction and its callers to explicit outcomes; verify empty
      success, failed admission and no duplicate reads
        > 2026-10-11 uv run pytest -q tests/test_page_for.py
        > 2026-10-11 Return LocatedReadFailure with path, language and retained text
- [x] P7 | One held round trip and independent comparisons verified | 3aa24584 | Move
      round-trip orchestration into a flow; verify one read and set plus
      separate identity and line-retention comparisons
        > 2026-10-11 uv run pytest -q tests/test_compositor.py
        > 2026-10-11 Return LocatedReadFailure with path, language and retained text
- [ ] P8 | Admit both proof inputs through shared outcomes; verify exact Git
      baselines and refusal of either-side or matching failures
        > 2026-10-11 uv run pytest -q tests/test_proof_command.py
        > 2026-10-11 Render failure context from held snapshots into report messages
- [ ] P9 | Verify multi-file rollback and import boundaries; check failed
      rereads preserve originals and cannot imply equal addresses
        > 2026-10-11 uv run pytest -q tests/test_proof_setter.py tests/test_areas.py
- [ ] P10 | Run focused and full regression suites; verify source and proof
      integration with expected skips reported separately
        > 2026-10-11 uv run pytest -q
- [ ] P11 | Run repository lint and formatting checks; verify both exit zero on
      the completed implementation
        > 2026-10-11 uv run ruff check .; uv run ruff format --check .
- [ ] P12 | Run type, shipped-syntax and vocabulary gates; verify Python 3.11
      and standard-library runtime compatibility
        > 2026-10-11 Use the exact P10-P12 gate commands in the objective
- [x] P13 | Retained failure context renders locations without rereading | fc54847c | Define
      LocatedReadFailure(ReadFailure) in flows/read_diagnostics.py; verify
      commands render stored source spans without rereading
        > 2026-10-11 Frozen fields: path: str, language: str | None, text: str | None
