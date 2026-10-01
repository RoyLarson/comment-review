# The turn -- what a turn IS, and what closes the editorial roles

**This file is the source.** What a turn is, what goes out in one, what comes back, and what
ends the editorial part of a run are stated here. `desk/evaluate/`, `desk/work/` and
`flows/bus.py` implement this file; `SKILL.md` tells the task agent to drive it. **Neither of
them defines it.**

**It exists because the mechanism lived only in Roy's head and in chat.** Roy, 2026-09-02,
after typing it out for the second time: *"This time give that story line a more permanent
home because it is a lot to remember and type back in."* Before this file, the turn was
reconstructed from a decision-log quote each time it came up -- and reconstructed wrongly
twice: once as a code-enforced limit (`a-revise-answer-has-no-artifact` T8, ticked, unticked,
then superseded), and once as dissolved entirely, by a session reading `Process: #78` to mean
that turns were not structural. **A decision log records when something was ruled. It is not
where someone goes to learn how the thing works.**

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

**Two of that quotation's names are 2026-09-02's and have been replaced.** What it calls a
`DiffMark` is an `Answer` (`desk/answers/answer.py`); *recollated* is the fold run again over
the same places, which is what `flows.bus` does with each turn's answers written onto them.
The loop is unchanged. What the old names belonged to is in [`history.md`](history.md),
*Reconciliation*.

## The loop, as steps

    COLLECT     `collate` folds one stage's returned copies into places; each place
                no one text settles is carried forward
    BATCH       one file, one slot per carried-forward place per role asked
    ANSWER      each role answers every slot it was sent, in its own file
    FOLD        `turn` writes those answers onto the places and folds again
                                                            <- that is turn one
    REMAINDER   what is still carried forward goes out in the next batch, is
                answered, and is folded again
                                                            <- that is turn two
    CAP         the number of turns is what the task agent was told
    CHIEF       `disposition` takes the chief's ruling at every place still
                carried forward
    CLOSE       the editorial roles are done

**One batch, not one message per disagreement.** *"all of the disagreements are sent out as
one batch"* -- so a turn is one send and one return per role, whatever the count of places.
`flows.bus._batch_of` builds one dict of role -> slots and `flows.proof_io.save_batch` writes
it as one file.

**A turn is a structural unit and the cap is not.** The turn is one batch-answer-fold cycle:
countable, observable, the same shape every time. **How many are allowed is an instruction to
the task agent** -- `decision-log.md Process: #78`, and Roy on the same day: *"If I come back
and say it can be 1000 revises or 0 revises to the task agent then that is what I expect the
task agent to do not what the code enforces."*

**So a code-enforced cap is wrong and a turn counter is not.** The two were conflated in both
directions before this file existed. The counter is derived rather than stored:
`flows.bus.turn_of` returns the highest turn any of a proof's places records an answer at, and
the next turn is that plus one. Nothing counts turns of its own, and no module holds a maximum.

## The copy chief's own ruling is the terminator

**When max turns is reached, the chief rules.** Not "the run fails", not "it escalates to a
human", not "the place is dropped": *"the copy-chief or the task agent acting as copy chief
applies its own ruling to the final piece and puts that in the copy-chiefs edit copy."*

**The chief may be the task agent wearing that hat.** The role is a seat, not a separate
dispatch -- which is how `flows.places.chief_copy_of` is called, with
`desk.proof.disposition.CHIEF`, the string `copy-chief`.

**This is what makes the loop terminate without a code cap.**
`a-revise-answer-has-no-artifact` T2 asked it as *"with no bound, send it back is a loop."*
The bound is the instruction; the terminator is the chief's ruling. A run cannot spin, because
the last turn always ends in somebody deciding -- and `flows.bus._on_dispositions` refuses a
carried-forward place the chief left unruled, so the close cannot happen with one outstanding.

---

## The place, and the seven states

**A place is the aggregate the middle decides** -- `desk/proof/place.py`. It carries its
address and anchor, its base text as the page holds it (read by the collate handler, below), the
roles whose copies held that page
(`readers`), every mark filed on it with the role that filed it and which end of a move it is
(`filed`) -- on the proof, a pointer to the mark where its edit_copy holds it, `{copy, sheet,
mark, touch}`, so each mark is stored once -- each turn's answers by role, the chief's disposition where there is one, and what
the passes decide: `state`, `text`, `sides`, `reasons`, `notes`, `asking`, `owed` and
`question`. A move is an aggregate of its own, over its two places --
`desk/proof/move.py`, and the passes that decide it `desk/evaluate/move.py`, below.

