# A page entry that is not an object loses every record under it, silently

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

A page entry that is not an object loses every record under it, silently.

## Tasks

- [ ] `record.every_record` does `if not isinstance(page, dict): continue` -- no
      `malformed` entry, no `--check` line. `verdicts.py` then reports the whole
      page as that reviewer's coverage gap, which points the reader at the
      reviewer.
- [ ] ! `held.held_records` documents itself as NOT filtering, which is true at
      the record level and false at the page level it now depends on.
- [ ] ! A record under a page missing its `page` key is reported as 'a record with
      no place', because `address_for` returns '' when either half is empty. The
      message sends the fixer to the record's `place` field, which is fine.
