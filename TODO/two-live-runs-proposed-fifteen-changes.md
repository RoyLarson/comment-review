# Two live runs proposed fifteen changes

```
Status:   decision-needed
Progress: 11 of 16 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17, from `evidence/todo-tool-full-v0_2/proposals.md` (5) and
          `evidence/redacted-corpus-full-v0_2/PROPOSALS.md` (10)
Narrowed: 2026-08-19 -- the 0.2.4 scope moved to docs/plans/; this file is the job board
          for the fifteen proposals again. Linkage audited -- 0 of 15 tasks had named
          the TODO they close
Re-verified: 2026-08-23 -- BOTH SOURCE PACKAGES ARE GONE FROM THE TREE, so every citation
          in this file to `evidence/todo-tool-full-v0_2/` or
          `evidence/redacted-corpus-full-v0_2/` resolves nowhere. Four proposals were
          re-checked against the shipped code and are landed or superseded
```

## Objective

**Two sessions ran this system end to end on real repositories and wrote up what they had to
work around.** They were field reports, not design notes -- both had to NAVIGATE the tool to get
work done, and every claim in them was measured on a run whose artifacts sat in the same
directory.

!! **THE ARTIFACTS ARE NOT IN THIS TREE ANY MORE.** Verified 2026-08-23:
`evidence/todo-tool-full-v0_2/` and `evidence/redacted-corpus-full-v0_2/` are both removed, and
the only surviving packages are `evidence/cycle-0.2.3/` and
`evidence/comment-review-skill-023-dev-review/`. **Every measurement quoted below is therefore
un-re-derivable here**, and is kept for the same reason `CLAUDE.md` keeps its 31-defect run: the
numbers are specific enough to be checked against a NEW run, which is the only thing that would
settle them. The same absence is tracked in
[`dangling-links-resolve-nowhere`](dangling-links-resolve-nowhere.md) and
[`held-runs-need-a-one-off-migration`](held-runs-need-a-one-off-migration.md).

!! **That provenance is why they outranked reasoning from outside.** The 83 refusals spent on
transcription fidelity, the 213 citations resolving to nothing, the 31 defects stage 8 found
while every mechanical gate was green -- none of those is derivable from reading the code.

! **What they agreed on is worth more than either alone.** Both raised the work list being
withheld; both raised the record format; both found the reviewers are NOT the weak stage.
redacted-corpus stated it flatly: *"every failure this run is downstream of MARK."*

## What the runs established, and what must not be broken while fixing the rest

- **Blind dispatch produced real corroboration and a real contradiction.** One defect was found
  independently by three roles at three scopes; a caller count was disputed BETWEEN roles, which
  is what made the operator count it by hand -- *"and I got it wrong, and `block-context` was
  right."* ! **That is the strongest evidence in either file**: the disagreement was what prompted
  the check, and the tool beat the hand count.
- **`query -- outside my role` works as designed.** One role returned 1008 of them, and all 16 of
  its substantive findings came from the 167 paragraphs its remit reaches.
- **Re-dispatching a role with its own refusals is cheap.** 186 problems to 7 in one round, with
  **zero findings withdrawn** -- the refusals were contract failures, not judgement failures.
- !! **The reviewers are not the weak stage.** *"Every failure this run is downstream of MARK."*

## Replay needs the TREE pinned as well as the census

`SOURCES` cites the working tree. Measured on this repo's own smoke test: the same four reports
gave **78 "SOURCES not found" against HEAD** and **903 findings / 35 STANDS / 46 NEEDS A RULING /
14 CODE CONCERNS, exit 0** against a worktree at their commit. The tree had moved 197 lines in one
file. ! This SUPERSEDES the note that pinning the census is enough.

## The measurement behind P1's placeholder case

Measured 2026-08-17 on the pinned 3.11:

```
'"""<empty - the whole block is deleted>"""'
parses?          YES -- a parse-after-write check sees nothing wrong
prove_unchanged: PROVEN    m.py: reads the same (ast)
```

`PROVEN` is correct there: `_blank_docstrings` removes docstring content before comparing, by
design, because that is the prose the skill is allowed to rewrite. ! The other two examples break
syntax and are already caught -- `proof kind changed (ast -> stripped) -- likely broke Python
syntax`, exit 1 -- by a guard present in `v0.2.0`. **So the placeholder routes to P4, and
parse-after-write earns its place only for the non-Python cases the kind guard cannot reach.**

## Tasks

! In the order the evidence argues for.

- [ ] T1 -- * **P6 -- RE-READ THE APPLIER'S FOUR DEFECTS AGAINST THE SHIPPED GALLEY, then size
      what is left.** P6 called itself *"the deepest finding here"* and named four: placeholder
      handling, drop scoping, comment prefixes, indent framing. ! Its premise -- *"the step that
      actually edits files is not shipped"* -- is no longer true: `galley.py` and `compositor.py`
      both ship, the galley refuses overlapping and stale ranges and refuses a destructive `--out`
      (`galley.py:365`), and the compositor sets the page. Verify: each of the four named against
      `galley.py`/`compositor.py` with a file:line, and each either closed here or filed against
      [`galley-and-compositor-write-path`](galley-and-compositor-write-path.md) (1/5).

