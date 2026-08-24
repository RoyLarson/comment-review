# Outside Python the `a` place is emitted and never filled

```
Status:   open
Progress: 17 of 18 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
Traced:   2026-08-21 — 2026-08-21 -- IT IS A MISSING WIRE, and both halves already
          exist. The lexer gets the KIND right (it reads doc_line and doc_block off the
          Language row, so '/// The name.' censuses as kind=docstring) and
          page.documentable() already computes which declaration a doc belongs to.
          Nothing joined the two: paragraphs_lexical never set Paragraph.declares, so
          attach() fell past its FIRST branch and landed on above() -> a b place.
Ruled:    2026-08-21 — the criterion is a C round trip, not an argument about keyword
          recall. Measured on CPython v3.13.1 while settling it: a keyword list finds
          the anchor line for 92.9% of definitions, and 81.1% of its false positives
          are lines nobody documented.
Condition: 2026-08-22 — THE C CONDITION IS MET. Roy set it as a demonstration, not an
           argument: *"if we can show that we can round trip the comments correctly in a
           c document ... with the a foliation then we add it back."* MEASURED
           2026-08-22: 489 of 489 `.c` and `.h` files in `corpora/cpython` round trip
           IDENTICAL, zero differ, zero crash.
TRIAGED:  2026-08-23 — 15 of 18 boxes were measurements, rulings, quoted specs or
          argument, and are ticked into the Objective. Of the three that were tasks, TWO
          HAVE LANDED and are ticked done: the WIRE (T7) and the CLAUDE.md text (T12).
          One is open: T18, match the keyword anywhere in the line. ! `Requires-Roy` is
          set FALSE, from `true`: every ruling this file waited on has been made -- the
          anchor 2026-08-21, the C condition met 2026-08-22, and the match-anywhere
          change authorised by Roy 2026-08-23.
```

## Objective

!! **THE TITLE IS FALSE AS OF 2026-08-23 FOR EVERY LANGUAGE BUT TWO, AND THE WIRE IS WHY.**
`page.py:726` calls `document_declarations(got, declarations(text, lang, code), code)`, and
`lexer.py:1617` sets `held.declares = ordinal` on the run that documents each declaration.
MEASURED today by censusing the fixtures, one per language:

| fixture | what the `a` series does |
| --- | --- |
| `sample.rs` | `@a1 1-4 docstring` on `pub fn add(...)` |
| `sample.go` | `@a1`, `@a2`, `@a3` filled |
| `sample.java` | `@a1` on the class, `@a2` on the method |
| `sample.ts` `sample.kt` `sample.swift` `sample.cs` `sample.rb` | filled |
| `sample.c` | **no `a` series at all** |

! So the residual is not a wire and not a fill rule: it is that `c` and `cpp` carry an EMPTY
`declares` tuple (`language.py:185-209`), because `_declares_here` reads a line's FIRST word or
its first two, and a C declaration opens with its RETURN TYPE.

## The measurement this file was opened on, and what it now reads

- **2026-08-21.** `/// The name.` above `pub fn f()` in Rust censused `a1 undocumented
  declares=1` AND `b0 docstring 'The name.'` -- the place said the function was undocumented
  while its documentation sat in the gap. Same for `.go`, `.java`, `.ts`, `.cs`. **That is
  fixed**: measured 2026-08-23, the doc comment takes the `a`.
- The consequence that made it expensive -- `function-context` filing an `add` for prose that
  already exists, and `ownership-context` reading a doc comment as a gap paragraph -- went with
  it.
- `CLAUDE.md`'s claim that the keyword lists made an `a` place resolve for eleven languages was
  true of EMITTING the place and not of filling it. It is true of both now for 16 of 18
  languages; `c` and `cpp` are the two that are not, and four more -- `sql`, `toml`, `ini`,
  `yaml` -- have no `a` series by design.

## The rulings, all made

!! **THE ACCEPTANCE TEST IS A ROUND TRIP.** Roy, 2026-08-21: *"if we can show that we can round
trip the comments correctly in a c document (assuming the documentation doesn't have
typographical errors) with the a foliation then we add it back. If it causes errors then we
leave all of them as b and a's do not get populated and are not queriable/settable in the
program. That is an easy out for the language."* The condition was met 2026-08-22 -- 489 of 489
files identical -- and has never been cashed in.

