# doc_is_structural means two things and its docstring names one

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-18 (Roy, 2026-08-18, asking whether docstrings are separable per
          language)
RE-CHECKED: 2026-08-23 — 2026-08-23. Both tasks are still live and both are now
            verified by running the code rather than reading it. The language count in
            this file was stale: 18 language records, not 11, and the shipped comment
            already says "seventeen of the eighteen". The three that set the flag are
            unchanged -- python, go, ruby -- and go and ruby still declare no doc
            marker, so the failure is still LATENT. ! The latent case was reproduced
            directly against `lexer.block_text`, so it is no longer a forecast.
```

## Objective

!! **ONE FLAG, TWO PROPERTIES, AND THE DOCSTRING NAMES ONLY ONE.** `lexer.block_text`
(`lexer.py:609-649`) documents `structural` as *"whether this language's doc is a STRING IN A
DECLARATION'S BODY (Python) rather than a marked comment run"* (`:634-635`), and states outright
at `:643-644`: *"Only Python's docstring is a string in a declaration's body, which is what
`doc_is_structural` records."*

MEASURED 2026-08-23 over `language.LANGUAGES` (18 records): exactly three set the flag --
`python`, `go`, `ruby`. Two of them are not strings in a body. What Go and Ruby actually share is
that **docs attach BY POSITION** -- a run touching a declaration is documentation -- which is a
different property, and it is the property `lexer.flag_structural_docs` (`:1453-1494`) reads the
same flag for.

| language | a string in a declaration's body | docs attach by position |
| --- | --- | --- |
| python | yes | -- |
| go | **no** | yes |
| ruby | **no** | yes |

## Not live, and one row away from being live

`block_text` routes `kind == "docstring" and structural` to `docstring_text`, which strips
QUOTES. No Go or Ruby block ever reaches it: MEASURED 2026-08-23, both have `doc_line=()` and
`doc_block=()`, and the lexical tier stamps `docstring` only on a run opening with one.

!! **So the guard is an ABSENCE, not a check -- and the failure reproduces the moment the
absence ends.** VERIFIED 2026-08-23, calling the function directly:

```
block_text("docstring", ["/// The one doc.", "/// Second line."], ("///", "//"), True)
    -> '/// The one doc. /// Second line.'          the marker survives into the prose
block_text("docstring", ["/// The one doc.", "/// Second line."], ("///", "//"), False)
    -> 'The one doc. Second line.'
```

That is exactly what the same comment warns about at `:641-643`: *"Reading them as literals
leaves the marker in the prose and refuses every doc comment in seventeen of the eighteen
languages."*

! The row that would do it is one line. `rust` sits directly above `go` in `LANGUAGES` and
carries `doc_line=("///", "//!")`; adding `doc_is_structural=True` to a `doc_line` language --
or `doc_line` to `go` -- is the whole change. Adding a language is documented as *"data, no
code"*, which is the reason to fix this: the row is where someone will add both fields, and
nothing says they cannot.

! **The dispatch is by FILE SUFFIX, so the census cannot catch it either.** `desk.as_block`
(`desk.py:377-386`) takes `structural = lang.doc_is_structural` from `language_for(path)` and
hands it straight to `block_text`. Nothing between the language record and the strip asks whether
the two fields are compatible.

## What was verified, 2026-08-18, and re-verified 2026-08-23

Real files, one per language:

```
m.rs   docstring  markers stripped        -- separable by syntax
m.go   comment    doc-kind-unresolved     -- position, and the census says so
m.rb   comment    doc-kind-unresolved     -- position, and the census says so
```

! The census is HONEST about Go and Ruby: it stamps `comment`, annotates `doc-kind-unresolved`
and notes the run *"may be documentation governed by FORMAT rather than a comment governed by
LENGTH ... NOT counted against the cap"*. The defect is in what the FIELD claims, not in what the
census emits.

! **A rule proposed for a role file goes to**
  [`role-rule-register`](role-rule-register.md) **and is decided with the others.**
  Role prose is budget-fixed, so a candidate is judged against what it displaces.

## Tasks

- [ ] T1 -- SPLIT the field, or rename it and correct the docstring. `lexer.py:634-635` and
      `:643-644` document it as "a STRING IN A DECLARATION'S BODY (Python)" and say only Python
      is one, while `go` and `ruby` set it for a different property -- docs attach BY POSITION,
      which is what `flag_structural_docs` reads it for. Verify: `grep -n "doc_is_structural"
      plugins/comment-review/skills/comment-review/scripts/*.py` shows each reader naming the
      property it uses, and no comment claims Python is the only language that sets it.

- [ ] T2 -- REFUSE OR ROUTE the latent case, which reproduces today. Verify: a language record
      carrying both `doc_line` (or `doc_block`) and `doc_is_structural=True` is refused where
      the record is built, OR `block_text` routes on a property that separates the two -- and
      `block_text("docstring", ["/// x"], ("///", "//"), True)` no longer returns text with
      `///` still in it. ! The guard today is that no shipped row sets both; nothing enforces it.
