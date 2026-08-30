# The mark -- the shape, and the classifiers that are allowed to exist

!! **THIS FILE IS THE SOURCE.** A mark's fields, and the classifiers that decide what each
instruction owes, are stated HERE and nowhere else. `desk/mark.py` implements this file;
`reviewer-brief.md` publishes it to a role. **Neither of them defines it.**

!! **IT EXISTS BECAUSE THE SHAPE HAD NO OWNING FILE, AND SOMETHING ELSE BECAME THE SPEC.**
Roy, 2026-08-28: *"None of those were part of the accepted shape of the mark structure or any part
of the plan ... We had a specific plan for the mark structure and the appropriate classifiers for
each part. I don't know where these came from or why"*, and: *"That is the shape that I approved
going into this plan. I had not knowledge of the other shape."*

! **WHAT HAPPENED, recorded so the mechanism is legible rather than the blame.** On 2026-08-28 a
session was asked whether the mark type was usable and whether it needed a CLI endpoint. It began
answering by naming `prototype/original/record.py`'s `--seed`/`--check` verbs and its validator
stack. **Roy interrupted mid-sentence**, then ruled: *"You can copy it from there and update the
rules/requirements from there but it doesn't belong in the new records.py. It belongs in the
desk/."* **The only thing on screen was the ENDPOINT and the checkers.** The `Instruction`
dataclass was never shown. The port copied it whole anyway, and a 22-field classifier scheme
entered `src/` having never been proposed.

! **THE CONTENT BELOW IS THE SHAPE MEASURED OVER FOUR ROUNDS ON 2026-08-27** and captured in
[`../evidence/the-loop-measured-2026-08-27/the-mark.md`](../evidence/the-loop-measured-2026-08-27/the-mark.md).
That file stays as it is -- a snapshot of what those rounds RAN against, which is why it still
names the old `query` shapes. **This file states the requirement as it stands today**, with every
superseding ruling applied rather than annotated.

---

## The fields -- seven

| field | what it is | who fills it |
| --- | --- | --- |
| `address` | `path@cue`. WHICH PLACE | **seeded** -- copied from the row, never built |
| `anchor` | the line of code the place sits on | seeded |
| `instruction` | one of the seven | the role |
| `claim` | the surgical spec -- structured keys, per instruction | the role |
| `reason` | WHY. The evidence, in prose. No checker settles it | the role |
| `sources` | `{cite, verbatim, ran}` | the role |
| `change` | the RESULT: **the updated paragraph, as RAW TEXT** | the role |

!! **`claim` IS THE SPEC AND `change` IS THE RESULT.** Roy, 2026-08-17: *"the change is what allows
the apply section to apply the claim appropriately."* Every check that reads the ORIGINAL sentence
reads it out of `claim`; `change` is a whole paragraph and no sentence can be parsed back out of
it.

!! **`change` IS RAW TEXT -- NOT LINES, NOT SENTENCES.** Roy, 2026-08-28: *"`change` needs to be
the updated paragraph as raw text not lines or sentences. This will make it easier to diff per the
rest of the stages."*

| | |
| --- | --- |
| the seeded row carries | `raw_text` -- the paragraph as it stands, verbatim |
| the role returns | `change` -- the same paragraph as it should read |

! **THE TWO DIFF DIRECTLY, AND THAT IS THE WHOLE REASON.** Every stage downstream is a diff of one
against the other: source-verification, the `diff3` conflict where `raw_text` is the base and each
role's `change` a side, `taken_in`, and the revise. A line array has to be joined before any of
them can run, and a sentence cannot be placed at all.

!! **AND THE HOLE THIS CLOSES IS MEASURED.** Roy, 2026-08-28: *"The original had it as one sentence
to change but that did not work which is why you probably put in prose because it is a hole with
that part of the spec without it."* ! MEASURED: `move`'s row carried `change_all=("to",)` and a
`change_help` sentence -- *"move needs the DESTINATION paragraph in `change`, as `to` -- plus
`from`, the origin as it reads after"* -- and **those two fields exist for no other reason.** With
the shape unstated, a prose field was written to state it. **An underspecified column grows a prose
field to explain itself.**