**The seven states are `desk/proof/state.py`'s own closed set.**

| state | when a place is in it | what becomes of it |
| --- | --- | --- |
| `stands` | no role proposed a text here, or exactly one did and no other role that read the place is owed a say | settled, on that text or on the base |
| `agreed` | two or more roles' proposals come to one text and every role owed a say has accepted it | settled on that text |
| `composed` | proposals on different sentences compose, or one text is not yet accepted by every role owed a say | carried forward, asking a `composition` |
| `contested` | proposals that will not compose against the base | carried forward, asking an `escalation` |
| `unsettlable` | a `query` of shape `human-review-necessary` is filed here, or an answer of that shape is given | rides to the author; no later pass changes it |
| `refused` | a mark or an answer its table will not read | back to the role, and the fold rolls back |
| `to-come` | an end of a move whose placement is undecided | waits on the placement; holds no text, is put to no role, takes no ruling |

**Carried forward is `composed` and `contested`, and the set has a name.**
`desk.proof.state.CARRIED` is those two, and every reader of "is this still open" asks it:
the bus builds the batch from it, refuses an answer at a place outside it, and the
dispositions table's `closes` is that same set.

## The three tables

**Three actors write with three vocabularies, so there are three tables and one shape of row.**
Nothing outside the three names an instruction, an answer or a disposition, which
`tests/gates/test_tables_name_the_rows.py` holds over the tree.

| table | rows | what a row answers |
| --- | --- | --- |
| `desk/marks/table.py` | the seven instructions | the `claim` keys and which one quotes the paragraph; which places it `touches`; what it `sets` at a touch; what it `reads` as a problem; what it `notes` for the chief; how it `pairs` with the others; which `answers` a turn may give on it |
| `desk/answers/table.py` | twelve, keyed by `(question, name)` | which question it answers, its `effect` on the role's own side or on the move, whether it owes a `change`, and the `claim` keys it owes |
| `desk/dispositions/table.py` | `taken_in` and `recast` | which states it `closes`, what it `owes`, and the text it `sets` |

**The `Row` shape is declared once**, in `desk/marks/table.py`, and the other two tables have
their own row types built to the same idea: a frozen dataclass whose cells are values and
functions, never prose.

**`stet` is not a disposition row today.** `DISPOSITIONS` holds two names, and
`desk.proof.disposition.read_disposition` refuses any other by name. The word is still what the console prints
for a place the fold settled on its own -- see *What each command prints*, below -- and a
`stet` the chief emits waits on `TODO/no-mark-for-let-it-stand.md`.

## The passes, and the one order they run in

`desk.evaluate.passes.decide(places, moves, turn)` is the whole sequence and the only entry:

    for each move      placement_pass, with the chief's placement ruling where
                       there is one; then settle_ends, which takes a withdrawn
                       move off both ends and an agreed move's untaken movers off
    for each place     marks_pass, then answers_pass once per turn up to `turn`
    for each move      hold_ends: an undecided move's ends are `to-come`,
                       except an end refused on its own; a held one's are
                       unsettlable
    for each place     dispositions_pass

**A move's placement is decided before either end's words** -- `decision-log.md Process: #195`
and `#200`. So the placement pass and its settling run first, and the ends are then read as
ordinary places -- an agreed move's against the move still filed there (`#205`); `hold_ends` runs after them and before the chief's pass, so a `to-come` end is
what the chief's pass sees, and a ruling there is refused rather than closing words the move's
outcome may change.

**And `decide` takes the places and the moves together.** `desk.work.fold.Fold` finds the moves
on its own places (`moves_in`), so a caller cannot fold a move's two ends as unrelated places.
The passes stay public and `tests/test_passes.py` drives them one at a time.

## A text settles only when every role that read the place has had its say

**This is the invariant, and it is one rule rather than a rule per instruction** --
`decision-log.md Process: #180`. `desk.evaluate.passes.owed_a_say` names the roles that have
not accepted the text; a place with any is carried forward as a `composition` to exactly those
roles, at the first fold and after a turn alike. A role is not owed a say when one of three
things is true of it:

