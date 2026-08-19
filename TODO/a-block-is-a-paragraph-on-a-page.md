# A block is a paragraph and a pCST is a page -- the rename the vocabulary already made

```
Status:   blocked
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (Roy's ruling while shipping the address vocabulary, 2026-08-19)
Updated:  2026-08-19 — DEFERRED past 0.2.4, whose scope is what a reviewer is HANDED.
          ~1,935 sites is a release of its own, and the vocabulary half is already done:
          the terms are settled, shipped, and correct. Nothing is blocked on the rename.
```

## Objective

!! **A pCST IS A PAGE AND A BLOCK IS A PARAGRAPH.** Roy, 2026-08-19. The register is EDITORIAL
and `CLAUDE.md` makes it a rule; `block` is the last structural term still borrowed from
compilers, and `pseudo Concrete Syntax Tree` is the whole name borrowed.

!! **AND IT IS NOT ONLY REGISTER.** Roy: *"this will make the text document formats read better
when we implement them."* The shipped definition of a block was *"the interval between two lines
of CODE"* -- which a markdown file does not have, and which is why
[`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md) is open. A PAGE made of PARAGRAPHS
is the model a prose file already fits.

! **The term is already in the shipped text, used correctly.** Measured 2026-08-19: `page` 19
times -- `review.md` opens *"Stage 8 -- REVIEW: the finished page"* and asks *"does it still read
as one page"* -- and `docs/vocabulary.md` already defines `proof` as *"the finished page"*.
`paragraph` 11 times, every one meaning what the term of art would mean.

! **It passes the test that rejected `place`.** `place` was refused because its 119 ordinary-
English uses meant LOCATION while the term would have meant ADDRESSABLE SLOT -- two meanings in
the file `ownership-context` reads. Every current use of `paragraph` (*"a paragraph naming the
module's one job"*, *"keep a paragraph readable"*) already means the unit of prose. It is not
polysemy; the register got there first.

**DONE 2026-08-19, and it is the whole vocabulary half:** `docs/vocabulary.md` carries `page` and
`paragraph` as settled terms, `vocabulary.toml` ships `paragraph` to the four editorial roles and
`page` to the stage-8 reader, and `block`'s shipped definition now reads *"a PARAGRAPH -- the
older word"* instead of the retired interval text.

!! **WHAT REMAINS IS THE RENAME, AND IT IS RELEASE-SIZED.** Measured 2026-08-19, uses of
`block`/`blocks`:

| where | uses |
| --- | ---: |
| shipped CODE -- `Block`, `blocks_stdlib`, `block_matches`, `by_block`, 460 bare `block` | **721** |
| tests | **548** |
| `docs/` | **368** |
| shipped PROSE -- `SKILL.md` 110, `reviewer-brief.md` 52, `compact.md` 43, `re-review.md` 33 | **298** |

**~1,935 sites.** ! It cannot be done piecemeal: `check_vocabulary` refuses a role a term its own
text never uses, so the moment `[roles] all` says `paragraph` the role FILES must say it too.

## Tasks

- [ ] Shipped PROSE first -- 298 uses across `SKILL.md` (110), `reviewer-brief.md`
      (52), `compact.md` (43), `re-review.md` (33) and the agent files. This is
      the half that must move before `[roles] all` can say `paragraph`, because
      `check_vocabulary` refuses a role a term its own text never uses.
- [ ] Shipped CODE -- 721 uses. `Block` -> `Paragraph`, `pcst.py` -> the page
      module, `blocks_stdlib`/`blocks_lexical`, `block_matches`, `by_block`, and
      460 bare `block`. ! The JSON census key `block` is read by held reports and
      by `record.Finding.block`, which is already deprecated -- rename it with
      that, not before.
- [ ] Tests -- 548 uses, including `test_census_blocks.py` which is named for the
      word.
- [ ] `docs/` -- 368 uses. ! Most are in dated design documents under
      `docs/superpowers/`, which are a RECORD of what was decided then: correct
      the live docs and leave the dated ones, or the record stops being one.
- [ ] Retire `block` from `vocabulary.toml` once the prose no longer uses it, and
      move it to the retired table in `docs/vocabulary.md` with the reason.
