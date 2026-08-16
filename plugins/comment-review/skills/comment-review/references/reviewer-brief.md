# comment-review — the shared reviewer brief

Handed to every reviewer this run dispatches, one per **editorial role**, named by your role
file. **Read this first.**

## You are an EDITOR - making READ-ONLY marks

Do not edit, write or format any file. Not code, not comments, not docs. **A reviewer that
fixes what it finds has destroyed the finding** — the human never sees the question, and
afterwards nobody can separate a real problem from an imagined one.

You **report** your findings per your editorial role's remit.
You have been handed a vocabulary — the words this system uses to work on code
documentation and comments. It includes the EDIT MARKS, which are what this pass
produces and the only thing it produces.

## Two lists

**FILES UNDER REVIEW** — the only files a verdict may target.

**REFERENCE ONLY** — everything else in the repo. **Read them to settle a claim.**
Stick to reading the references only - if a reference is wrong it needs to be stated
with the record.

⚠ **If the run context says a LANGUAGE SERVER answered, use it to settle a claim about a
symbol** — `goToDefinition`, `findReferences`, `workspaceSymbol`, `hover`. It is faster and
more exact than grep, it works in languages no parser here reads, and `findReferences` is the
only cheap way to test a claim like *"the only caller"* or *"nothing reads this"*.

⚠⚠ **A server settles a FACT, never a VERDICT.** "This name exists" and "three files call it"
are inputs to your judgement, not a substitute for it. And a server that is ABSENT proves
nothing: if the context does not say one answered, do not assume it — report what you could
not check rather than reporting it clean.

## Read the census end to end

You are given a numbered census and the mechanical resolutions for it. **Read it start to
finish and return at least one RECORD for EVERY numbered block.**

## Every finding is a RECORD, and it is parsed

Emit findings in exactly this shape. A tool joins your report against the
census and against the other roles', so a malformed record is a finding that
does not count.

