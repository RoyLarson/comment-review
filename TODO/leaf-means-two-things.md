# A leaf is the page and also the place, in two shipped definitions

```
Status:   open
Progress: 15 of 19 tasks done
Owner:    comment-review
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22, describing stage 2 as stacking pages into leaves
          -- the sense addresser.py rules against)
Narrowed: 2026-08-23 — paginate ruled out for stage 2 on the split-infinite-output
          sense; the leaf premise is what the remaining choice turns on
Settled:  2026-08-23 — the binder model closes it -- no leaf in the picture, cue
          becomes cue, and Cues needs no exotic noun because completeness is in the
          tabbing practice
Worked:   2026-08-23 — the folio family is retired in the gate, a quoted span is exempt
          outside agent-facing files, and the graph sense of leaf is kept as declared
          polysemy
```

## Objective

**The model is settled, 2026-08-23, and it is one picture in one register.** Roy: *"by the time
we are back to census I think we are back to it being a Binder of pages. The cues are the little
sticky notes that we put on the edge of the page and, like an overly diligent person, we also
sticky-noted the places where we might want to insert text explicitly."*

| | what it is |
| --- | --- |
| **binder** | what the census supplies -- loose pages, kept in order but not bound to it, updated by replacing one page |
| **page** | one file |
| **cue** | the tab on the page edge. It carries NO content, only the claim that content belongs here |
| **note** | the prose a cue points at |
| **address** | `path@cue` -- the full routing, with the runner's root implicit and never written |

!! **THIS DISSOLVES BOTH HALVES OF THIS FILE RATHER THAN SETTLING THEM.** There is no leaf in the
picture at all, so the two contradicting definitions have nothing to contradict about; and `folio`
becomes `cue`, so the false equivalence in `vocabulary.toml:81` -- *"a leaf's number in
publishing, which is what it is here"* -- goes with the word.

!! **AND COMPLETENESS LIVES IN THE PRACTICE, NOT IN THE NOUN**, which is what ends the search for a
word for `Foliation`. Roy asked for *"a name for a contiguous list of addresses"* -- his block,
where every lot has an address whether or not a house sits on it. `cadastre` was the exact word
for that and carries completeness IN the word. ! It is not needed: an overly diligent person tabs
every place they might insert, so *every cue on this page* is already the full enumeration. **The
tabbing habit delivers what the noun would have promised**, and that habit is what `cue` does
-- it emits a place per trigger whether prose sits there or not.

! **THE FAR-AFIELD CANDIDATES ARE RECORDED AND NOT TAKEN.** `cadastre`, `plat`, `registrar`,
`address space`, `cue sheet` -- all free, all measured. Roy: *"going too far afield too many times
on this is not an ideal thing."* ! `cadastre` and `plat` are land-law and surveying, which is the
neighbourhood `jurisdiction` came from before it became `remit` -- the recorded example of a term
checked for collisions and never for register. **The binder picture needs no second register.**

! **`register` ITSELF IS TAKEN TWICE** and was refused on that: 48 uses, mostly the linguistic
sense this repo's whole method runs on, plus `printing register`, where being out of register is a
press defect.

!! **THE GUARD, KEPT AS A TEST.** Roy: *"I want to be careful in this because I don't want the
line-numbers creeping in again."* **A name reinvents line numbers if it implies POSITION MEASURED
FROM A START** -- `index`, `sequence`, `ordinal` all fail it. ! And this is why `b3` is not a line
number even though it is the fourth gap: it is assigned once by walking CODE, and code does not
move when prose is edited. **Line numbers fail because the thing they count is the thing the edit
changes.**

## Tasks

- [x] TWO SHIPPED DEFINITIONS DISAGREE ABOUT WHAT A LEAF IS.
      `references/vocabulary.toml:27` defines the census as *"Flat, because a page
      is: paragraphs run down a leaf and do not nest"* -- a leaf is the PAGE.
      `addresser.py:17` reads *"the numbering of LEAVES, which is what a place is"*
      -- a leaf is a PLACE. ! A place cannot both BE a leaf and be one of the
      things that run down a leaf.
- [x] ! AND `folio` IS DEFINED AGAINST THE FIRST SENSE. `vocabulary.toml:81`: *"A
      leaf's number in publishing, which is what it is here."* A folio numbers a
      PLACE here -- `b3`, `a0` -- so if a leaf is the page, this definition says a
      folio numbers the page, which is the one thing an address does not do.
- [x] ! A THIRD SENSE IS THE DEPENDENCY GRAPH'S, and it is the one that reads as
      harmless: `constants.py:3`, *"A LEAF WITH NO SIBLINGS"*, and the ULTIMATE
      LEAF rule Roy stated 2026-08-22. Different domain, no overlap in what it
      operates on -- which is the test `docs/vocabulary.md` states for allowed
      polysemy. ! What is missing is the DECLARATION, not the separation.
- [x] * WHICH SENSE SURVIVES IS A RULING. In the trade a leaf is one SHEET and
      carries TWO pages, recto and verso -- so a leaf CONTAINS pages, and this
      tree has it the other way in both live senses. Rule whether a leaf is the
      page, the place, or a word this system stops using.
- [x] ! `check_vocabulary.py` CANNOT SEE THIS and is not the gate to extend
      blindly. It refuses a term defined twice and a term no role uses; both
      `leaf` definitions are inside OTHER terms' definition strings, where nothing
      reads them as definitions at all. ! Whatever check is added has to be able
      to fail -- see `docs/gates.md`.
- [ ] RAISED BY THE SENTENCE THAT USED IT. Roy, 2026-08-22, on what stage 2 does:
      *"it calls census to get the pages and the references and stacks them
      together into leafs I think is the correct term."* ! That is the
      `vocabulary.toml` sense, and it is the sense `addresser.py` contradicts -- so
      the collision is not dormant; it is what a reader reaches for.
