# Nine findings in the record, verdict and desk system, from review round 4

```
Status:   open
Progress: 1 of 9 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (/code-review high round 4, 2026-08-22 -- the findings OUTSIDE the
          seven reader modules, filed rather than fixed because this system is due an
          independent review session and the reader modules shift under it)
RE-VERIFIED: 2026-08-23 — 2026-08-23. Task 6 is FIXED and ticked: record.py:1074 now
             guards with isinstance(report.get("pages"), list) and returns "not a seeded
             report" instead of dying with AttributeError. ! TWO RE-CONFIRMED BY RUNNING
             THEM, not by reading: task 7 still raises -- record_problems({"verdict":
             ["patch"]}, None) gives TypeError: unhashable type: list, because the
             membership test is asked of unvalidated JSON; and task 1 still contradicts
             itself -- the patch row payload generates "A patch needs no source"
             verbatim into the shipped brief while owes_sources stays True by default,
             so desk.py fatally refuses every compliant patch. The shipped instruction
             and the shipped gate still disagree. Tasks 2, 3, 4, 5, 8 and 9 were not re-
             run.
```

## Objective

Nine findings in the record, verdict and desk system, from review round 4.

## Tasks

- [ ] record.py -- the `patch` row's payload says a patch needs no source and that
      sentence is generated VERBATIM into the shipped reviewer-brief, but
      `owes_sources` stays True (only `clean` clears it), so desk.py fatally
      refuses every `patch` a compliant reviewer files. The shipped instruction
      and the shipped gate contradict each other.
- [ ] verdicts.py -- `published` is built from `vocabulary.Reviewer`, which also
      holds `compact` and `review`, so a file named review.json passes the
      UNKNOWN-reviewer check. A run where module-context never ran certifies
      `Every finding is admissible` at exit 0 and never names the absence.
- [ ] census.py + verdicts.py -- zero path arguments emit `[]` at exit 0, and the
      join's emptiness guard is satisfied by an empty list, so it certifies `0
      findings over 0 prose paragraphs` as COMPLETE. Reachable whenever stage 1's
      merge-base diff yields no paths -- the exact complete-because-nothing-was-
      incomplete failure that guard exists to stop, one step out.
- [ ] desk.py -- a blank line inside the SOURCE window collapses to an empty
      string and emits two spaces where the needle has one, so any honest verbatim
      quote SPANNING a blank line is fatally refused. `_resolve_lines` invites
      function-sized ranges, where blank lines are guaranteed.
- [ ] desk.py -- any at-sign in a `move`'s `to:` is treated as an address claim,
      but the address pattern matches only a series letter and digits, so both a
      prose destination naming a decorated accessor and a real front-matter
      address are rejected as `not an address`.
- [x] record.py -- `report.get('pages')` has no type guard, so passing a census
      where a report is expected dies with AttributeError instead of the shape
      diagnostic held.py documents guarding for.
- [ ] record.py -- `verdict not in VERDICTS` is asked of unvalidated JSON, so a
      verdict written as a LIST raises TypeError and takes the pre-flight down.
- [ ] run_context.py -- the success message names three machine-checked sections
      and subtracts three, but FOUR are checked; the lookup census is omitted from
      what the message claims to have verified.
- [ ] compositor.draft writes `set_page(page)` with no losslessness check. ! The
      obvious fix does NOT work and the reason matters: `lossless()` rebuilds the
      page FROM DISK, so it cannot be asked of a drafted page -- the whole point
      of a draft is that lines changed. The guard that would work is an identity
      check on the page BEFORE any verdict is applied, so a later difference is
      attributable to the edit rather than to the model.
