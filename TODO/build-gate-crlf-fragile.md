# The build gate's raw byte compare is line-ending-fragile on Windows

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-08-28 (found by the Task 1 reviewer during fix round 1, 2026-08-28, and
          reproduced live in this same session: filecmp.cmp(..., shallow=False) in
          scripts/build_plugin.py is a raw byte compare; with core.autocrlf=true, any
          operation that rewrites a src/ file through git (a checkout, or a Python text-
          mode write on Windows) converts it to CRLF while the plugins/ copy keeps the
          LF build_plugin.py wrote, so tests/gates/test_build.py fails on a tree whose
          committed blobs are identical)
```

## Objective

The build gate's raw byte compare is line-ending-fragile on Windows.

## Tasks

- [ ] T1 | Fix the normalisation point: either compare src/ and plugins/ after
      normalising line endings (e.g. read both in universal-newlines text mode)
      instead of a raw byte compare, or make build_plugin.py's copy step force a
      specific line ending on both sides so a plain checkout can't diverge from
      what the build produced.
- [ ] T2 | Add a test: a src/ file written with CRLF and its built plugins/ copy
      written with LF, identical content otherwise, and confirm the fix's
      compare treats them as matching.
