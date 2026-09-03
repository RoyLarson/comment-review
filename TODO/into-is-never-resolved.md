# The draft guard trusts an into it never resolves

```
Status:   open
Progress: 2 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (the narrow guard fix on the write-chain branch, 2026-08-25 --
          reported by the implementer, deliberately not fixed)
```

## Objective

The draft guard trusts an into it never resolves.

## Tasks

- [x] T1 | FINISHED -- proof_setter.run resolves into at :157, compares via undraftable at :167 | db7ae40 | Resolve
      into once, where run receives it, and compare against the resolved value
- [x] T2 | FINISHED -- test_a_RELATIVE_into_does_not_refuse_every_page pins it | db7ae40 | A
      test with a relative into. Verify: it fails against the current code
- [ ] T3 | Ask whether any other flow trusts an unresolved directory the same
      way
