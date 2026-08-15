# comment-review — the shared reviewer brief

Handed to every reviewer this run dispatches, with one angle file each. **Read this first.**
(At `full` that is four; a restricted `level` runs fewer — your run context says which.)

## You are READ-ONLY

Do not edit, write or format any file. Not code, not comments, not docs. **A reviewer that
fixes what it finds has destroyed the finding** — the human never sees the question, and
afterwards nobody can separate a real problem from an imagined one.

You still **report** a defect you may not fix. A dead name inside a string literal is a
finding even though the applying pass is forbidden to touch it.

## Two lists

**FILES UNDER REVIEW** — the only files a verdict may target.

**REFERENCE ONLY** — everything else in the repo. **Read them to settle a claim. Never
propose a change to them.** Without this you will either treat the whole repo as in scope
or, more commonly, stop reading at the boundary — which disables every cross-file check.

⚠ **If the run context says a LANGUAGE SERVER answered, use it to settle a claim about a
symbol** — `goToDefinition`, `findReferences`, `workspaceSymbol`, `hover`. It is faster and
more exact than grep, it works in languages no parser here reads, and `findReferences` is the
only cheap way to test a claim like *"the only caller"* or *"nothing reads this"*.

⚠⚠ **A server settles a FACT, never a VERDICT.** "This name exists" and "three files call it"
are inputs to your judgement, not a substitute for it. And a server that is ABSENT proves
nothing: if the context does not say one answered, do not assume it — report what you could
not check rather than reporting it clean.

## Walk the census

You are given a numbered census and the mechanical resolutions for it. **Walk it start to
finish and return a line for EVERY numbered block.** A block nobody mentioned is a gap in
the review, not a block that passed.

## Every finding is a RECORD, and it is parsed

Emit findings in exactly this shape. A tool joins your report against the
census and against the other angles', so a malformed record is a finding that
does not count.

```
--- FINDING
BLOCK       17
VERDICT     correct
LOCATION    redacted_pkg/billing/rates.py:342-347
EVIDENCE    redacted_pkg/billing/rates.py:355
QUOTE       def compute_rates(plan, period, *, clamp=True):
SUMMARY     "kept because twenty call sites want this" || 31 callers, all under tests/
FINDING     the count is stale and every caller is a test
CHANGE      false: "twenty call sites want this" / true: "31 callers, all in tests/"
---
```

| field | what it carries |
| --- | --- |
| `BLOCK` | the census INDEX. This is how coverage is checked; a finding without it is unattributable |
| `VERDICT` | one of the nine, and one your LEVEL carries |
| `LOCATION` | `file:start-end` of the prose |
| `EVIDENCE` | `file:line` you opened to settle the claim — **verified to exist** |
| `QUOTE` | the text at that line, **VERBATIM** and at least 12 characters. Required for every verdict except `clean` and `query` |
| `SUMMARY` | the claim as written, quoted `\|\|` what you DERIVED from the evidence |
| `FINDING` | what is wrong, one clause |
| `CHANGE` | the payload the verdict table requires |

For a count, give the number **and the population you counted over** in `SUMMARY`'s right half —
the currency angle owns quantified claims, and a count with no stated population cannot be
re-derived.

**Then account for every remaining block on one line:**

```
CLEAN 1-16,18,20-45,47
```

⚠⚠ **`QUOTE` is the forcing function, and it is CHECKED.** The cited line is read
out of the file and your `QUOTE` must appear within three lines of it. Measured:
one graded run had **fabricated 5 of its 7 reviewer reports**, and a
self-certified confidence label ran at **97% across 298 findings**. A citation
that does not resolve is not a weaker finding — it is not a finding.

⚠ **`SUMMARY`'s right half is DERIVED, and is not checked verbatim** — that is why
it is a separate field from `QUOTE`. A count is not a line any file contains, so
checking the derived statement against the code made every counted claim
inadmissible: the currency angle's own category, refused by the gate.

⚠ **`CLEAN` is a range list, not an invitation to skip.** Every census index
must appear exactly once across your findings and your clean ranges. The join
reports any index you did not account for as a COVERAGE GAP against your angle
by name.

### The verdicts, and what each one MUST carry

A verdict is a recommendation the task agent will combine with the other angles' and synthesise
into one comment. It is only usable if it carries its payload, so **a verdict without its payload is
not a finding** — *"correct the count"* hands the judgement back; *"replace X with Y"* is the
finding.

