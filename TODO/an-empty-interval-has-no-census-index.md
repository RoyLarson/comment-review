# An empty interval has no census index, so `add` has no block to cite

```
Status:   open
Progress: 0 of 8 tasks done
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
      `census.py` is 1044 lines, 606 of them code, and censuses as **59 blocks** — under (a)
      it is ~606. `verdicts.py`: 617 lines, 388 code, **28 blocks** today.

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

- [ ] Check the clean-arithmetic and the acquittal rate. `verdicts.py`'s STANDS set is
      `all_blocks - ruled`, and `module-context` measures an acquittal rate whose denominator is
      blocks. Both shift by an order of magnitude when most blocks are empty, and neither states
      a denominator today.

- [ ] Give `add` its block, which is the point of the change: the empty interval where the
      prose should go. Then close the ⭐ on `add` in
      [`the-finding-record-is-eight-fields-and-six-would-do`](the-finding-record-is-eight-fields-and-six-would-do.md),
      which is blocked on exactly this.

- [ ] Re-measure the census afterwards and record it. Today `census.py --json` over `census.py`
      is 60,503 bytes for 59 blocks (~1,025 bytes each); an empty interval carries no text,
      `raw_lines` or marks, so ~203 bytes each puts the ~547 empty ones near 111 KB. ⚠ Record
      it as a fact, not as a budget question — `docs/limitations.md` states that rule files are
      budgeted and run data is not.