! **THE FALLBACK IS A REAL OUTCOME, NOT A FAILURE.** If the round trip errors, C keeps
`declares=()`: every paragraph stays `b`, no `a` is populated, and an `a` is neither queriable
nor settable for that language. A language opting out is a supported state -- `yaml`, `toml`,
`ini` and `sql` are already in it, and `lexer.declarations` states it: *"AN EMPTY LIST MEANS
THIS LANGUAGE HAS NO `a` SERIES, not 'none found here'."*

! **THE ANCHOR IS THE LINE THE KEYWORD IS ON.** Roy, 2026-08-21: *"The line static ... is where
a belongs and the documentation above is where it should go. The fact that the next line is a
separate line of code which is implicitly referred to from the previous line is not our
problem."* `lexer.declarations` already encodes this -- it returns `(line, insert)` where
`insert` IS the keyword line for every above-doc language.

! **THE JOIN RULE IS NEAREST-ABOVE, NOT ADJACENCY.** MEASURED 2026-08-21 on CPython v3.13.1
(`corpora/cpython`, 489 `.c`/`.h` files): of 2,987 documented column-0 declaration lines, 1,863
(62%) carry a comment flush against them and 1,124 (38%) have a blank line between. A strict
`end + 1 == insert` test abandons that 38% in `b`. ! It is implemented:
`lexer.document_declarations` walks up from the declaring line past blanks, stopping at CODE,
and compares the two distances.

! **PRECISION IS NOT THE OBJECTION IT LOOKED LIKE.** MEASURED on CPython: 15,813 column-0 lines
carry a whitespace-delimited C keyword and only ~6,850 declare a function -- but 12,826 of them
(81.1%) have NO comment above them at all. A spurious `a` on a non-declaration is therefore an
EMPTY PLACE that nothing ever fills, which is the cost the round-trip test measures directly.

! **RECONSTRUCTION IS NOT WHAT A SHARED ADDRESS BREAKS -- VERIFICATION IS.** Prose returns where
it came from whatever cue it carries. What fails is `record.entry_for`, which resolves by address
and returns the FIRST match: a correct edit to the second paragraph is checked against the first
and `verdicts.py` exits 1. So a round trip that only proves bytes come back will pass while the
gate still refuses the edit -- which is why T18's verify names the SPURIOUS `a`, not the bytes.

## The match rule, stated and already tried

**THE RULE, ROY 2026-08-22.** `_declares_here` searches for `"\n{keyword} "` or `" {keyword} "`.
The keyword opens the line, or is preceded by a space, and is followed by a space either way;
read per line the first form is `startswith(f"{keyword} ")`. ! **IT IS STILL NEVER A SUBSTRING**,
which the space either side buys: `deffered = 1` opens with `deffered`, `x = my_func()` has no
space before `func`, and `return fn(a)` has a bracket after `fn`. ! And it no longer has to be
the first word or the second, which is the change: today a keyword behind two modifiers is
invisible -- `pub async fn foo`, or a c-family `static inline void f()` whose list holds
`static`. The two-word form papers over ONE modifier and cannot reach two. ! The trailing space
means a keyword ENDING a line does not declare, which is the rule as stated and costs nothing
real.

**THE BODY THAT PASSED**, so this is a paste rather than a re-derivation.
`_declares_here(line, declares)` becomes: `return any(line.startswith(f"{keyword} ") or
f" {keyword} " in line for keyword in declares)` -- and the whole of the previous body goes,
including the `_FIRST_WORD` match, the two-word reassembly, and the module-level `_FIRST_WORD`
pattern itself (`lexer.py:1500-1523` today).

**THE CASES IT WAS CHECKED AGAINST**, all measured 2026-08-22. MUST NOT declare: `deffered = 1`
against `def`; `funcs = []` against `func`; `x = my_func()` against `func`; `return fn(a)`
against `fn`. MUST declare: `        fn inner() {}` against `fn` (indentation does not hide it);
`macro_rules! thing {` against `macro_rules!`; `pub async fn foo() {}` against `fn`; `static
inline void f(void)` against `static`; `public static void f()` against `static`; `data class
Pair(val a: Int)` against `data class`. ! The last four are the ones the current
first-word-or-second rule gets WRONG.

