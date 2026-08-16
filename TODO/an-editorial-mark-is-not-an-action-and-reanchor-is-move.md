# An editorial mark is not an action, and `reanchor` is `move`

```
Status:   in-progress
Progress: 11 of 13 tasks done
Owner:    session · Roy (⭐ 2 rulings left)
Raised:   2026-08-15 (Roy, while reviewing the placement precedence before merge)
```

## Objective

The verdicts are named for operations — `drop`, `patch`, `add`, `move`, `split` — and a
verdict is a **mark, not an action**. Roy: *"The editorial mark is not the
action. And because words aren't physical things that have to be picked up and moved it is in
some sense meaningless to make the final action resolution action be considered a move."* The
system already separates MARK from EDIT because a reviewer that fixes what it finds destroys
the finding; naming verdicts for operations works against that split. `reanchor` is the
clearest case and is ruled: it is `move` carrying the reason *this belongs to X*, and whether
X is another line, another module or another package is payload, not a second judgment.

The vocabulary as it stands: [`docs/vocabulary.md`](../docs/vocabulary.md).

## Tasks

- [x] ⭐ Name the collapsed verdict. **Roy ruled 2026-08-15: it is `move`.** With the
      reasoning that settled the rest — the record already carries `LOCATION` and `FINDING`,
      so `move` can say *this comment belongs to that line there* as its reason, and that
      IS reattachment. The second word was encoding in the verdict what the record has
      fields for.

- [x] Collapse `reanchor` into it. **Done 2026-08-15.** The word appears 26 times under `plugins/`, in five files.
      The distinction is *asserted* at: `SKILL.md:54-60` (the verdict table, plus "different
      AVAILABILITY" as the stated reason they are separate words), `SKILL.md:186` (the `line`
      level's verdict set), `:252`, `:596-602`, `references/reviewer-brief.md:110-111` and
      `:120-125`, `agents/comment-review-ownership-context.md:79-84` ("The word is `reanchor`,
      and it is NOT `move`"), and `agents/comment-review-function-context.md:115` and `:119` —
      where a body comment read out of order is `reanchor` naming a line *inside* the same
      function. That is the shortest relocation the system has, and whatever the collapsed
      verdict is called still has to carry it. Done when `reanchor` returns no hits under
      `plugins/`.

- [x] Key availability on the **destination**, not the verdict. **Done 2026-08-15** — only a
      destination OUTSIDE the code needs the tree resolved at 1.4, so only that case can be
      unavailable; a relocation into tracked code is never withheld. Stated once in
      `SKILL.md` (1.4 and the verdict table) and once in the brief.

- [x] Branch the synthesis order on the destination too. **Done 2026-08-15** — a `move`
      leaving the code is applied at step 2 with `drop`; a `move` staying inside it waits
      until step 6, because it removes nothing.

- [x] Update `scripts/verdicts.py` and its tests. **Done 2026-08-15** — `VERDICTS` is eight,
      the `line` set drops `reanchor`, the two payload rows are one, and
      `test_reanchor_needs_line` became `test_relocation_needs_line`, which now also asserts
      `reanchor` is carried at NO level. Verified: the gate rejects it, `move` is carried at
      `line` and not at `fact-check`.

- [x] Change "the nine verdicts" wherever it is counted. **Done 2026-08-15 — eight.**
      `SKILL.md` (heading and "these eight words"), `CLAUDE.md` twice, `README.md`, the
      brief's `VERDICT` row, all four agent files' shared line, `module-context`'s "outside
      the eight", `verdicts.py`'s rejection message, and both vocabulary docs. Checked: no
      other site states the count.

- [x] Confirm, then delete, the measured-loss note. **Done 2026-08-15 — confirmed removed,
      not merely undocumented.** The loss needed a relocation to be labelled with a verdict
      that availability could withhold. With availability keyed on the destination, an
      in-code relocation is never withheld, so the path that lost the finding no longer
      exists. Replaced by the destination rule that prevents it.

- [x] Resolve the precedence duplication. **Done 2026-08-15** — the brief now states only
      the reviewer's half (both findings stand, neither defers, report yours and say why in
      `FINDING`), and `SKILL.md` alone states which destination wins. The two agent files
      pointed at the brief "for which placement governs" and no longer do, since it no
      longer says.

- [ ] ⭐ Rule on the other operation-named verdicts. `drop`, `patch`, `add` and `split` name
      what to do rather than what is wrong, the same shape as `move`. Deciding they stay is a
      real answer — the collapse does not depend on it — but leaving it unasked means the next
      person re-derives this argument.

- [x] **Distribution is DESIGNED and moved to its own file, 2026-08-16.** Roy ruled the shape:
      *"the task agent runs a command and puts the correct vocabulary verbatim into the agents
      prompt. No summarizing no duplication."* Eight tasks, including the one that made this
      worth deferring — removing the in-place statements the emitted block replaces, where a
      definition is a clause inside a working sentence.
      → [`the-task-agent-emits-the-vocabulary`](the-task-agent-emits-the-vocabulary.md)

- [x] **Written 2026-08-16, once, where the agents read it.** In
      `references/vocabulary.toml`, emitted to the four editorial roles: *"What you emit on a
      sentence: the VERDICT together with its payload. The preferred action — what WOULD improve
      or correct the prose if it were applied. A mark is not the action; marking and applying are
      different stages and different actors."* ⚠ Found because the brief USED the term without
      defining it — Roy: *"is an edit-mark defined?"* — one occurrence in the whole shipped tree
      and none in the vocabulary. He chose to define rather than drop it: *"because we are an
      editorial board and want to stick with that as framing."*

- [ ] Relabel every site that calls an edit mark an **action**, and reserve that word for what
      stage 7b does. ⚠ `mark` was carrying four senses when this was raised; three are now gone.
      The census's are ANNOTATIONS (settled 2026-08-15), `detector` is deleted, and `sweep` is
      not a term — so `mark` means stage 4's name and what it emits. "Edit mark" now lands
      clear, and this task is only about defining it.

- [x] Add the CHANGELOG entry. **Done 2026-08-15** — under `[Unreleased]`, alongside the
      `angle` and `sweep` retirements, with the destination rules that make the collapse
      safe rather than lossy.
