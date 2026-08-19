# Two live runs proposed fifteen changes

```
Status:   open
Progress: 5 of 16 tasks done
Owner:    session * Roy (* 3 rulings)
Requires-Roy: true
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

!! **These carry CHECKED boxes because an unchecked one is a claim that work remains.** Roy,
2026-08-18: *"a check box not-marked is left as something todo, even if it was superseded and no
longer necessary."* Held as prose in a table, these five were invisible to any recount -- the
README row read `0/9` while five were done.

- [x] **P2, both reports -- the work list is withheld on a refusal.** Printed on a refusal now,
      labelled PROVISIONAL, exit unchanged.

- [x] **P2, todo-tool -- N coordinated edits.** `reviewer-brief.md` says N records each read
      oddly alone, and that this is the format working rather than failing.

- [x] **P1, todo-tool -- altitude.** A third question after checkable/necessary in the brief, and
      `compact.md` hands an over-specified block back rather than cutting it.

- [x] **P9, redacted-corpus -- `verdicts.py --out`.** The stage-5 gate was unrunnable in the
      session type the skill is written for.

- [x] **P3, todo-tool -- a prose file has no blocks.** Filed as
      [`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md); the
      measurement is what this adds -- **190 of 196 files** in one merge-base diff were
      `TODO/*.md`.

## SUPERSEDED -- three proposals overtaken by later measurement

! Kept with their measurements. Each was right when written; what moved is recorded beside it.

- [ ] **P1, redacted-corpus -- parse after every write. SUPERSEDED for the placeholder case,
      STILL WANTED for the rest**, so it is open rather than checked -- the box tracks the
      remainder, which is the non-Python cases the kind guard cannot reach.

Measured 2026-08-17 on the pinned 3.11:

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

## Routed 2026-08-18, against the 0.2.4 scope

**Four of the ten go into 0.2.4, and three of those four are one defect.** P7, P4 and the
todo-tool P1 are each a consumer inferring what only the producer knows -- the shape 0.2.3 spent
its eleven findings on, continuing into the record's remaining untyped fields. They are scheduled
with the split rather than after it because they all edit the same two halves.

| # | why now |
| --- | --- |
| **P10** typed `SOURCES` | the run's best finding -- **213 citations resolving to nothing** -- was an ABSENCE, which `file:line \| verbatim` cannot express. It was blocked on the record being a value, and 0.2.3 shipped that. Lands in the per-finding checker |
| **P7** the insertion op | now a task on the census filter. `galley.py` still infers insert-against-replace from `kind`, and `record.py` regexes the side out of prose |
| **P4** deletion scope | `may_empty` half-addressed it; WHOLE against PARTIAL is still inferred rather than stated |
| **P1** todo-tool, `REASON` naming an unclaimed sentence | a checker change, and *"three places"* is still wrong on disk |

! **P6 -- SHIP THE APPLIER -- is not scoped until it is RE-READ against `galley.py`.** It was
written before the galley existed and calls itself *"the deepest finding here"*, naming four
defects: placeholder handling, drop scoping, comment prefixes, indent framing. `galley.py`
shipped in 0.2.3, does the splice, and refuses overlapping and stale ranges. **Read the four
against what the galley now does before giving this a size** -- what remains may be P3's indent
contract alone.

! **P5, P3, P2 and P8 are group C and stage 6/7a work**, not this release. See
[`docs/superpowers/specs/2026-08-17-review-process-coherence-design.md`](../docs/superpowers/specs/2026-08-17-review-process-coherence-design.md).

### !! AND ONE KEY RELEASE REQUIREMENT THAT IS NOT A PROPOSAL FROM EITHER RUN

**STAGE 4 SERIALISES. `ownership-context` runs ALONE; the other three run only after it has had
its say.** Roy, 2026-08-19: *"1 required -- ownership-context has to run else verdicts are made
on statements that are not in the 'right' place. The other 3 are optional and only run after
ownership-context has had its say."* Filed in full at
[`ownership-is-read-first-but-nothing-makes-it-so`](ownership-is-read-first-but-nothing-makes-it-so.md),
3 of 10, `Requires-Roy`.

