# Does the review process hold together — design, 2026-08-17

**Consolidates 23 open TODOs into 5 work groups and a tail, and settles the contradictions
between them.** Written after two days in which the pipeline ran end to end for the first time,
on three repositories and two languages, and was rolled back once by its own stage 8.

⚠ Every ruling below is Roy's unless marked otherwise. Where he ruled in his own words they are
quoted, because the reasons are load-bearing and the paraphrase loses them.

## Why now

Eleven TODOs were raised on 2026-08-17 alone, from live runs. They were filed one defect at a
time and never read against each other. Reading them together found four contradictions, one
supersession and one piece of work already ruled two days earlier and re-derived as an open
question — enough that filing the twelfth would have cost more than consolidating the eleven.

## The consolidation

| group | absorbs | one question underneath |
| --- | --- | --- |
| **A** unit of review | `the-unit-of-review-is-the-statement-not-the-block`, `move-and-correct-compose`, `a-wrapped-trailing-comment-is-split-into-two-blocks`, `the-finding-record-is-eight-fields-and-six-would-do`, `an-empty-interval-has-no-census-index` (its one open star) | Is a verdict about a block or a sentence, and what does the join key on? |
| **B** send it back | `re-review-is-ordered-everywhere-and-defined-nowhere`, `a-coverage-gap-should-go-back-to-the-reviewer` | One mechanism, five triggers |
| **C** who reads the page | `the-author-approves-blocks-and-never-sees-the-page`, `stage-5-is-the-only-stage-with-no-independent-reader`, `the-code-check-refuses-add-and-drop-on-a-docstring` | What is proven before the author is asked? |
| **D** ownership's standing | `ownership-is-read-first-but-nothing-makes-it-so`, `the-strongest-precedence-has-the-weakest-support` | Does ownership run first? |
| **E** reach | `a-prose-file-has-no-blocks`, `reference-only-misses-the-documentation`, `correcting-one-copy-strands-the-reference-copy` | Do documentation files enter scope? |
| **F** tail | seven files, independent | sequenced by cost |

---

## A — the unit of review

**Settled model, unchanged: a block is how a finding is ADDRESSED; a sentence is what is ruled
on.** The census keeps enumerating blocks.

⚠ **A third of this fixed itself** as a side effect of the interval work. `reviewer-brief.md`'s
*"every census index must appear exactly once"* is gone; it now says *"at least one RECORD for
EVERY block that HOLDS PROSE"* and *"A verdict rules on a SENTENCE, not on a block."*

### A1 — `SKILL.md` is now the outlier

It says *"you receive one per role per block and must synthesise ONE"*. The brief says a role may
file six on one block; the gate permits N (`by_reviewer[...].add(f.block)` is a set).

**Replacement, two clauses:**

> You receive **one or more** per role per block and must emit **ONE** replacement — and you are
> expected to read the code around where that replacement lands, to verify it.

⚠ The second clause is Roy's addition and it is not decoration. Both worse-than-before findings
from the rolled-back run die there: *"every site reads the groups BY NAME"* is checkably false
the moment `_stale_row_scan` is read.

### A2 — `contradictions()` keys on the block; verdicts rule on sentences

**Key on the TEXT.** Both payloads already carry it verbatim: `drop`'s `CHANGE` is the sentence,
`correct`'s is `false: "…"`. Two findings collide only if those strings OVERLAP — either
contains the other, whitespace-normalised, case-insensitive. **No new field**, which matters
because the record is shrinking.

Validated against all three measured cases before proposal:

| block | texts | keyed on block | keyed on text |
| --- | --- | --- | --- |
| 728 | identical sentence | collision | **collision** ✓ |
| 981 | disjoint sentences | collision | **clear** ✓ |
| 1575 | identical sentence | collision | **collision** ✓ |

With `move` leaving the set (composition, ruled 2026-08-17), the measured run goes **8 flagged →
2**, and the re-review independently found exactly 2 genuine.

### A3 — the census can split one sentence across two blocks

