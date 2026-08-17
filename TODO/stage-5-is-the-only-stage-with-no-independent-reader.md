# Stage 5 is the only stage whose writer is also its checker

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    Roy (⭐ 1 ruling) · session
Raised:   2026-08-17, by the session that ran all eight stages and rolled its own work back.
          Its words: "the synthesis -- where four verdicts become one sentence -- is written
          by the same agent that then decides it's correct."
```

## Objective

**Every stage but one is read by somebody who did not write it.**

| stage | who checks it |
| --- | --- |
| 4 MARK | `verdicts.py` — the join, mechanically |
| 6 COMPACT | a separate agent, given a narrow contract and none of the reasoning |
| 7b WRITE | the CODE CHECK, against the pre-edit ref |
| 8 REVIEW | a separate agent, reading the finished page |
| **5 APPLY** | **itself** |

⚠⚠ `compact.md` already makes the argument, for its own stage: *"An agent that never saw the
argument cannot keep a sentence because it remembers writing it — which is what makes this pass
safe... **The contract only buys anything if the reader is not the writer.**"*

That reasoning applies to stage 5 verbatim and is not applied there. Stage 5 writes the
replacement text and then runs the residue check on its own output.

## ⚠ Measured: the self-administered rails were read and not run

A run reached stage 8 with `ruff` clean, the formatter clean, the AST **PROVEN**, and 1103 tests
green — and stage 8 returned twelve findings, enough that the operator rolled the whole pass
back to `REDACTED_SHA_D`. Three of the twelve were the same rail failing:

- **`write.md` requires re-deriving a claim before touching its block.** Three findings were a
  reviewer's `correct` applied without re-derivation. The operator: *"I read that rail and
  didn't run it."*
- **The residue check's four refusals** were answered once instead of four times, which is how
  the `_salvage_row` laundering passed. Filed separately and since fixed in shape.
- **A `drop` was applied whose own `FINDING` named an owner** — `move`'s payload wearing
  `drop`'s label.

⚠⚠ **Two of the twelve are the system making prose WORSE than it found it**, which no other
finding today reaches:

- An unfalsifiable claim was replaced with a **checkably false** one — *"every site reads the
  groups BY NAME"* — in the comment whose entire subject is positional renumbering, while
  `_stale_row_scan` reads `m.group(2)` positionally and is called with a pattern that has no
  named groups at all.
- A reviewer's `correct` dropped a qualifier that was carrying a true sentence, and the result
  is falsified by the test it annotates.

## ⚠ What is NOT established

- **That a second reader would have caught them.** Stage 8 did, which is the design working
  one stage later than it could have.
- **That stage 5 can be split at all.** It holds four verdicts per block, the census, the style
  sheet and the originals; the narrow contract that makes stage 6 safe may not exist here.
- **Whether the cost is payable.** A per-block second reader on 43 blocks is 43 dispatches.

## Tasks

- [ ] ⭐ Rule on whether stage 5 gains an independent reader, and what it is given. ⚠ The
      candidates differ in what they can catch:
      **(a) nothing — stage 8 is the reader**, one stage late and after the write;
      **(b) a residue-check agent** handed only the ORIGINAL and the REPLACEMENT, and asked the
      four refusals — the narrowest contract, and it is the check that failed;
      **(c) a re-derivation agent** handed the claim and the code, asked only "is this true",
      which is the failure that produced both worse-than-before findings;
      **(d) stage 8 moves BEFORE the write.**
      ⚠ (d) is the cheapest and changes the stage order, which is Roy's to rule.

- [ ] Consider (d) seriously before building (b) or (c). Stage 8 already exists, already has a
      separate reader, and already caught all of this. What it cannot do today is stop the
      write, because it runs after 7b. ⚠ Against it: `review.md` reads the FINISHED PAGE, and a
      proposal is not a page.

- [ ] Count how many of stage 8's twelve findings a pre-write reader could have caught, from
      that run's preserved artifacts. ⚠ That number decides whether this is worth paying for,
      and it is available now rather than by argument.

- [ ] Make the `write.md` re-derivation rail answerable, the way the residue check's four
      refusals now are. A rail read and not run is a shape problem, and it has now been measured
      twice in one day.

- [ ] ⚠ Record that the mechanical stages held. The join gated correctly, the interval exemption
      removed the 65-refusal class, `compact` respected the docstring exemption and flagged its
      own width trade rather than hiding it, and the CODE CHECK stopped the run on a real AST
      change. The failure is specific to the stage with no second reader.

- [ ] ⚠ Record the rollback as the system working. Twelve findings, tree returned to
      `REDACTED_SHA_D`, 0 modified files. A pass that makes the page worse and says so is the outcome
      stage 8 exists for.
