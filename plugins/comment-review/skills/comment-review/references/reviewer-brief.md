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
only quick way to test a claim like *"the only caller"* or *"nothing reads this"*.

⚠⚠ **A server settles a FACT, never a VERDICT.** "This name exists" and "three files call it"
are inputs to your judgement, not a substitute for it. And a server that is ABSENT proves
nothing: if the context does not say one answered, do not assume it — report what you could
not check rather than reporting it clean.

## Read the census end to end

You are given a numbered census and the mechanical resolutions for it. **Read it start to
finish and return at least one RECORD for EVERY block that HOLDS PROSE.**

⚠⚠ **`continues-a-trailing-comment` means the census may have split one sentence.** A trailing
comment closes its run, so a sentence wrapped onto the next line becomes a SECOND block, anchored
to the code BELOW it. Read the two together before ruling. **A mid-clause ending on a block
carrying this annotation is the census's doing, not the author's, and is not a `correct`.**

⚠⚠ **An `interval` block holds nothing, and you owe it no record.** Every gap between two
lines of code is numbered, so most of the census is empty intervals — they are there to be
CITED, not accounted for. An `add` says a constraint exists in code and NOWHERE in prose, which
is a finding about an empty interval; without an index for it the finding had to borrow a
neighbouring block's and read as being about that block's text.

## Every finding is a RECORD, and it is parsed

Emit findings in exactly this shape. A tool joins your report against the
census and against the other roles', so a malformed record is a finding that
does not count.

```text
--- RECORD
BLOCK       17 | redacted_pkg/billing/rates.py:352-354
            # Kept because twenty call sites want this. Narrowing it
            # means re-deriving the clamp bounds.
VERDICT     correct
CLAIM       false: "twenty call sites want this" / true: "31 callers, all in tests/"
REASON      31 callers and every one is under tests/, so the count is stale
SOURCES     redacted_pkg/billing/rates.py:355 | def compute_rates(plan, period, *, clamp=True):
            redacted_pkg/export/invoice.py:88 | rates = compute_rates(plan, period)
CHANGE      # Kept because 31 callers want this, all of them in tests/.
            # Narrowing it means re-deriving the clamp bounds.
---
```

⚠ **A field may run onto the lines below it**, indented, as `BLOCK`, `SOURCES` and `CHANGE` do
here. A blank line ends it.

⚠⚠ **The order is a CHAIN OF CUSTODY, and it is why the fields are in this sequence.** The
ruling, then what must change, then why, then the evidence the why rests on, then the result:
each field answers the question the one above it raises. Write them in this order — a reader
following your finding is following that chain.

| field | what it carries |
| --- | --- |
| `BLOCK` | THREE things: the census INDEX, then `\|`, then the ADDRESS as `path:start-end` — and on the lines below, **the block's text exactly as the file reads it now**. ⚠ **All three are CHECKED against the census.** ⚠ **A finding is ADDRESSED by index and RULED on a sentence, so several of your findings may carry the same `BLOCK`** |
| `VERDICT` | one of the seven |
| `SOURCES` | where you looked, as `file:line | verbatim` — the citation and the text AT it, both verbatim. **Repeat the line, one per place examined.** EVERY one is resolved and every verbatim half must be there |
| `CLAIM` | the SPEC: what must change, and from what to what, in the shape your verdict's row below gives. ⚠ **The half naming the EXISTING sentence is CHECKED against the census text for your `BLOCK`** — if it is not in the block you cited, the finding is on the wrong block |
| `REASON` | what you DERIVED from the source, and why the claim is wrong — one statement |
| `CHANGE` | the RESULT: that edit already made, written out **with the surrounding block**, ready to be substituted |

⚠⚠ **`CLAIM` and `CHANGE` say the same edit twice, and that is deliberate.** `CLAIM` is
surgical, so a checker can find the sentence you are ruling on and two roles ruling on one block
can be told apart. `CHANGE` is the finished prose, so the task agent applies your text rather
than re-deriving it from a diff. ⚠ Write the whole block in `CHANGE`, not just the line you
touched — a block is what gets substituted.

⚠⚠ **`BLOCK` carries the ORIGINAL so the record can be read on its own.** Whoever reads your
finding — the task agent at stage 5, or another role on a re-review — otherwise has to hold the
census open beside it to learn what prose you were even talking about. Transcribe the block;
whitespace and case are forgiven, the words are not.

