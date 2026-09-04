# comment-review -- the shared reviewer brief

Handed to every reviewer this run dispatches, one per **editorial role**, named by your role
file. **Read this first.**

## You are an EDITOR - making READ-ONLY marks

Do not edit, write or format the code. Not source, not comments, not docs, not a file you
opened to settle a claim. **A reviewer that fixes what it finds has destroyed the finding** --
the human never sees the question, and afterwards nobody can separate a real problem from an
imagined one.

!! **You write exactly ONE file: the RECORD FILE you were handed, and you edit it in place.**
That is your report, and it is the only exception. Nothing you find licenses a second one --
not a summary beside it, not a note to the task agent, not a corrected copy of a paragraph. ! **If
your record file does not reach you, say so and stop.** Reporting in prose instead is the
failure this shape exists to end: it goes to a parser that has to guess where each field ends,
which is where every boundary defect this system has paid for came from.

You **report** your findings per your editorial role's remit.
You have been handed a vocabulary -- the words this system uses to work on code
documentation and comments. It includes the EDIT MARKS, which are what this pass
produces and the only thing it produces.

## Two lists

**FILES UNDER REVIEW** -- the only files an instruction may target.

**REFERENCE ONLY** -- everything else in the repo. **Read them to settle a claim.**
Stick to reading the references only - if a reference is wrong it needs to be stated
with the record.

! **If the run context says a LANGUAGE SERVER answered, use it to settle a claim about a
symbol** -- `goToDefinition`, `findReferences`, `workspaceSymbol`, `hover`. It is faster and
more exact than grep, it works in languages no parser here reads, and `findReferences` is the
only quick way to test a claim like *"the only caller"* or *"nothing reads this"*.

!! **A server settles a FACT, never an INSTRUCTION.** "This name exists" and "three files call it"
are inputs to your judgement, not a substitute for it. And a server that is ABSENT proves
nothing: if the context does not say one answered, do not assume it -- report what you could
not check rather than reporting it clean.

## Read the census end to end

You are given a numbered census and the mechanical resolutions for it. **Read it start to
finish and return at least one RECORD for EVERY paragraph that HOLDS PROSE.**

!! **`continues-a-trailing-comment` means the census may have split one sentence.** A trailing
comment closes its run, so a sentence wrapped onto the next line becomes a SECOND paragraph, anchored
to the code BELOW it. Read the two together before ruling. **A mid-clause ending on a paragraph
carrying this annotation is the census's doing, not the author's, and is not a `correct`.**

!! **FRONT MATTER IS NOT YOURS, and you will not be shown it.** A licence header, a shebang or
a coding line -- the prose above a module's own docstring. It states no constraint the code
could contradict, documents no function, and sits where law or convention puts it, so no role
here can settle it. It is filtered out of your census. ! **An edit proposed on it anyway
becomes a `query`** -- a licence is a legal instrument and a shebang is how the file runs, and
both are the human's to change.

!! **A paragraph that holds nothing owes you no record.** Most of the census is empty -- a gap
between two lines of code (`interval`), or a declaration with no docstring (`undocumented`).
They are there to be CITED, not accounted for: an `add` says a constraint exists in code and
NOWHERE in prose, which is a finding about one of them.

!! **THE `@` NAMES A PLACE AGAINST THE CODE, and it is what you cite.** `@a5` is a
DECLARATION's documentation, `@c3` is prose BESIDE a line of code, and `@b3` is a GAP.
**Which line each one names is not something you can work out -- ask.**

!! **YOU CANNOT WORK OUT A CUE. ASK FOR IT.** The three series are counted by three
separate addressers, and no number in one tells you a number in another -- nor does a line's
position tell you either. Two of them lining up on the file in front of you is a coincidence of
that file, and it may change.

! **`@f0` IS THE FILE'S OWN MATTER** -- a licence header, a shebang, a coding line, and at the
other end an index, a glossary or a run of footnotes -- and not the gap above the first line of
code. It is filtered out of your census, and any edit proposed on it becomes a `query`.

!! **YOUR CENSUS CARRIES `a`, `b` AND `c`. THAT IS THE WHOLE SET YOU RULE ON.** The `f` series
is not a place you were asked about, so there is no instruction to reach on one.

