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
`desk.dispositions.disposition.CHIEF`, the string `copy-chief`.

**This is what makes the loop terminate without a code cap.**
`a-revise-answer-has-no-artifact` T2 asked it as *"with no bound, send it back is a loop."*
The bound is the instruction; the terminator is the chief's ruling. A run cannot spin, because
the last turn always ends in somebody deciding -- and `flows.bus._on_dispositions` refuses a
carried-forward place the chief left unruled, so the close cannot happen with one outstanding.

---

## The place, and the six states

**A place is the aggregate the middle decides** -- `desk/evaluate/place.py`. It carries its
address and anchor, its base text as the page held it, the roles whose copies held that page
(`readers`), every mark filed on it with the role that filed it and which end of a move it is
(`filed`), each turn's answers by role, the chief's disposition where there is one, and what
the passes decide: `state`, `text`, `sides`, `reasons`, `notes`, `asking`, `owed`, `question`
and `partner`.

**The six states are `desk/evaluate/state.py`'s own closed set.**

| state | when a place is in it | what becomes of it |
| --- | --- | --- |
| `stands` | no role proposed a text here, or exactly one did and no other role that read the place is owed a say | settled, on that text or on the base |
| `agreed` | two or more roles' proposals come to one text and every role owed a say has accepted it | settled on that text |
| `composed` | proposals on different sentences compose, or one text is not yet accepted by every role owed a say | carried forward, asking a `composition` |
| `contested` | proposals that will not compose against the base | carried forward, asking an `escalation` |
| `unsettlable` | a `query` of shape `human-review-necessary` is filed here, or an answer of that shape is given | rides to the author; no later pass changes it |
| `refused` | a mark or an answer its table will not read | back to the role, and the fold rolls back |

**Carried forward is `composed` and `contested`, and the set has a name.**
`desk.evaluate.state.CARRIED` is those two, and every reader of "is this still open" asks it:
the bus builds the batch from it, refuses an answer at a place outside it, and the
dispositions table's `closes` is that same set.

## The three tables

**Three actors write with three vocabularies, so there are three tables and one shape of row.**
Nothing outside the three names an instruction, an answer or a disposition, which
`tests/gates/test_tables_name_the_rows.py` holds over the tree.

| table | rows | what a row answers |
| --- | --- | --- |
| `desk/marks/table.py` | the seven instructions | the `claim` keys and which one quotes the paragraph; which places it `touches`; what it `sets` at a touch; what it `reads` as a problem; what it `notes` for the chief; how it `pairs` with the others; which `answers` a turn may give on it |
| `desk/answers/table.py` | eight, keyed by `(question, name)` | which question it answers, its `effect` on the role's own side, whether it owes a `change`, and the `claim` keys it owes |
| `desk/dispositions/table.py` | `taken_in` and `recast` | which states it `closes`, what it `owes`, and the text it `sets` |

**The `Row` shape is declared once**, in `desk/marks/table.py`, and the other two tables have
their own row types built to the same idea: a frozen dataclass whose cells are values and
functions, never prose.

**`stet` is not a disposition row today.** `DISPOSITIONS` holds two names, and
`Disposition.deserialize` refuses any other by name. The word is still what the console prints
for a place the fold settled on its own -- see *What each command prints*, below -- and a
`stet` the chief emits waits on `TODO/no-mark-for-let-it-stand.md`.

## The passes, and the one order they run in

`desk.evaluate.passes.decide(places, turn)` is the whole sequence and the only entry:

    for each place    marks_pass, then answers_pass once per turn up to `turn`
    pair_moves        a move's two ends take the worse of their two states
    for each place    dispositions_pass
    pair_moves        again

**The dispositions pass reads the paired state, and did not until 2026-09-18.** A move's origin
that nobody else marked is `agreed` on its own and `contested` once paired, so with the pass
running before the pairing the chief's ruling was measured against a state its own report had
not printed: a run reported both ends contested, put them to both roles, wrote `contested` on
the proof, and then refused every ruling with *"taken_in cannot close a place that is agreed"*.
The chief could not close a contested move at all.

**And `decide` takes the places, not one place**, for that reason. A caller holding one place
cannot pair anything, so there is no single-place entry left to call in the wrong order. The
three passes stay public and `tests/test_passes.py` drives them one at a time.

**The second pairing is the chief's own refusal travelling.** Two ends the chief closed are
both `stands`, so the guard touches neither and each keeps the text its own ruling set. What it
carries is a ruling `dispositions_pass` refused: a move refused at one end rolls back both, as
it does when the refusal comes from the marks.

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

## The two questions a turn asks

`desk.answers.answer.Question` is a closed set of two, and a slot carries which one it is.
`decision-log.md Process: #49` split the turn in two and called the second *conflict*; the
code's name is `escalation`.

| the question | when it is asked | the answers |
| --- | --- | --- |
| `composition` | this text is what the fold came to, and you have not accepted it | `clean`, `query`, `correct`, `patch` |
| `escalation` | two or more proposals here will not compose | `hold`, `withdraw`, `correct`, `patch` |

**What each answer does to the role's own side** is the row's `effect`
(`desk.answers.table.Effect`), and it is the whole of what an answer means to the fold:

    hold        keeps      the side stands as it was
    withdraw    removes    the side is taken off the place
    correct     replaces   the side becomes the answer's `change`
    patch       replaces   the same
    clean       accepts    the side becomes the text that was put to it
    query       abstains   unless its `claim.shape` is `human-review-necessary`,
                           which makes the place unsettlable

**Only `clean` and `query` owe no `change`**, and that is read off the row's `owes_change`
rather than from a list anybody typed. `check --contract` prints the two questions, the answers
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

