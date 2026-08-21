# Shipped prose still describes formats and flags this branch deleted

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

Shipped prose still describes formats and flags this branch deleted.

## Tasks

- [ ] `record.py` carries four comments asserting a second record format that no
      longer exists, one chopped mid-clause by the edit that removed it -- and
      `desk.py` a fifth. These are the obituary class block-context is chartered
      to catch, shipping inside the tool that catches it.
- [ ] `foliator.py`'s module usage line names `--repo`, which argparse rejects:
      `error: unrecognized arguments: --repo .`, exit 2. The same commit that
      fixed `main()`'s docstring left the usage line four lines above it.
- [ ] !! `docs/addressing.md` states 'Every ADDRESS is unique -- measured `a0 b1
      b2 b3 c1 c2`'. MEASURED: the example directly above it now yields `a0 b0 b1
      b2 c0 c1 f0`. Every folio but `a0` is wrong and `f0` is missing, in the file
      CLAUDE.md calls the crux.
- [ ] `reviewer-brief.md` shows the record shape WITHOUT its `pages` wrapper -- a
      bare `{page, records}` where `seed()` writes `{record_version, reviewer,
      allowed, pages, code_concerns}`. The brief is a reviewer's only spec for the
      shape this branch changed.
