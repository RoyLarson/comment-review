# A prose file has no blocks, so the system cannot review documentation

```
Status:   decision-needed
Progress: 4 of 9 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-17 (Roy: "both todo-tool and another project ended up in / six rules are
          attributed to CLAUDE.md while living in conventions.md / which tells me that the
          system does need to figure out how to work with .md, .rst, .txt files")
Unblocked: 2026-08-20 — the lexer is its own module as of 2026-08-20 and is the
           CONVERSION POINT -- text in, paragraphs out. A markdown reader is a Language
           row plus a reader, and the page assembles the result the same way. That is a
           far smaller job than when this was filed, when the blocker was that `block`
           meant 'the interval between two lines of CODE'.
TRIAGED:  2026-08-23 — TWO of nine were rulings ALREADY MADE by Roy on 2026-08-20 -- the
           four desks transfer, and a header is a documentable declaration -- so the box
           asking WHICH ROLES read a prose file is answered and ticked. One more is
           SUPERSEDED: the eight dangling `CLAUDE.md stage N` pointers no longer exist in
           this tree, measured today. FOUR RULINGS REMAIN OWED and they gate the build,
           which is what `decision-needed` says.
SPLIT:    2026-08-23 -- every box cut to two lines. T1's four candidate answers were an
           enumeration inside a box; they are in the Objective, where a ruling can read
           them. Every open box now carries a Verify clause; T1 and T3 had none.
```

## Objective

!! **MEASURED 2026-08-17: 190 of the 196 files in one branch's merge-base diff were `TODO/*.md`
and could not be reviewed at all.** The run reviewed the six that were code.

! **A downstream cost from the same run:** `function-context` found the same stale sentence in a
docstring AND in `.claude/skills/todo-tool/SKILL.md`. The `.md` is REFERENCE ONLY, so no verdict
could target it -- **the pair is still drifted.** A prose file being uncensusable is not only a
coverage gap; it makes the copy that a reviewer CAN see unfixable in the copy it cannot.

**`.md`, `.rst` and `.txt` have no `LANGUAGES` record**, verified 2026-08-23 -- no row in
`language.py` names any of the three -- **so a documentation file cannot be reviewed at all**:
handing one in is fatal, *"1 of 1 files handed in were not censused."* They reach a run only as
REFERENCE ONLY, which is read-to-settle and never ruled on.

! The gap is already listed in `README.md:348` -- *"Markdown and reStructuredText | no record at
all | prose files are where cited documentation actually lives"* -- with no owner and no plan.
**Two independent repos hit the same consequence on 2026-08-17**, each with a run that found
code prose attributing rules to `CLAUDE.md` that live in `conventions.md`. Six rules in one of
them. The reviewers caught the citation from the CODE side; nothing can look at the documents.

## !! The file this system CANNOT review is the one every agent reads first

`CLAUDE.md` is an instruction file. Every session in a repo reads it before touching anything,
and a wrong line in it is acted on rather than merely believed. **It is a `.md` file, so it is
permanently outside scope** -- the census exits nonzero rather than skipping it, and no run has
ever ruled on one.

**Measured twice on 2026-08-17, in two repos, by two independent readers:**

| repo | defect | found by |
| --- | --- | --- |
| `comment-review` | `CLAUDE.md` listed `split` as one of the seven verdicts; the code says `move`, and `test_reanchor_collapsed_into_move` pins it | a session reading the file by hand, an hour before the run below |
| `redacted_corpus` | **nine** `CLAUDE.md` citations naming section numbers and quoted phrases that file does not contain | `function-context`, 0.2.0 builder run |

!! **Both were found from the CODE side, and that is the only side there is.** The builder run
reached them because functions in scope cited into `CLAUDE.md`; nothing looked at the document.
A stale line no code happens to cite is unreachable by construction -- and an instruction file's
worst lines are exactly the ones no code cites, because nothing else forces them current.

! **A hygiene guard does not close this.** `redacted_corpus` publishes a cap and a width with
a live guard over `redacted_pkg/` and `tests/`, and the same run still found six
functions claiming production callers they do not have and a documented `None` return the body
cannot produce. **The guard checks length and format; it has never checked whether a claim is
true.** So "the guard is live" says nothing about the defect class this TODO is about.

## What Roy has already RULED, 2026-08-20

!! **THE FOUR DESKS ALREADY ASK THE MARKDOWN QUESTIONS, so there is no fifth role.** Roy: a prose
file *"does have a title, headers, prose, and references, all map pretty cleanly to the editorial
desks we have identified"*. title -> `module-context` (does it announce ONE subject); headers ->
`function-context` (a header is a promise the way a signature is, so: does the section deliver
what its header says); prose and references -> `block-context` (claims, and whether a cited thing
says that); placement under a header -> `ownership-context`. **No new role, no new remit.**
! That is a constraint on T1 rather than an open question: do not add a fifth reviewer.

