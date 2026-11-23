# The turn -- what a turn IS, and what closes the editorial roles

**This file is the source.** What a turn is, what goes out in one, what comes back, and what
ends the editorial part of a run are stated here. `desk/evaluate/`, `desk/work/` and
`flows/bus.py` implement this file; `SKILL.md` tells the task agent to drive it. **Neither of
them defines it.**

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

What the quotation calls a `DiffMark` is an `Answer` (`desk/proof/answer.py`); *recollated* is
the fold run again over the same places, which is what `flows.bus` does with each turn's
answers written onto them. The current escalation slot carries the base paragraph and
role-labeled sides. The bus puts the decisions on the master proof, and the command saves it.

## The loop, as steps

    COLLECT     `collate` folds one stage's returned copies into places; each place
                not decided on one text is carried forward, and so is each move
                whose placement is undecided
    BATCH       one file, one slot per carried-forward place or undecided move per
                role it is put to
    ANSWER      each role answers every slot it was sent, in its own file
    FOLD        `turn` writes those answers onto the places and moves and folds again
                                                            <- that is turn one
    REMAINDER   what is still carried forward goes out in the next batch, is
                answered, and is folded again
                                                            <- that is turn two
    CAP         the number of turns is what the task agent was told; where
                `collate` carries a place forward as `composed`, one turn runs
                when no number is given
    CHIEF       `disposition` takes the chief's ruling at every place and move
                still carried forward, and a `recast` at any decided place the
                style sheet asks it to change
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

**One turn runs by default where `collate` composes** -- `decision-log.md Process: #298`. A
`composed` place may hold a merge of several sides or a lone proposal that other readers
still need to see. The turn sends that text to the roles owed a say before the chief rules; a
change no role but its proposer read is owed to no role and goes to the chief with no turn
(`Process: #385`). `SKILL.md` tells the task agent so; nothing in the code requires
the turn.

**So a code-enforced cap is wrong and a turn counter is not.** The counter is derived rather
than stored: `flows.bus.turn_of` returns the highest turn any of a proof's places or moves
records an answer at, and the next turn is that plus one. Nothing counts turns of its own, and
no module holds a maximum.

## The copy chief's own ruling is the terminator

