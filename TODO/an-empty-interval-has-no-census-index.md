# An empty interval has no census index, so `add` has no block to cite

```
Status:   open — the census change is DONE 2026-08-17; what is left is a NAMING
          ruling, which is Roy's
Progress: 8 of 10 tasks done
Owner:    session · Roy (⭐ 1 ruling, deferred by him and now unblocked)
Raised:   2026-08-15 (Roy ruled (a): every interval is a block, empty ones included)
```

## Objective

**A block is the interval between two lines of code** — settled 2026-08-15, and the prose said
so while the census still enumerated from PROSE: it emitted a block where it found a comment
run or a docstring, so an interval with nothing in it produced no entry and therefore had no
index. Measured: three adjacent code lines with nothing between them censused as **0 blocks**.

That was the whole reason `add` did not fit the finding record. `add` says *a constraint exists
in code and nowhere in prose* — the finding is about an EMPTY interval — yet `BLOCK` is required
and coverage is computed from it, so an `add` had to borrow a neighbouring index.

⚠ **DONE 2026-08-17**, except the naming ruling in the last task.

Roy ruled **(a)**: enumerate every interval, empty ones included. He named the cost himself —
*"I don't see a way around this pseudo-concrete syntax tree and I don't think it matters"* — and
separately ruled that run data is not what the budget protects, which `docs/limitations.md` now
records.

⚠ **This is not vocabulary and is deliberately not on that branch.** The definition was
vocabulary and is done; this is the census change that follows from it.

## Tasks

- [x] Enumerate every interval between two code lines, including empty ones — `intervals()`
      in `census.py`, run from `census_for` after the prose blocks are built. A gap that HOLDS
      a comment run is that run's block already, so only the empty ones are emitted and the
      census stays one block per interval either way. ⚠ **Measured 2026-08-17:** `census.py`
      over itself is 847 lines and **546 blocks**, 48 of them prose — up from 44.

- [x] Define **"a line of code"** per tier — `code_lines()` states it: a line is code when it
      holds something that is not blank and not prose. The tiers differ on the DOCSTRING, which
      is the whole of the difference: `tokenized` knows a string literal is a declaration's
      documentation and `lexical` knows only what its comment-syntax record spells. So a
      block's BOUNDS are tier-dependent while its CONTENT is not, and the docstring says so.
      ⚠ A `trailing-comment` sits ON a code line, so that line stays code.

- [x] Decide what bounds the FIRST and LAST interval in a file — ⚠ **the FILE BOUNDARY counts
      as a bound.** Special-casing them would have left a module docstring and a comment at EOF
      in no interval at all, which is the hole this whole file is about. A file with no code is
      therefore one interval. Tested on both ends.

- [x] Reconcile with the block kinds that are not intervals — they COEXIST, and `kind` is
      what tells them apart. A `docstring` and a `comment` occupy their lines entirely, so those
      lines are not code and the block IS its interval. A `trailing-comment` shares a line with
      code, so its line stays code and it hangs off that line rather than sitting between two.
      An `interval` occupies nothing. ⚠ That last one is what makes `code_lines` safe to run
      over a census that already holds intervals.

- [x] Update coverage in `references/reviewer-brief.md` — ⚠⚠ **ADDRESSABLE is not
      ACCOUNTABLE, and that is the ruling the fabrication question forces.** A reviewer returns
      a record for every block that HOLDS PROSE; an empty interval is there to be CITED, not
      accounted for. Owing a record on all 546 would have made `CLEAN 1-N` — the cheapest
      fabrication there is — nine parts in ten true, which is the compensating check this task
      asked for and the reason coverage did not simply widen. `verdicts.py` computes
      `all_blocks` from `kind != "interval"`; the range line was already deleted by an earlier
      ruling, so there was none left to update.

- [x] Check the STANDS arithmetic — it reads `all_blocks`, which is now the PROSE blocks, so
      it did not shift at all: an empty interval nobody wrote about is not standing unchanged,
      it is empty. The join's first line states both denominators rather than one. ⚠ The
      `acquittal` rate named here no longer exists; `acquittal` was deleted from the vocabulary
      on 2026-08-16 as a term that arrived from LAW.

- [x] Give `add` its block — done, and the ⭐ in
      [`the-finding-record-is-eight-fields-and-six-would-do`](the-finding-record-is-eight-fields-and-six-would-do.md)
      is closed with it. An `add` cites the empty interval the prose belongs in; it no longer
      borrows a neighbour's index and no longer reads as being about that neighbour's text.

- [ ] ⭐ **`pCST` and `prose tree` now name ONE thing, and only one should.** Before
      2026-08-17 the two were distinguishable: the pCST was every interval as a node, and the
      prose tree was "what the census IS today", a node per comment run and per docstring. The
      census now builds the first, so the second's definition had to be rewritten into it.
      ⚠ Which name survives is a NAMING ruling. `pCST` is precise and is the word Roy used;
      `prose tree` is the one every shipped file says. Whichever goes, the loser belongs in the
      retired-words table with the reason.

- [x] ⭐ **RULED 2026-08-17: stage 2 is COLLATE.** Was: relitigate the name **ANNOTATE**. Roy,
      2026-08-16: *"I think at a future time we might relitigate the word ANNOTATE. It seems
      close but not quite correct for the stage that is about turning the code into the pCST
      and finding external references."* The name was to be chosen against what the stage does
      once it builds intervals rather than prose runs, and on 2026-08-17 it does. ⚠ **The pairing check this
      task called for came back BETTER, not neutral.** `annotation` was ruled in for two
      reasons and only one was the stage name — the other, that an editorial MARK is what an
      editor writes on a manuscript while the census's are mechanical observations, stands on
      its own. And the rename ends a real collision: ANNOTATE named stage 2 while `annotate.py`
      performs stage 3, so one word pointed at two stages.

- [x] Re-measure the census afterwards and record it — ⚠ **measured 2026-08-17:**
      `census.py --json` over `census.py` is **177,615 bytes for 546 blocks**, against 36,777
      bytes for 44 before. The estimate here was ~118 KB and it was low. Recorded as a fact, not
      as a budget question — `docs/limitations.md` states that rule files are budgeted and run
      data is not.
