# The shipped Python's comments say what the code does NOT do

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session
Raised:   2026-08-16 (Roy, on `census.py`: "this creates the pCST and that is it.
          Comments about 'cannot answer OWNERSHIP' are not helpful.")
```

## Objective

**A comment should state what the code does.** This repo's own scripts spend a sixth of their
prose on what it does *not* do, on what it is *not*, and on comparisons to other passes —
exactly the shapes the four editorial roles exist to remove.

Measured 2026-08-16 over `plugins/**/*.py`, counting comment and docstring lines carrying
`cannot` / `never` / `does not` / `is not` / `nothing` / `neither` / `without`:

| file | negative-form prose lines |
| --- | ---: |
| `census.py` | 52 / 284 (18%) |
| `prove_unchanged.py` | 21 / 111 (19%) |
| `referrers.py` | 9 / 54 (17%) |
| `run_context.py` | 14 / 104 (13%) |
| `verdicts.py` | 27 / 161 (17%) |
| **total** | **123 / 714 (17%)** |

Roy's example: `census.py:351` — *"cannot answer OWNERSHIP, so no block gets an owner and the
ownership-context…"*. **`census.py` builds the pCST. That is what it does.** What it cannot
answer is a fact about a tier, and where it is load-bearing it can be stated positively — *what
IS recorded* rather than what is not.

⚠ **A negative is not automatically wrong.** *"A file this cannot prove is REPORTED as
unprovable, never passed"* states a real behaviour, and a refusal aimed at a future editor is
one of the four refusals the residue check protects. The task is to find the ones that only
compare, hedge, or pre-empt — not to strip every `not`.

## Tasks

- [ ] Establish the test before rewriting anything. A negative stays when it names an OUTPUT
      (*"reports UNPROVABLE rather than passing"*) or is a refusal aimed at whoever edits next.
      It goes when it only distinguishes this thing from another (*"it is NOT stage 8's proof
      pass"*), hedges, or answers a question nobody asked. Write the test down first; it is what
      makes this checkable rather than a matter of taste.

- [ ] `census.py` first — 52 lines, the largest share, and the file Roy named. Start from the
      module docstring: say it builds the pCST and what each output contains, and move
      tier-capability statements to positive form.

- [ ] Then `prove_unchanged.py`, `verdicts.py`, `run_context.py`, `referrers.py`.

- [ ] ⚠ Re-run the measurement afterwards and record both numbers. The point is not zero —
      a target of zero would delete the legitimate refusals. Record what the residue was and
      why each survivor earned its place.

- [ ] Check the same shape in the shipped MARKDOWN before deciding it is a Python problem.
      `SKILL.md`, the brief and the agent files are instructions, where prohibitions are
      legitimate — but *"it is NOT X"* used as a definition is the same defect wherever it sits.

- [ ] ⚠ Do not run `/comment-review` on this repo to do it. The skill is mid-rewrite across
      several branches; a run now would review prose that is about to change and would grade
      itself. This is a hand pass, and the eval harness stays out of it.
