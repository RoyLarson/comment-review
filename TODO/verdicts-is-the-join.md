# The module is `verdicts.py` and everything calls it the join

```
Status:   open
Progress: 6 of 8 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22: the term the agent keeps saying is the join but
          the module is verdicts -- two separate things or one misnomer)
Answered: 2026-08-22 -- the register question has an answer -- collating / master proof /
          editor -- and it splits the misnomer from a second unnamed step; two term
          collisions now need a ruling
Narrowed: 2026-08-23 -- stage 2 is GATHER, so collate is free for the marks -- the first
          collision is gone; editorial role vs editor is the one left
Triaged:  2026-08-23 -- six of the eleven boxes were measurements or rulings already made.
          They are ticked and stated in the Objective; two tasks remain, one of them a
          ruling owed
```

## Objective

**The module is `verdicts.py` and everything calls it the join.** One ruling settles whether the
file is renamed.

!! **IT IS ONE MISNOMER, MEASURED 2026-08-22 AND RE-VERIFIED 2026-08-23.** `verdicts.py` does not
hold the verdicts: `VERDICTS` is defined at `record.py:181` and IMPORTED by `verdicts.py`. So the
module is named for a table it does not own, while every other file calls it by what it DOES.

!! **THE TREE ALREADY AGREES ON THE OTHER NAME.** `grep -ro "the join" plugins/ --include=*.md
--include=*.py --include=*.toml | wc -l` returns **31** on 2026-08-23 -- 8 in `SKILL.md`, 7 in
`record.py`, 5 in `desk.py`, 3 in `held.py`, 2 in `reviewer-brief.md`, 2 in `re-review.md`, 1
each in `census.py` and `language.py`, and only **twice inside `verdicts.py` itself**, where it
describes what the file is. ! The count was **43** when this was raised on 2026-08-22, and
`docs/vocabulary.md:85` still says 43; the command above is what to re-run rather than either
number. The agent's own instructions call it the join; only the filename disagrees.

! **AND `desk.py` DRAWS THE LINE BY THAT NAME**, at `desk.py:18`: *"a question that needs two
findings -- who contradicts whom, which paragraphs nobody accounted for -- is the join's, and
lives in `verdicts.py`."* The sentence has to name the concept AND the file because they are
different words for one thing.

! **IT IS THE SECOND MODULE NAMED FOR SOMETHING IT IS NOT**, and the pair is worth deciding
together: `lexer.py` mostly reads a parse rather than lexing -- see
[`lexer-does-not-lex`](lexer-does-not-lex.md). Both are cases of a name that was true when the
file was created and stopped being true as the split settled.

## What the register answered, 2026-08-22

**THE TRADE SPLITS THE QUESTION IN THREE, and only the middle one is a rename.** **Collating** is
transferring every hand's marks onto one proof -- conflicts go down beside each other, nothing is
decided. The **master proof** is the copy they land on. The **editor** reads it and rules.

! So `verdicts.py` is a **COLLATOR**: it checks citations, reports contradictions, names coverage
gaps and hands every conflict up. It is not the editor.

! **AND THE ONE WHO RULES IS THE STEP THAT HAS NO MODULE.** Stage 5 APPLY, performed by the task
agent, is the only thing here that reads every mark and decides what stands. Naming the join
`editor` would name the collator after the job it explicitly does not do.

!! **RULED 2026-08-23: THAT STEP IS THE `copy chief`, AND IT GETS ITS OWN AGENT FILE.** Roy:
*"copy chief works. We will want to have a specific agent file for that separate from the task
agent."* `editor` collides with `editorial role` -- one of the four reviewers -- and the trade's
copy chief rules over the copy editors' marks, one level above the four hands. ! **The ruling
does not rename this module**: the collator still rules on nothing, so T2 goes to `collator.py`
and T8 tracks the agent file.

! **`COLLATE` IS NO LONGER TAKEN.** Stage 2 is **GATHER**, verified 2026-08-23 at `SKILL.md:16`,
`:28` and `:332`, so the first collision is gone and `collate` is free for the marks.

! **RECORDED IN `docs/vocabulary.md:76-88`** under *Bringing the marks together*, with what each
word would name and both collisions, and now the ruling that settled them.

## Tasks

- [x] T1 -- RULED 2026-08-23: THE ONE WHO RULES IS THE `copy chief`. Roy: *"copy chief works.
      We will want to have a specific agent file for that separate from the task agent."* In the
      trade the copy chief rules over the copy editors' marks, one level above the four hands,
      so it names the job without landing a syllable from `editorial role`. ! The collision it
      was raised against is real and is now avoided rather than accepted. Recorded in
      `docs/vocabulary.md` and `decision-log.md Vocabulary: #11`.

- [ ] T2 -- Rename the module for what it DOES, which the ruling leaves unchanged: it collates
      and rules on nothing. `collate` is free since stage 2 became GATHER, so `collator.py` is
      the name the register supplies -- NOT `copy chief`, which names the agent that rules on
      what this module hands up. The cost is mechanical: the imports in the modules that take
      it, the command lines in `SKILL.md` and `CLAUDE.md`, `tests/test_verdicts.py`, and
      `docs/`. ! Nothing about the CONTENT moves. Verify: `uv run pytest -q` green, `uv run ty
      check plugins/comment-review/skills/comment-review/scripts/` clean, and `grep -rn
      "verdicts.py" plugins/ docs/ CLAUDE.md` returns nothing.

- [x] T3 -- FINISHED 2026-08-22. The register was asked first, per `CLAUDE.md`'s rule that a new
      term comes from publishing before anywhere else. `join` is a database word; the trade's
      answer is in the Objective.

- [x] T4 -- SUPERSEDED. This box held the collating / master proof / editor finding. It is a
      MEASUREMENT of what the trade says, not a checkpoint; it is stated in the Objective and the
      record stays.

- [x] T5 -- SUPERSEDED. The `COLLATE`-is-stage-2 collision. Stage 2 is GATHER, so the two senses
      no longer operate on the same word and there is nothing to declare. Verified 2026-08-23 at
      `SKILL.md:16`.

- [x] T6 -- FINISHED. Recorded in `docs/vocabulary.md` under *Bringing the marks together*, with
      what each word would name and both collisions.

- [x] T7 -- SUPERSEDED. The `VERDICTS`-lives-in-`record.py` measurement, the 43-site count, the
      `desk.py:18` sentence and the `lexer.py` pairing each carried a box and none can be ticked
      by an observation of work. All four are in the Objective, with the command that re-derives
      the count.

- [ ] T8 -- GIVE THE COPY CHIEF ITS OWN AGENT FILE, separate from the task agent. Roy ruled the
      shape along with the word, 2026-08-23. !! **TODAY STAGE 5 APPLY IS THE TASK AGENT
      DECIDING**, which is why `docs/vocabulary.md` recorded this role as *"unnamed, and there is
      no module"* -- the job had no artifact, so nothing could be GIVEN to it, TOLD to it, or
      CHECKED of it. ! `agents` lane owns the file itself; this box tracks that it is owed.
      Verify: `plugins/comment-review/agents/` holds a copy-chief agent, `check_vocabulary.py`
      passes with `copy chief` defined and used, and `SKILL.md` names it at stage 5.
