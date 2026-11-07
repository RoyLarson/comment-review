# Read Python documentation after a UTF-8 BOM

```
Status:   closed
Progress: 1 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-13 (implementation)
```

## Objective

Read Python documentation after a UTF-8 BOM.

## Tasks

- [x] T1 | BOM docs and cookies retain exact bytes; page checks reviewed | fcd2f0f8 | Recognize
      a leading BOM before Python documentation
        > 2026-10-13 Location: reading/python/scanner.py:167 treats BOM as a name.
        > 2026-10-13 Check: BOM module docs and cookies read with exact byte roundtrip.
