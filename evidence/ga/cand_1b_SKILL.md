---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles — locality,
  currency, functionality, module coherence — using four parallel subagents, and return each finding
  with a proposed verdict (drop / move / compact / keep) for the human to rule on. Use this whenever
  comments or documentation are the subject: after finishing a task that added or edited commentary,
  when a file's comments have drifted from what the code now does, when someone says a comment is
  too long or out of date or "isn't this history", when reviewing a diff specifically for its prose
  rather than its logic, before a docs or comment burn-down, or when asked to check whether a module
  still reads as one module. Trigger on phrasings that never say "comment review" — "these comments
  are getting out of hand", "does this docstring still match", "is this comment still true", "clean
  up the narration in this file", "why does this file need so much explaining" all mean run this. It
  is NOT /simplify (which reviews code structure and applies its fixes) and NOT /code-review (which
  hunts correctness bugs) — this one ONLY EVER PROPOSES and never edits anything, not code and not
  even the comments it rules on, because an edit applied is a verdict the human never got to rule
  on. Run it even when the request sounds like an instruction to cut ("cap these", "clean this up"):
  the deliverable is still the verdict list, and applying is a separate step. It is explicitly not a
  reviewer's job to judge whether the code works: code concerns get raised in a line and left, while
  every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` → 4 reviewers in parallel → a verdict per finding → you rule.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you return is a
verdict on a comment. Note code problems in a separate section, one line each — **raise a concern,
do not open an investigation** — and never give one a `drop`/`move`/`compact`/`keep` verdict. The
best findings look like code findings and are not: *the comment says this reads one field and it
reads three* is yours, *it should not read three* is `/simplify`'s. ⚠ **Straying into correctness is
where this skill's worst output comes from, measured**: twice a reviewer read
`except ValueError, TypeError:` and reported the file "cannot compile" — wrong, 3.14 permits it — and
once four agreeing reviewers shipped it. If a claim is about whether the code RUNS it is not yours.
⚠ **THE GOVERNING LAW, measured across a whole burn-down: every false statement found was one that
NOTHING asserted.** Not the oldest, not the longest, not the furthest from its code — false clauses
sat inside blocks whose other sentences were true, same voice, under the same warning mark; one split
at a comma, the covered half true and the uncovered half false. **So search where no test, no type
and no assertion reaches** — prose beside a passing test, a number nothing recomputes, a claim about
callers, a docstring on a function only tests call. "Where is nothing checking?" finds far more than
"which block is longest?".

## Arguments and scope

**`cap`** is an optional integer, the most lines one comment block may run; pass it to every
reviewer. **This skill has no cap of its own and must not invent one** — with none given, review by
judgement and **report the longest block found**, visible without having been asserted. **`target`**
is an optional path, defaulting to the files in the diff — from
`git diff --name-only @{upstream}...HEAD`, else `main...HEAD`, else `HEAD~1`, adding
`git diff --name-only HEAD` if the tree is dirty. ⚠ **Those fail silently in a worktree** — no
upstream is configured, `main` may not exist, and `HEAD~1` then narrows a ten-commit branch to one
commit with no error. Say which command produced your list and how many files it found. Then review
**every comment and docstring in those files**, not just changed lines — the one place this skill
departs from `/simplify`. Comment debt is cumulative and mostly pre-existing; the 54-line block that
has sat above a four-line expression for months is the finding worth having.

**Widen from a file to a claim.** If a finding is about a symbol, a path, a number or a rule, every
file naming it is in scope for THAT finding — `grep` decides, not the diff. Fixing one copy of a
duplicated number and leaving its twin is how a pass CREATES the drift it came to remove.
**And if the repo publishes its own cap or prose rules, use them and say where you got them** — a
lint config or hygiene test is a decision already made and beats your judgement. Read how it
*measures*, not just its number: matching the number while counting differently produces a file that
claims to comply and does not. Quote its rules rather than recalling them.

## Phase 1 — Four reviewers, in parallel

Launch **four subagents in one message**, each with the file list, the `cap`, any published repo
prose rules, one angle, and: ⚠ **you are READ-ONLY — read, grep, report, never edit.** Four agents
editing one file is a race whose loser's edits vanish, and a reviewer that fixes what it finds has
destroyed the finding. Each finding returns `file`, `line`, a one-line `summary`, the **exact claim**
quoted, the **exact code, grep result or arithmetic that settles it**, and `CONFIRMED` (both sides
read) or `SUSPECTED` (not) — a `SUSPECTED` finding is welcome, an unlabelled one is not. Overlap
between angles is signal: a finding all four report is almost always real. Three habits every angle
needs, because they are where confident reviewers are wrong:

- **Resolving a citation is not verifying it.** A path, test or constant that EXISTS does not check
  what the prose SAYS about it — open the target. A comment once cited a real constant with a real
  value that was simply the wrong one, and the reviewer who looked it up confirmed the finding.
- **Re-derive; do not re-read.** Redo the sum, count the set, list the callers. A stale arithmetic
  read `60 / (1 + 11/30) = 43.90 → 45` where the true working was `62.0 / (1 + 10/30) = 46.5 → 45`;
  all three round the same, so nothing objected, and a reviewer's own correction rotted the same way.
- **Read the prose adjacent to a block before proposing a REMEDY** — not before reporting it, since
  a deliberate-design note can itself be the false one. A function reported for mixing units did so
  deliberately per the line above it, and the remedy would have reopened a settled call.

### Locality — does this comment belong to the line it sits on?

A comment is a claim about the code beside it. **A block points DOWN at the code under it; a
trailing comment points AT its own line.** A field annotation (`retries: int  # 0 disables backoff`)
is where it belongs — never report one as misplaced merely for following a statement. Ask:
1. **What is this fragment ABOUT?** Read it against the statement it touches, not against where it
   sits. Flag a block whose later half turns back to narrate what came before, a note describing a
   function further down, a rule at the top of a class that really constrains two integer literals
   two hundred lines away — seams where two notes merged, or one split and half faced backwards.
