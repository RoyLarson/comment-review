# The containers and the source-verification half are wired to nothing

```
Status:   open
Progress: 13 of 41 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-30 (2026-08-30, Roy ruling that containers are wired and that the
          collator's source-verification half is wired into the flow rather than split
          out, after a review measured containers with no production importer and
          verify_report with only test callers)
Retitle:  2026-08-31 -- title now false: they are wired; what is left is nothing HOLDS
          one
```

## Objective

The containers are wired, and nothing downstream holds one.

!! **THE FIRST HALF LANDED 2026-08-31 IN SP-2** --
`docs/superpowers/plans/2026-08-31-sp2-the- wiring-and-shard-coverage.md`,
closing `P21`, `P25` and `P27`. `flows.collate.collate` parses every returned
copy at its inbound boundary and the proof after `gather`; `verify_report` runs
over every ruled mark; a role short of its shard is named. **The measurements
below are what that closed, and are kept because a stranger should be able to
see what the file was opened for.**

## What was measured, 2026-08-30, and is now false

| | |
| --- | --- |
| `desk/containers.py` | **no production importer.** It declared `Sheet`, `EditCopy`, `MasterProof` and their parses while `desk/collator.py` hand-rolled its own `isinstance` checks with its own definition of a valid copy |
| `desk/collator.py` source verification | **only test callers.** `grep -rn "verify_report" src/ tests/` returned five prose mentions inside `collator.py` itself and six call sites, all in `tests/test_collator.py` |

Both now return real production callers -- T1, T2 and T3, against `eeb983f`,
`6bb8f8e` and `7bd7dd3`.

## What is measured NOW, 2026-08-31, and is the rest of this file

**A container is built, checked, and thrown away.** `flows/collate.py:691` keeps
the parsed `EditCopy` only to test it against `None`; `:753` drops the
`MasterProof` entirely; and the one field read off a parsed object anywhere in
`src/` is `copies[0].read_from`, inside `containers.py` itself. **29 signatures
between the load and the save take or return a raw dict, and 3 lines in the
whole middle construct a container object.**

!! **RULED `Process: #65`, 2026-08-31.** Roy, on being told this was a design
question: *"Defect not a design question ... Unless it is the flow passing the
json decoded item into the container on the first step of loading the flow no
downstream results should get the raw json. Everything after the load step to
the save step works on or with the containers and the containers serialize and
deserialize themselves or seed themselves and the flow saves the resulting
object to json through json.dumps"*

    LOAD   json.loads -> the decoded item -> `parse_*` -> a container
    WORK   every step from there takes and returns CONTAINERS
    SAVE   the container serializes itself -> json.dumps

! **IT IS WHAT THIS MODULE ALREADY SAID IT WAS FOR.** `desk/containers.py`'s own
docstring: a parse returns `(T, [])` *"so a caller holds a checked object rather
than re-deriving the same keys with `isinstance` ladders."* No caller holds one,
and every step downstream re-derives the keys the parse just checked. ! **THE
WIRE STAYING DICTS IS NOT A CONTRADICTION** -- that is about what crosses the
process boundary, what a role is handed and what `json.dumps` writes. In memory,
between load and save, the value is the container.

## The refuse-versus-report tension is resolved BY LEVEL, not by precedence

`parse_edit_copy` REFUSES a bad copy while `desk.collator.problems_in` REPORTS
one and continues, so each problem routes back to the role that wrote it. That
reads as two contracts competing for one boundary. **It is two boundaries:**

| | rules on | on failure |
| --- | --- | --- |
| a container | the **ENVELOPE** -- is this document the shape a copy must be | the run errors out |
| `problems_in` | the **CONTENTS** -- what one role wrote in one slot | reports, and routes it back |

Neither answers the other's question, and wiring the first did not weaken the
second.

! **THE ENVELOPE REPORTS RATHER THAN RAISES, decided in SP-2.** `Process: #57`
says a container *"errors out"*, and the run does: `commands/collate.py` prints
every `Problem` and returns `BROKEN` without writing the chief copy. What
changes is that it says everything it found on the way -- a raise there was
measured discarding every routable problem already computed.

