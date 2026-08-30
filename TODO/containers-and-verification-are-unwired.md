# The containers and the source-verification half are wired to nothing

```
Status:   open
Progress: 0 of 5 tasks done
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

- [ ] Implement the `desk.containers.parse_edit_copy` call at the flow's inbound
      boundary, so a document that is not the shape an edit copy must be ERRORS
      OUT rather than being re-derived downstream. Verify: a copy missing `sheets`
      is refused by name from the flow, and the test goes red when the call is
      removed.
- [ ] Implement the `desk.containers.parse_master_proof` call at the master
      proof's boundary, on the same terms. Verify: a proof whose `edit_copies` is
      not a list is refused by name from the flow, and the test goes red when the
      call is removed.
- [ ] Implement the `desk.collator.verify_report` call in the flow, so source
      verification runs in production. Verify: `grep -rn "verify_report" src/`
      returns a caller outside `desk/collator.py`; a test asserts a mark whose
      `sources` cite does not resolve is reported by a RUN OF THE FLOW, not only
      by calling the function.
- [ ] Delete the hand-rolled `isinstance` checks the containers now answer for, so
      one definition of a valid copy survives. Verify: no two places in `src/`
      decide what a well-formed edit copy is, and `problems_in` reports only on
      CONTENTS -- the per-mark problems that route back to a role.
- [ ] Update `desk/containers.py` and `desk/collator.py` prose to state what each
      boundary refuses and what it reports, now that both are reached. Verify: no
      sentence in either file claims a consumer that `grep -rn` does not show, and
      the ENVELOPE/CONTENTS split is stated once rather than in both files.
