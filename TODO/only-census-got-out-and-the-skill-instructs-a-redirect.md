# Only `census.py` got `--out`, and `SKILL.md` instructs the redirect it forbids

```
Status:   open
Progress: 3 of 5 tasks done
Owner:    agents
Raised:   2026-08-17 (the 0.2.0 builder run, at the collator: "verdicts.py has no --out
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
Landed:   2026-08-24 — T1, T2 and T4. `run_context.py` and `referrers.py` each take
          `--out`, copied from `census.py:276` onto a new `_report` seam; `verdicts.py`
          writes the file AND prints, so a captured join is not a silent one, and its
          help now says that instead of census's exclusive wording. ! FOUND DOING IT:
          `run_context.py`'s OWN usage line, at the top of the module, wrote the
          redirect too -- a fifth site the table below never named, and the one a
          reader of that script would copy. REMAINS: T3 is `SKILL.md` (`agents`), T5
          is the grep test -- `systems`, not `testing`, per `decision-log.md Process: #5`:
          a gate over a shipped file is a system gating test.
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
| `verdicts.py` | the collator; the evidence layout keeps `join-1...`/`join-2...` | **yes** -- verdicts.py:293 |
| `run_context.py --template` | the packet -- required, and `--check`ed | **yes**, 2026-08-24 -- and SKILL.md:617 still writes the redirect |
| `referrers.py` | the `REFERENCE ONLY` candidates | **yes**, 2026-08-24 |

! `vocabulary.py` is pasted into a prompt rather than saved, so it is outside this.

!! **THE FLAG IS COPIED FROM `census.py:276` EXACTLY** -- same flag name, same help, same
behaviour -- so there is one thing to remember rather than three.

!! **SUPERSEDED IN PART.** `verdicts.py` was the third script named in the original box and
gained the flag at `verdicts.py:293`; the remainder is `run_context.py` and `referrers.py`.

!! **NOT WHILE A RUN IS IN FLIGHT.** Two runs were mid-join when this was raised, and one of them
was being diagnosed for a refusal -- editing the script under a diagnosis makes the measurement
worthless.

! **`verdicts.py --out` as it landed was EXCLUSIVE**, because the help was copied: it read
*"write the report to PATH, not stdout"*. The collator is read by a human at the terminal as often as
it is captured, and `census.py --out` is silent by comparison because nobody reads a census by
eye.

!! **SO THE COPY RULE ABOVE HAS ONE DELIBERATE EXCEPTION, LANDED 2026-08-24.** T4 made
`verdicts.py --out` write the file **and** print, and its help now reads *"write the report to
PATH, and print it too"*. ! **The three that stay exclusive are the three nobody reads by eye**
-- a census, a packet and a candidate list are inputs to a later stage. The collator is the one
stage whose output a person acts on, and a gate that goes silent when its output is captured
makes *saw nothing* and *found nothing* the same event there.

! **The missing test is a grep.** This defect is a doc and a script disagreeing, which is the
class this repo already tests for elsewhere, and it would have caught this the day it shipped.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- Add `--out` to `run_context.py`, copied
      from `census.py:276`. Verify: `run_context.py --template --out F` leaves
      the packet in `F`.
- [x] T2 | FINISHED | unknown | T2 -- Add `--out` to `referrers.py`, copied from
      `census.py:276`. Verify: it appears in the argparse, and the `REFERENCE
      ONLY` candidates land in the named file.
- [ ] T3 | T3 -- Fix `SKILL.md:617` to use the flag once it exists. Verify: no
      `python <skill>/scripts/...` line in `SKILL.md` carries a `>`.
- [x] T4 | FINISHED | unknown | T4 -- Keep `verdicts.py` writing its report to
      stdout AS WELL AS `--out`. Verify: with `--out` given, the file is written
      and stdout is non-empty.
- [ ] T5 | T5 -- Test that no `python <skill>/scripts/...` line in `SKILL.md`
      carries a `>`. Verify: it fails on `SKILL.md:617` today and passes after
      T3.