2. **If this code changed, would the comment become wrong — and would anyone notice?** Prose that
   would quietly survive a change to the code it claims to describe is not local to it.
3. **Does it point with a WORD that a reorder breaks?** "above", "below", "the next function", "two
   lines down". If the fact is inherently order-dependent the fix is to DELETE the direction word,
   not correct it — corrected in place it is re-armed, not fixed. Same for an in-file pointer:
   `see X's docstring` must still find what it promises, and compacting X is what silently guts it.
4. **Does this block annotate any statement at all?** A `#` run between two declarations, followed
   by a blank line and then unrelated code, owns nothing. That is a rule with no home.
5. **Was a continuation SEVERED?** A trailing comment whose sentence ran on to the next line, where
   that line has since been rewritten, now ends mid-clause — `# … no`, the rest four fields down.
   Nothing red fires: not the formatter, not the type checker, not a cap. Read every trailing
   comment as a whole sentence.
6. **Is this claim written down somewhere else too?** Duplicated prose drifts one copy at a time and
   the copy rots while the owner stays right; report both sites and say which owns the rule. And
   **the inverse: a line carrying a non-obvious constraint with NO comment** — absence is a finding.

⚠ **The keep this angle must protect: a comment whose whole function is WHERE IT IS.** A warning
aimed at the next author, at the point of temptation, is load-bearing *because* it interrupts, and
moving it to a doc satisfies every other rule and destroys it. Test: does it stop a specific edit
somebody would plausibly make right here? Then it stays — compacted, never relocated.

### Currency — does this describe the program as it is now?

