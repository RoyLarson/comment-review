# The turn -- what a turn IS, and what closes the editorial roles

!! **THIS FILE IS THE SOURCE.** What a turn is, what goes out in one, what comes back, and
what ends the editorial part of a run are stated HERE. `flows/collate.py` and the desk
implement this file; `SKILL.md` tells the task agent to drive it. **Neither of them defines
it.**

!! **IT EXISTS BECAUSE THE MECHANISM LIVED ONLY IN ROY'S HEAD AND IN CHAT.** Roy, 2026-09-02,
after typing it out for the second time: *"This time give that story line a more permanent
home because it is a lot to remember and type back in."* ! Before this file, the turn was
reconstructed from a decision-log quote each time it came up -- and reconstructed WRONG twice:
once as a code-enforced cap (`a-revise-answer-has-no-artifact` T8, ticked, unticked, then
superseded), and once as dissolved entirely, by a session reading `Process: #78` to mean that
turns were not structural. **A decision log records WHEN something was ruled. It is not where
someone goes to learn how the thing works.**

---

## The loop, in Roy's own words

Roy, 2026-09-02, verbatim and unelided:

> *"Any disagreements between two agents are collected at the collate step that brings the
> final topology together.*
>
> *Then all of the disagreements are sent out as one batch with the diffs to the agents which
> they rule on with the DiffMark. That is then recollated into the copy-chiefs edit copy (if
> resolved) that is round one.*
>
> *Any remaining disagreements go back again. They get ruled on again, re-collated, and added
> to the non-disagreements go into the copy-chiefs edit copy again and that is round two. If
> the task agent is told 2 rounds that stops the edit, and the copy-chief or the task agent
> acting as copy chief applies its own ruling to the final piece and puts that in the
> copy-chiefs edit copy. That closes out the editorial roles of the system."*

## The loop, as steps

    COLLECT     the final topology's collate gathers every disagreement
    BATCH       ALL of them go out at once, each carrying its diff
    RULE        each role answers with a DiffMark
    RECOLLATE   what resolved joins the copy chief's edit_copy
                                                            <- that is TURN ONE
    REMAINDER   what did not resolve goes out again, is ruled, is recollated,
                and joins the non-disagreements in the chief's edit_copy
                                                            <- that is TURN TWO
    CAP         the number of turns is what the TASK AGENT was told
    CHIEF RULES on whatever is still unresolved when the cap is reached
    CLOSE       the editorial roles are done

!! **ONE BATCH, NOT ONE MESSAGE PER DISAGREEMENT.** *"all of the disagreements are sent out as
one batch"* -- so a turn is one send and one return per role, whatever the count of places.

!! **A TURN IS A STRUCTURAL UNIT AND THE CAP IS NOT.** The turn is one
BATCH-RULE-RECOLLATE cycle: countable, observable, the same shape every time. **How many are
allowed is an instruction to the task agent** -- `decision-log.md Process: #78`, and Roy on the
same day: *"If I come back and say it can be 1000 revises or 0 revises to the task agent then
that is what I expect the task agent to do not what the code enforces."*

! **SO A CODE-ENFORCED CAP IS WRONG AND A TURN COUNTER IS NOT.** The two were conflated in
both directions before this file existed. Counting turns, and saying which kind each was, is
`docs/plans/0.2.4-the-mark-and-the-collator.md` **P3**; enforcing a maximum was T8, and T8 is
superseded.

## The copy chief's own ruling is the terminator

**When the cap is reached, the chief rules.** Not "the run fails", not "it escalates to a
human", not "the place is dropped": *"the copy-chief or the task agent acting as copy chief
applies its own ruling to the final piece and puts that in the copy-chiefs edit copy."*

! **THE CHIEF MAY BE THE TASK AGENT WEARING THAT HAT.** The role is a seat, not a separate
dispatch -- which is already how `flows.collate._chief_copy` writes `role="copy-chief"`.

