# The galley updates the page AND sets the text, which are two roles

```
Status:   open
Progress: 4 of 13 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, on why every galley update to date has been
          refused)
Built:    2026-08-21 — the split is built and wired: galley.reset places by address,
          compositor.set_page sets, splice/overlaps/splice_range/paragraph_matches
          deleted. The shipped PROSE still describes the old shape -- vocabulary.toml,
          SKILL.md and review.md remain
```

## Objective

**`galley.py` does two jobs, and the second one keeps destroying the first.** It decides
which paragraph each verdict belongs to and whether the census still matches -- *updating the
page* -- and then splices that text into a copy of the file at line ranges and writes bytes --
*setting it*. Roy, 2026-08-21: *"That is all because the galley is trying to do two things at
once instead of one thing well."*

!! **THE SHIPPED VOCABULARY ALREADY SAYS SO.** `references/vocabulary.toml` defines `page` and
adds: *"the GALLEY is text set but not yet made into pages."* A galley that writes files has
made pages. `galley.py`'s own module docstring quotes that definition and then does the
opposite -- and so, in the trade, does the sequence: a galley proof is pulled from type still
in the tray precisely so that correcting it costs nothing, because nothing has been made up
yet.

!! **THIS IS THE ERROR CLAUDE.md OPENS WITH.** Roy, 2026-08-21: *"The galley was always broken
and on this commit is still broken ... that header is referencing this exact error even though
it was masked by so many other things."* **739 tests pass, `ruff` is clean, the 3.11 floor
holds, `check_vocabulary` reports 0 drifted, and the shipped definition of a term disagrees
with the shipped implementation of it.** No gate can ask that question; it is not the kind of
question a gate asks.

## The split, ruled 2026-08-21

| | takes | returns | may not |
| --- | --- | --- | --- |
| **galley** | a page, and the records | an UPDATED PAGE -- marks applied | set text |
| **compositor** | a page | TEXT | decide anything |

Roy: *"galley gets the old page - updates the old page with the verdict/record/marks and then
a page-setter sets the page to rewrite the output text."* The term is his ruling too --
*"compositor works"* -- and it is the trade word: a compositor SETS type, make-up is what turns
set type into pages.

## Why it is worth doing beyond tidiness

**A compositor that is the only writer makes `set(page_for(text)) == text` a byte-for-byte
identity, over any file in any language.** Nothing in this system tests that. `prove_unchanged`
is strictly weaker -- it proves the executable code survived, not that the model of a page is
lossless. Roy: *"we can compare the round trip directly page in page out, page in, comments
removed, page out no comments ... No ambiguity about how the page gets written. No this got
lost this wasn't done right."*

! **It also closes [`a-series-never-fills-outside-python`](a-series-never-fills-outside-python.md)
mechanically.** That TODO waits on a C round trip which was going to be a judgement call. The
identity above IS the instrument, and one run over `corpora/cpython` settles C while the same
run settles Rust, Go, Java and the rest.

## Not in scope

The margin rendering and the marks-on-the-page proposal, which live on
[`the-census-is-mostly-intervals-nobody-rules-on`](the-census-is-mostly-intervals-nobody-rules-on.md).
A compositor writes a FILE; what a reviewer READS is that other question.

## Tasks

- [ ] !! THE SHIPPED VOCABULARY ALREADY SAYS WHAT A GALLEY IS, AND THE CODE
      CONTRADICTS IT. `references/vocabulary.toml` defines `page` and adds: *"the
      GALLEY is text set but not yet made into pages."* `galley.py` splices
      proposed text into copies of files at line ranges and writes them to disk --
      which is MAKING PAGES. Its own module docstring quotes the correct
      definition and then does the opposite.
- [ ] !! IT IS THE `GREEN GATE` CASE CLAUDE.md OPENS WITH, and Roy named it
      2026-08-21: *"The galley was always broken and on this commit is still
      broken ... that header is referencing this exact error even though it was
      masked by so many other things."* 739 tests pass, ruff is clean, the 3.11
      floor holds, `check_vocabulary` reports 0 drifted -- and the shipped
      definition of the term disagrees with the shipped implementation of it. No
      gate can ask that question.
