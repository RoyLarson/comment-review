# The master proof, and reconciliation -- design

**What this is.** The middle of the chain: what a role hands back, what holds it, and what turns
several roles' marks into one docket. It fills in P4 of
[`docs/plans/0.2.4-the-mark-and-the-collator.md`](../../plans/0.2.4-the-mark-and-the-collator.md)
and reaches back into containers P1 and P2 already built.

**The constraint it is written under.** Roy, 2026-08-28: *"the order of reviewers and revise has to
be able to be flexible in the system, from all 4 at the same time to all 4 sequentially to fanning
out block-context across many agents."* Every rule below is written so those three topologies are
the same code path.

---

## 1. The containers

```
census -> binder -> edit_copy (per role) -> master_proof -> docket -> revise
```

```
master_proof
  +-- edit_copy        one per role; one per SHARD under fan-out
        +-- sheet      one per page
              +-- mark one per place
```

| container | shape | made by | how many |
| --- | --- | --- | --- |
| `binder` | `{version, read_from, pages: [{path, sha, rows}]}` | `binder.bind` | one per stage |
| `edit_copy` | `{role, read_from, sheets: [{path, sha, marks}]}` | `flows.marks.seed` | N per stage |
| `sheet` | `{path, sha, marks: [...]}` | inside an `edit_copy` | one per page |
| `master_proof` | `{stage, read_from, edit_copies: [...]}` | reconciliation | one per stage |
| `docket` | `{pages: [{path, sha, alterations, role}]}` | reconciliation | one per stage |

!! **`master_proof` HOLDS `edit_copies`, NOT SHEETS DIRECTLY.** The level between them is the one
this design adds, and skipping it is what the earlier sketch did.

### Why the level exists

The role is handed the binder, copies the pages out of it into a binder of its own, and marks
those. That copy is the `edit_copy`. What it emits is sheets -- pages with marks -- which in a
program need carry only the marks and their addresses, because duplicating the text buys nothing.

!! **`binder` AND `docket` HAVE NO ROLES LEVEL AND THIS DOES.** One binder goes out; one docket
comes back; in between there are N marked copies, one per role. Roy, 2026-08-29: *"Each role is
handed the binder - they each emit sheets with marks on them. They are separate containers, and
calling each of them as having a `master_proof` would be incorrect."*

### `sheet` changes meaning, and the old sense is in shipped prose

`sheet` today names the PER-ROLE CONTAINER -- `flows/marks.py` opens *"Hand a role a sheet to
fill"*, and `SKILL.md` uses it nine times that way. Under this design `sheet` is the PAGE-UNIT and
the per-role container is `edit_copy`.

! **BOTH SIDES MOVE IN ONE CHANGE**, per `docs/conventions.md`'s shared-vocabulary rule.
`docs/vocabulary.md` already lists **master proof** as *"unnamed. It is what `verdicts.py`
prints"*; that row becomes named, and `edit_copy` and the two senses of `sheet` join it.

### The register is the copy desk, not the bindery

`docs/vocabulary.md` records Roy's own line: the binder is *"the binder as in a 3-ring binder full
of stuff not binder as the person who bounds books"*, and a justification that reached for the
BOOKBINDER's sense of gathering was cut there. So `gathering` and `sheaf` are out of register.
`edit_copy` sits beside `copy`, `copy desk` and `copy chief`, which is the vocabulary this system
already speaks. Roy, 2026-08-29: *"the reason I like edit_copy is because it isn't overloaded with
the other copy's it is adjacent and explicit."*

### The sheet carries the sha, and that is not decoration

A sheet mirrors a binder page: `path` and `sha`. Roy, 2026-08-29: *"it also lands us a place to
copy the page shas from so we are not reaching into the binder to get it. That breaks the only
current read-write link coupling in the system."*