!! **THIS IS WHAT MAKES THE LOOP TERMINATE WITHOUT A CODE CAP.** `a-revise-answer-has-no-
artifact` T2 asked it as *"with no bound, send it back is a loop."* The bound is the
instruction; the TERMINATOR is the chief's ruling. A run cannot spin, because the last turn
always ends in somebody deciding.

## What a DiffMark is

**A DiffMark is not a `Mark` and not an eighth instruction.** `decision-log.md Process: #22`:
it is *"a DIFFERENT ARTIFACT answering a different question -- does your finding still stand
rather than what is wrong with this page -- so it carries its own closed set. The seven stay
seven."*

Its closed set is `hold`, `withdraw`, `correct`, `patch` -- Roy, 2026-08-27: *"I would prefer
the explicit hold/withdrawn/patch/correct marks"*, and the pair is present-tense
`hold`/`withdraw` (`Process: #22`).

!! **AN UNANSWERED PLACE IS NOT AN INFERRED `withdraw`.** The null answer must be written by a
hand. That is `#22`'s whole point, and it is why a turn can end with places still unresolved
rather than with silence counted as agreement.

## The two questions a turn row can ask

`decision-log.md Process: #49` split the turn into two, and they take different answer sets:

| the question | when it is asked |
| --- | --- |
| **composition** | two roles both EDITED the paragraph. Does the joined text still hold together? |
| **conflict** | two roles DISAGREE about the same place. Which stands? |

! **`clean` AND `query` ARE THE ONLY PASSES on a composition**, derived from `owes_change`
being False for exactly those two -- so the rule comes from the approved shape rather than
from a list somebody typed.

! **AN `add` GOES BACK TO EVERY ROLE OF THE STAGE**, because an `add`'s blast radius is the
PAGE and not the place: two `add`s at two addresses never meet under per-place grouping, so a
duplicated comment would pass every check.

## What this does to stages 4 and 5

Roy, 2026-09-02: *"I think it also collapses stages 4 and 5 a lot because the copy-chief is not
doing nearly as much in transcribing the words since the editorial roles are stating what they
would like the paragraph to read like."*

!! **AND THAT IS ALREADY HALF-TRUE IN THE SHAPE, NOT A CHANGE STILL TO MAKE.** `Mark.change`
carries *"the RESULT -- the updated paragraph, as RAW TEXT"*, ruled 2026-08-28: *"`change`
needs to be the updated paragraph as raw text not lines or sentences. This will make it easier
to diff per the rest of the stages."* **A role already states what it wants the paragraph to
read like**, so the chief is choosing between texts rather than composing one.

! **WHAT REMAINS OF STAGE 5 IS THE CHOOSING AND THE CHIEF'S OWN RULING**, not transcription.

## What is BUILT and what is NOT

MEASURED 2026-09-02, on `feat/the-mark-and-the-collator`:

| | |
| --- | --- |
| disagreements collected at collate | **built** -- `Collated.escalations`, `Collated.rereads` |
| the chief's edit_copy | **built** -- `flows.collate._chief_copy` |
| a role states the paragraph it wants | **built** -- `Mark.change`, raw text |
| **the DiffMark** | **NOT built.** `grep -rn "DiffMark" src/` returns nothing |
| **the batch send-out** | **NOT built.** Escalations are carried forward; nothing sends them |
| **the ruling coming back, and the recollate** | **NOT built** |
| **the turn counter** | **NOT built** -- `P3` |
| **the chief's own final ruling** | **NOT built** |

! **SO THE LOOP DESCRIBED HERE RUNS NOWHERE YET.** What exists is the collect and the fold at
either end of it. This file is the specification, not a description of behaviour -- and it says
so rather than letting a reader assume the machinery matches the prose.

---

## Where the rules in this file come from

| | |
| --- | --- |
| the loop, the batch, the chief's terminator | Roy, 2026-09-02, quoted in full above |
| the turn is structural, the cap is the agent's | `decision-log.md Process: #78` |
| the DiffMark is its own artifact, and its closed set | `Process: #22` |
| the composition re-read, and its passes | `Process: #49` |
| `change` is the wanted paragraph as raw text | Roy, 2026-08-28; `docs/the-mark.md` |