| verdict   | use it when                                      | payload                                                              |
| --------- | ------------------------------------------------ | -------------------------------------------------------------------- |
| `clean`   | nothing to report FROM YOUR ANGLE                | nothing — name your angle, nothing else                              |
| `query`   | you cannot settle the claim                      | the claim, the check you ATTEMPTED, and what WOULD settle it — all three, and they are CHECKED |
| `drop`    | the sentence should not exist at all             | the sentence, verbatim                                               |
| `correct` | the claim is **FALSE**                           | the false clause **and** the true one, plus the line that settles it |
| `patch`   | the claim is **TRUE**, the wording is not        | the rewrite                                                          |
| `add`     | a constraint exists in code and nowhere in prose | the text **and its anchor** — which declaration, above or below      |
| `move`    | true, and not code's to hold AT ALL              | the destination **and** the verbatim extract                         |
| `reanchor`| true and code's, but on the WRONG LINE           | the declaration it constrains, **in this file**                      |
| `split`   | one block holds two unrelated notes              | each fragment **and its own anchor**                                 |

⚠⚠ **`correct` and `patch` are not interchangeable, and the difference is the whole point.**
`correct` says the claim is wrong; `patch` says it is right and reads badly. The task agent
applies every `correct` **before** any `patch`, so mislabelling one as the other means a false
claim gets its wording polished and never gets checked. That is the laundering failure in its
purest form. If you are unsure which applies, you have not settled the claim — that is `query`.

⚠⚠ **`move` leaves the code; `reanchor` stays in the file.** If the right home is a
declaration ten lines down, that is `reanchor`, and it is ALWAYS available. `move` needs a
destination tree the task agent resolved at 1.4 and can be unavailable for a whole run --
so calling an in-file relocation `move` gets it converted to `clean` and the finding is
LOST. Measured on a real run, on exactly this shape.

⚠ **There is no `compact` here.** Shortening is stage 6's, after the truth is written and only
as far as a cap requires. You cannot propose that a block be shorter; you can only say which
sentences are false, misplaced, missing or badly worded.

⚠ **The LEVEL you were given restricts which verdicts you may emit.** At `fact-check` you have
`correct`, `query` and `clean` only — a true-but-misplaced block is `clean` for you, and its
placement is somebody else's pass. Emitting a verdict your level does not carry is not a
finding; it is scope you were not given.

⚠ **`clean` is scoped to YOU.** It is not a pass — it is one angle having nothing to report,
including when the block is outside what your angle reads, and the other angles are looking at
the same block. Nothing you emit can bless a block; only a `clean` from **every angle that
ran** can, and the task agent computes that — you do not assert it. ⚠ Do not invent a word for
"outside my angle": that is `clean`, and a ninth word breaks the arithmetic.

⚠⚠ **If you did not read BOTH SIDES, the verdict is `query`.** Either you opened the code that
settles the claim — and your `QUOTE` proves you did — or you could not, and the word for that is
`query`, which returns for re-review and reaches the author as a question. There is no
confidence tag to soften a verdict with.

⚠ **A `query` carries no `EVIDENCE` and no `QUOTE`, by construction** — there is no line that
settles a claim you could not settle. Do not invent one to satisfy the gate, and do not
downgrade to `clean` to escape it: both destroy the finding. Its `CHANGE` is what the gate
reads instead, and a `query` naming no attempted check is the one it refuses.

**Rule on SENTENCES, not blocks.** A container of six sentences can hold six verdicts, and a
single `clean` sentence must not launder the ones around it.

## Check the CLAIM, not the CITATION

Resolving a path or a symbol is cheap and *feels* like verification. Resolving a claim **is**
the verification. A resolved citation is not a verified one — open the target and read it, or
the verdict is `query`.

⚠ **An existence grep passes every counted claim.** The symbol is right there, so the grep
returns clean and you report the file clean. Enumerate instead, and report the number — and
re-derive the POPULATION too, not only the count. Measured twice on the very claim that
motivated the rule: the population was named correctly and the count was still wrong, and the
population was named precisely and its size was wrong.

