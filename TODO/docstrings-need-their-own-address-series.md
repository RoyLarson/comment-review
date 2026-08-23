# A docstring needs its own address series, and it names what it documents

```
Status:   open
Progress: 5 of 7 tasks done
Owner:    session * Roy (* 1 ruling -- the numbering)
Requires-Roy: false
Raised:   2026-08-18 (Roy, 2026-08-18, on splitting the census by editorial role)
Unblocked: 2026-08-19 — Requires-Roy cleared: the numbering was ruled 2026-08-19 -- 'a
           is the module, class, function, method definitions in order' -- and the
           a-series ships. The flag means a DECISION is owed; work still remaining is
           what the unchecked boxes already say.
```

## Objective

!! **A DOCSTRING IS ABOUT ITS DECLARATION; A COMMENT IS ABOUT WHAT SITS WITH IT.**
Those are different questions and the `b`/`c` forms cannot express the first.
`b3` means "the gap after code line 3", which reads as prose about what FOLLOWS
-- and a Python docstring sits after its `def` and is about the `def`. Roy,
2026-08-18: *"a docstring is about the thing above not the thing below."*

## The series enumerates DECLARATIONS, not docstrings

Roy, 2026-08-18:

```
a0 - module docstring
a1 - function/class/method_one docstring
a2 - function/class/method_two docstring
```

*"even if the docstrings are currently empty -- the same as any missing bs and
cs are still assigned."*

!! **THAT IS WHY IT CANNOT RENUMBER.** Adding a docstring does not add a
declaration, so filling `a2` moves nothing. Only adding a DECLARATION shifts the
series, and that is a CODE change -- which stage 7b proves byte-identical, so
this tool never makes one.

!! **AND IT IS WHY THE EMPTY ONES ARE THE POINT.** Measured 2026-08-18 on a
four-declaration file, the census emitted TWO docstring blocks while the AST
offered FIVE declarations:

```
a0  <module>       has one
a1  documented     has one
a2  undocumented   NONE  -- no citable place today
a3  Thing          NONE  -- no citable place today
a4  method         NONE  -- no citable place today
```

**Three of five have nowhere to cite a missing docstring.** That is exactly the
hole `an-empty-interval-has-no-census-index` closed for gaps, still open for
declarations: an `add` naming the docstring a function does not have cannot be
written, because there is no block to name.

! It also settles the direction question. The number names the DECLARATION, so
it does not matter that Python's docstring sits after its `def` and Rust's `///`
sits before its `fn` -- verified 2026-08-18, subject ABOVE in one and BELOW in
the other, and neither reading is needed once the series counts declarations.

## What the series buys, and what it does NOT

!! **FOCUS, NOT A SMALLER JOB.** Roy: *"I don't want to make it too easy and they
do have to review all bs and cs but the focus for them gets a lot easier."*
`function-context` and `module-context` still read every `b` and every `c`. The
`a` set is where they START, and it is the prose their remit is written around.

! So this is an ORDERING of the dispatched census, never a filter of it.

**Measured**, 13 shipped scripts, 400 prose blocks: 139 docstrings, 227 comment
runs, 34 trailing comments. The 2,587 empty intervals under the same census are
already collapsed by `census.py --filtered`.

## Where the series can be built, and where it cannot

**Python, today, from the AST** -- the tokenized tier already walks it for
docstring anchors.

! **Every other language needs a declaration list the lexical tier does not
have.** Stage 1.7 probes for a language server, and `documentSymbol` is exactly
this list -- which is what `SKILL.md` already says an LSP buys. Without one, a
repo has no `a` series and a role must be TOLD so rather than handed nothing.
Five of the eleven languages have no docstring notion at all; `go` and `ruby`
attach by position and carry `doc-kind-unresolved`. See
[`doc-is-structural-means-two-things`](doc-is-structural-means-two-things.md).

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

- [x] * **RULED 2026-08-18 by Roy: the series counts DECLARATIONS, and an empty
      one is still assigned.** `a0` is the module, `a1..an` its declarations in
      source order, whether or not each holds a docstring. ! It cannot renumber
      under this tool's edits, because only a code change adds a declaration and
      stage 7b proves the code byte-identical.

- [x] **Enumerate the declarations, in SOURCE order.** `ast.walk` is breadth
      first, so a nested `def` comes back out of position -- order by `lineno`.
      Verify: a file with a method inside a class inside a function numbers the
      same way a reader counts down the page.

- [x] !! **Emit an `a` entry for a declaration with NO docstring.** That is the
      whole point of the series and the thing the census does not do today:
      measured 2026-08-18, a four-declaration file produced two docstring blocks
      and left three declarations with no citable place. Verify: an `add` naming
      the docstring a function does not have resolves through the same path an
      `add` on an empty interval does.

- [x] **The census STATES which declaration a docstring belongs to**, rather
      than the foliation inferring it from position or tier. The direction is
      language-dependent -- Python's subject is the code line ABOVE, Rust's is
      BELOW -- and inference here is the defect this release has spent itself
      removing.

- [x] **Add the `a` form to `foliator.stable`**, and hold it to the same rule
      `--check` applies to `b` and `c`: every address resolves back to the block
      that carries it.

- [ ] **ORDER the dispatched census by series -- do NOT filter it.** Roy,
      2026-08-18: *"I don't want to make it too easy and they do have to review
      all bs and cs but the focus for them gets a lot easier."* Every role still
      reads every prose block; the `a` set is where `function-context` and
      `module-context` START. ! Verify the coverage gate still counts the whole
      prose population per role, so an ordering cannot quietly become a filter.

- [ ] **Say what a repo with NO `a` series gets.** Python builds it from the
      AST; every other language needs `documentSymbol` from stage 1.7's language
      server, and five of the eleven have no docstring notion at all. Verify: a
      role is TOLD the series is empty and why, rather than handed nothing.
