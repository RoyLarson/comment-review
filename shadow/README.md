# The shadow suite

**Invariants derived from the code, checked over real inputs.** Built overnight
on 2026-08-25 at Roy's instruction, without copying or reading `tests/`.

```bash
uv run pytest shadow/            # the whole suite, and nothing from tests/
uv run pytest shadow/ -q         # 735 cases, ~0.7s
```

!! **IT IS NOT COLLECTED BY DEFAULT.** `pyproject.toml` sets
`testpaths = ["tests"]`, so this runs only when named. That is deliberate: it
earns its place before it joins the gate. **Verified: `pytest shadow/` collects
735 cases and ZERO from `tests/`.**

## Why it exists

Roy, 2026-08-25: *"866 tests are likely garbage piling up with maybe 50 good
ones in the mix."* The night before, three changes each broke something real and
were noticed by **zero** tests:

| what changed | tests that noticed |
| --- | --- |
| fences stopped being emitted to agents | 0 |
| eleven fields left the census row | 0 |
| `text` renamed, breaking EVERY finding | 0 |

The mechanism was the same each time. **The fixtures are hand-authored in the
shape the code expects, by whoever wrote the code, so they can only confirm.**
When the contract moved the fixtures did not, and they went on asserting that
the old contract was met -- because they still supplied the old fields.

That is not 866 independent tests. It is one assumption, restated 866 times.

## What is different here

**94 test functions, 735 executions.** A small set of invariants, each checked
over many real inputs -- rather than one test per remembered incident.

- **Nothing is hand-built where the system can build it.** Pages come from
  `page_for` over real source; binders come from `bind`. The one place a literal
  appears is a refusal case, where the point is that the input is malformed.
- **Every asserted value was OBSERVED first.** Where a test states what a
  paragraph holds, that came from running the code and looking.
- **Completeness is asserted, not assumed.** Every galley case states the exact
  set of places allowed to differ, so an edit that also disturbed a neighbour
  fails even though its own place is right.

## Scope

Two chains, and they are independent. Roy: *"Reading -> binder. Page -> galley ->
compositor. The binder is not going through the galley."*

| file | chain |
| --- | --- |
| `test_reading.py` | a file becomes a page -- partition, ordering, addresses |
| `test_addressing.py` | the naming scheme, and the series definition |
| `test_binder.py` | reading -> binder: what an agent is handed |
| `test_galley.py` | page -> galley: every cue type x every operation |
| `test_compositor.py` | page -> compositor: 54 forms, in equals out |

**OUT OF SCOPE, deliberately:**

- **the desk, the verdicts, the join.** Roy: *"There is code there none of it is
  correct so testing it is solidifying wrong."*
- **the front-matter/`b` collision** -- a file whose front matter is not on line
  1. A ruled normalisation; a test over it would pin the sacrifice.

## The update matrix

`test_galley.py` covers **every series x every operation**, discovering the
target cue from the page rather than hardcoding it:

| | `a` | `b` | `c` | `f` |
| --- | --- | --- | --- | --- |
| modify a filled place | yes | yes | yes | yes |
| drop it (empty string) | yes | yes | yes | yes |
| add to an ABSENT place | yes | yes | yes | yes |

Each asserts the place changed, **and that nothing else did** -- including the
fences, which have their own rule: a drop vacates the fence it owns, and a `c`
owns none.

## Does it catch more?

Measured by mutating the source and running both suites. `tests/` was already
red at the time (16 baseline failures, mid-refactor), so only the DELTA counts.

| mutation | `tests/` | `shadow/` |
| --- | --- | --- |
| the binder drops `kind` from every row | +0 | **+2** |
| the binder repeats `path` on every row | +0 | **+2** |
| a `c` drop vacates leading it does not own | +0 | **+2** |
| line endings always LF | +3 | +7 |
| the trailing newline is always added | +2 | +4 |
| a non-text replacement is accepted | +5 | +12 |
| a drop no longer vacates the fence below it | +3 | +1 |
| `series` answers a blank instead of raising | +3 | +1 |
| census emits fences again | +2 | +0 |

**Three defects only this suite catches**, and they are exactly the class that
broke on 2026-08-24: wire-format changes, and the `c`/leading rule.

! **THE LAST ROW IS NOT A GAP.** `bind()` filters fences itself, so removing
`carried()` does not change the binder -- what `tests/` caught was the LISTING,
which is a text rendering and out of scope here. It did surface a real
redundancy: `bind()` and `carried()` state the same rule twice. Filed.

## What it found on its first run

- **`go`, `ruby` and `lua` place a declaration's documentation at an `a` cue and
  type it `comment`** -- the `b` series' kind. One row making two claims about
  itself. Held as three strict `xfail`s, so fixing it turns them red and prompts
  their removal. Filed as `TODO/a-doc-comment-is-cued-a-and-typed-b.md`.
- **`bind()` and `carried()` both filter fences**, with the identical predicate.
  Filed as `TODO/two-filters-for-one-fence-rule.md`.
