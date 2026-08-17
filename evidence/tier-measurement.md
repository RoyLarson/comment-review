# What a structural tier bought, and why it was removed

Measured 2026-08-14 over the nine corpus files that produced the README's
numbers -- 160 comment blocks, both tiers run over identical input in one
process.

## The result

| | structural (libcst) | tokenized (stdlib) |
| --- | --- | --- |
| comment blocks given an OWNER | 80 of 160 (50%) | 0 |
| blocks MISSED that the other tier found | **13** | 0 |

Ownership was real: half of every comment block in the corpus gained a
recorded owner, and without one the locality angle answers by reading the file
-- a judgement no field records and nothing downstream can check.

Coverage was the problem, and it is one-sided. libcst attaches comments through
a node's `leading_lines`, and a comment inside an expression belongs to no such
sequence:

```python
"resolvedInNextRelease": GroupStatus.UNRESOLVED,
# TODO(dcramer): remove in 9.0     <- absent from the structural census
"muted": GroupStatus.IGNORED,
```

Thirteen blocks vanished this way across nine files, including a file-header
copyright block at `fwupd.py:1` -- the first prose in the file, not an edge
case.

## Why that decided it

**A block missing from the census is a block nobody reviews.** An unresolved
owner produces a weaker verdict; an absent block produces no verdict and no gap
report. The second failure is worse and it is silent.

! **And the tier was selected by whether an unrelated package happened to be
importable.** `libcst` is a common transitive dependency, so the same command
on two machines could census different sets of blocks, with the lossy path
being the one labelled most trustworthy. A review tool whose coverage depends
on the ambient environment cannot report coverage.

**The deciding argument was neither.** Roy, 2026-08-14: libcst is Python-only,
and the corpus this tool is meant to grow into is not. A structural tier for
one language out of eleven buys ownership on the one language while every other
still answers locality by reading -- so the gap it closes is narrow, and paying
for it in silent coverage loss is the wrong trade.

## What the measurement fixed on the way

Comparing two tiers over identical input found three defects, each of which had
been live in every published measurement:

- **libcst split comment runs on blank lines.** A 41-line block read as 19 + 22
  -- the cap evasion the CODE-bounded rule exists to refuse, arriving in the
  tier a reviewer trusts most.
- **The stdlib tier stored the whole source line as a block's prose.** A
  trailing comment's own code went to the mark regexes as the comment's text.
- **A trailing comment never closed its run.** Its code sits before it, so no
  later token flushed it, and the run absorbed the next leading block across
  two blank lines -- gluing two unrelated comments into one.

The first is gone with libcst. The other two are fixed and remain fixed.

## Reproducing it

The instrument compared `blocks_cst` against `blocks_stdlib` over the same
file in one process, keyed blocks on `(path, start, end, kind)`, and reported
set difference in both directions plus the count of comment blocks gaining an
owner. Both are gone with the libcst path; recover them from the commit that
removed it if the question is ever reopened.

**Reopen it if** a structural tier lands that covers expression-level comments,
or if tree-sitter arrives and makes the same ownership available across
languages rather than for Python alone. The number to beat is **zero blocks
missed** -- ownership is worth nothing if coverage is not total.