! **It is listed here because 0.2.4 cannot ship without it and it belongs to no proposal.** The
ruling was made twice -- the serialisation 2026-08-17, the never-dropped rule 2026-08-18 -- and
`SKILL.md` still contradicts both halves: `:160` says *"all four roles run every time"* and
`:510-512` dispatches all four in ONE message, in parallel. **The file the task agent reads was
never brought along.**

! **The ADDRESS system removes the objection this was blocked on.** The design rested on *"nothing
renumbers, so there is ONE census for the whole run"* -- an argument about the census INDEX,
which 0.2.4 dropped. It gets stronger, not weaker: 4b changes what a block BELONGS to and never
where it sits, so every address 4a cites is still valid at 4c by construction, and the rejected
"two censuses and an index map" cannot arise.

## Tasks

! In the order the evidence argues for.

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

- [ ] **P3 -- the indent contract.** Closes
      [`a-block-does-not-say-where-its-text-starts`](a-block-does-not-say-where-its-text-starts.md),
      which is the same fact stated from the producer's side: a block records which lines it
      spans and never where on the first line its text begins. A reviewer's `CHANGE` carried the RECORD's presentation
      indent, not the file's, and a six-line block landed inside an `if ...: continue` body,
      annotating an unreachable position. `write.md`'s *"write the APPROVED text verbatim"* is
      wrong for any block not already file-framed, and the transformation is specified nowhere.
      ! Decide it against the record as it now is -- see the correction above.

- [ ] **P2 -- give the WIDTH a stage, or fold it into stage 6.** Closes
      [`compact-can-buy-lines-with-width`](compact-can-buy-lines-with-width.md) -- zero
      occurrences of `width`, `column` or `character` in `compact.md`. Stage 1.2 measures two
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

- [ ] * **RELEASE REQUIREMENT -- STAGE 4 SERIALISES.** `ownership-context` runs alone at 4a;
      the other three run at 4c against its resolved placement. **One role is REQUIRED and
      three are OPTIONAL** -- the legal sets are `{ownership-context}` plus any subset of the
      others. Close
      [`ownership-is-read-first-but-nothing-makes-it-so`](ownership-is-read-first-but-nothing-makes-it-so.md)
      (3/10), whose seven open tasks are the build. ! The first is a design decision Roy already
      named: the pCST must carry a PROPOSAL, and that is a second SUBJECT -- a second module,
      not a flag on the census.

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

!! **LINKAGE AUDITED 2026-08-19, and it was ABSENT.** None of the fifteen tasks named the TODO it
closes; three were named in this section only, one of them already completed. A task that does
not name its TODO is a task nobody can close from either end -- the backlog cannot see the work
scheduled against it, and the plan cannot see the work already filed. **Four now carry a link;
the rest have no TODO because none was ever filed**, which is the answer to "what closes this"
rather than an omission to fix by inventing one.

| task | closes |
| --- | --- |
| P3, todo-tool -- a prose file has no blocks | [`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md) |
| P3 -- the indent contract | [`a-block-does-not-say-where-its-text-starts`](a-block-does-not-say-where-its-text-starts.md) |
| P2 -- give the WIDTH a stage | [`compact-can-buy-lines-with-width`](compact-can-buy-lines-with-width.md) |
| RELEASE REQUIREMENT -- stage 4 serialises | [`ownership-is-read-first-but-nothing-makes-it-so`](ownership-is-read-first-but-nothing-makes-it-so.md) |
| P6, P10, P5, P4, P7, P1, P8 | **no TODO filed.** Each is tracked here and nowhere else |

! **P5 has two candidates and neither is a clean fit** --
[`the-author-approves-blocks-and-never-sees-the-page`](the-author-approves-blocks-and-never-sees-the-page.md)
and [`7a-can-prove-the-change-by-applying-it-to-a-copy`](7a-can-prove-the-change-by-applying-it-to-a-copy.md).
P5 asks for the proposition check to run BEFORE the write; the first is about what the author is
shown, the second about rendering the proposal as a file. Left unlinked rather than guessed.

- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- P4, P7 and P10 are all record-shape changes and belong to that build.
- [`stage-5-is-the-only-stage-with-no-independent-reader`](stage-5-is-the-only-stage-with-no-independent-reader.md)
  -- P5's four questions are what 5b should ask.
- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- D9 survives the JSON move, as redacted-corpus's own table says.
