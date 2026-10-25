# A reader finds prose and rebuilds nothing after it

```
Status:   open
Progress: 9 of 20 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #224)
```

## Objective

A reader supplies what only parsing can find -- each paragraph's span, its raw
lines, its kind and its anchor. Everything that follows from those is derived
once for every language: `Paragraph` derives its own fields, the page places it,
and the addresser addresses it, as they did for Python before the lexical
readers. decision-log.md Process: #224.

Measured 2026-10-25: the lexer (`_join`), the Python reader
(`reading/python/projection.py`) and the Rust reader
(`reading/rust/projection.py`) each build `Paragraph.text` their own way, and
the Python and Rust readers stamp `address` themselves. `lines` was the same
defect and is repaired (lexer-and-language-findings T12, b30cc510).

## Tasks

- [x] T1 | Paragraph.text is comment_form text, set once after the reader | d8a5666a | Derive
      Paragraph.text in one place for every reader
        > 2026-10-25 Check: one comment in .py, .rs and .go reads the same text
        > 2026-10-25 Check: no reader passes text to Paragraph
- [ ] T2 | Assign each paragraph's address in the page instead of in a reader
        > 2026-10-25 Check: git grep finds no address= in reading/python or reading/rust
- [x] T3 | Nine duties filed as T4-T12, each naming file:line | 17c030f6 | List
      each Paragraph, Page or Addresser duty a reader still performs
        > 2026-10-25 Check: each duty is a task on this file naming its file:line
- [-] T4 | Readers own code text (#228); reissued as T18 | 56d0e3d1 | Derive
      each line's code in the page for every reader
        > 2026-10-25 python/projection.py:212 and rust/projection.py:327 code_for
        > 2026-10-25 Rust keeps a literal's trailing space: c0 anchor+raw breaks line 1
        > 2026-10-25 Check: no def code_for under reading/python or reading/rust
        > 2026-10-25 Check: every margin anchor + raw_lines[0] equals its line, .rs
- [ ] T5 | Give a Python docstring paragraph its whole source lines
        > 2026-10-25 python/projection.py:136 cuts raw_lines at the statement end
        > 2026-10-25 Reason: in """doc""" \ the \ belongs to no place; set drops it
        > 2026-10-25 Check: that input sets back identical through set_page
- [ ] T6 | Delete the continues-a-trailing-comment stamp from lexer.py
        > 2026-10-25 lexer.py:846; the Python and Rust readers never stamp it
        > 2026-10-25 Reason: nothing in src or src/plugin reads the annotation
        > 2026-10-25 Check: git grep continues-a-trailing-comment -- src returns none
- [x] T7 | Ruled: matter is a Kind the reader assigns | c59b3424 | Decide
      whether matter is a kind a reader assigns or a page place
        > 2026-10-25 Reason: #224 gives kind to the reader; matter is position-only
        > 2026-10-25 Copies: lexer.py:765-823, python/projection.py:146-187
        > 2026-10-25 Copies: rust/projection.py:185-254, rust/documentation.py:372
        > 2026-10-25 Roy: the reader assigns matter; decision-log.md Process: #225
- [ ] T8 | Move the front and back matter rule to one shared place
        > 2026-10-25 Waits on the matter ruling in this file
        > 2026-10-25 Rust holds two copies: documentation.py:182 and projection.py:205
        > 2026-10-25 Check: .rs and .kt give the same f places on matter-only input
        > 2026-10-25 Per #225 the reader assigns matter; a helper may share the rule
- [-] T9 | #226: sectioning is the reader's; reissued as T14 | cf911ec9 | Move
      the one-paragraph-per-place rule from the Rust reader to the page
        > 2026-10-25 rust/projection.py:139 _one_per_place; Rust spec lines 227-232
        > 2026-10-25 Reason: page.py:904-910 assigns cues and never checks for a clash
        > 2026-10-25 Check: no _one_per_place under reading/rust; Rust tests pass
- [-] T10 | #226: detaching a doc assigns a kind; reader's | cf911ec9 | Move the
      Rust reader's a-place capacity rules to the page
        > 2026-10-25 rust/documentation.py:211-247,281-290: _beside, _outer, _attach
        > 2026-10-25 Reason: which item owns a doc is grammar; what a place holds is not
        > 2026-10-25 Suspected, not shown to disagree; Rust spec lines 202-221
        > 2026-10-25 Check: the three detach reasons are decided outside reading/rust
- [-] T11 | #226: page drops it; reissued as T15 | cf911ec9 | Carry detached
      documentation as one fact instead of two
        > 2026-10-25 rust/projection.py:132 annotation and page.py:940-976 warning
        > 2026-10-25 Suspected redundant; no input found where the two disagree
        > 2026-10-25 Check: one of the two is gone; the gather warning still prints
- [ ] T12 | Replace the Rust reader's _Lines with the shared line splitter
        > 2026-10-25 rust/projection.py:368-389 copies constants.text_lines
        > 2026-10-25 Check: git grep "class _Lines" -- src returns none
- [ ] T13 | Stop the page changing a reader's matter kind to comment
        > 2026-10-25 page.py:898-899 turns MATTER into COMMENT when it has an a address
        > 2026-10-25 Reason: #225, the reader assigns the kind; the page only addresses
        > 2026-10-25 Check: git grep "b.kind = Kind" -- src/comment_review/binder: none
- [ ] T14 | Form one comment section per gap in the Rust reader
        > 2026-10-25 A detached doc joins the comments around it; #226
        > 2026-10-25 Replaces rust/projection.py:139 _one_per_place merging afterward
        > 2026-10-25 Check: a detached /// between // lines reads as one b comment
        > 2026-10-25 Check: no _one_per_place under reading/rust
- [ ] T15 | Remove the page's detached-documentation placement
        > 2026-10-25 page.py:940-976 _warnings, PageWarning; rust/projection.py:132
        > 2026-10-25 Reason: #226, the warning names a file and line from the read
        > 2026-10-25 Check: git grep -E "PageWarning|DETACHED_DOCUMENTATION" -- src
        > 2026-10-25 Check: gather prints the warning as file:line
        > 2026-10-25 Reason: several detached docs merged at one b cue read the same
- [-] T16 | Filed with another task's notes; reissued as T20 | cb6a5005 | Move
      the lexical path's code lines and declarations into its reader
        > 2026-10-25 Design: docs/superpowers/specs/2026-10-25-code-lines-design.md
        > 2026-10-25 Check: no def documentable in binder/page.py
        > 2026-10-25 Check: fn a() {} fn b() {} gives one documented line, one warning
- [-] T17 | Filed with another task's notes; reissued as T18 | cb6a5005 | Correct
      each reader's code text
        > 2026-10-25 Check: page builds places without code_lines or declarations
        > 2026-10-25 Check: corpus address dump unchanged for two lexical languages
- [ ] T18 | Correct each reader's code text
        > 2026-10-25 Check: every .rs margin anchor + raw_lines[0] equals its line
        > 2026-10-25 Check: the Python backslash docstring sets back byte-identical
- [ ] T19 | Return CodeLines from the Python and Rust readers
        > 2026-10-25 Design: docs/superpowers/specs/2026-10-25-code-lines-design.md
        > 2026-10-25 Check: no def documentable in binder/page.py
        > 2026-10-25 Check: fn a() {} fn b() {} gives one documented line, one warning
- [ ] T20 | Move the lexical path's code lines and declarations into its reader
        > 2026-10-25 Check: page builds places without code_lines or declarations
        > 2026-10-25 Check: corpus address dump unchanged for two lexical languages
