# A docstring needs its own address series, and it names what it documents

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session * Roy (* 1 ruling -- the numbering)
Requires-Roy: true
Raised:   2026-08-18 (Roy, 2026-08-18, on splitting the census by editorial role)
```

## Objective

!! **A DOCSTRING IS ABOUT ITS DECLARATION; A COMMENT IS ABOUT WHAT SITS WITH IT.**
Those are different questions, and the `b`/`c` forms cannot express the first.
`b3` means "the gap after code line 3", which reads as prose about what FOLLOWS
-- and a Python docstring sits after its `def` and is about the `def`. Roy,
2026-08-18: *"a docstring is about the thing above not the thing below."*

! The direction is LANGUAGE-DEPENDENT, which is why the position cannot carry
it. Verified the same day:

```
p.py   docstring line 2   nearest code ABOVE = 1  (`def add`)    subject is ABOVE
m.rs   docstring line 1   nearest code BELOW = 2  (`pub fn add`) subject is BELOW
```

**Naming the code line it DOCUMENTS dissolves the direction.** Both of those are
`a1`, because both name the declaration rather than a side of it.

## What the series buys, and what it does NOT

!! **FOCUS, NOT A SMALLER JOB.** Roy, 2026-08-18: *"I don't want to make it too
easy and they do have to review all bs and cs but the focus for them gets a lot
easier."* `function-context` and `module-context` still read every `b` and every
`c`. What the series gives them is a place to START -- the prose that is
about a declaration is the prose their remit is written around -- and an
orientation for everything they read afterwards.

! So this is an ORDERING of the dispatched census, never a filter of it. A role
handed only its own series would stop being a review of the file.

**Measured 2026-08-18**, 13 shipped scripts, 400 prose blocks:

| series | blocks | what it is |
| --- | ---: | --- |
| `a` | 139 | docstrings -- where `function-context` and `module-context` begin |
| `b` | 227 | comment runs -- most of `block-context`'s work |
| `c` | 34 | trailing comments -- the rest of it |

! 2,587 empty intervals sit under the same census and are already collapsed by
`census.py --filtered`. This series question is about the 400 that hold prose.

## Where it does not apply

Five of the eleven languages have no docstring notion at all -- shell, sql, lua,
toml-ini, yaml -- and `go` and `ruby` attach docs by POSITION, so the census
stamps `comment` and annotates `doc-kind-unresolved` rather than deciding. A
repo in any of those has an empty `a` series, and a role must be told that
rather than handed nothing. See
[`doc-is-structural-means-two-things`](doc-is-structural-means-two-things.md).

## Tasks

- [ ] * **Rule the numbering: `aN` = the code line it DOCUMENTS, not the Nth
      docstring.** Sequential `a1..an` renumbers when a docstring is added earlier
      -- the ordering fragility already refused once for `b`. Numbering by the
      documented code line is a pure function of the block, and direction-free:
      Python's docstring sits after its `def` and Rust's `///` before its `fn`,
      and both name the declaration. Verified 2026-08-18: both give `a1`.
- [ ] !! **The census must STATE which code line a docstring documents.** The
      direction is language-dependent -- Python's subject is the nearest code line
      ABOVE, Rust's is BELOW -- and the addresser can only infer it from `tier`,
      which is the consumer-infers-what-the-producer-knows defect this release has
      been removing. Verify: a block carries the documented line, and a language
      whose docs sit on the other side needs no addresser change.
- [ ] **Add the `a` form to `addresser.stable`**, and make `--check` hold it to
      the same rule as `b` and `c`: every address resolves back to the block that
      carries it.
- [ ] **ORDER the dispatched census by series -- do NOT filter it.** Roy,
      2026-08-18: *"I don't want to make it too easy and they do have to review all
      bs and cs but the focus for them gets a lot easier."* Every role still reads
      every prose block; the `a` set is where `function-context` and
      `module-context` START. ! Verify the coverage gate still counts the whole
      prose population per role, so an ordering cannot quietly become a filter.

- [ ] **Say what a language with NO docstring notion does.** Five of the eleven --
      shell, sql, lua, toml-ini, yaml -- have no `a` series at all, and go and
      ruby carry `doc-kind-unresolved` rather than a kind. Verify: a role given
      the `a` set on such a repo is told the set is empty and why, not handed
      nothing.
