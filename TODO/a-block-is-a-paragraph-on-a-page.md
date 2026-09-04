# A block is a paragraph and a pCST is a page -- the rename the vocabulary already made

```
Status:   in-progress
Progress: 3 of 11 tasks closed
Owner:    backend
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
Ruled:    2026-08-20 — pCST -> page is settled and GATED, 2026-08-20. Roy: 'it never
          really fit -- using libcst in python made it easy to move and edit comments
          and so I thought that was what this was. It isn't.' The shipped tree, README,
          CLAUDE.md and the live docs no longer say it; `check_vocabulary.RETIRED` now
          holds 'pcst' alongside 'block'.
TRIAGED:  2026-08-23 — Status was `blocked` and its own header said nothing blocks it;
          it is `in-progress`. THREE of five are done, and the vocabulary task with
          them: `docs/vocabulary.md:20` carries the retired row and
          `references/vocabulary.toml` defines only `paragraph` and the ROLE NAME
          `block-context`. RE-MEASURED, and the two open counts were both stale -- see
          the objective.
Split:    2026-08-23 -- every box cut to two lines. The tests box was four files and the
          live-docs box three, so five boxes became ten. Second pass: the file-rename box
          held a rename and a path sweep, so ten became eleven
```

## Objective

!! **THE VOCABULARY AND EVERYTHING A HUMAN OR AN AGENT READS ALREADY SAY PARAGRAPH.** Done
2026-08-19: 285 renames across 13 shipped prose files, `block` retired from `vocabulary.toml`, the
eight count nouns in `verdicts.py`'s report, and the census listing's own header and tier table.
Done since: the shipped CODE, where `Block` is `Paragraph` and the two readers are
`paragraphs_stdlib` (`lexer.py:1699`) and `paragraphs_lexical` (`lexer.py:984`).
**What remains is the TESTS and the LIVE DOCS.**

! **Three stale references to the RETIRED index went with the prose pass**: the brief's worked
record opened `{ "block": 17,` (a seeded slot has no such key), it told reviewers to file two
records *"with the same `block`"* where it is the same ADDRESS, and `SKILL.md` described a slot
as carrying *"the census `block` index and the `address`"*.

!! **RE-MEASURED 2026-08-23**, `grep -oi block <files> | wc -l`, which counts every sense:

| where | uses | what they are |
| --- | ---: | --- |
| shipped CODE | 68 | ! NOT the retired noun. `block_comment` / `doc_block` (`language.py`), `block_text` / `as_block` / `block_problem`, and the `BLOCK` record marker -- the four senses declared in `check_vocabulary.NOT_THE_TERM` in `d8ccef3` |
| shipped prose | 14 | `block-context`, the role name |
| tests | **205** | `test_verdicts.py` 117, `test_census_blocks.py` 34 -- and that file is NAMED for the word |
| live `docs/` | **34** | `addressing.md` 16, `parsing.md` 15, `limitations.md` 3 |
| `docs/history.md`, `docs/vocabulary.md` | 7 | the RECORD and the retired-terms table. Leave both |
| `docs/superpowers/`, `docs/plans/` | 426 | dated design records. Leave |

!! **LEAVE `docs/history.md`, `docs/vocabulary.md`'s retired table, and the 426 uses under
`docs/superpowers/` and `docs/plans/`**: those are a RECORD of what was decided then, and
correcting them stops it being one.

! **`docs/limitations.md` is the `agents` lane's file**, so its 3 uses are a crossing to name
and ask about rather than an edit in passing.

!! **ONLY THE NOUN WAS RETIRED, and forgetting that corrupted live prose once.** `d8ccef3`:
the VERB, a PYTHON code block and a JAVA TEXT BLOCK are current English and current terms of art.
Undeclared, the gate flagged all four and the cheapest way to satisfy it was to make the prose
wrong -- `SKILL.md:68` read *"it PARAGRAPHS every other verdict"*, and `prove_unchanged.py`
described *"a Java text PARAGRAPH"*, a language feature that does not exist under that name.
**Any pass over the tests or the docs must leave those four senses alone.**

