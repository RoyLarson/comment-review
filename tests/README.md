# The test suite

**Invariants derived from the code, checked over real inputs.**

```bash
uv run pytest            # 873 passed, 1 skipped, 3 xfailed, 451 subtests, ~1.6s
                         # the skip needs symlinks; it runs where they exist.
                         # the subtest count moves with `TODO/`: three per open
                         # file, from `gates/test_todo_counts_agree.py`
```

## How it got here

Built overnight on 2026-08-25 as `shadow/`, deliberately **without reading the
suite it replaced**, then swapped in. Roy: *"Delete the old test suit put in the
new one."*

The old suite was 866 tests. Three changes on 2026-08-24 each broke something
real and were noticed by **zero** of them:

| what changed | tests that noticed |
| --- | --- |
| fences stopped being emitted to agents | 0 |
| eleven fields left the census row | 0 |
| `text` renamed, breaking EVERY finding | 0 |

One mechanism each time: **the fixtures were hand-authored in the shape the code
expected, by whoever wrote the code, so they could only confirm.** When the
contract moved, the fixtures did not -- and they went on supplying the old
fields and asserting the old contract was met. That is not 866 independent
tests; it is one assumption restated 866 times.

## What is different

**218 test functions, collected as 877 tests.** A small set of invariants, each
checked over many real inputs -- rather than one test per remembered incident.

- **Nothing is hand-built where the system can build it.** Pages come from
  `page_for` over real source; binders from `bind`. A literal appears only in a
  refusal case, where malformed IS the input.
- **Every asserted value was OBSERVED first**, by running the code and looking.
- **Completeness is asserted.** Every galley case names the exact set of places
  allowed to differ, so an edit that also disturbed a neighbour fails even
  though its own place is right.

## The files

| file | what it holds to |
| --- | --- |
| `test_reading.py` | a file becomes a page -- partition, ordering, addresses |
| `test_addressing.py` | the naming scheme, and the series definition |
| `test_binder.py` | reading -> binder: what an agent is handed |
| `test_galley.py` | page -> galley: every cue type x every operation |
| `test_compositor.py` | page -> compositor: 54 forms, in equals out |
| `gates/` | does a GATE still bite -- the build, the release, the floor |

`gates/` is the part of the old suite that survived, because it asks a different
question: it tests `scripts/` and the release rather than the code under
redesign.

## Two chains, and they are independent

Roy, 2026-08-25: *"Reading -> binder. Page -> galley -> compositor. The binder is
not going through the galley."* The write path re-reads each page from disk,
because it needs the FULL page -- fences included -- and none of what a binder
carries.

## What is deliberately NOT tested

- **The desk, the verdicts, the record.** Roy: *"There is code there none of it is
  correct so testing it is solidifying wrong."* That code now lives in
  `prototype/`.
- **The front-matter/`b` collision** -- a file whose front matter is not on line
  1. A ruled normalisation; a test over it would pin the sacrifice.

## The update matrix

`test_galley.py` covers **every series x every operation**, discovering the
target cue from the page rather than hardcoding it:

| | `a` | `b` | `c` | `f` |
| --- | --- | --- | --- | --- |
| modify a filled place | yes | yes | yes | yes |
| drop it (empty string) | yes | yes | yes | yes |
| add to an ABSENT place | yes | yes | yes | yes |

Each asserts the place changed **and that nothing else did** -- including the
fences, which have their own rule: a drop vacates the fence it owns, and a `c`
owns none.

## Does it catch more?

Measured by mutating the source and running both suites while both existed.
`tests/` was mid-refactor and already red, so only the DELTA counts.

| mutation | old | new |
| --- | --- | --- |
| the binder drops `kind` from every row | +0 | **+2** |
| the binder repeats `path` on every row | +0 | **+2** |
| a `c` drop vacates leading it does not own | +0 | **+2** |
| line endings always LF | +3 | +7 |
| the trailing newline is always added | +2 | +4 |
| a non-text replacement is accepted | +5 | +12 |

Three defects only this suite catches, and they are exactly the class that broke
on 2026-08-24.

## The three xfails are a tripwire

`go`, `ruby` and `lua` place a declaration's documentation at an `a` cue and type
it `comment` -- the `b` series' kind. Held as **strict** xfails, so fixing it
turns them red and demands their removal rather than leaving them green and
forgotten. Filed as `TODO/a-doc-comment-is-cued-a-and-typed-b.md`.
