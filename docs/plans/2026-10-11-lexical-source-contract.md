# Shared lexical source contract

```
Status:   in-progress
Progress: 0 of 1 TODO tasks closed
Plan-tasks: 3 of 13 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-11 (founded by move-t from 2026-10-11-lexical-readers)
```

## Objective

Implement the shared source representation for parent P1, following
docs/superpowers/specs/2026-10-11-lexical-readers-design.md. Branch
feat/lexical-source-contract starts from feat/lexical-readers and returns there
with a no-ff merge after verification. Create
src/comment_review/reading/source.py and tests/test_reading_source.py. The
module is a standard-library-only leaf, compatible with Python 3.11. It imports
no binder, desk, flow, result, lexer, paragraph or addresser module. Existing
source_contract tests concern evidence citations and are unrelated.

Use frozen dataclasses and tuple collections. SourceSpan(start: int, end: int)
is a half-open range of characters in the exact decoded input. It validates
nonnegative ordered bounds. Empty spans can denote points; source regions,
sections and declaration headers must be nonempty. SourcePosition(line: int,
column: int) uses one-based physical lines and zero-based character columns.
Columns are neither encoded byte offsets nor display widths.

RegionKind is a StrEnum with CODE, LITERAL, COMMENT, WHITESPACE and DIRECTIVE,
whose values are lowercase. SourceRegion(span: SourceSpan, kind: RegionKind)
records a reader-supplied classification. A docstring remains lexically LITERAL
and obtains its documentation ownership through a separate relationship.
Delimiters stay within their lexical region; source slices retain every
character. Whitespace inside a literal or comment belongs to that region.
Interpolation can produce alternating literal and code regions; this contract
does not flatten them or decide any language's grammar.

SourceSection(span: SourceSpan, form: str) identifies a whole prose section with
a nonempty language-owned form identifier. The span includes the section's
markers and internal blank lines. Separate same-form fragments can lie inside
this single section. The language reader establishes the boundary; this leaf
does not split on blank lines, strip markers, decode prose or interpret form
names. Form recognition and raw-to-decoded payload mapping are later integration
work.

SourceDeclaration(header: SourceSpan, anchor: int, kind: str) records a
documentable declaration's header range, character offset of its code anchor
within that header, and nonempty language-owned declaration kind. The tuple is
in source order; nested declarations are permitted because the header span does
not stand for the entire declaration body. It does not allocate a place, symbol
name or address. DocumentationOwner(section: int, declaration: int | None)
refers to zero-based section and declaration tuple indices; None explicitly
denotes module ownership. An ordinary comment section has no DocumentationOwner
entry. Module ownership, ordinary comments and the first declaration are
distinct.

SourceStructure(text: str, regions: tuple[SourceRegion, ...], sections:
tuple[SourceSection, ...], declarations: tuple[SourceDeclaration, ...],
documentation: tuple[DocumentationOwner, ...]) validates its structural
invariants on construction. Each sequence preserves source order. Regions
exactly partition text, with no gap, overlap, missing prefix or suffix, or empty
region; empty text has empty collections. Sections are ordered, nonoverlapping
and within text. Declaration headers are ordered by start and within text; their
anchors lie within their headers. Documentation references must exist, be
ordered by section, and give at most one owner to a section and one whole
section to an owner. Invalid producer data raises ValueError with the failing
collection and index. It must never be silently sorted, clipped, merged or
completed.

SourceStructure.slice(span: SourceSpan) -> str validates bounds and returns the
exact characters. SourceStructure.reconstruct() -> str joins region slices in
order. SourceStructure.position(offset: int) -> SourcePosition accepts offsets
through EOF, rejects offsets outside the input and derives coordinates from
original text. Treat CRLF as one physical line break and lone CR or LF as one
each. Offsets on either CRLF character belong to the preceding physical line;
the next line starts after both characters. Tabs, a decoded BOM, combining
characters and non-ASCII characters count as characters. Cache derived line
starts once on the immutable structure rather than scanning the whole input per
position query.