- [x] * RULED 2026-08-21 -- THE SPLIT. Roy: *"galley gets the old page - updates
      the old page with the verdict/record/marks and then a page-setter sets the
      page to rewrite the output text."* GALLEY takes a Page and the records and
      returns an UPDATED PAGE -- marks applied, nothing set. COMPOSITOR takes a
      Page and returns TEXT. Two roles, two sets of rules.
- [x] * RULED 2026-08-21 -- THE TERM IS `compositor`. In the trade a compositor is
      the one who SETS type; make-up is what turns set type into pages. Roy:
      *"compositor works."* ! Chosen against the register rather than after it,
      which is the rule three LAW words broke.
- [ ] GIVE `galley` ITS OWN DEFINITION. It has none: `vocabulary.toml` mentions it
      only inside the definition of `page`, and `scripts/vocabulary_sweep.py`
      cannot flag it because a term absent from the inventory is not a term the
      sweep knows to look for. It is used in `reviewer-brief.md`, `re-review.md`,
      `SKILL.md` and eight scripts.
- [ ] DEFINE `compositor` in `references/vocabulary.toml`, and give it to the
      roles whose text uses it -- `check_vocabulary.py` holds three ways at once:
      every key a role is given has a definition, no definition is written for
      nobody, and no role is given a term its own text never uses. A definition
      added without a reader fails the second.
- [ ] SKILL.md: the pipeline gains the compositor at stage 7. Today 7a PRESENT and
      7b WRITE both sit on the galley, and the stage diagram shows neither the
      update nor the setting.
- [x] `references/review.md` -- the FINAL REVIEWER, stage 8 -- reads the finished
      page. Roy asked for the term to land there: a proofreader reads a PROOF,
      which is what the compositor produced, and the file currently has no word
      for where its input came from.
- [ ] !! THE SPLIT MAKES A NEW INVARIANT TESTABLE, and it is the point rather than
      a side effect: if the compositor is the ONLY thing that writes text, then
      `set(page_for(text)) == text` is a byte-for-byte identity over any file in
      any language. Nothing tests that today. `prove_unchanged` is strictly weaker
      -- it proves the EXECUTABLE CODE survived, not that the model of a page is
      lossless. Roy: *"we can compare the round trip directly page in page out,
      page in, comments removed, page out no comments."*
- [x] ! IT CLOSES THE C QUESTION MECHANICALLY. `a-series-never-fills-outside-
      python` waits on a round trip that was going to be a judgement call; the
      identity above is that instrument, and one run over `corpora/cpython`
      answers it for C while the same run answers Rust, Go, Java and the rest.
- [ ] ! THE REFUSALS THE SPLIT DELETES, both of which are SETTING failures that
      abort the UPDATE: `REFUSED {rel}: {n} range(s) no longer match the census`
      and `REFUSED {rel}: edits at X and Y share a line`. Each does `refused +=
      len(file_edits)` -- one line-arithmetic collision throws away EVERY edit for
      that file, with the verdicts and the page update both correct. !
      `overlaps()` cannot even be expressed against a Page: two paragraphs are two
      places, and a place holds one paragraph. Sharing a LINE is an artifact of
      line-range surgery.
- [ ] * OPEN, and no ruling is owed until the build reaches them: whether the
      galley emits a `Page` object or a serialised one, and whether the compositor
      is a new module or `galley.py` renamed with the update half moved out.
- [ ] ! EVIDENCE THE PLACES ARE STABLE ENOUGH FOR THIS, measured 2026-08-21: a
      file edited from 10 lines to 16 -- an `add` filling an empty gap and prose
      grown from one line to four -- kept a byte-identical folio set (`a0 a1 a2
      b0..b6 c0..c5 f0`) and byte-identical anchors, while 13 of its 17 anchor
      LINES moved. A folio is an ordinal over the code, and a verdict cannot
      change the code.
