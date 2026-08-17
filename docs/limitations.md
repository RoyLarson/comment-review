# Limitations

## Notes for Changes

**An example carries the SHAPE and nothing else.** Two ways it carries more:

- **A real quotation** teaches a reviewer to recognise *that comment* instead of the shape,
  and it rots — a hygiene skill carrying its own obituary. Measurements anonymise for free.
- **A settled term in a foreign sense.** An example about a database `record` teaches a
  second meaning for a word a reviewer emits, and `vocabulary.py` then hands that role a
  definition it only appeared to need. ⚠ Nothing catches this. `vocabulary_sweep.py` skips
  every word already in `vocabulary.toml`, because it hunts terms that are NOT yet settled;
  `check_vocabulary.py` compares distribution against usage, never usage against meaning. A
  term used in two senses is the complement of both, and is found by a person reading.

⚠⚠ **THE BUDGET IS THE POINT, AND IT IS PER FILE.** A **budget** is how much CONTEXT one of
these files costs everyone who loads it, measured in lines. That is the only budget this
system has — a comment's line limit is its `cap`, a different thing, and the census a run
produces is not a budget at all. ⚠ **RULE FILES are budgeted; RUN DATA is not.** A census
large enough to name every interval in a file is the cost of doing the job properly, and
trading its completeness for size would buy nothing this budget is protecting. A tight budget forces
a *generalization*
instead of one rule per incident; without it these files become a case file for whatever repo
they last ran in — fitted to that project, useless to the next. **This is the opposite of the
cap rule for comments**, and the reason is what is optimised: **a comment must be true about
ONE thing, so cutting to fit deletes its evidence; a rule must cover MANY, so cutting to fit
forces the covering abstraction.**

Four questions before adding anything. Would it fire in a repo about something else? Is the
evidence a **number or ratio** rather than a story? Does it change what a reviewer **does**?
⚠ And is **the REASON** true in a fresh checkout? A rule can be right and its reason fitted to
this repo's harness — a reader who tests the reason, finds it false, and drops the rule is the
failure that question catches.

**Cutting has one exception: ROLE FRAMING is not justification.** *"You are the PROOFREADER"*,
*"You did not write this text, and that is the point"* — a sentence establishing the role an
agent occupies stays, though no rule depends on it. Roy, 2026-08-16: *"the role framing is
doing work."* An agent that occupies a role writes in it better than one consulting a glossary,
which is the same argument the editorial register rests on. Everything else that only explains
WHY a rule exists is cuttable; state the rule and its discriminator instead.
Assume a reasoning reader: state the rule and its discriminator, not the argument for it. At
budget, a new rule **replaces** one — and if two rules are instances of one generalization,
write the generalization and delete both.

**The budget for the four editorial roles is their current length, and these are the numbers:**

| agent file (`plugins/comment-review/agents/`) | lines |
| --- | --- |
| `comment-review-ownership-context.md` | 96 |
| `comment-review-block-context.md` | 111 |
| `comment-review-function-context.md` | 126 |
| `comment-review-module-context.md` | 121 |

⚠ Each is AT budget, so the replaces-one rule is live on all four. Raising a number here is a
change to this file that a reviewer rules on, not a side effect of adding a rule — and a count
that no longer matches `wc -l` is a finding against this file.

⚠ **A rule belongs in exactly one file.** Shared reviewer contract →
`reviewer-brief.md`; one role's → that role's agent definition; a stage's procedure → that
stage's file under `references/` (`residue-check.md`, `compact.md`, `write.md`, `review.md`); a
rule a SCRIPT enforces → that script's docstring (`census.py`, `annotate.py`, `repo.py`,
`referrers.py`, `verdicts.py`, `run_context.py`, `prove_unchanged.py`, `vocabulary.py`);
orchestration → here. Restating one across two files is
the antipattern this skill exists to find, and the four agents are the place it will happen —
they read alike and invite copy-paste.

⚠⚠ **THE TWO LARGEST FILES A RUN LOADS AS CONTEXT HAVE NO BUDGET.** Measured 2026-08-16:
`reviewer-brief.md` is 10,888 bytes and `SKILL.md` 48,421. A reviewer loads its role file
plus the brief — about 17 KB, of which **61% is the brief, not its own role** — and four
reviewers dispatched in parallel load **four copies of it**, 43 KB of the run's 70 KB. The
numbers above budget the four role files only: 27 KB of the 217 KB shipped, and the
smallest part of what a run actually costs. ⚠ Larger files ship — `census.py` is 31 KB — but
are EXECUTED, never read into a prompt.

**Any Python shipped here must be generic** — no hardcoded paths, no assumed directory names,
no cap baked into a script whose prose says the skill has no cap of its own.