! **SUPERSEDES the four rounds' "an ARRAY of file-ready lines".** That form was chosen against two
measured hand-transcription failures -- a 3-line update returned for a 48-line paragraph, and a
paragraph returned with its comment markers stripped, which would have made the file unparseable.
**Raw text does not re-open them: it makes them louder**, because the diff against `raw_text` shows
a missing marker or a truncated paragraph directly, where a line array only shows a shorter list.

!! **THE ORDER IS A CHAIN OF CUSTODY.** Roy, 2026-08-17: *"Verdict -> Claim -> REASON -> SOURCES ->
CHANGE ... a clear chain of custody on the reasoning and the required actions."*

!! **THE RULING FIELD IS `instruction`, AND THIS TABLE SPELLED IT `mark` UNTIL 2026-08-29.** Roy,
2026-08-29: *"the agent emits the 'mark', the 'instruction' was ... the action that turned the mark
into an actionable thing."* A `Mark.mark` is the self-nesting that made this ambiguous -- the enum
was already `Instruction` and `reviewer-brief.md` already published `instruction`, so this file and
`desk/mark.py` are what moved.

! **AND THE COST OF THE DISAGREEMENT WAS MEASURED BEFORE IT WAS FIXED.** `desk/mark.py` read the key
`mark` while the brief published `instruction`, and `flows/marks.py` skipped any entry whose `mark`
key was absent -- so **the brief's own worked example passed `mark --check` at exit 0, counted as a
place nobody looked at.** A reviewer following the brief produced findings that vanished in silence.
`tests/test_brief_worked_example.py` is what keeps that from returning.

## What each instruction owes

**Defaults:** an instruction owes `claim`, `reason`, `change`, `address` and `sources`, and is
substantive and diffable, **unless its row says otherwise.**

```
           claim carries    verbatim   change   sources   the row's own flags
--------------------------------------------------------------------------------------
clean      --               --         no       no        not substantive. The NULL
                                                          mark, and the coverage record
query      shape,           --         no       YES       may declare scope
           attempted,
           settles
drop       drop             drop       yes      yes       an empty change IS the edit
                                                          where the claim names the
                                                          whole paragraph
correct    false, true      false      yes      yes       rules on text
patch      from, to         from       yes      NO        wording alone -- nothing
                                                          outside the paragraph
                                                          settles it
add        missing,         --         yes      yes       not diffable. The anchor is
           anchor                                         NAMED IN BACKTICKS
move       from, to         --         the      yes       the `to` must be ADDRESSABLE
                                       COMPOSITE
```

## `move` is TWO OPERATIONS UNDER ONE LABEL, AND IT IS INDIVISIBLE

Roy, 2026-08-28: *"The move needs the composite of the delete/add paragraphs. It really is two
operations wrapped in one label and justification. Which is right -- you don't want to say it can
move and it can't complete the move because 1/2 is rejected."*

**`change` carries the COMPOSITE**: the origin as it reads once the prose has left, and the
destination as it reads once the prose arrives. Both raw text, in one `change`.

    a move  =  a delete at the origin  +  an add at the destination
               one label, one reason, one `sources`

!! **AND THE REASON IT IS ONE INSTRUCTION IS ATOMICITY, NOT TIDINESS.** Filed as a `drop` and an
`add`, the two halves can be judged separately -- and **half a move is a defect neither half
reports**: prose deleted from a place and never landed, or landed and never removed, so the file
now says it twice. **Nothing downstream would know the pair was meant to be one thing.**

**What that binds, everywhere the mark is handled:**

| stage | the rule |
| --- | --- |
| **source-verification** | both ends are checked; a failure at either refuses the mark |
| **reconciliation** | a `move` escalated at EITHER place escalates WHOLE. It may not be settled at one end and escalated at the other |
| **the revise step** | a role answering a `move` answers for both ends. There is no half `hold` |
| **the write chain** | both paragraphs are set, or neither is |

! **THIS IS WHAT [`collate-buckets-a-move-at-one-end`](../TODO/collate-buckets-a-move-at-one-end.md)
IS ABOUT**, and it is now a rule rather than a bug report: a `move` is grouped by every place it
TOUCHES, because being seen at only one of them is how half of it gets settled.

