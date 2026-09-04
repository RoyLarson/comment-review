# `apply` named two different stages -- stage 5 is APPLY, stage 7b is WRITE

```
Status:   COMPLETE 2026-08-16
Progress: 6 of 6 tasks closed
Owner:    session
Raised:   2026-08-15 (Roy, stating the workflow as "Apply, Compact, Approval")
```

## Objective

**One word named two stages.** Applying a MARK produces replacement text at stage 5; applying
APPROVED TEXT writes it to disk at 7b. Both were `apply`, and the system's own rule is that a
name belongs in exactly one place. Roy's workflow sentence puts "Apply" at stage 5, and his
framing of an edit mark puts it there too -- *"the preferred action that, **if applied**, would
improve the comments"* -- while `sweep`'s retirement earlier the same day had put APPLY on 7b.

**Ruled B: stage 5 is `APPLY`, stage 7b is `WRITE`, and `EDIT` is retired.**

! **Not a vocabulary task.** Settling which word goes where is naming, but the change is a
stage rename across the pipeline diagram, the stage table, a reference filename and a published
CHANGELOG entry -- so it is its own refactor and is tracked here rather than in
[`eight-terms-have-no-definition-and-angle-means-five-things`](eight-terms-have-no-definition-and-angle-means-five-things.md).

## Tasks

- [x] T1 | FINISHED | unknown | * Rule A or B. **Roy ruled B, 2026-08-15.** B
      puts the word where his own sentences already put it, and `WRITE` says the
      one thing 7b does that no other stage does: touch a file. A would have
      kept `APPLY` on 7b and changed three stage-5 sites to say "write".

- [x] T2 | FINISHED | unknown | Apply it to the stage-5 sense. **Done 2026-08-15
      -- and under B these needed NO change.** `SKILL.md:51` (`correct` ->
      "apply the true/false pair"), `:52` (`patch` -> "apply the rewrite") and
      `reviewer-brief.md:116` ("the task agent applies every `correct` before
      any `patch`") were already using `apply` for what stage 5 does. They
      became correct the moment stage 5 took the name, which is the strongest
      evidence B is the right way round.

- [x] T3 | FINISHED | unknown | Apply it to the stage-7b sense. **Done
      2026-08-15** -- `references/apply.md` renamed to `write.md` with `git mv`,
      plus the pipeline diagram, the stage table, the stage section,
      `SKILL.md:37,88,716,721`, `compact.md:119,132`, `census.py:183`,
      `prove_unchanged.py` (4 sites), `comment-review-review.md:3`, `README.md`,
      `CLAUDE.md` (4), `marketplace.json` and `docs/limitations.md`'s routing
      list.

- [x] T4 | FINISHED | unknown | Amend the `[Unreleased]` CHANGELOG entry. **Done
      2026-08-15** -- the `sweep` entry no longer claims 7b is APPLY, and the
      stage rename is published as its own breaking change, naming the file move
      so anything loading `apply.md` by path is warned.

- [x] T5 | FINISHED | unknown | Check the word did not leak into the scripts.
      **Done 2026-08-15** -- `census.py:183` and `prove_unchanged.py` both named
      the 7b sense and now say WRITE. No ordinary-English use of "apply" needed
      keeping, unlike plain-English "sweep the file", which survived `sweep`'s
      retirement.

- [x] T6 | FINISHED | unknown | **Moot 2026-08-16** -- the inventory was deleted
      with the rest of the survey; the settled state is `docs/vocabulary.md`.
      Was: re-derive its Stages table. The `EDIT (5)` and `APPLY (7b)` rows are
      updated, but the table still carries "APPROVAL / 7a / 7b" as one row,
      which now spans two differently-named stages.