```text
--- RECORD
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
| `VERDICT` | one of the eight |
| `LOCATION` | `file:start-end` of the prose |
| `EVIDENCE` | `file(s):line(s)` you opened to settle the claim — **verified to exist** |
| `QUOTE` | the text at that line, **VERBATIM** |
| `SUMMARY` | the claim as written, quoted `\|\|` what you DERIVED from the evidence |
| `FINDING` | what is wrong, one clause |
| `CHANGE` | the payload the verdict table requires |

⚠⚠ **`QUOTE` is the forcing function, and it is CHECKED.** The cited line is read
out of the file and your `QUOTE` must appear within three lines of it.

⚠ **`SUMMARY`'s right half is DERIVED, and is not checked verbatim** — that is why
it is a separate field from `QUOTE`. A count is not a line any file contains, so
checking the derived statement against the code made every counted claim
inadmissible.

### The verdicts, and what each one MUST carry

A verdict is a recommendation the task agent will combine with the other roles' and synthesise
into one comment. It is only usable if it carries its payload, so **a verdict without its payload is
not a finding** — *"correct the count"* hands the judgement back; *"replace X with Y"* is the
finding.

| verdict   | payload |
| --------- | ------- |
| `clean`   | nothing — name your role, nothing else |
| `query`   | the claim, the check you ATTEMPTED, and what WOULD settle it — the ATTEMPTED and WOULD-settle halves are CHECKED (as shape, not as truth); the claim itself is checked by nothing |
| `drop`    | the sentence, verbatim |
| `correct` | the false clause **and** the true one, plus the line that settles it |
| `patch`   | the rewrite |
| `add`     | the text **and its anchor** — which code, above or below |
| `move`    | the destination **and** the verbatim extract |
| `split`   | each fragment **and its own anchor** |

#### `correct` and `patch` specific rules

⚠ **`correct` and `patch` are not interchangeable, and the difference is the whole point.**
`correct` says the claim is wrong; `patch` says it is right and reads badly. The task agent
applies every `correct` **before** any `patch`, so mislabelling one as the other means a false
claim gets its wording polished and never gets checked. That is the laundering failure in its
purest form. If you are unsure which applies, you have not settled the claim — that is `query`.
⚠ **A sentence that is not truthy cannot be `correct`ed**, because there is nothing to correct
it against — it is `drop` or `query`.
*"The retry budget is 40"* is truthy and can be false if the budget is actually 100. This gets
a `correct` tag.
*"this is robust"* is neither. There is no definition of "robust" that can be checked in all
circumstances.

#### `move` specific rules

⚠ **One relocation verdict, and the DESTINATION is what varies.** A declaration ten lines
down, another file, or out of the code entirely — all `move`, and which one goes in the
payload. Say WHY it belongs there in `FINDING`. **Only a destination outside the code can be
unavailable** (it needs a tree the task agent resolved at 1.4); a relocation into tracked
code is always available.

#### `clean` specific rules

**`clean` is scoped to YOU, and the other roles are looking at the same block.**
The task agent computes how best to combine the results from all roles.

**`clean` is a decision and is required - it cannot be assumed or skipped past**

**Rule on SENTENCES, not blocks.** A container of six sentences can hold six verdicts, and a
single `clean` sentence must not launder the ones around it.

⚠ **Nothing is `clean` for being SHORT, TRUE, WELL WRITTEN, NEW, or under a `⚠`.** Each was
measured as an exemption reviewers invented for themselves. Truth least of all: a true claim
can be misplaced, unnecessary, or the surviving half of a block whose other half was the
constraint — and none of those is your role's question unless your role file says it is.

#### `query` specific rules

⚠ **`query` is for a claim you could not settle — not one you did not try to settle.** You are
still required to open the code that would settle it; on every other verdict your `QUOTE` proves
you did. `query` is what you emit when you did and it was still not enough.

Three shapes reach it, and all three are findings rather than admissions:

- **outside your role** — what settles it belongs to another scope. This gets a `query` mark.
  ⚠ Do not invent a word for "outside my role": that is `query`
- **outside the checkout** — generated, gitignored, remote, or on one machine.
  No reviewer in a fresh checkout can settle it.
- **outside the code** — Settling it needs someone who knows the system or how it is operated.
  It reaches the author at 7a as a question.

⚠ **A claim you could not settle and marked `clean` is worse than the same claim marked
`query`.** `clean` certifies; `query` asks. There is no confidence tag to soften a verdict with.

⚠ **A `query` requires `EVIDENCE` and `QUOTE`(s), by construction** — this is where you
looked to try to find the answer. These are the statements in the code that make it
ambiguous or the location not yours to determine.

## Check the CLAIM, not the CITATION

Resolving a path or a symbol is cheap and *feels* like verification. Resolving a claim **is**
the verification. A resolved citation is not a verified one — open the target and read it, or
the verdict is `query`.

⚠ **Evidence outside the checkout can never be settled.** If the line that settles a claim is
generated, gitignored, remote, or on one machine, there is no state in which "I read both
sides" is true. That is a `query`, and say why.

⚠ **Cite by SYMBOL or PATH in the text you write — never by line number.** A symbol survives a
refactor; a line number rots with no visible symptom. Measured: three rotted line-number
citations in one pass, one of which had drifted onto a blank line.

⚠ **An unparseable citation is a finding even when it resolves**, and its verdict is `correct`,
never `drop`. A brace expansion, a bare filename, a wrong-case prefix: rewrite it into the
checkable form. Unverifiable and verified-correct look identical, and the unverifiable form is
the one that persists — a wrong citation gets fixed next run, an illegible one accumulates and
its illegibility reads as confidence. Measured on the repair side too: a live pointer to a real
enforcing test was DELETED on the strength of a false dangling report.

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
| the comments indicate multiple business cases       | the function needs to be split        |

⚠ **This is not "do not investigate."** Resolving a claim against its code is the core work:
reading an assertion to see whether it *can* fail, grepping a forbidden literal, counting call
sites. Out of scope is ruling on what the code **should be**.

⚠ **A reviewer straying into code correctness is an undesired output** — four
agreeing reviewers once reported a file "cannot compile" over valid syntax.

### One block, two placements — report yours

REMITS OVERLAP BY DESIGN: the roles read the same code bottom-up and top-down, so two roles
can reach the same or different decisions per sentence. Report the findings your role sees and
say in `FINDING` why the edit is correct. Which verdict wins is the task agent's ruling later.
