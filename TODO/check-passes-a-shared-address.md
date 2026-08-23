# addresser --check prints SHARED and exits 0

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

addresser --check prints SHARED and exits 0.

## Tasks

- [ ] `_check` returns `1 if missing else 0` -- it gates only UNADDRESSED
      paragraphs. MEASURED: on the file in `two-paragraphs-one-address` it prints
      `SHARED lic.c@b0 <- 1-3 comment | 4-4 docstring` and exits 0.
- [ ] ! ITS ADVICE NAMES A DELETED FIELD. The message says to 'cite the census
      index alongside the address', and `record.slot` carries no index -- it was
      replaced by `place` on this branch.
- [ ] ! `record.entry_for` says '`--check` is what reports it', which is true only
      for a human reading stdout.
