# The four roles are named for what they read, not for the desk they sit at

```
Status:   deferred
Progress: 0 of 4 tasks done
Owner:    agents
Requires-Roy: false
Raised:   2026-08-19 (Roy approving the desk names while the paragraph rename landed,
          2026-08-19)
Updated:  2026-08-19 -- DEFERRED past 0.2.4 -- Roy, 2026-08-19: 'I agree though on that
          we can wait.' Its scope is what a reviewer is HANDED; a role's NAME is what
          dispatches it.
Triaged:  2026-08-23 -- the fifth box was a citation instruction, not a checkpoint; it is
          ticked and its content is in the Objective. Status corrected from `blocked` to
          `deferred`: nothing external blocks it, Roy ruled it waits
```

## Objective

!! **THE FOUR ROLES ARE NAMED FOR WHAT THEY READ, NOT FOR THE DESK THEY SIT AT.**
`ownership-context`, `block-context`, `function-context`, `module-context` -- and `block` is not
even a term this system uses any more, ruled 2026-08-19 and replaced by `paragraph`.

**Roy approved the rename 2026-08-19**, and corrected the one name that did not fit the register:
*"to be consistent, maybe `fact-check-editor` instead of `fact-checker`, because it is supposed to
mark edits if it finds incorrect facts."* All four are EDITORS that emit edit marks; a
*fact-checker* verifies and hands back.

! **The desk table this works from is in
[`ownership-is-read-first-but-nothing-makes-it-so`](ownership-is-read-first-but-nothing-makes-it-so.md)**,
reconstructed 2026-08-17 after a compaction dropped it and confirmed by Roy then. **Cite it
rather than re-deriving it** -- it has already been rebuilt once from nothing:

| role | the desk | what that desk does |
| --- | --- | --- |
| `ownership-context` | notes editor | checks every note hangs off the sentence it is actually about |
| `block-context` | fact-check editor | takes each claim to a source and resolves it; owns nothing about placement |
| `function-context` | line editor | section level -- does this section deliver what its heading announces |
| `module-context` | developmental editor | reads the whole work and asks whether it argues ONE thing |

!! **UNLIKE `block` -> `paragraph`, THESE ARE ON THE WIRE.** That rename touched nothing a
consumer reads -- measured, the census JSON has no `block` key and neither does a record slot.
A role name is different, and it is load-bearing in five places at once:

- the **plugin agent id**, `comment-review:comment-review-block-context`, which the skill
  dispatches by name and which resolves only if the plugin was installed before the session began
- the **file name** under `plugins/comment-review/agents/` -- verified 2026-08-23, all four are
  still `comment-review-<role>.md`
- the `--reviewers` value, and `verdicts.py` takes the role from the report file's STEM
- `[roles]` keys in `references/vocabulary.toml` -- verified 2026-08-23 at `:108` and `:148` --
  and the AGENTS glob `check_vocabulary.py` walks
- the key **every held report in `evidence/` is filed under**. Verified 2026-08-23: two packages
  survive in the tree, `evidence/cycle-0.2.3/records/` and
  `evidence/comment-review-skill-023-dev-review/records/`, each holding
  `ownership-context.json`, `block-context.json`, `function-context.json` and
  `module-context.json`

! **So it is a version-bumping change to the installed plugin**, and every held run's reports keep
the old names. A conversion is not needed -- the reports are read by stem -- but a run replayed
against renamed agents will not match, and that is the thing to decide before starting.

! **Roy, 2026-08-19: *"I agree though on that we can wait."*** Not in 0.2.4, whose scope is what a
reviewer is HANDED. **Deferred is not done** -- the four tasks below are unstarted work waiting on
that scope closing, not work overtaken.

## Tasks

- [ ] T1 -- * !! DECIDE FIRST what happens to the two held runs in `evidence/`, whose
      reports are filed under the old stems and which `verdicts.py` reads BY STEM.
      Nothing needs converting to keep them readable; what breaks is replaying one
      against renamed agents. Finishes the day Roy answers.

- [ ] T2 -- Rename the four agent files under `plugins/comment-review/agents/` and the
      ids inside them. ! The id is `comment-review:comment-review-<role>` and resolves
      only if the plugin was installed before the session began, so this is a version
      bump, not a hot edit. Verify: `claude plugin validate plugins/comment-review` exits
      0 and `grep -rn "comment-review-block-context" plugins/` returns nothing.

- [ ] T3 -- Move the `[roles]` keys in `references/vocabulary.toml` to the new names.
      Verify: `uv run python scripts/check_vocabulary.py` exits 0. ! The checker will
      refuse the half-state, which is a feature: it did exactly that during the paragraph
      rename.

- [ ] T4 -- Rename the role everywhere the shipped prose and `docs/` name it: `SKILL.md`'s
      4a/4c dispatch table, the `--reviewers` examples, `CLAUDE.md`'s command block.
      Verify: `grep -rn "ownership-context\|block-context\|function-context\|module-context"
      plugins/ docs/ CLAUDE.md` returns only the held-run paths T1 ruled on.
