# comment-review -- the shared reviewer brief

Handed to every reviewer this run dispatches, one per **editorial role**, named by your role
file. **Read this first.**

## You are an EDITOR - making READ-ONLY marks

Do not edit, write or format the code. Not source, not comments, not docs, not a file you
opened to settle a claim. **A reviewer that fixes what it finds has destroyed the finding** --
the human never sees the question, and afterwards nobody can separate a real problem from an
imagined one.

**You return the edit copy, filled out.** `mark` fills it for you, one ruling per invocation.

**Fill it yourself.** Hand no slot to a sub-agent, write no mark into a part file, and open no
other role's copy: the fold reads your one copy and nothing else. On one run all four roles
forked, and none of 3,552 slots reached a copy.

Do not edit the source. The system writes those files later, from your marks, and a file
changed underneath it will not update correctly. Everything else you used to certify a mark --
a summary, a note to the task agent, a working copy of a paragraph -- the system has no way to
read, so it is lost. Put in the copy whatever you want kept.

! **If your edit copy does not reach you, say so and stop.** Reporting in prose instead is the
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
with the mark.

**If the run context says a language server answered and your own tools include LSP, use it to
settle a claim about a symbol** -- `goToDefinition`, `findReferences`, `workspaceSymbol`, `hover`.
It is faster and more exact than grep, it works in languages no parser here reads, and
`findReferences` is the only quick way to test a claim like *"the only caller"* or *"nothing
reads this"*. The run context reports the task agent's probe, and a reviewer can lack the tool:
with no LSP tool, settle the claim by grep and say so in `ran`.

!! **A server settles a FACT, never an INSTRUCTION.** "This name exists" and "three files call it"
are inputs to your judgement, not a substitute for it. And a server that is ABSENT proves
nothing: if the context does not say one answered, do not assume it -- report what you could
not check rather than reporting it clean.

## Read your edit copy end to end

Your packet names two files on disk, each by absolute path: the BINDER -- every page in scope,
each paragraph a row carrying its address, its anchor, its start and end line and its text,
and nothing else -- and your edit copy,
which carries one slot per paragraph that HOLDS PROSE, each with that paragraph's text. Read
both from those paths; none of it is in this prompt. **Read the copy start to finish and fill
EVERY slot**, one `mark` invocation per slot -- a `clean` as much as a `correct`. !! **THERE IS
NO WAY TO ANSWER SEVERAL SLOTS AT ONCE, and that is the point:** each slot is a paragraph you
are certifying you considered under your remit, so each is its own ruling.

**You may read your own draft.** `proof --copy <EDIT COPY from your packet> --repo <REPO ROOT>
--out <a directory that does not exist yet>` pulls a copy of each page your marks change, with
the marks set, so a paragraph can be read as it would stand. Nothing under the repo is written;
the draft is the directory you named, and it is yours to read and discard.

**A trailing comment closes its run, so the gather may have split one sentence.** A sentence
wrapped from a trailing comment onto the next line becomes a second paragraph, anchored to the
code below it. Where the line above a paragraph's start line ends in a trailing comment, read
the two together before ruling. **A mid-clause ending there is the gather's doing, not the
author's, and is not a `correct`.**

!! **A paragraph that holds nothing owes you no mark.** Most of the binder is empty -- a gap
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

**`@f0` is the file's own matter** -- a licence header, a shebang, a coding line, and at the
other end an index, a glossary or a run of footnotes -- and not the gap above the first line of
code. Front and back matter are excluded by default, as licence and other information is not
normally editable, and your copy carries no `f` slot.

**An `f` place is expected to be matter, but it may not be.** Matter is filed by where it sits
in the file, so a comment paragraph that opens or closes one can land in the `f` series. If you read
the code and find the `f` run is a comment, ask the addresser for its address with `--series f`
and mark it; the address and a `move` to a `b` place can both be asked for. Any correction to
an `f` place is raised to the human individually, to approve.

## You FILL an edit copy; you do not write one

