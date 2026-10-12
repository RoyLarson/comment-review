# Define language registry contracts

```
Status:   closed
Progress: 4 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-11 (Approved lexical-reader design and P4 decomposition)
```

## Objective

Define language registry contracts.

## Tasks

- [x] T1 | Strict immutable TOML definitions and located acquisition pass integration gates | 8338dfa3 | Load
      strict independent TOML language definitions; verify explicit fields,
      useful errors and no rule inheritance
        > 2026-10-11 Roy approved independent rules; no implementation choice is pending
- [x] T2 | Validated registry selection and coverage pass focused tests and independent review | 8338dfa3 | Select
      readers through one registry; verify unique routes, actual coverage and
      excluded file categories
- [x] T3 | Language module describes current configuration responsibilities; scoped review passes | f0fbb346 | Describe
      installed language configuration accurately; verify the module docstring
      agrees with its imports and responsibilities
        > 2026-10-11 Review: reading/language.py:1 retains obsolete leaf-module claims
- [x] T4 | Page coverage prose states current behavior; scoped review passes | 1f3ab4ce | Describe
      page coverage in current terms; verify the edited docstring contains no
      dated deletion history
        > 2026-10-11 Review: binder/page.py:133 retains dated field-deletion history
