# machine/ reads git output and JSON without the guards its callers assume

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-22 (code review 2026-11-22, merged findings)
```

## Objective

`machine/` is the checkout's I/O. Three of its reads hand callers something
other than what was on disk or end in a traceback: machine/repo.py splits git
output on line breaks instead of NUL, and machine/json_object.py keeps the last
of two repeated keys and lets json.loads errors other than JSONDecodeError
escape.

Found by the code review of 2026-11-22 (M34, M37, M38).

## Tasks

- [ ] T1 | Split git ls-files output on NUL with -z at machine/repo.py:233, as
      git grep -l needs too
        > 2026-11-22 Check (M34): a name holding U+2028 comes back as one path
- [ ] T2 | Refuse a repeated JSON key at machine/json_object.py:54 object_of
        > 2026-11-22 Check (M37): a copy with 'marks' twice is refused by check
- [ ] T3 | Catch json.loads ValueError with RecursionError at
      machine/json_object.py:54 as a refusal
        > 2026-11-22 Check (M38): a 5000-digit int gives a named refusal, no traceback
- [ ] T4 | Add machine's own imports to tests/test_areas.py, admitting
      exceptions only
        > 2026-11-22 Check: a machine import of binder turns the gate red (#377)
