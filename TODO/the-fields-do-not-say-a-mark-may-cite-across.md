# The mark's fields permit a cross-citation and never say so

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-27 (Roy, on a finding whose subject is the relation between two
          places: "I would think one or both sides get a correct or query with a
          reason / The reason says this contradicts that / Along with the sources
          pointing at the 'that' / It is disjoint but both parts are fully cite-able
          and stated in the current findings. / Maybe better instructions are
          necessary for the findings fields")
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
same set, and the run data settles which one roles actually use: **292 source citations across
six roots** -- `src`, `scripts`, `docs`, `TODO`, `prototype` and `corpora` -- and `corpora/` is
GITIGNORED. Roles were already citing outside the git checkout before anything told them they
could.

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

- [ ] T1 -- State in `reviewer-brief.md` that a source may cite a place other than the mark's
      own, with the disagree-and-cite rule and its corollary. Verify: `grep -rn` for the rule
      returns exactly one path.
- [ ] T2 -- State the same for the fields whose misreading was measured -- `change` is a LINE
      ARRAY, `sources` are `{cite, verbatim}` pairs, `address` is COPIED and never built. Verify:
      each appears once, in the brief, not restated in an agent file.
- [ ] T3 -- State what `ran` is for and when it is OWED: a claim settled by RUNNING something
      carries the command that settled it. ! It is the only field the experiment ADDED, ratified
      by Roy 2026-08-27, so no role has ever been told it exists -- an undescribed field is an
      empty one. Verify: the brief names `ran`, and says a claim settled by execution without it
      is incomplete.
- [ ] T4 -- Say what a role does when it cannot tell which side of a disagreement is wrong.
      Verify: the brief names `query` for that case and says which of its three shapes.
- [ ] T5 -- * Rule on `query: outside the checkout`, which now points the OTHER WAY from T1.
      One word bounds two things in opposite directions: a source may cite the LIBRARY (wider),
      while that query shape says the evidence is unreachable and lists *gitignored* among its
      cases -- yet `corpora/` is gitignored and carries 292 citations' worth of real evidence.
      ! The three shapes are a CLOSED SET and the word list is required (Roy, 2026-08-26: *"else
      they start inventing words"*), so this is a ruling and not an edit. Verify: the ruling says
      whether the shape's cases change or its name does, and is recorded in `decision-log.md`.
- [ ] T6 -- Confirm no agent file restates any of T1-T5. Verify: `grep -rn` over
      `plugins/comment-review/agents/` returns nothing for the rule's phrase.
