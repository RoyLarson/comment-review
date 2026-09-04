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

MEASURED 2026-09-04, on `feat/the-turn`, after SP-4
(`docs/superpowers/plans/2026-09-04-sp4-the-turn.md`):

| | |
| --- | --- |
| disagreements collected at collate | **built** -- `Collated.escalations`, `Collated.rereads` |
| the chief's edit_copy | **built** -- `flows.collate._chief_copy`, DERIVED from the Determineds since `bc62ea5` |
| a role states the paragraph it wants | **built** -- `Mark.change`, raw text |
| the DiffMark | **built** -- `desk/diff_mark.py`, `5574f0a`; the four, closed |
| the batch send-out | **built** -- `desk.diff_mark.batch_of`, seeded by question (`#86`), `bc62ea5` |
| the ruling coming back, and the recollate | **built** -- `flows.turn.parse_answers`, paired to the sent slot (`2c04181`); `apply`; `run_turn` |
| the turn counter | **built** -- `Determined.turn`, and `MasterProof.turns`; a stet keeps its turn (`aefefdd`) |
| the chief's own final ruling | **built** -- `flows.turn.rule_at_cap` (`taken_in`, `recast`), `determined_chief` refusing an unruled place (`d1ddbd8`) |
| the record of how each place was ruled | **built** -- `desk/determined.py`, one `Determined` per resolved place on the master proof (`#87`) |
| the human's query riding with the set | **built** -- `Collated.unsettlable`, `MasterProof.unsettlable` (`99c7620`) |
| **a console command that runs a turn** | **NOT built.** The session's game harness drives `run_turn`; nothing in `commands/` does |
| **what SKILL.md tells the task agent about a turn** | **NOT built** -- `agents` lane |

! **THE LOOP RUNS, AND IT IS STILL A PROTOTYPE BY NAME.** It has been played twice as a
game -- five hands on `bc62ea5`, which produced `Process: #88`-`#91`, and once more on the
build above -- and every finding either landed here or is a task on
`TODO/a-revise-answer-has-no-artifact.md`. What keeps the PROTOTYPE banners on
`desk/determined.py`, `desk/diff_mark.py` and `flows/turn.py` is the two rows still NOT
built: nothing outside a scratchpad can run it.

---

## Where the rules in this file come from

| | |
| --- | --- |
| the loop, the batch, the chief's terminator | Roy, 2026-09-02, quoted in full above |
| the turn is structural, the cap is the agent's | `decision-log.md Process: #78` |
| the DiffMark is its own artifact, and its closed set | `Process: #22` |
| the composition re-read, and its passes | `Process: #49` |
| `change` is the wanted paragraph as raw text | Roy, 2026-08-28; `docs/the-mark.md` |
| an escalation answers with a DiffMark, a composition with a fresh Mark | `Process: #86` |
| the chief's ruling is a `Determined`, one per resolved place, on the master proof | `Process: #87` |
| agreement is the text alone, and it takes every owing mark | `Process: #88` |
| a lone owing mark goes back to every role that marked but a query | `Process: #89` |
| a human-review query rides and is asked last; the other shapes abstain | `Process: #90` |
| once stet, always stet, for the review; nothing persists across runs | `Process: #91` |