- [ ] T2 -- * **P10 -- a reviewer cannot report an ABSENCE or a COUNT.** `SOURCES` requires
      `file:line | verbatim` -- verified 2026-08-23 at `record.py:609` and `:620`, which still
      parse each entry as `file:line` or `file:start-end` plus prose. That form cannot express
      *"this phrase appears nowhere in CLAUDE.md"*, and that absence was **the single best finding
      of the run: 213 citations resolving to nothing.** Reviewers coped by citing where they
      looked and putting the absence in prose, which works only because a human reads it. Typed
      sources are checkable BY MACHINE:
      `{"kind": "absence", "searched": ..., "pattern": ..., "hits": 0}` and
      `{"kind": "count", "population": ..., "scope": ..., "n": 30}`. ! Re-running the search is
      strictly better than trusting the prose. Ruling owed on the two shapes before the build.

- [x] T3 -- SUPERSEDED. **P5 -- run the is-it-still-a-proposition check BEFORE the write.** It has
      landed on both halves. `references/residue-check.md:59` makes *"What remains is STILL A
      PROPOSITION -- subject, referent, and a claim"* a conjunct of the check APPLY runs on its
      own output, and `SKILL.md:104` records that it runs there; **stage 5b RE-REVIEW is built**
      (`SKILL.md:905`, `references/re-review.md`), which is where P5 said its questions belonged.
      ! Stage 8 was kept, as P5 asked: it is the only pass that sees paragraphs INTERACTING.
      The 31-defect measurement stays in the Objective as the reason.

- [ ] T4 -- **P4 -- type the deletion, and separate WHOLE from PARTIAL.** A whole-paragraph drop
      was expressed as the English sentence `<empty - the whole block is deleted>` in `CHANGE`,
      and landed in seven files. ! The fix is not "every drop is empty": a `drop` naming ONE
      sentence carries the REMAINING paragraph. Verified 2026-08-23: `may_empty` (`record.py:150`,
      enforced at `desk.py:233` and `:810`) admits a blank `CHANGE` only where `CLAIM` names the
      whole paragraph, so the SCOPE is still inferred rather than stated -- there is no `scope`
      key on a `drop`. Verify: a `drop` record carries `"scope": "block"` or `"scope": "sentence"`
      and the desk refuses one that does not.

- [x] T5 -- SUPERSEDED. **P7 -- an `add` on an empty interval is an INSERTION.** The proposal was
      `{"op": "insert", "anchor": ..., "side": "above"}` because a range replace over the two code
      lines bounding a gap deletes both. Both halves are gone. **There is no range**: a page has a
      PLACE for the gap and the compositor sets places in order (`tests/test_galley.py:184-185`).
      And `side` was RULED OUT at `record.py:327-332`: *"NO `side`. The ADDRESS carries it: an `a`
      is a declaration's documentation, a `b` is a gap, a `c` is the room beside a line of code"*
      -- measured 2026-08-19, an `add` on a `c` address passed the gate carrying `side: above`,
      and there was no `beside` to write instead.

- [x] T6 -- SUPERSEDED HERE, tracked in its own file. **P3 -- the indent contract.** It is the
      same fact stated from the producer's side and it is filed at
      [`a-block-does-not-say-where-its-text-starts`](a-block-does-not-say-where-its-text-starts.md)
      (7/10, open). A second box here makes two counts of one job. ! The measurement it carries
      stays: a reviewer's `CHANGE` carried the RECORD's presentation indent, not the file's, and a
      six-line paragraph landed inside an `if ...: continue` body, annotating an unreachable
      position.

- [x] T7 -- SUPERSEDED HERE, tracked in its own file. **P2 -- give the WIDTH a stage, or fold it
      into stage 6.** Filed at
      [`compact-can-buy-lines-with-width`](compact-can-buy-lines-with-width.md) (1/6,
      in-progress). ! Still true 2026-08-23: `grep -ci "width\|column" references/compact.md`
      returns **0**. The measurement stays -- re-wrapping twelve over-width lines pushed a
      paragraph from 33 to 34 against a cap of 33, and the repo's own guard caught what the
      pipeline had not.

- [x] T8 -- FINISHED. **P1 (todo-tool) -- a `REASON` naming a sentence no `CLAIM` names.** The
      checker ships: `verdicts.py:170-191` returns *"Phrases a `REASON` quotes from its own
      paragraph that no `CLAIM` names"*, and its docstring records the rule P1 asked for --
      **REPORTED, NEVER FATAL**, because `REASON` legitimately discusses context.