Git holds what the code used to be; a comment narrating its own history is doing git's job badly.
Flag dates, review-round labels ("fix round 2", "finding C3", "Part B", "the 08-03 wave"), quotations
and attributed rulings, "this used to…", "X was changed to Y", "retired", "no longer", "before the
fix" — and the sharpest form, **obituaries**: prose naming a symbol, file, test, flag or config key
that no longer exists. Those are worse than noise: the reader greps, finds nothing, and reads it as
*their* mistake. Obituaries are objectively checkable, so **check them**, the way that works:
- ⚠ **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar`
  gets written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Search a loose stem, then triage.
  Measured on one deletion: the identifier grep found ten mentions, all correctly dated tombstones,
  and **missed an eleventh written with a hyphen — the only present-tense claim in the set.** The
  failure is self-concealing; a clean grep reads as a clean file. ⚠ Likewise **a one-word name is
  invisible to a symbol regex** — no dot, no underscore, no camel hump — so read for those by hand.
- ⚠ **A dead name is not always an obituary**: where the dead thing is the SUBJECT of the record —
  "the X column was removed, do not re-add it" — deleting the line loses the only surviving reason.
  An obituary is a stale POINTER; does it send a reader looking, or tell them not to go?
- **A counted claim** — "the 37 ids", "eight callers", "all 1626 other tests", "the one consumer",
  "zero readers". **Re-derive the POPULATION first, then the number.** Naming the set is not enough
  and most of these are wrong at the set, not the count: one correction of a false number produced a
  differently false number because the scope was wrong — direction right, magnitude out by 5×. If
  you cannot re-derive it, the finding is that it is unverifiable; a number nothing recomputes rots.
- **A cited path, test or line number.** Verify it, then READ it. A line number rots silently where
  a symbol survives — two cited "filters" resolved to a blank line and a stray parenthesis. A
  citation a checker cannot parse (a brace expansion, a bare filename, an identifier wrapped across
  lines) is worse than a parseable wrong one: it never gets fixed, and reads as confidence.
- **A label of provenance or status** — "measured", "authored", "ruled on 2026-…", "shipped" — is a
  claim about a decision, so no code can settle it: check the decision record or mark it SUSPECTED,
  never inventing a settlement to tidy a hedge. Likewise **a retracted fact surviving as decoration**
  beside a passing test that never needed it: nothing goes red, which is why it lived.

### Functionality — does the commentary match what the thing is for?

Read the name, the signature, the docstring, then the body, and flag where they disagree: a
`Returns:` naming a shape the code no longer returns, a mapping documented backwards (`{a: b}` where
the body builds `{b: a}`), an `Args:` entry for a parameter that is gone, a documented exception
nothing raises, a summary that describes only the first four lines. Then four questions:

1. **Is it a COVERAGE claim?** "pinned by X", "guarded by X", "asserted in Y", "the only call site",
   "nothing reads this". This class **licenses deletions** and is disproportionately wrong, so it is
   never read — it is checked, and checked for what it ASSERTS. A real guard has been deleted here
   on a pointer to a test nobody ever wrote. ⚠ Check the cited guard CAN fail: one exercised where
   an earlier gate returns first passes whether it exists, is broken, or is deleted.
2. **Is it a UNIVERSAL?** "every X does Y", "always", "never", "all N of them". A universal is a
   CHECKLIST, not a sentence — enumerate the Xs and tick them off. The largest hole measured in one
   review was a module-level "LOUD, NEVER SILENT" false for two of seven paths; every angle passed
   it, because each individual path made it look true.
3. **Is it a DESCRIPTION or a PROHIBITION?** A description must be **positive**: `⚠ NOT the kernel
   call site` makes the reader establish what the code does and argue backwards, where *asserts on
   `session_set_equivalents` directly* is one line to confirm. A prohibition may be negative —
   *"never call `soft_trim` here, or the expectation moves with the code"* has no positive form that
   keeps its force. This tells apart two cases identical from outside: **a DESCRIPTION disagreeing
   with the code means the comment is wrong → drop or fix it; a PROHIBITION disagreeing means the
   CODE broke the rule → file it, and leave the prose alone.**
4. **Does the running commentary describe one job, or five?** Read the `#` comments in order, end to
   end. Take `build_foo_bar`, docstring *"Building a FooBar"*, whose comments read *"Now i need to
   adjust the foo bar" / "oh I should set this other thing up" (a global) / "This other thing should
   also happen" (an I/O call) / "I should also send back those extra args"*. Each is true; together
   they say the function builds, mutates, publishes a global, performs I/O and returns a second value
   the name never hinted at, while the docstring describes the first four lines.