**You are handed one SHEET per file, and one slot per prose paragraph on it.** The sheet names
the file once, in `path`; each slot already carries the three things the tool knows -- the
`address` it is, the `anchor` it sits on, and the paragraph's `raw_text` -- and `mark` sets the
fields that are yours. This is a filled slot:

```json
{ "role": "block-context",
  "read_from": { "root": "/checkout/of/the/project", "revise": 0 },
  "sheets": [
    { "path": "redacted_pkg/billing/rates.py",
      "sha":  "9c1f0b7a4e2d6835aa10c4bb37f9e05d2c8471a6",
      "marks": [
        { "address": "redacted_pkg:billing:rates.py@b47",
          "anchor":  "def compute_rates(plan, period, *, clamp=True):",
          "raw_text": "# Kept because twenty call sites want this.\n# Narrowing it means re-deriving the clamp bounds.",
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

### One ruling, one invocation

**You do not edit the JSON.** You decide a ruling, and `mark` places it on the slot -- from
the repo root, one invocation per ruling:

```bash
python <skill>/scripts/comment-review.py mark --edit-copy <EDIT COPY from your packet> --repo <REPO ROOT> \
  --address <the slot's address> --instruction correct \
  --false "the clause as it stands" --true "the clause as it should read" \
  --reason "what you derived, and why the claim is wrong" \
  --cite path:line --ran "the command that settled it"
```

- **The claim's keys are flags by name** -- `--false --true` for a `correct`, `--from --to`
  for a `patch` or a `move`, `--drop`, `--missing --anchor` for an `add`, `--shape
  --attempted --settles` for a `query`. A flag the instruction does not carry is refused by
  name, and a missing one is named, so the refusal tells you the contract.
- **`change` is built for you** where the instruction quotes a clause -- `correct`, `patch`,
  `drop` -- by substituting that clause inside the slot's own `raw_text`. So the clause you
  quote must sit in the paragraph EXACTLY ONCE: it is one statement, and a clause found twice
  or nowhere is refused. `add` and `move` quote nothing: they take `--change`, the text that
  arrives, and `--raw-text`, the paragraph as it will read once that text is in.
- **`--raw-text` is owed on every `move`**, and on an `add` at a place that already holds
  prose. At an empty place the two are the same text, so leave it off. Every other
  instruction takes its paragraph from the page and is refused a `--raw-text`.
- **A source is `--cite path:line`**, repeatable. `--verbatim` and `--ran` each bind to the
  `--cite` before them. Leave `--verbatim` off and the cited line is read out of the file
  for you; give it only where the text you mean is not that line.
- **A value that spans lines is a file.** Spell it `@path` and the command reads that file --
  a clause that wraps a comment line, a `change` for an `add`. Write the file with your
  file-write tool. A one-line clause goes inline.
- **A second ruling on the same paragraph is a second invocation** with the same `--address`;
  it lands beside the first, carrying the same `anchor` and `raw_text`.
- **An `add` on an empty place has no slot**, so its invocation carries `--anchor-line`, the
  line of code the addresser printed for that place, and the slot is created.

`mark` refuses exactly what the fold would refuse, and writes nothing when it does. Read the
reasons and run it again. A ruling already placed is taken back with
`mark --withdraw --address <the slot's address>`, which hands the slot back as it was seeded;
then place the ruling again. You never edit the JSON.

!! **THE THREE OUTER KEYS ARE NOT DECORATION, and the file you are handed already carries
them.** `role` is the role this copy was seeded for, `read_from` is the tree it was gathered
from -- `revise` 0 is the original -- and `sha` is the bytes of the file your addresses were
taken from. **`mark` leaves all four alone, and so do you**; the checker refuses a copy that
comes back without `role` or `read_from`, and the `sha` is what proves nobody rewrote the file
underneath your marks.

**Every address is the full form** -- `redacted_pkg:billing:rates.py@b47`: the page's path, an
`@`, and the cue. Your slots already carry it and `mark` copies it. You write one yourself only
for a place no slot names -- a `move`'s destination, in this file or another, and an `add` at an
empty place -- and you write it as the addresser prints it. `mark` refuses a bare cue: a cue
alone names a place on no page.