| | |
| --- | --- |
| it filed only a `query` | either deferring shape hands the place on and waits on nothing (`Process: #121`) |
| its side is this text | it proposed the text, or its answer replaced or accepted its way to it |
| it answered and holds no side | it was asked, and withdrew or abstained; it has had its say |

**A lone proposal at a place no other role read stands**, because no reader is owed anything
there. **A lone proposal against three `clean`s does not**: those three read the place and have
not seen this text, so it goes back to them.

**`#89` and `#116` are this rule's cases and are no longer rules of their own.** *A lone owing
mark goes back to every role that marked but a query* and *an `add` goes back to every role of
the stage* both fall out of the invariant, so the marks table's `rereads` cell -- true on `add`
alone -- was removed with `#180` and no row is asked. The two entries stand in the log as the
rulings that produced the invariant; as separate mechanisms they are superseded.

**Who a place is put to is recorded, not re-derived.** The pass writes `place.owed`;
`desk.work.fold.asked` reads it back; `flows.bus._batch_of` builds a slot per role in it, and
`flows.bus._on_answers` refuses an answer from a role that is not.

## One role's own marks at one place compose

`decision-log.md Process: #179`. A role may file a second ruling at an address, and its marks
there make one side: `desk.evaluate.passes.composed_side` sets the side from the one mark where
there is one, and composes the rest against the base. Marks on different sentences become one
text; marks on the same sentence do not compose and are refused back to that role naming both,
with *"withdraw one"*. A mark that proposes no text stands beside them: a `query` sends the
place to the human from one role as it does from any.

## The three questions a turn asks

`desk.proof.answer.Question` is a closed set of three, and a slot carries which one it is.
`decision-log.md Process: #49` split the turn in two and called the second *conflict*; the
code's name is `escalation`. The third, `placement`, is asked of a move (`Process: #195`).

| the question | when it is asked | the answers |
| --- | --- | --- |
| `composition` | this text is what the fold came to, and you have not accepted it | `clean`, `query`, `correct`, `patch` |
| `escalation` | two or more proposals here will not compose | `hold`, `withdraw`, `correct`, `patch` |
| `placement` | a move's placement is undecided and you are owed a say on it | `agree`, `stet`, `withdraw` (its mover), `query` |

**What each answer does to the role's own side** is the row's `effect`
(`desk.answers.table.SideEffect`):

    hold        keeps      the side stands as it was
    withdraw    removes    the side is taken off the place
    correct     replaces   the side becomes the answer's `change`
    patch       replaces   the same
    clean       accepts    the side becomes the text that was put to it
    query       defers     removes the role's side; human-review-necessary
                           asks the author before the production fold

**A move is answered on the move, once, for the pair** -- `decision-log.md Process: #195`.
The placement slot names both addresses and every mover's snippet and arrival, and its answer is
recorded on the move rather than at either end. `agree` accepts the placement, `stet` contests
it for the chief, a mover's `withdraw` takes the move off both ends, and a `query` of shape
`human-review-necessary` asks the author before the production fold. The placement rows use
`desk.answers.table.PlacementEffect`; either other query shape relinquishes the role's prior
placement vote. No answer at an end reaches the move:
while the placement is undecided the ends are `to-come` and are put to nobody (`#200`), so there
is no end answer to reach it. Once the move is agreed, a `correct` or a `patch` at an end is an
answer on that place alone, like any other.

**Only `clean` and `query` owe no `change`**, and that is read off the row's `owes_change`
rather than from a list anybody typed. `check --contract` prints the three questions, the answers
each admits, which owe a change and the `claim` keys each owes, all generated from this table by
`flows.answers.contracts`.

**An unanswered slot is not an inferred `withdraw`.** The null answer must be written by a
hand -- `decision-log.md Process: #22` -- so `flows.answers.answers_of` refuses every sent slot
that came back without an `instruction`, by name, and the round rolls back. A turn can end with
places still open rather than with silence counted as agreement.

**An answer's evidence is verified before the fold, as a mark's is** -- `Process: #181`.
`answers_of` runs `desk.collator.cited_problems` over each answer's `sources` against the tree
the copies were read from; a cite that does not resolve refuses the answer, and
`check --answers` reports the same thing before the send. Opening a cited file is not a page
read.

## What the chief rules, and what it closes

**Two rulings, and each closes only a carried-forward place.**

| ruling | what it carries | the text it sets |
| --- | --- | --- |
| `taken_in` | `side` -- a role, or `original` | that role's side, or none, which leaves the paragraph as it was |
| `recast` | `prose` | the chief's own paragraph |

