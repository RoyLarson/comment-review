# Source acquisition and read results

## Purpose and scope

Define the source-acquisition and failure-handling boundary for P2 and P3 of
[the lexical readers plan](../../plans/2026-10-11-lexical-readers.md), following
[the shared reader design](2026-10-11-lexical-readers-design.md).

Every consumer must distinguish source that was acquired and completely read
from source that could not be acquired, decoded, recognized or placed. An empty
file can succeed. A failed read cannot become an empty page or a successful
preservation comparison. Supported source must survive an unchanged read/write
cycle byte for byte, including its BOM and physical line endings.

The shared source representation already supplies immutable character spans,
regions, sections, declarations, ownership and positions. This work adds read
outcomes and connects expected failures to the acquisition, page-building and
proof boundaries. It preserves the existing address series and whole-section
rules.

The proposed implementation branch is `feat/lexical-read-results`, based on
`feat/lexical-readers`. This specification is for review before the subplan is
written. It does not authorize implementation.

## Review of the proposed scope

P2 and P3 belong together because decoding and recognition failures need the
same caller behavior, and a preservation check needs the exact source that
produced its reading.

The current implementation already has useful pieces:

- `machine.repo.read_raw` and `write_raw` use strict UTF-8 and preserve newline
  characters. `read_source` pairs the decoded text with its identity.
- `flows.page_for.source_of` and `page_of` provide a shared acquisition path,
  but return strings as reasons. `page_of` can return an unparsed page, leaving
  gather to inspect paragraph kinds and catch arbitrary exceptions.
- `results.compositor.lossless` and `identity` repeat acquisition and page
  construction. Their file access belongs in a flow under the existing area
  rules.
- The standalone preservation command reads its working-tree input through
  `Path.read_text`. Its Git baseline comes through text-mode subprocess output.
  Both boundaries can translate newlines before comparison.
- `tests/test_proof_io.py` exercises saved review artifacts. It cannot be the
  principal acceptance test for P3's source-byte preservation.

Use explicit outcomes and the existing flow boundary. Keeping loose result and
reason tuples would leave each consumer responsible for maintaining the same
relationship. Building a general reader framework here would require the
language registry and language-specific recognition before they are specified.
The selected design adds only the outcome and diagnostic types needed by these
callers and consolidates their existing acquisition work.

## Responsibilities

| Owner | Responsibility |
| --- | --- |
| `machine` | Read filesystem or Git blob bytes and write encoded bytes; preserve existing path and subprocess protections. |
| `flows` | Acquire a snapshot, translate expected acquisition failures, select the current reader, build a page, and coordinate setting and proof. |
| `reading` | Define diagnostics and reader outcomes; recognize supplied text without file access. |
| `binder` | Construct a page from admitted reading facts and assign existing places. |
| `results` | Set or compare supplied values without acquiring files or importing flow containers. |
| `commands` | Invoke flows and present diagnostics using the command's established exit behavior. |

The machine layer imports no reading types. Flows translate its expected I/O
and decoding errors into shared diagnostics. The reading leaf imports no page,
binder, docket, flow or machine type. Flow-owned outcomes can contain the
existing source snapshot or page without moving those types into the leaf.

## Read outcomes

A language reader returns either a complete `SourceStructure` or a
`ReadFailure`. A `ReadFailure` contains a nonempty immutable tuple of
`ReadDiagnostic` values. There is no successful structure inside a failure.

Returning `SourceStructure` means that the reader reached the end of the input
and established the classifications, sections and ownership it supplies. The
structure's partition validation proves coverage; the reader's recognition
rules establish that the coverage is meaningful. Reconstruction alone does not
establish successful recognition.

An unsuccessful reader retains the exact input at its caller. It returns the
diagnostics needed to explain the failure, without filling an unknown tail with
invented regions or exposing a recognized prefix as a complete result. Partial
regions are not part of this contract.

The corresponding flow boundaries return a source snapshot or `ReadFailure`,
and a page or `ReadFailure`. A successful empty snapshot has `text == ""` and
its normal source identity. A successful empty reading is an empty
`SourceStructure`. A successful empty page can be set back to empty bytes.
Neither a missing value, an empty paragraph list nor an empty fingerprint is a
failure indicator.

The new diagnostic and failure records are immutable. Constructors reject
invalid field types and empty failure-diagnostic tuples. Existing page editing
behavior is unchanged. Invalid producer records are programming errors; they
are not translated into claims that the input language is invalid.

## Diagnostics

`ReadDiagnostic` carries the following facts:

| Fact | Purpose |
| --- | --- |
| Stage | Distinguish acquisition, decoding, language selection, lexical recognition and placement. |
| Code | A stable nonempty identifier for the condition; callers do not parse prose. |
| Message | Explain the boundary or context that could not be established. |
| Character span, when known | Locate recognition or placement failures in the exact decoded input using `SourceSpan`. |
| Byte offset, when known | Locate a decoding failure before a decoded character span exists. |

Character spans and byte offsets are mutually exclusive. A span may be an empty
point at EOF; a byte offset is nonnegative and counts input bytes. Missing
locations remain absent rather than being reported as character zero. A
source-dependent boundary validates that a supplied span or offset lies within
the input it describes.