**When max turns is reached, the chief rules.** Not "the run fails", not "it escalates to a
human", not "the place is dropped": *"the copy-chief or the task agent acting as copy chief
applies its own ruling to the final piece and puts that in the copy-chiefs edit copy."*
The current command records that ruling on the master proof (Process #313).

**The chief may be the task agent wearing that hat.** The role is a seat, not a separate
dispatch. Its name is `desk.proof.disposition.CHIEF`, the string `copy-chief`.

**The task agent applies the turn cap.** The commands have no maximum turn count.
`disposition` refuses a carried-forward place or an undecided move the chief
left unruled, so a proof cannot close while either is outstanding.

---

## The place, and the six states

**A place is the aggregate the middle decides** -- `desk/proof/place.py`. It carries its
address and anchor, its base text as the page holds it (read by the collate handler, below), the
roles whose copies held that page (`readers`), every mark filed on it with the role that filed
it and which end of a move it is (`filed`) -- on the proof, a pointer to the mark where its
edit_copy holds it, `{copy, sheet, mark, touch}`, so each mark is stored once -- each turn's
answers by role, the chief's disposition where there is one, and what the passes decide:
`state`, `text`, `sides`, `reasons`, `notes`, `owed` and `question`. A move is an aggregate of
its own, over its two places -- `desk/proof/move.py`, and the passes that decide it
`desk/evaluate/move.py`, below.

**The six states are `desk/proof/state.py`'s own closed set.**

| state | when a place is in it | what becomes of it |
| --- | --- | --- |
| `stands` | see [the definition on `State.STANDS`](../src/comment_review/desk/proof/state.py) | decided |
| `agreed` | two or more roles' proposals come to one text and every role owed a say has accepted it | decided on that text |
| `composed` | proposals whose changed words do not overlap compose, one text is not yet accepted by every role owed a say, or a change only its proposer read awaits the chief (`Process: #385`) | carried forward, asking a `composition` |
| `contested` | proposals that will not compose against the base | carried forward, asking an `escalation` |
| `refused` | a mark, an answer or a ruling its table will not read; one role's marks that will not compose; marks at one address carrying differing anchors; a human query still standing | back to the role or the chief, and the fold rolls back |
| `to-come` | an end of a move whose placement is undecided | waits on the placement; holds no text, is put to no role, takes no ruling |

**Carried forward is `composed` and `contested`, and the set has a name.**
`desk.proof.state.CARRIED` is those two, and every reader of "is this still open" asks it:
the bus builds the batch from it and refuses an answer at a place outside it, and the
dispositions table's `taken_in` closes that same set. **Decided is `stands` and `agreed`**,
`desk.proof.state.DECIDED` (`Process: #333`), which is the set the write end requires of every
place.

## A human question stops the round before the fold

**No state holds a place for the human** -- `decision-log.md Process: #197`. A query of shape
`human-review-necessary`, filed as a mark (`flows.human.queries_in_copies`) or given as an
answer (`flows.human.queries_in_answers`), and a change to the file's own matter that
still needs approval each become one `AsksTheHuman`. The bus checks for pending approval
when it receives marks, answers, or chief rulings. The
round rolls back with nothing written, and the command exits `ASKS_THE_HUMAN` where no refusal
stands beside them.

**The human's answers file rides on the message** -- `Process: #198`. `collate`, `turn` and `disposition` accept `--human`. An answered query is printed with
the response. A matching approval clears the pending matter question. The asking
role replaces its query with a mark or an answer that reflects the response, and the round runs
again. A human query that reaches a pass is refused there (`marks_pass`, `answers_pass`,
`placement_pass`).

## The three tables

**The mark, answer and disposition tables define how each row acts.**
`tests/gates/test_tables_name_the_rows.py` checks selected row-name spellings outside the
tables and their associated proof types. Its docstring lists the patterns it misses.

| table | rows | what a row answers |
| --- | --- | --- |
| `desk/marks/table.py` | the seven instructions | which places a mark `touches`; what it `sets` at a touch; what it `reads` as a problem; what it `notes` for the chief; how it `pairs` with the others; whether it `carries_raw_text` |
| `desk/answers/table.py` | twelve, keyed by `(question, name)` | the answer's `effect` -- on the role's own side (`SideEffect`), or on its placement vote (`PlacementEffect`) |
| `desk/dispositions/table.py` | `taken_in` and `recast` | which states it `closes`, and the text it `sets` |

**What a mark, an answer or a ruling owes in order to be read is its type's, not its row's**:
the claim keys, whether a `change` is owed, whether `sources` are, in `desk/proof/mark.py`,
`desk/proof/answer.py` and `desk/proof/disposition.py`.

**The `Row` shape is declared once**, in `desk/marks/table.py`, and the other two tables have
their own row types built to the same idea: a frozen dataclass whose cells are values and
functions, never prose.

**`stet` is not a disposition row.** `DISPOSITIONS` holds two names, and
`desk.proof.disposition.read_disposition` refuses any other by name. The chief's stet is
`taken_in` with side `original` (`Process: #332`). `stet` is a reader's answer refusing a
move's placement (`Process: #195`, `#393`), below.

## The passes, and the one order they run in

`desk.evaluate.passes.decide(places, moves, turn)` is the whole sequence and the only entry:

    for each move      placement_pass, with the chief's placement ruling where
                       there is one; then decide_ends, which takes a withdrawn
                       move off both ends and an agreed move's untaken movers off
    for each place     marks_pass, then answers_pass once per turn up to `turn`
    for each move      cover_ends: a move the chief took in from its one mover
                       decides each end that reads exactly as the move sets it;
                       then hold_ends: an undecided move's ends are `to-come`,
                       except an end already refused
    for each place     dispositions_pass
    for each move      keep_ends: a ruling that puts an agreed move's end back
                       to its base is refused

**A move's placement is decided before either end's words** -- `decision-log.md Process: #195`
and `#200`. So the placement pass and its settling run first, and the ends are then read as
ordinary places -- an agreed move's against the move still filed there (`#205`); `hold_ends`
runs after them and before the chief's pass, so a `to-come` end is what the chief's pass sees,
and a ruling there is refused rather than closing words the move's outcome may change.

**And `decide` takes the places and the moves together.** `desk.work.fold.Fold` finds the moves
on its own places (`moves_in`), so a caller cannot fold a move's two ends as unrelated places.
The passes stay public and `tests/test_passes.py` drives them one at a time.

## A text is decided only when every role that read the place has had its say

**This is the invariant, and it is one rule rather than a rule per instruction** --
`decision-log.md Process: #180`. `desk.evaluate.passes.owed_a_say` names the roles that have
not accepted the text; a place with any is carried forward as a `composition` to exactly those
roles, at the first fold and after a turn alike. A role is not owed a say when one of three
things is true of it:

| | |
| --- | --- |
| it filed only a `query` | a deferring query hands the place on and is not a second party |
| its side is this text | it proposed the text, or its answer replaced or accepted its way to it |
| it answered and holds no side | it was asked, and withdrew or deferred; it has had its say |

**A change no role but its proposer read goes to the copy chief** -- `Process: #385`, which
supersedes `#180`'s lone-proposal clause. No role is owed a say, so no turn is run for it: the
place is carried forward as `composed`, owed to nobody, and `desk.work.fold.put_to` names the
chief. A role that only filed deferring queries there is not a second party, so an `add` beside
them goes to the chief too (`#386`, superseding `#121`), and a stage 6 condensation is under the
same rule (`#387`). A move whose one mover is its only reader is held `open`, owed to no role,
the same way. **A lone proposal against three `clean`s is different**: those three read the place
and have not seen this text, so it goes back to them.

**The chief's ruling on a lone move is the second party at both ends** -- `#388`.
`desk.evaluate.move.cover_ends` decides each end whose one side is the mover's and reads exactly
as the move sets it; an end where the mover changed more stays carried for its own ruling.

**`#89` and `#116` are cases of this rule.** *A lone owing mark goes back to every role that
marked but a query* and *an `add` goes back to every role of the stage* both fall out of the
invariant, so no row of the marks table is asked.

**Who a place is put to is recorded, not re-derived.** The pass writes `place.owed`;
`desk.work.fold.asked` reads it back; `flows.bus._batch_of` builds a slot per role in it, and
`flows.bus._on_answers` refuses an answer from a role that is not.

## One role's own marks at one place compose

`decision-log.md Process: #179`. A role may file a second ruling at an address, and its marks
there make one side: `desk.evaluate.passes.composed_side` sets the side from the one mark where
there is one, and composes several against the base with `differences.compose`, the one rule
two roles' sides compose by too (`Process: #389`-`#392`). It reads only the texts: edits clash
only where the base words they change overlap, where two inserts sit at one position, or where
an insert falls inside another edit, so edits on neighbouring words or lines compose. Marks
whose edits clash are refused back to that role
naming each: the reason asks it to withdraw one, or, where every one of them sets its own
`raw_text` and none is a move's origin, to restate the paragraph with both texts. A `clean` or a
deferring `query` proposes no text and stands beside them.

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
    query       defers     removes the role's side; a `human-review-necessary`
                           query is a human question instead, above

A filed `clean` proposes no text. A `clean` answer to a composition accepts the specific
text in the slot and makes it the reader's side. If another answer introduces a conflicting
rewrite, that reader is asked in the escalation. A reader who has no position can defer with
an `outside-my-role` or `unable-to-determine` query (`Process: #314`).

**A move is answered on the move, once, for the pair** -- `decision-log.md Process: #195`.
The placement slot names both addresses and every mover's snippet and arrival, and its answer is
recorded on the move rather than at either end. `agree` accepts the placement, `stet` contests
it for the chief, a mover's `withdraw` takes its filing off the move -- a `withdraw` from a role
that did not file the move is refused -- and a `query` of shape `human-review-necessary` is a
human question. The placement rows use `desk.answers.table.PlacementEffect`; either other query
shape relinquishes the role's prior placement vote. No answer at an end reaches the move: while
the placement is undecided the ends are `to-come` and are put to nobody (`#200`), so there is no
end answer to reach it. Once the move is agreed, a `correct` or a `patch` at an end is an answer
on that place alone, like any other.

**`correct` and `patch` owe a `change`, and `correct`, `patch` and `clean` owe a source** --
`decision-log.md Process: #306`. Each is a class attribute of the answer's type in
`desk/proof/answer.py` (`owes_change`, `owes_sources`), and a `query` owes the claim keys
`shape`, `attempted` and `settles`. `check --contract` prints what `flows.answers.contracts`
generates from the tables and the types: the shape of a stage-4c mark (`stage_4c_mark`), the
chief's rulings (`chief`, from `desk.proof.disposition.contract`), and for each question the
answers it admits, which owe a change and which a source, the claim keys each owes, and what
each field is.

**An unanswered slot is not an inferred `withdraw`.** The null answer must be written by a
hand -- `decision-log.md Process: #22` -- so `flows.answers.answers_of` refuses every sent slot
that came back without an `instruction`, by name, and the round rolls back. A turn can end with
places still open rather than with silence counted as agreement.

**A role may answer one slot more than once** -- `decision-log.md Process: #308`, `#309`.
`answers_of` reads each answer on its own, and `flows.answers._one_answer` makes them one.
Rewrites compose against the text the role was asked about -- its own side at an escalation,
the slot's `raw_text` otherwise -- into one `correct` where any of them is a `correct` and a
`patch` otherwise, carrying every reason and every source. Repeats of one other answer with one
claim collapse to the first. Every other combination is a contradiction: rewrites whose edits
meet, two different answers side by side, or two of one answer whose claims differ. The slot is
then refused by role and address, and the round rolls back.

**An answer's evidence is verified before the fold, as a mark's is** -- `Process: #181`.
`answers_of` runs `desk.collator.cited_problems` over each answer's `sources` against the tree
the copies were read from; a cite that does not resolve refuses the answer, and
`check --answers` reports the same thing before the send. Opening a cited file is not a page
read.

## What the chief rules, and what it closes

**Two rulings, each owing a `reason`.**

| ruling | what it carries | the text it sets | what it closes |
| --- | --- | --- | --- |
| `taken_in` | `side` -- a role, or `original` | that role's side, or none, which leaves the paragraph as it was | a carried-forward place |
| `recast` | `prose` | the chief's own paragraph; empty `prose` drops the paragraph whole (`Process: #299`) | a carried-forward place, or a decided one (`Process: #310`) |

**A `recast` at a decided place is how the chief brings the roles' text into line with the style
sheet** -- `Process: #310`; its reason names the style-sheet entry. A `taken_in` at a decided
place is refused, and so is a `recast` whose prose is the text the roles decided on, which would
change nothing.

`dispositions_pass` refuses a ruling at a place outside its row's `closes`, a `taken_in` naming
the chief's own side, and one naming a side that proposed nothing here.
`flows.bus._on_dispositions` refuses a ruling at a place its row does not close, a ruling at a
`to-come` end, a second ruling at one place or on one move -- identical or not, since the chief
has not said which stands -- and a carried-forward place or an undecided move left unruled,
naming the roles a place was put to. Any refusal rolls the round back and nothing is written,
so neither of two rulings at one place is applied.

**The proof records the chief's reason.** A decided place holds its decided text, filed marks and any disposition. The disposition carries the chief's reason, and each filed mark keeps its reviewer's reason.

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

**A refused move is reported once, from the move**: its own reasons at its two addresses, and
an end's own reasons at that end (`desk.work.fold.Fold.run`).

## What the write end reads

**The closed proof, and the places it decided** -- `decision-log.md Process: #184`.
`proof --proof <the closed proof>` transcribes one alteration per place whose decided text
differs from the paragraph already there, in each page's own place order, with an emptied place
written as the delete; `flows.transcribe.docket_of_proof` is that step. It refuses, naming each:
a place that is not decided -- such a text has not been decided (`Process: #180`), so a proof holding
one is not closed -- an undecided move, a place that will not read back, and a page a decided
place sits on that the checkout cannot open.

**A partial approval is a place filter on that same command** -- `Process: #192`. The author
approves some decided places and not others, so `proof --proof <the closed proof> --only
<address>`, repeatable, transcribes those places alone and leaves every other place as the page
has it. It refuses an address the proof does not carry, and one end of an agreed move whose
other end is not approved: a move is one decision at two places, and setting the origin alone
drops the paragraph and adds it nowhere, while setting the destination alone writes it in both.
A named place the write end sets nothing at -- it stands on the text already there -- is
approved with nothing to set rather than refused. `--only` without `--proof` is an argument
error: a copy holds marks and a docket holds alterations already chosen, so neither has places
to filter.

**The master proof is the record of the decisions.** The `collate`, `turn` and `disposition` commands write it to `--proof-out` on commit. The docket reads the closed proof's decided places.

**`proof --copy` stays, for a role's own draft.** A role's copy holds that role's marks and
nobody else's, and drafting it is how one stage's output becomes the revise the next stage
reads (`Process: #76`).

## The Unit of Work, and the events

**One fold over one stage's places, in `desk/work/fold.py`.** `Fold(places, recorded,
turn).run()` hands the places and the moves found on them to `decide`, walks the places in
address order and then the moves, and either commits -- every place decided, none refused, no
move refused -- or rolls back, in which case `Fold.decided` is empty and the flow saves nothing.
It opens no file and knows no container of the read or write end.

**The events describe the fold outcome** -- `desk/report.py`. The commands also report
the files they save and derive proof counts from its places.

| event | what it says |
| --- | --- |
| `Refused` | one role's reasons at one place or move; the round is rolling back |
| `AsksTheHuman` | one human question, found before the fold, and the human's answer where the answers file holds one; the round is rolling back |
| `CarriedForward` | the address, its state, its question and the roles it is put to |
| `PlacementCarried` | an undecided move's two addresses, its placement and the roles it is put to |
| `Advised` | what one role is told about one place without being refused for it |
| `Decided` | one place the fold decided, the roles whose text stands, and the chief's ruling where there is one |
| `Committed` | the fold committed |
| `RolledBack` | the fold rolled back and saved nothing |

**An advisory note decides nothing** -- `decision-log.md Process: #177`. The `correct` row's
`notes` cell reports a change that drops words the claim never named; the fold emits an
`Advised` and commits over it.

