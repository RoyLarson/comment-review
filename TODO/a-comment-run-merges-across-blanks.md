# A licence header and a doc comment become one paragraph with one address

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

A licence header and a doc comment become one paragraph with one address.

## Tasks

- [ ] Only CODE ends a run; blank lines go to `pending`. MEASURED on a Rust file:
      the licence header, the `//!` crate doc and the `///` item doc census as ONE
      paragraph, lines 1-6, `kind=comment` -- because `flush()` decides `is_doc`
      from `raw[0]` alone.
- [ ] ! `compact.md` routes on KIND, so a crate doc is cut to the COMMENT cap.
- [ ] ! And ownership-context is handed a licence header plus a function's
      documentation as one indivisible paragraph at one address, which no verdict
      can act on correctly.
- [ ] !! IT MOVES A PARAGRAPH BOUNDARY, NOT JUST AN ANNOTATION, and that is the
      work. Today only CODE ends a run, so a Rust file opening `// Copyright` /
      `// MIT` / blank / `/// Returns the name.` censuses as ONE paragraph over
      lines 1-4. MEASURED 2026-08-21. Under the ruling it must split: `f0` = 1-2,
      and line 4 is the declaration's own documentation. `text` is the run with
      its comment markers stripped, so the split has to go through the lexer's own
      construction rather than re-deriving it.
- [ ] ! THE RULING CLOSES THIS AT THE TOP AND FOOT OF A FILE ONLY. A run merging
      across a blank in the MIDDLE is untouched by it -- `flush()` still decides
      `is_doc` from `raw[0]` alone, and two comment runs separated by a blank line
      between two functions are still one paragraph at one address.
