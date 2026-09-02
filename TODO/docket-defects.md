# Six defects in docket.py, and one discards an approved page at exit 0

```
Status:   open
Progress: 0 of 8 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, a code review of `docket/docket.py` run end to end
          through a temp repo -- eight tasks, and no TODO on the board is a home for
          that module)
Pending:  2026-08-30 — the `Schedule.role` delete (task 7) is SUPERSEDED IN PART if
          `docket-role-is-per-page-not-per-alteration.md` task 2 lands first: that task
          gives the field a reader. Reword task 7 to track the remainder rather than
          ticking it.
```

## Objective

Eight tasks over six defects in `docket/docket.py`, found on 2026-08-30 by running the
write chain end to end through a temp repo -- `page_of`, `docket.read` and
`proof_setter.run`.

!! **ONE OF THEM REACHES A USER'S FILE.** A docket carrying schedules for `pkg/a.py`
and `./pkg/a.py` produces ZERO refusals: `read` answers `''` for both,
`flows/proof_setter.py:361` resolves both to one draft file, one page's approved text
is discarded, `commands/proof.py:143` prints `2 page(s) drafted for review` and the
process returns 0. `pkg\a.py`, `PKG/A.py` and `pkg/../pkg/a.py` are accepted too. That
is verbatim the failure the guard's own comment at `docket.py:134-145` claims to
prevent, and the same outcome `proof_setter.py:354-360` records as MEASURED and FIXED
on 2026-08-25 for basename flattening. `revise.pull`'s address-set assertion cannot
see it -- a lost alteration moves no addresses.

!! **THESE LAND TOGETHER, WHICH IS WHAT EARNS THE FILE.** The normalisation cannot
close that finding alone: the test guarding it today, `tests/test_docket.py:130`
(`test_TWO_SCHEDULES_FOR_ONE_PAGE_are_refused`), feeds two BYTE-IDENTICAL paths -- the
one case the guard already handles -- so it CANNOT FAIL on the shape the guard is
written against, and a normalisation landed without the test rewrite is a fix nothing
can hold. `docs/gates.md` states the rule: the question is not whether the check
passes but whether it could fail. The sort-order defect is reachable through `read`
only until the normalisation lands, so the two are ordered by the same mechanism, and
the `Schedule.role` delete is the field the null-role defect poisons.

## The rest of what was measured

- `desk.collator.docket_from` writes `"sha": ""` for a flattened path that resolves
  against nothing (`collator.py:993-995` documents doing so), and ONE such page makes
  the WHOLE docket unreadable at `docket.py:146-147`, discarding every other page's
  approved alterations and naming the sha when the cause is the path. Latent today
  because nothing in `src/` calls `docket_from`; it goes live when
  [containers-and-verification](containers-and-verification-are-unwired.md) lands, and
  the fix may belong in `desk/collator.py`
- a hand-built docket whose two schedules share `path` and `sha` raises a bare
  `TypeError: '<' not supported between instances of 'dict' and 'dict'` from
  `NamedTuple` default ordering reaching the `alterations` field -- where every other
  bad input in that flow produces a `Refusal`
- `grep -rn "schedule\.role\|s\.role" src/comment_review/ tests/` is empty: no
  `Schedule` reader exists in `proof_setter.py`, `commands/proof.py`,
  `tests/test_docket.py` or `tests/test_proof_setter.py`
- `pull._set_by` does not exist -- `module _set_by: True`, `pull._set_by: False` --
  and the dotted form is in the two docstrings a reader of the write boundary reads
  first
- `read` accepts `/etc/passwd`, `../outside.py` and `C:/Windows/x.py` on purpose,
  while `Schedule.path`'s docstring calls itself the one field a containment guard has
  to rule on; the single guard is `machine.repo.can_escape` at
  `flows/proof_setter.py:184`

