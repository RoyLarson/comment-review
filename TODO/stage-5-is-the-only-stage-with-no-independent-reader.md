# Stage 5 is the only stage whose writer is also its checker

```
Status:   open
Progress: 1 of 9 tasks done
Owner:    Roy (⭐ 3 rulings, 2 made) · session
Raised:   2026-08-17, by the session that ran all eight stages and rolled its own work back.
          Its words: "the synthesis -- where four verdicts become one sentence -- is written
          by the same agent that then decides it's correct."
```

## Objective

**Every stage but one is read by somebody who did not write it.**

| stage | who checks it |
| --- | --- |
| 4 MARK | `verdicts.py` — the join, mechanically |
| 6 COMPACT | a separate agent reads stage 5's work — but ⚠ **nothing reads the compact agent's own output** until stage 8, after the write |
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
      **(d) stage 8 moves BEFORE the write**;
      **(e) ⭐ ROY, 2026-08-17 — send the PATCH BACK TO THE REVIEWERS: "is this what you mean?"**
      ⚠⚠ **(e) is the recommendation.** See the section below; the others are kept for the
      record and (d) remains worth weighing because stage 8 catches things no filer would.

## ⭐ (e) — send the patch back to the reviewers

Roy, 2026-08-17: *"instead of step 5 just asking step 4 to relitigate the editors answers, it
should create the patch for the answer and send it back to the reviewers since that is what it
needs. Basically stating - is this what you mean?"*

**It is not relitigation, and that is the whole of it.** *"Reconsider your verdict"* is
unanswerable — nothing changed. *"Is this the text your finding asked for?"* is a narrow
question with a hold/revise answer, and **the filer is the only participant who knows.** Stage 5
turns four verdicts into one sentence; when it misreads one, no other reader can tell.

⚠ **It catches precisely the two failures that ended the measured run.** A reviewer would
recognise its own claim replaced with a checkably false one, and the reviewer whose `correct`
dropped a qualifier carrying a true sentence would see the qualifier gone.

**Cheap, because the mechanism already exists.** It is the re-review channel: `SendMessage` to
roles that still hold their reads, measured at ~2 minutes and ZERO tool calls. Each reviewer
sees only the blocks it filed on, so a 43-block run is FOUR messages.

**It needs no new contract.** The reviewer already holds the census, the code and its own
reasoning; it is given its own record and the resulting text. That is the narrowest contract in
the system, and it resolves the objection above that stage 6's narrow contract may not exist
here — it does, and it is narrower.

⚠ **MARK/APPLY separation is not broken.** The finding is already filed and already read by the
join; the reviewer is not fixing, it is confirming the fix matches what it filed. Same argument
Roy made for showing the competing verdict at re-review: blindness protects the FIRST read and
that is banked.

### ⚠ The two things to get right

**Confirmation bias.** A reviewer shown a patch may wave it through. The question must be
specific — *does the replacement still carry the claim your `EVIDENCE` settles, and is anything
from your `QUOTE` gone?* — not *is this OK*.

**WHERE it sits — ⭐ RULED 2026-08-17: BOTH, and they ask DIFFERENT questions.** Roy: *"I think
it can run before and after stage 6. Stage 5 - is this what you meant. Stage 6 - is this still
correct after my edits. The 4 editor roles i think are well verified roles at this point."*

| | asked after | question | catches |
| --- | --- | --- | --- |
| **5b** | APPLY | *is this what you meant?* | a synthesis that misread a finding |
| **6b** | COMPACT | *is this still correct after my edits?* | compaction that cut what the finding rested on |

⚠⚠ **6b gives stage 6 a checker, which it did not have.** The table at the top of this file
credits stage 6 with an independent reader — and that is the compact agent reading stage 5's
work. **Nothing read the compact agent's own output** until stage 8, after the write. On the
measured run it reached the cap by writing 98-column lines and flagged that itself; nothing
would have caught it if it had not.

⚠ Roy's stated basis for leaning on the reviewers for both: *"the 4 editor roles i think are
well verified roles at this point."* Recorded as the reason, not as a measurement.

### ⭐ RULED: a block stage 6 must edit that NO ROLE ruled on goes to all four

Roy: *"If stage 6 has to edit a block not in the specific review results it sends it back to all
of them for a response/verdict."*

A block every role returned `clean` on can still be over the cap. Compacting it is an edit with
no verdict behind it, and neither 5b nor 6b reaches it — there is no filer to ask. So it is
dispatched to all four as a fresh block, and comes back with verdicts.

⚠ It is the only path by which stage 6 originates work, and it inverts the usual direction:
every other finding travels 4 → 5, this one travels 6 → 4.

## Tasks (continued)

- [x] ⭐ **RULED: (e) runs BEFORE and AFTER stage 6**, asking a different question each time,
      and a block stage 6 must edit that no role ruled on goes to all four. See above.

- [ ] Write the two questions as input contracts. ⚠ They are not interchangeable: 5b asks
      whether the synthesis carried the finding, 6b asks whether compaction broke it. A single
      "is this still right" prompt collapses them and answers neither.

- [ ] Say where they live. `compact.md` owns stage 6 and would own 6b; 5b has no reference file
      because stage 5 has none. ⚠ That absence is itself a finding — stages 1, 2-3 and 5 are the
      only stages with no `references/` file, and 5 is the one this whole task is about.

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