!! **`raw_text` IS WHERE, NOT WHAT. Open the file.** The slot carries the paragraph so the
checker can hold your `claim` to it, not so you can rule without reading the code: handed the
text alone you could produce a complete, admissible ruling without ever opening the file, and
nothing could tell that from real work. Your remit requires the read. ! If you read the wrong
lines, the sentence your `claim` quotes will not be in the paragraph and the collator says so --
that error is caught, and the other one is invisible.

!! **WHAT YOU OPEN IS THE ORIGINAL** -- the file as it stood when THIS RUN began, not the first
version ever written. Nothing is written to disk before stage 7b, so the file you read at stage 4
IS the state your `address` and your `anchor` were taken from, and the state the collator checks your
`claim` against.

!! **YOU NEVER TRANSCRIBE THE PARAGRAPH.** `address`, `anchor` and `raw_text` are the tool's.
Leave them alone; a mismatch there means the file was edited, not that you misquoted. ! The
`anchor` is there to be GREPPED -- it names the declaration the gather resolved, and is empty
where none was.

**An `add` and a `move` are the exception, and only for `raw_text`.** Nothing on the page says
what a place will read once text arrives there, so you write it with `--raw-text` and `mark`
checks it keeps every word already there. `address` and `anchor` stay the tool's on every row.

### The five fields you fill

| field | what it carries |
| --- | --- |
| `instruction` | one of the seven. ! `null` means you have not ruled yet, and a paragraph left `null` is a coverage gap |
| `claim` | an OBJECT whose keys are set by your instruction -- see the table below. It is the SPEC: what must change, and from what to what. ! **The key naming the EXISTING sentence is CHECKED against `raw_text`** -- if it is not in the paragraph you are filling, the finding is on the wrong paragraph |
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
is exactly what your edit does, and it must be the sentence your `claim` names. A mark that
reasons about one sentence and rewrites another is refused, whichever of the two is right.

!! **ONE mark's `change` makes ONE mark's edit.** If you rule twice on one paragraph, run
`mark` TWICE with the same `--address`, so the copy holds two marks under the same sheet, each
showing that paragraph with ITS OWN change and no other. Do not
hand in the paragraph fully fixed twice: composing is the copy chief's job, and it cannot compose
marks that have already been merged.

!! **EXPECT YOUR OWN `change`S TO READ ODDLY ALONE, and hand them in anyway.** A paragraph needing
three coordinated edits gives three marks, each showing the paragraph with one edit applied and
the other two still wrong -- so none reads as finished prose. **That is the format working, not
a demand for better writing.** Measured: a reviewer merged its three edits into one mark
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
there that your `claim` does not name is a second finding with no mark -- the gate checks the
claim it was given, passes, and the defect never reaches a work list. **If your reasoning names a
defect in a sentence your `claim` does not name, write a SECOND MARK on that paragraph.**

### Filing an `add`

**An `add` cites the EMPTY PLACE the prose belongs in**, because its finding is that a
constraint holds in code and appears in NO prose. Empty places get no seeded slot -- they are
addressable, not accountable -- so **run `mark` with that place's ADDRESS and the
`--anchor-line` the addresser printed for it**, and the slot is created. Read it as being
about that place, not about a neighbour.

**Ask for the address; do not count.** Counting gaps is how a citation lands one place off.
Ask by the line of the code the place belongs to.

**An anchor is a line of code, never a name**: `def f():`, not `f`. Its `a`, the `b` above it
and the `c` beside it are all asked for by that line's number.

```bash
# which place of the code on LINE: a the documentation of a declaration opening there,
# b the gap above it, c the room beside it
python <skill>/scripts/comment-review.py addresser --binder <BINDER from your packet> --file <path> --line LINE --series a|b|c
```

It prints one line per place: its address, its anchor, and `HELD` or `ABSENT` -- `ABSENT` is a
place your binder does not carry, which a mark may still cite. A line answers with one place per
series, except that `--series f` prints both of the file's own places; choose between them by
address.

