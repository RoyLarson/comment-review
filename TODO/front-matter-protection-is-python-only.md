# mark_matter cannot fire outside Python, so a licence header is editable work

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

mark_matter cannot fire outside Python, so a licence header is editable work.

## Tasks

- [ ] MEASURED: `lic.c` and `lic.rs` census with `annotations=[]` and `f0
      kind=dark-matter`; an identical `lic.py` gets `annotations=['matter']`. The
      `doc` lookup in `mark_matter` requires `declares == 0`, never true at the
      lexical tier.
- [ ] !! SO THE `query` GUARD NEVER FIRES. `verdicts.py`'s rule 'ANY EDIT PROPOSED
      ON FRONT MATTER BECOMES A query' keys on `series_of(held) == FRONT`, so a
      `correct` on licence text in C, Rust, Java, JS or Go is admitted as ordinary
      work. Roy's reason for that guard was that the cost is asymmetric and sits
      OUTSIDE this system -- a licence is a legal instrument.
