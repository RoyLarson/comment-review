# The shipped Python's comments say what the code does NOT do

```
Status:   open
Progress: 0 of 8 tasks done
Owner:    session
Raised:   2026-08-16 (Roy, on `census.py`: "this creates the pCST and that is it.
          Comments about 'cannot answer OWNERSHIP' are not helpful.")
```

## Objective

⚠⚠ **The reason is not tidiness — it is what the system learns from reading itself.** Roy,
2026-08-16: *"I don't want the system picking up bad cues from the documentation in the code."*
`CLAUDE.md` carries the same argument for vocabulary: an agent reads these files and then writes
in them, so the REGISTER is an instruction. A repo whose own scripts spend a fifth of their prose
on what the code does NOT do is demonstrating the shape its four editorial roles exist to remove.

**A comment should state what the code does.** These scripts state what it does *not* do, what it
is *not*, and how it compares to other passes.

Measured over `plugins/**/*.py`, counting comment and docstring lines carrying `cannot` /
`never` / `does not` / `is not` / `nothing` / `neither` / `without` / `no longer` / `not a`:

| file | before 2026-08-16 | after that day's work |
| --- | ---: | ---: |
| `census.py` | 52 / 284 (18%) | 55 / 286 (19%) |
| `prove_unchanged.py` | 21 / 111 (19%) | 22 / 110 (20%) |
| `referrers.py` | 9 / 54 (17%) | 10 / 42 (24%) |
| `run_context.py` | 14 / 104 (13%) | 17 / 96 (18%) |
| `verdicts.py` | 27 / 161 (17%) | 28 / 144 (19%) |
| `vocabulary.py` | — | 4 / 19 (21%) |
| **total** | **123 / 714 (17%)** | **136 / 697 (20%)** |

⚠ **It went UP.** All five scripts were rewritten that day and the prose written with them carries
the same defect — which is the argument for fixing it at the source rather than trusting a pass
to notice. The second column is the baseline to work from.

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

- [ ] `census.py`'s two uses of **suppressed** go with the rest. `:80` (*"a real obituary is
      suppressed because some library happens to define that name"*) and `:615` (*"it can only
      ever suppress an obituary, never manufacture one"*) describe a FAILURE — a true finding
      silently lost — in a word that named a mechanism this system no longer has. Roy,
      2026-08-16, ruling `NOISE_FLOOR` out of `referrers.py`: *"Nothing gets suppressed… that
      form of suppressed will also go."* ⚠ `:149` referenced the brief's *"suppression list"*
      and is fixed with it, not here.

- [ ] Then `prove_unchanged.py`, `verdicts.py`, `run_context.py`, `referrers.py`.

- [ ] ⚠ Re-run the measurement afterwards and record both numbers. The point is not zero —
      a target of zero would delete the legitimate refusals. Record what the residue was and
      why each survivor earned its place.

- [ ] ⚠ **A second shape, ruled 2026-08-16: a script's output may state only what the script
      DID.** Roy: *"the python files are mechanical runs, they should only have documentation
      about what they are doing."* Two headers argued a rule at the reader instead —
      `census.py` printed *"every block. A block nobody mentions is a gap in the review"* and
      `verdicts.py` *"a block nobody mentioned is a gap, not a pass"*. Both are now what they
      print: *"every block, numbered"* and *"indices no reviewer accounted for"*. ⚠ Sweep the
      other output strings in all five scripts for the same shape; the rule the two carried is
      the task agent's and is stated at `SKILL.md:82-84`.

- [ ] Check the same shape in the shipped MARKDOWN before deciding it is a Python problem.
      `SKILL.md`, the brief and the agent files are instructions, where prohibitions are
      legitimate — but *"it is NOT X"* used as a definition is the same defect wherever it sits.

- [ ] ⚠ Do not run `/comment-review` on this repo to do it. The skill is mid-rewrite across
      several branches; a run now would review prose that is about to change and would grade
      itself. This is a hand pass, and the eval harness stays out of it.