A wrapped trailing comment becomes two blocks and the tail re-anchors to the next declaration.
**STAMP it, do not re-cut it.** Merging changes block boundaries and renumbers every census,
invalidating every measurement taken so far. The harm is a reviewer filing `correct` against a
mid-clause ending the census manufactured, and an annotation removes that.

### A4 — the record becomes six fields

`BLOCK, VERDICT, CLAIM, SOURCE, REASON, CHANGE` — ruled previously, and it **is** A's model in
the record: `BLOCK` is purely the address, `CLAIM`/`REASON` are per-sentence.

| was | becomes |
| --- | --- |
| `LOCATION` | **dropped** — the census supplies the range for a block |
| `EVIDENCE` + `QUOTE` | `SOURCE` |
| `SUMMARY` | `CLAIM` |
| `FINDING` | `REASON` |

⚠ It belongs in A rather than the tail: A, B and C all reference these fields, and doing it
later means building three groups against names that then change.

⚠ The checks added 2026-08-17 survive the rename — `FINDING` required becomes `REASON` required,
and `EVIDENCE` taking several comma-separated citations becomes `SOURCE`'s rule. `location_problem`
retires with `LOCATION`.

### A5 — the tree has two names

`an-empty-interval-has-no-census-index` is 9 of 11 done; the census change landed 2026-08-17 and
stage 2 was renamed COLLATE. **One star is open: `pCST` and `prose tree` now name the same
thing.** Before the census enumerated intervals they were distinguishable — the pCST was the
aspiration, the prose tree was *"what the census IS today"*. It builds the first now, so the
second's definition was rewritten into it.

⚠ It belongs in A because it is what A's model is CALLED. `pCST` is precise and is Roy's word;
`prose tree` is what every shipped file says. Whichever goes, the loser belongs in the
retired-words table with its reason.

---

## B — send it back

**Five triggers, one channel:** `SendMessage` to a reviewer that still holds its read. Measured
at ~2 minutes and **zero tool calls**, because nothing is re-derived.

They split in two, and the test is **does it produce a verdict?**

| trigger | kind | who | returns |
| --- | --- | --- | --- |
| contradiction, same sentence | 1 | the colliding roles | amended records |
| coverage gap | 1 | the role that skipped | records for the blocks it missed |
| a block stage 6 must edit that no role ruled on | 1 | **all four** | verdicts on a fresh block |
| `5b` — is this what you meant? | 2 | the filers | hold / revise |
| `6b` — still correct after my edits? | 2 | the filers | hold / revise |

**Kind 1 amends the report** and **ends with the join re-run.** The join is already re-runnable —
one pass ran it three times. That closes a hole: verdicts arriving from stage 6 currently reach
the write with no gate between them.

**Kind 2 confirms the synthesis.** The replacement text is stage 5's work, not the reviewer's, so
no record changes and no re-join. The answer goes back to the stage that wrote the text.

⚠ **The question must be specific**, or a reviewer waves the patch through: *does the replacement
still carry the claim your `SOURCE` settles, and is anything from it gone?* — never *is this OK*.

⚠ **Showing the competing verdict does not break MARK/APPLY separation.** The finding is already
filed and already read by the join. Blindness protects the FIRST read and that is banked.

**Termination:** a Kind-1 round that comes back still contradicting escalates to the author as a
`query` — the existing path. Measured: both real contradictions resolved in one round.

**Consequence:** a coverage gap stops being fatal. Today the join exits nonzero and a human reads
index numbers; under this it is a send-back and the outcome is a completed census.

---

## C — who reads the page

**Ruled 2026-08-15:** *"We do need something that looks at the whole document(s) as it(they)
would be written with the new comments before bringing it to the attention of the person."*

**So 7b's write becomes a dry run first:**

```
5 APPLY → 5b → 6 COMPACT → 6b → materialise into a scratch copy
                                 → CODE CHECK + PROSE CHECK + page read
                                 → 7a PRESENT → author → 7b = copy the proven files into place
```

Everything mechanical happens **before** the author is asked. `7a`'s *"every proposal must be
safe to approve blindly"* stops being an assertion and becomes a result.

### C1 — the PROSE CHECK