## The bus -- three messages, one handler each

`flows/bus.py` is in-process and synchronous: a dict of message type to handler, not
infrastructure. A handler checks what its message carries, derives the places, opens a `Fold`,
and on commit builds what the stage saves.

| message | what it reads | what a commit leaves |
| --- | --- | --- |
| `CopiesReturned` | one stage's parsed copies, the binder, each copy's received binder where given, the checkout, the topology where there is one, and the human's answers | the master proof at turn 0 and the first batch |
| `AnswersReturned` | the last proof, each role's answers, the checkout a cite resolves against, and the human's answers | the next proof and the next batch |
| `DispositionsWritten` | the last proof, the chief's rulings, and any human approvals | the next proof -- closed, or carrying a ruled move's ends forward -- |

**`collate` can take each copy with its received binder**, by `--edit-copy` and
`--received-binder` repeated in one order, or by `--pairs`, a JSON list of
`{edit_copy, received_binder}` paths, in place of both.

**Collate checks admission before the fold opens.** A quote
that is not in its paragraph, a cite that resolves against nothing, an address no page carries,
a place a role left unruled, a role short of its shard, a received binder or reading context
that disagrees with the stage's, a copy dealt in another stage, a mark its stage does not admit,
and a copy gathered from a tree other than the binder's (`Process: #178`) each become one
`Refused`, reported beside the trial fold's own refusals. None of them is a question about how the roles' rulings
meet. The fold then applies mark-row rules against each place's base. A short shard and
an unruled place roll the whole round back like the rest: the role is
named, nothing is written, and `collate` runs again over the repaired copies (`Process: #186`).
`flows.verify.admit` checks addresses and evidence against the pages, then runs a trial fold
over every mark but the human queries; `collate` commits from that fold. `check --edit-copy`,
`mark` and `proof --copy` call the same `admit` with the inputs they hold, so `check` reports
the fold's own row reads and compositions rather than applying the mark rows itself.