The flow attaches the file name and selected language to the rendered report.
Acquisition can fail before a language has been selected, so that report does
not invent a language. Recognition reports include the selected language and
the relevant lexical context, such as an unterminated literal or comment.
Character positions use `SourceStructure`'s existing line and column convention;
failed reads use the same coordinate calculation over their retained input.
The implementation extracts the shared calculation if needed rather than
duplicating newline rules or constructing a falsely classified structure.

Every diagnostic in this contract blocks admission. Warning severity, recovery
policy and suppression are outside this subplan. Readers return diagnostics in
source encounter order. A reader may stop at the first failure when continuing
would require guessing a boundary.

Expected input failures become diagnostics. Unexpected exceptions propagate
through the existing cleanup boundary; a broad exception handler must not turn
a programming error into a successful or apparently empty reading.

## Exact acquisition and identity

Retain strict UTF-8 support. Valid UTF-8 with or without its BOM is accepted at
the acquisition boundary. Bytes that cannot be decoded as UTF-8, including
UTF-16 BOM signatures, produce decoding failures. There is no
replacement-character decoding, locale-dependent decoding, encoding detection
or fallback codec. Bytes that are valid UTF-8 are decoded as UTF-8; acquisition
does not guess whether their author intended another encoding. Recognition of
decoded control characters, including NUL, belongs to the selected reader.

A UTF-8 BOM is retained as the initial U+FEFF character in decoded source and
re-encodes to its original bytes. It is included in character offsets and source
identity. Acquisition never strips it. Whether a reader recognizes the initial
signature belongs to that language's definition; interior U+FEFF characters
remain source characters. Acquisition success does not imply reader success.

Filesystem and Git-baseline acquisition use the same strict decode operation
on bytes. Git blob contents must not pass through text-mode subprocess newline
conversion. Preserve argument-based Git invocation, the repository-relative
path behavior and the distinction between an empty blob and an unavailable
revision or path. Metadata-oriented Git commands can retain their existing
text interface.

Retain LF, CRLF, lone CR, mixed endings, tabs, Unicode, literal whitespace and
the absence of a final newline. No acquisition step splits and rejoins lines,
trims text, normalizes Unicode or changes endings.

Keep the existing source snapshot and identity algorithm. For the supported
strict UTF-8 inputs, re-encoding the exact decoded text reproduces the acquired
bytes, including a BOM. Compute the identity from that same snapshot without a
second file read. This subplan adds no competing source hash, encoding field or
saved-artifact version. Tests compare actual bytes as well as text and identity.

The write boundary encodes supplied text strictly before opening the target for
writing, so an encoding failure cannot truncate an existing target. It preserves
the supplied characters and writes their UTF-8 bytes without platform newline
conversion. The machine writer retains parent-directory creation; flows retain
target containment, tracking of created directories and cleanup. This work does
not introduce a new multi-file write transaction or authorize overwriting
reviewed source during drafting.

## Admission and integration

The acquisition flow owns expected filesystem, Git and decoding failures. Page
construction consumes its successful snapshot without reopening the source.
The same snapshot supplies both text and identity to all checks for that source
version.

Move the known unparsed-result check into the page-building boundary. Gather,
drafting, rereading and compositor checks consume the resulting page or failure;
they do not search paragraphs to rediscover whether parsing succeeded. A
placement refusal receives a located diagnostic when the failure site has the
source span. No incompatible sections are merged to make a page build succeed.

Current readers have different result shapes. While they remain in use, their
existing explicit refusal signals are translated at one reader boundary.
Translate the unparsed result and unterminated-comment annotations there rather
than teaching every consumer those representations. This translation does not
construct a `SourceStructure` from legacy paragraphs or assert recognition
coverage that the current reader cannot establish. Its temporary role and its
removal under the reader replacement work must be explicit in the subplan.

The new reader-outcome contract is exercised with deterministic test readers.
Production integration also exercises actual failure cases from the current
readers. Both are necessary: test doubles verify caller admission, while real
inputs verify that existing refusal signals reach it.

Both preservation entry points must refuse a failed read on either side before
comparing executable representations. Two identical failures do not prove
preservation. Equality of source strings or empty fingerprints cannot bypass
this rule. A placement failure also blocks the address-based preservation
operation. Existing conservative unprovable cases remain refusals until their
language reader supports them.

This subplan standardizes refusal admission and exact inputs. The common lexical
comparison algorithm, elimination of Python AST/tokenizer dependence and full
language recognition remain with P37 and P41-P42. Successful acquisition and
successful reading also remain distinct from the agent's later compilation or
syntax check.

Compositor round-trip checks acquire, read and set a source once per requested
check run. A flow supplies the original and rendered values to the existing
identity and line-retention comparisons. The results module does not import
`flows.page_for` to avoid duplicating that work. No-op byte reconstruction and
the weaker line-retention check remain separately named outcomes.

