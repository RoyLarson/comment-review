# SP-1 -- the containers and the collate flow

The first subplan under [`docs/plans/0.2.4-the-commands-for-the-middle.md`](../../plans/0.2.4-the-commands-for-the-middle.md).
**That plan is the scope and the requirements.** This file designs ten of its steps and
nothing else.

```
Plan:     docs/plans/0.2.4-the-commands-for-the-middle.md
Steps:    P36, P34, P35, P21, P13, P1, P2, P24, P3, P37
Closes:   TODO/no-command-for-the-middle.md T1, T2, T3
Lane:     backend
Branch:   feat/the-mark-and-the-collator
Raised:   2026-08-30
```

## What SP-1 delivers

**A clean forward run from a stage's returned `edit_copies` to the copy chief's own
`edit_copy` and a report, stopping at the first place that needs a person.**

    census --json --out          a binder                        COMMAND (exists)
    distribute --seed            N places for one role           COMMAND (renamed here)
    the reviewer agent           marks over those places         AGENT
    collate                      the chief's edit_copy, and      COMMAND (NEW)
                                 what it could not resolve
    proof --docket               a revise                        COMMAND (exists)

! **THE MIDDLE HAS NO COMMAND TODAY.** `gather`, `places`, `reconcile` and `docket_from`
are built and tested and nothing exposes them, so the 2026-08-29 end-to-end run drove
them from a hand-written script.

## Scope

| step | delivers |
| --- | --- |
| `P36` | `desk/collator.py`'s prose states only what the code can be checked against |
| `P34` | `Mark` carries `raw_text` as a seeded field |
| `P35` | `Mark.seed` builds the seeded row from `Mark`'s own field names |
| `P21` | `desk/containers.py` -- `Sheet`, `EditCopy`, `MasterProof` |
| `P13` | the COMPOSE -- two edits on disjoint spans merged, overlapping spans refused |
| `P1` | `flows/collate.py` -- one flow: check, gather, reconcile, resolve |
| `P2` | the automatic resolutions inside that flow |
| `P24` | `unruled`, `problems_in` and `tally` move to the collator |
| `P3` | the `collate` command |
| `P37` | `flows/marks.py` becomes the DISTRIBUTE flow, and the command follows |

### Two changes to the plan's own SP table, both ruled 2026-08-30

!! **`P24` MOVES IN FROM SP-2.** `decision-log.md Process: #54` says *"THE MOVE LANDS
WITH THE FLOW, NOT BEFORE IT ... `mark --check` reaches these through
`flows/collate.py`"* -- and SP-1 is where that flow is built. Landing `P24` in SP-2
instead would have SP-1 ship `P37`'s clause *"seed and the shape verbs reach commands
through the renamed flow"* one plan before `P24` makes it false.

!! **`P22` MOVES OUT TO SP-6.** Its verify -- *"no command reports only a count the way
`mark --check` does today"* -- is a rule for every middle command, and SP-1 builds one.
! **THE CONSEQUENCE IS STATED RATHER THAN HIDDEN:** `collate` ships in SP-1 with the
three buckets `P3` requires and WITHOUT the *"and here is the command that continues
it"* line `Process: #51` requires. SP-6 adds it. **The report is structured so that line
is an addition and not a rewrite** -- the buckets are computed and returned by the flow,
and the command formats them, so a continuation line is one more formatted line over
data the flow already returns.

## Not in scope

| | where it lives |
| --- | --- |
| the copy-chief AGENT | 0.2.5 -- `Process: #42`. In 0.2.4 the task agent is the chief |
| the chief's three acts -- `taken_in`, `stet`, `recast` | `P14`, SP-4 |
| the `docket` command, and `docket_from` taking one argument | `P4`, `P5`, SP-4 |
| the diff-mark, the `diff3` payload, the revise round | `P6`, `P8`, `P12`, `P18`, `P19`, SP-5 |
| the topology VERIFY and BUILD | `P29`-`P33`, SP-3 |
| STAGE, SHARD and ADDRESS coverage | `P26`, `P27`, `P28`, SP-2 |
| wiring source-verification into production | `P25`, SP-2 |
| the continuation line every command ends with | `P22`, SP-6 |
| sequencing, the gates, `SKILL.md`, the log | `P9`, `P10`, `P11`, SP-6 |

