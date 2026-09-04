# Ten defects in `results/differences.py`, none of them in its arithmetic

```
Status:   open
Progress: 0 of 10 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, a code review of `results/differences.py` that
          exercised `compose` against an independent merge oracle and mutated its suite
          -- every defect found is in what the module REPORTS or DOCUMENTS)
```

## Objective

Ten defects in `results/differences.py`, found on 2026-08-30. Every one of them is
about what this module REPORTS or DOCUMENTS. None is in its arithmetic.

!! **THE ARITHMETIC WAS EXERCISED AND HELD: 0 disagreements over 3,191,784 cases.**
74,088 exhaustive two-side cases, 3,111,696 exhaustive three-side cases and 6,000
randomized cases were run against an independently written merge oracle -- zero
compositions over a real overlap, and zero texts differing from the oracle's. **Order
independence holds structurally**: 120 permutations of a five-side dict give one
distinct result, and 79,507 two-side cases with the roles renamed to reverse the sort
give zero disagreements. **`compose` could not be made to produce a wrong
composition**, which was the severe direction the review was pointed at.

! **THAT PARAGRAPH IS HERE SO A READER OF THIS FILE'S TITLE DOES NOT INFER THE MERGE
IS UNSOUND.** Ten reporting defects on a module whose merge was verified over three
million cases is a different situation from ten defects in the merge.

!! **THE TEN LAND TOGETHER, BECAUSE THE REPORTING HALF CANNOT BE FINISHED PIECEWISE.**
The span fix corrects a message nothing reads; the `span`/`roles` attributes give that
message a machine-readable form; carrying `CannotCompose` out of `_composition` makes
anything able to read it; and the address is what a send-back to a role needs. Landing
the span fix alone corrects a message nothing reads; landing the carry alone carries a
span that renders `2-1`.

## What was measured

- four minimal reproductions through the public `compose` render `base lines 2-1` and
  `base lines 1-0`: `start == end` makes `{start + 1}-{end}` run backwards. MUTATION
  RUN M12 and M13 both SURVIVED against 16 passing tests, because
  `test_two_edits_on_one_line_refuse_by_name` asserts only the role names. The
  non-empty case is correct -- span `(3,5)` renders `base lines 4-5`
- `grep -rn "CannotCompose" src/` returns exactly two use sites outside the declaring
  file, and the second is followed by `return None`, so the message is read by nothing
  in `src/`. That undoes the class's own claim to be *"RAISED, NOT RETURNED AS A
  SENTINEL"* and its `Process: #51` citation
- `unified("one\ntwo\nthree", "one\ntwo\nTHREE", "p.py")` yields two final lines with
  no newline and no `\ No newline at end of file` marker, and
  `commands/taken_in.py:87` joins them into `-three+THREE`. `apply_unified` in the
  suite walks the LIST, so the join is untested
- `difflib.SequenceMatcher`'s `bpopular` is empty at n=199 and non-empty at n=200;
  over 400 random paragraphs of 200-320 lines the shipped module and an
  `autojunk=False` variant disagreed on 400 of 400, with refusals as wide as `base
  lines 17-257`. Latent in this tree -- 0 of 16,947 non-interval paragraphs reach 200
  lines -- and reachable on the pinned corpora
- `compose("a\nb\nc\n", {"r1": "a\nB\nc\n", "r2": "a\nB\nc\n"})` refuses a
  BYTE-IDENTICAL pair. Over 74,088 exhaustive two-side cases, 15,640 of the 69,026
  refusals -- 22.7% -- had no real interval overlap, and `flows/collate.py` catches
  agreement only on the ESCALATIONS path, so the REREADS path costs a human round trip

! **FIFTEEN PROSE CLAIMS IN THIS FILE WERE CHECKED AND HOLD** -- `_conflict_spans`
growth over 20,000 cases, `_side_slice` non-adjacency, `compose`'s empty-`sides`
identity over 43 texts, both `decision-log.md` citations resolving, and ASCII and
88-column compliance. Ten of the fifteen mutants planted were CAUGHT by
`tests/test_differences.py`.

! **TWO MUTANTS ARE EQUIVALENT, NOT TEST GAPS, AND ARE RECORDED SO NOBODY RE-FILES
THEM**: `touching[0]` to `touching[-1]`, and the overlap test replaced by strict
containment. Each showed 0 behavioural differences over 104,088 cases.

## Tasks

- [ ] T1 | Implement a correct line span in `CannotCompose`'s message for a
      zero-width merged span, where `start == end` renders `{start + 1}-{end}`
      backwards. Verify: two roles both proposing an `add` at one place produce
      a message naming a real position, and a test asserts the numbers so that
      shifting them by 7, or replacing them with `?-?`, goes red; both of those
      mutants survive the suite today.
- [ ] T2 | Implement `span` and `roles` attributes on `CannotCompose`, so a
      caller recovers the refusal without parsing an English sentence. Verify: a
      refused `compose` raises an exception whose `.span` and `.roles` match its
      own message, asserted by a test; the class declares no attributes today.
- [ ] T3 | Update `flows/collate.py`'s `_composition` so a `CannotCompose` is
      carried into what the run reports instead of becoming `None`. Verify: a
      re-read caused by a refused composition names the span and the roles in
      the run's own output, and the test goes red against today's code, where
      the sole `except CannotCompose:` returns `None`.
- [ ] T4 | Implement attaching the ADDRESS to a refused composition, which the
      message never names. Verify: a send-back for a refused composition names
      the place, not only base line numbers inside one paragraph;
      `flows/collate.py:192` holds `entry["address"]` and cannot attach it today
      because `_composition` returns `None`.
- [ ] T5 | Update `unified` so its output is not corrupt when joined and the
      last line has no trailing newline -- emit the missing-newline marker, or
      stop promising the join in the docstring. Verify: a page whose last line
      lacks a trailing newline prints two separate diff lines through
      `commands/taken_in.py`, not `-three+THREE` on one line. DO NOT fix by
      appending a newline -- that claims a newline the file does not have.
- [ ] T6 | Update both `difflib.SequenceMatcher` constructions in
      `results/differences.py` to state a choice about `autojunk`, which
      reshapes the opcodes every correctness claim in the file is about. Verify:
      the file either passes `autojunk=False` or carries a sentence saying the
      heuristic is accepted and why, and a test pins the behaviour at the
      199/200-line boundary.
- [ ] T7 | Update the module docstring of `results/differences.py`, whose
      opening sentence announces three operations over a base and its sides
      while `unified` has neither. Verify: the header agrees with `unified`'s
      own `Args` -- the page's text before the revise -- and the word `side` is
      not spent on something that is not a side in the sense the rest of the
      file uses it.
- [ ] T8 | Update `compose`'s prose to state that two sides making the
      BYTE-IDENTICAL edit are refused, which the docstring explains for the
      abutting case and not for this one. Verify: the sentence exists and a test
      asserts the identical- edit refusal, so a reader is not left to read *no
      composition exists* as a claim about disagreement.
- [ ] T9 | Update `diff3`'s `Returns` block so it says the `\|\|\|\|\|\|\| base`
      section is legitimately EMPTY for a pure insert. Verify: the sentence is
      there and a test renders a pure insert and asserts the empty base section,
      so a reader or an agent parsing the format can tell an insert from a
      truncated render.
- [ ] T10 | Update the sentence *`difflib.unified_diff` reads two strings, not
      two commits*, which reads two SEQUENCES OF LINES that this function splits
      at lines 48-49. Verify: the sentence is literally true and still makes its
      point that no git process is involved.
