# Two live runs proposed fifteen changes

```
Status:   open
Progress: 5 of 15 proposals resolved
Owner:    session * Roy (* 3 rulings)
Raised:   2026-08-17, from `evidence/todo-tool-full-v0_2/proposals.md` (5) and
          `evidence/redacted-corpus-full-v0_2/PROPOSALS.md` (10)
```

## Objective

**Two sessions ran this system end to end on real repositories and wrote up what they had to
work around.** They are field reports, not design notes -- both had to NAVIGATE the tool to get
work done, and every claim in them is measured on a run whose artifacts are in the same
directory.

!! **That provenance is why they outrank reasoning from outside.** The 83 refusals spent on
transcription fidelity, the 213 citations resolving to nothing, the 31 defects stage 8 found
while every mechanical gate was green -- none of those is derivable from reading the code.

! **What they agree on is worth more than either alone.** Both raised the work list being
withheld; both raised the record format; both found the reviewers are NOT the weak stage.
redacted-corpus states it flatly: *"every failure this run is downstream of MARK."*

## Resolved -- do not redo

| # | from | what |
| --- | --- | --- |
| **P2** work list withheld | both | **DONE.** Printed on a refusal, labelled PROVISIONAL, exit unchanged |
| **P2** N coordinated edits | todo-tool | **DONE.** `reviewer-brief.md` says N records each read oddly alone and that this is the format working |
| **P1** altitude | todo-tool | **DONE.** A third question after checkable/necessary in the brief, and `compact.md` hands an over-specified block back rather than cutting it |
| **P9** `verdicts.py --out` | redacted-corpus | **DONE.** The stage-5 gate was unrunnable in the session type the skill is written for |
| **P3** a prose file has no blocks | todo-tool | already filed; the measurement is added -- **190 of 196 files** in one merge-base diff were `TODO/*.md` |

## SUPERSEDED -- three proposals overtaken by later measurement

! Kept with their measurements. Each was right when written; what moved is recorded beside it.

**P1 (redacted-corpus) -- parse after every write. SUPERSEDED for the placeholder case, still
wanted for the rest.** Measured 2026-08-17 on the pinned 3.11:

```
'"""<empty - the whole block is deleted>"""'
parses?          YES -- a parse-after-write check sees nothing wrong
prove_unchanged: PROVEN    m.py: reads the same (ast)
```

`PROVEN` is correct there: `_blank_docstrings` removes docstring content before comparing, by
design, because that is the prose the skill is allowed to rewrite. ! The other two examples break
syntax and are already caught -- `proof kind changed (ast -> stripped) -- likely broke Python
syntax`, exit 1 -- by a guard present in `v0.2.0`. **So the placeholder routes to P4 or P5, and
parse-after-write still earns its place for the non-Python cases the kind guard cannot reach.**

**Replay needs the TREE pinned as well as the census. SUPERSEDES the note that pinning the
census is enough.** `SOURCES` cites the working tree. Measured on this repo's own smoke test:
the same four reports gave **78 "SOURCES not found" against HEAD** and **903 findings / 35
STANDS / 46 NEEDS A RULING / 14 CODE CONCERNS, exit 0** against a worktree at their commit. The
tree had moved 197 lines in one file.

**P3's recommendation -- SUPERSEDED by the record shape settled the same day.** It argues
`"text"` as unindented prose over `"lines"` as file-ready lines, because *"a reviewer reading a
census has no reliable way to know the file's frame."* ! The record now carries neither the
census text nor the original, so the reviewer opens the file and does know the frame. **The
contract still has to be written down; which of the two it should be is the part that moved.**

## Open, in the order the evidence argues for

- [ ] * **P6 -- SHIP THE APPLIER.** *"The deepest finding here."* `census.py`, `verdicts.py`,
      `referrers.py` and `prove_unchanged.py` are shipped and hardened across three versions.
      **The step that actually edits files is not**, so every task agent writes it from scratch
      at the point in a run where its context is most spent. That run's applier had four
      defects -- placeholder handling, drop scoping, comment prefixes, indent framing -- and
      *"the next agent meets the same four alone."*
      !! The measured argument: five joins each got cheaper as `verdicts.py` hardened, because
      the tool carried the lesson. **The applier carries none, because there is no applier.**

- [ ] * **P10 -- a reviewer cannot report an ABSENCE or a COUNT.** `SOURCES` requires
      `file:line | verbatim`, which cannot express *"this phrase appears nowhere in CLAUDE.md"*
      -- and that absence was **the single best finding of the run: 213 citations resolving to
      nothing.** Reviewers coped by citing where they looked and putting the absence in prose,
      which works only because a human reads it. Typed sources are checkable BY MACHINE:
      `{"kind": "absence", "searched": ..., "pattern": ..., "hits": 0}` and
      `{"kind": "count", "population": ..., "scope": ..., "n": 30}`. ! Re-running the search is
      strictly better than trusting the prose.