! **SP-1 BUILDS THE FLOW SP-2's COVERAGE CHECKS NEED AND WIRES NONE OF THEM.**
`collate` is the first thing that sees a whole stage at once, which is why `Process: #54`
puts them there; they are a separate plan because each is its own question about what
was RETURNED, and `P25`'s five verification functions are unwired today rather than
unwritten.

## Decisions taken

### D1 -- the automatic resolutions sit DOWNSTREAM of `reconcile`

`desk.collator.Reconciled` keeps exactly three lists and stays the INTERMEDIATE
`decision-log.md Vocabulary: #30` already names it. `flows/collate.py` runs `reconcile`
and then resolves over its output. `desk/collator.py` gains no fourth bucket and
`reconcile` promotes nothing.

! **A PROPOSAL TO RESOLVE INSIDE `reconcile` IS STRUCK.** It would make `settled` mean
*"has one answer"* rather than *"one role owed a change"*, and `P2` and `P13` would lose
a separate home -- so the two things a stranger most needs to tell apart, what the roles
said and what the machine did with it, would be computed in one pass.

### D2 -- no `rounds` field on the container

`Vocabulary: #30` proposed `{"rounds": {"m.py@b1": {"composition": 1, "conflict": 0}}}`
on the chief's copy. **`P7` is superseded by `Process: #51`**, which struck carried round
state as guarding an accident that cannot happen -- nothing advances a round but a
command someone invokes. A field nothing reads is the decoration `P21`'s own verify
forbids.

### D3 -- the compose lives in `results/differences.py`

Beside `diff3`, sharing `_conflict_spans`, `_touching_roles` and `_side_slice`. It is
arithmetic over text using machinery that already exists, and `Vocabulary: #53` rules
that *"making the design fit to `collator.py` is not the way."*

### D4 -- an unresolved place is ABSENT from the chief's copy, not untouched

`desk.mark.untouched` means **nobody wrote here** -- a coverage gap. A place two roles
wrote on that nothing resolved is a different fact, and writing it as an untouched slot
would give one shape two meanings. The chief's copy carries one mark per RESOLVED place;
what did not resolve rides beside it in the flow's return.

### D5 -- the per-copy check becomes `collate`'s FIRST ACT

`mark --check` disappears. `collate` checks every `edit_copy` handed to it before
gathering -- `problems_in` and `unruled` per copy -- and refuses if any is malformed.

! **IT CANNOT BE SKIPPED AND IT COULD BE BEFORE.** `places()` already raises
`MalformedMark` on an entry `parse` refuses, so a malformed copy could never be folded;
what a separate command added was the chance to run the fold without ever having run the
check. ! **THE COST IS NAMED:** a role can no longer validate its own returned copy
alone -- the whole stage's copies must be in hand. No caller does that today.

### D6 -- exit codes extend the existing convention

`commands/mark.py` uses `0` ok, `1` a rule broken, `2` an input could not be read.
`collate` keeps all three and adds two, **strongest first, matching `OUTCOMES`' own
precedence**:

| code | means |
| --- | --- |
| `0` | every place resolved; nothing carried forward |
| `1` | a copy broke a rule, or the proof could not be reconciled |
| `2` | an input could not be read |
| `3` | re-reads remain, and no escalations |
| `4` | escalations remain |

This is `A-T3` -- *"a stage that settles everything, one that escalates, and one that
owes a re-read are distinguishable by exit code alone."*

### D7 -- a composed place carries a synthesized `correct`

**The mark written onto the chief's copy for a composed place is a `correct` whose
`claim.false` is the whole `raw_text` and whose `change` is the composed text.** That
parses, and it is TRUE: the whole paragraph is being replaced. `reason` names the
compose and both roles; `sources` is both sides' sources in role order.