**The tell is grammatical and cheap: a comment that SEQUENCES instead of CONSTRAINS.** *"Now I need
to…", "oh I should…", "then we…"* narrate the author's path through the problem; a comment that earns
its place says why a line must be as it is, and goes visibly wrong when that line moves. Say which of
two each step is: **(A) not needed for the function to be the function** — the global; or **(B) real
work at the wrong level**, belonging to the caller. ⚠ **Report the fork, do not pick it:** either the
docstring grows until it tells the truth — at which point the NAME is wrong — or the function shrinks
to what it is called. ⚠ And that last comment sits above a `return` of the CLASS, not the instance:
**narration of INTENT hides a mismatch that narration of EFFECT would expose**, because it reads as
confirmation and the eye stops. Prefer a claim about the value produced over one about what was meant.

### Module coherence — do the comments say this is one module?

Read the module docstring, the section banners and the top-of-file commentary, and ask whether they
describe one thing. Flag prose announcing two or three subjects, banners reading like chapter breaks
rather than parts of one argument, a docstring enumerating unrelated responsibilities to stay
accurate, and a file or section named for the OCCASION that produced it (a review round, a task
number, a wave) — nobody can apply "it was in that batch" as a membership rule. Two more:

- **Does the file contradict its own headline?** "Single source of truth for X" twenty-five lines
  above a comment explaining that X deliberately lives elsewhere; "one class per session type" in a
  file holding thirteen. Read the headline claim LAST, against everything under it — an overclaim is
  written first, when the file is small, and is never revisited.
- **Is the same rule explained in several modules?** Then it has no owning function, and every site
  performing part of it re-explains the whole. **That is the structural cause of long comments**, and
  a 40-line comment above a four-line expression is usually it. Report it as a code-shape finding
  with the comment as evidence; do not extract it yourself. Two places giving one rule OPPOSITE
  instructions is the same finding at its worst — say which one has code behind it.

**Give this angle the whole file, not a block** — its yield is low when starved: three references to
one dead constant in one file, and only the first was ever noticed.

## Phase 2 — One verdict per finding

Wait for all four, dedup findings on the same block, then rule. **First, the truth table over (what
the comment says, what the code does):**

| | **the code does it** | **the code does not** |
|---|---|---|
| **comment asserts it** | keep — then test necessity | it is the SPEC → file it, the code moves |
| **comment asserts otherwise** | dead → **drop** | **drop**, and file it |

Then, for anything still standing, **two questions in order**. **Is it CHECKABLE?** Could a reader
confirm or refute it from the code as it stands, without archaeology? *"The floor is gated and the
ceiling is not"* is checkable — read the branch. *"This changed last spring"* is not. **Is it
NECESSARY?** Would someone changing this code make a **worse decision** without it? Not "is it
interesting", not "is it true" — would they get it wrong.

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** — a verifiable constraint they need | **drop** — it narrates the code |
| **not checkable** | **move** — real rationale, unverifiable here | **drop** — history |

⚠ **Accuracy is not a licence.** *"Moved here from `x.validate` when that module was deleted"* is
true, and a reader needs the check to live HERE — not where it used to; uncheckable and unnecessary,
so it goes, because history that is *correct* reads as earning its place and does not.

**Rule on sentences, not on blocks.** A container of six sentences holds six verdicts, and the common
shape is a live constraint beside the story of where it came from. ⚠ **A single `keep` sentence
launders every sentence around it** — ruling `keep` because *part* of a block is load-bearing is the
signal to descend a level, and since a block's most defensible sentence is usually why the whole
block survived, that is the default outcome, not a rare one. There is no third category for warnings:
one is load-bearing only where **nothing goes red**; where a test already refuses the mistake it
saves twenty minutes, not correctness, and that is a `compact`.

