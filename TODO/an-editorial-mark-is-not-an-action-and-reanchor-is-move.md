# An editorial mark is not an action, and `reanchor` is `move`

```
Status:   in-progress
Progress: 9 of 13 tasks done
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

The vocabulary as it stands: [`docs/vocabulary-usage.md`](../docs/vocabulary-usage.md).

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

- [ ] ⭐ Give the agents a copy of the definitions. Roy asked for this once the vocabulary is
      settled. Decide where: `references/reviewer-brief.md` is the shared contract all four
      already read and already carries the verdict table, so the definitions can land there,
      or in a reference it points at. Whichever, it is one file — the four agent files point,
      they do not restate.

- [ ] Write the definition of an edit mark, once, where the agents read it. Roy's words:
      *"edit marks are the preferred action from the editorial roles that if applied would
      improve or correct the comments and docstrings."* The conditional is the whole point —
      the mark names what would be done, and nothing is done until 7b.

- [ ] Relabel every site that calls an edit mark an **action**, and reserve that word for what
      stage 7b does. ⚠ `mark` is already carrying four senses per the survey — the census's
      mechanical annotations (`names-a-symbol`, `counted`), stage 4's name, a detector, and a
      block selected for the sweep — so check whether "edit mark" lands clear of them or
      whether one of those needs a different word instead.

- [x] Add the CHANGELOG entry. **Done 2026-08-15** — under `[Unreleased]`, alongside the
      `angle` and `sweep` retirements, with the destination rules that make the collapse
      safe rather than lossy.