! **YOU WILL STILL READ IT, AND THAT IS FINE.** Opening the file puts a licence header in front
of you, and you should use it the way you use any other context -- to understand what the file
is and who owns it. Roy, 2026-08-20: *"they will obviously read the matter ends when they look at
the file ... anytime you start to do something you load the whole document and then slice the
pieces that matter."* ! **What is ruled out is RULING on it**, not seeing it.

## You FILL a record; you do not write one

**You are handed one SHEET per file, and one slot per prose paragraph on it.** The sheet names
the file once, in `path`; each slot already carries the two things the tool knows -- the
`address` it is and the `anchor` it sits on -- and you set the five that are yours:

```json
{ "role": "block-context",
  "read_from": { "root": "/checkout/of/the/project", "revise": 0 },
  "sheets": [
    { "path": "redacted_pkg/billing/rates.py",
      "sha":  "9c1f0b7a4e2d6835aa10c4bb37f9e05d2c8471a6",
      "marks": [
        { "address": "b47",
          "anchor":  "def compute_rates(plan, period, *, clamp=True):",
          "instruction": "correct",
          "claim":   { "false": "twenty call sites want this",
                       "true":  "31 callers, all in tests/" },
          "reason":  "31 callers and every one is under tests/, so the count is stale",
          "sources": [ { "cite": "redacted_pkg/billing/rates.py:355",
                         "verbatim": "def compute_rates(plan, period, *, clamp=True):" },
                       { "cite": "redacted_pkg/export/invoice.py:88",
                         "verbatim": "rates = compute_rates(plan, period)" } ],
          "change":  "# Kept because 31 callers want this, all of them in tests/.\n# Narrowing it means re-deriving the clamp bounds." } ] } ] }
```

!! **THE THREE OUTER KEYS ARE NOT DECORATION, and the file you are handed already carries
them.** `role` is the role this copy was seeded for, `read_from` is the tree it was censused
from -- `revise` 0 is the original -- and `sha` is the bytes of the file your addresses were
taken from. **Edit in place and leave all four alone**; the checker refuses a copy that comes
back without `role` or `read_from`, and the `sha` is what proves nobody rewrote the file
underneath your marks.

!! **THIS EXAMPLE SHOWED A TWO-LEVEL `{"page", "records"}` UNTIL 2026-08-29, AND NOTHING
ACCEPTED IT.** The container is `sheets`, one per file; the file's own name is `path`, inside
its sheet; each sheet's entries are `marks`; and a mark names its `address`. `role`, `read_from`
and `sha` appeared nowhere in this file at all.

! **THE PLACE IS A CUE, NOT A FULL ADDRESS** -- `b47`, because the page above it already said
which file. You will still meet the full form `redacted_pkg:billing:rates.py@b47` in one place: a `move`
whose destination is in ANOTHER file, which no page of yours can name.

!! **YOU ARE TOLD WHERE, NOT WHAT. Open the file.** The record carries no copy of the paragraph's
prose, deliberately: handed the text you could produce a complete, admissible ruling without
ever reading the code, and nothing could tell that from real work. Your remit requires the
read. ! If you read the wrong lines, the sentence your `claim` quotes will not be in the paragraph
and the collator says so -- that error is caught, and the other one is invisible.

!! **WHAT YOU OPEN IS THE ORIGINAL** -- the file as it stood when THIS RUN began, not the first
version ever written. Nothing is written to disk before stage 7b, so the file you read at stage 4
IS the state your `address` and your `anchor` were taken from, and the state the collator checks your
`claim` against.

!! **YOU NEVER TRANSCRIBE THE PARAGRAPH.** `address` and `anchor` are the tool's. Leave them alone;
a mismatch there means the file was edited, not that you misquoted. ! The `anchor` is there to
be GREPPED -- it names the declaration the census resolved, and is empty where none was.

! **The file states what each constrained field allows** -- the seven instructions, the `claim` keys
each one owes, `query`'s three shapes, `add`'s two sides. Read `allowed` at the top of your file
rather than remembering them.

### The five fields you fill

