# The containers and the source-verification half are wired to nothing

```
Status:   open
Progress: 1 of 24 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, Roy ruling that containers are wired and that the
          collator's source-verification half is wired into the flow rather than split
          out, after a review measured containers with no production importer and
          verify_report with only test callers)
```

## Objective

The containers and the source-verification half are wired to nothing.

!! **RULED 2026-08-30 -- `decision-log.md Process: #57` and `#58`.** Two questions were put
to Roy separately and he answered them the same way.

On the containers: *"yes because the system is broken without it. It may not error but it
also is not protected from future errors which the containers are an explicit statement for
what is contained and what can be contained or errors out"*

On the collator's title needing an *and*: *"Nope the source-verification side needs to be
wired into the flow - same as 1) the flow coordinates the things in the modules do"*

## What is measured

| | |
| --- | --- |
| `desk/containers.py` | **no production importer.** It declares `Sheet`, `EditCopy`, `MasterProof` and their parses while `desk/collator.py` hand-rolls its own `isinstance` checks with its own definition of a valid copy |
| `desk/collator.py` source verification | **only test callers.** `grep -rn "verify_report" src/ tests/` returns five prose mentions inside `collator.py` itself and six call sites, all in `tests/test_collator.py` |

So `address_problems`, `claim_verbatim_problems`, `source_problems`, `source_verification`
and `verify_report` are reached by tests and by nothing in production, and the shape a copy
must be is stated in one place and decided in another.

## The refuse-versus-report tension is resolved BY LEVEL, not by precedence

`parse_edit_copy` REFUSES a bad copy while `flows/collate.py`'s `problems_in` REPORTS one
and continues, so each problem routes back to the role that wrote it. That reads as two
contracts competing for one boundary. **It is two boundaries:**

| | rules on | on failure |
| --- | --- | --- |
| a container | the **ENVELOPE** -- is this document the shape a copy must be | errors out |
| `problems_in` | the **CONTENTS** -- what one role wrote in one slot | reports, and routes it back |

Neither answers the other's question, and wiring the first does not weaken the second.

!! **THE ARGUMENT IS ABOUT FUTURE ERRORS, NOT PRESENT ONES** -- Roy: *"It may not error but
it also is not protected."* A shape nothing states is a shape every consumer re-derives, and
the re-derivations drift silently because each one is locally correct.

!! **AND THE *"NEEDS AN AND"* TELL POINTED THE WRONG WAY HERE.** `collator.py`'s title reads
*"SOURCE-VERIFICATION and RECONCILIATION"*, which `module-context` treats as evidence for a
split. The defect was the opposite: **a module half with no caller READS like a second
module**, because nothing in the running system ties it to the first. The fix is a caller,
not a boundary -- and moving it to a new file would have left it exactly as unwired.

! **`desk/containers.py` CANNOT BE FULLY CORRECT UNTIL A MOVE HAS SOMEWHERE TO GO.** An edit
copy is one slot per place and a move spans two -- `Process: #60`, task 9 of
[`move-is-a-composite-mark`](move-is-a-composite-mark.md). This file's task 1 lands the
envelope check; that file's task 9 lands the region a move needs inside it.

## Tasks

- [ ] T1 | Implement the `desk.containers.parse_edit_copy` call at the flow's
      inbound boundary, so a document that is not the shape an edit copy must be
      ERRORS OUT rather than being re-derived downstream. Verify: a copy missing
      `sheets` is refused by name from the flow, and the test goes red when the
      call is removed.
- [ ] T2 | Implement the `desk.containers.parse_master_proof` call at the master
      proof's boundary, on the same terms. Verify: a proof whose `edit_copies`
      is not a list is refused by name from the flow, and the test goes red when
      the call is removed.
- [ ] T3 | Implement the `desk.collator.verify_report` call in the flow, so
      source verification runs in production. Verify: `grep -rn "verify_report"
      src/` returns a caller outside `desk/collator.py`; a test asserts a mark
      whose `sources` cite does not resolve is reported by a RUN OF THE FLOW,
      not only by calling the function.
- [ ] T4 | Delete the hand-rolled `isinstance` checks the containers now answer
      for, so one definition of a valid copy survives. Verify: no two places in
      `src/` decide what a well-formed edit copy is, and `problems_in` reports
      only on CONTENTS -- the per-mark problems that route back to a role.
- [ ] T5 | Update `desk/containers.py` and `desk/collator.py` prose to state
      what each boundary refuses and what it reports, now that both are reached.
      Verify: no sentence in either file claims a consumer that `grep -rn` does
      not show, and the ENVELOPE/CONTENTS split is stated once rather than in
      both files.
- [ ] T6 | Implement a check at the flow's inbound boundary that a returned edit
      copy still carries the binder's address set, so a copy cannot decide which
      places exist. Verify: a copy whose `sheets` is `[]`, one whose sheets are
      not objects, one whose `marks` is a string, and one that kept 1 of its 4
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
- [ ] T23 | Update `parse_master_proof` so `_read_from_problem` runs when
      `edit_copies` is empty, where any value is admitted today
        > 2026-08-31 'oops', None, 7, [] and {'root': 7} all pass when copies is empty
- [x] T24 | Sheet.seed, EditCopy.seed and MasterProof.seed land, built from fields(cls) | f943d7b | Implement
      `Sheet.seed`, `EditCopy.seed` and `MasterProof.seed`, so a container is
      written through its type as a mark already is
        > 2026-08-31 rename Sheet.sha: parse gives sha='' []; Mark.seed raises at build