**What each handler reads.**

| handler | what it opens | why |
| --- | --- | --- |
| `CopiesReturned` (`collate`) | the pages its copies' marks touch, and the files a mark cites | to check each address and quote against the page (`Process: #119`, `#122`), to take each place's base text and anchor from it (`#187`, `#125`), and to verify each citation |
| `AnswersReturned` (`turn`) | the files an answer cites | to verify the citation (`#181`); its places come off the proof |
| `DispositionsWritten` (`disposition`) | nothing | its places come off the proof |

**The collate handler reads the base off the page, not the binder** -- `Process: #187`, which
restores `#125`. The binder is the seed for what a role is handed, not every place a mark may
touch: a move may land in a file the run did not gather, and measured against the binder such a
place would have the base `""`, so a destination text that dropped a word of the paragraph
already there would pass every check. `flows.on_the_page` is the one reader of what a page holds
at an address; `check`, `collate` and `proof` read through it, and `mark` does for every place
but the slot it seeds, so the four measure a mark against the same text. A place's anchor is
read the same way, except at a mark's own address, where it is the anchor the role returned,
since the write end checks that one against the page's (`#134`).

**Nothing asks whether a page changed** -- `Process: #62`, `#185`. Reading the page for a base
is not a drift check: nothing compares what a role was seeded with against what came back, and
nothing compares the page against the binder. Once the places are built, the fold decides from
them alone.

