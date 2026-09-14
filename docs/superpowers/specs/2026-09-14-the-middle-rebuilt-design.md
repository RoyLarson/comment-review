# The middle, rebuilt: three tables, an evaluator, and a Unit of Work

Design, 2026-09-14. Approved section by section in conversation with Roy the same day; the
rulings it rests on are in `docs/decision-log.md`, Process #168 to #176.

A better prototype, not the finished middle. Roy, 2026-09-14: *"This is still a prototype.
It's just hopefully a better prototype."* It is built against what three real runs showed
the middle must do, and nothing speculative.

## Why

The middle -- `desk/` and the folding half of `flows/` -- is about 6,000 lines, and the rules
that combine marks are not in one place. Measured 2026-09-14: 58 sites test an instruction
by name across 7 files, 31 of them in `flows/turn.py`, which holds 38 functions, most of them
one special case each. What a mark does to a place is decided in six functions in four
modules. The atomicity rules Roy has ruled -- a move is both ends or neither, a refused copy
writes nothing, a disposition refuses and writes nothing -- are each enforced where someone
noticed, not once.

The self-run of 2026-09-14 over this repo's own code found seventeen defects in how a run is
carried (`OneDrive/comment-review-feedback/2026-09-14-self-run`), six of them fixed on
`feat/the-cli-carries-a-real-run` before this design. Roy, the same day: *"the prototype code
is turning into a tangled mess and rules are becoming adhoc and forgotten."*

## The shape, in one paragraph

Roy: *"the process I think would fit C best, but how it's done is best fit by A."* What
happens at a place is an evaluator dispatching through tables of rows (A, an interpreter
with a dispatch table). What happens between stages is a message bus whose handlers each
open a Unit of Work (C, Cosmic Python). The business -- the tables, the place, the evaluator,
the Unit of Work -- lives in `desk/`; `flows/` pushes the pieces through; `commands/` parses,
sends and prints.

## Decisions this design rests on

| decided | choice | consequence |
| --- | --- | --- |
| the instruction set | deliberately open | a new instruction, answer or disposition is one row; no reader changes |
| the aggregate | a place | a move is two aggregates in one transaction; both commit or neither |
| the transaction | one fold: `collate`, one `turn`, or `disposition`; and `mark` over one copy | every "nothing written" rule is a rollback |
| how it lands | rebuilt beside; the old goes private as each piece passes, then is deleted with its tests | nothing has to keep working in between |
| where the business lives | `desk/`, in sub-packages; `flows/` runs the steps | desk imports leaves only; the flow derives places from the copies and the proof and hands them over |
| what it is measured against | the three real runs, and the old tests where they still describe wanted behaviour | the fixture is real copies, not hand-built shapes |

## The three tables

Three actors write with three vocabularies, so there are three tables, one shape of row.
Every reader in the middle asks a row; nothing outside the three table modules names a mark,
an answer or a disposition, and a gate test walks the tree to hold that.

### The marks table -- what a role files

One row per instruction: `clean`, `query`, `drop`, `correct`, `patch`, `add`, `move`. A row
answers five questions:

| field | what it answers |
| --- | --- |
| `claim` | the keys the claim carries, and which one quotes the paragraph |
| `touches` | which places the mark writes: its own, or an origin and a destination |
| `sets` | the text the mark puts at a touched place, from the mark and the base; *unchanged* for a mark that proposes no text |
| `pairs` | how it combines with another mark at the same place: agree, compose, contest, abstain, unsettlable |
| `answers` | which answer rows a turn may give on it |

The values the rulings already fix:

- `correct`, `patch`, `drop` set the base with the quoted clause substituted or removed,
  exactly once (`derived_change`); a drop across a line break is rewrapped to the paragraph's
  width (P6, `e4d69ded`).
