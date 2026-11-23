# Determine where the flow helpers belong

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-23 (decision-log #384)
```

## Objective

About ten `flows/` modules decide no order -- `source`, `proof_io`,
`reading_context`, `read_diagnostics`, `referrers`, `human` among them. They
hold a read, a write or a rule a stage uses, and they sit in `flows` because
`flows` is the one area that may import `machine` (`docs/conventions.md`, *Areas
are isolated*). `flows/__init__.py` says a flow decides order, not behaviour.

Determine where each of these helpers belongs: whether an existing package fits
it better, or whether a new package is needed. Nothing moves until that is
settled (decision-log #384).

## Tasks

- [ ] T1 | Determine which existing package fits each flow helper
- [ ] T2 | Determine whether the helpers no package fits need a new package
