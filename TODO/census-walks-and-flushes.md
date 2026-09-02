# census.py walks the whole repo, runs git twice, and its run-flush never fires

```
Status:   open
Progress: 3 of 7 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (/simplify rounds 1 and 2 and /code-review high round 3,
          2026-08-22; round 2 measured the walk at 53% of a run)
RE-VERIFIED: 2026-08-23 — 2026-08-23, verified in place. THREE FIXED and ticked: task 1,
             `code_names` no longer walks the tree -- it takes `tracked` and
             census.py:323 passes `tracked_paths(repo)`, with the walk surviving only as
             the git-cannot-answer fallback; task 2, `git ls-files` is ONE site now at
             repo.py:117, not two in census.py; task 3, `flush_run` fires -- the path
             check runs BEFORE both continues, and the comment above it records the old
             defect and the constants.py row that measured it.
RE-CHECKED: 2026-08-23 — 2026-08-23, re-read against the tree rather than trusted.
            T1-T3 confirmed fixed: census.py:125-127 is `code_names(roots, tracked=None)`
            and census.py:323 passes `tracked_paths(repo)`; `ls-files` appears once, at
            repo.py:117; `flush_run()` is called at census.py:567, :574, :579 and :592,
            so both continues reach it. ! FOUR STILL LIVE, with corrected citations:
            T4 (addresser.py:1137 unwraps the dict form, verdicts.py:332 does not),
            T5 (`_report` is census.py:296-649 = 354 lines, up from the 289 filed),
            T6 (referrers.py:53 -- and prove_unchanged.py:176 is a THIRD site), and
            T7 (referrers.py:126-127 loops `_grep` per token; `_grep` is at :71).
SPLIT:      2026-08-23 -- the boxes were cut to two lines each. The measurements they
            carried are in the Objective; the task count is unchanged at seven
```

## Objective

census.py walks the whole repo, runs git twice, and its run-flush never fires.

! **THE THREE DEFECTS THE TITLE NAMES ARE ALL FIXED** (T1, T2, T3, re-verified
2026-08-23). What remains under this file is the four neighbouring findings the same
rounds raised, and the title no longer describes them -- it is left as filed so the
record stays readable, and the remaining work is what the unticked boxes say.

### What the boxes carried -- the measurements, moved out of the tasks

! **T1.** MEASURED 2026-08-22: `code_names` walked and resolved the WHOLE tree to harvest
60 files -- 53% of a census run. 3,152 paths walked, 3,021 of them in `corpora/`, 66
tracked -- and `resolve()` ran BEFORE the tracked test.

! **T2.** `git ls-files` was spawned TWICE per run (census.py:301-302), two full index
dumps for one answer.

! **T3.** census.py:501 -- `flush_run()` never fired on a `b.path` change and BOTH
continues bypassed it. VERIFIED at the time: constants.py, 43 lines, carried a row reading
`15-72 @c2..b58 41-0` -- another file's intervals attributed to it, a NEGATIVE span, and
any `add` composed from that row cited an address that does not exist.

! **T4 -- CENSUS LOADING IS WRITTEN FOUR TIMES AND THE FOURTH DIVERGES.**
addresser.py:1137 unwraps the dict form
(`loaded.get("paragraphs", []) if isinstance(loaded, dict) else loaded`); verdicts.py:332
assigns `json.loads(census_text)` straight through and never unwraps it. galley.py and
record.py accept the dict form too. ! Round 2 checked and NOTHING in the tree or the tests
emits that dict form -- so three modules carry dead defensive code and the fourth is
inconsistent with them. `addresser` already owns `unaddressed()` and is the vacant home
for a `load_census`.

! **T5.** `_report` is census.py:296-649, 354 lines -- it was filed at 289 and has grown.
! SUPERSEDED IN PART: the *"--languages wrapped in redirect_stdout for no reason"* half is
wrong now. `redirect_stdout` wraps the whole of `_report` for `--out`
(census.py:289-292) and census.py:285-288 states the reason -- a shell redirect is refused
outright by a worktree-isolated harness. Only the size half remains.

! **T6.** referrers.py:53 re-spells the `(".py", ".pyi")` suffix tuple that language.py:99
already owns -- the same defect as `tier-dispatched-on-name`. ! WORSE THAN FILED:
prove_unchanged.py:176 spells it a THIRD time, so there are two re-spellings against one
owner.

! **T7.** referrers.py:126-127 SPAWNS ONE `git grep` PER TOKEN -- the loop at :126 calls
`_grep` (defined at :71, running `git grep -l -F` at :85) once per token, about 200
subprocesses for a 17-file review, each one a full tree scan. MEASURED 2026-08-22: 37
tokens took 2.288s one at a time against 0.074s batched, a 31x difference. `git grep`
takes repeated `-e`, and `-o` preserves the per-token attribution the report prints.
! Filed here on Roy ruling 2026-08-22 -- referrers supports the whole thing and is not
part of the front half that will shift.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- FINISHED. `code_names` no longer walks the
      tree: census.py:125-127 takes `tracked` and census.py:323 passes
      `tracked_paths(repo)`. The walk is a fallback.
- [x] T2 | FINISHED | unknown | T2 -- FINISHED. `git ls-files` was spawned twice
      per run; it is one site now, repo.py:117.
- [x] T3 | FINISHED | unknown | T3 -- FINISHED. `flush_run()` never fired on a
      `b.path` change; it is now called at census.py:567, :574, :579 and :592,
      so both continues reach it.
- [ ] T4 | T4 -- Give census loading ONE loader, in `addresser.py`. Verify: one
      loader, four callers, and a test that fails without it.
- [ ] T5 | T5 -- Split `_report` (census.py:296-649, 354 lines) so it only
      dispatches. Verify: `--languages`, `--json`, `--filtered` and the default
      listing are each a function.
- [ ] T6 | T6 -- Stop re-spelling the `(".py", ".pyi")` suffix tuple
      language.py:99 owns. Verify: `grep -n "\.pyi"` over the shipped scripts
      returns only language.py.
- [ ] T7 | T7 -- Batch referrers.py's git grep -- the loop at :126-127 calls
      `_grep` once per token. Verify: one `git grep` runs for the whole token
      set, with repeated `-e`.