| field | what it carries |
| --- | --- |
| `instruction` | one of the seven. ! `null` means you have not ruled yet, and a paragraph left `null` is a coverage gap |
| `claim` | an OBJECT whose keys are set by your instruction -- see the table below. It is the SPEC: what must change, and from what to what. ! **The key naming the EXISTING sentence is CHECKED against the census text for your paragraph** -- if it is not in the paragraph you are filling, the finding is on the wrong paragraph |
| `reason` | what you DERIVED from the source, and why the claim is wrong -- one statement |
| `sources` | a list of `{ "cite": "file:line", "verbatim": "the text AT it", "ran": "the command" }`, **one entry per place examined.** Every one is resolved and every `verbatim` must really be there. `ran` is owed only where the entry was settled by RUNNING something |
| `change` | the RESULT: **the updated paragraph, as RAW TEXT** -- not lines, not sentences. Indentation and comment markers exactly as they will sit on disk |

!! **`ran` -- A CLAIM SETTLED BY RUNNING SOMETHING MUST CARRY THE COMMAND.** `sources` records
WHAT you saw; `ran` records HOW you saw it. Add it to the `sources` entry it belongs to whenever
a `grep`, a test, or any other command is what settled that entry -- a claim settled by execution
and missing `ran` is incomplete.

!! **`claim` and `change` say the same edit twice, and that is deliberate.** `claim` is surgical,
so a checker can find the sentence you rule on and two roles ruling on one paragraph can be told
apart. `change` is the finished prose, so the task agent applies your text rather than
re-deriving it from a diff.

!! **THE TWO ARE CHECKED AGAINST EACH OTHER.** The difference between the paragraph and your `change`
is exactly what your edit does, and it must be the sentence your `claim` names. A record that
reasons about one sentence and rewrites another is refused, whichever of the two is right.

!! **ONE record's `change` makes ONE record's edit.** If you rule twice on one paragraph, write
TWO records with the same `address`, under the same sheet, each showing that paragraph with ITS OWN
change and no other. Do not
hand in the paragraph fully fixed twice: composing is the task agent's job, and it cannot compose
records that have already been merged.

!! **EXPECT YOUR OWN `change`S TO READ ODDLY ALONE, and hand them in anyway.** A paragraph needing
three coordinated edits gives three records, each showing the paragraph with one edit applied and
the other two still wrong -- so none reads as finished prose. **That is the format working, not
a demand for better writing.** Measured: a reviewer merged its three edits into one record
twice, trying to keep a paragraph readable, and was correctly refused both times.

!! **`sources`'s `verbatim` is the forcing function, and it is CHECKED.** The cited line is read
out of the file and your text must appear within three lines of it.

! **Cite every site you had to open.** A claim often needs two to settle -- the definition and
its callers -- and citing one means dropping the other, which is the cut-the-provenance failure
this system exists to catch. ! Each entry carries a LINE. A bare filename says you opened a file
and not what you read in it.

!! **A `source` MAY CITE ANY PLACE IN THE LIBRARY** -- every file in the project under review,
never this program's own tree. A citation is not limited to the paragraph's own file: where your
claim is that two places disagree, mark the one that is WRONG and cite the other as the evidence
that it is. A library citation is checked exactly like any other -- resolved, and its `verbatim`
confirmed. ! **The corollary is what keeps it honest**: if you cannot tell which side is wrong,
that is a `query`, not two `correct`s.

! **`reason` is DERIVED and is not checked verbatim** -- that is why it is a field of its own. A
count is not a line any file contains, so checking it against the code made every counted claim
inadmissible.

!! **A DEFECT YOU STATE IN `reason` REACHES NOBODY.** `reason` is read by no check, so a sentence
there that your `claim` does not name is a second finding with no record -- the gate checks the
claim it was given, passes, and the defect never reaches a work list. **If your reasoning names a
defect in a sentence your `claim` does not name, write a SECOND RECORD on that paragraph.** The collator
reports a phrase you quote from the paragraph that no claim names, so you will see it; write the
record instead.

### Filing an `add`

**An `add` cites the EMPTY PLACE the prose belongs in**, because its finding is that a
constraint holds in code and appears in NO prose. Empty places get no seeded slot -- they are
addressable, not accountable -- so **append a new record carrying that place's ADDRESS.** Read
it as being about that place, not about a neighbour.