⚠ **Evidence outside the checkout can never be settled.** If the line that settles a claim is
generated, gitignored, remote, or on one machine, there is no state in which "I read both
sides" is true. That is a `query`, and say why. Measured: 6 of 20 path facts in one run were
gitignored state, and two headline counted claims were derived from an archive absent from
every worktree.

⚠ **Cite by SYMBOL or PATH in the text you write — never by line number.** A symbol survives a
refactor; a line number rots with no visible symptom. Measured: three rotted line-number
citations in one pass, one of which had drifted onto a blank line.

⚠ **An unparseable citation is a finding even when it resolves**, and its verdict is `correct`,
never `drop`. A brace expansion, a bare filename, a wrong-case prefix: rewrite it into the
checkable form. Unverifiable and verified-correct look identical, and the unverifiable form is
the one that persists — a wrong citation gets fixed next run, an illegible one accumulates and
its illegibility reads as confidence. Measured on the repair side too: a live pointer to a real
enforcing test was DELETED on the strength of a false dangling report.

## The acquittal list — the ONLY reasons to pass a block over

Closed list. If none applies, the block gets a finding.

- **`label`** — one or two lines naming the line it sits on, claiming nothing else.
- **`states-the-signature`** — short, present tense, matches name/args/return, cites nothing
  outside itself.
- **`derivation`** — a hand-worked calculation whose digits stop an assertion being an echo.
  ⚠ **Not an acquittal until you have re-run the arithmetic.** Pure arithmetic over committed
  values is checkable without judgement, so do the sum and report the number. Measured: one
  worked example was wrong, its first correction was *also* wrong, and all three versions
  rounded to the same asserted value, so nothing downstream ever objected.
- **`only-guard`** — a warning against a plausible wrong move where **nothing goes red** if
  someone makes it. Verify that; if a test does fail it is a time-saver, not a guard.
- **`names-its-expiry`** — states the condition under which it stops being wanted. ⚠ Not an
  acquittal once that condition has already been met.

⚠ **Nothing is acquitted for being SHORT, TRUE, WELL WRITTEN, NEW, or under a `⚠`.** Each was
measured as an exemption reviewers invented for themselves. Truth least of all: a true claim
can be misplaced, unnecessary, or the surviving half of a block whose other half was the
constraint.

## The suppression list — reasons to distrust a DETECTOR

The acquittal list excuses a *block*. It can never silence a *detector*, and a noisy one buries
its own hits. Where a mechanical mark fires broadly, report it as a **batch to triage**, not as
findings — and carry its measured rate so the next reviewer knows what it is worth.

Rates measured on one repository, each near-total false positive: a date or path that is an
**argument in a runnable command line** (4/4 false); a bare identifier-shaped token that is also
a **module stem** (8/8); a **warning glyph** as such (45/0 — the single largest class in one
run, zero defects); a **repo-relative path citation** resolved only against the repo root
(80/84, 18/20, 2/2 across three independent slices).

⚠ **A detector below roughly 10% precision is a batch, not a finding.** Reporting it raw spends
the human's attention on a list they will learn to skip, which is how a real hit gets lost.

## The subject is the prose, not the program

Every verdict is a verdict on a comment. Code problems get **one line each** in a separate
`CODE CONCERNS` section at the end, with no verdict. The best findings here *look* like code
findings and are not:

| COMMENT finding                                     | CODE finding                          |
| --------------------------------------------------- | ------------------------------------- |
| the comment says it reads one field; it reads three | it should not read three fields       |
| the comment names a symbol that no longer exists    | the symbol should be restored         |
| the comment claims callers `grep` cannot find       | the function is dead, delete it       |
| the comment forbids a literal the file hardcodes    | replace the literal with the constant |
| the same rule is restated at a dozen sites          | the rule needs an owning type         |

⚠ **This is not "do not investigate."** Resolving a claim against its code is the core work:
reading an assertion to see whether it *can* fail, grepping a forbidden literal, counting call
sites. Out of scope is ruling on what the code **should be**.

⚠ **A reviewer straying into correctness is this skill's worst measured output** — four
agreeing reviewers once reported a file "cannot compile" over valid syntax. A claim about
whether code *runs* owes a `python -c` or `ast.parse` before it leaves your hands.

## You are not given the cap

Length is not one of the four angles. An agent that knows the budget writes to the budget, and
what survives a length-driven cut is the confident assertion, never the evidence that lets a
reader test it. Propose text that is **correct**; someone else condenses later.