**`prove_unchanged.py` states the claim: *"prose changed and the rest reads the same."* It proves
the second half only.** Nothing proves the approved text landed where it was approved to land —
`write.md` asks the applier to *say* so, which is the shape of every rail read and not run.

**Mechanical, and the machinery exists.** Re-census after materialising; for each approved block
assert its approved text is present at the location approved (or at its `move` destination), and
its original text is gone. It catches an Edit landing on the wrong occurrence, a `move` to the
wrong destination, and a block written into a neighbour's position — none of which the AST proof
can see, because it is all comments.

### C2 — stage 8's second run becomes conditional

If the PROSE CHECK proves every block landed and the CODE CHECK proves nothing else moved, **the
written file is provably the file that was read.**

- **blanket approval** → no second page read.
- **selective approval** → a different page. Re-materialise, re-check, re-read.

⚠ Roy: *"If I had stated apply this one not that one would nullify that effort."* A whole-page
reader reads the blocks as a SET; approving a subset means it validated interactions between
edits that will not sit together.

### C3 — INDEPENDENT is not FRESH

| | means | who has it |
| --- | --- | --- |
| independent | did not write the text it reads | the join, the compact agent, filers at 5b/6b, stage 8, the human |
| **FRESH** | formed no prior view of this block | **stage 8 and the human, and nobody else** |

`5b`/`6b` catch *"the synthesis lost my finding"*. They cannot catch *"this page no longer
reads"*, because a filer already has a view.

### C4 — prerequisite: `add` and `drop` on a docstring

The CODE CHECK counts a docstring as an AST statement, so **`add` has never been able to land on
one** and `drop` has the same hole. `5b` would otherwise confirm an edit 7b will refuse.

⚠ Do not weaken the fingerprint — presence is observable, and every shipped CLI here uses
`ArgumentParser(description=__doc__)`. **Split the report:** prove the executable code, list
docstring-presence deltas beside the declaration they sit on, and let a delta with no matching
approval stay a stop.

### C5 — the scope gate

A run may present **the join's work list** and let the author narrow it, before stage 5
synthesises. It is a cost decision, not an approval — final text still reaches the author at 7a
for whatever survived. **Optional, and declared in the proposal when used.**

---

## D — ownership's standing

**RULED: no 4a. Stage 4 stays four blind reviewers in one message.**

Roy: *"the send back is the way this gets resolved — like the initial blind review too much to
let it go."*

The blind dispatch buys corroboration — **51 of 150 blocks had two or more roles converge** on
one measured run. Serialising it to fix ordering spends what is working to patch what B already
handles.

So `ownership-is-read-first-but-nothing-makes-it-so` is ruled **"nothing does at dispatch,
deliberately."** Ownership is read first at SYNTHESIS — step 2, moves before corrects — and that
is the only place it needs to be.

**Verification falls out of B.** A `move` relocates prose that other roles measured at the old
anchor; `6b` asks those filers whether their claim still holds where it landed. That is what
`the-strongest-precedence-has-the-weakest-support` was asking for, arriving as a consequence
rather than a phase.

**One task survives and detaches: census anchors from a LANGUAGE SERVER.** 1.7 already probes,
`documentSymbol` returns the declaration after a run ends, and the census has an `anchor` field
populated only for Python docstrings. The task agent does this by hand today. It belongs with
stages 2–3.

⚠ Residual, stated not solved: at the lexical tier there are no anchors from anywhere and
ownership still holds precedence. Disclosed every run by the census's own header, mitigated by
`6b`, not eliminated.

---

## E — reach

**Reference files become fixable.** Roy: *"leaving stale documentation behind references just
asks to make these harder to trace down later."*

⚠ **The reason this is worth the cost:** the owner of a mis-cited or duplicated rule is
frequently in a file we may not touch, so **the one-edit fix is unavailable and only the N-edit
fix remains.** Measured: 15 blocks cite `CLAUDE.md §N` where the § scheme belongs to
`training-model.md`, six more attribute rules to `CLAUDE.md` that live in `conventions.md`, and
`conventions.md:238` already records the drift. The right fix is one `move`; the reachable fix
was thirty `correct`s, and the run correctly declined to make them.

