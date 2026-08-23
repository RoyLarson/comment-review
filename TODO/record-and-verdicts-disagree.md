# record.py and verdicts.py disagree about what a valid record is, in four places

```
Status:   deferred
Progress: 0 of 8 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (/code-review high round 3, 2026-08-22, and Roy: the record/verdict
          pieces have got a lot of work to do and need an independent review work
          session)
```

## Objective

record.py and verdicts.py disagree about what a valid record is, in four places.

## Tasks

- [ ] DEFERRED TO ITS OWN SESSION, and this file exists so the findings survive
      the wait. Roy, 2026-08-22: *particularly the record/verdict pieces ... needs
      an independent review work session*. ! It also waits on front-half-
      undetermined, which is where what a RECORD IS gets settled
- [ ] !! ALL FOUR ARE ONE CLASS: record.py --check REFUSES a record that
      verdicts.py ADMITS. Two gates over one file, disagreeing about whether it is
      valid -- and the admitting one is the gate that certifies a review
- [ ] verdicts.py:559 with held.py:172 -- load_report filters sources to DICTS, so
      a bare-string source vanishes before source_problem ever runs. record.py
      --check exits 1; verdicts.py exits 0 saying *Every finding is admissible*. !
      The bare-string form is the RETIRED text-record spelling, which is to say
      the likely mistake
- [ ] verdicts.py:626 with desk.py:711 -- nothing requires claim.shape, so
      declares_scope falls back to a SUBSTRING TEST on the claim text. A query
      whose prose merely contains *outside my role* is reclassified as a boundary
      report and disappears from stage 5
- [ ] record.py:552 -- _answered uses str(...).strip() where every sibling uses
      filled(), so a JSON null renders as the TRUTHY string None and satisfies the
      check on a required payload half. ! record.py already documents fixing this
      exact defect once: *str() here rendered None as the word None and handed it
      downstream as the sentence being ruled on*
- [ ] desk.py:169 -- the present-and-empty test covers markers but NOT the extras,
      so the two tools disagree again. That is the failure class filled() was
      written to end
- [ ] held.py:118 -- *pages not in report* checks the KEY, not the type. A dict or
      a string under pages yields findings=0 AND malformed=[], so verdicts.py
      blames the reviewer for a coverage gap the FILE caused -- the exact
      consequence the docstring at :112 claims to prevent
- [ ] verdicts.py:563 -- address_problem is INERT. _report continues when
      entry_for returns None, so want == f.address by construction and both
      branches are unreachable. By the rule in docs/gates.md -- could it fail --
      no
