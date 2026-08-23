# A leaf is the page and also the place, in two shipped definitions

```
Status:   open
Progress: 0 of 14 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22, describing stage 2 as stacking pages into leaves
          -- the sense foliator.py rules against)
Narrowed: 2026-08-23 — paginate ruled out for stage 2 on the split-infinite-output
          sense; the leaf premise is what the remaining choice turns on
```

## Objective

**A leaf is ONE SHEET and carries TWO pages, recto and verso. This tree uses it for the page in
one shipped definition and for the PLACE in another, and both are wrong against the trade.**

!! **THE FALSE ONE IS SHIPPED AS A DEFINITION AGENTS READ.** `references/vocabulary.toml:81`:

> `folio = "The `b3` half of an address, after the `@`. A leaf's number in publishing, which is
> what it is here."`

! **`b3` is the fourth gap on one page.** It is not any leaf's number, and the clause *"which is
what it is here"* asserts the equivalence rather than merely borrowing the word. A reviewer is
given this and nothing contradicts it.

!! **AND A RULING RESTS ON THE SAME PREMISE.** `foliator.py:17` reads *"FOLIATION, not
pagination: the numbering of LEAVES, which is what a place is."* The choice between the two words
is justified by the claim that a place is a leaf. **A place is not a leaf**, so the reason given
does not hold -- whatever the right answer turns out to be.

! **The trade's split is narrow and neither half fits:** foliation numbers LEAVES, the practice
that predates page numbers; pagination numbers PAGES. This system numbers **positions within a
page**, which is neither, because a proof is marked by MARGIN AND LINE and the trade never needed
addressable slots.

! **`page` and `place` are both correct and are not in question.** A file has one continuous side
and no verso, so it is a page and there is no leaf anywhere in the model. What has no trade word
is the numbering of places -- which the register rule permits as a coinage, since the method is
to name the job by what it DOES and take the trade's word only where one exists.

! **The dependency-graph sense is a separate matter and reads as harmless** -- `constants.py`'s
ULTIMATE LEAF, ruled 2026-08-22. Different domain, no overlap in what it operates on, which is
the test `docs/vocabulary.md` states for allowed polysemy. What is missing there is the
DECLARATION, not the separation.

!! **`check_vocabulary.py` CANNOT SEE ANY OF THIS**, and extending it is not the obvious fix: it
refuses a term defined twice and a term no role uses, and both `leaf` claims sit INSIDE other
terms' definition strings, where nothing reads them as definitions at all.