### E1 — the block model for prose

**A heading is a `banner`; a section is the interval between two headings.** One substitution and
the existing definition transfers: **heading ↔ declaration, section ↔ function, document ↔
module.**

### E2 — all four roles read a prose file

| role | on a `.py` file | on a `.md` file | editorial desk |
| --- | --- | --- | --- |
| `module-context` | does this read as ONE module | **do the headings and layout support the purpose of the doc** | developmental / structural editor |
| `function-context` | does the commentary match what the unit is FOR | **does the section deliver what its heading promises** — a heading is a promise the way a function name is | line editor |
| `block-context` | is every claim true of the code it sits with | **given the heading, is the block appropriate**, and are its claims true — against the code it CITES | fact-checker |
| `ownership-context` | does this belong to the ANCHOR it sits on | does this paragraph belong under THIS heading | — |
| stage 8 | the finished page | the finished page | proofreader |

⚠ `function-context` was nearly retired here by matching on the word *function* rather than on
the question. It is the role that reads a unit against the promise its name makes, and a heading
makes one.

⚠ Honest note: three of the four have their own desk in non-fiction publishing.
`ownership-context` does not — *"this belongs in chapter 2"* is an instrument of the
developmental editor. The split is justified by the mechanism (it holds precedence), not by the
register.

### E3 — the stranded copy

With reference files fixable, `correcting-one-copy-strands-the-reference-copy` reduces to the
detection question: **grep each `correct`'s false clause across the reference files before
applying.** The task agent holds both. It cannot be the join's — `contradictions()` keys on
census block indices and a reference file has no blocks until E1 lands.

---

## F — the tail, by cost

| | file | note |
| --- | --- | --- |
| 1 | `nothing-checks-that-four-reviewers-were-launched` | `--reviewers` defaults to four; the agent WRITES the four names at dispatch. ⚠ Declaration, not observation — the display lags and misled two readers |
| 2 | `compact-can-buy-lines-with-width` | two rules in `compact.md`: no widening to buy a line, no changing KIND to escape the cap. Needs the observed-vs-published ruling |
| 3 | `stage-1-is-re-derived-every-run` **+** `the-emitted-vocabulary-can-collide-with-the-repo` | both are *what the style sheet carries*. Includes the 1.7/1.8 collapse and the CodeGraph ruling |
| 4 | `a-scope-declaration-costs-as-much-as-a-finding` | measure the byte split first, then rule |
| 5 | `a-role-can-reverse-itself-between-runs` | 51-of-150 convergence is its first data point |
| 6 | `the-two-lists-were-tuned-to-one-diff` | five entries to re-derive |
| 7 | `the-shipped-python-does-not-pass-its-own-review` | 6 of 8 done |

⚠ (5) is the only file that could undercut B and C, both of which lean on reviewers as checkers.
Roy has ruled them *"well verified at this point"*, so it is a measurement confirming a standing
ruling, not a blocker.

## Order

**A → B → C → D → E → F**, with the reasons: A defines what a verdict is about and carries the
record change every later group references; B's mechanism is what C's `5b`/`6b` and D's
resolution both use; C needs B; D reduces to one detached task; E is independent but grows scope
and needs A's model for its own block definition.

## Still Roy's to rule

- **A3** — stamp, merge, or leave the split trailing comment
- **A5** — `pCST` or `prose tree`; one name retires
- **C4** — accept *split the report*, or go further and make the CODE CHECK a diff against the
  approved set rather than a blanket nothing-changed proof
- **F2** — is stage 6 bound by an OBSERVED wrap or only a published one
- **F3** — where a style sheet lives; whether CodeGraph becomes a structure source
- **B** — the name of the file that owns the send-back, now that it is more than re-review
- **E** — whether `CODE CONCERNS` widens to carry a systemic finding, or gets a sibling section

## Not measured, and load-bearing

⚠ **Every measurement behind this design was taken by a session that knew it was testing the
skill.** Refusing to reword a report to satisfy a parser, and rolling back rather than shipping,
are cheap when the refusal is the result being sought. Nothing here measures the case where the
gate is the obstacle between an operator and finishing.
