# Read Python documentation after a UTF-8 BOM

```
Status:   open
Progress: 0 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-13 (implementation)
```

## Objective

Read Python documentation after a UTF-8 BOM.

## Tasks

- [ ] T1 | Recognize a leading BOM before Python documentation
        > 2026-10-13 Location: reading/python/scanner.py:167 treats BOM as a name.
        > 2026-10-13 Check: BOM module docs and cookies read with exact byte roundtrip.
