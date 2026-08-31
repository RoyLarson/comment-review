# The draft guard trusts an into it never resolves

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (the narrow guard fix on the write-chain branch, 2026-08-25 --
          reported by the implementer, deliberately not fixed)
```

## Objective

The draft guard trusts an into it never resolves.

## Tasks

- [ ] T1 | Resolve into once, where run receives it, and compare against the
      resolved value
- [ ] T2 | A test with a relative into. Verify: it fails against the current
      code
- [ ] T3 | Ask whether any other flow trusts an unresolved directory the same
      way