`dispositions_pass` refuses a ruling at a place outside the row's `closes`, and one naming a
side that proposed nothing here. `flows.bus._on_dispositions` refuses a ruling at a place
nothing carries forward, and refuses a carried-forward place left unruled, naming the roles it
was put to. Any refusal rolls the round back and nothing is written.

**The chief rules an undecided move's placement once, then its ends** --
`decision-log.md Process: #195` item 4, `#200` and `#201`. While a move's placement is open or
contested, both of its ends are `to-come`: each holds no text, is put to no role and takes no
ruling (`desk.evaluate.move.hold_ends`). A reader answers the placement on a question of its
own, `agree`, `stet`, `withdraw` or `query`, in one slot for the pair that names every mover.

| ruling | what it carries | what it does to the move |
| --- | --- | --- |
| `taken_in` | `to`, the destination, and `side` -- a mover | agrees the move as that mover filed it; any other mover's filing comes off |
| `taken_in` | `to`, and `side` -- `original` | withdraws the move; the paragraph stays where it is |

The ruling is addressed by the move's origin and carries `to`; `desk.evaluate.move._ruled`
applies it in the placement pass. `flows.bus._on_dispositions` refuses an undecided move left
unruled, naming it by its two addresses, and a ruling at a `to-come` end. Once the placement is
decided the move stays filed at both ends, and each end is an ordinary place decided against it
(`#205`): one that needs words is carried forward in what `disposition` writes, and the chief
rules it by running `disposition` again on that proof. The chief rules the words at each end
alone.

**A move held for the human is held at both ends and reported from the move** --
`decision-log.md Process: #155` and `#182`. `hold_ends` makes both ends `unsettlable` with no
text, so nothing is written to a page while the question is open, and `desk.work.fold.Fold.run`
reports the held move from the move, naming both ends. **A refused move is reported once, from
the move**: its own reasons at its two addresses, and an end's own reasons at that end.

## What the write end reads

**The closed proof, and the places it decided** -- `decision-log.md Process: #184`.
`proof --proof <the closed proof>` transcribes one alteration per place whose decided text
differs from the paragraph already there, in each page's own place order, with an emptied place
written as the delete; `flows.transcribe.docket_of_proof` is that step. It refuses, naming each
place: one still carried forward or refused -- such a text has not settled (`Process: #180`), so
a proof holding one is not closed -- one that will not read back, and a page a decided place
sits on that the checkout cannot open.

**A partial approval is a place filter on that same command** -- `Process: #192`. The author
approves some decided places and not others, so `proof --proof <the closed proof> --only
<address>`, repeatable, transcribes those places alone and leaves every other place as the page
has it. It refuses an address the proof does not carry, and one end of a move whose other end is
not approved, naming the end left out: a move is one decision at two places, and setting the
origin alone drops the paragraph and adds it nowhere, while setting the destination alone writes
it in both. A named place the write end sets nothing at -- it stands on the text already there,
or it is held for the human -- is approved with nothing to set rather than refused, and the
command prints `approved <address>: nothing to set`. `--only` without `--proof` is an argument
error: a copy holds marks and a docket holds alterations already chosen, so neither has places
to filter.

**The chief's copy is the record of what was decided, and nothing reads it back.** `collate`
and `disposition` write it with `--out`; no command loads one. It restates each decision as a
mark -- the side taken in, or one synthesized where no side set the decided text -- and folding
those marks a second time made the docket depend on that restatement reproducing the fold.
Measured 2026-09-18: two roles patching one paragraph settle on a composition no filed mark
sets, `patch` owes no sources, and the synthesized `correct` carried none -- so `proof --copy`
over the chief's copy answered *"copy-chief m.py@b1: needs at least one source"* and the
decided text reached no docket.

**`proof --copy` stays, for a role's own draft.** A role's copy holds that role's marks and
nobody else's, and drafting it is how one stage's output becomes the revise the next stage
reads (`Process: #76`).

## The Unit of Work, and the events

**One fold over one stage's places, in `desk/work/fold.py`.** `Fold(places, turn).run()` hands
them to `decide`, walks them in address order, and either commits -- every place decided, none
refused -- or rolls back, in which case `Fold.decided` is empty and the flow saves nothing. It
opens no file and knows no container of the read or write end.

