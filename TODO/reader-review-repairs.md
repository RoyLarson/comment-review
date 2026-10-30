# Repair what the reader-hands-prose-only review found

```
Status:   open
Progress: 7 of 18 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-30 (/broken-review, 2026-10-30, 0abe0010..106b767d)
```

## Objective

Repair what the reader-hands-prose-only review found.

## Tasks

- [-] T1 | SUPERSEDED by T18, per #247 | 0f9cf8f8 | Decide how a drop beside a
      #245 partner place reads back
        > 2026-10-30 W1 D3 I6: proof_setter.py:548; base accepted, branch aborts the run
- [ ] T2 | Track the previous comment by line in Comment._without_range
        > 2026-10-30 I2: comment.py:156; /* a */ /* b */ /* c */ minus b c merges lines
- [ ] T3 | Replace the gap scan's membership tests with a bisect
        > 2026-10-30 I5: lexer.py:1301,1371; 16k lines 17.9s, 4.6x per doubling
- [ ] T4 | Reduce _cut_gap to one rule with no early-return path
        > 2026-10-30 I3: lexer.py:1341-1456; two mutants pass alone, fail together
- [ ] T5 | Stop using Kind as a message between read steps
        > 2026-10-30 I4: lexer.py:1372,1627; flipped to COMMENT, restored in _cut_gap
- [x] T6 | FINISHED: one matter rule in matter.py; _cut_gap's back branch gone | 70f1f028 | Move
      the foot's matter rule into reading/matter.py
        > 2026-10-30 A2: _cut_gap's back branch is a second home for #240, #243
        > 2026-10-30 #246: landing with lexer-and-language-findings T53, here
- [ ] T7 | State the multi-line anchor in _change_problems and the vocabulary
        > 2026-10-30 D1: guard compares single lines; vocabulary.toml:19 says one
- [ ] T8 | Mark _cut_by_place provisional in the code
        > 2026-10-30 A1: #244 defers it; conventions require the marking
- [-] T9 | SUPERSEDED by T18, per #247 | 0f9cf8f8 | Delete _partner's no-code
      branch, which no draft reaches
        > 2026-10-30 A4: StrippedRead refuses no-code files; lexical-code-identity T7
- [-] T10 | SUPERSEDED by T18, per #247 | 0f9cf8f8 | Move _partner's rule beside
      the place rule it depends on
        > 2026-10-30 A3: page-model fact in a flow, coupled to _cut_gap's #245 rule
- [-] T11 | SUPERSEDED by T18, per #247 | 0f9cf8f8 | Make _written_once check
      position, with a failing test each guard
        > 2026-10-30 D4 I10: proof_setter.py:574-610; no test fails on 3 guards
- [ ] T12 | Delete the dead conditions in the lexer
        > 2026-10-30 I8: lexer.py:870,1110,1031,1312; mutants pass the full suite
- [ ] T13 | Replace the Cues count-stamped caches with cached_property
        > 2026-10-30 I9: addresser.py:451-576; stamp guards a mutation that never occurs
- [ ] T14 | Correct the comments that disagree with the code
        > 2026-10-30 I13: lexer.py:966,1074,1272,1565,70; addresser.py:600,724,779
- [-] T15 | SUPERSEDED by one-reader-builder T7; Roy moved it | 4494431b | Remove
      the reader anchor the page discards
        > 2026-10-30 A8: 5 of 5 probes identical blanked; 4 MODULE_ANCHOR stamps dropped
- [ ] T16 | Give anchor_line one meaning across reader and page
        > 2026-10-30 D5: Java line 3 from reader, 2 from page; T51 would break owner_at
- [ ] T17 | State a unit once, in joins or in DocPlace.at
        > 2026-10-30 D9: both say it and nothing checks they agree
- [x] T18 | FINISHED: re-read asks landed, dropped, unchanged, by code-line count; chain passes | f71e1a17 | Check
      a draft by where its text landed, per #247
        > 2026-10-30 Check: Roy's chain: add a1, reads a0, unchanged, move, original
        > 2026-10-30 'original' means the draft from step 1, byte-identical
        > 2026-10-30 Roy: blank doc = blank docstring on function f() {}; no T7 needed
