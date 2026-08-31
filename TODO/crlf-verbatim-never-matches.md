# A multi-line verbatim from a CRLF file can never match

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, from the blind rewrite. MEASURED: `'# one\r\n# two' in
          '# one\n# two'` is False, on the platform CLAUDE.md names as primary)
```

## Objective

A multi-line verbatim from a CRLF file can never match.

## Tasks

- [ ] T1 | Reproduce it as a failing test over a real CRLF file. Verify: a
      two-line `verbatim` taken verbatim from that file is reported as not
      found, and the test fails against today's code.
- [ ] T2 | Decide which side normalises -- the window, the `verbatim`, or both
      at the boundary. Verify: whichever is chosen, a single-line `verbatim`
      still matches and the choice is stated where `_lines` says it preserves
      the endings.
- [ ] T3 | Check the same rejoin elsewhere. Verify: no other comparison in
      `src/` splits on real line endings and rejoins with one spelling.
