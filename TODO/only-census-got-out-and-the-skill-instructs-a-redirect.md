# Only `census.py` got `--out`, and `SKILL.md` instructs the redirect it forbids

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    agents
Raised:   2026-08-17 (the 0.2.0 builder run, at the join: "verdicts.py has no --out
          (the census scripts do) -- and this session refuses shell redirects")
TRIAGED:  2026-08-23 -- RE-MEASURED, and one row of the table below turned over.
          `verdicts.py` NOW HAS `--out` (verdicts.py:293, help string byte-identical to
          census.py:276), so T1 is SUPERSEDED IN PART and tracks the two scripts that
          still lack it. STILL LIVE: `run_context.py` and `referrers.py` declare no
          `--out` (their whole argparse is run_context.py:303-304 and
          referrers.py:99-100), and the redirect is still in the skill --
          SKILL.md:617 reads `run_context.py --template > <run-dir>/context.md`. ! The
          line number moved from 510; the line did not. And no test forbids a `>` on a
          script line: `grep -rn redirect tests/` returns three hits, all unrelated.
```

## Objective

**`SKILL.md` contradicts itself 300 lines apart.**

- `SKILL.md:310` -- *"!! `--out`, never a shell redirect. A worktree-isolated session REFUSES a
  command carrying one -- 'too complex to verify that it stays inside the worktree' -- and the
  JSON census is what stage 5 parses, so a redirect makes the run impossible there rather than
  merely awkward."*
- `SKILL.md:617` -- `python <skill>/scripts/run_context.py --template > <run-dir>/context.md`

! **The reasoning at 310 applies to every script whose output the run must keep**, and it has
been acted on for two of the four. MEASURED 2026-08-23:

| script | output the run needs on disk | has `--out`? |
| --- | --- | --- |
| `census.py` | the two censuses | **yes** -- census.py:276 |
| `verdicts.py` | the join; the evidence layout keeps `join-1...`/`join-2...` | **yes** -- verdicts.py:293 |
| `run_context.py --template` | the packet -- required, and `--check`ed | no, and SKILL.md:617 writes a redirect |
| `referrers.py` | the `REFERENCE ONLY` candidates | no |

! `vocabulary.py` is pasted into a prompt rather than saved, so it is outside this.

## Tasks

- [ ] T1 -- Add `--out` to `run_context.py` and `referrers.py`, matching `census.py:276`
      exactly: same flag name, same help, same behaviour, so there is one thing to remember.
      Verify: `--out` appears in each script's argparse, and `run_context.py --template --out
      F` leaves the packet in `F`.
      ! **SUPERSEDED IN PART.** `verdicts.py` was the third script named here and gained the
      flag at verdicts.py:293; the remainder is the two above.
      !! **Not while a run is in flight.** Two runs were mid-join when this was raised, and one
      of them was being diagnosed for a refusal -- editing the script under a diagnosis makes the
      measurement worthless.

- [ ] T2 -- Fix `SKILL.md:617` to use the flag once it exists. Verify: no `python
      <skill>/scripts/...` line in `SKILL.md` carries a `>`.

- [ ] T3 -- Keep `verdicts.py` writing its report to **stdout as well as** `--out`. MEASURED
      2026-08-23: the flag as it landed reads *"write the report to PATH, not stdout"*
      (verdicts.py:293), copied from `census.py`, so it is EXCLUSIVE. The join is read by a
      human at the terminal as often as it is captured, and `census.py --out` is silent by
      comparison because nobody reads a census by eye. Verify: with `--out` given, the file is
      written and stdout is non-empty.

- [ ] T4 -- Add a test that no `python <skill>/scripts/...` line in `SKILL.md` carries a `>`.
      ! This defect is a doc and a script disagreeing, which is the class this repo already
      tests for elsewhere -- the check is a grep, and it would have caught it the day it
      shipped. Verify: the test fails against SKILL.md:617 as it reads today, then passes
      after T2.
