# The mark's fields permit a cross-citation and never say so

```
Status:   open
Progress: 5 of 8 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-27 (Roy, on a finding whose subject is the relation between two
          places: "I would think one or both sides get a correct or query with a
          reason / The reason says this contradicts that / Along with the sources
          pointing at the 'that' / It is disjoint but both parts are fully cite-able
          and stated in the current findings. / Maybe better instructions are
          necessary for the findings fields")
Updated:  2026-08-28 — T2 STATES A FACT THAT IS NOW SUPERSEDED, and the task is worked
          with this correction rather than reworded. It says `change` is a LINE ARRAY.
          Roy ruled 2026-08-28: "`change` needs to be the updated paragraph as raw text
          not lines or sentences. This will make it easier to diff per the rest of the
          stages." The array form was chosen against two measured transcription
          failures; raw text makes both LOUDER, because a diff against the seeded
          `raw_text` shows a stripped comment marker or a truncated paragraph directly.
          See `docs/the-mark.md`, which is now the SOURCE for the mark's shape, and
          `decision-log.md Process: #37`. ! T2's other two facts stand unchanged --
          `sources` are `{cite, verbatim}` pairs, `address` is COPIED and never built. !
          And `move` is the one instruction whose `change` is not a single paragraph: it
          carries the COMPOSITE of both, because a move is a delete plus an add under
          one label and is indivisible.