!! **THE ARGUMENT IS ABOUT FUTURE ERRORS, NOT PRESENT ONES** -- Roy: *"It may
not error but it also is not protected."* A shape nothing states is a shape
every consumer re-derives, and the re-derivations drift silently because each
one is locally correct.

!! **AND THE *"NEEDS AN AND"* TELL POINTED THE WRONG WAY HERE.** `collator.py`'s
title reads *"SOURCE-VERIFICATION and RECONCILIATION"*, which `module-context`
treats as evidence for a split. The defect was the opposite: **a module half
with no caller READS like a second module**, because nothing in the running
system ties it to the first. The fix was a caller, not a boundary -- and moving
it to a new file would have left it exactly as unwired.

! **`desk/containers.py` CANNOT BE FULLY CORRECT UNTIL A MOVE HAS SOMEWHERE TO
GO.** An edit copy is one slot per place and a move spans two -- `Process: #60`,
task 9 of [`move-is-a-composite-mark`](move-is-a-composite-mark.md).

## Tasks

- [x] T1 | collate parses every copy at the boundary and reports; 9 tests red without it | eeb983f | Implement
      the `desk.containers.parse_edit_copy` call at the flow's inbound boundary,
      so a document that is not the shape an edit copy must be ERRORS OUT rather
      than being re-derived downstream. Verify: a copy missing `sheets` is
      refused by name from the flow, and the test goes red when the call is
      removed.
- [x] T2 | collate parses the proof after gather and reports; the test goes red without it | 6bb8f8e | Implement
      the `desk.containers.parse_master_proof` call at the master proof's
      boundary, on the same terms. Verify: a proof whose `edit_copies` is not a
      list is refused by name from the flow, and the test goes red when the call
      is removed.
- [x] T3 | collate calls verify_report over every copy; a RUN reports an unresolvable cite | 7bd7dd3 | Implement
      the `desk.collator.verify_report` call in the flow, so source verification
      runs in production. Verify: `grep -rn "verify_report" src/` returns a
      caller outside `desk/collator.py`; a test asserts a mark whose `sources`
      cite does not resolve is reported by a RUN OF THE FLOW, not only by
      calling the function.
- [x] T4 | the flow's downstream shape guards are cut; the module boundary keeps its own as depth | 1c6e13e | Delete
      the hand-rolled `isinstance` checks the containers now answer for, so one
      definition of a valid copy survives. Verify: no two places in `src/`
      decide what a well-formed edit copy is, and `problems_in` reports only on
      CONTENTS -- the per-mark problems that route back to a role.
- [x] T5 | the three files state what each boundary refuses; the split is stated once, in containers | 866a0a4 | Update
      `desk/containers.py` and `desk/collator.py` prose to state what each
      boundary refuses and what it reports, now that both are reached. Verify:
      no sentence in either file claims a consumer that `grep -rn` does not
      show, and the ENVELOPE/CONTENTS split is stated once rather than in both
      files.
- [x] T6 | collate compares each role's returned address set against the binder and reports | 3fc3414 | Implement
      a check at the flow's inbound boundary that a returned edit copy still
      carries the binder's address set, so a copy cannot decide which places
      exist. Verify: a copy whose `sheets` is `[]`, one whose sheets are not
      objects, one whose `marks` is a string, and one that kept 1 of its 4
      seeded slots are each reported by name; today all four give `problems ==
      []` against a binder carrying `m.py@b1..b4`.
- [ ] T7 | Implement the comparison of EVERY edit copy's `read_from` in
      `parse_master_proof`, as `desk.proof.gather` does. Verify: a proof whose
      second copy was censused from revise 1 while the first names revise 0 is
      refused by name -- today it returns zero problems, while `gather` raises
      `MismatchedRoot` on the identical two copies.