- `move` touches an origin and a destination. At the origin it sets the base minus the
  snippet, removed exactly once; at the destination it sets the mark's `raw_text`, the
  paragraph as it will read with the snippet in (#172, #175). `change` is the snippet.
- `add` sets its `raw_text`, the paragraph as it will read; `change` is the added text; at
  a place holding prose, `raw_text` keeps every word of it in order (#132, #176).
- `clean` and `query` set nothing (#174).
- Agreement is the text alone, whatever instructions produced it (#88). Two proposals on
  different sentences of one base compose; on one sentence they contest. A `query` of a
  deferring shape abstains; `human-review-necessary` makes the place unsettlable.
- A destination is a `path@cue` place on a gathered page, for now (#173); a bare cue or a
  path outside the code is refused at `mark`, and the role files a human-review query
  naming it (#169).

### The answers table -- what a role says in a turn

One row per answer, keyed by the question it answers: on an escalation `hold`, `withdraw`,
`correct`, `patch`; on a composition `clean`, `query`, `correct`, `patch`. A row answers:
which question it belongs to; what it does to the role's own proposal at the place (keeps
it, removes it, replaces its text); and what it does at a move's other end -- an answer at
either end reaches the move whole (#129, #152, #153).

### The dispositions table -- what the chief rules

One row per ruling: `taken_in` (a side, or the original) and `recast` (the chief's own
prose), and `stet` when the open TODO for it lands. A row answers: which carried-forward
states it may close; what text it sets; that a move's two ends are never ruled apart (#139,
#155); what happens at an `add`'s empty place; and that an unsettlable place takes no
disposition and rides to the author (#94).

### Row discipline

Rows are frozen dataclasses in Python, not TOML, because `sets` and `pairs` are code. The
`Row` shape is declared once, in the marks table, and the other two tables use it. Today's
`_recast_as`, `_the_origin`, `_the_destination`, `_agreed_moves`, `_moved_here_twice`,
`text_at` and the branches on `Instruction.MOVE` are each a cell in one row.

## The place, and the evaluator

A place is the aggregate: its address and anchor; its base text as the page holds it; the
marks filed there, each with its role; the answers from each turn, by role; and the chief's
disposition, if any. A move contributes a mark to two places, and each records which end
it is.

The evaluator is pure: no I/O, no page, no file, no exit code. It takes a place and returns
the place decided. It runs up to three passes, one table each, in order; each narrows the
place's state, and what is still open after the last pass is what the author sees at 7a.

| state | meaning | next |
| --- | --- | --- |
| stands | every mark proposes nothing, or the one proposal is unopposed | settled on the proposal or the base |
| agreed | every proposal is one text | settled on that text |
| composed | proposals touch different sentences and compose | carried forward as a composition |
| contested | proposals on one sentence differ | carried forward as an escalation |
| unsettlable | a human-review query is present | rides to the author; no later pass changes it |
| refused | a mark the table cannot read | back to the role; the transaction does not commit |

A move's two places are evaluated together: both take one state, and a refusal at either
refuses both. The evaluator never reads a page, verifies a source or counts turns.
Verification runs before it, in the fold, so a mark it sees has been read, cited and
resolved.

## The Unit of Work

One fold over one stage, in `desk/`. It takes places, runs the evaluator at each, and
answers *commit with these decided places* or *roll back with these reasons*. It knows no
file and no container of the read or write end; the flow derives the places and saves the
result.

| UoW | reads | commits |
| --- | --- | --- |
| collate | the returned copies, verified first | the master proof at turn 0 |
| turn | the last proof and each role's answers | the next proof |
| disposition | the last proof and the chief's rulings | the closed proof and the chief's copy |
| mark | one copy and one ruling | the copy with the ruling placed |

A commit requires every place to have a state and no move to be half done. A rollback
writes nothing, and its reasons are the report.

## The bus

The stage transitions are messages, each with one handler in `flows/` that opens the
matching Unit of Work: copies returned, answers returned, dispositions written. A handler
loads the copies or the proof from disk, derives the places, hands them to desk, and on
commit saves the proof or the chief's copy. It emits events -- a place refused, a place
carried forward, a place unsettlable, a copy that could not be read -- and the commands
print from the events and derive their exit code from them. The bus is in-process and
synchronous: a list of handlers, not infrastructure.

`commands/collate.py`, `turn.py` and `disposition.py` become parse, send, print, exit. The
result object with five lists, the hand-written `Revisit` loops and the exit-code precedence
spelled twice go with them.

## The ends

The middle touches no files. Its two boundaries do, and both read the marks table:

- In: `mark` and `flows/fill.py`. A ruling is placed only if its row can read it: the
  derived change, the snippet once in the origin, the destination text keeping every word,
  a `path@cue` destination. `mark --withdraw` stays (P5, `1a4d7cfc`). `check` runs the
  fold's first half without the commit, so it refuses what the fold refuses (P3,
  `42987afd`).
- Out: `transcribe.docket_of`. One alteration per place whose decided text differs from
  the base, read from the decided places rather than from marks. `text_at` goes, and with
  it "an empty change is a delete". A move gives the origin its remainder and the
  destination its `raw_text`. The write end's refusal of two alterations at one place (P2,
  `4a3ccf8b`) stays as depth.
- Verification -- `collator.py`'s source half, `drift_in`, resolution -- is unchanged and
  runs before the evaluator. Drift skips a mark whose row says its `raw_text` is the
  destination text.

## Layout

```
desk/
  marks/           the marks table and what a mark is
    mark.py          Mark, seed/serialize/deserialize, derived_change
    table.py         the seven rows, and the Row shape the other two tables share
  answers/         what a role says in a turn
    answer.py        the answer container (today's DiffMark)
    table.py         the eight rows
  dispositions/    what the chief rules
    disposition.py   the ruling container
    table.py         taken_in, recast, later stet
  evaluate/        the place, decided
    place.py         Place: address, anchor, base, marks, answers, disposition, state
    passes.py        the marks, answers and dispositions passes
  work/            the Unit of Work
    fold.py          takes places, runs the passes, commits or rolls back
    events.py        the events a fold emits
  containers.py    EditCopy, Sheet, MasterProof (unchanged)
  collator.py      source verification and drift only, once reconciliation leaves
flows/
  bus.py           the handlers, one per stage message
  ...              gather, distribute, fill, transcribe, revise, proof_setter as today
commands/          flat, as today
```

`scripts/release.py` copies sub-packages intact, so the shipped tree takes the same shape.
The three `table.py` modules are the only places that name a row.

## What replaces what

| old | new |
| --- | --- |
| `flows/collate.py` (fold, resolve, chief copy, move order) | `desk/evaluate/`, `desk/work/`, `flows/bus.py` |
| `flows/turn.py` (answers, refold, rule at max turns, close) | the answers and dispositions tables, the passes, the turn and disposition handlers |
| `desk/collator.py`'s reconciliation half (`places`, `_outcome`, `_join_moves`, `reconcile`) | the marks pass |
| `desk/determined.py` | the decided place |
| `desk/diff_mark.py` | `desk/answers/` |
| `desk/mark.py`'s `INSTRUCTIONS` and `text_at` | `desk/marks/table.py`; `text_at` deleted |
| `flows/transcribe.py::docket_of` over marks | `docket_of` over decided places |

## How it is measured

- The three runs are the fixture: the self-run's twelve copies and the two live runs'
  copies, checked in as test inputs, redacted where they must be. A test folds each through
  the new middle and asserts what the rulings say: the 23 destinations refused at `mark`, an
  all-clean copy drafting unchanged, every move landing whole, every place in exactly one
  state.
- Differential where the old was right: for each old test whose expectation stands, the new
  fold over the same input must agree; where the expectation was the defect, the test is
  rewritten to the ruling and the old one deleted.
- Gates: nothing outside the three table modules names a row; every field of every row is
  exercised by a place in the fixture runs; the smoke plants every row.

## The order

Each step is a unit: work and verify, commit, tick, commit.

1. The three tables under `desk/`, with the gate. The old code made to pass the gate by
   reading the tables -- the first differential: same outputs, one source.
2. The place and the evaluator, on hand-written places and on the self-run's copies; the
   old fold left in place.
3. The Unit of Work in `desk/work/`, the bus and the collate handler in `flows/`; `collate`
   switched, differential against the old on the fixture runs; the old fold made private.
4. `turn` and `disposition` switched the same way; the old `turn.py` made private.
5. The ends: `fill`, `docket_of` and `check` reading the tables; `text_at` deleted; #172,
   #175 and #176 landed -- the paused P7 and the add step of
   `0.2.4-the-cli-carries-a-real-run`.
6. Delete what went private and its tests. Nothing moves to `prototype/` unless a piece is
   worth keeping to read.
7. The smoke planted for every row, then the self-run again through the commands
   (`0.2.4-the-cli-carries-a-real-run` P11).

This replaces that subplan's P7 to P10 and P13; its P11 and P12 stay as the finish. It is
founded as a subplan of `0.2.4-the-cli-carries-a-real-run`, on its own branch, since that
plan's merge waits on it.

## Not in this design

- Addresses for external documents, and a move out of the code (#173 leaves them for later).
- `stet` as a disposition: the row is one cell when `no-mark-for-let-it-stand` is ruled.
- The read end and the write end, beyond the two boundaries named above.
- Any change to what a role is told; the brief and the role files change only where a
  command's contract changes (`mark --withdraw`, the destination form).

## Provisional

The single-`Mark` move, the three states a place may be carried forward in, and the answer
and disposition vocabularies are as ruled to date and no further. Roy, 2026-09-02, on an
earlier attempt to enumerate how a shape fails: *"it could fail any number of ways and
acting like it you can come up with a closed set of failure modes is silly."* What this
design fixes is where a new case goes -- one row -- not what the cases are.