!! **A HEADER IS A DOCUMENTABLE DECLARATION, so the `a` series works unchanged** -- `a0` the
document, `a1..aN` its headers in source order, which is what the `a` addresser already does once
the reader states which lines declare. ! **`c` HAS NO ANALOGUE**: there is no room beside a
header, so a markdown page emits `a` and `b` only. The walk handles that (`c` simply never emits)
but `attach`, `margins` and `intervals` assume three series -- markdown would be the first
language whose tier reaches two, and that is a cost T1's answer has to price.

! **This does NOT settle what bounds a paragraph.** Headers give the `a` places; the prose
BETWEEN two headers still has to be cut into paragraphs by something, and that is T1.

## !! Why it was never a missing `LANGUAGES` row alone

**A block was the interval between two lines of CODE. A prose file has no code lines.** Adding a
comment-syntax record gives the census nothing to bound a paragraph with, and the interval model
returns either one paragraph per file or none. ! The lexer/page split of 2026-08-20 is what makes
this tractable: the reader states the paragraphs and the page assembles them, so a markdown
reader is a row plus a reader rather than a change to the model.

!! **AND IN A DOCUMENTATION FILE EVERY CLAIM IS ABOUT CODE SOMEWHERE ELSE.** That inverts the
model: the system verifies prose against adjacent code, and a document verifies against distant
code. It is closer to what `referrers.py` already computes -- who names whom -- than to anything
the four roles do against a `.py` file. ! That is also the machinery T3's ruling may reach for:
`referrers.py` answers the inverse question already -- which tracked files NAME a given file.

## The four candidates for T1, so the ruling reads them rather than re-deriving them

- **(a) headings** -- each section is a paragraph, which is how an editor works a manuscript, and
  a heading is a `banner` in the term this system already has;
- **(b) fenced code blocks** -- the fences are the "code lines" and the prose between them is the
  interval, which keeps the existing definition literally intact but makes a document with no
  fences one paragraph;
- **(c) paragraphs**;
- **(d) nothing -- prose files stay REFERENCE ONLY, and the system says so on purpose.**

! **(d) is a legitimate answer and should be RULED rather than defaulted into**, which is what is
happening today. ! Roy's header ruling above settles the `a` series, not this.

## What the CAP means here, and what `docs/limitations.md` does not say

! The cap is measured in lines of a `#` run; a markdown section has no such unit, so stage 6
would have nothing to apply. That is T4.

! MEASURED 2026-08-23: `docs/limitations.md` says nothing about markdown or prose files. The
ASYMMETRY exists today whatever T1 answers -- code prose citing a document is checkable by a
reviewer opening it, and the document's own drift is invisible -- and that asymmetry is the
measured defect: six rules attributed to the wrong file.

## What has already been ruled out as a second defect

! SUPERSEDED 2026-08-23. The eight dangling `CLAUDE.md stage N` pointers are not in this tree:
`grep -rn "CLAUDE\.md.*[Ss]tage [0-9]"` over `plugins/`, `docs/*.md` and `README.md` returns
nothing. Relative links that resolve nowhere are counted and owned by
[`dangling-links-resolve-nowhere`](dangling-links-resolve-nowhere.md), which is a different
defect -- a tool measures it.

## Tasks

- [?] T1 | T1 -- * RULE what BOUNDS a paragraph in a prose file, from the four
      candidates in the Objective. Verify: the ruling is recorded in
      `docs/decision-log.md`.
- [x] T2 | FINISHED | unknown | T2 -- RULED 2026-08-20: the four existing desks
      read a prose file, and no fifth. The mapping is in the Objective.
- [?] T3 | T3 -- * RULE what a claim in a document is checked AGAINST. Verify:
      the answer names the input a `block-context` reviewer is handed for a
      `.md` page.
- [?] T4 | T4 -- * RULE what happens to the CAP on a prose page. Verify:
      `SKILL.md`'s cap rule states what it means there, including if the answer
      is "no cap applies".
- [ ] T5 | T5 -- Name the prose-file asymmetry in `docs/limitations.md`: code
      prose citing a document is checkable, the document's drift is not. Verify:
      the file carries it.
- [x] T6 | FINISHED | unknown | T6 -- SUPERSEDED 2026-08-23. The eight dangling
      `CLAUDE.md stage N` pointers are not in this tree. Measurement in the
      Objective.
- [ ] T7 | T7 -- Move `README.md:348`'s gap row when T1's answer lands,
      including if the answer is (d). Verify: the row states the ruled position
      and cites where it was ruled.
- [x] T8 | FINISHED | unknown | T8 -- RULING, MADE 2026-08-20: the four desks
      already ask the markdown questions. Kept in the Objective as the record of
      Roy's words.
- [x] T9 | FINISHED | unknown | T9 -- REASONING, kept in the Objective: a header
      is a documentable declaration, so `a` works and `c` never emits -- and
      markdown is the first tier to reach two series.