⚠ **`clean` owes neither the address nor the original** — just the index. Your role returns
`clean` on most of the census, and transcribing every one would make the bulk of your report
text nobody reads.

⚠⚠ **`SOURCES`'s verbatim half is the forcing function, and it is CHECKED.** The cited line is
read out of the file and your text must appear within three lines of it.

⚠ **Cite every site you had to open.** A claim often needs two to settle — the definition and
its callers — and citing one means dropping the other, which is the cut-the-provenance failure
this system exists to catch. ⚠⚠ EVERY one is resolved AND every verbatim half must be there:
a `SOURCES` entry is one statement about one place, so each is checked on its own. ⚠ Each carries a
LINE. A bare filename says you opened a file and not what you read in it, and it is refused.

⚠ **`REASON` is DERIVED, and is not checked verbatim** — that is why it is a separate field
from `SOURCES`. A count is not a line any file contains, so checking the derived statement against
the code made every counted claim inadmissible. ⚠ `CLAIM` and `REASON` were one field split by
`||`; a checker cannot verify both halves of one field, so they are two.

### The verdicts, and what each one MUST carry

**A verdict rules on a SENTENCE, not on a block.** A block of six sentences can carry six
verdicts, and one `clean` sentence must not launder the five around it.

A verdict is a recommendation the task agent will combine with the other roles' and synthesise
into one comment. It is only usable if it carries its payload, so **a verdict without its payload is
not a finding** — *"correct the count"* hands the judgement back; *"replace X with Y"* is the
finding.

**Every shape below is `CLAIM`'s.** `CHANGE` is the same edit already made, written out with
its surrounding block, and it is required for all of these but `clean` and `query` — those two
propose no text, so there is nothing for the task agent to apply.

| verdict   | `CLAIM` |
| --------- | ------- |
| `clean`   | nothing — name your role, nothing else |
| `query`   | which of the three SHAPES it is, in those words, then the claim, the check you ATTEMPTED, and what WOULD settle it — the shape, the ATTEMPTED and the WOULD-settle halves are all CHECKED (as shape, not as truth); the claim itself is checked by nothing |
| `drop`    | `drop: "<the sentence, verbatim>"` |
| `correct` | `false: "<the false clause>" / true: "<the true one>"`, and a `SOURCES` entry carrying the line that settles it |
| `patch`   | `from: "<the sentence now>" / to: "<the rewrite>"` |
| `add`     | `missing: "<the text>"`, **the anchor NAMED in backticks**, and which side — above or below it. The word "anchor" is not an anchor |
| `move`    | `from: <where it sits> / to: <the destination>` |

⚠⚠ **`correct` keeps `false:`/`true:` where `patch` and `move` take `from:`/`to:`, and the pair
is not interchangeable.** `false:`/`true:` ASSERTS the sentence is wrong, and that assertion is
the whole difference between the two verdicts: a `patch` sentence is TRUE and merely reads
badly. A neutral from/to on a `correct` would erase the distinction the synthesis order rests
on, and it is refused.

⚠ **A `move`'s halves are PLACES, not text** — from where it sits, to where it belongs. It is
the one edit whose `CLAIM` names no sentence, because the `BLOCK` is what identifies the prose.

⚠⚠ **A `move` changes TWO blocks, so its `CHANGE` carries BOTH — and this is the only verdict
where `CHANGE` is not a single block.** Write them labelled:

```text
CHANGE      to:   # the destination block, as it reads once the prose arrives
                  # ...including the lines already there.
            from: # the origin block, as it reads once the prose has left.
```

⚠ **`to:` is required. `from:` may be omitted, and omitting it ASSERTS the WHOLE block moved** —
that nothing is left behind to show. Nothing can tell a whole-block move from a partial one by
inspection, so you say which by what you supply. ⚠ If a sentence leaves and the rest stays,
`from:` is how the task agent learns what the remainder reads like; without it, the block is
applied as if it emptied.

⚠ These are `CLAIM`'s two words used again, and they mean something different here: in `CLAIM`
they are PLACES, in `CHANGE` they are the two resulting BLOCKS. The field you are writing
decides which.

#### Does a TRUE sentence earn its place?

**Is it CHECKABLE?** confirmable from the code as it stands. **Is it NECESSARY?** would someone
changing this code make a **worse decision** without it? Those two questions decide:

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | it stays | **drop** — it narrates what the code already says |
| **not checkable** | **move** — real rationale, unverifiable in place | **drop** — history |