!! **AND THE COMPOSE IS REFUSED WHERE THE TWO SIDES' INSTRUCTIONS DIFFER**, so no mark
on the chief's copy ever carries an instruction invented over two that disagreed. A
refused compose is carried forward as a re-read, the same as an overlapping one.

! **`set_by` IS NOT ADDED TO `Mark`.** `P13` observes that a composition *"was set by
BOTH roles -- which `set_by` can carry"*; `set_by` today is `flows/revise.py`'s
per-place provenance on `Pulled`, not a mark field. Attribution rides in `reason` here,
and what the DOCKET says about who set a page is `P4`'s question in SP-4 -- `docket_from`
already drops `role` from a page two roles settled on.

! **THIS IS THE ASSUMPTION MOST LIKELY TO BE OVERTURNED**, and it is written here rather
than discovered in the code so that overturning it costs one edit.

### D8 -- an auto-resolution must re-pair `move`s

`_join_moves` gives both ends of a `move` one outcome, because a `move` is one
instruction at two places -- a delete at the origin and a write at the destination.
**An auto-resolution that promoted one end and not the other would apply half of it**:
the paragraph read twice, or deleted and never rewritten.

So: after the resolutions are computed, **a place holding a `move` is resolved only if
every place that `move` touches also resolved**; otherwise all of its ends are carried
forward. Like `_join_moves` this runs to a fixed point, because moves chain.

## The work, in order

### 1 -- `P36` -- `desk/collator.py`'s prose

**Deliver.** The module header states *"THE COLLATOR RULES ON NOTHING ... it never
judges which mark is right, never renders the composed text, and never reads a file"*
and cites `Vocabulary: #11`. `#53` rules that `#11` names the module and nothing else.
Rewrite the header to state what the module does, with no clause presented as a
constraint that `#11` does not carry.

**Verify.** `Vocabulary: #11` is cited nowhere in `collator.py` as the authority for a
behavioural constraint, and every function still in the file is named beside the step
that needs it:

| function | needed by |
| --- | --- |
| `known_addresses` | `flows/revise.py` today; `P28` (SP-2) |
| `address_problems`, `claim_verbatim_problems`, `source_problems`, `source_verification`, `verify_report` | `P25` (SP-2) |
| `places`, `reconcile` | `P1` (this plan) |
| `docket_from` | `P4` (SP-4) |
| `unruled`, `problems_in`, `tally` | `P24` (this plan) |

! **IT IS FIRST BECAUSE THE FALSE CLAIM ALREADY MISLED A SESSION** into ruling that a
compose could not live in reconciliation, citing a ruling about retired prototype code.
Building `P13` before this would shape the compose around a constraint `#53` says does
not exist.

### 2 -- `P34` -- `Mark` carries `raw_text`

**Deliver.** `raw_text` becomes `Mark`'s eighth field. `parse` admits it --
`desk/mark.py:520-522` excludes it deliberately today, and the paragraph at
`desk/mark.py:262-266` arguing it should not becomes false and is deleted.
`docs/the-mark.md`'s field table moves with the dataclass.

Consequences, all of which delete threading rather than add it:

- `claim_verbatim_problems(where, mark)` reads `mark.raw_text` instead of taking it as a
  loose third argument.
- `source_verification` drops its `raw_text` keyword.
- `verify_report` stops digging `entry.get("raw_text")` back out of the wire entry.
- `Placed` stays `(mark, role)` and carries the base for free. **No
  `Placed(mark, role, raw_text)` and no `Mark` holding a `Placed`.**

**Verify.** `tests/gates/test_mark_shape.py` passes with the field in both the table and
the dataclass and fails if either moves alone. `grep -rn "raw_text" src/` shows no
function taking it as a parameter beside a `Mark`.

