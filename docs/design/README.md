# Design -- what each piece IS, how it works, and why it is that way

!! **DRAFT, 2026-09-02. The layout and the rule below want Roy's approval before
nine package files are written under them.** Nothing has moved yet.

## The gap this fills, and it is measured

Roy, 2026-09-02: *"we are missing a good place for design documentation ... Some
of the history and decision-log are helpful but what and how things are supposed
to work and what things are what and why is not well done right now."*

Three kinds of knowledge, and until now only two had a home:

| the question | where it lives |
| --- | --- |
| **WHAT was decided, and WHEN** | [`decision-log.md`](../decision-log.md) -- the dated chain of rulings, retractions and supersessions |
| **What the system USED TO do** | [`history.md`](../history.md) -- a retired format or mechanism, with the commit that removed it |
| **How it works NOW, and why** | **here** |

!! **WITH NO THIRD HOME, THAT KNOWLEDGE LANDED IN THREE BAD PLACES**, and each
was measured on 2026-09-02:

| where it went | what it cost |
| --- | --- |
| **a commit message** | a determination that a `move` is provisionally ONE `Mark` was made *"yesterday or the day before"* and written nowhere; a cross-TODO sweep then reported it as the board's largest live conflict |
| **a module docstring** | Roy's ruling that *"which role set a place is answered by which copy was pulled from"* exists only at `docket/docket.py:91-96`. A `[?]` in his own queue still asks the question it answers |
| **a TODO Objective** | `desk/mark.py`'s `Row` justified its own name by citing `docs/the-mark.md`'s *"seven row flags"* -- prose using a word, offered as authority for taking it |

! **AND THE DECISION LOG CANNOT ABSORB THIS.** It records that a thing was
decided; it has no place to say how the piece works, so a correction lands as an
entry while the boxes and the code go on saying the opposite. `Process: #79` is
that failure written down.

## The rule

**One folder per package under `src/comment_review/`, and each file is the SOURCE
for its subject.** A design statement lives in exactly one place; everywhere else
cites it.

!! **EVERY SENTENCE MUST BE FALSIFIABLE BY READING THE CODE.** The same standard
`CLAUDE.md` sets for a comment applies here and is the only thing that keeps
these files honest: *"if a sentence cannot be falsified by reading the code or
re-running a command, it does not belong."* No "robust", no "clean design", no
claim a reader cannot check.

!! **WHERE THE DOC AND THE CODE DISAGREE, ONE OF THEM IS A DEFECT AND THE DOC
SAYS WHICH.** That is the whole point of writing the intent down: a comment that
merely describes what the code does cannot disagree with it, and so can never
catch anything.

! **A design doc is not a plan and not a task.** It says what IS and why. What
should CHANGE is a `TODO/`; what one release does about it is a `docs/plans/`
entry.

! **PROVISIONAL IS SAID OUT LOUD, AND NAMES ITS PREMISES.** Where a shape is not
settled, the doc states what it rests on rather than a list of ways it might
fail. Roy, 2026-09-02: *"it could fail any number of ways and acting like it you
can come up with a closed set of failure modes is silly."* See
[`the-mark.md`](../the-mark.md)'s move section for the worked form.

## The layout

    docs/design/
      README.md        this file -- the rule
      machine/         the floor: constants, exceptions, json_object, repo
      reading/         addresser, language, lexer, paragraph, series
      binder/          addresses, binder, page
      concordance/     annotate, code_names, names, referrers
      desk/            collator, containers, external_address, mark, proof,
                       stages, topology
      docket/          docket
      results/         compositor, differences, galley, prove_unchanged
      flows/           carry, census, collate, distribute, fan_out, mark_errors,
                       page_for, proof_setter, revise, transcribe
      commands/        every main() and its argparse

! **THE ORDER IS THE DEPENDENCY ORDER**, which `docs/conventions.md` already
rules: `machine`, `reading` and `concordance` are LEAVES; `binder` is the READ
END; `desk` is the MIDDLE; `docket` and `results` are the WRITE END; `flows` and
`commands` are neither and run the steps.

## What a package file holds

A `<package>/README.md` answers, in this order:

1. **What this package is for** -- one sentence a stranger can check.
2. **What it may import, and what may import it** -- its area, from
   `conventions.md`'s table.
3. **Each module: what it owns.** One subject per module, which is what
   `module-context` asks of any module.
4. **The shapes it defines** -- the types, and what each field is FOR.
5. **Why it is this way** -- the constraints that produced the design, each
   citing the `decision-log.md` entry that ruled it.
6. **What is provisional**, with its premises.

## What moves in, and it needs a ruling

Three files already do this job and prove the pattern:

| file | is the SOURCE for | would live at |
| --- | --- | --- |
| [`the-mark.md`](../the-mark.md) | the mark's fields and classifiers | `desk/` |
| [`the-revise.md`](../the-revise.md) | what a ROUND is, what closes the roles | `flows/` |
| [`addressing.md`](../addressing.md) | how a place is NAMED | `reading/` |

!! **MOVING THEM BREAKS CITATIONS, AND THAT IS THE DECISION.** `docs/lanes.md`
names two of them as SOURCEs by path, and `decision-log.md`, `CLAUDE.md` and the
TODO board cite all three by path many times over. **Two options, and neither is
free:**

- **Leave them and link.** No citation breaks; the design docs are then in two
  places and a reader must know both.
- **Move them and repoint.** One home; every citation is a one-for-one path swap,
  which `conventions.md` permits without a lane crossing -- but it is a sweep,
  and a missed one is a dead link.

! `parsing.md`, `gates.md`, `limitations.md` and `vocabulary.md` are NOT design
docs in this sense and do not move: they describe where structure could come
from, whether a check bites, how the skill's own prose is changed, and what the
words mean.

## Owner

`backend` owns `src/comment_review/**`, so it owns these -- with the standing
exception that the vocabulary belongs to no lane and any lane may correct it.
`docs/lanes.md` would gain a row.

## What this does not solve

! **A design doc goes stale exactly like a comment does**, and nothing here
gates it. `check_vocabulary.py` sees retired words and `dead_sweep.py` sees names
nothing reads; neither can tell whether a paragraph describing a mechanism still
describes it. **The one thing that has ever caught this class in this repo is a
reader** -- which is what the four editorial roles are for, and these files are
in their remit the moment they exist.