**The events are the report, and the commands print from nothing else** --
`desk/work/events.py`:

| event | what it says |
| --- | --- |
| `Refused` | one role's reasons at one place; the round is rolling back |
| `CarriedForward` | the address, its state, its question and the roles it is put to |
| `Unsettlable` | the address, who asks the human and why, the partner where a move is held at both ends, and the move itself as a `HeldMove` |
| `Advised` | what one role is told about one place without being refused for it |
| `Settled` | one place the fold decided, and the text if any |
| `Committed` | the count of places decided |
| `RolledBack` | the count of reasons, and nothing saved |

**An advisory note decides nothing** -- `decision-log.md Process: #177`. The `correct` row's
`notes` cell reports a change that drops words the claim never named; the fold emits an
`Advised` and commits over it.

## The bus -- three messages, one handler each

`flows/bus.py` is in-process and synchronous: a dict of message type to handler, not
infrastructure. A handler checks what its message carries, derives the places, opens a `Fold`,
and on commit builds what the stage saves.

| message | what it reads | what a commit leaves |
| --- | --- | --- |
| `CopiesReturned` | one stage's parsed copies, the binder, the checkout, the topology where there is one | the master proof at turn 0, the chief's copy, the first batch |
| `AnswersReturned` | the last proof and each role's answers, and the checkout a cite resolves against | the next proof and the next batch |
| `DispositionsWritten` | the last proof and the chief's rulings | the closed proof and the chief's copy |

**A turn builds a chief's copy and saves none.** `flows.bus._on_answers` returns one on its
`Result`, the way the other two handlers do, and `commands/turn.py` has no `--out` to write it
with. `collate` and `disposition` are the two commands that save one.

**Everything a copy can be wrong about on its own is found before the fold opens.** A quote
that is not in its paragraph, a cite that resolves against nothing, an address no page carries,
a place a role left unruled, a role short of its shard, and a copy gathered from a tree the
others were not (`Process: #178`) each become one `Refused`, and the fold never runs. None of
them is a question about how the roles' rulings meet. A short shard and an unruled place roll
the whole round back like the rest: the role is named, nothing is written, and `collate` runs
again over the repaired copies (`Process: #186`). `flows.verify.copy_problems` is the list one
copy is held to against the pages, and `check --binder` runs the same call before the send.

**What each handler reads.**

| handler | what it opens | why |
| --- | --- | --- |
| `CopiesReturned` (`collate`) | the pages its copies' marks touch, and the files a mark cites | to check each address and quote against the page (`Process: #119`, `#122`), to take each place's base text and anchor from it (`#187`, `#125`), and to verify each citation |
| `AnswersReturned` (`turn`) | the files an answer cites | to verify the citation (`#181`); its places come off the proof |
| `DispositionsWritten` (`disposition`) | nothing | its places come off the proof |

**The collate handler reads the base off the page, not the binder** -- `Process: #187`, which
restores `#125`. The binder is the seed for what a role is handed, not every place a mark may
touch: a move may land in a file the run did not gather. Measured against the binder, such a
place had the base `""`, so a destination text that dropped a word of the paragraph already there
passed `mark`, `check`, `collate` and the turns, and `proof` drafted it. `flows.on_the_page` is the one
reader of what a page holds at an address; `check`, `collate` and `proof` read through it, and
`mark` does for every place but the slot it seeds, so the four measure a mark against the same
text. A place's anchor is read the same
way, except at a mark's own address, where it is the anchor the role returned, since the write
end checks that one against the page's (`#134`).

**Nothing asks whether a page changed** -- `Process: #62`, `#185`. Reading the page for a base
is not a drift check: nothing compares what a role was seeded with against what came back, and
nothing compares the page against the binder. Once the places are built, the fold decides from
them alone.

## What each command prints, and what it exits

**Five exit codes, and all three commands share them**, so a caller branching on a code branches
once. `commands/collate.py` declares them and `turn` and `disposition` import them.

| code | name | what it means |
| --- | --- | --- |
| 0 | `OK` | the fold committed and carried nothing forward |
| 1 | `BROKEN` | a rollback: something was refused, every reason is on stdout, nothing was written |
| 2 | `UNREADABLE` | a file or an argument is not what it says; nothing was read past it |
| 3 | `REREADS` | places carried forward, all of them compositions |
| 4 | `ESCALATIONS` | at least one place carried forward as an escalation |

