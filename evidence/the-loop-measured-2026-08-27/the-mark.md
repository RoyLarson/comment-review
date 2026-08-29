# The shape of a mark

!! **THE SHAPE NOW HAS AN OWNING FILE: [`docs/the-mark.md`](../../docs/the-mark.md), added
2026-08-28.** Read that for the requirement as it stands. **This file is unchanged below and stays
that way** -- it records what the four rounds RAN against, which is why it still names the old
`query` shapes.

! **AND THE SENTENCE BELOW NAMING `record.py` AS A SOURCE IS SUPERSEDED**, not edited. Roy,
2026-08-28: *"Why are you talking about code in `prototype/original/`? And fixing things based upon
something in there?"* `prototype/` is a record of how it once worked; it defines nothing. **Taking
it as a source is what put a classifier scheme into `src/` that had never been proposed** -- the
history is in `docs/the-mark.md`.

Two sources, kept apart: what `prototype/original/record.py` and the shipped `reviewer-brief.md`
already encoded, and what these four rounds measured.

!! **THIS IS A SNAPSHOT OF THE SHAPE THESE ROUNDS RAN AGAINST. IT IS NOT THE SOURCE.** The shape
is defined in `reviewer-brief.md` and `record.py`; a rule belongs in exactly one file and this is
not that file. It is recorded here because a mark cannot be read without it, and it keeps the
form that was current on 2026-08-27 -- the same rule [`../README.md`](../README.md) states for
every captured run in this directory: *renaming inside a captured run would make it describe
something that never happened.*

! **Where a ruling has SUPERSEDED part of it since, that is marked in place** rather than
rewritten away.

## The fields

| field | what it is | who fills it |
| --- | --- | --- |
| `address` | `path@cue`. WHICH PLACE | **seeded** -- copied from the row, never built |
| `anchor` | the line of code the place sits on | seeded |
| `mark` | one of the seven | the role |
| `claim` | the surgical spec -- structured keys, per verdict | the role |
| `reason` | WHY. The evidence, in prose. No checker settles it | the role |
| `sources` | `{cite, verbatim, ran}` | the role |
| `change` | the RESULT: an ARRAY of file-ready lines | the role |

! **`claim` IS THE SPEC AND `change` IS THE RESULT.** Roy, 2026-08-17: *"the change is what allows
the apply section to apply the claim appropriately."* Every check that reads the ORIGINAL sentence
reads it out of `claim`; `change` is a whole paragraph and no sentence can be parsed back out of
it.

! **THE ORDER IS A CHAIN OF CUSTODY.** Roy, 2026-08-17: *"Verdict -> Claim -> REASON -> SOURCES ->
CHANGE ... a clear chain of custody on the reasoning and the required actions."*

## What each verdict owes

Defaults: a verdict owes `claim`, `reason`, `change`, `address`, `sources`, and is substantive and
diffable, unless a row says otherwise.

| verdict | `claim` carries | verbatim | `change` | `sources` | other |
| --- | --- | --- | --- | --- | --- |
| `clean` | -- | -- | no | no | not substantive. The NULL verdict, and the coverage record |
| `query` | one of THREE shapes | -- | no | **yes** | needs `attempted` + `settles`; may declare scope |
| `drop` | `drop:` | `drop:` | yes | yes | an empty change IS the edit where the claim names the whole paragraph |
| `correct` | `false:` + `true:` | `false:` | yes | yes | rules on text |
| `patch` | `from:` + `to:` | `from:` | yes | **NO** | wording alone -- nothing outside the paragraph settles it |
| `add` | `missing:` | -- | yes | yes | needs an ANCHOR in the claim; not diffable |
| `move` | `from:` + `to:` | -- | yes, showing BOTH | yes | the `to:` must be ADDRESSABLE |

### The three `query` shapes

**REPLACED SINCE THESE ROUNDS RAN.** They were `outside my role`, `outside the checkout`,
`outside the code`; `decision-log.md Process: #33` re-keyed them on WHO RESOLVES IT --
`outside-my-role`, `unable-to-determine`, `human-review-necessary`. **The rounds in this package
were run against the OLD set**, which is why `query` appears 56 times in each full round.

! The scope-declaring shape is a BOUNDARY REPORT and not work, and it survived the re-keying
unchanged.

### `move`'s destination: ADDRESSABLE, not CARRIED

Roy, 2026-08-27: *"the destination needs to be addressable not necessarily in the binder. That
includes an external_address-able item."* Three legal destinations:

    a place the binder carries      resolves today
    a place it does NOT carry       an EMPTY place -- addressable by the walk, cut from the
                                    binder, citable via `carry`
    an external address             a coordinate in a file this system does not SET

!! **WHAT THE CODE ENFORCED DURING THESE ROUNDS WAS NARROWER**, and two consequences were
measured: a `move` into an empty place was REFUSED, the same wall `add` hit; and an external
destination was allowed by FALLING THROUGH rather than by being recognised, so *legitimately
external* and *malformed* were indistinguishable.

! **The binder's sections answer the first.** A page taken from the library mid-run goes in
`pulled`, a document in `references` -- `decision-log.md Vocabulary: #16`, `Process: #32`.

### The one contradiction the set can express

`drop` against `correct` or `patch` **on the same sentence**. That is a re-review. ! `move` is
deliberately neither: relocation and a truth-fix compose.

## What these rounds changed

**`change` IS AN ARRAY OF LINES, NOT A STRING.** MEASURED: a role returned a 3-line update for a
48-line paragraph, and another returned a different paragraph with its comment markers gone,
which would have made the file unparseable. Both are hand-transcription failures.

**`sources` ARE `{cite, verbatim}` PAIRS**, so a joiner can confirm each verbatim string sits
within three lines of its cited line. Strings are not checkable the same way.

**`ran` -- A SOURCE FOR A CLAIM SETTLED BY RUNNING SOMETHING MUST CARRY THE COMMAND.** The only
field these rounds added, and it is at zero uses in the data: one role's first pass ran on
ambient Python 3.14 instead of the pinned 3.11 floor and produced a false negative caught only by
re-running. `sources` records WHAT was seen and never HOW it was obtained.

    {"cite": "...:247", "verbatim": "    pass", "ran": "uv run python -c \"...\""}

**`claim`'s PARTS ARE SEPARATE KEYS, NOT ONE STRING.** The `false` clause is checked VERBATIM
against the paragraph; flattened, a paraphrase and a quote look the same to whatever reads the
file.

**`address` IS COPIED, NEVER BUILT, AND ALWAYS FULLY QUALIFIED.** Measured twice -- see
[`measurements.md`](measurements.md), *The address form*. The row already carries `address`;
`binder.rows_of` composes it with `address_for`, the single producer.

## What these rounds left unsettled

**Recording the WORK rather than the conclusion.** Four roles asked for it in four forms --
*enumerated it and it is true*, *read hard and nearly marked it*, *checked internal consistency
only*, *could have re-run it and did not*. All land as `clean`, which asserts one thing and was
used for four.

! **NOT A NEW VERDICT.** Roy, 2026-08-26: *"the word list we used was the words required else they
start inventing words."* If it is anything it is a field on `clean`.

**A finding whose subject is the RELATION between two places** was recorded here as
unexpressible. ! **THAT WAS WRONG and is superseded** -- Roy, 2026-08-27: *"one or both sides get
a correct or query with a reason / The reason says this contradicts that / Along with the sources
pointing at the 'that'."* Two roles produced exactly that shape unprompted. What remains is a
`collate` defect, not a shape one:
[`collate-buckets-a-move-at-one-end`](../../TODO/collate-buckets-a-move-at-one-end.md).