! **THE COUPLING IS PROSPECTIVE, NOT PRESENT.** `proof_setter` stopped taking a binder on
2026-08-26 once the docket carried path and sha (`decision-log.md Vocabulary: #14`). Nothing
builds a docket yet, because reconciliation is what will -- and a flat `edit_copy` would force
that emitter to reach back into the binder for every sha, re-opening the seam one layer up.

!! **NOT EVERY BINDER READ IS COUPLING.** `collator.known_addresses(binder)` must keep reading the
binder: its job is checking that a role did not invent an address, and that has to be asked of the
authority, never of the role's own copy. What this removes is a FACT CARRIED TO THE WRITE SIDE.

---

## 2. Topology, and fan-out

**The topology is data, in a run-scoped file** -- an ordered list of stages, each holding a list of
DISPATCHES. `desk/stages.py`'s `STAGES` is a literal today, so every configuration would otherwise
be a source edit.

```toml
[[stage]]
name     = "4c"          # the stage's own label
kind     = "editorial"   # or "enriching" -- decides whether a revise is pulled
reads    = "revise:4a"   # "original", or the revise a named earlier stage pulled
carries  = []            # edit_copies of earlier stages, handed along unsettled

  [[stage.dispatch]]
  role  = "block-context"
  paths = ["src/comment_review/reading/*.py"]

  [[stage.dispatch]]
  role  = "block-context"          # the same role again -- this is fan-out
  paths = ["src/comment_review/binder/*.py"]

  [[stage.dispatch]]
  role  = "function-context"       # no `paths` -- every page
```

!! **`paths` IS ON THE DISPATCH, NOT THE STAGE, AND THE FIRST DRAFT HAD IT ON THE STAGE.** MEASURED
by writing the three topologies out: a stage fans out ONE role while leaving the others whole --
`block-context` split two ways above, `function-context` not split at all. A stage-level `paths`
cannot say that. **A stage is a list of dispatches, not a list of roles**, and two dispatches naming
one role IS the fan-out.

### The three topologies, written out

| topology | stages | each `master_proof` holds | revises |
| --- | --- | --- | --- |
| all four at once | 1 | 4 `edit_copies` | 1 |
| pure sequential | 4 | 1 `edit_copy` | 4 |
| `4a` then `4c` | 2 | 1, then 3 | 2 |

! **THE RE-READ RULES FIRE IN PROPORTION TO CONCURRENCY**, which is the design working rather than
a special case: all-at-once composes four sets of edits nobody read, and pure sequential composes
none.

### `reads` and `carries` are different inputs, and only one is built

| what a stage reads | it sees | status |
| --- | --- | --- |
| `reads = "revise:N"` | the rebuilt tree with stage N's SETTLED corrections set -- corrected TEXT, not marks | **built**, P2 |
| `carries = ["N"]` | the binder, plus stage N's `edit_copies` -- the PROPOSALS, unsettled | **format only; not built** |

!! **THE DIFFERENCE IS WHAT A LOSING PROPOSAL LOOKS LIKE.** A revise shows only what settled, so a
later role cannot see a mark that lost; `carries` shows the marks themselves, so a later role can
disagree with a SUGGESTION rather than with the applied result.

!! **`carries` IS A HYPOTHESIS, NOT A FEATURE.** Roy, 2026-08-29: *"It is something that should be
tested by the agents and testing lane on what allows for better answers. I think that giving the
later roles information might help, but it might not."*

! **SO IT IS THE VARIABLE `CLAUDE.md`'s TWO-LANE RULE TURNS**: land the machinery with
effectiveness UNCHANGED, then change what agents are told, then measure whether recommendations
improved. ! **AND THE MEASUREMENT CANNOT RUN YET** --
[`the-harness-cannot-run-the-system-it-grades`](../../../TODO/the-harness-cannot-run-the-system-it-grades.md)
is open and is what blocks both halves of that rule today. Whether carrying an `edit_copy` forward
helps is genuinely unanswered.

! **THE VALIDATOR REFUSES A NON-EMPTY `carries` RATHER THAN IGNORING IT.** A key that is silently
dropped is indistinguishable from one that worked, which is the failure this repo's gates exist to
refuse.