!! **FOUR TRAPS, EACH FOUND BY BREAKING THE SUITE. THIS IS THE EXPENSIVE PART AND IT IS NOW
KNOWN. READ THEM BEFORE ANY OF THE PASSES BELOW.** A bulk rename that does not guard all four
leaves 60-152 tests red:

| trap | why it bites |
| --- | --- |
| `block=` | EVERY one is a kwarg on the deprecated `Finding.block`, never an assignment -- measured, `block = ` with spaces does not occur in the tree at all. Guarding only `block=int(` missed 33 call sites |
| `.block` as a LITERAL guard | it also swallows `.block_matches`, so the definition renames and the call sites do not. Guard it as `\.block(?![\w])` |
| uppercase `BLOCK` | the 0.2.x report's LINE MARKER, parsed by `FIELD = re.compile(r"^(BLOCK\|VERDICT\|...)")`. Renaming it makes every held report unreadable -- *"a record with no PARAGRAPH index"* on 173 of 173 |
| quoted `'block'` | the OPPOSITE of a wire use: all eight are count nouns for `_n(...)`, so guarding them leaves the output saying "3 blocks unaccounted". They are already done |

! **`block-context` is a ROLE NAME and is not part of this** -- a plugin agent id, a `--reviewers`
value, a filename, and the key every held report is filed under. Roy approved renaming the roles
to their editorial desks separately, `fact-check-editor` among them; that is its own scope.

! **Nothing is on the wire.** Measured 2026-08-19: the census JSON has no `block` key and neither
does a record slot. The only load-bearing uses are `Finding.block` and the `BLOCK` marker, both
the deprecated 0.2.x record index.

! **THE REASON IS RECORDED AT `docs/vocabulary.md:20`** -- *"`block` -> paragraph. The register is
EDITORIAL ... Its definition -- the interval between two lines of CODE -- is also untrue of a
prose file"* -- with `pCST` beside it at `:23`.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- DONE 2026-08-19: shipped PROSE, 285
      renames across 13 files, plus the three stale references to the retired
      index. What went with it is in the Objective.
- [x] T2 | FINISHED | unknown | T2 -- DONE: shipped CODE -- `Block` ->
      `Paragraph`, `pcst.py` -> the page module, both readers renamed. VERIFIED
      2026-08-23: the 68 hits are the four live senses.
- [ ] T3 | T3 -- **`tests/test_verdicts.py` -- 117 uses.** Verify: `grep -oi
      block` over it returns only the declared live senses, and `uv run pytest
      -q` is green.
- [ ] T4 | T4 -- **`tests/test_census_blocks.py` -- 34 uses.** Verify: `grep -oi
      block` over it returns only the declared live senses, and `uv run pytest
      -q` is green.
- [ ] T5 | T5 -- **Rename the file `tests/test_census_blocks.py`.** Verify: `uv
      run python -m unittest discover -s tests` collects the same case count as
      before.
- [ ] T6 | T6 -- Sweep the retired noun out of every path under `tests/`.
      Verify: `git ls-files tests/ \| grep -i block` returns nothing.
- [ ] T7 | T7 -- **The remaining nine test files -- 54 uses.** Verify: `grep
      -oil block tests/` returns nothing but the declared live senses, and `uv
      run pytest -q` is green.
- [ ] T8 | T8 -- **`docs/addressing.md` -- 16 uses.** Verify: the file holds no
      use of the retired NOUN, and `uv run python scripts/check_vocabulary.py`
      exits 0.
- [ ] T9 | T9 -- **`docs/parsing.md` -- 15 uses.** Verify: the file holds no use
      of the retired NOUN, and `uv run python scripts/check_vocabulary.py` exits
      0.
- [ ] T10 | T10 -- **`docs/limitations.md` -- 3 uses.** Verify: the file holds
      no use of the retired NOUN, and `uv run python
      scripts/check_vocabulary.py` exits 0.
- [x] T11 | FINISHED | unknown | T11 -- DONE: `block` is retired. VERIFIED
      2026-08-23 -- `vocabulary.toml` defines `paragraph` and the role name
      only; `docs/vocabulary.md:20` carries the retired row.
