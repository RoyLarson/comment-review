# Outside Python the `a` place is emitted and never filled

```
Status:   open
Progress: 0 of 12 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
Traced:   2026-08-21 — 2026-08-21 -- IT IS A MISSING WIRE, and both halves already
          exist. The lexer gets the KIND right (it reads doc_line and doc_block off the
          Language row, so '/// The name.' censuses as kind=docstring) and
          page.documentable() already computes which declaration a doc belongs to -- on
          Rust it answers {0: 3}, meaning declaration 0's doc goes on line 3, exactly
          where the doc comment is. Nothing joins the two: paragraphs_lexical never sets
          Paragraph.declares, so attach() falls past its FIRST branch (declares >= 0 ->
          the declaration's a) and lands on above() -> a b place. ! So this is not an
          inference problem and needs no text finder. The 10 languages with a declares
          keyword list can be wired from what is already computed.
Ruled:    2026-08-21 — 2026-08-21 -- the criterion is a C round trip, not an argument
          about keyword recall. Measured on CPython v3.13.1 while settling it: a keyword
          list finds the anchor line for 92.9% of definitions, and 81.1% of its false
          positives are lines nobody documented.
Condition: 2026-08-22 — THE C CONDITION IS MET. Roy set it as a demonstration, not an
           argument: *"if we can show that we can round trip the comments correctly in a
           c document ... with the a foliation then we add it back."* MEASURED
           2026-08-22: 489 of 489 `.c` and `.h` files in `corpora/cpython` round trip
           IDENTICAL, zero differ, zero crash. ! So the ruling is not a standing refusal
           -- it is a conditional whose condition has since been satisfied and never
           cashed in. ! WHAT IS ACTUALLY BLOCKING IS THE WIRE, the task two lines below
           this one: `paragraphs_lexical` never sets `Paragraph.declares` from what
           `page.documentable()` already computes, so the `a` series fills for NO
           lexical language -- Rust, Go, Java, all sixteen -- not for C alone. MEASURED
           the same day: 205 `a` places over 19 Python files on the AST tier, and 0 over
           180 cpython C and H files. ! Roy, 2026-08-22, on reading the current state:
           *"I swear this problem was solved."* Half of it was: the demonstration
           passed. The half that fills the place did not.
```

## Objective

Outside Python the `a` place is emitted and never filled.

## Tasks

- [ ] !! MEASURED 2026-08-21. `/// The name.` above `pub fn f()` in Rust censuses
      `a1 undocumented declares=1` AND `b0 docstring 'The name.'` -- the place
      says the function is undocumented while its documentation sits in the gap.
      Same for `.go`, `.java`, `.ts`, `.cs`.
- [ ] `Paragraph.declares` is set only in `paragraphs_stdlib` and on synthetic
      empty places. `paragraphs_lexical` never sets it, so `attach` falls through
      to `above()` for every doc comment in every lexical language.
- [ ] ! SO function-context CAN FILE AN `add` FOR PROSE THAT ALREADY EXISTS, and
      ownership-context reads a doc comment as a gap paragraph.
- [ ] ! CLAUDE.md's claim that the keyword lists made an `a` place resolve for
      eleven languages holds for EMITTING the place, not for ever filling it. 16
      of 17 languages are affected.
- [ ] !! THE ACCEPTANCE TEST IS A ROUND TRIP, ruled by Roy 2026-08-21: *"if we can
      show that we can round trip the comments correctly in a c document (assuming
      the documentation doesn't have typographical errors) with the a foliation
      then we add it back. If it causes errors then we leave all of them as b and
      a's do not get populated and are not queriable/settable in the program. That
      is an easy out for the language."* So this closes on a DEMONSTRATION, not on
      an argument about whether a keyword list can recognise a declaration.
- [ ] ! THE FALLBACK IS A REAL OUTCOME, NOT A FAILURE. If the round trip errors, C
      keeps `declares=()`: every paragraph stays `b`, no `a` is populated, and an
      `a` is neither queriable nor settable for that language. A language opting
      out is a supported state -- `yaml`, `toml-ini` and `sql` are already in it.
- [ ] Wire it: `paragraphs_lexical` sets `Paragraph.declares` from what
      `page.documentable()` already computes. Both halves exist -- see `Traced:`
      above. This is the load-bearing change and it covers all 16 lexical
      languages, not C alone.
- [ ] The join rule is NEAREST-ABOVE, not adjacency. MEASURED 2026-08-21 on
      CPython v3.13.1 (`corpora/cpython`, 489 `.c`/`.h` files): of 2,987
      documented column-0 declaration lines, 1,863 (62%) carry a comment flush
      against them and 1,124 (38%) have a blank line between. A strict `end + 1 ==
      insert` test abandons that 38% in `b`. The nearest comment paragraph above
      the declaring line takes the `a`.
- [ ] * RULING SETTLED, and it is Roy's reframe of the criterion: the anchor is
      the line the KEYWORD is on, and a declaration spilling onto the next
      physical line is not this system's problem. Roy, 2026-08-21: *"The line
      static ... is where a belongs and the documentation above is where it should
      go. The fact that the next line is a separate line of code which is
      implicitly referred to from the previous line is not our problem."*
      `lexer.declarations` already encodes this -- it returns `(line, insert)`
      where `insert` IS the keyword line for every above-doc language.
- [ ] ! PRECISION IS NOT THE OBJECTION IT LOOKED LIKE. MEASURED on CPython: 15,813
      column-0 lines carry a whitespace-delimited C keyword and only ~6,850
      declare a function -- but 12,826 of them (81.1%) have NO comment above them
      at all. A spurious `a` on a non-declaration is therefore an EMPTY PLACE that
      nothing ever fills, which is the cost the round-trip test measures directly.
- [ ] ! RECONSTRUCTION IS NOT WHAT A SHARED ADDRESS BREAKS -- VERIFICATION IS.
      WRITE works from `start`/`end` spans, so prose returns where it came from
      whatever folio it carries. What fails is `record.entry_for`, which resolves
      by address and returns the FIRST match: a correct edit to the second
      paragraph is checked against the first and `verdicts.py` exits 1. So the
      round-trip test must exercise the JOIN, not just the write -- a test that
      only proves bytes come back will pass while the gate still refuses the edit.
- [ ] Reverse the C ruling only if the round trip holds. CLAUDE.md records the
      empty tuple for C/C++ as deliberate (*"a C function opens with its RETURN
      TYPE, so the list could never be complete, and a spurious `a` renumbers
      every `a` below it"). That text needs updating or reaffirming with whichever
      way this lands, and the renumbering half stays true either way -- it is
      bounded to one run, since records are seeded per-run and census, reviewers
      and WRITE all see one numbering.
