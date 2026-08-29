# The flow assumes every role reads the same page at the same time, once

```
Status:   open
Progress: 6 of 7 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28, reviewing the draft plan for the mark and the collator. Roy:
          "it bakes in the idea that all editorial-role agents see everything at the
          same time and only rule on it once."
```

## Objective

**The shipped skill has never worked that way and the code has no word for it.** `SKILL.md`
stage 4 runs `ownership-context` ALONE at 4a and the other three at 4c, and Roy expects at least
one more agent before those three. But `flows.marks.seed(binder, role)` is a function of the
binder and a role -- there is no stage, no prior marks, and no way to say WHICH page a role is
holding.

    stage 1   ownership-context           reads the original
    stage 2   <an enriching agent>        reads the original
    stage 3   block / function / module   reads ... the original?

! **Today the answer is yes, and it is the wrong one.** `SKILL.md:578` says the three receive
`ownership-context`'s *"resolved PLACEMENT, not its findings"* -- so a role at stage 3 cannot
know an earlier role already ruled a sentence false, and will re-derive it or contradict it.

## What a later stage reads instead

!! **A REVISE -- the trade's word, already defined.** `decision-log.md Process: #10` carries it
from `vocabulary.md`: *"the second proof, pulled after the marked corrections have been set."*
Roy, 2026-08-28: *"unless as part of the binder we copy the whole program into a tempdir and
allow edits there."*

| | |
| --- | --- |
| **between stages** | sequential. Stage N+1 reads a revise carrying stage N's taken-in edits. Nothing to merge |
| **within one stage** | concurrent. Conflicts are the collator's, rendered `diff3` per place |

! **THE MECHANISM IS BUILT.** `flows/proof_setter.py` already reads from disk, sets the page and
writes a draft into `--out DIR` -- *"a temporary file, never the original"* -- proving executable
code unchanged, and refusing a draft directory that overlaps the repo. ! And every read command
already takes a root: `census`, `carry`, `proof`, `prove_unchanged` and `referrers` all carry
`--repo`, so pointing a stage at a revise is passing a different value.

## Why the addresses cannot move

**`prove_unchanged` holds the executable code byte-identical across a draft**, and a place is
determined by CODE -- a declaration, a gap between two code lines, the room beside a line, the
leading between paragraphs. Prose changing inside a place neither creates nor destroys one, and
`add`/`drop` fill and empty places that already exist.

! **THAT IS THE WHOLE SAFETY ARGUMENT, so it is a claim to gate rather than to assert.** T4 is
what makes it falsifiable.

## Tasks

- [x] T1 -- A stage list as DATA, each entry naming its kind -- `editorial` (fills a sheet, its
      marks are reconciled, a revise is pulled after it) or `enriching` (hands back facts that go
      into the next binder, no docket, no revise). Verify: an enriching entry pulls no revise, and
      adding a stage is a row rather than a code change.
- [x] T2 -- The binder records which revise it was censused from. Verify: a sheet seeded from it
      names the revise and the original in its header, and a binder built from the original says
      so rather than leaving the field absent.
- [x] T3 -- Pull a revise at each editorial boundary: the settled docket through `proof_setter`
      into a tree copy with the drafts overlaid. Verify: the revise root holds every library file,
      only the scheduled pages differ, and `prove_unchanged` passes on it.
- [x] T4 -- Gate the address space. Verify: re-censusing a revise yields the address set the
      original yielded, over real files -- and the check FAILS on a revise whose code was changed
      by hand, which is what proves it can bite.
- [x] T5 -- Every read for a stage resolves against that stage's root. Verify: a `source` citing a
      page an earlier stage edited returns the REVISE's text, not the repo's.
- [x] T6 -- `taken_in`: original against the revise in a role's hand, as a unified diff per page,
      plus which stage took in which addresses. Verify: it prints nothing when no stage has set
      anything, and its diff applies cleanly to the original.
- [ ] T7 -- The last revise IS the draft the human approves at 7a. Verify: no second draft-building
      path exists, and the artifact 7a reads is the final revise root.
