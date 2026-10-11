# Define language registry contracts

```
Status:   open
Progress: 1 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-11 (Approved lexical-reader design and P4 decomposition)
```

## Objective

Define language registry contracts.

## Tasks

- [~] T1 | Load strict independent TOML language definitions; verify explicit
      fields, useful errors and no rule inheritance
        > 2026-10-11 Roy approved independent rules; no implementation choice is pending
- [ ] T2 | Select readers through one registry; verify unique routes, actual
      coverage and excluded file categories
- [x] T3 | Language module describes current configuration responsibilities; scoped review passes | f0fbb346 | Describe
      installed language configuration accurately; verify the module docstring
      agrees with its imports and responsibilities
        > 2026-10-11 Review: reading/language.py:1 retains obsolete leaf-module claims