Implement spans and exact partitioning before ownership relationships, then
reference fixtures and dependency checks. Tests compare explicit expected
slices, kinds, section spans and owners, not merely joined text. They include a
deliberately relabelled region that still reconstructs exactly but fails the
fixture's classification comparison. This verifies the representation and the
adequacy of the assertion, not language recognition; actual reader
classification tests remain in each language subplan.

Review focus: empty input and EOF coordinates; mixed line endings and multibyte
characters; literal text containing comment-looking markers; directives
retaining a distinct classification; and nested declaration ownership with whole
sections across blank lines. The steps below assign those cases to tests. Use
invented examples only. For each implementation unit add its named failing
assertions, verify the failure, implement the specified interface and rerun the
focused tests. Once focused checks pass, run the repository gates listed below.
Required outcome is a usable, tested leaf contract, with no active workflow
switched over.

Diagnostics and successful-read admission belong to parent P2: SourceStructure
makes no claim that a read completed or that code is unchanged. Source
acquisition, language configuration, saved contexts, address integration,
Paragraph.lines, setting, proof algorithms, formatting, operational instructions
and release assembly remain with their existing parent tasks. No new runtime
dependency, third-party parser, language-family definition or compatibility shim
is introduced. Runtime executors receive only their task's interfaces, required
behaviors and checks; do not give them internal plans, specifications or
development history.

## TODO tasks this plan closes

### A - [2026-10-11-source-reading-contract](../../TODO/2026-10-11-source-reading-contract.md)

- [~] T1 | Represent source as ordered regions and ownership facts; verify exact
      reconstruction and independently expected classifications

## Plan Tasks

- [x] P1 | Span and position records pass 35 tests and independent review | 937ba33b | Define
      SourceSpan and SourcePosition; test half-open slicing, empty spans,
      negative bounds and reversed bounds
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py -k span
- [x] P2 | Partition and slicing checks pass with independent review | ad7d9faf | Implement
      SourceStructure partition checks; test empty input, gaps, overlaps, wrong
      order, empty regions and lost ends
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py -k partition
- [x] P3 | Exact reconstruction passes focused fixtures and independent review | 82aa1e8b | Implement
      exact reconstruction; test BOM, tabs, Unicode, mixed newlines and no final
      newline without normalization
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py -k reconstruct
- [ ] P4 | Derive cached character coordinates; test CRLF, lone CR and LF, both
      CRLF offsets, EOF and invalid offsets
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py -k position
- [ ] P5 | Define source sections and declaration headers; test bounds,
      ordering, form names, anchors and nested declarations
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py -k declaration
- [ ] P6 | Validate documentation relationships; test module, first declaration,
      ordinary sections, missing references and duplicate owners
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py -k ownership
- [ ] P7 | Preserve whole sections and language-owned forms; test
      blank-separated fragments retain one section and its full span
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py -k section
- [ ] P8 | Verify explicit region-kind fixtures distinguish code, literals,
      comments, whitespace and directives despite equal reconstruction
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py -k classification
- [ ] P9 | Verify immutable tuples and the leaf import boundary; test source.py
      imports without loading workflow or language-reader modules
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py -k boundary
- [ ] P10 | Run focused source-contract tests; verify every required fixture
      passes and no active workflow has been switched over
        > 2026-10-11 uv run pytest -q tests/test_reading_source.py
- [ ] P11 | Run the existing regression suite and dependency gates; verify all
      tests pass with unchanged runtime requirements
        > 2026-10-11 uv run pytest -q
- [ ] P12 | Run lint and formatting checks; verify repository checks pass after
      formatting changed Python files
        > 2026-10-11 uv run ruff check .; uv run ruff format --check .
- [ ] P13 | Run type, shipped-syntax and vocabulary checks; verify exit zero and
      Python 3.11 compatibility after formatting
        > 2026-10-11 Use the existing CLAUDE.md gate commands; all must exit zero
