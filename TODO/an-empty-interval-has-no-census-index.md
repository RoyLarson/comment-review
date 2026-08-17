# An empty interval has no census index, so `add` has no block to cite

```
Status:   open
Progress: 0 of 9 tasks done
Owner:    session
Raised:   2026-08-15 (Roy ruled (a): every interval is a block, empty ones included)
```

## Objective

**A block is the interval between two lines of code** — settled 2026-08-15, and the prose now
says so. But the census still enumerates from PROSE: it emits a block where it finds a comment
run or a docstring, so an interval with nothing in it produces no entry and therefore has no
index. Measured: three adjacent code lines with nothing between them census as **0 blocks**.

That is the whole reason `add` does not fit the finding record. `add` says *a constraint exists
in code and nowhere in prose* — the finding is about an EMPTY interval — yet `BLOCK` is required
and coverage is computed from it, so an `add` must borrow a neighbouring index today.

Roy ruled **(a)**: enumerate every interval, empty ones included. He named the cost himself —
*"I don't see a way around this pseudo-concrete syntax tree and I don't think it matters"* — and
separately ruled that run data is not what the budget protects, which `docs/limitations.md` now
records.

⚠ **This is not vocabulary and is deliberately not on that branch.** The definition was
vocabulary and is done; this is the census change that follows from it.

## Tasks

- [ ] Enumerate every interval between two code lines, including empty ones. Today
      `blocks_stdlib` / `blocks_lexical` emit only where prose exists. Measured for scale:
      re-measured 2026-08-16, after `census.py` was split into three modules: `census.py` is
      768 lines, ~624 of them code, and censuses as **44 blocks** — under (a) it is ~624.
      `verdicts.py`: 535 lines, ~426 code, **23 blocks** today.

- [ ] Define **"a line of code"** per tier, because the two tiers cannot answer the same
      question. `tokenized` has an AST; `lexical` has only a comment-syntax record, so a line of
      code is whatever is neither comment nor blank. State both, and state that a block's
      boundaries are therefore tier-dependent while its CONTENT is not.

- [ ] Decide what bounds the FIRST and LAST interval in a file. There is no code line above a
      module docstring or a file header, and none below a trailing comment at EOF. Either the
      file boundary counts as a bound, or those two intervals are special-cased — say which.

- [ ] Reconcile with the block kinds that are not intervals. A `docstring` is owned by a
      declaration, and a `trailing-comment` shares a line with code rather than sitting between
      two. Both are blocks today. Say whether they are intervals under the new definition or a
      second kind of block that coexists with it.

- [ ] Update coverage and the `CLEAN` range line in `references/reviewer-brief.md`. A reviewer
      must account for every index, and the count rises roughly tenfold. ⚠ **Check what this
      does to the cheapest fabrication.** The brief already records that a report reading only
      `CLEAN 1-N` accounts for everything, cites nothing, and exits 0 having read no file. If
      nine in ten blocks are empty, that report becomes MORE plausible, not less — decide
      whether the gate needs a compensating check before the count changes.

- [ ] Check the STANDS arithmetic and the acquittal rate. `verdicts.py`'s STANDS set is
      `all_blocks - ruled`, and `module-context` measures an acquittal rate whose denominator is
      blocks. Both shift by an order of magnitude when most blocks are empty, and neither states
      a denominator today.

- [ ] Give `add` its block, which is the point of the change: the empty interval where the
      prose should go. Then close the ⭐ on `add` in
      [`the-finding-record-is-eight-fields-and-six-would-do`](the-finding-record-is-eight-fields-and-six-would-do.md),
      which is blocked on exactly this.

- [ ] ⭐ Relitigate the name **ANNOTATE** once the pCST exists. Roy, 2026-08-16: *"I think at a
      future time we might relitigate the word ANNOTATE. It seems close but not quite correct
      for the stage that is about turning the code into the pCST and finding external
      references."* Deliberately deferred — the name should be chosen against what the stage
      does once it builds intervals rather than prose runs, not before. ⚠ Stage 2 keeping the
      name is what made `annotation` the right word for the census's marks; if ANNOTATE moves,
      check that pairing still holds.

- [ ] Re-measure the census afterwards and record it. Today `census.py --json` over `census.py`
      is 36,777 bytes for 44 blocks (~836 bytes each, re-measured 2026-08-16); an empty interval
      carries no text, `raw_lines` or annotations, so ~203 bytes each puts the ~580 empty ones
      near 118 KB. ⚠ Record
      it as a fact, not as a budget question — `docs/limitations.md` states that rule files are
      budgeted and run data is not.
