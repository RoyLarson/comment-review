# A block is a paragraph and a pCST is a page -- the rename the vocabulary already made

```
Status:   blocked
Progress: 1 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (Roy's ruling while shipping the address vocabulary, 2026-08-19)
Updated:  2026-08-19 — DEFERRED past 0.2.4, whose scope is what a reviewer is HANDED.
          ~1,935 sites is a release of its own, and the vocabulary half is already done:
          the terms are settled, shipped, and correct. Nothing is blocked on the rename.
Narrowed: 2026-08-19 — Prose done 2026-08-19 and un-deferred at Roy's word -- the
          deferral was wrong, and check_vocabulary plus the generated verdict table both
          refused the half-state within minutes. What remains is internal identifiers.
          The four traps that break a bulk rename are now recorded in the objective,
          which is the expensive half of the job.
```

## Objective

!! **THE VOCABULARY AND EVERYTHING A HUMAN OR AN AGENT READS ALREADY SAY PARAGRAPH.** Done
2026-08-19: 285 renames across 13 shipped prose files, `block` retired from `vocabulary.toml`, the
eight count nouns in `verdicts.py`'s report, and the census listing's own header and tier table.
**What remains is INTERNAL: identifiers in the shipped scripts and in the tests.**

| where | uses | what they are |
| --- | ---: | --- |
| shipped CODE | **706** | `Block`, `blocks_stdlib`, `blocks_lexical`, `block_matches`, `blocks_in`, `prose_blocks`, `by_block`, locals, and docstring prose |
| tests | **539** | mirrors of the above; `test_census_blocks.py` is named for the word |
| `docs/` | **379** | ! most are dated design records under `docs/superpowers/` -- correct the LIVE docs and leave those, or the record stops being one |
| shipped prose | 11 | all `block-context`, the role name |

!! **FOUR TRAPS, EACH FOUND BY BREAKING THE SUITE. THIS IS THE EXPENSIVE PART AND IT IS NOW
KNOWN.** A bulk rename that does not guard all four leaves 60-152 tests red:

| trap | why it bites |
| --- | --- |
| `block=` | EVERY one is a kwarg on the deprecated `Finding.block`, never an assignment -- measured, `block = ` with spaces does not occur in the tree at all. Guarding only `block=int(` missed 33 call sites |
| `.block` as a LITERAL guard | it also swallows `.block_matches`, so the definition renames and the call sites do not. Guard it as `\\.block(?![\\w])` |
| uppercase `BLOCK` | the 0.2.x report's LINE MARKER, parsed by `FIELD = re.compile(r"^(BLOCK\|VERDICT\|...)")`. Renaming it makes every held report unreadable -- *"a record with no PARAGRAPH index"* on 173 of 173 |
| quoted `'block'` | the OPPOSITE of a wire use: all eight are count nouns for `_n(...)`, so guarding them leaves the output saying "3 blocks unaccounted". They are already done |

! **`block-context` is a ROLE NAME and is not part of this** -- a plugin agent id, a `--reviewers`
value, a filename, and the key every held report is filed under. Roy approved renaming the roles
to their editorial desks separately, `fact-check-editor` among them; that is its own scope.

! **Nothing is on the wire.** Measured 2026-08-19: the census JSON has no `block` key and neither
does a record slot. The only load-bearing uses are `Finding.block` and the `BLOCK` marker, both
the deprecated 0.2.x record index.

## Tasks

- [x] **DONE 2026-08-19 -- shipped PROSE, 285 renames across 13 files**, plus `block` retired
      from `vocabulary.toml` and the eight count nouns in `verdicts.py`'s report and the census
      listing's header and tier table. Everything a human or an agent READS says paragraph.
      ! Three stale references to the RETIRED index went with it: the brief's worked record
      opened `{ "block": 17,` (a seeded slot has no such key), it told reviewers to file two
      records *"with the same `block`"* where it is the same ADDRESS, and `SKILL.md` described a
      slot as carrying *"the census `block` index and the `address`"*.
      ! ORIGINAL: Shipped PROSE first -- 298 uses across `SKILL.md` (110), `reviewer-brief.md`
      (52), `compact.md` (43), `re-review.md` (33) and the agent files. This is
      the half that must move before `[roles] all` can say `paragraph`, because
      `check_vocabulary` refuses a role a term its own text never uses.
- [ ] Shipped CODE -- **706** uses, all internal identifiers and docstring prose. ! **READ THE
      FOUR TRAPS IN THE OBJECTIVE FIRST.** Each was found by breaking the suite, and a bulk pass
      that misses one leaves 60-152 tests red. Shipped CODE -- 721 uses. `Block` -> `Paragraph`, `pcst.py` -> the page
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
