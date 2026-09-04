# A conflict is detected and nothing renders it

```
Status:   open
Progress: 3 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28, filing the work `decision-log.md Process: #20` created. The
          rendering was ruled the same day it was invented and has no backlog entry,
          so the plan step that builds it cited a ruling rather than a task.
```

## Objective

**Reconciliation can say two marks collide and has no way to SHOW it.** The lab's version
returned `"2 roles differ on one sentence"`, which tells a role that something is wrong and not
what.

!! **THE FORM IS RULED: `diff3`, WITH THE BASE.** Roy, 2026-08-27, on why the artifact should be
a diff at all: *"Your training has made you pretty good at reading a git diff and using that to
show the conflict would probably be useful. The diff could go right back to the editor for a new
mark immediately."*

!! **AND THE TWO-SIDED FORM IS REFUSED ON A MEASUREMENT.** Two roles edited DIFFERENT lines of one
paragraph; the two-sided render showed each side differing from the other in BOTH lines, so a
reader cannot tell which line either role touched. With the base present it is immediate:

    <<<<<<< block-context
    # Rebuild the index when the cache is MISSING.
    # Costs one pass over the tree.
    ||||||| base
    # Rebuild the index when the cache is cold.
    # Costs one pass over the tree.
    =======
    # Rebuild the index when the cache is cold.
    # Costs two passes over the tree.
    >>>>>>> ownership-context

! **THE TWO-SIDED FORM IS STRUCTURALLY INCAPABLE of separating a real conflict from two composable
edits in one hunk** -- which is the exact distinction reconciliation exists to make. It would
escalate composable edits, the same failure as keying agreement on the proposed text.

! **AND THE BASE IS WHAT KEEPS SOURCE-VERIFICATION WORKING ON THE RETURN.** A `claim.false` is
checked verbatim against the paragraph; a role ruling on a two-sided conflict has no stable text
to quote, only two candidate rewrites.

### Why it is its own module

**Detecting a collision and rendering one are different jobs.** That is the split the galley cost
this repo -- a module that both ruled and set type -- and `decision-log.md Vocabulary: #11` holds
the collator to ruling on nothing.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- Render base plus every edit in `diff3`
      form, from an escalation. Verify: the output parses back into three sides,
      and the base side is byte-identical to the paragraph.
- [x] T2 | FINISHED | unknown | T2 -- Prove the form was chosen for a reason.
      Verify: a test builds two edits on DIFFERENT lines of one paragraph and
      asserts the `diff3` render shows them disjoint -- and fails if the
      renderer is switched to the two-sided form.
- [ ] T3 | T3 -- Keep rendering out of reconciliation. Verify: reconciliation
      returns escalations carrying no rendered text, and the renderer takes an
      escalation and returns lines.
- [x] T4 | FINISHED | unknown | T4 -- Handle more than two marks at one place.
      Verify: three conflicting marks render without losing one, or the design
      says why three cannot arise.