- [x] CORRECT `vocabulary.toml:81`. The `cue` definition ends *"A leaf's number
      in publishing, which is what it is here"* -- a shipped false equivalence,
      since `b3` is the fourth gap on one page. ! It is EMITTED to reviewers by
      `vocabulary.py`, so this is prose an agent acts on rather than prose a
      maintainer reads.
- [x] CORRECT `vocabulary.toml:27`. The census definition closes *"paragraphs run
      down a leaf and do not nest"*. The flatness claim is TRUE and is the point
      of the sentence; only the word `leaf` is wrong -- a page is what they run
      down.
- [x] * RE-DECIDE `addresser.py:17` ON A PREMISE THAT HOLDS. It rules *"FOLIATION,
      not pagination: the numbering of LEAVES, which is what a place is."* A place
      is not a leaf. ! The conclusion may still be right; what is certain is that
      the stated reason is not a reason. Rule the word again with the trade split
      in view -- foliation numbers leaves, pagination numbers pages, and this
      numbers positions within a page.
- [x] ! AND IT IS THE SAME QUESTION AS THE STAGE NAME. Roy, 2026-08-22: *"I think
      the collate step now is actually a paginate step."* `addresser.py:17` is the
      only thing in the tree that rules against `pagination`, and it does so on
      the false premise. ! Settle the two together or the stage takes a word the
      module refuses.
- [ ] ! WHAT IS NOT IN QUESTION: `page` and `place`. A file has one continuous
      side and no verso, so it is a page and there is no leaf in the model at all.
      The numbering of PLACES has no trade word because a proof is marked by
      margin and line -- a coinage is correct here, which is what the register
      rule allows.
- [x] `PAGINATE` IS OUT FOR STAGE 2, AND THE REASON IS THE SENSE OF THE WORD. Roy,
      2026-08-23: *"the way I have used in the past is by taking something that
      can print infinitely and split it into pages."* ! Stage 2 splits nothing --
      the division arrives from the filesystem, one file, one page -- so
      pagination names an act it does not perform. Recorded because it was
      PROPOSED the same day and will read as open otherwise.
- [x] ! WHAT IS LEFT IS THE NUMBERING, WHICH IS THE ONLY THING STAGE 2 CREATES.
      The division arrives done, the lexing happens on the way, and the stacking
      is MEASURED order-free -- see `galley.py`, 179 paragraphs identical forward
      and reversed. ! So the candidate that needs no new vocabulary is `CUE`:
      already the function, the module and the result type, and an act like MARK,
      APPLY, COMPACT and REVIEW. * Unruled.
- [x] ! AND `collate` IS FREED WHATEVER STAGE 2 BECOMES, which is the first
      starred blocker on `verdicts-is-the-join` -- collating would then mean what
      the trade means: transferring every hand's marks onto one proof.
- [x] `PORTFOLIO` IS PROPOSED FOR WHAT THE CENSUS PRODUCES. Roy, 2026-08-23: *"The
      census creates a portfolio."* A portfolio is a case of LOOSE sheets --
      gathered but unbound -- and it is the only container that makes `--filtered`
      coherent: you cannot hand a reviewer pages 12, 40 and 88 of a bound book,
      because the binding IS the order, but you can hand them sheets from a
      portfolio. ! The word appears nowhere in the tree. ! It also names a THING
      rather than an act, so it leaves the stage name free instead of competing
      with FOLIATE, which was the stage-name candidate at the time. * Unruled; the one strain is that a trade portfolio usually
      holds FINISHED work.
- [x] RULED 2026-08-23: THE ADDRESS IS `path@cue`. Roy: *"path@place is definitely
      @cue. Place was a good stand in but imprecise enough that we have had
      problems already."* ! A CUE is the mark in the text saying a note belongs at
      this point -- it carries no content, only the claim that content belongs
      HERE, which is exactly what the `@` half asserts. The note carries the
      content and not the position. ! `cue`, `reference mark` and `superior
      figure` are all unused in the tree.
- [x] * STILL OPEN: what `Foliation` and `folio` become. `folio` follows `cue`
      (278 sites); `Cues` -- the complete ordered set of cues for one page,
      filled or not -- does not. ! Candidates measured 2026-08-23: `register` is
      TAKEN TWICE (48 uses: the linguistic sense this repo's method runs on, plus
      `printing register`, where out-of-register is a press defect). `registrar`,
      `cadastre`, `plat`, `cue sheet` and `address space` are all free.
- [ ] ! THE TEST FOR LINE-NUMBER CREEP, which is what Roy asked to guard against:
      a name reinvents line numbers if it implies POSITION MEASURED FROM A START.
      `index`, `sequence`, `ordinal` fail it. `cadastre`, `register`, `plat` pass
      -- they enumerate IDENTIFIED PARCELS, and the identifier belongs to the
      parcel rather than being recomputed by counting. !! AND THIS IS WHY `b3` IS
      NOT A LINE NUMBER even though it is the fourth gap: it is assigned once by
      walking CODE, and code does not move when prose is edited. Line numbers fail
      because the thing they count is the thing the edit changes.
- [ ] ! WHAT REMAINS IS MECHANICAL, NOT A RULING: 278 `folio` sites become `cue`,
      and `Foliation`/`foliate`/`foliator` follow the addresser rename. ! HISTORY
      KEEPS THE OLD NAMES -- `docs/history.md`, `TODO/completed/`, `CHANGELOG.md`
      and `evidence/` record what the system WAS, and renaming inside them is what
      makes an old artifact unreadable, which is the thing those files exist to
      prevent.