## What each command prints, and what it exits

**Six exit codes are declared in `commands/report.py`.** `collate`, `turn` and
`disposition` share them. `check` uses 0, 1, 2 and 5.

| code | name | what it means |
| --- | --- | --- |
| 0 | `OK` | the fold committed and carried nothing forward |
| 1 | `BROKEN` | a rollback: something was refused, every reason is on stdout, nothing was written |
| 2 | `UNREADABLE` | a file or an argument is not what it says; nothing was read past it |
| 3 | `REREADS` | places carried forward, all of them compositions, or a placement still open |
| 4 | `ESCALATIONS` | at least one place carried forward as an escalation, or a placement contested |
| 5 | `ASKS_THE_HUMAN` | a rollback holding human questions and no refusal; nothing was written |

A short shard, a place a role left unruled and a slot a role left unanswered are found before
the fold opens, so each is a `Refused` and the round rolls back (`Process: #186`).

**The events print first -- the places in address order, then the moves -- and the advisory
notes after them; what was written prints last.**

| the line | the event |
| --- | --- |
| `<role> <address>: <reason>`, the address `(the copy)` where there is none | `Refused` |
| `asks the human <at>: <role> -- <question>; ask it, record the answer in the answers file, and send it back to <role>` | `AsksTheHuman`, not yet answered |
| `answered by the human <at>: <role> -- <answer>; <role> replaces this query with its mark or answer` | `AsksTheHuman`, with the answers file's answer |
| `<state> <address>: <roles> (<question>)`, the roles `copy-chief` where no role is owed a say (`desk.work.fold.put_to`) | `CarriedForward` |
| `<placement> <origin> -> <destination>: <roles> (placement)`, the same | `PlacementCarried` |
| `decided <address>: <roles>`, or `decided <address>: original` where the text is the stage's base (`Process: #396`) | `Decided`, by the fold alone |
| `<ruling> <address>: <side> -- <reason>` | `Decided`, by the chief's ruling |
| the `for the chief -- advisory notes:` heading, then `<role> <address>: <note>` | `Advised`, printed last, and only over a commit: `Fold.run` reports a rollback's refusals and nothing else. A note itself still rolls nothing back (`Process: #177`) |