Proof input from a Git revision and proof input from the working tree use the
same exact decoding policy. File-specific failures retain their reasons through
the command output and existing nonzero result. Existing drafting rollback
removes earlier drafts if a later source fails; the original files stay intact.

## Acceptance evidence

Use invented source examples and literal expected values. The subplan must
provide these checks:

- Outcome construction distinguishes complete empty input, acquisition failure,
  decoding failure, incomplete recognition and unsupported placement. Invalid
  diagnostic fields and empty failure tuples are rejected.
- Explicit diagnostics carry the correct file, selected language where known,
  stage, code and location. Byte locations are never rendered as character
  columns. CRLF and multibyte Unicode demonstrate the distinction.
- A successful source snapshot hashes exactly the bytes decoded, with one read
  per snapshot. Supplying that snapshot to page construction performs no read.
- Byte fixtures cover empty input, BOM-only input, UTF-8 BOM with content, LF,
  CRLF, lone CR, mixed endings, tabs, non-ASCII and combining characters, literal
  trailing whitespace, and no final newline. Acquisition followed by an
  unchanged write reproduces every byte.
- Invalid UTF-8, including UTF-16 BOM signatures, returns decoding failures.
  UTF-8-valid bytes containing NUL reach the reader unchanged. An unencodable
  output string fails before changing an existing target. Missing files and
  unavailable Git blobs remain distinct from successful empty input.
- A temporary repository contains a blob with known mixed endings and Unicode.
  Both baseline acquisition and working-tree acquisition return independently
  expected exact text. A changed literal whitespace fixture reaches comparison
  unchanged by I/O; the final lexical comparison behavior remains separately
  tested under its owning plan tasks.
- Current-reader failures and injected failed outcomes reach gather, page
  acquisition, drafting, rereading and both preservation entry points. Each
  refuses without admitting a successful page or proof. Test failure on either
  comparison side and the same failure on both sides.
- Round-trip checks share one acquisition and setting operation when requested
  together. A later failure in a multi-file draft removes earlier drafts and
  preserves all original bytes.
- BOM acquisition is tested independently of language recognition. A reader
  that currently refuses that input must report its failure; no BOM test passes
  by silently omitting the file. Full BOM-bearing page and setting behavior is
  a language-integration acceptance case.
- Import-boundary checks preserve machine, reading, flow and results ownership.
  Runtime dependencies remain standard-library-only and Python 3.11 compatible.

Use `tests/test_reading_diagnostics.py` for outcome and location checks and
`tests/test_source_io.py` for exact acquisition and writing. Extend the existing
page, gather, compositor, proof-setter and proof-command tests for real call-path
coverage. `tests/test_proof_io.py` remains the saved-artifact regression suite.
Run the full test suite and the established lint, formatting, type,
shipped-syntax and vocabulary gates before completing the subplan.

## Task mapping and completion boundaries

| Parent work or existing TODO | Treatment in the subplan |
| --- | --- |
| P2 | Define outcomes and diagnostics, route current explicit failures consistently, and demonstrate refusal admission at page and proof boundaries. New recognition algorithms remain language-owned. |
| P3 | Verify exact filesystem and Git source acquisition and exact writing. Replace its artifact-I/O test prescription with source-I/O checks through job-board when authoring the subplan. |
| `the-flow-lives-in-the-command` T8 | Replace the tuple-specific prescription with the shared page-or-failure outcome; gather consumes that outcome without a paragraph-kind scan or broad parse-error catch. |
| `galley-and-compositor-write-path` T5-T8 | Verify newline preservation and consolidate round-trip acquisition/setting in a flow, including the single-read case. Preserve the separate comparison meanings. |
| `galley-and-compositor-write-path` T9-T10 | Replace an unread-page flag with explicit failure admission; independently prove that successful empty input sets back to empty. |
| `no-step-produces-a-page` T3 | Preserve its consolidation goal while keeping filesystem access and page construction out of results. Supersede the cross-area call prescription before implementation. |
| `the-lexer-reads-no-files` T17-T18 | Replace stale module-location and historical failing-test prescriptions with exact byte expectations over source acquisition and round-trip output. |
| `lexer-and-language-findings` T2 | The diagnostic mechanism replaces per-paragraph refusal stamping. Close the full recognition goal only when the affected language readers detect the required boundaries; split mechanism and remaining recognition claims if needed. |

The parent design's broader replacements for `the-lexer-reads-no-files` T9-T20
are not all completed here. Console I/O, unrelated source consumers and the
old fixed-chain prescriptions are not silently closed by adding this boundary.
Apply the existing supersede-and-replace procedure to obsolete or partly
delivered tasks while preparing the subplan. Every replacement retains an
independently checkable behavior.

The subplan can close when the shared outcome contract, current refusal
admission and exact source-I/O checks pass. That closure does not claim that
every supported language now recognizes all of its required syntax. Language
specifications and readers, registry dispatch, saved reading compatibility,
decoded prose mapping, address integration, formatting and operational
instructions retain their parent owners. No release assembly is included.

Implementation agents receive only their task's interfaces, required behavior,
allowed files and verification commands. This specification and other internal
development material are not runtime instructions or executor inputs.
