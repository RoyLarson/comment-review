# Limitations

## Notes for Changes

**Every example here is invented. Keep it that way.** A real quotation teaches a reviewer to
recognise *that comment* instead of the shape, and it rots — a hygiene skill carrying its own
obituary. Measurements anonymise for free.

⚠⚠ **THE BUDGET IS THE POINT, AND IT IS PER FILE.** A tight budget forces a *generalization*
instead of one rule per incident; without it these files become a case file for whatever repo
they last ran in — fitted to that project, useless to the next. **This is the opposite of the
cap rule for comments**, and the reason is what is optimised: **a comment must be true about
ONE thing, so cutting to fit deletes its evidence; a rule must cover MANY, so cutting to fit
forces the covering abstraction.**

Three questions before adding anything. Would it fire in a repo about something else? Is the
evidence a **number or ratio** rather than a story? Does it change what a reviewer **does**?
Assume a reasoning reader: state the rule and its discriminator, not the argument for it. At
budget, a new rule **replaces** one — and if two rules are instances of one generalization,
write the generalization and delete both.

**The budget for the four editorial roles is their current length, and these are the numbers:**

| agent file (`plugins/comment-review/agents/`) | lines |
| --- | --- |
| `comment-review-ownership-context.md` | 101 |
| `comment-review-block-context.md` | 101 |
| `comment-review-function-context.md` | 129 |
| `comment-review-module-context.md` | 120 |

⚠ Each is AT budget, so the replaces-one rule is live on all four. Raising a number here is a
change to this file that a reviewer rules on, not a side effect of adding a rule — and a count
that no longer matches `wc -l` is a finding against this file.

⚠ **A rule belongs in exactly one file.** Shared reviewer contract →
`reviewer-brief.md`; one role's → that role's agent definition; a stage's procedure → that
stage's file under `references/` (`residue-check.md`, `compact.md`, `apply.md`, `review.md`); a
rule a SCRIPT enforces → that script's docstring (`census.py`, `referrers.py`, `verdicts.py`,
`run_context.py`, `prove_unchanged.py`); orchestration → here. Restating one across two files is
the antipattern this skill exists to find, and the four agents are the place it will happen —
they read alike and invite copy-paste.

**Any Python shipped here must be generic** — no hardcoded paths, no assumed directory names,
no cap baked into a script whose prose says the skill has no cap of its own.