**Then the files, one line each, and only on a commit** (`commands/collate.py`,
`commands/turn.py`, `commands/disposition.py`; the counts are `commands.report.counted`):

    <proof-out>: the master proof -- <n> places -- <d> decided, <c> carried forward, <t> to come
    <batch-out>: turn 1's batch -- <role> <slots>, ...

    <proof-out>: the master proof after turn <t> -- <counts>               turn
    <batch-out>: turn <t+1>'s batch -- <role> <slots>, ...

    <proof-out>: the proof closed at turn <t> -- <counts>
    <proof-out>: the proof at turn <t> is not closed -- <counts>; rule what it carries and run disposition again on it

**Nothing carried forward is no batch rather than an empty one.** A file holding `{}` would be
handed to roles as a turn with nothing in it, so `--batch-out` writes only where the fold
carried something forward, and a turn that carries nothing is the last one there is to run.

## What a stage deals, and what its roles may file

**Three keys on a topology stage row, and each is optional** -- `decision-log.md Process: #193`.
Absent on every ordinary stage, which is what makes one deal every place a role is handed and
admit every instruction.

| key | what it says | read by |
| --- | --- | --- |
| `cap` | the length, in lines, a place's text must run over to be dealt | `desk.stages.deals` |
| `series` | which series this stage deals, by letter | `desk.stages.deals` |
| `admits` | which instructions its roles may file, by name | `desk.stages.not_admitted` |

`desk/topology.py` checks each against the set that defines it -- a letter against
`reading.series`, an instruction name against the marks table -- so a row naming something
outside either is refused by the value it typed.