! **HALF OF THIS ALREADY TRAVELS.** `seed` writes `raw_text` onto every slot
(`flows/marks.py:87`) and `docs/the-mark.md:53` says the seeded row carries it. What
drops it is `parse`. **The work is promoting a field that is already on the wire.**

### 3 -- `P35` -- `Mark.seed`

**Deliver.** `Mark.seed(address, anchor, raw_text) -> dict` builds the seeded row from
`Mark`'s own field names. It replaces the four dict literals at `flows/marks.py:82-89`.

**Verify.** Renaming a `Mark` field breaks at construction rather than leaving the
distribute flow writing the old key -- a test renames a field and asserts the failure.
The literals at `flows/marks.py:82-89` are gone, and `raw_text` rides the same round
trip as `address` and `anchor`.

! `Process: #54` makes *"did this parse back correctly"* the mark's own question. Today
only the READ half lives with the `Mark`; the WRITE half is a dict literal one layer
away.

### 4 -- `P21` -- `desk/containers.py`

**Deliver.** `Sheet`, `EditCopy` and `MasterProof` as frozen dataclasses with a boundary
parse, the way `desk/mark.py` defines `Mark`. **The wire stays dicts.** Each type gets
`parse(where, data) -> (T | None, list[str])`, matching `desk.mark.parse`'s contract, and
the flow parses at its boundary.

| type | fields |
| --- | --- |
| `Sheet` | `path`, `sha`, `marks` |
| `EditCopy` | `role`, `read_from`, `sheets` |
| `MasterProof` | `stage`, `read_from`, `edit_copies` |

**Verify.** The types are built over what `seed()` produces from a REAL tree, not a
literal. The chief's copy parses as an ordinary `EditCopy` with no second shape
(`Vocabulary: #30`). Every field declared is one the code reads -- a field nothing reads
is what let `Instruction` be an enum the wire never carried. **No `rounds`** (D2).

! **THE TYPE IS THE DEFINITION AND THERE IS NO MARKDOWN SOURCE.** `docs/the-mark.md`
exists because an agent AUTHORS a mark. **No agent ever authors a container** -- `seed`,
`fan` and `gather` build them -- so `Vocabulary: #30` puts the type in `desk/`.

### 5 -- `P13` -- the COMPOSE

**Deliver.** `compose(base: str, sides: dict[str, str]) -> str` in
`results/differences.py`, beside `diff3` and sharing its three helpers. For every merged
base span `_conflict_spans` returns:

- exactly one touching role -> splice that role's `_side_slice`
- two or more touching roles -> **REFUSE BY NAME**, naming the span and the roles

A refusal is raised, not returned as a sentinel, so a caller cannot mistake it for text.

**Verify.** Two edits on different sentences of one paragraph merge to a paragraph
carrying both. Two edits on the same sentence refuse by name rather than picking a side.
An `insert` at a span boundary is claimed by exactly one span, the way `_side_slice`
already documents.

! **`diff3` DOES NOT DO THIS.** It RENDERS -- every span at least one side edited wrapped
in a conflict span, even where only one side touched it. A compose ACTS on the
disjointness the render only shows.

! **IT NEEDS NO FIFTH ANSWER.** `hold` already says *my mark stands*, so two holds on
disjoint spans are saying it and the composition is arithmetic.

### 6 -- `P1` and `P2` -- `flows/collate.py`

**Deliver.** One flow, in this order:

```
collate(stage, edit_copies) -> Collated

  1  CHECK    problems_in and unruled over each copy   (D5)
              -> refuse if any copy breaks a rule
  2  GATHER   desk.proof.gather(stage, edit_copies)
  3  PLACE    desk.collator.places(proof)
  4  RECONCILE desk.collator.reconcile(proof)          (untouched -- D1)
  5  RESOLVE  the automatic resolutions                 (P2)
  6  FOLD     write the copy chief's edit_copy          (D4)
```

The resolutions at step 5, over `Reconciled`'s three lists:

