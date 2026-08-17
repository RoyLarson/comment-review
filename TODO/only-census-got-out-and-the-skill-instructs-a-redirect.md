# Only `census.py` got `--out`, and `SKILL.md` instructs the redirect it forbids

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Raised:   2026-08-17 (the 0.2.0 builder run, at the join: "verdicts.py has no --out
          (the census scripts do) — and this session refuses shell redirects")
```

## Objective

**`SKILL.md` contradicts itself 200 lines apart.**

- `SKILL.md:310` — *"⚠⚠ `--out`, never a shell redirect. A worktree-isolated session REFUSES a
  command carrying one — 'too complex to verify that it stays inside the worktree' — and the
  JSON census is what stage 5 parses, so a redirect makes the run impossible there rather than
  merely awkward."*
- `SKILL.md:510` — `python <skill>/scripts/run_context.py --template > <run-dir>/context.md`

⚠ **The reasoning at 310 applies to every script whose output the run must keep**, and it was
acted on for exactly one of them:

| script | output the run needs on disk | has `--out`? |
| --- | --- | --- |
| `census.py` | the two censuses | **yes** |
| `run_context.py --template` | the packet — required, and `--check`ed | no, and the skill writes a redirect |
| `verdicts.py` | the join; the evidence layout keeps `join-1…`/`join-2…` | no |
| `referrers.py` | the `REFERENCE ONLY` candidates | no |

⚠ `vocabulary.py` is pasted into a prompt rather than saved, so it is outside this.

## Tasks

- [ ] Add `--out` to `run_context.py`, `verdicts.py` and `referrers.py`, matching `census.py`'s
      flag exactly — same name, same behaviour, so there is one thing to remember.
      ⚠⚠ **Not while a run is in flight.** Two runs were mid-join when this was raised, and one
      of them was being diagnosed for a refusal — editing the script under a diagnosis makes the
      measurement worthless.

- [ ] Fix `SKILL.md:510` to use the flag once it exists.

- [ ] ⚠ Keep `verdicts.py` writing its report to **stdout as well**. It is read by a human at
      the terminal as often as it is captured, and `census.py --out` is silent by comparison
      because nobody reads a census by eye.

- [ ] Add a test that no `python <skill>/scripts/...` line in `SKILL.md` carries a `>`. ⚠ This
      defect is a doc and a script disagreeing, which is the class this repo already tests for
      elsewhere — the check is a grep, and it would have caught it the day it shipped.