!! **ASK FOR THE ADDRESS. DO NOT COUNT.** A row like `2-9  @b12..b19  48-58  no-prose  0L
8-intervals` hides eight numbered gaps, and counting them is how a citation lands one place off.
Two ways to ask:

!! **AN ANCHOR ANSWERS WITH SEVERAL PLACES, AND THAT IS NOT AN ERROR.** An anchor has MANY
addresses; an address has ONE anchor. Two identical statements in one file are two anchors spelled
alike -- `X=2  # initial` and `X=2  # reseting X` -- so asking for *"the `c` of `X=2`"* answers
with both and you **choose by ADDRESS**. Taking the first rules on the wrong statement.

! **The `b` series is worse on the same file: THREE gaps answer**, and they are drawn from two
different statements -- the gap above the first, the gap holding the comment between them (which
is anchored to the code BELOW it, the second statement), and the gap at the end of the file. The
tool prints how many answered; read that line.

! **An anchor is a LINE OF CODE, never a name**: ask with `def f():`, not with `f`. Its `a`, the
`b` above it and the `c` beside it all answer to that one spelling.

```bash
# by ANCHOR -- which place of this declaration: a its documentation,
# b the gap above its opening line, c the room beside it
python <skill>/scripts/comment-review.py addresser --census <FULL CENSUS> --anchor LINE --series a|b|c
```

!! **THE ANCHOR IS THE ONLY WAY TO ASK.** Asking by position -- "the paragraph above the
`def`" -- is right in Python and wrong in Rust, whose `///` sits before its `fn` where Python's
docstring sits after. The census parsed the file and knows which is which; a count does not.

! **There is no by-LINE lookup, and that is deliberate.** One existed until 2026-08-20 and was
dropped: the anchor IS the line of code, verbatim, so asking by anchor already asks by line --
and its other use, *where do I insert text*, is not a question a reviewer answers. You name the
PLACE; the galley puts the text in it and the compositor sets the page.

!! **A LINE NUMBER IS HOW YOU ASK; AN ADDRESS IS HOW YOU ANSWER.** A record naming a line as the
place a thing belongs is refused.

! **The SIDE is the address's to say, never yours.** An `a` is a declaration's documentation, a
`b` is a gap, a `c` is the room beside a line of code. **Which one a given number names is not
something you can work out** -- ask, as above. Your payload names WHAT is missing and WHICH
anchor.


!! **YOUR `change` REPLACES THE GAP, INCLUDING ITS BLANK LINES.** An interval is bounded by two
lines of CODE and the gap between them is whatever sits there -- nothing, or blank lines. The
edit is applied to the GAP, so a two-blank-line separation you do not write out is a separation
the file loses. **Write the blank lines you want kept**, as blank lines in the raw text, the
same way you would write them in the file.

!! **A `c` PLACE STARTS AT THE END OF THE CODE, so your `change` carries its own separator.**
A trailing comment is written from the point the statement stops -- `"  # why"`, with the two
spaces you want between them. Write `"# why"` and it lands hard against the code. This is the
same rule an interval follows: the text is file-ready, and whatever whitespace you want is
whitespace you write.

! **It is why a `margin` and the trailing comment that would replace it are ONE place.** Roy,
2026-08-19: *"c addresses start at the end of the code on the line."* Adding a comment where
there is none and rewording one that is there write to the same column, so the two instructions do
not need different rules.

!! **AN INTERMEDIATE COMMENT IS NOT IN THE CENSUS AT ALL** -- one with code on BOTH sides, as in
`int x = /* why */ 5;`. It is ignored for the same reason a Python type annotation is: it cannot
be verified the same way across codebases, and a line-length rule moves it. It is not a paragraph, it
has no address, and no instruction reaches it. **If one is wrong, it is a `code_concerns` line.**

### Code problems

`code_concerns` at the end of your file is a list of strings, one line each, no instruction. See
"The subject is the prose, not the program" below for what belongs there.

### The instructions, and what each one MUST carry

**An instruction rules on a SENTENCE, not on a paragraph.** A paragraph of six sentences can carry six
instructions, and one `clean` sentence must not launder the five around it.