! **It does not change what a `move` COMPOSES with.** Relocation and a truth-fix are still
compatible -- see *The one contradiction the set can express*, below. Indivisible means its own two
halves travel together, not that it conflicts with everything.

## What each `claim` carries, in the role's own terms

!! **THIS IS THE PROSE A ROLE READS, AND IT IS WRITTEN BY A HUMAN, HERE.** It is what
`reviewer-brief.md`'s generated table publishes in its third column. **It is not derived from the
keys, and no row in the code carries it** -- Roy, 2026-08-28: *"What finishes can be put into the
instruction set and the cli help."* This file is the instruction set.

| instruction | what the `claim` carries |
| --- | --- |
| `clean` | nothing. Name your role and stop -- `clean` proposes no text, so there is nothing for the apply step to apply |
| `query` | the SHAPE in these exact words, the check you ATTEMPTED, and what WOULD settle it. All three are checked as SHAPE and none as truth; the claim itself is checked by nothing, so the other three are all that stands behind the ruling |
| `drop` | the sentence, verbatim, as it stands in the paragraph. ! It is CHECKED against the page, so a paraphrase is refused |
| `correct` | the false clause and the true one, and a `sources` entry carrying the line that settles it. ! The FALSE half is checked against the paragraph -- if it is not there, the finding is on the wrong one |
| `patch` | the sentence as it stands and the rewrite. ! `from` is checked against the paragraph. A `patch` needs no source: the claim is already true, and only its wording is at issue |
| `add` | the text that is missing and the anchor NAMED IN BACKTICKS. ! The word "anchor" is not an anchor -- name the declaration. Which SIDE is the address's to say, never the claim's |
| `move` | where the prose sits now and where it belongs -- another line, another file, or out of the code entirely. ! These are PLACES, not text: the same two key names in `change` mean the resulting PARAGRAPHS |

!! **IT WAS LOST ONCE ALREADY, ON 2026-08-28, AND THE MECHANISM IS WORTH KNOWING.** This prose used
to live in a `payload` field on each row. Deleting that field was right -- a row carries no prose --
but the text had **no other home**, so the brief's generator was pointed at this file's *flags*
column instead and published `"rules on text"` where a role had been reading *"the false clause and
the true one, and a `sources` entry carrying the line that settles it."*

! **DELETING A FIELD DOES NOT DELETE WHAT IT HELD.** The content has to land somewhere first, or
the next thing that reads it silently gets a worse answer. ! `add`'s sentence ended *"never the
payload's"* and now reads *"never the claim's"*: the old word named the field that was removed.

## The classifiers -- FOUR COLUMNS AND A CLOSED LIST OF FLAGS

!! **THIS IS THE PART THAT WAS MISSING, AND ITS ABSENCE IS WHAT LET TWENTY-TWO FIELDS IN.** A row
may state these and nothing else -- **eleven things, and no prose.** A new classifier is a change
to THIS FILE first.

| classifier | what it decides | shape |
| --- | --- | --- |
| **claim keys** | every key `claim` must carry, in one list | a list of names |
| **verbatim** | which ONE claim key is checked word-for-word against the paragraph | a name, or none |
| **change** | whether a change is owed, and for `move` that it shows both ends | owed / not owed |
| **sources** | whether sources are owed | owed / not owed |

**The flags, and there are seven:**

    not substantive        clean alone. It is the NULL mark and the coverage record
    may declare scope      query alone. A boundary report is not work and must not block
                           the other roles
    empty change allowed   drop alone, where the claim names the whole paragraph
    rules on text          correct and patch. The two that propose wording
    not diffable           add alone. There is no original to diff against
    anchor named in backticks   add alone, and it is a FORM check on `claim.anchor`
    destination addressable     move alone

!! **A ROW CARRIES NO PROSE. THE EXPLANATION LIVES IN THE INSTRUCTION SET AND THE CLI HELP.**
Roy, 2026-08-28: *"What finishes can be put into the instruction set and the cli help. I forbid
you from including anything like this in the code right now."*

! **AND THAT FORBIDS THE MACHINERY, NOT ONLY THE FIELD.** A session proposed deleting the two
prose fields and GENERATING their sentences from the claim-keys list instead. That is the same
mistake wearing a different hat: it puts prose-building in the code to avoid storing prose in the
code. **Neither the string nor the generator belongs there.**

