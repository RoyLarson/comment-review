---
name: comment-review
description: Review the comments and docstrings in the files a change touched, across four angles -- locality, currency, functionality, module coherence -- using four parallel subagents, and return each finding with a proposed verdict (drop / move / compact / keep) for the human to rule on. Use this whenever comments or documentation are the subject: after finishing a task that added or edited commentary, when a file's comments have drifted from what the code now does, when someone says a comment is too long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether a module still reads as one module. Trigger on phrasings that never say "comment review" -- "these comments are getting out of hand", "does this docstring still match", "is this comment still true", "clean up the narration in this file", "why does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews code structure and applies its fixes) and NOT /code-review (which hunts correctness bugs) -- this one ONLY EVER PROPOSES and never edits anything, not code and not even the comments it rules on, because an edit applied is a verdict the human never got to rule on. Run it even when the request sounds like an instruction to cut ("cap these", "clean this up"): the deliverable is still the verdict list, and applying is a separate step. It is explicitly not a reviewer's job to judge whether the code works: code concerns get raised in a line and left, while every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` -> 4 reviewers in parallel -> a verdict per finding -> you decide -> apply.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you
return is a verdict on a comment. A reviewer who starts debugging has changed the
question, and the report stops being about the thing it was asked about.

You will still notice code problems -- you cannot read a comment against its code
without forming an opinion of the code. Say so, in a clearly separated section,
in one line each, and move on. **Raise a concern, do not open an investigation**,
and never let a code finding acquire a `drop`/`move`/`compact`/`keep` verdict:
those four words apply only to prose.

The distinction is sharper than it sounds, because the best findings this skill
produces look like code findings and are not:

| This is a COMMENT finding | This is a CODE finding |
|---|---|
| the comment says the function reads one field; it reads three | the function should not read three fields |
| the comment names a symbol that no longer exists | the symbol should be restored |
| the comment claims callers that `grep` cannot find | the function is dead and should be deleted |
| the same rule is restated at a dozen sites | the rule needs an owning type |

Every row's left cell is checkable against the file and is yours to rule on. Every
right cell is a design change belonging to `/simplify`, `/code-review`, or the lane
owner -- **name it and leave it.**

! **A reviewer straying into correctness is where this skill's worst output comes
from, measured.** In two separate eval rounds a reviewer read `except ValueError,
TypeError:` and reported the file "cannot compile" -- a claim about the *program*,
volunteered while reviewing *prose*, and wrong (PEP 758 permits it in Python 3.14).
Once, four agreeing reviewers shipped it. The rule that catches this is the same
one that keeps the report on topic: if the claim is about whether the code runs,
it is not your finding, and if you make it anyway you owe it a `python -c` or an
`ast.parse` before it leaves your hands.

Comments rot differently from code. Code that stops being true usually breaks a
test; a comment that stops being true just sits there, and the next reader
believes it. Worse, comments accrete: nobody deletes the paragraph explaining a
decision, so the paragraph outlives the decision, and the file grows until the
code is spaced too far apart to hold in view. That is the failure this skill
exists to catch, and it is why the review is not scoped to the diff.

## Arguments

- **`cap`** -- an integer, optional. The maximum lines a single comment block may
  run. Pass it to every reviewer. **This skill has no cap of its own** and must
  not invent one: a good cap comes from how much code the human needs on screen
  either side of a comment, which is a fact about their editor and their
  reading, not about the language. If no cap is given, review by judgement and
  **report the longest block found** -- the number is then visible without having
  been asserted.
- **`target`** -- a path, optional. Defaults to the files in the diff (below).

## Phase 0 -- Scope: whole files, not the diff

Run `git diff --name-only @{upstream}...HEAD` (or `main...HEAD`, or `HEAD~1`).
If the tree is dirty or the range is empty, add `git diff --name-only HEAD`.
That gives you a **list of files**.

Now review **all of the comments and docstrings in those files**, not just the
changed lines. This is the one place this skill deliberately departs from
`/simplify`. Comment debt is cumulative and mostly pre-existing: the 54-line
block that has sat above a four-line expression for months is the finding worth
having, and a diff-scoped reviewer would never see it. The diff tells you which
files are live in the human's head right now; it should not bound what gets read
inside them.

Skip files with no commentary worth reviewing (generated code, data tables). Say
which you skipped.

## Phase 1 -- Four reviewers, in parallel

Launch **four subagents in a single message** so they run concurrently. Give
each: the file list, the `cap` if one was given, and one angle. Each returns
findings with `file`, `line`, a one-line `summary`, and the concrete cost.

! **Reviewers are READ-ONLY. Tell them so explicitly in their prompt.** They
read, grep, and report; they never edit. Nothing in this skill writes to a source
file at any phase -- see Phase 3. Two reasons, and the second is the one that
bites: four agents editing one file concurrently is a race whose loser's edits
vanish silently, and a reviewer that fixes what it finds has destroyed the
finding -- the human never gets to rule on it, and afterwards nobody can tell a
real problem from an imagined one.

**If the repo publishes its own cap, use it and say where you got it.** A cap
sitting in a guard (a lint config, a hygiene test) is a decision the team already
made, and it beats both the argument and your judgement. Read the guard for how
it *measures*, too, not just its number -- the counting rule is where these differ,
and matching the number while counting differently produces a file that claims to
comply and does not.

The angles are deliberately different lenses on the same text, so overlap
between them is a signal (a finding all four report is almost always real), not
waste.

### Locality -- does this comment belong to the line it sits on?

A comment is a claim about the code beside it. Flag one that is really about
something else: a rule stated at the top of a class that actually constrains two
integer literals 200 lines down, a note about the schedule that will silently
stop being true the moment the schedule moves, a paragraph that describes the
module's history rather than the branch it precedes.

**A comment points at the code it is attached to** -- DOWN for a block on its own
lines, AT the declaration for a trailing one. A field comment
(`retries: int  # 0 disables the backoff entirely`) is annotating the thing on
its own line and is exactly where it belongs; do not read it as facing the wrong
way just because it sits after a statement.