**There were three more until the fold became a Unit of Work**: `DRIFT` 5, `COVERAGE` 6 and
`CARRIED_AND_UNRULED` 7. Each named a finding that routed back to a role without voiding the
round, and there is no such finding left. Drift is not measured at all (`decision-log.md
Process: #185`). A short shard, a place a role left unruled and a slot a role left unanswered
are found before the fold opens, so each is a `Refused` and the round rolls back (`#186`).

**The events print first, in address order; what was written prints after.** These lines are
from `pwsh -NoProfile -File scripts/smoke_middle.ps1`, 2026-09-18, which exits 0 and whose
`collate` and both of whose turns are each expected to exit 4:

    composed fib.py@a0: function-context, module-context, ownership-context (composition)
    contested fib.py@a3: block-context, function-context, module-context (escalation)
    stet fib.py@b0
    unsettlable fib.py@a1: block-context asks the human -- the docstring and the decorator disagree about what counts
    unsettlable store.py@b5 and store.py@b12: block-context asks the human -- whether this note belongs beside the code or at the foot is the author's call
      and module-context's move drops the paragraph at store.py@b5 and adds it at store.py@b12, one move -- rounding is the last thing the module does and reads as its closing note
    for the chief -- each correct below drops words its claim never named:
    block-context store.py@c5: its change drops 'wants', which its claim never names

| the line | the event |
| --- | --- |
| `<state> <address>: <roles> (<question>)` | `CarriedForward` |
| `stet <address>` | `Settled` |
| `unsettlable <address>: <role> asks the human -- <reason>` | `Unsettlable`, with the partner's address joined by `and` where a move is held at both ends, and an indented `and ...` line for the move |
| `<role> <address>: <reason>`, the address `(the copy)` where there is none | `Refused` |
| the `for the chief` heading, then `<role> <address>: <note>` | `Advised`, printed last, and only over a commit: `Fold.run` reports a rollback's refusals and nothing else. A note itself still rolls nothing back (`Process: #177`) |

**Then the files, one line each, and only on a commit:**

    <out>: 17 places resolved                                       collate
    <proof-out>: the master proof -- 28 places -- 10 settled, 3 unsettlable, 15 carried forward
    <batch-out>: turn 1's batch -- block-context 12, function-context 10, module-context 8, ownership-context 8

    <proof-out>: the master proof after turn 1 -- 28 places -- 15 settled, 4 unsettlable, 9 carried forward   turn
    <batch-out>: turn 2's batch -- block-context 6, function-context 5, module-context 5, ownership-context 5

    <proof-out>: the master proof after turn 2 -- 28 places -- 17 settled, 4 unsettlable, 7 carried forward   turn
    <batch-out>: turn 3's batch -- block-context 6, function-context 6, module-context 4, ownership-context 5

    <out>: the chief's copy, 18 places                              disposition
    <proof-out>: the proof closed at turn 2 -- 28 places -- 24 settled, 4 unsettlable, 0 carried forward

**Nothing carried forward is no batch rather than an empty one.** A file holding `{}` would be
handed to roles as a turn with nothing in it, so `--batch-out` writes only where the fold
carried something forward, and a turn that carries nothing is the last one there is to run.

## What a stage deals, and what its roles may file

**Three keys on a topology stage row, and each is optional** -- `decision-log.md Process: #193`.
Absent on every ordinary stage, which is what makes one deal every place a role is handed and
admit every instruction, as every stage did before that ruling.

| key | what it says | read by |
| --- | --- | --- |
| `cap` | the length, in lines, a place's text must run over to be dealt | `desk.stages.deals` |
| `series` | which series this stage deals, by letter | `desk.stages.deals` |
| `admits` | which instructions its roles may file, by name | `desk.stages.not_admitted` |

`desk/topology.py` checks each against the set that defines it -- a letter against
`reading.series`, an instruction name against the marks table -- so a row naming something
outside either is refused by the value it typed.

**A place is dealt where its series is one the stage names and its own lines run over the cap.**
The count is the page's own `lines`, which `binder.page` fills from the paragraph's raw text
when a binder is read back and the lexer fills when a page is built; a place holding no prose
counts none, so it is never over a cap.

