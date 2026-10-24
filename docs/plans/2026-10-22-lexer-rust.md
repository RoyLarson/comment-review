# Rust lexical reader implementation

```
Status:   in-progress
Progress: 6 of 6 TODO tasks closed
Plan-tasks: 13 of 13 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-22 (founded by move-t from 2026-10-11-lexical-readers)
```

## Objective

Implement the approved Rust specification at
docs/superpowers/specs/2026-10-18-rust-lexical-reader-design.md. Branch:
feat/lexer-rust, based on feat/lexical-readers, returned by no-ff merge. The
work is a reading change; the five changes outside reading are the spec's O1-O5,
approved by Roy 2026-10-22, and any other change outside reading needs his
approval with justification first. Each step lands its failing tests first, then
the code, then a review, and ends with its focused tests and the full suite
green. Implementation starts when Roy asks; subagent-driven like the Python
reader.

## TODO tasks this plan closes

### A - [lexer-and-language-findings](../../TODO/lexer-and-language-findings.md)

- [x] T16 | T16 -- Declare Rust's spanning quotes; language.py:117-146 carries
      none. Verify: a Rust multi-line string is neither refused wholesale nor
      read as comments.
- [x] T27 | T27 -- Declare Rust's `//!` inner; `///` stays outer. Verify: a
      `.rs` opening `//!` above nothing types `docstring`, and `///` above
      nothing types `comment`.
- [x] T32 | Recognize raw string delimiters in lexer.py:510; verify a quoted
      marker inside a Rust raw string stays literal data
- [x] T49 | State Rust's inner doc openers in Rust's own definition file

### B - [matter-misses-two-languages](../../TODO/matter-misses-two-languages.md)

- [x] T2 | T2 -- Stop a Rust file's opening `//` run being claimed as a
      declaration's doc. Verify: a `.rs` opening `// Copyright` types `f0
      matter` and an empty `a1`.

### C - [fixtures-do-not-test-the-shape](../../TODO/fixtures-do-not-test-the-shape.md)

- [x] T2 | T2 -- Make `tests/fixtures/sample.rs` open the way a licence header
      does, or add a `.rs` fixture that does. Verify: it reproduces
      `matter-misses-two-languages`.

## Plan Tasks

- [x] P1 | Rust definition, validator, binding installed; row removed; review clean | 3f1a4817 | Install
      the Rust definition file, its validator and the rust-lexical binding
        > 2026-10-22 Spec: Order of work 1; removes the rust LANGUAGES row
        > 2026-10-22 Check: pytest -k rust_definition; .rs gives rust-lexical
        > 2026-10-22 Check: grep finds no rust row in reading/language.py
- [x] P2 | Validated Rust records; 29 records tests; review clean | 33474b0d | Represent
      a validated Rust read in reading/rust/records.py
        > 2026-10-22 Check: pytest tests/reading/test_rust.py -k records
- [x] P3 | Rust comment scanner partitions the source; review clean | 51e270cf | Read
      Rust comments into regions that partition the source
        > 2026-10-22 Spec: nested blocks, the six comment forms, exact source
        > 2026-10-22 Check: test_rust.py -k comments, plus BOM/CRLF/no-EOL cases
- [x] P4 | FINISHED: the Rust scanner reads literals, lifetimes and attributes from rust.toml keys; task review and re-review clean | b239c6ca | Read
      Rust literals by the prefix boundary rule
        > 2026-10-22 Spec: strings, raw, byte and C strings; char against lifetime
        > 2026-10-22 Check: test_rust.py -k literals and -k quotes
        > 2026-10-22 Check: a marker inside a raw string stays literal data
- [x] P5 | FINISHED: Rust owners are placed from a body-kind stack where the head leads its line, filtered by rust.toml owners; task review and re-reviews clean | e2027267 | Find
      Rust owners from the body-kind stack
        > 2026-10-22 Spec: heads start at the first attribute (Addressing #30)
        > 2026-10-22 Check: test_rust.py -k owners, -k heads and -k macros
- [x] P6 | FINISHED: Rust documentation binds to its owner; detached runs warn one-to-one; a0, shebang and f0 matter decided; task review and re-review clean | 7b4fce41 | Bind
      Rust documentation to its owner
        > 2026-10-22 Spec: detached runs warn (Addressing #29); a0; shebang; f0
        > 2026-10-22 Check: test_rust.py -k attachment, -k detached, -k matter
        > 2026-10-22 Check: test_rust.py -k directives; // Copyright gives f0
- [x] P7 | Rust reads compose into RustRead with paragraphs, code and declarations; ReaderRecord protocol in reading/proof.py, satisfied by PythonRead; projection tests and ty clean | 239c0a77 | Derive
      paragraphs, code and declarations from a Rust read
        > 2026-10-22 Spec: ReaderRecord protocol satisfied by both records
        > 2026-10-22 Check: test_rust.py -k projection; ty check is clean
- [x] P8 | page_for builds pages from any ReaderRecord; Rust pages give the expected cues and warnings and every probe shape round-trips; Python and generic pages byte-identical over 1,377 files | b9c5ed1e | Build
      a page from any ReaderRecord in binder/page.py
        > 2026-10-22 Spec: O1 and O2, approved 2026-10-22
        > 2026-10-22 Check: build(text, name="m.rs") gives the expected cues
        > 2026-10-22 Check: the Python page suite passes unchanged
- [x] P9 | RustRead.proof/preserved compare code with prose comments removed; every listed mutation fixture fails and every prose change passes (test_lexical_preservation -k rust, 43 passed) | 4f7e6d7a | Prove
      Rust preservation on both comparison paths
        > 2026-10-22 Check: test_lexical_preservation -k rust
        > 2026-10-22 Check: each mutation fixture fails; each prose change passes
- [x] P10 | gather prints one stderr warning line per detached run, exit code and binder unchanged; detached documentation defined in docs/vocabulary.md (toml move filed as stage-two-detached-warnings T2) | f696f274 | Print
      detached-documentation warnings from gather
        > 2026-10-22 Spec: O3 and O5, approved 2026-10-22; exit code unchanged
        > 2026-10-22 Check: test_gather_command -k detached
        > 2026-10-22 Check: check_vocabulary.py exits 0 with the new term
- [x] P11 | TODO/stage-two-detached-warnings.md exists with Owner: agents | a073b5bd | Create
      the agents TODO for SKILL.md stage 2 warnings
        > 2026-10-22 Spec: O4, approved 2026-10-22; agents lane edits SKILL.md
        > 2026-10-22 Check: the TODO exists with Owner: agents
- [x] P12 | revision-1 and pre-reader Rust contexts are refused (page_of: reading-context-mismatch; saved artifacts: regather); a Rust context survives gather through drafting; existing Rust cases pass (test_reading_context -k rust; full suite 5400 passed) | b9ef359e | Refuse
      a revision-1 Rust reading context
        > 2026-10-22 Spec: old Rust cases pass or are superseded case by case
        > 2026-10-22 Check: test_reading_context -k rust; full suite green
        > 2026-10-22 Check: ruff, ty and check_shipped_syntax.py pass
- [x] P13 | Full /comment-review over a local edition-2021 crate (9 src files): every file read by rust-lexical; cargo check passed before and after; prove_unchanged against the pre-edit ref exited 0 (3 pages PROVEN); 3 places written; worktrees removed by hand | 288639bc | Run
      /comment-review end to end on a local Rust crate
        > 2026-10-22 Check: cargo check before and after; prove_unchanged exits 0
        > 2026-10-22 Check: every file read by rust-lexical; worktree removed by hand
        > 2026-10-22 Spec: the crate is named nowhere in this repo
