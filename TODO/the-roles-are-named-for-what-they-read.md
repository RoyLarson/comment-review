# The four roles are named for what they read, not for the desk they sit at

```
Status:   blocked
Progress: 0 of 5 tasks done
Owner:    agents
Requires-Roy: false
Raised:   2026-08-19 (Roy approving the desk names while the paragraph rename landed,
          2026-08-19)
Updated:  2026-08-19 — DEFERRED past 0.2.4 -- Roy, 2026-08-19: 'I agree though on that
          we can wait.' Its scope is what a reviewer is HANDED; a role's NAME is what
          dispatches it.
```

## Objective

!! **THE FOUR ROLES ARE NAMED FOR WHAT THEY READ, NOT FOR THE DESK THEY SIT AT.**
`ownership-context`, `block-context`, `function-context`, `module-context` -- and `block` is not
even a term this system uses any more, ruled 2026-08-19 and replaced by `paragraph`.

**Roy approved the rename 2026-08-19**, and corrected the one name that did not fit the register:
*"to be consistent, maybe `fact-check-editor` instead of `fact-checker`, because it is supposed to
mark edits if it finds incorrect facts."* All four are EDITORS that emit edit marks; a
*fact-checker* verifies and hands back.

! **The desks were already recorded**, reconstructed 2026-08-17 after a compaction dropped them
and confirmed by Roy then, in
[`ownership-is-read-first-but-nothing-makes-it-so`](ownership-is-read-first-but-nothing-makes-it-so.md):

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
- the **file name** under `plugins/comment-review/agents/`
- the `--reviewers` value, and `verdicts.py` takes the role from the report file's STEM
- `[roles]` keys in `vocabulary.toml`, and the AGENTS glob `check_vocabulary.py` walks
- the key **every held report in `evidence/` is filed under**

! **So it is a version-bumping change to the installed plugin**, and every held run's reports keep
the old names. A conversion is not needed -- the reports are read by stem -- but a run replayed
against renamed agents will not match, and that is the thing to decide before starting.

! **Roy, 2026-08-19: *"I agree though on that we can wait."*** Not in 0.2.4, whose scope is what a
reviewer is HANDED.

## Tasks

- [ ] !! DECIDE FIRST what happens to the held runs in `evidence/`, whose reports
      are filed under the old stems and which `verdicts.py` reads BY STEM. Nothing
      needs converting to keep them readable; what breaks is replaying one against
      renamed agents.
- [ ] Rename the four agent files under `plugins/comment-review/agents/` and the
      ids inside them. ! The id is `comment-review:comment-review-<role>` and
      resolves only if the plugin was installed before the session began, so this
      is a version bump, not a hot edit.
- [ ] `[roles]` keys in `vocabulary.toml`, and the AGENTS glob
      `check_vocabulary.py` walks. ! The checker will refuse the half-state, which
      is a feature: it did exactly that during the paragraph rename.
- [ ] `SKILL.md`'s dispatch list, `--reviewers` examples, and every place a role
      is named in the shipped prose and in `docs/`.
- [ ] ! `ownership-is-read-first-but-nothing-makes-it-so` holds the desk table
      this works from. Cite it rather than re-deriving; it was reconstructed once
      already after a compaction dropped it.