The finding is a comment that talks about something **else**: a block whose
later half turns back to narrate what came before, a note that describes a
function further down the file, a paragraph at the top of a class that really
constrains two literals two hundred lines away. Those are usually the seam where
two unrelated notes were merged, or where one was split and half of it ended up
facing backwards. Read the fragment against the statement it touches and ask
what it is *about*, not where it sits.

The second test, for anything that survives the first: **if this code changed,
would the comment become wrong -- and would anyone notice?** A comment that would
quietly survive a change to the code it claims to describe is not local to it.

Also flag the inverse: a line carrying a non-obvious constraint with no comment
at all, where getting it wrong is silent. Absence is a locality finding too.

### Currency -- does this describe the program as it is now?

Git holds what the code used to be and why it changed. A comment that narrates
its own history is doing git's job badly, and it costs the reader every time.

Flag: dated rulings, review-round labels ("fix round 2", "finding B4"), "this
used to...", "X was changed to Y", "before the fix", and -- the sharpest form --
**obituaries**: a comment naming a symbol, file, test, or flag that no longer
exists anywhere. Those are worse than noise, because a reader greps for the name
and finds nothing, which reads as *their* mistake rather than the comment's.

Obituaries are objectively checkable, so **check them** rather than eyeballing:
grep each named symbol across the repo and report the ones with no definition.
Same for cited paths -- a comment claiming a rule is "pinned by tests/x.py" is
licensing future edits on that evidence, so verify the file and the test exist.
A citation to coverage nobody can find reads as safe for exactly that reason.

! **Grep the stem, not the identifier.** A comment is prose, and prose does not
obey identifier spelling: a dead `foo_bar` gets written as `foo-bar`, `foo bar`,
`FooBar`, or just "the barrer". Take the identifier apart and search a loose stem
(`grep -ri "foo.\?bar"`), then triage the hits -- the failure here is
self-concealing, because an identifier grep returns clean and you report the file
clean. Measured on a real deletion: the identifier grep found ten mentions, every
one a correctly dated tombstone, and **missed an eleventh written with a hyphen --
which was the only present-tense claim about the dead path in the whole set.**
The sweep was confident and wrong in the same motion, and nothing about its
output said so.

### Functionality -- does the commentary match what the function is for?

Read the function's name, its signature, and its docstring, then its body. Flag
where they disagree: a docstring describing a return shape the code no longer
returns, a `Returns:` naming fields in the wrong order, an `Args:` entry for a
parameter that does not exist, a documented exception nothing raises.

Then the harder version: **is the comment describing logic that wants to be a
function?** A long comment above a short expression is the classic tell -- if it
takes many lines to say what a few lines of code are doing, the code usually
wanted a name. Report those as findings about the *code shape*, with the comment
as the evidence, and let the human decide whether to extract. Do not extract it
yourself; that is a design change, not a prose change.

