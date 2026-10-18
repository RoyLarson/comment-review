# Use accepted Python reader vocabulary

```
Status:   closed
Progress: 1 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-12 (implementation)
```

## Objective

Use accepted Python reader vocabulary.

## Tasks

- [x] T1 | Vocabulary gate reports zero retired uses after scoped renames | 5564f046 | Replace
      retired Python reader terms
        > 2026-10-12 Check: scripts/check_vocabulary.py exits zero.
        > 2026-10-12 Reason: definition.py:99, scanner.py:162, structure.py:101 fail.