**A nonempty series list limits the places dealt.** It restricts the
eligible addresses. A positive cap deals only places whose line count exceeds it.
The count is the page's own `lines`, which `binder.page` fills from the paragraph's raw text
when a binder is read back and the lexer fills when a page is built; a place holding no prose
counts none, so it is never over a cap.

**The deal is narrowed in two places and stated in one.** `flows.distribute.seed` gives a slot
to the places the stage deals, and `flows.verify.admit` measures a returned copy
against the same `deals` -- Roy, 2026-09-19: *"only touching places that are over the length
limit - all other places are automatically clean for this role."* A page a stage deals nothing
on keeps its sheet and no slot, and `distribute` prints `0 places for <role> to rule on`.
A stage that deals part of the binder and is collated without `--topology` is reported short of
its coverage, and correctly: nothing else in the run says what was dealt.

**What a role may file rides on the copy.** The seed stamps the stage's name and its admitted
instructions onto the `edit_copy`, as `read_from` carries the tree it was cut from, so
`flows.fill` refuses a ruling as `mark` places it -- `stage 6 admits patch, drop, add, clean,
and not correct` -- and `commands/check.py` holds a hand-written copy to the same rule without
the run's topology beside it. `flows.verify._admitted_problems` holds the returned copies to the
row itself at `collate`, where the row is in hand.

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

**A role states what it wants the paragraph to read like**, because a mark's `change` is the
updated paragraph as raw text ([`the-mark.md`](the-mark.md)). The chief can take in a role's text, keep the original, or recast the paragraph.
`place.sides` records the role-labeled proposals on the proof and supplies them to the batch.

**What remains of stage 5 is the choosing and the chief's own ruling**, not transcription.

---

## Where each piece lives

| | |
| --- | --- |
| disagreements collected at the fold | `flows.places.places_of`, `desk.evaluate.passes.marks_pass` |
| the docket the write end sets from | `flows.transcribe.docket_of_proof`, from the closed proof's places |
| the author's partial approval | `flows.transcribe._approved`, reached through `docket_of_proof`'s `only`; the flag is `proof --only` |
| what a page holds at an address -- the base and anchor a place is built on | `flows.on_the_page.held_at`, read by `flows.places.bases_and_anchors` and `flows.verify` |
| which places a stage deals | `desk.stages.deals`, read by `flows.distribute.seed` and `flows.verify.admit` |
| which instructions its roles may file | `desk.stages.not_admitted`, read by `flows.verify._admitted_problems` |
| a role states the paragraph it wants | `Mark.change`, raw text |
| the answer a role gives in a turn | `desk/proof/answer.py` -- `Answer` and its types; `desk/answers/table.py`, the twelve rows |
| several answers at one slot, made one | `flows.answers._one_answer` |
| the batch send-out | `flows.bus._batch_of`, one slot per carried-forward place or undecided move per role asked |
| the answers coming back, and the fold again | `flows.answers.answers_of`, `flows.bus._on_answers` |
| the turn counter | derived: `flows.bus.turn_of`, off the places' and moves' own answers |
| a human question | `flows.human`, reported as `AsksTheHuman` by `flows.bus._asks` |
| the chief's own final ruling | `desk/proof/disposition.py`, `desk/dispositions/`, `desk.evaluate.passes.dispositions_pass`, `flows.bus._on_dispositions` |
| the record of how each place was ruled | the place itself -- `state`, `text`, `sides`, `disposition` -- serialized onto the master proof |
| the console commands | `collate`, `turn`, `disposition`, sharing `commands/report.py`; `check --answers` and `check --contract`; the proof on disk is `flows/proof_io.py` |
| what `SKILL.md` tells the task agent about a turn | the `agents` lane's, and it is written |

---

## Where the rules in this file come from

