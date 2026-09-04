# A docstring needs its own address series, and it names what it documents

```
Status:   open
Progress: 5 of 9 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-18 (Roy, 2026-08-18, on splitting the census by editorial role)
Unblocked: 2026-08-19 — Requires-Roy cleared: the numbering was ruled 2026-08-19 -- 'a
           is the module, class, function, method definitions in order' -- and the
           a-series ships. The flag means a DECISION is owed; work still remaining is
           what the unchecked boxes already say.
TRIAGED:  2026-08-23 — 2026-08-23. The `a` series SHIPS: measured over the 19 shipped
          scripts, 206 `a` places exist and 203 hold prose. Tasks 1-5 are done. The two
          that remain are the two that were never built -- ORDERING the dispatch, and
          TELLING a role its series is empty -- and both were re-checked today and are
          still absent. ! The Objective carried the same section twice, with two copies
          of one measurement; they are merged, and the counts are re-measured. ! The
          language counts were stale: 18 records now, not 11.
SPLIT:    2026-08-23 -- the two open boxes each held two artifacts. ORDERING split from
          the gate that stops an ordering becoming a filter; TELLING a role split from
          correcting the two shipped sentences that say "The three series".
```

## Objective

!! **A DOCSTRING IS ABOUT ITS DECLARATION; A COMMENT IS ABOUT WHAT SITS WITH IT.**
Those are different questions and the `b`/`c` forms cannot express the first. `b3` means "the gap
after code line 3", which reads as prose about what FOLLOWS -- and a Python docstring sits after
its `def` and is about the `def`. Roy, 2026-08-18: *"a docstring is about the thing above not the
thing below."*

## The series enumerates DECLARATIONS, not docstrings

Roy, 2026-08-18:

```
a0 - module docstring
a1 - function/class/method_one docstring
a2 - function/class/method_two docstring
```

*"even if the docstrings are currently empty -- the same as any missing bs and cs are still
assigned."*

!! **THAT IS WHY IT CANNOT RENUMBER.** Adding a docstring does not add a declaration, so filling
`a2` moves nothing. Only adding a DECLARATION shifts the series, and that is a CODE change --
which stage 7b proves byte-identical, so this tool never makes one.

!! **AND IT IS WHY THE EMPTY ONES ARE THE POINT.** Measured 2026-08-18 on a four-declaration
file, the census emitted TWO docstring blocks while the AST offered FIVE declarations, so three
of five had nowhere to cite a missing docstring. That is the hole
`an-empty-interval-has-no-census-index` closed for gaps. **It is closed for declarations now**:
re-measured 2026-08-23 over the 19 shipped scripts, 206 `a` places exist and 203 hold prose, so
the three undocumented declarations have citable addresses.

! It also settles the direction question. The number names the DECLARATION, so it does not matter
that Python's docstring sits after its `def` and Rust's `///` sits before its `fn` -- verified
2026-08-18, subject ABOVE in one and BELOW in the other, and neither reading is needed once the
series counts declarations.

! `ast.walk` is breadth first, so a nested `def` comes back out of position; the declarations are
ordered by `lineno` instead, which is what T2 closed.

## What the series buys, and what it does NOT

!! **FOCUS, NOT A SMALLER JOB.** Roy, 2026-08-18: *"I don't want to make it too easy and they do
have to review all bs and cs but the focus for them gets a lot easier."* `function-context` and
`module-context` still read every `b` and every `c`. What the series gives them is a place to
START -- the prose that is about a declaration is the prose their remit is written around -- and
an orientation for everything they read afterwards.

! So this is an ORDERING of the dispatched census, never a filter of it. A role handed only its
own series would stop being a review of the file. **That is why T6 and T7 are two boxes**: the
ordering is one artifact and the gate that stops it quietly becoming a filter is another.

! **MEASURED 2026-08-23: the census emits in WALK ORDER, not series order.** `sample.rs` comes
back `f0 f1 a0 a2 b0 b2 b3 b4 a1 c0 b1 c1 c2 c3`.

**RE-MEASURED 2026-08-23**, 19 shipped scripts, 8,738 census rows:

| series | places | holding prose | what it is |
| --- | ---: | ---: | --- |
| `a` | 206 | 203 | docstrings -- where `function-context` and `module-context` begin |
| `b` | 4,056 | 414 | comment runs -- most of `block-context`'s work |
| `c` | 4,037 | 70 | trailing comments -- the rest of it |
| `f` | 38 | -- | the file's own front matter, not a reviewer's |

! The empty places under the same census are already collapsed by `census.py --filtered`. This
series question is about the 687 that hold prose.

## Where it does not apply

MEASURED 2026-08-23 over the 18 language records:

- **Six carry no docstring notion at all** -- `shell`, `sql`, `lua`, `toml`, `ini`, `yaml`: no
  `doc_line`, no `doc_block`, no `doc_is_structural`.
- **`go` and `ruby` attach docs by POSITION**, so the census stamps `comment` and annotates
  `doc-kind-unresolved` rather than deciding. See
  [`doc-is-structural-means-two-things`](doc-is-structural-means-two-things.md).
- **`c` and `cpp` carry `/**` but an EMPTY `declares` list**, so nothing can join. VERIFIED
  2026-08-23: `page_for` on `/** The one doc. */` above `int one(void)` returns `m.c@b0` --
  the doc is a `b`, and the file has NO `a` place at all, not even `a0`.

A repo in any of those has an empty or partial `a` series, and a role must be TOLD that rather
than handed nothing. ! Python builds it from the AST; every other language needs a declaration
list, which stage 1.7's `documentSymbol` is exactly.

! **AND THE TWO SHIPPED SENTENCES SAY OTHERWISE.** `SKILL.md:378` and `reviewer-brief.md:69` both
still read *"The three series"*, and neither mentions an empty one.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- RULED 2026-08-18 by Roy: the series counts
      DECLARATIONS, and an empty one is still assigned. A ruling, kept in the
      Objective.
- [x] T2 | FINISHED | unknown | T2 -- FINISHED. The declarations are enumerated
      in SOURCE order, by `lineno`.
- [x] T3 | FINISHED | unknown | T3 -- FINISHED. An `a` entry is emitted for a
      declaration with NO docstring; the three undocumented ones over the
      shipped scripts are citable.
- [x] T4 | FINISHED | unknown | T4 -- FINISHED. The census STATES which
      declaration a docstring belongs to, via `declares`, rather than the cues
      inferring it from position or tier.
- [x] T5 | FINISHED | unknown | T5 -- FINISHED. The `a` form is in
      `addresser.stable`, and `--check` holds it to the same rule as `b` and
      `c`.
- [ ] T6 | T6 -- ORDER the dispatched census by series -- `a`, then `b`, then
      `c` -- and do NOT filter it. Verify: a dispatched census reads `a` first,
      then `b`, then `c`.
- [ ] T7 | T7 -- Hold the ordering to not becoming a filter. Verify:
      `verdicts.py`'s coverage gate still counts the whole prose population per
      role after T6 lands.
- [ ] T8 | T8 -- Tell a role when its `a` series is empty, and why. Verify: a
      run over a `.sh` file hands the role that sentence.
- [ ] T9 | T9 -- Correct the two "The three series" sentences at `SKILL.md:378`
      and `reviewer-brief.md:69`. Verify: neither states three series
      unconditionally.
