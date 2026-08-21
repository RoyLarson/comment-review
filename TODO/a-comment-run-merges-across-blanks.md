# A licence header and a doc comment become one paragraph with one address

```
Status:   open
Progress: 0 of 3 tasks done
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