! Raised by Roy, 2026-08-22, in two steps -- first using the word (*"stacks them together into
leafs I think is the correct term"*), then asking whether it is one.

## Tasks

- [ ] TWO SHIPPED DEFINITIONS DISAGREE ABOUT WHAT A LEAF IS.
      `references/vocabulary.toml:27` defines the census as *"Flat, because a page
      is: paragraphs run down a leaf and do not nest"* -- a leaf is the PAGE.
      `foliator.py:17` reads *"the numbering of LEAVES, which is what a place is"*
      -- a leaf is a PLACE. ! A place cannot both BE a leaf and be one of the
      things that run down a leaf.
- [ ] ! AND `folio` IS DEFINED AGAINST THE FIRST SENSE. `vocabulary.toml:81`: *"A
      leaf's number in publishing, which is what it is here."* A folio numbers a
      PLACE here -- `b3`, `a0` -- so if a leaf is the page, this definition says a
      folio numbers the page, which is the one thing an address does not do.
- [ ] ! A THIRD SENSE IS THE DEPENDENCY GRAPH'S, and it is the one that reads as
      harmless: `constants.py:3`, *"A LEAF WITH NO SIBLINGS"*, and the ULTIMATE
      LEAF rule Roy stated 2026-08-22. Different domain, no overlap in what it
      operates on -- which is the test `docs/vocabulary.md` states for allowed
      polysemy. ! What is missing is the DECLARATION, not the separation.
- [ ] * WHICH SENSE SURVIVES IS A RULING. In the trade a leaf is one SHEET and
      carries TWO pages, recto and verso -- so a leaf CONTAINS pages, and this
      tree has it the other way in both live senses. Rule whether a leaf is the
      page, the place, or a word this system stops using.
- [ ] ! `check_vocabulary.py` CANNOT SEE THIS and is not the gate to extend
      blindly. It refuses a term defined twice and a term no role uses; both
      `leaf` definitions are inside OTHER terms' definition strings, where nothing
      reads them as definitions at all. ! Whatever check is added has to be able
      to fail -- see `docs/gates.md`.
- [ ] RAISED BY THE SENTENCE THAT USED IT. Roy, 2026-08-22, on what stage 2 does:
      *"it calls census to get the pages and the references and stacks them
      together into leafs I think is the correct term."* ! That is the
      `vocabulary.toml` sense, and it is the sense `foliator.py` contradicts -- so
      the collision is not dormant; it is what a reader reaches for.
- [ ] CORRECT `vocabulary.toml:81`. The `folio` definition ends *"A leaf's number
      in publishing, which is what it is here"* -- a shipped false equivalence,
      since `b3` is the fourth gap on one page. ! It is EMITTED to reviewers by
      `vocabulary.py`, so this is prose an agent acts on rather than prose a
      maintainer reads.
- [ ] CORRECT `vocabulary.toml:27`. The census definition closes *"paragraphs run
      down a leaf and do not nest"*. The flatness claim is TRUE and is the point
      of the sentence; only the word `leaf` is wrong -- a page is what they run
      down.
- [ ] * RE-DECIDE `foliator.py:17` ON A PREMISE THAT HOLDS. It rules *"FOLIATION,
      not pagination: the numbering of LEAVES, which is what a place is."* A place
      is not a leaf. ! The conclusion may still be right; what is certain is that
      the stated reason is not a reason. Rule the word again with the trade split
      in view -- foliation numbers leaves, pagination numbers pages, and this
      numbers positions within a page.
- [ ] ! AND IT IS THE SAME QUESTION AS THE STAGE NAME. Roy, 2026-08-22: *"I think
      the collate step now is actually a paginate step."* `foliator.py:17` is the
      only thing in the tree that rules against `pagination`, and it does so on
      the false premise. ! Settle the two together or the stage takes a word the
      module refuses.
- [ ] ! WHAT IS NOT IN QUESTION: `page` and `place`. A file has one continuous
      side and no verso, so it is a page and there is no leaf in the model at all.
      The numbering of PLACES has no trade word because a proof is marked by
      margin and line -- a coinage is correct here, which is what the register
      rule allows.
- [ ] `PAGINATE` IS OUT FOR STAGE 2, AND THE REASON IS THE SENSE OF THE WORD. Roy,
      2026-08-23: *"the way I have used in the past is by taking something that
      can print infinitely and split it into pages."* ! Stage 2 splits nothing --
      the division arrives from the filesystem, one file, one page -- so
      pagination names an act it does not perform. Recorded because it was
      PROPOSED the same day and will read as open otherwise.
- [ ] ! WHAT IS LEFT IS THE NUMBERING, WHICH IS THE ONLY THING STAGE 2 CREATES.
      The division arrives done, the lexing happens on the way, and the stacking
      is MEASURED order-free -- see `galley.py`, 179 paragraphs identical forward
      and reversed. ! So the candidate that needs no new vocabulary is `FOLIATE`:
      already the function, the module and the result type, and an act like MARK,
      APPLY, COMPACT and REVIEW. * Unruled.
- [ ] ! AND `collate` IS FREED WHATEVER STAGE 2 BECOMES, which is the first
      starred blocker on `verdicts-is-the-join` -- collating would then mean what
      the trade means: transferring every hand's marks onto one proof.