| place | resolution |
| --- | --- |
| `settled` -- one owing mark | taken as-is |
| an `escalation` whose owing marks carry the SAME instruction and byte-identical `change` | taken as-is, role-sorted first mark |
| a `reread` whose sides `compose` | the composed text as a synthesized `correct` (D7) |
| anything else | **carried forward NAMED** |

Then D8: any place holding a `move` is resolved only if every place that `move` touches
resolved, run to a fixed point.

`Collated` returns:

```python
@dataclass(frozen=True)
class Collated:
    chief: dict                     # the copy chief's edit_copy, wire shape
    escalations: list[dict]         # carried forward: differing answers to one sentence
    rereads: list[dict]             # carried forward: a compose refused, or an `add`
                                    # -- both as `reconcile` built each entry,
                                    #    `{"address", "roles", "marks"}`
    problems: list[str]             # the per-copy check, in copy order
    unruled: dict[str, list[str]]   # role -> the addresses nobody wrote in
    tally: dict[str, dict]          # role -> instruction counts
```

The chief's copy is `{"role": "copy-chief", "read_from": ..., "sheets": [...]}`.
`read_from` comes from the master_proof. Sheets are grouped by REAL path -- an address
carries the flattened path, resolved with `unflatten` against the proof's own sheet
paths, exactly as `docket_from` does today -- and each carries that page's `sha`.

**Verify.** With the filled `edit_copies` of a stage on disk, one call produces the
chief's copy and the two carried-forward lists, and **what it cannot resolve it carries
forward named, resolving nothing on its own**. A stage whose four roles all returned
`clean` produces a chief copy with zero marks and empty carried-forward lists. A stage
with one `move` whose destination escalated carries BOTH ends forward.

! **`Vocabulary: #30`'s FOLD, ARRIVING:** *"After the chief acts every place has exactly
ONE answer."* SP-1 delivers the places that need no chief; the chief's own three acts are
`P14` in SP-4.

### 7 -- `P24` -- the shape verbs move

**Deliver.** `unruled`, `problems_in` and `tally` move from `flows/marks.py` to
`desk/collator.py`, and reach a command through `flows/collate.py` rather than by an
import of `desk/` (`Process: #12`, `Process: #54`).

**Verify.** `commands/` imports none of the three from `desk/`. `grep -rn "from
comment_review.desk" src/comment_review/commands/` names no collator function.

! **`P24`'s WORDING SAYS `commands/mark.py`, AND THE COMMAND IT NAMES IS GONE BY D5.**
The three verbs now reach `commands/collate.py` through `flows/collate.py`, which is the
routing `Process: #12` and `#54` actually require -- *a command exposes a flow*. The
command's NAME was incidental to that ruling and `P37` was already changing it.

! `desk/mark.py` cannot answer a collator question and its imports prove it -- `re`,
`dataclasses`, `enum`, and nothing else. Coverage is a question about the SET.

### 8 -- `P3` -- the `collate` command

**Deliver.** `commands/collate.py`, added to `Command`:

```
comment_review collate --stage 4c --out chief.json \
    --edit-copy a.json --edit-copy b.json --edit-copy c.json
```

! **THERE IS NO `--binder`, BECAUSE NOTHING IN SP-1 READS ONE.** `known_addresses` is
`P28`'s in SP-2, and `gather` already refuses copies that disagree with each OTHER about
`read_from`. A flag nothing reads is the same defect as a field nothing reads (D2).

stdout names the three buckets -- what resolved, what escalated, what owes a re-read --
each carried-forward place named by address and roles, never counted alone. Exit codes
per D6.

**Verify.** Closes `A-T1`, `A-T2`, `A-T3`:

- **`A-T1`** -- the chain `census -> distribute --seed -> collate -> proof` runs with no
  Python written by hand.
- **`A-T2`** -- a run that resolves 4 of 10 says what became of the other 6, by address.
- **`A-T3`** -- three runs, one resolving everything, one escalating, one owing a
  re-read, are distinguishable by exit code alone.

### 9 -- `P37` -- the rename