**The deal is narrowed in two places and stated in one.** `flows.distribute.seed` gives a slot
to the places the stage deals, and `flows.verify.coverage_problems` measures a returned copy
against the same `deals` -- Roy, 2026-09-19: *"only touching places that are over the length
limit - all other places are automatically clean for this role."* A page a stage deals nothing
on keeps its sheet and no slot, and `distribute` prints `0 places for <role> to rule on`.
A stage that deals part of the binder and is collated without `--topology` is reported short of
its coverage, and correctly: nothing else in the run says what was dealt.

**What a role may file rides on the copy.** The seed stamps the stage's name and its admitted
instructions onto the `edit_copy`, as `read_from` carries the tree it was cut from, so
`flows.fill` refuses a ruling as `mark` places it -- `stage 6 admits patch, drop, add, clean,
and not correct` -- and `commands/check.py` holds a hand-written copy to the same rule without
the run's topology beside it.

**Compaction is the stage these were built for, and it runs before the author is shown
anything.** Roy, 2026-09-19: the editorial stages' proof is pulled into a scratch revise, the
compacting stage reads that revise, and the revise its own proof pulls is the galley the author
approves. It is dealt the `b` and `c` places whose text runs over the cap, files the edit
instructions with `mark`, and its copy is folded and set like any stage's. A docstring is never
dealt, so nothing has to refuse one; length is no concern of the four editorial roles, whose
remit is that a comment is correct, true and current at whatever length that takes.

**The three keys are independent of `reads`.** Which tree a stage is seeded from and which of
that tree's places it is dealt are two questions: a stage reading `"original"` may narrow what
it deals, and a stage reading a revise may narrow nothing. `#193` is the use they were built
for, not the only row they fit.

## What this does to stages 4 and 5

Roy, 2026-09-02: *"I think it also collapses stages 4 and 5 a lot because the copy-chief is not
doing nearly as much in transcribing the words since the editorial roles are stating what they
would like the paragraph to read like."*

**And that is in the shape rather than a change still to make.** A mark's `change` is the
updated paragraph as raw text, ruled 2026-08-28: *"`change` needs to be the updated paragraph
as raw text not lines or sentences. This will make it easier to diff per the rest of the
stages."* **A role already states what it wants the paragraph to read like**, so the chief is
choosing between texts rather than composing one -- and `place.sides` is that choice laid out,
role by role, on the batch slot and on the proof.

**What remains of stage 5 is the choosing and the chief's own ruling**, not transcription.

---

## Where each piece lives

Measured 2026-09-18, on `feat/the-middle-rebuilt`, after the middle was rebuilt and the old
fold deleted (`0e2ff82a`).

| | |
| --- | --- |
| disagreements collected at the fold | `flows.places.places_of`, `desk.evaluate.passes.marks_pass` |
| the chief's edit copy | `flows.places.chief_copy_of`, from the decided places -- the record, read by nothing |
| the docket the write end sets from | `flows.transcribe.docket_of_proof`, from the closed proof's places |
| the author's partial approval | `flows.transcribe._approved`, reached through `docket_of_proof`'s `only`; the flag is `proof --only` |
| what a page holds at an address -- the base and anchor a place is built on | `flows.on_the_page.held_at`, read by `flows.places.bases_and_anchors`, `flows.verify`, `flows.fill.page_text_at` and `commands/check.py` |
| which places a stage deals | `desk.stages.deals`, read by `flows.distribute.seed` and `flows.verify.coverage_problems` |
| which instructions its roles may file | `desk.stages.not_admitted`, read by `flows.fill.fill` and `commands/check.py` |
| a role states the paragraph it wants | `Mark.change`, raw text |
| the answer a role gives in a turn | `desk/answers/` -- `Answer`, and the eight rows |
| the batch send-out | `flows.bus._batch_of`, one slot per carried-forward place per role asked |
| the answers coming back, and the fold again | `flows.answers.answers_of`, `flows.bus._on_answers` |
| the turn counter | derived: `flows.bus.turn_of`, off the places' own answers |
| the chief's own final ruling | `desk/dispositions/`, `desk.evaluate.passes.dispositions_pass`, `flows.bus._on_dispositions` |
| the record of how each place was ruled | the place itself -- `state`, `text`, `sides`, `disposition` -- serialized onto the master proof |
| the human's query riding with the set | `State.UNSETTLABLE` and `place.asking`, reported as `Unsettlable` |
| the console commands | `collate`, `turn`, `disposition`; the proof on disk is `flows/proof_io.py` |
| what `SKILL.md` tells the task agent about a turn | the `agents` lane's, and it is written |