**The chief rules each end of a move, and may rule them differently.** A `taken_in` at both
ends puts one entry on the chief's copy, the `move` at its origin; a `taken_in` at one end and
a `recast` at the other puts two, each end written from its own decided text.
`desk.marks.table._sets_both_ends` is what decides between them: a two-place mark is taken in
only where its partner closed on what that mark sets there, because a move whose destination
was recast is not what happened.

**A move held for the human is held at both ends and prints as one entry** --
`decision-log.md Process: #155` and `#182`. `pair_moves` gives the pair one state and clears
the text at the end that took it, so nothing is written to a page while the question is open;
`desk.work.fold._prints` emits the entry once, from the origin.

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
| `AnswersReturned` | the last proof and each role's answers, and the checkout a cite resolves against | the next proof, the chief's copy, the next batch |
| `DispositionsWritten` | the last proof and the chief's rulings | the closed proof and the chief's copy |

**Everything a copy can be wrong about on its own is found before the fold opens.** A quote
that is not in its paragraph, a cite that resolves against nothing, an address no page carries,
a place a role left unruled, a role short of its shard, and a copy gathered from a tree the
others were not (`Process: #178`) each become one `Refused`, and the fold never runs. None of
them is a question about how the roles' rulings meet.

**No handler reads a page.** A place carries its own base text, so what the fold decides comes
from the record alone -- `decision-log.md Process: #62`. The one file a later message opens is
a file an answer cites.

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
round, and there is no such finding left -- drift, a short shard, a place a role left unruled
and a slot a role left unanswered are all found before the fold opens, so each is a `Refused`
and the round rolls back.

**The events print first, in address order; what was written prints after.** These lines are
from `pwsh -NoProfile -File scripts/smoke_middle.ps1`, 2026-09-18, which exits 0 and whose
`collate` and `turn` are each expected to exit 4:

    composed fib.py@a0: function-context, module-context, ownership-context (composition)
    contested fib.py@a3: block-context, function-context, module-context (escalation)
    stet fib.py@b0
    unsettlable fib.py@a1: block-context asks the human -- the docstring and the decorator disagree about what counts
    unsettlable store.py@b5 and store.py@b10: block-context asks the human -- whether this note belongs beside the code or at the foot is the author's call
      and module-context's move drops the paragraph at store.py@b5 and adds it at store.py@b10, one move -- rounding is the last thing the module does and reads as its closing note
    for the chief -- each correct below drops words its claim never named:
    block-context store.py@c5: its change drops 'wants', which its claim never names

| the line | the event |
| --- | --- |
| `<state> <address>: <roles> (<question>)` | `CarriedForward` |
| `stet <address>` | `Settled` |
| `unsettlable <address>: <role> asks the human -- <reason>` | `Unsettlable`, with the partner's address joined by `and` where a move is held at both ends, and an indented `and ...` line for the move |
| `<role> <address>: <reason>`, the address `(the copy)` where there is none | `Refused` |
| the `for the chief` heading, then `<role> <address>: <note>` | `Advised`, printed last and on every path, a rollback included |

**Then the files, one line each, and only on a commit:**

    <out>: 16 places resolved                                       collate
    <proof-out>: the master proof -- 26 places -- 10 settled, 3 unsettlable, 13 carried forward
    <batch-out>: turn 1's batch -- block-context 10, function-context 10, module-context 7, ownership-context 8

    <proof-out>: the master proof after turn 1 -- 26 places -- 15 settled, 4 unsettlable, 7 carried forward   turn
    <batch-out>: turn 2's batch -- block-context 4, function-context 5, module-context 3, ownership-context 5

    <out>: the chief's copy, 17 places                              disposition
    <proof-out>: the proof closed at turn 1 -- 26 places -- 22 settled, 4 unsettlable, 0 carried forward

**Nothing carried forward is no batch rather than an empty one.** A file holding `{}` would be
handed to roles as a turn with nothing in it, so `--batch-out` writes only where the fold
carried something forward, and a turn that carries nothing is the last one there is to run.

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
| the chief's edit copy | `flows.places.chief_copy_of`, from the decided places |
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
| `change` is the wanted paragraph as raw text | Roy, 2026-08-28; [`the-mark.md`](the-mark.md) | `desk/marks/mark.py` |
| an escalation and a composition take different answer sets | `Process: #86` | `desk/answers/table.py`, keyed by question |
| the chief's ruling closes a place, one per carried-forward place | `Process: #87` | `desk/dispositions/` |
| agreement is the text alone, and it takes every owing mark | `Process: #88` | `desk.evaluate.passes._from_sides` |
| a lone owing mark goes back to every role that marked but a query | `Process: #89` | superseded by `#180` as a rule of its own; it is the invariant's case |
| an `add` goes back to every role that read the page | `Process: #116` | superseded by `#180` the same way; the `rereads` cell is gone |
| a human-review query rides and is asked last; the other shapes abstain | `Process: #90`, `#121` | `desk.marks.table._query_stance`, `desk.answers.table._query_effect` |
| once settled, always settled, for the review; nothing persists across runs | `Process: #91` | `desk.evaluate.passes.answers_pass`, which narrows only a carried-forward place |
| a text settles only once every reader has proposed or accepted it | `Process: #180` | `desk.evaluate.passes.owed_a_say` |
| one role's marks at one place compose | `Process: #179` | `desk.evaluate.passes.composed_side` |
| an answer's sources are verified before the fold | `Process: #181` | `flows.answers.answers_of` |
| a held move is one entry naming both ends | `Process: #155`, `#182` | `desk.work.fold._prints`, `commands.collate._for_the_human` |
| the dropped-words list is advisory | `Process: #163`, `#177` | `desk.marks.table._correct_notes`, `events.Advised` |
| copies from different trees are refused | `Process: #178` | `flows.bus._root_problems` |