An instruction is a recommendation the task agent will combine with the other roles' and synthesise
into one comment. It is only usable if it carries its payload, so **an instruction without its payload is
not a finding** -- *"correct the count"* hands the judgement back; *"replace X with Y"* is the
finding.

**Every shape below is `CLAIM`'s.** `CHANGE` is the same edit already made, written out with
its surrounding paragraph, and it is required for all of these but `clean` and `query` -- those two
propose no text, so there is nothing for the task agent to apply.

!! **THE TABLE BELOW IS GENERATED, FROM TWO SOURCES** -- the `claim` keys from `INSTRUCTIONS`
in `desk/mark.py` (`claim_all`, stated once per row), and the "what they carry" prose from
`docs/the-mark.md`'s "What each instruction owes" table, written by a human. Edit the row or
the spec, never this table; `uv run python scripts/render_brief.py --write` regenerates it, and
a test refuses a brief whose table disagrees with a fresh render, or where the two sources name
different instructions. ! It had drifted once already: the hand-written table taught an older
marker form under a JSON worked example, and ten of the eleven keys a reviewer must type
appeared nowhere here as keys -- which is what let `add`'s row go stale while the caption still
claimed the table was generated, when no such script existed anywhere in the tree.

<!-- BEGIN GENERATED: instruction table -- scripts/render_brief.py -->

| instruction | `claim` keys | what they carry |
| --- | --- | --- |
| `clean` | none | nothing. Name your role and stop -- `clean` proposes no text, so there is nothing for the apply step to apply |
| `query` | `shape`, `attempted`, `settles` | the SHAPE in these exact words, the check you ATTEMPTED, and what WOULD settle it. All three are checked as SHAPE and none as truth; the claim itself is checked by nothing, so the other three are all that stands behind the ruling |
| `drop` | `drop` | the sentence, verbatim, as it stands in the paragraph. ! It is CHECKED against the page, so a paraphrase is refused |
| `correct` | `false`, `true` | the false clause and the true one, and a `sources` entry carrying the line that settles it. ! The FALSE half is checked against the paragraph -- if it is not there, the finding is on the wrong one |
| `patch` | `from`, `to` | the sentence as it stands and the rewrite. ! `from` is checked against the paragraph. A `patch` needs no source: the claim is already true, and only its wording is at issue |
| `add` | `missing`, `anchor` | the text that is missing and the anchor NAMED IN BACKTICKS. ! The word "anchor" is not an anchor -- name the declaration. Which SIDE is the address's to say, never the claim's |
| `move` | `from`, `to` | where the prose sits now and where it belongs -- another line, another file, or out of the code entirely. ! These are PLACES, not text: the same two key names in `change` mean the resulting PARAGRAPHS |

<!-- END GENERATED -->

!! **`correct` keeps `false:`/`true:` where `patch` and `move` take `from:`/`to:`, and the pair
is not interchangeable.** `false:`/`true:` ASSERTS the sentence is wrong, and that assertion is
the whole difference between the
two instructions: a `patch` sentence is TRUE and merely reads badly. A neutral from/to on a
`correct` would erase the distinction the synthesis order rests on, and it is refused.

! **A `move`'s halves are PLACES, not text** -- from where it sits, to where it belongs. It is
the one edit whose `CLAIM` names no sentence, because the `PARAGRAPH` is what identifies the prose.

!! **A `move` changes TWO paragraphs, so its `CHANGE` carries BOTH -- and this is the only instruction
where `CHANGE` is not a single paragraph.** Write them labelled:

```text
CHANGE      to:   # the destination paragraph, as it reads once the prose arrives
                  # ...including the lines already there.
            from: # the origin paragraph, as it reads once the prose has left.
```

! **`to:` is required. `from:` may be omitted, and omitting it ASSERTS the WHOLE paragraph moved** --
that nothing is left behind to show. Nothing can tell a whole-paragraph move from a partial one by
inspection, so you say which by what you supply. ! If a sentence leaves and the rest stays,
`from:` is how the task agent learns what the remainder reads like; without it, the paragraph is
applied as if it emptied.

! These are `CLAIM`'s two words used again, and they mean something different here: in `CLAIM`
they are PLACES, in `CHANGE` they are the two resulting PARAGRAPHS. The field you are writing
decides which.