**Deliver.** `flows/marks.py` -> `flows/distribute.py`, and `commands/mark.py` ->
`commands/distribute.py`. The command keeps `--shape` and `--seed`; `--check` is gone
(D5). Every comment in `src/` naming `mark --check` names what the code does now.

**Verify.** No module under `flows/` is named for the artifact it carries rather than
the act it performs. `seed` reaches a command through the renamed flow. **`unruled`,
`problems_in` and `tally` do NOT** -- `P24` routes them through `flows/collate.py`, and
this is the clause of `P37` that `P24` narrows. `grep -rn "mark --check" src/` is empty.
`distribute` and `collate` read as the two halves of one round.

! **`SKILL.md` NAMES NO MIDDLE COMMAND TODAY**, which is this plan's whole premise, so
no agent-facing prose breaks and `tests/gates/test_skill_commands.py` keeps passing on
prose it already passes on. Naming the new commands there is `P10`, SP-6.

## Testing

Per `docs/lanes.md`, every test here asks *does this Python do what it says*, so all of
it is `backend`'s and lives in `tests/`.

**Inputs are derived, never literal.** `tests/README.md`'s rule: pages come from
`page_for` over real source, binders from `bind`, edit_copies from `seed`. A literal
appears only where malformed IS the input -- the per-copy check and the container
boundary parses.

| what | asks |
| --- | --- |
| `test_containers.py` | each type parses what `seed`/`gather` build over a real tree; each refuses a malformed wire value by name |
| `test_differences.py` (extended) | `compose` merges disjoint spans, refuses overlapping ones by name, and handles a boundary `insert` |
| `test_mark.py` (extended) | `raw_text` survives the round trip; `Mark.seed` breaks on a renamed field |
| `test_collate.py` | the flow over real seeded copies: each resolution, each carried-forward case, the `move` re-pairing, the chief's copy shape |
| `test_collator.py` (extended) | the three verbs still answer what they answered from their new home |

!! **AND ONE THING MUST BE PROVED ABLE TO FAIL** -- `docs/gates.md`'s rule, *"does the
check pass" is not the question; "could the check fail" is.* The compose is the exposure:
it is built from the same opcode machinery that produced the two texts it merges, so a
test that composes and then asserts the result equals one side's own edit **cannot
disagree with itself**. The composed text is asserted against prose written out in the
test, and a mutation that drops one side's slice must fail it.

## Verification of the whole

```
uv run pytest -q
uv run ruff check .
uv run ruff format .
uv run python scripts/check_shipped_syntax.py
uv run ty check src/comment_review/
uv run python scripts/build_plugin.py
uv run python scripts/build_plugin.py --check
uv run python scripts/check_vocabulary.py
```

! **`build_plugin.py` RUNS AND ITS OUTPUT IS COMMITTED.** `plugins/` is a copy of
`src/`, so a rename that does not reach it ships a stale module under a name nothing
imports.

! **`check_vocabulary.py` RUNS BECAUSE `distribute` AND `collate` ARE NEW TERMS.**
`docs/vocabulary.md` and `references/vocabulary.toml` belong to no lane and are updated
in this same change -- `docs/conventions.md`, *The vocabulary is shared, and crossing is
the point.*

## What SP-1 files rather than fixes

! Every finding gets a TODO in whatever lane owns it, per `CLAUDE.md`. Known now:

- **The chief's copy has no `set_by`** (D7). If attribution of a composed place needs to
  be machine-readable rather than prose in `reason`, that is a field question for SP-4,
  where `docket_from` already drops `role` from a page two roles settled on.
- **`collate` reports buckets and not the command that continues them** -- `P22`, SP-6,
  by this plan's own scoping.
- **Nothing checks a copy's `read_from` against the binder it was seeded from.**
  `flows/marks.py:136-141` names this gap and says the comparison *"belongs wherever the
  two meet"* -- which is `collate`, now that one exists. It is not an SP-1 step and no
  plan step covers it, so it is filed rather than slipped in.