⚠ **This runs only on sentences you have already established are TRUE.** A false claim is not a
point on it — it is `correct`. Read generally, *"truth is not one of the questions"* acquits a
falsehood. It applies to history that is TRUE-but-useless and nowhere else.

#### `correct` and `patch` specific rules

⚠ **`correct` and `patch` are not interchangeable.** `correct` says the claim is wrong;
`patch` says it is right and reads badly. The task agent applies every `correct` **before** any
`patch`, so mislabelling one as the other means a false claim gets its wording polished and
never gets checked — that is laundering. If you are unsure which applies, you have not settled
the claim — that is `query`.
⚠ **A sentence that is not truthy cannot be `correct`ed**, because there is nothing to correct
it against — it is `drop` or `query`.
*"The retry budget is 40"* is truthy, and false if the budget is 100. That is a `correct` mark.

*"this is robust"* is not truthy: no line, symbol or run settles it. ⚠ Neither is *"there is no
definition of robust that can be checked in all circumstances"* — **"all circumstances" is as
unbounded as "robust"**, so the sentence refusing the claim fails the same test.

#### `move` specific rules

⚠ **One relocation verdict, and the DESTINATION is what varies.** A declaration ten lines
down, another file, or out of the code entirely — all `move`, and which one goes in the
payload. Say what is wrong in `REASON`. **Only a destination outside the code can be
unavailable**, and your run context says whether it is; a relocation into tracked code is
always available.

#### `clean` specific rules

**`clean` is scoped to YOU, and the other roles are looking at the same block.** The task
agent combines every role's records into one comment or docstring.

**`clean` is a decision and is required — it cannot be assumed or skipped past.**

⚠ **Nothing is `clean` for being SHORT, TRUE, WELL WRITTEN, NEW, or under a `⚠`.** Each was
measured as an exemption reviewers invented for themselves. Truth least of all: a true claim
can be misplaced, unnecessary, or the surviving half of a block whose other half was the
constraint — and none of those is your role's question unless your role file says it is.

#### `query` specific rules

⚠ **`query` is for a claim you could not settle — not one you did not try to settle.** You are
still required to open the code that would settle it; on every other verdict your `SOURCES` proves
you did. `query` is what you emit when you did and it was still not enough.

⚠⚠ **Three shapes reach it, and your `CLAIM` must NAME which one — in these exact words.**
The three are findings rather than admissions, and they route differently: the first says which
scope owns the block, the other two are work that reaches the author. Nothing downstream can
tell them apart if you do not say which:

- **outside my role** — what settles it belongs to another scope.
- **outside the checkout** — generated, gitignored, remote, or on one machine. No reviewer in a
  fresh checkout can settle it.
- **outside the code** — settling it needs someone who knows the system or how it is operated.

⚠ **A claim you could not settle and marked `clean` is worse than the same claim marked
`query`.** `clean` certifies; `query` asks.

⚠ **A `query` requires `SOURCES`, by construction** — this is where you
looked to try to find the answer. These are the statements in the code that make it
ambiguous or the location not yours to determine. **All three shapes carry them**, including
`outside my role`: the block is real and in the checkout on every one of them, so there is
always a line to quote.

⚠⚠ **`outside my role` is a FINDING, so you have to show it is not yours.** It is the shape a
reviewer reaches for when it has nothing to say, and it is the one that costs the most when
it is wrong — the block leaves your report certified by nobody. So quote the line that fixes
the block's SUBJECT, and say in `REASON` what about that subject your remit does not reach,
in the words your own role file uses for its remit. **Never name another role**; you do not
know what the others were asked. *"Not mine"* is an admission. *"Its subject is the loop body,
and my remit is what the module as a whole announces"* is a finding.

## Check the CLAIM, not the CITATION

Resolving a path or a symbol is quick and *feels* like verification. Resolving a claim **is**
the verification. A resolved citation is not a verified one — open the target and read it, or
the verdict is `query`.

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
`CODE CONCERNS` section at the end, with no verdict. The findings this line exists for *look*
like code findings and are not:

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

⚠ **Ruling on the code spends this review on what the code's own tests settle**, and four
agreeing reviewers once reported a file "cannot compile" over valid syntax. A code problem has
a place: `CODE CONCERNS`, one line, no verdict.

### One block, two placements — report yours

REMITS OVERLAP BY DESIGN: the roles read the same code bottom-up and top-down, so two roles
can reach the same or different decisions per sentence. Report what your role sees and say in
`REASON` what is wrong. Which verdict wins is the task agent's ruling later.