- [ ] T8 | Update the two sentences in `desk/containers.py` that describe
      `desk.proof.gather`'s check as this parse's -- the prose at lines 197-202
      and the `MasterProof.read_from` declaration at 94-96. Verify: no sentence
      in the file says the parse takes `read_from` from the first copy or
      refuses the disagreement `gather` refuses, and the no-copies case (where
      there is no first copy) is stated.
- [ ] T9 | Update `parse_sheet`'s stated reason for admitting an absent or null
      `sha` at lines 113-115, which says a tree that is not a repo has none.
      Verify: the sentence names the real producer -- `desk/collator.py:992` and
      `flows/collate.py:391` write an empty sha for a path `unflatten` cannot
      resolve -- and a census over a directory holding no `.git` is shown to
      report a real sha.
        > 2026-08-31 Roy: sha_of is hashlib over the TEXT, not a git sha
        > 2026-08-31 a non-repo tree is NOT why an empty sha exists
        > 2026-08-31 open: admit an absent key at all? no producer writes one
- [ ] T10 | Update `desk/containers.py` so its stated contract and its behaviour
      agree: either report one message per broken header rule the way
      `desk.mark.parse` does, or amend the module docstring at lines 17-20.
      Verify: `parse_sheet("s", {"path": None, "marks": "nope"})` returns two
      messages, or no sentence in the file claims `desk.mark.parse`'s
      accumulating contract -- today it returns one message under a docstring
      claiming the other.
- [ ] T11 | Update `parse_edit_copy` and `flows.collate._chief_copy` so an empty
      `read_from` is decided in one place. Verify: the chief that
      `collate(stage, [], binder)` builds round-trips through `parse_edit_copy`
      with no problems, and the proof `desk.proof.gather("4c", [])` writes still
      parses -- today the first is refused by name and the second accepted, one
      stage apart.
- [ ] T12 | Update `tests/test_containers.py:167` so it derives the
      field-earns-itself property instead of asserting `"rounds" not in names`.
      Verify: adding `Sheet.round_count: int = 0` that nothing reads turns the
      test red -- today it passes.
- [ ] T13 | Implement the test that hands a real `flows.collate._chief_copy`
      output to `desk.containers.parse_edit_copy`. Verify: the test exists and
      goes red today on the empty-`read_from` refusal;
      `tests/test_containers.py:56` builds its chief by relabelling a seed copy,
      so nothing in the suite parses a chief the flow actually built.
- [ ] T14 | Update `parse_master_proof` so `MasterProof.stage` is held to the
      same rule as `Sheet.path` and `EditCopy.role`, or delete the field where
      the `where` argument already carries the label. Verify:
      `parse_master_proof("4c", {"edit_copies": []})` is refused by name, or the
      field is gone -- today it returns `MasterProof(stage="")` with no
      problems, and so do `None`, `4` and `""`.
- [ ] T15 | Update `_read_from_problem`'s absent-`read_from` message so it
      composes at both call sites, which each prefix a possessive. Verify: a
      test asserts all four messages at both sites read as sentences -- today
      the absent case renders `4c: edit_copy 1: block-context's carries no
      read_from -- ...` and `4c: master_proof's carries no read_from -- ...`.
- [ ] T16 | Update `parse_sheet` and `parse_master_proof` so a `sha` or a
      `stage` holding a non-string that is not null is refused rather than
      folded to `""`. Verify: `parse_sheet("s", {"path": "p.py", "marks": [],
      "sha": 12345})` is refused by name -- today it returns `Sheet(sha="")`
      with no problems, and so do a list, a dict and `True`.
- [ ] T17 | Update `parse_master_proof` to check its own header before walking
      `edit_copies`, as `parse_edit_copy` already does. Verify:
      `parse_master_proof("4c", {"stage": "4c", "read_from": "oops",
      "edit_copies": [{"role": "r"}]})` reports the proof's `read_from` as well
      as the copy -- today it reports the copy alone and returns at line 218.