**Then: is it longer than it needs to be?** If so, **compact** — same content, fewer words; not a
fifth verdict but what you do to a `keep`, or to a `move`'s remainder. Propose the replacement text,
keeping the constraint and what breaks without it. For **move**, name the destination, preferring
wherever the repo already stages extracted prose. ⚠ **The destination gets the WHOLE block, including
the part that stays in the code** — a doc holding only the discarded half reads as a list of
deletions rather than a record of what the code said. ⚠ And **a block one line over cap is, by
construction, mostly right**: cut the single least-checkable line, and do NOT re-author prose already
true, current and on-subject — of the last 48 over-cap runs in one burn-down, 27 were over by exactly
one line. Do not pad the list either: **keep** is a real verdict and a mostly-`keep` review is good.

## Comments and docstrings are governed differently

**A `#` comment is governed by LENGTH** — it interrupts code, so its cost is the screen space between
the line above and the line below, and a run is bounded by CODE, not by blank lines. ⚠ Work markers
(`TODO`, `FIXME`, `HACK`, `XXX`, `BUG`) point *outward* at work not done; where the repo exempts them
they neither spend the budget nor split a run, so never call a block over-cap for a marker line.

**A docstring is governed by FORMAT, not length**: a summary line, then as much body as the reader
needs, then `Args:` / `Returns:` / `Raises:` where they say something the signature does not — so
never propose `compact` on a docstring merely for running long. ⚠ **But "uncapped" is not "anything
goes", and this is where a burn-down silently undoes itself**: prose evicted from a `#` run relocates
into a docstring and nothing notices. A docstring **body carrying a date, a quotation, an attributed
ruling, a review-round or finding label, a "considered and rejected", a rationale paragraph, a
measurement story, or a claim about callers or coverage is a finding at ANY length** — a format
failure, not a length one, and its verdict is `move`. Everything else applies to both: wrong code
described, a parameter documented that is gone, history carried. And check the **summary line** every
time — it is the only part most readers see and it drifts silently, because changing a return type
does not change the sentence describing it; one running past its own first line is a finding itself.

## Phase 3 — Present. Always.

**This skill never edits — not the code, not the comments, at any phase.** It ends with the verdict
list, grouped by verdict, most consequential first, replacement text inline for every `compact`.
⚠ **Even when the human names the edit** — "cap them", "fix these", "go do it" — the deliverable is
the report: *"Report only, per the skill — say the word and I'll apply the verdicts you accept."*
That is a ruling: this review's value IS the human's disagreement with it, and **an edit applied is a
verdict never ruled on**. Measured before this rule, two runs on near-identical imperative prompts
split, one returning a report and one an 846-line diff.

Hand these rails to the pass that DOES apply the verdicts; each cost something on a 43-file run.
**Never change a line of code, a docstring's meaning, or a string literal — and PROVE it**, by
diffing every non-comment line against the pre-edit file on EVERY commit, not the ones where it is
cheap to pass (of four prose-only commits audited later, the one that skipped this had changed three
string literals and a type annotation). **Extract before you cut on a `move`**, destination verbatim
first — the other order loses the text on any interruption, and did, three times — **and do not sever
a sentence**. **Match exactly one occurrence or refuse the whole file**, building the match text
programmatically, and check the replacement's WIDTH as well as its line count. **Re-read what you
wrote**: a pass that cut seven obituaries wrote seven new ones, the same one twice in one file.

## What this is not, and a note for whoever edits it

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness bugs.
This one reviews prose and **only ever proposes** — a defect noticed anyway gets **named and left.**
**Every example above is invented. Keep it that way.** Quoting a real comment teaches a reviewer to
recognise *that comment* rather than the shape, and it rots — the day someone acts on the finding,
this file cites something gone, a hygiene skill carrying its own obituary. Anonymised measurements
keep: "an identifier grep found ten and missed the hyphenated eleventh" is the whole lesson.