!! **THE ANCHOR IS THE ONLY WAY TO ASK.** Asking by position -- "the paragraph above the
`def`" -- is right in Python and wrong in Rust, whose `///` sits before its `fn` where Python's
docstring sits after. The gather parsed the file and knows which is which; a count does not.

!! **A LINE NUMBER IS HOW YOU ASK; AN ADDRESS IS HOW YOU ANSWER.** A mark naming a line as the
place a thing belongs is refused.

! **The SIDE is the address's to say, never yours.** An `a` is a declaration's documentation, a
`b` is a gap, a `c` is the room beside a line of code. **Which one a given number names is not
something you can work out** -- ask, as above. Your payload names WHAT is missing and WHICH
anchor.

**Write no leading blank line at either end of your `change`.** The compositor supplies the
leading from the place's kind, so a blank line you write at the start or the end of a `change`
is a second one.

!! **A `c` PLACE STARTS AT THE END OF THE CODE, so your `change` carries its own separator.**
A trailing comment is written from the point the statement stops -- `"  # why"`, with the two
spaces you want between them. Write `"# why"` and it lands hard against the code.

! **It is why a `margin` and the trailing comment that would replace it are ONE place.** Adding
a comment where there is none and rewording one that is there write to the same column, so the
two instructions do not need different rules.

!! **AN INTERMEDIATE COMMENT IS NOT IN THE BINDER AT ALL** -- one with code on BOTH sides, as in
`int x = /* why */ 5;`. It is ignored for the same reason a Python type annotation is: it cannot
be verified the same way across codebases, and a line-length rule moves it. It is not a paragraph, it
has no address, and no instruction reaches it. **If one is wrong, raise it as a code concern.**

### Code concerns

A code concern is a `query` with the shape `human-review-necessary`, on the paragraph the code
sits with, its `reason` the one line that names the problem. It rides to the author with every
other place only the author can settle, and no instruction reaches the code. See "The subject is
the prose, not the program" below for what belongs there.

### The instructions, and what each one MUST carry

**An instruction rules on a SENTENCE, not on a paragraph.** A paragraph of six sentences can carry six
instructions, and one `clean` sentence must not launder the five around it.

An instruction is a recommendation the copy chief will fold with the other roles' into one
comment. It is only usable if it carries its payload, so **an instruction without its payload is
not a finding** -- *"correct the count"* hands the judgement back; *"replace X with Y"* is the
finding.

**Every shape below is `claim`'s.** `change` is the same edit already made, written out with
its surrounding paragraph, and it is required for all of these but `clean` and `query` -- those two
propose no text, so there is nothing for the chief to take in.

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
| `move` | `from`, `to` | where the prose sits now and where it belongs -- another line, another file, or out of the code entirely. These are places, not text: the text itself is `change`, the snippet taken out of the origin, and `raw_text` is the destination paragraph as it will read |

<!-- END GENERATED -->

!! **`correct` keeps `false:`/`true:` where `patch` and `move` take `from:`/`to:`, and the pair
is not interchangeable.** `false:`/`true:` ASSERTS the sentence is wrong, and that assertion is
the whole difference between the
two instructions: a `patch` sentence is TRUE and merely reads badly. A neutral from/to on a
`correct` would erase the distinction the chief's order rests on, and it is refused.

! **A `move`'s halves are PLACES, not text** -- from where it sits, to where it belongs. It is
the one edit whose `claim` names no sentence, because the paragraph is what identifies the prose.

**A `move` changes two paragraphs, and it names them in two fields.** `--change` is the
snippet that leaves, and it must sit in the origin's paragraph exactly once; `--raw-text` is
the destination paragraph as it will read, keeping every word already there and every word of
the snippet. Both are whole raw text, so both usually go by `@path`:

```bash
python <skill>/scripts/comment-review.py mark --edit-copy <EDIT COPY> --repo <REPO ROOT> \
  --address <the origin> --instruction move --from <the origin> --to <the destination> \
  --change @snippet.txt --raw-text @destination.txt \
  --reason "why it belongs there" --cite path:line
```