- [ ] T9 -- **P8 -- somewhere to put a REPO-LEVEL tension no verdict can settle.** Two arose on
      that run: a citation form the style sheet demands and the width forbids, and a convention
      the reviewers deliberately worked against. ! `NEEDS A RULING` already exists
      (`verdicts.py:640`, `SKILL.md:771`) but it counts PARAGRAPHS carrying a substantive verdict
      -- a repo-level tension is attached to no paragraph and still has nowhere to go, so both had
      to be raised in conversation. Verify: the join's output carries a section a tension with no
      address can be written into, and a test that a record with no address reaches it.

- [ ] T10 -- **P1 (redacted-corpus) -- parse after every write, for the NON-PYTHON cases.**
      SUPERSEDED for the placeholder case (see the measurement above); the remainder is every
      language where the `proof kind changed (ast -> stripped)` guard cannot reach, because there
      is no parser. Verify: name what stands in for a parse at the `lexical` tier, or record that
      nothing can and close this.

- [x] T11 -- SUPERSEDED HERE, tracked in its own file. **RELEASE REQUIREMENT -- STAGE 4
      SERIALISES.** Roy, 2026-08-19: *"1 required -- ownership-context has to run else verdicts
      are made on statements that are not in the 'right' place. The other 3 are optional and only
      run after ownership-context has had its say."* !! **The SKILL.md contradiction this box was
      filed against is GONE**, verified 2026-08-23: `SKILL.md:30` gives 4a/4c, `:161-162` states
      *"ONE ROLE IS REQUIRED AND THREE ARE OPTIONAL"*, and `:550-551` dispatches
      `ownership-context` alone at 4a and the other three in one message at 4c. The build is
      [`ownership-is-read-first-but-nothing-makes-it-so`](ownership-is-read-first-but-nothing-makes-it-so.md)
      (3/10), which is where the remaining seven tasks are counted.

## Resolved -- do not redo

!! **These carry CHECKED boxes because an unchecked one is a claim that work remains.** Roy,
2026-08-18: *"a check box not-marked is left as something todo, even if it was superseded and no
longer necessary."* Held as prose in a table, these five were invisible to any recount -- the
README row read `0/9` while five were done.

- [x] T12 -- FINISHED. **P2, both reports -- the work list is withheld on a refusal.** Printed on
      a refusal now, labelled PROVISIONAL, exit unchanged.

- [x] T13 -- FINISHED. **P2, todo-tool -- N coordinated edits.** `reviewer-brief.md` says N
      records each read oddly alone, and that this is the format working rather than failing.

- [x] T14 -- FINISHED. **P1, todo-tool -- altitude.** A third question after checkable/necessary
      in the brief, and `compact.md` hands an over-specified paragraph back rather than cutting it.

- [x] T15 -- FINISHED. **P9, redacted-corpus -- `verdicts.py --out`.** Verified 2026-08-23 at
      `verdicts.py:293`. The stage-5 gate was unrunnable in the session type the skill is written
      for.

- [x] T16 -- FINISHED. **P3, todo-tool -- a prose file has no blocks.** Filed as
      [`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md); the measurement is what this
      adds -- **190 of 196 files** in one merge-base diff were `TODO/*.md`.

## Related

!! **LINKAGE AUDITED 2026-08-19, and it was ABSENT.** None of the fifteen tasks named the TODO it
closes; three were named in this section only, one of them already completed. A task that does
not name its TODO is a task nobody can close from either end. **Four now carry a link; the rest
have no TODO because none was ever filed**, which is the answer to "what closes this" rather than
an omission to fix by inventing one.

| task | closes |
| --- | --- |
| P3, todo-tool -- a prose file has no blocks | [`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md) |
| P3 -- the indent contract | [`a-block-does-not-say-where-its-text-starts`](a-block-does-not-say-where-its-text-starts.md) |
| P2 -- give the WIDTH a stage | [`compact-can-buy-lines-with-width`](compact-can-buy-lines-with-width.md) |
| RELEASE REQUIREMENT -- stage 4 serialises | [`ownership-is-read-first-but-nothing-makes-it-so`](ownership-is-read-first-but-nothing-makes-it-so.md) |
| P6, P10, P4, P8 | **no TODO filed.** Each is tracked here and nowhere else |

! **P5 had two candidates and neither was a clean fit** --
[`the-author-approves-blocks-and-never-sees-the-page`](the-author-approves-blocks-and-never-sees-the-page.md)
and [`7a-can-prove-the-change-by-applying-it-to-a-copy`](7a-can-prove-the-change-by-applying-it-to-a-copy.md).
It is closed at T3 rather than linked.

- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- P4 and P10 are record-shape changes and belong to that build.
- [`stage-5-is-the-only-stage-with-no-independent-reader`](stage-5-is-the-only-stage-with-no-independent-reader.md)
  -- the 5b that answers P5.
- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- D9 survives the JSON move, as redacted-corpus's own table said.