- [ ] T18 | Update the COPIED, NOT ALIASED comment at lines 177-179 and 242 to
      the depth the copy holds. Verify: the sentence bounds the guarantee to the
      two fields `_read_from_problem` checks, or a nested key mutated after the
      parse cannot reach `EditCopy.read_from` -- today `nested["meta"]["n"] =
      99` is visible through it.
- [ ] T19 | Update the `checked: dict = data` comment at lines 150-153, which
      blames a loop back-edge for a narrowing the annotation fixes. Verify: the
      sentence states the real cause -- `isinstance(x, dict)` narrows `object`
      to a `__getitem__` taking `Never` -- and a function with no loop at all
      shows the same `invalid-argument-type` diagnostic without the annotation.
- [ ] T20 | Update the proof-versus-copy `read_from` comparison at line 228 so
      it compares the fields `_read_from_problem` checks and names them in its
      message. Verify: a proof whose `read_from` carries an extra key but the
      same `root` and `revise` is accepted, and the refusal names what has to
      match -- today `!=` refuses it and says only "disagrees".
- [ ] T21 | Update the module docstring's builder list at lines 13-14 to name
      `flows.collate._chief_copy`. Verify: every builder of an `EditCopy` in
      `src/` appears in that closed enumeration, checked with `grep -rn
      '"sheets"' src/comment_review/`.
- [ ] T22 | Update `Sheet.marks`' declaration, which reads "one entry per place
      on the page, as they came back". Verify: the sentence says what a move
      does to that count today -- `desk.collator._join_moves` carries one `Mark`
      under two keys and `_chief_copy` dedups on `id(mark)`, so the sheet holds
      `n` entries for `n+1` ruled places -- and names `move-is-a-composite-mark`
      as what makes it true again.
- [x] T23 | the read_from shape check no longer hides inside if copies; six junk values refused | 6bb8f8e | Update
      `parse_master_proof` so `_read_from_problem` runs when `edit_copies` is
      empty, where any value is admitted today
        > 2026-08-31 'oops', None, 7, [] and {'root': 7} all pass when copies is empty
- [x] T24 | Sheet.seed, EditCopy.seed and MasterProof.seed land, built from fields(cls) | f943d7b | Implement
      `Sheet.seed`, `EditCopy.seed` and `MasterProof.seed`, so a container is
      written through its type as a mark already is
        > 2026-08-31 rename Sheet.sha: parse gives sha='' []; Mark.seed raises at build
- [x] T25 | RULED yes, Process #65: the parse hands a container on, and only load and save see json | 78dd7ca | Decide
      whether the parses should return a value at all, since every production
      caller discards the object and reads the dict
        > 2026-08-31 collate.py:691 keeps parsed only to test None; :753 drops it
        > 2026-08-31 only copies[0].read_from is read off a parsed object
        > 2026-08-31 RULED: yes -- the parse hands a container on, Process #65
        > 2026-08-31 load decodes json into a container; save serializes it back out
        > 2026-08-31 no step between the two sees raw json; T26-T28 are the work
- [ ] T26 | Update every step between the load and the save so it takes and
      returns a container rather than a dict
        > 2026-08-31 measured 2026-08-31: 29 signatures in the middle carry a raw dict
        > 2026-08-31 3 lines in the whole middle construct a container object
- [ ] T27 | Implement the serialize half on each container, so the save step is
      json.dumps over what a container hands out
- [x] T28 | SUPERSEDED by Process #66 -- a seed is an empty form, so it cannot be the container | df7e0da | Update
      Sheet.seed, EditCopy.seed and MasterProof.seed to return the container,
      splitting seed from serialize as Mark already does
        > 2026-08-31 Mark splits seed from as_entry already; the containers do not
- [ ] T29 | Update the desk so it does not produce a docket its own reader
      refuses -- an empty one when nothing settles, and a page whose sha it
      folded to empty
        > 2026-08-31 Latent -- nothing writes a docket until P42/P43 wire the middle
        > 2026-08-31 Both shapes have tests pinning the producer; the reader is right