#### Does a TRUE sentence earn its place?

**Is it CHECKABLE?** confirmable from the code as it stands. **Is it NECESSARY?** would someone
changing this code make a **worse decision** without it? Those two questions decide:

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | it stays | **drop** -- it narrates what the code already says |
| **not checkable** | **move** -- real rationale, unverifiable in place | **drop** -- history |

! **This runs only on sentences you have already established are TRUE.** A false claim is not a
point on it -- it is `correct`. Read generally, *"truth is not one of the questions"* acquits a
falsehood. It applies to history that is TRUE-but-useless and nowhere else.

!! **A THIRD question the matrix cannot ask: is this the RULE, or ONE INSTANCE of it?** If a
reader can construct a case the sentence does not cover but the code still governs, the ALTITUDE
is wrong -- and that is a `patch`, not a `clean`.

**The matrix passes an over-specified sentence cleanly**, because it is confirmable and a reader
would decide worse without it. Both axes are satisfied and the sentence is still the wrong one.
! **A number can be WRONG; an over-specified sentence can only be NARROW**, and nothing else in
this pass measures narrowness.

! Measured 2026-08-17: one run caught *"Six call sites"* and *"Four kinds"* -- countable claims,
which the annotations surface -- and missed, in the same file, a sentence describing one
positional column by name where the rule it stands for governs every column after any insertion.
**Generalising it lost nothing**: the rule, the four functions it names, both test files, the
exception, its cause and its pointer all survived. ! A reader who inserts a DIFFERENT column is
governed by the code and unserved by the sentence, which is the test above.

#### `correct` and `patch` specific rules

! **`correct` and `patch` are not interchangeable.** `correct` says the claim is wrong;
`patch` says it is right and reads badly. The task agent applies every `correct` **before** any
`patch`, so mislabelling one as the other means a false claim gets its wording polished and
never gets checked -- that is laundering. If you are unsure which applies, you have not settled
the claim -- that is `query`.
! **A sentence that is not truthy cannot be `correct`ed**, because there is nothing to correct
it against -- it is `drop` or `query`.
*"The retry budget is 40"* is truthy, and false if the budget is 100. That is a `correct` mark.

*"this is robust"* is not truthy: no line, symbol or run settles it. ! Neither is *"there is no
definition of robust that can be checked in all circumstances"* -- **"all circumstances" is as
unbounded as "robust"**, so the sentence refusing the claim fails the same test.

#### `move` specific rules

! **One relocation instruction, and the DESTINATION is what varies.** A declaration ten lines
down, another file, or out of the code entirely -- all `move`, and which one goes in the
payload. Say what is wrong in `REASON`. **Only a destination outside the code can be
unavailable**, and your run context says whether it is; a relocation into tracked code is
always available.

!! **`to:` IS AN ADDRESS when the destination is on a page THIS RUN CUED, and it is
RESOLVED.** Ask for it the same way an `add` does -- `--anchor LINE --series a|b|c`. A
destination naming a LINE on such a page is refused, and so is an address the census does not
carry.

!! **A FILE THE RUN NEVER CUED IS CITED BY LINE, AND THAT IS NOT A LOOPHOLE.** The run
cues the files the change touched; everything else has no places at all, so there is no
address to ask for. A line number is refused INSIDE the run because this run's own edits shift
the lines below them -- a file the run does not edit has no such shift. ! So the rule is not
*never a line number*; it is **never a line number for a place this run can name properly.**

! **The destination may hold NO PROSE, and that is ordinary.** A paragraph can move to a gap with
no comment in it or a declaration with no docstring: those are places with addresses, not
absences. A destination OUTSIDE the code carries no address and is written as the path.

#### `clean` specific rules

**`clean` is scoped to YOU, and the other roles are looking at the same paragraph.** The task
agent combines every role's records into one comment or docstring.

**`clean` is a decision and is required -- it cannot be assumed or skipped past.**

! **Nothing is `clean` for being SHORT, TRUE, WELL WRITTEN, NEW, or under a `!`.** Each was
measured as an exemption reviewers invented for themselves. Truth least of all: a true claim
can be misplaced, unnecessary, or the surviving half of a paragraph whose other half was the
constraint -- and none of those is your role's question unless your role file says it is.

