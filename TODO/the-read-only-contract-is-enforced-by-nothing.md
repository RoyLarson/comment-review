# The read-only contract is enforced by nothing, and four reviewers wrote files

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session · Roy (⭐ 1 ruling wanted — task 1)
Raised:   2026-08-17 (the 0.2.0 builder run: the operating session noticed scratch
          files left in the run directory by the reviewers themselves)
```

## Objective

**The brief's first rule is absolute and nothing checks it.** `reviewer-brief.md`: *"Do not
edit, write or format any file. Not code, not comments, not docs. A reviewer that fixes what it
finds has destroyed the finding."*

Measured on the builder run: all four reviewers left artifacts in the run directory —
`gen.py`, `blocks.json`, `part_*.md`, and a duplicate `census_prose.txt`. Nobody was told; the
operating session found them by looking.

⚠ **The agents are granted every tool.** `plugins/comment-review/agents/*.md` carry `name`,
`description` and `model` and **no `tools:` key**, so each reviewer holds `Write`, `Edit` and
`NotebookEdit`. The mechanism to restrict them exists and is used elsewhere in the same
registry — the `Explore` agent is declared *all tools except `Agent`, `Artifact`,
`ExitPlanMode`, `Edit`, `Write`, `NotebookEdit`*.

## ⚠⚠ The rule conflates two different things

| what a reviewer writes | does it destroy a finding? | currently |
| --- | --- | --- |
| a file **under review** | **yes** — the census goes stale, and the fix retires the finding | forbidden, undetected |
| a scratch file elsewhere | no | forbidden by the letter of the rule, and **useful** |

⚠ **`gen.py` is provenance.** A script a reviewer wrote to compute its findings is the only
artifact in a report that can be RE-RUN, which is a stronger check than any `SOURCES` line. This
repo's standing rule is to grade a run from its artifacts and never from its own report, so a
blanket ban on scratch throws away the one re-runnable thing a reviewer can produce.

## ⚠⚠ Nothing sits between the census and the join

The census is taken at stage 3 and the reviewers run at stage 4. **If a reviewer edits a file
under review, the census is silently stale and no stage notices.** `prove_unchanged.py` runs at
7b, against the pre-edit ref, and proves only that *executable code* reads the same — its own
docstring says so: the AST proof blanks every docstring, and the `stripped` proof deletes every
comment. **A reviewer that edited a COMMENT is invisible to it by construction**, because
comments are exactly what both proofs discard.

⚠ **0.2.0 added an accidental tripwire, and it is the only one there is.** `address_problem`
compares each record's transcribed `original` against the census text. A reviewer that edited a
block would transcribe the edited text and mismatch. That is not why the check exists, and it
bears on how far it can be relaxed — see
[`a-scope-declaration-costs-as-much-as-a-finding`](a-scope-declaration-costs-as-much-as-a-finding.md).

## Tasks

- [ ] ⭐ **RULE on which of the two the contract forbids.** Recommendation: forbid writing to
      any file **under review or in the checkout**, and permit scratch in the run directory —
      then say so, because the current sentence forbids both and the reviewers ignored it.
      ⚠ A rule four agents broke on its first measured run is not being read as absolute; make
      it narrower and enforceable rather than broader.

- [ ] **Add `tools:` to all six agent files.** Drop `Write`, `Edit` and `NotebookEdit` from the
      four reviewers at minimum. ⚠ This does NOT close it — `Bash` can redirect to a file — but
      it removes the path that requires no ingenuity, and it makes the intent machine-readable
      instead of prose.

- [ ] ⚠⚠ **Decide what the reviewers still need.** Their own vocabulary is built from verbs they
      are instructed in — `ran`, `grep`, `count`, `resolve`, `verify` — so a lockdown that
      removes execution removes the remit with it. `QUERY_ATTEMPTED` refuses a query that names
      no attempted check, so a reviewer that cannot check cannot pass its own gate.

- [ ] **Detect a stale census rather than trusting the rule.** Hash the files under review after
      stage 3 and re-check before the join; a changed file means the census no longer describes
      the tree and every record on it is suspect. ⚠ Cheaper than it sounds — `repo.py` already
      reads these files, and the join already loads the census.

- [ ] **Keep the scratch files in the evidence package**, in a labelled subdirectory. They are
      the measurement this file rests on, and the run that produced them is the first that could
      have shown it.

- [ ] **Say whether `prove_unchanged.py`'s scope is a gap or a boundary.** It proves executable
      code unchanged, which is the claim the skill makes to its users — but this run shows the
      claim nobody makes is *the reviewers changed no prose*, and that one has no proof at all.

## Related

- [`stage-5-is-the-only-stage-with-no-independent-reader`](stage-5-is-the-only-stage-with-no-independent-reader.md)
  — the other place a stage's output is trusted rather than checked.