- [ ] T30 | Update the docket so a flow assembles it, not
      desk.collator.docket_from, which reaches sideways into another area to
      construct Alteration, Schedule and Docket
        > 2026-08-31 Roy 2026-08-31: flows reach into containers, containers do not
        > 2026-08-31 Includes the Binder TYPE on collator, not only the construction
- [ ] T31 | Move the read_from shape check off binder.binder, where it is
      private, so the desk containers stop importing another area's underscore
      name for a rule three areas own
        > 2026-08-31 read_from sits on a binder, an edit_copy and a master_proof
- [ ] T32 | Update the compositor so a flow hands it the page, not
      results/compositor.py importing Page and page_for from the read end
        > 2026-08-31 lossless and identity are flow-shaped -- path in, page built
        > 2026-08-31 proof_setter already reaches flows.page_for; only these two do not
- [?] T33 | Is binder/page.py a LEAF both ends may reach down to, or the read
      end, given that Paragraph is already a leaf and both ends handle a Page?
        > 2026-08-31 Page used by results, flows, commands, binder -- both ends
- [ ] T34 | Move SYMBOLISH off reading/lexer.py to a real leaf, since it has no
      reader inside the lexer and was parked there to be one
        > 2026-08-31 Read by binder/annotate.py and concordance/code_names.py only
        > 2026-08-31 Same misplacement Paragraph was in; the comment states the motive
        > 2026-08-31 annotate builds the KEY, code_names the index -- one predicate both
        > 2026-08-31 code_names matches it on string constants only, not arg/alias/def
- [ ] T35 | Move the one filesystem call out of binder/annotate.py, where a path
      existence check is IO outside machine
        > 2026-08-31 line 156 -- the only IO in binder/; picks UNVERIFIABLE or UNRESOLVE
- [ ] T36 | Implement a container for the Reconciled entry, or rule that it
      stays a dict
        > 2026-08-31 P42 left it deliberately: a new type needs its purpose
        > 2026-08-31 named before the code -- conventions.md. _outcome builds it;
        > 2026-08-31 _composition, _resolve and commands/collate.py read it by key.
- [?] T37 | Decide whether a master_proof is ever written to disk, or delete its
      serialize, deserialize and stage
        > 2026-08-31 MEASURED after P42: grep -rn MasterProof src/ shows deserialize
        > 2026-08-31 and serialize with no production caller -- collate's PROOF boundary
        > 2026-08-31 was the last one, and gather returns the container now. stage is
        > 2026-08-31 read only by serialize, so it fails P21's third clause.
- [-] T38 | SUPERSEDED -- Roy ruled 2026-09-01 that a seed is an intentional empty whose container writes the dict out, and fan is N seeds over N shards, so both are already right | 02a4af9 | Update
      flows.distribute.seed and flows.fan_out.fan to return EditCopy, so the
      command serializes what the flow hands back
        > 2026-08-31 MEASURED 2026-08-31: seed returns a dict and commands/distribute.py
        > 2026-08-31 dumps it directly -- the one command of five whose output is not a
        > 2026-08-31 container that serialized itself. fan has the same shape, unwired.
- [x] T39 | RULED: Sheet.marks holds Marks. The two non-Mark kinds go OUT as addresses and reasons rather than onto the entry -- decision-log Process 72, and Roy 2026-09-01: we clearly need sheet to take Marks not Objects. Implementation is T40. | 7ffc71b | Decide
      what Sheet.marks holds on the way back, when a filled mark could be a Mark
      and a seeded one cannot
        > 2026-08-31 MEASURED 2026-08-31: it is the ONLY object in any container's field
        > 2026-08-31 The tension is real: Process 66 makes a SEEDED mark a wire dict, so
        > 2026-08-31 one type serves two states and only one can hold Marks.
- [x] T40 | Sheet holds Marks; the two other kinds are unruled and refused, both off the wire and both what the parse made of an entry rather than a copy of it. | b9ac7f8 | Update
      Sheet so marks holds Mark, with unruled and refused beside it, and every
      reader stops re-parsing
- [ ] T41 | Implement flows/mark_errors.py, which collects every place a role
      must revisit as addresses and reasons