| | |
| --- | --- |
| `backend` owns | the format, its validator, and the fan-out |
| `agents` owns | when a stage runs, in what order, and why |

That split is `decision-log.md Process: #40`.

! **A RUN IS AUDITABLE BECAUSE THE TOPOLOGY IS AN ARTIFACT** -- the file records which agent was
given which pages, beside that run's census and dockets.

### Fan-out partitions by FILE

Roy, 2026-08-28: *"By file because context should be more consistent. File thrashing would be
bad"*, and on why fan-out exists at all: *"It makes them more efficient and we have measured that
it makes them more diligent in actually inspecting the blocks, where they get overloaded on too
many records. Because it is tight detailed work it matters for their role most."*

Fan-out splits `binder["pages"]` by the paths a DISPATCH names and seeds one `edit_copy` per
shard. Two guards:

- no page appears in two shards of the same role
- every page in the binder appears in exactly one shard of each role

!! **NON-OVERLAP IS STRUCTURAL, NOT CONVENTIONAL.** An address is `path@cue`, so partitioning by
file means one role marks a place at most once. `Pulled.set_by`'s `address -> role` stays
unambiguous and fan-out needs no extra identity.

### `STAGES` is doing two jobs, and only one of them moves

!! **WHICH ROLES EXIST IS A CLOSED SET; WHEN THEY RUN IS A RUN'S BUSINESS.** `desk/stages.py`'s
`STAGES` currently answers both, and the topology file must take only the second.

| | stays in code | moves to the file |
| --- | --- | --- |
| the four role names | **yes** -- a closed set, `StrEnum` per `T1.15` | no |
| which stage dispatches which role, in what order | no | **yes** |
| what a stage READS, and what it CARRIES | no | **yes** |

! **THE CONSEQUENCE IS IN CODE THAT LANDED 2026-08-28.** `commands/mark.py` derives `--role`'s
`choices=` from `STAGES` (T1.16), which was correct while `STAGES` was the only list of the four.
Once the order moves to a run-scoped file, that derivation would let **a run's topology decide
which role names are valid** -- so `--role` must draw from the `Role` enum instead, and the
topology file's `role` keys are VALIDATED against it.

! **THAT ALSO KEEPS `desk.stages`'s PRODUCTION IMPORTER**, which T1.16 gave it: the module still
owns the closed set, and it stops owning the schedule.

### The barrier

A stage's revise pulls only after every `edit_copy` of that stage returns -- all roles, all shards.
`flows.revise.pulls_revise` already gates on the stage's kind; what is new is that a stage is not
finished until its `master_proof` is assembled.

!! **THE BARRIER IS WHAT MAKES `reads` RESOLVABLE.** `reads = "revise:4a"` names an artifact that
exists only once stage `4a` has assembled its `master_proof`, reconciled it, and pulled. So the
file's ordering is not decoration: a stage may only READ a revise pulled by a stage EARLIER in the
list, and the validator refuses a forward reference.

! **WHICH ALSO BOUNDS WHAT A TOPOLOGY CAN SAY.** There is no cycle to detect and no scheduler to
write -- the list IS the order, each entry reads backwards or reads `original`, and a run walks it
once. Roy, 2026-08-28: the forward pass is a line.

! **AN `enriching` STAGE PULLS NOTHING**, so nothing may name it in `reads`. Its output goes into
the next binder as facts -- `Process: #34` -- and the validator refuses `reads = "revise:<an
enriching stage>"` by name rather than resolving it to the previous editorial one.

### Topology is a tuning knob, not an invariant

Roy, 2026-08-28, on whether the same findings must produce the same page under every topology:
**no.** Sequential genuinely differs, because a later role reads text an earlier one already
corrected and so has less to disagree with -- which is the reason `ownership-context` runs first.
The run reports which topology produced it.

---

## 3. Reconciliation