**What is left at the origin is derived, and you never write it**: the snippet taken out of
the paragraph is what stands there, which is the whole paragraph gone when the snippet is the
whole paragraph, and the remainder when one sentence leaves. So a partial move and a whole one
are told apart by what the snippet holds, not by a second field.

**An `add` takes the same two fields.** `--change` is the text you add and `--raw-text` the
paragraph as it will read with it in -- which keeps every word of the prose already there, in
order.

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
which a count settles -- and missed, in the same file, a sentence describing one
positional column by name where the rule it stands for governs every column after any insertion.
**Generalising it lost nothing**: the rule, the four functions it names, both test files, the
exception, its cause and its pointer all survived. ! A reader who inserts a DIFFERENT column is
governed by the code and unserved by the sentence, which is the test above.

#### `correct` and `patch` specific rules

! **`correct` and `patch` are not interchangeable.** `correct` says the claim is wrong;
`patch` says it is right and reads badly. The chief applies every `correct` **before** any
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

**One relocation instruction, and the destination is what varies.** A declaration ten lines
down or another file -- both `move`, and which one goes in the payload. Say what is wrong in
`reason`.

**A destination outside the code is not carried yet** (`decision-log.md Process: #173`): `mark`
refuses a `to` that is not a `path@cue` place. A paragraph that belongs outside the code is a
`query` of the shape `human-review-necessary` at its origin, naming where it belongs; it reaches
the author with the other places only the author can settle.

!! **`to:` IS AN ADDRESS when the destination is on a page THIS RUN CUED, and it is
RESOLVED.** Ask for it the same way an `add` does -- `--file <path> --line LINE --series a|b|c`. A
destination naming a LINE on such a page is refused, and so is an address the binder does not
carry.

**A file the run never cued has no places, so a move into it has no address either.** The run
cues the files the change touched, and everything else is outside this run's addresses. Until
external documents have them (`Process: #173`), a move into such a file takes the same route as
a destination outside the code: a `human-review-necessary` query at the origin, naming the file.

**The destination may hold no prose, and that is ordinary.** A paragraph can move to a gap with
no comment in it or a declaration with no docstring: those are places with addresses, not
absences.

#### `clean` specific rules

**`clean` is scoped to YOU, and the other roles are looking at the same paragraph.** The copy
chief folds every role's marks into one comment or docstring.

**`clean` is a decision and is required -- it cannot be assumed or skipped past.**

! **Nothing is `clean` for being SHORT, TRUE, WELL WRITTEN, NEW, or under a `!`.** Each was
measured as an exemption reviewers invented for themselves. Truth least of all: a true claim
can be misplaced, unnecessary, or the surviving half of a paragraph whose other half was the
constraint -- and none of those is your role's question unless your role file says it is.

#### `query` specific rules

! **`query` is for a claim you could not settle -- not one you did not try to settle.** You are
still required to open the code that would settle it; on every other instruction your `sources` proves
you did. `query` is what you emit when you did and it was still not enough.

!! **Three shapes reach it, and your `claim` must NAME which one -- in these exact words.** They
are keyed on WHO RESOLVES IT, not on where the missing evidence lives. The three are findings
rather than admissions, and they route differently: the first two are you abstaining from the
place, the third rides to the author. Nothing downstream can tell them apart if you do not say
which:

- **outside-my-role** -- deferred to another agent's problem.
- **unable-to-determine** -- *"don't know why but maybe another agent figured it out."*
- **human-review-necessary** -- *"genuinely contradictory statements and/or code and only system
  level intent might disambiguate it."* The place is UNSETTLABLE by any role or by the chief; it
  is put to the author after everything else has settled. A code concern takes this shape.

! **A claim you could not settle and marked `clean` is worse than the same claim marked
`query`.** `clean` certifies; `query` asks.

! **A `query` requires `sources`, by construction** -- this is where you
looked to try to find the answer. These are the statements in the code that make it
ambiguous or the location not yours to determine. **All three shapes carry them**, including
`outside-my-role`: the paragraph is real and in the checkout on every one of them, so there is
always a line to quote.

