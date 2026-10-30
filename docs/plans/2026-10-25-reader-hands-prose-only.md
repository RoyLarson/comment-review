# A reader hands over only what parsing finds

```
Status:   in-progress
Progress: 29 of 43 TODO tasks closed
Plan-tasks: 24 of 24 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (founded by move-t from 2026-10-11-lexical-readers)
```

## Objective

A reader hands over only what parsing finds -- span, raw lines, kind and anchor
(Process #224; matter is a reader-assigned kind, #225; a detached doc is a
comment, #226). Paragraph derives text, the page derives each line's code and
assigns every address, and the page changes no kind and holds no
detached-documentation logic. Branch: feat/reader-hands-prose-only, based on
feat/lexical-readers, returned by no-ff merge. Subagent-driven, with a review
per step; each step lands its failing test first.

## TODO tasks this plan closes

### A - [a-reader-finds-prose-only](../../TODO/completed/a-reader-finds-prose-only.md)

- [x] T1 | Derive Paragraph.text in one place for every reader
- [x] T2 | Assign each paragraph's address in the page instead of in a reader
- [-] T4 | Derive each line's code in the page for every reader
- [x] T5 | Give a Python docstring paragraph its whole source lines
- [x] T6 | Delete the continues-a-trailing-comment stamp from lexer.py
- [x] T8 | Move the front and back matter rule to one shared place
- [x] T12 | Replace the Rust reader's _Lines with the shared line splitter
- [x] T13 | Stop the page changing a reader's matter kind to comment
- [x] T14 | Form one comment section per gap in the Rust reader
- [x] T15 | Remove the page's detached-documentation placement
- [-] T16 | Move the lexical path's code lines and declarations into its reader
- [-] T17 | Correct each reader's code text
- [x] T18 | Correct each reader's code text
- [x] T19 | Return CodeLines from the Python and Rust readers
- [x] T20 | Move the lexical path's code lines and declarations into its reader
- [x] T21 | Trim each Rust code line by the scanner's whitespace regions
- [x] T22 | Read a doc comment that trails code as a trailing comment
- [x] T23 | Cut file matter from the reader's runs, not a per-line prose mask
- [x] T24 | Give the <eof> a its own position in a file with no code line
- [x] T25 | Resolve the <eof> a through the addresser command
- [x] T26 | Derive a parenthesised Python docstring's text from its literal
- [x] T27 | Match a comment marker after a leading byte-order mark
- [x] T28 | Prove a lexical file whose prose lines end in whitespace
- [x] T29 | Attach a doc run above an annotation line to the declaration below

### B - [reader-review-repairs](../../TODO/reader-review-repairs.md)

- [-] T1 | Decide how a drop beside a #245 partner place reads back
- [ ] T2 | Track the previous comment by line in Comment._without_range
- [ ] T3 | Replace the gap scan's membership tests with a bisect
- [ ] T4 | Reduce _cut_gap to one rule with no early-return path
- [ ] T5 | Stop using Kind as a message between read steps
- [ ] T6 | Move the foot's matter rule into reading/matter.py
- [ ] T7 | State the multi-line anchor in _change_problems and the vocabulary
- [ ] T8 | Mark _cut_by_place provisional in the code
- [-] T9 | Delete _partner's no-code branch, which no draft reaches
- [-] T10 | Move _partner's rule beside the place rule it depends on
- [-] T11 | Make _written_once check position, with a failing test each guard
- [ ] T12 | Delete the dead conditions in the lexer
- [ ] T13 | Replace the Cues count-stamped caches with cached_property
- [ ] T14 | Correct the comments that disagree with the code
- [-] T15 | Remove the reader anchor the page discards
- [ ] T16 | Give anchor_line one meaning across reader and page
- [ ] T17 | State a unit once, in joins or in DocPlace.at
- [ ] T18 | Check a draft by where its text landed, per #247

### C - [lexer-and-language-findings](../../TODO/lexer-and-language-findings.md)

- [ ] T53 | Make every comment above a module docstring front matter, per #240

## Plan Tasks

- [x] P1 | One derivation (comment_form, #227); reviewed clean | d8a5666a | Derive
      Paragraph.text in Paragraph for every reader
        > 2026-10-25 Check: one comment in .py, .rs and .go reads the same text
        > 2026-10-25 Works a-reader-finds-prose-only T1
- [x] P2 | FINISHED: page assigns every address from anchor_line; doc-kind-unresolved retired; reviewed clean after 2 fix rounds | 20cbdbbd | Assign
      every paragraph's address in the page
        > 2026-10-25 Check: no address= in reading/python or reading/rust; suite green
        > 2026-10-25 Works T2
        > 2026-10-25 49389b6f reverted in e699deaf; redo on anchor_line after P13
        > 2026-10-25 Doc paragraphs are Kind.DOCSTRING; anchor_line names it (#229)
        > 2026-10-25 Redo after P16, not P13 (P13 superseded)
- [x] P3 | FINISHED: retype deleted (unreachable after P2); addresses unchanged by probe | 9ac42812 | Stop
      the page changing a reader's matter kind
        > 2026-10-25 Check: git grep "b.kind = " -- src/comment_review/binder: none
        > 2026-10-25 Works T13; needs P2
- [-] P4 | Readers own code text (#228); replaced by P15 | 56d0e3d1 | Derive
      each line's code in the page for every reader
        > 2026-10-25 Check: every .rs margin anchor + raw_lines[0] equals its line
        > 2026-10-25 Check: no def code_for under reading/python or reading/rust
        > 2026-10-25 Works T4
- [x] P5 | FINISHED: docstring holds its whole closing line; ; + code stays code; reviewed | 6a6f8659 | Give
      a Python docstring paragraph its whole source lines
        > 2026-10-25 Check: the """doc""" \ input sets back byte-identical
        > 2026-10-25 Works T5
        > 2026-10-25 Takes P15's Python case: doc span runs to line end
- [x] P6 | FINISHED: continues-a-trailing-comment deleted; 657 lexical files unchanged | 40f55321 | Delete
      the continues-a-trailing-comment stamp
        > 2026-10-25 Check: git grep continues-a-trailing-comment -- src: none
        > 2026-10-25 Works T6
- [x] P7 | FINISHED: one matter rule (#232); a at eof (#233, #234); reviewed, 1 fix round | 58727f6f | State
      the matter rule once in reading for every reader to call
        > 2026-10-25 Check: one definition; .rs and .kt give the same f places
        > 2026-10-25 Works T8
        > 2026-10-26 Also #233: a emits at eof; a series from doc practice
- [x] P8 | Sections formed once; post-merge removed; 5466 passed | 431d1614 | Form
      one comment section per gap in the Rust reader
        > 2026-10-25 Check: a detached /// between // lines reads as one b comment
        > 2026-10-25 Check: no _one_per_place under reading/rust
        > 2026-10-25 Works T14
- [x] P9 | Page warning placement removed; reviewed clean | 2d9c6652 | Remove
      the page's detached-documentation placement
        > 2026-10-25 Check: no PageWarning or DETACHED_DOCUMENTATION in src
        > 2026-10-25 Check: gather prints the warning as file:line
        > 2026-10-25 Works T15; after P8
        > 2026-10-25 Lands before P13: drops warning_owners, the last ordinal
        > 2026-10-25 Lands before P16, not P13 (P13 superseded)
- [x] P10 | FINISHED: _Lines replaced by shared line_span; 1647 .rs identical | 943ec462 | Replace
      the Rust reader's _Lines with the shared line splitter
        > 2026-10-25 Check: git grep "class _Lines" -- src returns none
        > 2026-10-25 Works T12
- [x] P11 | FINISHED: Rust spec states the page, addresser and shared owners; dead names gone | 5ad6ad3c | Amend
      the Rust spec where it gives the reader page duties
        > 2026-10-25 Spec lines 227-241 and 373-381; after P8 and P9
        > 2026-10-25 Check: those sections name the page or addresser as owner
        > 2026-10-25 Also amend the spec's code_for and declarations sections (#228)
- [x] P12 | FINISHED: 5552 passed; ruff, format, ty, shipped syntax, vocabulary green; suite 248s vs base 251s | ed4abb5b | Run
      the completion gates on the finished subplan
        > 2026-10-25 Check: pytest, ruff, ty, shipped syntax and vocabulary all green
- [-] P13 | Carries another step's notes; reissued as P17 | cb6a5005 | Move the
      lexical path's code lines and declarations into its reader
        > 2026-10-25 Works T16; after P9; design 2026-10-25-code-lines-design.md
        > 2026-10-25 Check: no def documentable in binder/page.py
        > 2026-10-25 Check: DocPlace(at, above=False) sets the a after at
- [-] P14 | Carries another step's notes; reissued as P15 | cb6a5005 | Correct
      each reader's code text
        > 2026-10-25 Works T17; after P13
        > 2026-10-25 Check: corpus address dump unchanged for two lexical languages
- [x] P15 | FINISHED: Rust literal whitespace trimmed; Python case moved to P5 | 573eb183 | Correct
      each reader's code text
        > 2026-10-25 Works T18; replaces P4
        > 2026-10-25 Check: Rust margins rebuild; Python backslash case round-trips
- [x] P16 | FINISHED: CodeLine/DocPlace from both readers; cue walks CodeLines; review clean after 1 fix round | 7962289d | Return
      CodeLines from the Python and Rust readers
        > 2026-10-25 Works T19; after P9; design 2026-10-25-code-lines-design.md
        > 2026-10-25 Check: no def documentable in binder/page.py
        > 2026-10-25 Check: DocPlace(at, above=False) sets the a after at
- [x] P17 | FINISHED: lexical reader returns CodeLines; one page path; review clean after 1 fix round | 456902d3 | Move
      the lexical path's code lines and declarations into its reader
        > 2026-10-25 Works T20; after P16
        > 2026-10-25 Check: corpus address dump unchanged for two lexical languages
- [x] P18 | FINISHED: T22 T23 T29; review clean after 4 fix rounds | 555b457d | Classify
      each lexical run once as whole-line or sharing code
        > 2026-10-26 Works T22, T23, T29; reader only, no compositor edit
- [x] P19 | FINISHED: T21 T27 T28; review clean after 2 fix rounds | f821db13 | Apply
      each reader's own whitespace definition to code and prose
        > 2026-10-26 Works T21, T27, T28
- [x] P20 | FINISHED: T24 T25; review loop 5 rounds + 1 approved by Roy | 4535709f | Give
      the <eof> a a position and an addresser route apart from a0
        > 2026-10-26 Works T24, T25; after P18
- [x] P21 | FINISHED: T26; controller-verified through the page | f53ceefb | Derive
      a parenthesised Python docstring's text from its literal
        > 2026-10-26 Works T26
- [x] P22 | FINISHED: page_for refuses a shared address; corpus 3002 files, 0 refused | f5a0fac1 | Refuse
      a page where two paragraphs share an address
        > 2026-10-27 Roy 2026-10-27: add the error, with tests that try to break it
- [x] P23 | FINISHED: head docs split per #245; review clean after 1 fix round | ba1cb4a8 | Split
      two head docs into a0 and the declaration's a, per #245
- [x] P24 | FINISHED: write chain accepts the partner re-read; 28 dockets tried | e78f6ebf | Accept
      a head or foot doc re-read at its partner place, per #245