#### `query` specific rules

! **`query` is for a claim you could not settle -- not one you did not try to settle.** You are
still required to open the code that would settle it; on every other instruction your `SOURCES` proves
you did. `query` is what you emit when you did and it was still not enough.

!! **Three shapes reach it, and your `CLAIM` must NAME which one -- in these exact words.** They
are keyed on WHO RESOLVES IT, not on where the missing evidence lives. The three are findings
rather than admissions, and they route differently: the first says which scope owns the
paragraph, the other two are work that reaches the author. Nothing downstream can tell them apart
if you do not say which:

- **outside-my-role** -- deferred to another agent's problem.
- **unable-to-determine** -- *"don't know why but maybe another agent figured it out."*
- **human-review-necessary** -- *"genuinely contradictory statements and/or code and only system
  level intent might disambiguate it."*

! **A claim you could not settle and marked `clean` is worse than the same claim marked
`query`.** `clean` certifies; `query` asks.

! **A `query` requires `SOURCES`, by construction** -- this is where you
looked to try to find the answer. These are the statements in the code that make it
ambiguous or the location not yours to determine. **All three shapes carry them**, including
`outside-my-role`: the paragraph is real and in the checkout on every one of them, so there is
always a line to quote.

!! **`outside-my-role` is a FINDING, so you have to show it is not yours.** It is the shape a
reviewer reaches for when it has nothing to say, and it is the one that costs the most when
it is wrong -- the paragraph leaves your report certified by nobody. So quote the line that fixes
the paragraph's SUBJECT, and say in `REASON` what about that subject your remit does not reach,
in the words your own role file uses for its remit. **Never name another role**; you do not
know what the others were asked. *"Not mine"* is an admission. *"Its subject is the loop body,
and my remit is what the module as a whole announces"* is a finding.

## Check the CLAIM, not the CITATION

Resolving a path or a symbol is quick and *feels* like verification. Resolving a claim **is**
the verification. A resolved citation is not a verified one -- open the target and read it, or
the instruction is `query`.

! **Cite by SYMBOL or PATH in the text you write -- never by line number.** A symbol survives a
refactor; a line number rots with no visible symptom. Measured: three rotted line-number
citations in one pass, one of which had drifted onto a blank line.

! **An unparseable citation is a finding even when it resolves**, and its instruction is `correct`,
never `drop`. A brace expansion, a bare filename, a wrong-case prefix: rewrite it into the
checkable form. Unverifiable and verified-correct look identical, and the unverifiable form is
the one that persists -- a wrong citation gets fixed next run, an illegible one accumulates and
its illegibility reads as confidence. Measured on the repair side too: a live pointer to a real
enforcing test was DELETED on the strength of a false dangling report.

## The subject is the prose, not the program

Every instruction is an instruction on a comment. Code problems get **one line each** in a separate
`CODE CONCERNS` section at the end, with no instruction. The findings this line exists for *look*
like code findings and are not:

| COMMENT finding                                     | CODE finding                          |
| --------------------------------------------------- | ------------------------------------- |
| the comment says it reads one field; it reads three | it should not read three fields       |
| the comment names a symbol that no longer exists    | the symbol should be restored         |
| the comment claims callers `grep` cannot find       | the function is dead, delete it       |
| the comment forbids a literal the file hardcodes    | replace the literal with the constant |
| the same rule is restated at a dozen sites          | the rule needs an owning type         |
| the comments indicate multiple business cases       | the function needs to be split        |

! **This is not "do not investigate."** Resolving a claim against its code is the core work:
reading an assertion to see whether it *can* fail, grepping a forbidden literal, counting call
sites. Out of scope is ruling on what the code **should be**.

! **Ruling on the code spends this review on what the code's own tests settle**, and four
agreeing reviewers once reported a file "cannot compile" over valid syntax. A code problem has
a place: `CODE CONCERNS`, one line, no instruction.

### One paragraph, two placements -- report yours

REMITS OVERLAP BY DESIGN: the roles read the same code bottom-up and top-down, so two roles
can reach the same or different decisions per sentence. Report what your role sees and say in
`REASON` what is wrong. Which instruction wins is the task agent's ruling later.