**The 2026-09-04 version of this table measured a tree that no longer exists.** It named
`flows/collate.py`, `flows/turn.py`, `desk/determined.py` and `desk/diff_mark.py`, all deleted
2026-09-18; what each did, and how to read an artifact one of them wrote, is
[`history.md`](history.md), *Reconciliation*.

---

## Where the rules in this file come from

| the rule | its source | where it lives now |
| --- | --- | --- |
| the loop, the batch, the chief's terminator | Roy, 2026-09-02, quoted in full above | `flows/bus.py`, `commands/` |
| the turn is structural, max turns is the agent's | `decision-log.md Process: #78` | nothing enforces a cap; `flows.bus.turn_of` counts |
| an answer is its own artifact, with its own closed sets | `Process: #22` | `desk/answers/` |
| the composition re-read, and its passes | `Process: #49` | `desk/answers/table.py`; the second question is spelled `escalation` |
| `change` is the wanted paragraph as raw text | Roy, 2026-08-28; [`the-mark.md`](the-mark.md) | `desk/proof/mark.py` |
| an escalation and a composition take different answer sets | `Process: #86` | `desk/answers/table.py`, keyed by question |
| the chief's ruling closes a place, one per carried-forward place | `Process: #87` | `desk/dispositions/` |
| agreement is the text alone, and it takes every owing mark | `Process: #88` | `desk.evaluate.passes._from_sides` |
| a lone owing mark goes back to every role that marked but a query | `Process: #89` | superseded by `#180` as a rule of its own; it is the invariant's case |
| an `add` goes back to every role that read the page | `Process: #116` | superseded by `#180` the same way; the `rereads` cell is gone |
| a human query is asked before the fold; the other shapes defer | `Process: #121`, `#197` | `desk.marks.table._query_stance`, `desk.answers.table.asks_human` |
| once settled, always settled, for the review; nothing persists across runs | `Process: #91` | `desk.evaluate.passes.answers_pass`, which narrows only a carried-forward place |
| a text settles only once every reader has proposed or accepted it | `Process: #180` | `desk.evaluate.passes.owed_a_say` |
| one role's marks at one place compose | `Process: #179` | `desk.evaluate.passes.composed_side` |
| an answer's sources are verified before the fold | `Process: #181` | `flows.answers.answers_of` |
| a held move is one entry naming both ends | `Process: #155`, `#182` | `desk.work.fold.Fold.run`, `commands.collate._for_the_human` |
| a move's placement is one question for the pair, answered on the move | `Process: #195` | `desk.evaluate.move.placement_pass`, `flows.bus._batch_of` |
| an acceptance of a withdrawn move's text goes with it | `Process: #188` | superseded by `#200`: an end asks nothing while its move is open, so no text is accepted before the placement settles |
| a withdrawal at one end beside a replacement at the other is refused | `Process: #189` | superseded by `#195`: a withdrawal is a placement answer on the move, and nothing withdraws half of one |
| one end of a move settles with the move, not before it | `Process: #190`, `#200`, `#201` | `desk.evaluate.move.hold_ends`, the `to-come` state |
| the chief rules an undecided move's placement once, then its ends | `Process: #195` item 4, `#201` | `desk.evaluate.move._ruled`, `flows.bus._on_dispositions` |
| the dropped-words list is advisory | `Process: #163`, `#177` | `desk.marks.table._correct_notes`, `events.Advised` |
| copies from different trees are refused | `Process: #178` | `flows.bus._root_problems` |
| the write end reads the proof's decided places | `Process: #184` | `flows.transcribe.docket_of_proof`, `commands/proof.py` |
| no drift check: nothing asks whether a page changed | `Process: #62`, `#185` | nothing; `drift_in` is deleted |
| a short shard or an unruled place rolls the round back | `Process: #186` | `flows.verify.coverage_problems`, `flows.mark_errors`, `flows.bus._on_copies` |
| the fold's base is the page's text | `Process: #125`, `#187` | `flows.on_the_page`, `flows.places.bases_and_anchors`, `flows.bus._on_copies` |
| a partial approval is a place filter on `proof` | `Process: #192` | `flows.transcribe._approved`, `commands/proof.py` |
| compaction is a stage, dealt the places over its cap | `Process: #193` | `desk/topology.py`'s three keys, `desk.stages.deals` and `not_admitted` |
