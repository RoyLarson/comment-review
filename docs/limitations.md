# Limitations

## Notes for Changes

**An example carries the SHAPE and nothing else.** Two ways it carries more:

- **A real quotation** teaches a reviewer to recognise *that comment* instead of the shape,
  and it rots -- a hygiene skill carrying its own obituary. Measurements anonymise for free.
- **A settled term in a foreign sense.** An example about a database `record` teaches a
  second meaning for a word a reviewer emits, and `vocabulary.py` then hands that role a
  definition it only appeared to need. ! Nothing catches this. `vocabulary_sweep.py` skips
  every word already in `vocabulary.toml`, because it hunts terms that are NOT yet settled;
  `check_vocabulary.py` compares distribution against usage, never usage against meaning. A
  term used in two senses is the complement of both, and is found by a person reading.

!! **THE BUDGET IS THE POINT, AND IT IS PER FILE.** A **budget** is how much CONTEXT one of
these files costs everyone who loads it, measured in lines. That is the only budget this
system has -- a comment's line limit is its `cap`, a different thing, and the census a run
produces is not a budget at all. ! **RULE FILES are budgeted; RUN DATA is not.** A census
large enough to name every interval in a file is the cost of doing the job properly, and
trading its completeness for size would buy nothing this budget is protecting. A tight budget forces
a *generalization*
instead of one rule per incident; without it these files become a case file for whatever repo
they last ran in -- fitted to that project, useless to the next. **This is the opposite of the
cap rule for comments**, and the reason is what is optimised: **a comment must be true about
ONE thing, so cutting to fit deletes its evidence; a rule must cover MANY, so cutting to fit
forces the covering abstraction.**

Four questions before adding anything. Would it fire in a repo about something else? Is the
evidence a **number or ratio** rather than a story? Does it change what a reviewer **does**?
! And is **the REASON** true in a fresh checkout? A rule can be right and its reason fitted to
this repo's harness -- a reader who tests the reason, finds it false, and drops the rule is the
failure that question catches.

**Cutting has one exception: ROLE FRAMING is not justification.** *"You are the PROOFREADER"*,
*"You did not write this text, and that is the point"* -- a sentence establishing the role an
agent occupies stays, though no rule depends on it. Roy, 2026-08-16: *"the role framing is
doing work."* An agent that occupies a role writes in it better than one consulting a glossary,
which is the same argument the editorial register rests on. Everything else that only explains
WHY a rule exists is cuttable; state the rule and its discriminator instead.
Assume a reasoning reader: state the rule and its discriminator, not the argument for it. If two
rules are instances of one generalization, write the generalization and delete both.

## !! A RULE PAYS FOR ITS OWN LINES, IN ONE OF TWO CURRENCIES

Roy, 2026-08-18. **A new rule does not have to displace another.** It has to earn the context it
costs, and there are exactly two ways:

**1. It CATCHES something.** Subjective, and the subjectivity is admitted -- but the cost of
missing is not, and it lands twice:

- **A defect a HUMAN finds that this system should have found is how the tool stops being
  used.** Not a bad run: a reason to stop running it.
- **A miss buys a SECOND and THIRD pass**, and those rack up tokens fast. One run over two files
  and 154 prose blocks measured 870,000 subagent tokens; a rule that prevents one re-run has
  paid for far more prose than it costs.

**2. It SAVES A SEARCH.** Pure token cost on the FIRST run. A reviewer that would otherwise scan
twenty documents hunting for what a rule could have told it outright is spending the budget this
file exists to protect -- and spending it on discovery rather than on judgement.

! **Both are hard to measure in aggregate and neither is a formula.** What each one gives you is
a QUESTION to answer about a candidate rule, and a rule that answers neither is the one to cut.
! And the two are not the same test: a rule can catch nothing new and still earn its place by
making a claim settleable without opening another file.

! **Length still matters, which is why the numbers stay.** They are what tells you a file has
grown and that the trade should be looked at -- not a ceiling that automatically evicts a rule.

**The four editorial roles, measured 2026-08-18:**

| agent file (`plugins/comment-review/agents/`) | lines |
| --- | --- |
| `comment-review-ownership-context.md` | 111 |
| `comment-review-block-context.md` | 117 |
| `comment-review-function-context.md` | 124 |
| `comment-review-module-context.md` | 130 |

!! **THREE OF THE FOUR HAD GROWN, AND THAT IS THE EVIDENCE, NOT THE DEFECT.**
`ownership-context` 91 -> 111, `block-context` 110 -> 117, `module-context` 128 -> 130. Roy,
2026-08-18: *"I have allowed expansion on those files just because of this"* -- because the
rules added paid in one of the two currencies above. **A replaces-one rule that was live would
have refused all three**, so the file was describing a policy it was not running, and the growth
is what proves it.

! A count that no longer matches `wc -l` is still a finding against this file -- but it is a
finding about the NUMBER being stale, not about the file being over a limit. Update it and say
what the growth bought.

! **A rule belongs in exactly one file.** Shared reviewer contract ->
`reviewer-brief.md`; one role's -> that role's agent definition; a stage's procedure -> that
stage's file under `references/` (`residue-check.md`, `compact.md`, `write.md`, `review.md`); a
rule a SCRIPT enforces -> that script's docstring (`census.py`, `annotate.py`, `repo.py`,
`referrers.py`, `verdicts.py`, `run_context.py`, `prove_unchanged.py`, `vocabulary.py`);
orchestration -> here. Restating one across two files is
the antipattern this skill exists to find, and the four agents are the place it will happen --
they read alike and invite copy-paste.

!! **THE TWO LARGEST FILES A RUN LOADS AS CONTEXT HAVE NO BUDGET.** A reviewer loads its role
file plus the brief, and four dispatched in parallel load **four copies of the brief**. The
numbers above budget the four ROLE files only -- the smallest part of what a run actually costs.

| | 2026-08-16 | 2026-08-18 | |
| --- | ---: | ---: | --- |
| `reviewer-brief.md` | 11,579 | 24,000 | paid FOUR times |
| `SKILL.md` | 45,257 | 62,531 | paid once, by the task agent |

!! **THE BRIEF HAS MORE THAN DOUBLED IN TWO DAYS, WHICH IS THIS WARNING COMING TRUE.** Every
addition was argued on its own and none was weighed against the file, because nothing measures
it -- the four role files are counted line by line while the thing costing four times as much
is not. ! Re-measure it whenever it is edited and say what the growth bought, the same
discipline the role table gets. ! Larger files ship -- `census.py` is 31 KB -- but
are EXECUTED, never read into a prompt.

**Any Python shipped here must be generic** -- no hardcoded paths, no assumed directory names,
no cap baked into a script whose prose says the skill has no cap of its own.