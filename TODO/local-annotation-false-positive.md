# check_shipped_syntax reads a local variable annotation as a forward reference

```
Status:   open
Progress: 0 of 1 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-09-01 (found landing P51, when the gate refused a file that imports clean
          on 3.11)
```

## Objective

check_shipped_syntax reads a local variable annotation as a forward reference.

## Tasks

- [ ] T1 | Update the checker so a LOCAL variable annotation is not read as a
      forward reference
        > 2026-09-01 MEASURED 2026-09-01: it refused desk/containers.py over
        > 2026-09-01 refused: list[Refused] = [] inside a function body. PEP 526 does
        > 2026-09-01 not evaluate a local annotation, and the module imports clean on
        > 2026-09-01 3.11. Worked around by reordering the class above its reader.
