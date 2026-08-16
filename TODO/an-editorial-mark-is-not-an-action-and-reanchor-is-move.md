# An editorial mark is not an action, and `reanchor` is `move`

```
Status:   open
Progress: 0 of 13 tasks done
Owner:    session · Roy (⭐ 3 rulings)
Raised:   2026-08-15 (Roy, while reviewing the placement precedence before merge)
```

## Objective

The nine verdicts are named for operations — `drop`, `patch`, `add`, `move`, `reanchor`,
`split` — and a verdict is a **mark, not an action**. Roy: *"The editorial mark is not the
action. And because words aren't physical things that have to be picked up and moved it is in
some sense meaningless to make the final action resolution action be considered a move."* The
system already separates MARK from EDIT because a reviewer that fixes what it finds destroys
the finding; naming verdicts for operations works against that split. `reanchor` is the
clearest case and is ruled: it is `move` carrying the reason *this belongs to X*, and whether
X is another line, another module or another package is payload, not a second judgment.

The vocabulary as it stands: [`docs/vocabulary-usage.md`](../docs/vocabulary-usage.md).

## Tasks

- [ ] ⭐ Name the collapsed verdict before touching anything else. `move` is the surviving
      word by default, but it carries the action framing that caused the confusion, and it is
      already used in plain English for "the step to take" at `docs/parsing.md:67`. A name
      that states the finding rather than the operation would settle every downstream task.

- [ ] Collapse `reanchor` into it. The word appears 26 times under `plugins/`, in five files.
      The distinction is *asserted* at: `SKILL.md:54-60` (the verdict table, plus "different
      AVAILABILITY" as the stated reason they are separate words), `SKILL.md:186` (the `line`
      level's verdict set), `:252`, `:596-602`, `references/reviewer-brief.md:110-111` and
      `:120-125`, `agents/comment-review-ownership-context.md:79-84` ("The word is `reanchor`,
      and it is NOT `move`"), and `agents/comment-review-function-context.md:115` and `:119` —
      where a body comment read out of order is `reanchor` naming a line *inside* the same
      function. That is the shortest relocation the system has, and whatever the collapsed
      verdict is called still has to carry it. Done when `reanchor` returns no hits under
      `plugins/`.

- [ ] Key availability on the **destination**, not the verdict. `SKILL.md:252` rules `move`
      UNAVAILABLE for a whole run when the destination tree is absent; a relocation into
      tracked code needs no such tree. Done when the rule reads off where the prose is going.

- [ ] Branch the synthesis order on the destination too. `SKILL.md:596` applies `move` at
      step 2 ("take out what is leaving") and `:602` applies `reanchor` at step 6 because "it
      removes nothing" — one verdict now spans both, and which step it takes depends on
      whether the destination is this file.

- [ ] Update `scripts/verdicts.py`: the `VERDICTS` tuple, the `LEVELS` sets at `:66-71`, and
      the two payload rows at `:308-311` become one. Both verdicts already arrive at the
      `line` rung, so no level moves. Update `tests/test_verdicts.py` with it.

- [ ] Change "the nine verdicts" wherever it is counted — `SKILL.md:41`, `CLAUDE.md:101`,
      `README.md:110`, `references/reviewer-brief.md:95` — and check nothing else states the
      count in prose.

- [ ] Confirm, then delete, `references/reviewer-brief.md:120-125`'s measured-loss note. It
      records an in-file relocation labelled `move` being converted to `clean` and lost. That
      failure exists *because* `move` can be ruled unavailable while `reanchor` cannot, so the
      collapse should remove the failure mode rather than the warning about it — verify that
      before cutting the note.

- [ ] Resolve the precedence duplication this closes. `references/reviewer-brief.md:288` and
      `SKILL.md:617-619` both state that `ownership-context`'s destination governs, in
      different words, because neither audience can read the other's file
      (`SKILL.md:33-39`). With one relocation verdict the rule is simpler; state the reviewer's
      half (report, do not defer) and the task agent's half (which destination wins) so that
      neither is a restatement of the other.

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

- [ ] Add the CHANGELOG entry. This is a second breaking change to the shipped vocabulary in
      one release cycle: a verdict disappears, and any report emitting it becomes invalid at
      the stage-5 gate.