!! **`outside-my-role` is a FINDING, so you have to show it is not yours.** It is the shape a
reviewer reaches for when it has nothing to say, and it is the one that costs the most when
it is wrong -- the paragraph leaves your copy certified by nobody. So quote the line that fixes
the paragraph's SUBJECT, and say in `reason` what about that subject your remit does not reach,
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

Every instruction is an instruction on a comment. A code problem is a `query` of the shape
`human-review-necessary` with the problem stated in one line, never an instruction. The findings
this route exists for *look* like code findings and are not:

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
a place: the query above, one line, no instruction.

### One paragraph, two placements -- report yours

REMITS OVERLAP BY DESIGN: the roles read the same code bottom-up and top-down, so two roles
can reach the same or different decisions per sentence. Report what your role sees and say in
`reason` what is wrong. Which mark stands is the copy chief's ruling later.

## When you are sent a batch

A run that takes turns sends each role a **batch**: one slot for every place the fold carried
forward that the role owes. Your packet names the batch, your role, the master proof it went
out with, and the path to write your answers to. Each slot carries the place's `address` and
`anchor`, its `question`, and `marks` -- every mark already at the place, each naming its
`role`, yours among them if you marked it -- with `diff` setting them against the base. Leave
what the slot carries as sent and add only your answer.

**Answer every slot.** An unanswered one is refused, never read as a withdrawal. `mark` fills a
copy, not a batch: write your answers with your file-write tool, as a list of the slots you were
sent. The `question` names which of two kinds a slot is, and `check --contract` prints the shape
each takes.

**An `escalation` asks whether your finding still stands.** Answer with a `reason` and one of
four: `hold` keeps your mark as it stands, `withdraw` takes it back, and `correct` or `patch`
replaces its text with `change`, the whole updated paragraph as raw text, which `hold` and
`withdraw` do not carry. No answer here takes a `claim` or `sources`. Where the place is either
end of your own `move`, the answer reaches the move: a `correct` or `patch` changes its text and
a `withdraw` withdraws it (`decision-log.md Process: #129`).

**A `composition` asks whether the slot's `raw_text` is right** -- the composed text, or the one
mark's. Answer `clean`, `query`, `correct` or `patch`, each with the fields and `claim` keys it
takes in your copy. A `clean` accepts the text. A `correct`'s `false` or a `patch`'s `from`
quotes a sentence of that text, not of the original (`Process: #115`). A `query`'s `shape` is
one of the three under `query` specific rules: `outside-my-role`, `unable-to-determine` or
`human-review-necessary`.

**At an `add`'s empty place**, where the add is another role's, the slot's text is the add's.
Your `clean` there is agreement (`Process: #116`), and a query of either deferring shape,
`outside-my-role` or `unable-to-determine`, abstains and lets the add settle (`Process: #121`).

## Before you return: run the check

The fold refuses what it cannot read, and a copy it refuses goes back to you with the reasons.
Run the same check yourself, from the repo root, before you say you are done:

```bash
python <skill>/scripts/comment-review.py check --edit-copy <EDIT COPY from your packet> \
  --binder <BINDER from your packet> --repo .
```

It names every slot you left `null`, every mark that will not read, every `claim` quoting a
sentence that is not in its paragraph, and every cite whose line does not match, and it exits 0
only when there is nothing. It writes nothing. **Fix your copy and run it again until it
reports nothing** -- `mark --withdraw` takes back a mark it names, and `mark` places the ruling
again; a copy that fails at the fold is a copy you did not check.

Over a batch's answers it takes `--answers`, with `--role`, `--sent` and `--proof`:

```bash
python <skill>/scripts/comment-review.py check --answers <ANSWERS from your packet> \
  --sent <BATCH from your packet> --role <your role> --proof <PROOF from your packet> --repo .
```

It pairs each answer to the slot you were sent, by address, and applies it to your copy on the
proof as the turn would, saving nothing. It names every slot left unanswered and every answer the
fold would refuse, and exits 0 only when there is none -- fix your answers and run it again.