Updated:  2026-08-28 — T5 ticked. The three ruled shapes now replace the old set in
          reviewer-brief.md (the only agent-facing occurrence). A repo-wide `grep -rn
          "outside the checkout"` still finds it in `src/comment_review/desk/mark.py:43`
          (and its built copy) -- a comment recording what the shapes REPLACED, matching
          this repo's own convention for keeping an error legible
          (`check_vocabulary.py`'s MENTION/RETIRED pattern) -- and in
          `tests/test_mark.py` (asserting the OLD names are refused), plus `evidence/`,
          `prototype/`, `.superpowers/` and other TODO files, all historical or
          archival. None is live agent-facing prose. Task 5, backend.
```

## Objective

**A finding whose subject is the RELATION between two places needs no new field, and nothing
tells a role that.** The shape already carries it: mark the place that is wrong, state the
contradiction in `reason`, and cite the other place in `sources`.

!! **MEASURED, TWICE, INDEPENDENTLY.** `module-context` produced exactly that shape in rounds 2
and 3 of the 2026-08-27 experiment, on the same place, without being told it could:

    address   src:comment_review:results:compositor.py@a0
    mark      correct
    reason    "This file defines no `__main__` block or argument parser; the only CLI
               entry point for identity-checking lives in commands/compositor.py"
    sources   src/comment_review/commands/compositor.py:5  | <the banner>
              src/comment_review/commands/compositor.py:15 | def main(argv: ...) -> int:

! **THE RISK IS NOT THAT IT FAILS -- IT IS THAT IT DEPENDS ON NERVE.** The brief never says a
source may cite a place other than the mark's own. A role that hesitates files
`query: outside my role` instead, which is a BOUNDARY REPORT and not work -- so the
best-corroborated finding of the run is downgraded to a note about scope. **The shape permitted
it; the instructions were silent; survival depended on temperament.**

!! **AND SILENCE ON A FIELD IS THE MEASURED CAUSE OF EVERY OTHER SHAPE DEFECT.** Same
experiment: `change` returned as a string where the spec wanted a line array (one role returned a
paragraph with its `#` markers gone, which would have made the file a `SyntaxError`); `sources`
returned as `path:line | text` strings rather than checkable pairs; bare cues written where the
row carried a full address. Each is a role reading prose and filling it in plausibly. **A prose
template cannot be wrong at the role; it can only be misread.**

### The proposed instruction, for review

For `sources`: *a source may cite any place in the LIBRARY -- every file in the project under
review -- including another place on this page. Where your claim is that two places disagree,
mark the one that is WRONG and cite the other as the evidence that it is.*

The corollary, which is the part that keeps it honest: *if you cannot tell which side is wrong,
that is a `query`, not two `correct`s.*

!! **THE SCOPE IS THE LIBRARY AND NOT THE CHECKOUT.** Roy, 2026-08-27, on a first draft that
said *"any place in the checkout"*: *"project/library Not just checkout."* ! The two are not the
same set, and the run data settles which one roles actually use: **382 source citations across
nine roots** -- `src`, `scripts`, `corpora`, `prototype`, `TODO`, `docs`, `CLAUDE.md`, `plugins`
and `tests` -- and `corpora/` is GITIGNORED while `prototype/` does not run. Roles were already
citing both before anything told them they could.

! **CORRECTED 2026-08-27, from 292 across six.** The first count was taken over the four role
STEMS and so excluded every fan-out agent, whose files are named for the file they read.
Re-derivable: `uv run python evidence/the-loop-measured-2026-08-27/derive.py`.

! **AND THE NARROWER WORD WOULD HAVE RETIRED REAL EVIDENCE.** `prototype/` does not run and
`corpora/` is fetched rather than tracked; both are where a claim about what this system USED to
do, or how it behaves on real source, is settled. A rule saying *the checkout* invites a role to
drop exactly those.

### What this does NOT cover

! **`move` is a separate, narrower defect and it is `backend`'s.** A `move` names two places in
one mark (`from:` + `to:`) -- it is the existing proof that two-endedness is expressible -- but
`collate` buckets on a single `mark["address"]`, so a `move` out of `a0` into `a8` lands in the
`a0` bucket while another role's mark on `a8` lands in its own. The two never meet and the
merge-or-fight table never sees the overlap. Filed as
[`collate-buckets-a-move-at-one-end`](collate-buckets-a-move-at-one-end.md).

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- State in `reviewer-brief.md` that a source
      may cite a place other than the mark's own, with the disagree-and-cite
      rule and its corollary. Verify: `grep -rn` for the rule returns exactly
      one path.
- [x] T2 | FINISHED | unknown | T2 -- State the same for the fields whose
      misreading was measured -- `change` is the updated paragraph in RAW TEXT,
      `sources` are `{cite, verbatim}` pairs, `address` is COPIED and never
      built. Verify: each appears once, in the brief, not restated in an agent
      file. ! **THIS SAID `change` IS A LINE ARRAY, AND WAS COMPLETED UNDER THAT
      RULE.** Roy ruled 2026-08-28 that `change` is the updated paragraph as raw
      text (`docs/the-mark.md`), and the code followed on 2026-08-29 --
      `desk/mark.parse` now refuses a list BY NAME. **A checked box asserting a
      superseded fact reads as settled**, which is why the wording is corrected
      here rather than left to be re-derived. Tracked in
      [`change-is-raw-text-not-lines`](change-is-raw-text-not-lines.md).
- [x] T3 | FINISHED | unknown | T3 -- State what `ran` is for and when it is
      OWED: a claim settled by RUNNING something carries the command that
      settled it. ! It is the only field the experiment ADDED, ratified by Roy
      2026-08-27, so no role has ever been told it exists -- an undescribed
      field is an empty one. Verify: the brief names `ran`, and says a claim
      settled by execution without it is incomplete.
- [ ] T4 | T4 -- Say what a role does when it cannot tell which side of a
      disagreement is wrong. Verify: the brief names `query` for that case and
      says which of its three shapes.
- [x] T5 | FINISHED | unknown | T5 -- Replace the three `query` shapes with the
      set RULED in `decision-log.md Process: #33` -- `outside-my-role`,
      `unable-to-determine`, `human-review-necessary`. ! The old set is at
      SEVENTEEN sites; the ones that must move are `reviewer-brief.md:411-414`,
      `SKILL.md`, `agents/comment-review-module-context.md`, and
      `record.py`/`verdicts.py`/`desk.py` in `prototype/`. Verify: `grep -rn
      "outside the checkout"` returns nothing outside `docs/` (history keeps the
      old set legible) and `corpora/`.
- [?] T6 | T6 -- * RULE the register for all three names. ! The CATEGORIES are
      ruled and are not reopened by this -- only the words. Candidates, Roy
      2026-08-27:

          human-review-necessary  ->  author query   only the author holds the intent
          unable-to-determine     ->  unverified     the copy desk's word for a claim
                                                     it could not check
          outside-my-role         ->  outside my remit

      !! **THE THIRD IS NOT A PROPOSAL -- IT IS ALREADY IN THE SHIPPED TREE**, at
      `agents/comment-review-module-context.md:102`, `agents/comment-review-ownership-context.md:84`
      and `references/reviewer-brief.md:428`, and `remit` was register-checked in 2026-08-16 when
      it replaced `jurisdiction`. **So the shape says `role` while the prose a role reads says
      `remit`: one concept, two words.** Neither is retired and both are correct English, which
      is why no gate sees it.

      ! **THE SET IS NOT FORMALLY PARALLEL AND MUST NOT BE FORCED TO BE.** Two name an
      ADDRESSEE, `unverified` names a STATE -- there is nobody to ask, which is exactly what
      separates it from the other two. A third "X query" would invent an addressee.

      ! **`desk` WAS CONSIDERED AND IS REFUSED.** The newsroom register fits, and it appears
      ZERO times in shipped prose -- but it names a whole sub-package in `src/`, so adopting it
      builds the `notations`/`annotations` collision on purpose.

      Verify: the ruling is recorded, `vocabulary.toml` agrees, and `grep -rn "outside my role"`
      over `plugins/` returns nothing if `remit` wins.
- [x] T7 | FINISHED | unknown | T7 -- Make collate ACT on `unable-to-determine`,
      which is what the new axis buys. If another role returned a substantive
      mark at the same place, the flow can see it settled what this role could
      not. Verify: a test where role A is `unable-to-determine` at a place and
      role B has a `correct` there, and the place does NOT reach the chief. !
      `backend`'s to write; filed here because the shape it depends on lives in
      the brief.
- [ ] T8 | T8 -- Confirm no agent file restates any of T1-T7. Verify: `grep -rn`
      over `plugins/comment-review/agents/` returns nothing for the rule's
      phrase. ! It does TODAY -- `comment-review-module-context.md` carries the
      old shapes.