**IT WAS TRIED AND REVERTED ON PURPOSE, 2026-08-22**, so the next session does not think it is
untested. All 27 tests in `tests/test_declarations.py` passed under the new rule -- the four
existing cases are compatible, not in conflict -- and the added cases resolved correctly. ! Roy
stopped it as scope creep on the folio-placement branch: *"that is definitely a todo and I want
to finish this branch."*

## Tasks

- [x] T1 -- MEASUREMENT, 2026-08-21, and FALSIFIED 2026-08-23. The Rust/Go/Java/TS/C#
      symptom is in the Objective, with today's re-measurement beside it.
- [x] T2 -- MEASUREMENT of the cause. `paragraphs_lexical` still does not set
      `Paragraph.declares`; `lexer.document_declarations` does, and `page.py:726` calls
      it. Recorded in the Objective.
- [x] T3 -- ARGUMENT, not work: the consequence of T1 for `function-context` and
      `ownership-context`. Recorded in the Objective.
- [x] T4 -- MEASUREMENT about `CLAUDE.md`'s eleven-language claim. Recorded in the
      Objective.
- [x] T5 -- RULING, made 2026-08-21 and quoted in full in the Objective: the acceptance
      test is a round trip.
- [x] T6 -- RULING/ARGUMENT: a language opting out is a supported state. Recorded in the
      Objective.
- [x] T7 -- DONE. **The wire.** `page.py:726` calls `document_declarations(got,
      declarations(text, lang, code), code)` and `lexer.py:1617` sets
      `held.declares = ordinal`. MEASURED 2026-08-23 over the fixtures: `sample.rs`,
      `.go`, `.java`, `.ts`, `.kt`, `.swift`, `.cs` and `.rb` all fill `@a1` and above
      with the doc comment that was in `b` before.
- [x] T8 -- RULING plus MEASUREMENT: nearest-above, and the 62/38 CPython split.
      Implemented in `lexer.document_declarations`. Recorded in the Objective.
- [x] T9 -- RULING SETTLED 2026-08-21 -- the anchor is the keyword's line. Quoted in the
      Objective.
- [x] T10 -- MEASUREMENT: 81.1% of the false positives are undocumented lines. Recorded
      in the Objective.
- [x] T11 -- ARGUMENT: a shared address breaks VERIFICATION, not reconstruction. Its
      operative half is now T18's verify. Recorded in the Objective.
- [x] T12 -- DONE 2026-08-23, commit `5cc4645`. `CLAUDE.md:380-390` no longer says a C
      keyword list *"could never be complete"*; it says the empty list is **a fact about
      the MATCHER, not about C**, and `references/vocabulary.toml:34` says the same to
      all four roles. ! That was the box asking for the C text to be updated or
      reaffirmed either way, and it was updated.
- [x] T13 -- THE MATCH RULE, quoted from Roy 2026-08-22. A specification, not a
      checkpoint; it is T18's content and is kept in the Objective.
- [x] T14 -- HISTORY: tried and reverted on purpose, 2026-08-22. Recorded in the
      Objective.
- [x] T15 -- THE BODY THAT PASSED. A patch to paste, not a checkpoint; kept in the
      Objective.
- [x] T16 -- THE TEN CASES it was checked against. Evidence for T18, kept in the
      Objective.
- [x] T17 -- ARGUMENT: the match rule alone changes nothing a reviewer sees without the
      wire. SUPERSEDED by T7 landing -- the wire is in, so T18 lands alone.
- [ ] T18 -- **Match the keyword ANYWHERE in the line, and give `c` and `cpp` a keyword
      list.** That single assumption is why they carry an empty one: a C declaration
      opens with its RETURN TYPE, so no keyword is ever the first word. Roy, 2026-08-23:
      *"a slightly smarter parser that looks for the correct keyword in the line instead
      of just the first word ... It is a simple fix."* Verify, all four:
      `_declares_here` answers correctly on the ten cases in the Objective;
      `grep -c _FIRST_WORD plugins/comment-review/skills/comment-review/scripts/lexer.py`
      answers 0; a `.c` file resolves an `a` place for `struct`, `enum`, `union` and a
      function definition; and no line gains a SPURIOUS `a` -- one would renumber every
      `a` below it, and the shared-address note above says why renumbering is caught by
      `record.entry_for` and not by the bytes.
