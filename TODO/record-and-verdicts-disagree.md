# record.py and verdicts.py disagree about what a valid record is, in four places

```
Status:   deferred
Progress: 2 of 8 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-22 (/code-review high round 3, 2026-08-22, and Roy: the record/verdict
          pieces have got a lot of work to do and need an independent review work
          session)
TRIAGED:  2026-08-23 -- 2026-08-23. Tasks 1 and 2 are records -- the deferral to its own
          session, and the framing that all of these are ONE class: record.py --check
          refuses what verdicts.py admits, and the admitting one is the gate that
          certifies a review. Tasks 3 to 8 are six specific findings and each is work. !
          Left deferred as filed: it waits on front-half-undetermined, where what a
          RECORD IS gets settled.
RE-VERIFIED: 2026-08-23 -- ALL SIX FINDINGS RE-READ IN THE SHIPPED TREE AND ALL SIX ARE
             STILL LIVE. Two line numbers drifted and are corrected in the tasks: the
             source filter is `held.py:172-175` reached from `verdicts.py:557`, not :559;
             `_answered` is `record.py:556`, not :552; the present-and-empty test is
             `desk.py:170-172`, not :169; `address_problem` is called at
             `verdicts.py:561`. ! T8 was re-checked against the CODE rather than the
             claim: `_report` `continue`s when `entry_for` returns None
             (verdicts.py:542-549), and the only surviving branch of `address_problem` is
             that same `entry is None` test (desk.py:614-616) -- so the check cannot
             fire, and desk.py:617-621 says so in its own comment.
Updated:  2026-08-28 — T4 was ticked at fcba2a6 and is UNTICKED again: only its gate
          half landed. `desk/mark.py` now requires `claim.shape` as a key and refuses a
          shape outside the three, so the substring fallback is gone from the live code.
          Its VERIFY sentence -- "a query with no shape and *outside my role* in its
          prose reaches stage 5" -- names routing that lives in the collator, which is
          not built; the substring test it describes survives only in
          `prototype/original/record.py`, which does not run. Found by the Task 1 task
          reviewer. The remainder is worked by `docs/plans/0.2.4-the-mark-and-the-
          collator.md` P4.3. The sentence is not being reworded to match what was done:
          an unchecked box says work remains, and it does.
```

## Objective

**record.py and verdicts.py disagree about what a valid record is, in six places, and the
disagreement always resolves the same way: `record.py --check` REFUSES a record that
`verdicts.py` ADMITS.** Two gates over one file, and the admitting one is the gate that certifies
a review.

! **Kept as a record, not as work:** this file exists so the findings survive the wait. Roy,
2026-08-22: *particularly the record/verdict pieces ... needs an independent review work
session*. It also waits on [`front-half-undetermined`](front-half-undetermined.md), which is
where what a RECORD IS gets settled -- which is why the Status is `deferred` and not `open`.

## The six findings, in full

**T3, the source filter.** `verdicts.py:557` with `held.py:172-175` -- `load_report` filters
`sources` to DICTS, so a bare-string source vanishes before `source_problem` ever runs.
`record.py --check` exits 1; `verdicts.py` exits 0 saying *Every finding is admissible*. ! The
bare-string form is the RETIRED text-record spelling, which is to say the likely mistake.

**T4, the substring fallback.** `verdicts.py:622-623` with `desk.py:718` -- nothing requires
`claim.shape`, so `declares_scope` falls back to `OUT_OF_ROLE in f.claim.lower()`, a SUBSTRING
TEST on the claim text. A `query` whose prose merely contains *outside my role* is reclassified as
a boundary report and disappears from stage 5.

**T5, `str()` where every sibling uses `filled()`.** `record.py:556` -- `_answered` uses
`str(...).strip()` where every sibling uses `filled()` (record.py:453), so a JSON null renders as
the TRUTHY string `None` and satisfies the check on a required payload half. ! `record.py` already
documents fixing this exact defect once: *str() here rendered None as the word None and handed it
downstream as the sentence being ruled on*.

**T6, present-and-empty.** `desk.py:170-172` -- the present-and-empty test covers `markers` but
NOT `_extras`, so the two tools disagree again. That is the failure class `filled()` was written
to end.

**T7, the key rather than the type.** `held.py:118` -- *pages not in report* checks the KEY, not
the type. A dict or a string under `pages` yields `findings=0` AND `malformed=[]`, so
`verdicts.py` blames the reviewer for a coverage gap the FILE caused -- the exact consequence the
docstring at held.py:112-117 claims to prevent.

**T8, a check that cannot fire.** `verdicts.py:561` -- `address_problem` is INERT. `_report`
`continue`s when `entry_for` returns None (verdicts.py:542-549), and `address_problem`'s only
surviving branch is that same `entry is None` test (desk.py:614-616), so by construction it can
never report. By the rule in `docs/gates.md` -- could it fail -- no.

## Tasks

- [x] T1 -- NOT A TASK. RECORD of the deferral, restated in the Objective, kept so the
      findings survive the wait for an independent review session.
- [x] T2 -- NOT A TASK. The FRAMING, restated in the Objective: all six are one class, and
      the admitting gate is the one that certifies a review.
- [ ] T3 -- Stop `load_report` dropping a bare-string source before `source_problem` runs.
      Verify: one report carrying a bare-string source, and both tools agreeing on it.
- [ ] T4 -- Require `claim.shape` instead of a substring test on the claim text. Verify: a
      `query` with no `shape` and *outside my role* in its prose reaches stage 5.
- [ ] T5 -- Make `_answered` use `filled()` like every sibling at `record.py:453`. Verify:
      a record with a JSON null in that slot is refused.
- [ ] T6 -- Extend the present-and-empty test at `desk.py:170-172` to `_extras`. Verify: a
      record with a present-and-empty EXTRA is refused by both tools.
- [ ] T7 -- Make `held.py:118` check the TYPE of `pages`, not just the key. Verify: a
      report whose `pages` is a dict is refused with the shape diagnostic.
- [ ] T8 -- Replace `address_problem` with a check that can fire. Verify: whatever
      replaces it can be made to fail on a crafted record.
