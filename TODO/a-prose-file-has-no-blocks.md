# A prose file has no blocks, so the system cannot review documentation

```
Status:   open
Progress: 0 of 9 tasks done
Owner:    Roy (* 2 rulings) * session
Requires-Roy: true
Raised:   2026-08-17 (Roy: "both todo-tool and redacted_lane_a ended up in / six rules are
          attributed to CLAUDE.md while living in conventions.md / which tells me that the
          system does need to figure out how to work with .md, .rst, .txt files")
Unblocked: 2026-08-20 — the lexer is its own module as of 2026-08-20 and is the
           CONVERSION POINT -- text in, paragraphs out. A markdown reader is a Language
           row plus a reader, and the page assembles the result the same way. That is a
           far smaller job than when this was filed, when the blocker was that `block`
           meant 'the interval between two lines of CODE'.
```

## Objective

!! **MEASURED 2026-08-17: 190 of the 196 files in one branch's merge-base diff were `TODO/*.md`
and could not be reviewed at all.** The run reviewed the six that were code.

! **A downstream cost from the same run:** `function-context` found the same stale sentence in a
docstring AND in `.claude/skills/todo-tool/SKILL.md`. The `.md` is REFERENCE ONLY, so no verdict
could target it -- **the pair is still drifted.** A prose file being uncensusable is not only a
coverage gap; it makes the copy that a reviewer CAN see unfixable in the copy it cannot.

**`.md`, `.rst` and `.txt` have no `LANGUAGES` record, so a documentation file cannot be
reviewed at all** -- handing one in is fatal: *"1 of 1 files handed in were not censused."* They
reach a run only as REFERENCE ONLY, which is read-to-settle and never ruled on.

! The gap is already listed in `README.md` -- *"Markdown and reStructuredText | no record at all
| prose files are where cited documentation actually lives"* -- with no owner and no plan.
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

## !! It is not a missing `LANGUAGES` row, and that is the whole difficulty

**A block is the interval between two lines of CODE. A prose file has no code lines.** Adding a
comment-syntax record gives the census nothing to bound a block with, and the interval model
returns either one block per file or none.

!! **And the four remits do not transfer.** They are built on prose sitting BESIDE the code it
describes:

| role | on a `.py` file | on a `.md` file |
| --- | --- | --- |
| `ownership-context` | does this belong to the ANCHOR it sits on | there is no declaration; the nearest thing is a heading |
| `block-context` | is every claim true of the code it sits with | **there is no code it sits with** |
| `function-context` | does the commentary match what the function is for | there is no function |
| `module-context` | do the comments say this is ONE module | there is no module surface to account for |

!! **In a documentation file every claim is about code SOMEWHERE ELSE.** That inverts the model:
the system verifies prose against adjacent code, and a document verifies against distant code.
It is closer to what `referrers.py` already computes -- who names whom -- than to anything the
four roles do.

## Tasks

- [ ] * Rule on what BOUNDS a block in a prose file. Candidates:
      **(a) headings** -- each section is a block, which is how an editor works a manuscript, and
      a heading is a `banner` in the term this system already has;
      **(b) fenced code blocks** -- the fences are the "code lines" and the prose between them is
      the interval, which keeps the existing definition literally intact but makes a document
      with no fences one block;
      **(c) paragraphs**;
      **(d) nothing -- prose files stay REFERENCE ONLY, and the system says so on purpose.**
      ! (d) is a legitimate answer and should be ruled rather than defaulted into, which is what
      is happening today.

- [ ] * Rule on WHICH ROLES read a prose file, if any do. The table above says none of the four
      transfers unchanged. ! Do not add a fifth role to solve this without ruling on it: the
      skill states there is deliberately no fifth reviewer for consistency, and the same
      argument may or may not apply here.

- [ ] Decide what a claim in a document is checked AGAINST. A rule stated in `conventions.md`
      is true or false about a tree, not about the line below it. ! `referrers.py` already
      answers the inverse -- which tracked files NAME a given file -- and may be the machinery.

- [ ] Say what happens to the CAP. It is measured in lines of a `#` run; a markdown section has
      no such unit, and stage 6 would have nothing to apply.

- [ ] Handle the ASYMMETRY that exists today even without any of the above: code prose citing a
      document is checkable by a reviewer opening it, and the document's own drift is invisible.
      ! That asymmetry is the measured defect -- six rules attributed to the wrong file -- and it
      may be worth naming in `docs/limitations.md` before any of this is built.

- [ ] Check whether the eight dangling `CLAUDE.md stage N` pointers are the same defect or a second
      one. A run reported them as ONE question needing one ruling rather than thirty near-
      identical findings, which is a judgement worth examining on its own.

- [ ] Re-measure after any change. `README.md`'s gap row is the current statement and must move
      with the answer, including if the answer is (d).
- [ ] !! THE FOUR DESKS ALREADY ASK THE MARKDOWN QUESTIONS. Roy, 2026-08-20: a
      prose file 'does have a title, headers, prose, and references, all map
      pretty cleanly to the editorial desks we have identified'. title -> module-
      context (does it announce ONE subject); headers -> function-context (a
      header is a promise the way a signature is, so: does the section deliver
      what its header says); prose and references -> block-context (claims, and
      whether a cited thing says that); placement under a header -> ownership-
      context. ! No new role, no new remit.
- [ ] !! A HEADER IS A DOCUMENTABLE DECLARATION, so the `a` series works unchanged
      -- `a0` the document, `a1..aN` its headers in source order, which is what
      the `a` addresser already does once the reader states which lines declare. !
      `c` HAS NO ANALOGUE: there is no room beside a header, so a markdown page
      emits `a` and `b` only. The walk handles that (`c` simply never emits) but
      `attach`, `margins` and `intervals` assume three series -- the first
      language whose tier reaches two.