| what | where it lives |
| --- | --- |
| what an instruction's `claim` carries, in prose | **this file**, and `reviewer-brief.md`, which publishes it |
| what a role reads when a claim is refused | the **CLI help** |
| the KEYS themselves | the claim-keys column above -- the one place they are stated |

! **A ROW STATES A FACT ONCE.** `query` owes the keys `shape`, `attempted` and `settles` -- that is
ONE list in the claim-keys column, not a list plus two booleans that a function reassembles.
**Writing a fact twice is what allowed half of it to be dropped in a port while the other half
stayed**, and the two then disagreed with nothing able to notice.

## The three `query` shapes

`decision-log.md Process: #33`, keyed on **WHO RESOLVES IT** and not on where the evidence lives:

| shape | what it says |
| --- | --- |
| `outside-my-role` | deferred to another agent's problem |
| `unable-to-determine` | *"don't know why but maybe another agent figured it out"* |
| `human-review-necessary` | *"genuinely contradictory statements and/or code and only system level intent might disambiguate it"* |

! **The scope-declaring shape is `outside-my-role`**, it is a BOUNDARY REPORT rather than work, and
it survived the re-keying unchanged. ! MEASURED: treating a scope declaration as a question let one
role veto three others and the docket fell from 12 alterations to 5.

! **The set these rounds ran against was `outside my role` / `outside the checkout` / `outside the
code`.** That is why the captured package reads differently; do not reconcile it.

## `move`'s destination: ADDRESSABLE, not CARRIED

Roy, 2026-08-27: *"the destination needs to be addressable not necessarily in the binder. That
includes an external_address-able item."* **Three legal destinations:**

    a place the binder carries      resolves today
    a place it does NOT carry       an EMPTY place -- addressable by the walk, cut from the
                                    binder, citable via `carry`
    an external address             a coordinate in a file this system does not SET

! **WHAT THE CODE ENFORCED WAS NARROWER, and two consequences were measured**: a `move` into an
empty place was REFUSED, the same wall `add` hit; and an external destination was allowed by
FALLING THROUGH rather than by being recognised, so *legitimately external* and *malformed* were
indistinguishable.

## The one contradiction the set can express

**`drop` against `correct` or `patch`, on the same sentence.** That is a revise.

! **`move` is deliberately neither**: relocation and a truth-fix compose.

## Requirements the four rounds established

- **THE TWO HAND-TRANSCRIPTION FAILURES.** MEASURED: a role returned a 3-line update for a 48-line
  paragraph, and another returned a paragraph with its comment markers gone, which would have made
  the file unparseable. ! **These produced the "array of lines" form, which is SUPERSEDED** by the
  raw-text ruling above -- see it for why raw text makes both failures louder rather than
  re-opening them.
- **`sources` ARE `{cite, verbatim}` PAIRS**, so a checker can confirm each verbatim string sits
  within three lines of its cited line. Strings are not checkable the same way.
- **`ran` -- A CLAIM SETTLED BY RUNNING SOMETHING MUST CARRY THE COMMAND.** One role's first pass
  ran on ambient Python 3.14 instead of the pinned 3.11 floor and produced a false negative caught
  only by re-running. `sources` records WHAT was seen; `ran` records HOW.
- **`claim`'s PARTS ARE SEPARATE KEYS, NOT ONE STRING.** The `false` clause is checked VERBATIM
  against the paragraph; flattened, a paraphrase and a quote look the same to whatever reads it.
- **`address` IS COPIED, NEVER BUILT, AND ALWAYS FULLY QUALIFIED.** MEASURED twice: with a one-file
  binder, 62 of 78 marks wrote a bare cue despite the row carrying the full address, and a bare cue
  collides on merge -- `a0` then means four different places.

## Open, and NOT a new instruction

**Recording the WORK rather than the conclusion.** Four roles asked for it in four forms --
*enumerated it and it is true*, *read hard and nearly marked it*, *checked internal consistency
only*, *could have re-run it and did not*. All land as `clean`, which asserts one thing and was
used for four.

! **NOT AN EIGHTH INSTRUCTION.** Roy, 2026-08-26: *"the word list we used was the words required
else they start inventing words."* **If it is anything, it is a field on `clean`.**