**Now read the body's comments as one sequence, in order, and ask what they
describe.** Individually each may be accurate. Read end to end they are a
narration of what the function *actually does* -- and that narration is the most
honest description of the function in the file, more honest than its name and
usually more honest than its docstring.

```python
def build_foo_bar(*args):
    """Building a FooBar"""
    created = FooBar(*args)

    # Now i need to adjust the foo bar
    created.items = args[10:] + ["zanzibar", "zimbabwe"]

    # oh I should set this other thing up
    global set_foobar
    set_foobar = FooBar

    # This other thing should also happen
    send_foo_bar_to_other(created)

    # I should also send back those extra args
    extras = ["..."]
    return FooBar, extras
```

Every comment is true. Together they say the function builds, mutates, publishes
a global, performs I/O, and returns a second value the name never hinted at. The
docstring says "Building a FooBar" and is not wrong -- it is just describing the
first four lines.

**The tell is grammatical, and cheap to spot: a comment that sequences instead of
constrains.** *"Now I need to...", "oh I should...", "this other thing should also...",
"then we..."* -- these narrate the author's path through the problem. A comment
earning its place says why a line must be the way it is (*"read before
attribution: the parse must arrive before the code that needs it"*), and it goes
visibly wrong if that line moves. A sequencing comment goes nowhere when its line
moves, because it was never about the line -- it was about the order things
occurred to somebody. A run of them is a to-do list left in the body.

Each such step is one of two things, and say which you think it is:

- **(A) not needed for the function to be the function** -- the global, the send.
  Remove them and `build_foo_bar` still builds a `FooBar`.
- **(B) at the wrong level** -- real work that belongs to the caller or to a
  function of its own, sitting here because here is where the author was.

! **Report the mismatch; do not resolve it.** The finding is *"the running
commentary describes five jobs, the name and docstring describe one"*, and it has
exactly two honest resolutions: the docstring grows until it tells the truth -- at
which point the **name** is the thing that is wrong -- or the function shrinks to
what it is called. Naming that fork *is* the deliverable. Choosing it is a design
change and belongs to the owner.

One more thing this reading catches: **narration of intent hides a mismatch that
narration of effect would expose.** *"I should also send back those extra args"*
sits above a return of `FooBar` -- the class, not `created`. A comment saying what
the author meant to do reads as confirmation, so the eye stops there. This is the
functionality angle's version of the guard table's dangerous cell.

This is the module-coherence question one level down. That angle rules on whether
a *module* is one thing, from its docstring and banners; this one rules on whether
a *function* is one thing, from its body's own commentary. Same test, same
evidence, smaller scope -- and the function-level version is where the module-level
problem is usually born.

### Module coherence -- do the comments say this is one module?

Read only the module docstring, the section banners, and the top-of-file
commentary. Ask whether they describe one thing. Flag a module whose own prose
announces two or three subjects, section banners that read like chapter breaks
in a book rather than parts of one argument, or a docstring that has to
enumerate unrelated responsibilities to be accurate.

Also flag the same rule explained in several modules -- that usually means the
rule has no owning function, and each place that performs part of it re-explains
the whole. That is a structural finding worth naming even though the fix is not
a comment change.

## Phase 2 -- One verdict per finding

Wait for all four, then dedup findings pointing at the same block. Then rule on
each survivor by asking **two questions, in this order**.

**Is it CHECKABLE?** Could a reader confirm or refute it from the code as it
stands right now, without archaeology? *"The floor is gated and the ceiling is
not"* is checkable -- read the branch. *"This was changed last spring after the
review"* is not: nothing in the file can confirm or deny it.

**Is it NECESSARY?** Would someone changing this code make a **worse decision**
without it? Not "is it interesting", not "is it true" -- would they get it wrong.

Those two answers give the verdict:

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader can verify and needs | **drop** -- it narrates what the code already says |
| **not checkable** | **move** -- real rationale, unverifiable in place | **drop** -- history |

! **Truth is not one of the questions, and that is the whole point.** A comment
can be perfectly accurate and still belong nowhere near the code. *"Moved here
from `x.validate` when that module was deleted"* is true, and a
reader needs to know the check lives **here** -- not where it used to live, or
when it moved. It is uncheckable (nothing in the file confirms it) and
unnecessary (nobody decides differently knowing it), so it goes.

This is the failure mode to watch for in yourself: history that is *correct*
reads as *earning its place*, and it does not. Accuracy is the reason it was
never deleted, not a reason to keep it.

**Rule on sentences, not on blocks.** A block is a container, and a container of
six sentences can hold six different verdicts. The common shape is a live
constraint sitting immediately beside the story of where it came from -- the
constraint is checkable and necessary, the origin story is neither, and they are
one paragraph. Splitting them is the ordinary case, not a special one.

! **A single `keep` sentence launders every sentence around it.** If you find
yourself ruling `keep` on a block because *part* of it is load-bearing, that is
the signal to descend a level, not to move on. Since a block's most defensible
sentence is usually the reason the whole block survived this long, this is not a
rare failure -- it is the default outcome for any comment that mixes a rule with
its origin, and mixing those two is the house style you are here to undo.

**Then, for anything that survives, ask one more question:** is it longer than
it needs to be? If so the verdict is **compact** -- same content, fewer words.
Compact is not a fifth category; it is what you do to a `keep` or to the
remainder left behind by a `move`.

For **move**, name the destination. If the repo already stages extracted prose
somewhere (a per-module doc tree, a decision log, an architecture doc), send it
there and say so. Staging is legitimate -- prose can land somewhere provisional
and be re-sorted into the right document later, and that beats deciding its
final home under time pressure while cutting.

For **compact**, propose the replacement text. Keep the constraint and what
breaks without it. Prefer *"X must be Y because Z breaks otherwise"* over *"this
used to be W."* Mark the one or two things a future edit is most likely to get
wrong so they survive skimming.

Do not pad the list. **keep** is a real verdict and a review that returns mostly
`keep` is a good outcome, not a failed one.

## Two more tables, for findings a length rule cannot express

### Does the comment claim a guard that exists?

A comment saying "this is pinned by X" or "X refuses this" is *licensing future
edits* -- the next person deletes something because the comment says it is
covered. So the claim has to be checked, not read.

| | **the guard exists** | **it does not** |
|---|---|---|
| **the comment claims one** | fine -- cite it precisely enough to find | ! **the dangerous cell**: a deletion gets justified by coverage nobody can find, and reads as safe for exactly that reason |
| **the comment claims none** | a silent constraint -- consider saying so | nothing to check |

Measured: a codebase can hit the bad cell often enough that one of its own
comments ends up *counting the instances* -- and that comment itself landed in the
commit that fixed the previous one. A real guard has been deleted on the strength
of a pointer to a test that was never written. Grep the cited name. Every time.

### Is the rule stated once, and does anything own it?

| | **one owning definition** | **no owner** |
|---|---|---|
| **stated once** | the healthy case | a rule living only in prose -- fine if small, a gap if load-bearing |
| **stated in several places** | redundant; point the copies at the owner | ! **the shape to report**: each site performs part of the rule and re-explains the whole |

The second-row-second-column cell is the single most common structural finding
in a long-commented codebase, and it is why the comments got long: nobody could
state the rule *once*, because no function held it. A 40-line comment above a
four-line expression is usually this. Report it as a code-shape finding with the
comment as evidence -- do not extract it yourself.

## Comments and docstrings are governed differently

**A `#` comment is governed by LENGTH.** It interrupts the code, so its cost is
the screen space between the line above and the line below.

**A docstring is governed by FORMAT, not length.** It sits at a boundary rather
than between two statements, and it is *supposed* to carry a longer
explanation -- a short summary line saying what the thing does, then as much body
as the reader genuinely needs, then `Args:` / `Returns:` / `Raises:` where they
say something the signature does not. A long docstring is not a violation. **Do
not propose `compact` on a docstring merely for being long** -- propose it when
the body is carrying something that fails one of the four angles.

Both are fully in scope for all four reviewers. What changes is the trigger:

| | `#` comment | docstring |
|---|---|---|
| too long | a finding | **not** a finding on its own |
| summary line does not summarise | n/a | a finding -- e.g. `"""Yield ..."""` on a function that returns a tuple |
| carries history | a finding | a finding |
| describes the wrong code | a finding | a finding |
| documents a parameter that does not exist | n/a | a finding |

The docstring-specific one worth checking every time is the **summary line**: it
is the only part most readers see, and it drifts silently because changing a
return type does not change the sentence describing it.

## What a length rule cannot see

If the repo enforces a cap with a test, **that test owns the cap -- this skill
does not re-litigate it.** Run this for what a line-counting test structurally
cannot see:

- **A trailing comment that carries past its own line.** One line after a
  declaration is the good form -- `sets: int  # per-round count, not per-session`
  -- and is not a finding. What reads badly is a trailing comment that runs on
  into comment-only lines beneath it, because the eye has to go back and find
  where the sentence started, mid-statement. It is also invisible to a run
  counter, which never treats the first line as the start of anything.

  ! **This is a FORMATTING finding, not a locality one.** The comment is usually
  about the right thing; it is the shape that is awkward. The fix is to lift the
  whole comment ABOVE the line so it is an ordinary block, then let the cap apply
  to all of it. Do not report these as misplaced.

- **A block split by an inserted statement.** The split itself is not the
  finding -- splitting is right when each half introduces the code beneath it.
  The finding is only the half that **still talks about what came before**. Some
  of what looks like a split is just a block that legitimately annotates several
  consecutive declarations; read it before calling it.
- **The wrong half surviving.** Shortening by deleting the constraint and keeping
  the narration passes the cap and makes the comment worse. Check what SURVIVED,
  not what went.
- **Refactoring drift.** When code moves, its commentary either moves with it,
  stays behind describing something that left, or follows and stops being true in
  its new home. No cap notices any of that; it is pure locality, and it is the
  main reason to run this after a restructuring rather than only after writing.

## Phase 3 -- Present. Always.

**This skill never edits. It ends with the verdict list.**

Report grouped by verdict, most consequential first, with the proposed
replacement text inline for every `compact`. Then stop.

! **Even when the human names the edit** -- "cap them", "fix these", "go do it" --
the deliverable is still the report. Applying is a separate, explicit step, and
saying so costs one line: *"Report only, per the skill -- say the word and I'll
apply the verdicts you accept."* Do not treat an imperative as authorization.

That is a deliberate ruling, not an oversight, and it is worth knowing why. This
review's whole value is the human's disagreement with it. Comment wording carries
their voice, and their corrections -- *"that example is weak"*, *"isn't this
history"* -- are the most valuable output of the run. **An edit applied is a
verdict never ruled on**: the finding is gone, the human never saw the question,
and afterwards nobody can tell a real problem from an imagined one. A review that
edits has quietly converted itself into an author.

It also protects the human from the surprise. Measured, before this rule: two
runs given near-identical imperative prompts split, one returning a report and
the other an 846-line diff. Both readings were defensible from the words. Neither
human knew which they were getting until it arrived.

## Rails for the pass that applies these

You are not that pass -- Phase 3 is the end of this one. Hand these along with the
verdicts, because each cost something to learn on a real 43-file pass, and the
pass that applies them is usually running without this skill loaded.

**A comment block is bounded by CODE, not by blank lines.** A comment, a blank
line, and another comment are one block to a reader, and treating the gap as a
separator makes any cap trivially evadable -- a 9-line block becomes 6+3 and
passes. Count the way a reader reads.

**Never change a line of code, a docstring's meaning, or a string literal.** The
verdicts above are about prose. If a finding needs code to move, it is a
proposal for the human, not an edit. Prove this rather than asserting it: diff
every non-comment line against the pre-edit file and confirm zero differences.
That check caught two occasions where a cut ran one line too far and took real
code with it.

**Extract before you cut, when the verdict is `move`.** Write the destination
first, verbatim, then remove the source. Doing it the other way round loses the
text on any interruption -- and it did, three times, before this became the rule.

**Re-read what you wrote.** The failure mode is producing exactly the thing you
are removing: a pass that cut seven obituaries wrote seven new ones, including
the same one twice in one file, and wrote several over-length blocks while
removing over-length blocks. Check your own replacements against the cap and
against the currency rule before reporting done.

## What this skill is not

`/simplify` reviews code structure -- reuse, complexity, efficiency, altitude, and
it applies what it finds. `/code-review` hunts correctness bugs. This one reviews
prose and **only ever proposes**: it does not restructure code, does not look for
defects, and does not edit anything, including the comments it rules on. When a
reviewer notices a defect anyway, **name it and leave it** -- a finding outside
the task gets measured and reported, never fixed in passing.

That is the sharpest difference from `/simplify`, and the easiest to lose:
`/simplify` ends in a diff, this one ends in a list of questions.

## A note for whoever edits this file

**Every example above is invented. Keep it that way.** Quoting a real comment
from this repo is tempting -- it is the most vivid illustration available -- and it
fails twice. It teaches a reviewer to recognise *that comment* instead of the
shape, so the reviewer scores well on the case in the skill and no better on the
next one. And it rots: the day someone acts on the finding, this file is citing a
comment that no longer exists -- a hygiene skill carrying its own obituary,
failing the currency rule it exists to enforce.

The measurements are worth keeping and cost nothing to anonymise. "An identifier
grep found ten and missed the hyphenated eleventh" is the whole lesson; naming
the symbol adds nothing but a trap.
