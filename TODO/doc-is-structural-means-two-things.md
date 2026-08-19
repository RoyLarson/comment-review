# doc_is_structural means two things and its docstring names one

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-18 (Roy, 2026-08-18, asking whether docstrings are separable per
          language)
```

## Objective

!! **ONE FLAG, TWO PROPERTIES, AND THE DOCSTRING NAMES ONLY ONE.** `block_text`
documents `doc_is_structural` as *"whether this language's doc is a STRING IN A
DECLARATION'S BODY (Python) rather than a marked comment run"*, and states
outright: *"Only Python's docstring is a string in a declaration's body, which is
what `doc_is_structural` records."*

Three languages set it: `python`, `go`, `ruby`. Two of them are not strings in a
body. What Go and Ruby actually share is that **docs attach BY POSITION** -- a
run touching a declaration is documentation -- which is a different property
that the same flag is also used for, in `_positional_docs`.

| language | a string in a declaration's body | docs attach by position |
| --- | --- | --- |
| python | yes | -- |
| go | **no** | yes |
| ruby | **no** | yes |

## Not live, and one row away from being live

`block_text` routes `kind == "docstring" and structural` to `docstring_text`,
which strips QUOTES. No Go or Ruby block ever reaches it, because neither
declares a `doc_line` or `doc_block` and the lexical tier stamps `docstring`
only on a run opening with one.

!! **So the guard is an absence, not a check.** Adding `doc_line=("///",)` to a
language that also attaches by position -- which is what Rust looks like, and
Rust is one row above Go in the table -- would read a comment run as a string
literal. The same comment warns about exactly that outcome: *"Reading them as
literals leaves the marker in the prose and refuses every doc comment in ten of
the eleven languages."*

! Adding a language is documented as *"data, no code"*. That is the reason to
fix this: the row is where someone will add both fields, and nothing says they
cannot.

## What was verified, 2026-08-18

Real files, one per language:

```
m.rs   docstring  markers stripped        -- separable by syntax
m.go   comment    doc-kind-unresolved     -- position, and the census says so
m.rb   comment    doc-kind-unresolved     -- position, and the census says so
```

! The census is HONEST about Go and Ruby: it stamps `comment`, annotates
`doc-kind-unresolved`, and notes the run *"may be documentation governed by
FORMAT rather than a comment governed by LENGTH ... NOT counted against the
cap"*. The defect is in what the FIELD claims, not in what the census emits.

! **A rule proposed for a role file goes to**
  [`role-rule-register`](role-rule-register.md) **and is decided with the others.**
  Role prose is budget-fixed, so a candidate is judged against what it displaces.

## Tasks

- [ ] **Split the field, or rename it and correct the docstring.** `block_text`
      documents it as "the doc is a STRING IN A DECLARATION'S BODY (Python)" and
      says "Only Python's docstring is a string in a declaration's body, which is
      what `doc_is_structural` records" -- while `go` and `ruby` both set it,
      meaning something else entirely: docs attach BY POSITION. Two properties,
      one flag, and the prose names only the first.
- [ ] **Verify the latent case before it becomes live.** `block_text` routes `kind
      == "docstring" and structural` to `docstring_text`, which strips QUOTES. A
      Go block never reaches it today because Go declares no `doc_line` or
      `doc_block`, so nothing stamps it `docstring` -- add one and a `//` run is
      read as a string literal, which is the failure that same comment warns
      about: "Reading them as literals leaves the marker in the prose". Verify: a
      language with both `doc_line` and `doc_is_structural` is refused, or routed
      on the right property.
