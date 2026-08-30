# The threshold moved, not the perception -- T50 on a keyed case, 2026-08-29

**The same judge read one artifact five times. Four of six fields came back
identical; the two that moved moved by one adjacent letter -- and on those two,
every reading gave the SAME factual account and disagreed only about which
letter it earned.**

!! **THAT DISTINCTION IS THE RESULT.** A judge that perceived different things
each time would be an instrument nobody could calibrate. A judge that perceives
the same thing and rules it `A` three times and `B` twice has a **rubric with an
underspecified boundary**, which is a cheaper defect and a different owner --
`agents`, not `testing`.

## The run

| | |
| --- | --- |
| case | `transcribes-one-comparison` -- START `97359c27`, END `476def7a` |
| file | `plugins/.../scripts/compositor.py`, 389 lines at START |
| key | [`end_diff.patch`](end_diff.patch), 37 lines, **prose only** -- `code_fingerprint` identical across the pair |
| hazard | `transcribes`' docstring claimed *"CONTIGUITY MADE IT ONE COMPARISON"* six lines above the branch that refutes it |
| artifact graded | [`findings.md`](findings.md), one `block-context` run, 48 records over 24 prose paragraphs |
| judge | `claude-opus-5`, rubric **v2** |
| readings | 5 |
| cost | **$0.68 per reading**, ~23,700 output tokens each |

! **THE CASE WAS FOUND BY [`evals/prose_commits.py`](../../evals/prose_commits.py)**, which
surveys history for commits whose Python diff is entirely prose -- an answer key by
construction, with no code half a finding could be right about for the wrong reason.

## What it returned

```
detection      !=  B A B A B     3B / 2A
prescription   !=  B A A A A     1B / 4A
diagnosis      ==  A A A A A
unkeyed        ==  A A A A A
evidence       ==  A A A A A
overall        ==  A A A A A

agreed: False  over 6 of 6 fields, 5 readings
```

**All six fields were measured**, unlike the keyless run recorded in
[`the-judge-disagreed-with-itself`](../the-judge-disagreed-with-itself/README.md), where three
axes graded `N/A` for want of a key and the run bought one axis of stability at the price of
five.

## Why `detection` moved, in the judge's own words

Every reading says the same thing. Reading 4: *"END changed exactly one paragraph: the
`transcribes` docstring (@a4, START lines 222-246). The run filed five records on that
paragraph, and two of them (33, 34) land on the precise sentences END rewrote."* Readings 1, 2,
3 and 5 each state that same account -- one paragraph, five records, two on the rewritten
sentences.

!! **SO THE FACTS NEVER MOVED AND THE LETTER DID.** Three readings called that `B` and two
called it `A`. Nothing in the transcript suggests one reading saw more or less than another;
what differs is where the `A`/`B` line falls on an agreed set of facts.

! **WHICH MAKES MORE SAMPLING THE WRONG FIX.** `decision-log.md Process: #56` -- *"a repeat or
three or four or five off the same result fixes the variance"* -- holds, and n=5 does resolve
this to a mode. But a boundary nobody has written down will keep producing a coin-flip on every
future case, and the rubric is one file.

## What the run says about the reviewer

**`overall` was `A` on all five readings**, and the run found the planted defect: records 33
and 34 of `findings.md` correct *"CONTIGUITY MADE IT ONE COMPARISON"* and *"nothing to
reassemble"* -- the two sentences END rewrote -- against `compositor.py:260` and `:262`.

! **The grade is the JUDGE'S, and it is recorded, not endorsed.** Nothing here checks the
judge's letters against the code; that is C3's job, and it is open.

## Two things underneath the letters

!! **`unkeyed_claims` RANGED 19 TO 47 WHILE `unkeyed` HELD AT `A` EVERY TIME** -- counts of
42, 22, 19, 39, 47 across the five readings. **The letter is stable and the itemisation it
rests on swings 2.5x**, so the list is not yet data anyone should count.

! **`summary.pass_rate` IS `0.0` ON EVERY READING**, because no `--mechanical` file was
supplied and the citation count is therefore `0 of 0`. Harmless here; `aggregate_benchmark`
reads that field, so a run wired into it would report 0% beside an editorial `A`.

## What it does not settle

- **Whether any letter is right.** No reading was checked against the code -- C3/T51.
- **Where the `A`/`B` boundary belongs.** Filed as its own TODO; it is `agents`' to rule.
- **Anything about the other three roles.** One role ran, on one file.
- **The `usage` figures are absent from this artifact** -- the run began 23 seconds before the
  code that records them landed. The per-reading cost above is derived from the account total,
  not read off the response; the next run records it directly.

## How to re-derive it

Free, from the stored readings:

```bash
uv run python -c "
import json, sys; sys.path.insert(0, 'evals'); import reread
d = json.load(open('evidence/the-threshold-moved-not-the-perception/t50-keyed.json', encoding='utf-8'))
print(json.dumps(reread.compare([r['editorial'] for r in d['readings']]), indent=2))
"
```

A NEW reading is Roy's to run -- [`docs/conventions.md`](../../docs/conventions.md), *The
grader costs money, and only Roy runs it*.