! **TWO OBSERVATIONS WERE CHECKED AND CARRY NO TASK.** Unknown keys are ignored at
both levels -- `{"extra": 1}` and a page-level `"junk"` both read without complaint --
which is not a defect while `role` is the only optional field. And the empty-docket
refusal at `docket.py:111-114` holds by CALLER DISCIPLINE: `read` returns `({}, why)`
and `schedules_of({})` returns `[]` without complaint, so the property depends on
every caller checking `why`. `commands/proof.py:104-107` does, and it is the only
caller.

## Tasks

- [ ] T1 | Implement path normalisation before the `seen` membership test at
      `docket.py:134-145`, or refuse outright any path not already in normal
      form. Verify: a docket carrying schedules for `pkg/a.py` and `./pkg/a.py`
      is refused by name; today `read` answers `''` for both,
      `flows/proof_setter.py:361` resolves both to one draft file, and one
      page's approved text is discarded at exit 0 while `commands/proof.py:143`
      prints `2 page(s) drafted for review` and returns 0. `pkg\a.py`,
      `PKG/A.py` and `pkg/../pkg/a.py` are accepted too.
- [ ] T2 | Implement a "this target was already drafted this run" refusal in
      `flows/proof_setter._one`. Verify: two schedules resolving to one `target`
      refuse by name rather than the second draft -- built from the ORIGINAL
      file, not from the first draft -- overwriting the first's approved text;
      the test goes red today.
- [ ] T3 | Update `tests/test_docket.py:130`
      (`test_TWO_SCHEDULES_FOR_ONE_PAGE_are_refused`) so it exercises the shape
      the guard is written against. Verify: the case feeds two DIFFERENT
      spellings of one path and fails against `docket.py:134-145` as it reads
      today; the byte-identical pair it feeds now is the one case the guard
      already handles.
- [ ] T4 | Implement a refusal in `desk.collator.docket_from` at the point a
      flattened path fails to resolve, naming the address it could not place.
      Verify: no docket is written carrying `"sha": ""` from `collator.py:1019`;
      today one unresolvable page makes the WHOLE docket unreadable at
      `docket.py:146-147` -- `({}, 'pkg/a.py: every page needs the sha it was
      read at')` -- discarding every other page's approved alterations, and
      naming the sha when the cause is a path that resolved against nothing.
- [ ] T5 | Update the two citations of `flows.revise.pull._set_by` at
      `docket.py:64-65` and `:92-93`. Verify: `grep -rn "pull\._set_by"
      src/comment_review/` is empty and the sentences name
      `flows.revise._set_by` (`revise.py:242`), the way `flows/revise.py:55-58`
      already spells the relationship.
- [ ] T6 | Update both `Schedule` sort sites to `sorted(schedules, key=lambda s:
      s.path)`. Verify: `flows/proof_setter.py:211` and `commands/proof.py:140`
      sort by path, and a hand-built docket whose two schedules share `path` and
      `sha` no longer raises `TypeError: '<' not supported between instances of
      'dict' and 'dict'` from the `alterations` field.
- [ ] T7 | Delete `Schedule.role` at `docket.py:100` and its justification at
      `:91-94`. Verify: `grep -rn "schedule\.role\\|s\.role" src/comment_review/
      tests/` was already empty before the delete -- no `Schedule` reader exists
      in `proof_setter.py`, `commands/proof.py`, `tests/test_docket.py` or
      `tests/test_proof_setter.py` -- the suite is green after, and
      `schedules_of` no longer runs `str(page.get("role", ""))` at
      `docket.py:203` on every unwind.
- [ ] T8 | Update `Schedule.path`'s docstring at `docket.py:84-86`, which calls
      it "the one field a containment guard has to rule on" while no guard in
      this file rules on it. Verify: the sentence points at
      `machine.repo.can_escape` as the single guard site
      (`flows/proof_setter.py:184`), and states that `docket.read` accepts
      `/etc/passwd`, `../outside.py` and `C:/Windows/x.py` on purpose.