```
reconcile(master_proof) -> (settled, escalations, rereads)
```

Pure: no file reads (source-verification already ran per mark), no rendering
(`docs/plans/...` T5.3), no binder.

!! **NONE OF THE RULES READ THE TOPOLOGY.** A `master_proof` holds whatever `edit_copies` its
stage produced -- one, four, or seven. Sequential is a `master_proof` with one `edit_copy` in it,
and every rule still holds; they simply rarely fire. **That is the test that the flexibility
constraint is satisfied rather than special-cased.**

### Grouping

Group every mark by every place it TOUCHES -- its address, and a `move`'s destination. A `move`
settles or escalates WHOLE, because it is indivisible ([`docs/the-mark.md`](../../the-mark.md)):
no docket ever carries one end of one.

### What forces a re-read

!! **A COMPOSITION NOBODY READ IS A DEFECT THE PER-PLACE RULES CANNOT SEE.** Roy, 2026-08-29:
*"If two roles have a mark that edits a paragraph - I think we need to send the revision back to
them because they could have fixed the same defect in different ways that then causes a new
defect. To ensure that the reading still sticks together any composition of edits has to be
re-read. The only two that get a pass is query and clean."*

! **THE PASS LIST IS ALREADY A COLUMN.** `owes_change` is False for exactly `clean` and `query`
and True for the other five, so this rule is derived from the approved shape rather than invented.

| marks owing a change on one paragraph | outcome |
| --- | --- |
| 0 | nothing |
| 1 | **settle** -- nobody composed anything |
| 2+, different sentences | **re-read** -- compose, send the composition back to the roles that marked it |
| 2+, same sentence | **escalate** -- the conflict case |

Both re-read and escalate go to the revise step; they differ in what the role is asked -- *does
this still read?* against *which of these?*

### An `add` goes back to every role of the stage

Roy, 2026-08-29: *"Or they could have duplicated the comment. An add on a new place is sent back
to all of them."*

! **AN `add`'S BLAST RADIUS IS THE PAGE, NOT THE PLACE.** It creates prose nobody has read, and it
can duplicate prose elsewhere -- which per-place grouping structurally cannot see, because two
`add`s at two addresses never meet. `ownership-context` decides which of several sites OWNS a
repeated claim and `module-context` asks whether the comments say one thing; both ran BEFORE the
added prose existed.

**NARROW, ruled 2026-08-29:** all roles of the stage, and for a partitioned role only the shard
holding that file. Cross-file duplication is not chased; it would cost the fan-out's whole benefit
on any page carrying an `add`.

### The remaining rules

| | rule | the case that proves it |
| --- | --- | --- |
| T4.3 | a scope-declaring `query` is a boundary report, not a blocker | three `clean` + one `outside-my-role` settles -- the case measured taking a docket from 12 alterations to 5 |
| T4.4 | `unable-to-determine` settles where another role of the same stage ruled substantively | A undetermined + B `correct` does not reach the chief |

`Process: #33` is T4.3's ruling.

### How far the re-read rule reaches

| | composition re-read? |
| --- | --- |
| across stages | **already** -- the next stage reads the REVISE, which is the composed text |
| within a stage | **no** -- this is the hole, and it is what the rules above close |

! **SEQUENTIAL WAS ALWAYS SAFE BY CONSTRUCTION**, and concurrency is where the defect lives --
the same axis the flexibility constraint runs along. Nothing already built has to change to
support it: `pulls_revise`, the revise sheet and the four revise outcomes exist. **What changes is
the trigger**: composition and `add`, not only disagreement.

---

## 4. What this changes in built code