| the rule | its source | where it lives now |
| --- | --- | --- |
| the loop, the batch, the chief's terminator | Roy, 2026-09-02, quoted in full above | `flows/bus.py`, `commands/` |
| the turn is structural, max turns is the agent's | `decision-log.md Process: #78` | nothing enforces a cap; `flows.bus.turn_of` counts |
| a collate that composes runs one turn by default | `Process: #298` | `SKILL.md` stage 5; nothing in the code |
| an answer is its own artifact, with its own closed sets | `Process: #22` | `desk/proof/answer.py`, `desk/answers/` |
| the composition re-read, and its passes | `Process: #49` | `desk/answers/table.py`; the second question is spelled `escalation` |
| `change` is the wanted paragraph as raw text | Roy, 2026-08-28; [`the-mark.md`](the-mark.md) | `desk/proof/mark.py` |
| an escalation and a composition take different answer sets | `Process: #86` | `desk/answers/table.py`, keyed by question |
| the chief's ruling closes a place, one per carried-forward place | `Process: #87` | `desk/dispositions/`, `flows.bus._on_dispositions` |
| agreement is the text alone, and it takes every owing mark | `Process: #88` | `desk.evaluate.passes._from_sides` |
| a lone owing mark goes back to every role that marked but a query | `Process: #89` | a case of `#180`; no row is asked |
| an `add` goes back to every role that read the page | `Process: #116` | a case of `#180`; no row is asked |
| a human query is asked before the fold; the other shapes defer | `Process: #197` | `flows.human`, `flows.bus._asks`, `desk.marks.table._query_stance`, `desk.answers.table.asks_human` |
| ordinary turn answers apply only to carried-forward places | `Process: #91` | `desk.evaluate.passes.answers_pass`; the chief may recast a decided place under #310 |
| a text is decided only once every reader has proposed or accepted it | `Process: #180` | `desk.evaluate.passes.owed_a_say` |
| a change only its proposer read goes to the chief, with no turn | `Process: #385`, `#386`, `#387` | `desk.evaluate.passes._from_sides`, `desk.evaluate.move.placement_pass`, `desk.work.fold.put_to` |
| the chief's ruling on a lone move decides both ends it sets | `Process: #388` | `desk.evaluate.move.cover_ends` |
| a ruling that puts an agreed move's end back is refused | `Process: #283` | `desk.evaluate.move.keep_ends` |
| one role's marks at one place compose | `Process: #179` | `desk.evaluate.passes.composed_side` |
| edits clash only where their changed words overlap, whoever filed them | `Process: #389`-`#392` | `differences.compose` |
| an answer's sources are verified before the fold | `Process: #181` | `flows.answers.answers_of` |
| a move's placement is one question for the pair, answered on the move | `Process: #195` | `desk.evaluate.move.placement_pass`, `flows.bus._batch_of` |
| one end of a move is decided with the move, not before it | `Process: #190`, `#200`, `#201` | `desk.evaluate.move.hold_ends`, the `to-come` state |
| the chief rules an undecided move's placement once, then its ends | `Process: #195` item 4, `#201` | `desk.evaluate.move._ruled`, `flows.bus._on_dispositions` |
| the dropped-words list is advisory | `Process: #163`, `#177` | `desk.marks.table._correct_notes`, `events.Advised` |
| copies from different trees are refused | `Process: #178` | `flows.verify.admit` |
| the write end reads the proof's decided places | `Process: #184` | `flows.transcribe.docket_of_proof`, `commands/proof.py` |
| no drift check: nothing asks whether a page changed | `Process: #62`, `#185` | nothing |
| a short shard or an unruled place rolls the round back | `Process: #186` | `flows.verify.admit`, `flows.mark_errors`, `flows.bus._on_copies` |
| the fold's base is the page's text | `Process: #125`, `#187` | `flows.on_the_page`, `flows.places.bases_and_anchors`, `flows.bus._on_copies` |
| a partial approval is a place filter on `proof` | `Process: #192` | `flows.transcribe._approved`, `commands/proof.py` |
| compaction is a stage, dealt the places over its cap | `Process: #193` | `desk/topology.py`'s three keys, `desk.stages.deals` and `not_admitted` |
| an empty recast drops the paragraph | `Process: #299` | `desk.proof.disposition.RecastRuling` |
| a `clean`, `correct` or `patch` answer owes a source | `Process: #306` | `desk.proof.answer`'s `owes_sources` |
| the chief's reason is on the place's disposition | `Process: #313` | `desk.proof.place.Place` |
| several answers at one slot compose, and any other mix is refused | `Process: #308`, `#309` | `flows.answers._one_answer` |
| the chief may recast a decided place for the style sheet | `Process: #310` | `desk.dispositions.table`'s `recast` row, `flows.bus._on_dispositions` |