- [ ] **P5 -- run the is-it-still-a-proposition check BEFORE the write.** Stage 8 found **31
      defects the run caused** while `prove_unchanged` passed 23/23, the hygiene guard 19/19,
      2413 tests passed, every citation resolved and the residue check was clean. **Nothing
      mechanical asks whether the prose still parses as English.** Twelve of the 31 are one
      shape: a false clause replaced with a longer true one, the paragraph re-wrapped, and the
      rest of the block left arguing the old claim.
      !! **Every one was findable without touching disk** -- the composed block is in hand at
      the end of stage 5. Its four questions belong in the 5b re-review being built.
      ! Keep stage 8: it is the only pass that sees blocks INTERACTING, and it caught three
      block-to-block contradictions here.

- [ ] **P4 -- type the deletion, and separate WHOLE from PARTIAL.** A whole-block drop was
      expressed as the English sentence `<empty - the whole block is deleted>` in `CHANGE`, and
      landed in seven files. ! The fix is not "every drop is empty": a `drop` naming ONE sentence
      carries the REMAINING block. `{"verdict": "drop", "scope": "block"|"sentence"}`.
      ! Partly addressed -- `may_empty` now admits a blank `CHANGE` only where `CLAIM` names the
      whole block -- but the SCOPE is still inferred rather than stated.

- [ ] **P7 -- an `add` on an empty interval is an INSERTION.** An interval's `path:start-end`
      spans the two CODE LINES bounding the gap, so a range replace **deletes both statements**.
      Caught on that run by a guard, not by design. The record should say
      `{"op": "insert", "anchor": ..., "side": "above"}` rather than leave an applier to infer it
      from a range that means something different for this one kind of block.

- [ ] **P3 -- the indent contract.** A reviewer's `CHANGE` carried the RECORD's presentation
      indent, not the file's, and a six-line block landed inside an `if ...: continue` body,
      annotating an unreachable position. `write.md`'s *"write the APPROVED text verbatim"* is
      wrong for any block not already file-framed, and the transformation is specified nowhere.
      ! Decide it against the record as it now is -- see the correction above.

- [ ] **P2 -- give the WIDTH a stage, or fold it into stage 6.** Stage 1.2 measures two
      published numbers and only the cap gets a stage. !! **They INTERACT**: re-wrapping twelve
      over-width lines pushed a block from 33 to 34 against a cap of 33, and the repo's own guard
      caught what the pipeline had not. Proposal: rename stage 6 COMPACT to **FIT** and give it
      both, reporting any block where the two cannot both be met.

- [ ] **P1 (todo-tool) -- a `REASON` naming a sentence no `CLAIM` names.** Already step 4 of the
      record change. `module-context` wrote the finding in `REASON`; the gate checked the claim
      it named and passed; *"three places"* reached no work list and **is still wrong on disk.**
      ! Report it, do not refuse it -- `REASON` legitimately discusses context.

- [ ] **P8 -- a RULINGS NEEDED section.** Two repo-level tensions no verdict can settle: a
      citation form the style sheet demands and the width forbids, and a convention the reviewers
      deliberately worked against. The tool has nowhere to put either, and both had to be raised
      in conversation.

## ! What worked, and must not be broken while fixing the above

- **Blind dispatch produced real corroboration and a real contradiction.** One defect was found
  independently by three roles at three scopes; a caller count was disputed BETWEEN roles, which
  is what made the operator count it by hand -- *"and I got it wrong, and `block-context` was
  right."* ! **That is the strongest evidence in either file**: the disagreement was what
  prompted the check, and the tool beat the hand count.
- **`query -- outside my role` works as designed.** One role returned 1008 of them, and all 16 of
  its substantive findings came from the 167 blocks its remit reaches.
- **Re-dispatching a role with its own refusals is cheap.** 186 problems to 7 in one round, with
  **zero findings withdrawn** -- the refusals were contract failures, not judgement failures.
- !! **The reviewers are not the weak stage.** *"Every failure this run is downstream of MARK."*

## Related

- [`the-record-is-a-parsed-template-and-should-be-a-value`](the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- P4, P7 and P10 are all record-shape changes and belong to that build.
- [`stage-5-is-the-only-stage-with-no-independent-reader`](stage-5-is-the-only-stage-with-no-independent-reader.md)
  -- P5's four questions are what 5b should ask.
- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- D9 survives the JSON move, as redacted-corpus's own table says.