| file | change |
| --- | --- |
| `flows/marks.py` | `seed` stops flattening through `rows_of`; emits `sheets`. `problems_in` walks sheets. `sheet` -> `edit_copy` in its prose |
| `desk/collator.py` | `verify_report` walks sheets; reconciliation lands here as the collator's second named step (`Vocabulary: #19`) |
| `commands/mark.py` | reads and writes an `edit_copy`; `--role`'s `choices=` moves from `STAGES` to the `Role` enum |
| `docket/docket.py` | a schedule carries `role` |
| `desk/stages.py` | keeps the four roles as a closed `StrEnum`; `Stage.roles` becomes DISPATCHES; the `STAGES` literal goes and a validated run-scoped file supplies the schedule. `pulls_revise` is unchanged -- it reads `stage.kind` |
| `SKILL.md`, `reviewer-brief.md` | `sheet` -> `edit_copy`; the new containers named |
| `docs/vocabulary.md` | the four containers; `master proof` stops being "unnamed" |
| `tests/` | every test reading `report["marks"]` walks sheets |

! **`revise.pull._set_by` NEEDS NO CHANGE.** It already reads an optional `role` per page and maps
`address -> role`; it maps everything to `""` today because nothing writes the field. P6's
provenance starts working the moment reconciliation writes it.

---

## 5. What this design does not do

- **decide.** Reconciliation emits; the copy chief is out of 0.2.4 -- `Process: #42`
- **render.** T5.3 keeps rendering out of reconciliation
- **read files.** Source-verification already ran
- **chase cross-file duplication.** Ruled narrow, above

---

## 6. What must be measured before it is trusted

!! **T4.5's "settle 13 of 16" WAS MEASURED UNDER SILENT-MERGE SEMANTICS.** Under the re-read rule
some of those 13 become re-reads. The number is suspect until re-derived, and it is re-derivable:
count how many of the 16 places carry 2+ marks owing a change, from
[`evidence/the-loop-measured-2026-08-27/`](../../../evidence/the-loop-measured-2026-08-27/).

! **A COUNT, NOT A JUDGEMENT.** Whatever it comes to is the new baseline; what would be wrong is
carrying the old number forward beside a rule that invalidates it.

---

## 7. A dependency the plan has pointing the wrong way

!! **P5's `diff3` IS A COMPOSER, NOT ONLY A RENDERER.** `change` is the whole updated paragraph as
raw text (`Vocabulary: #27`) and a sheet carries `raw_text` as the base -- so composing two edits
to one paragraph IS a three-way merge: base `raw_text`, sides each role's `change`. T5.1 is scoped
in the plan as SHOWING a conflict to a human; it is also what produces the composed text.

! **SO P4 DEPENDS ON T5.1**, where the plan has P5 downstream of P4. A textual conflict in that
merge is the same-sentence case; a clean merge is what goes back to be read.

---

## 8. The rulings this rests on

| ruling | where |
| --- | --- |
| stages are `editorial` or `enriching`; roles do not all read at once | `Process: #34` |
| the address space is invariant across a revise | `Process: #35` |
| a reversal is a row in the same revise step | `Process: #36` |
| the mark's shape has an owning file | `Process: #37` |
| accurate command instructions are `backend`'s; choreography is `agents`' | `Process: #40` |
| the copy chief is not in 0.2.4 | `Process: #42` |
| a scope-declaring query is a boundary report | `Process: #33` |
| the collator has two named steps | `Vocabulary: #19` |
| `change` is the updated paragraph as raw text | `Vocabulary: #27` |

**Ruled while this design was made, and recorded with it:**

| ruling | where |
| --- | --- |
| the four containers, `edit_copy`, and the sha riding on the sheet | `Vocabulary: #28` |
| fan-out partitions by FILE, for measured diligence | `Process: #47` |
| topology is data, and a tuning knob rather than an invariant | `Process: #48` |
| a composition of edits is re-read; `clean` and `query` pass; an `add` goes to every role | `Process: #49` |

! **SHEETS ARE STORED RATHER THAN DERIVED**, which is the one decision above that is a
consequence rather than a ruling: fan-out partitions by file, so the page is the unit of dispatch,
and an `edit_copy` with no page level could not show which files an agent was given -- only let a
reader infer it from the addresses present.
