# Block-comment markers survive into the prose the reviewers read

```
Status:   open
Progress: 0 of 10 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-17 (Roy: "use the github api to find a heavily documented file
          for each of the languages so we can verify that the lexers work for the
          11 languages we claim")
Renamed:  2026-08-20 -- the language rows measured here were SPLIT, so the names in the
          tables below no longer resolve. `c-family` became `c`, `cpp`, `java`,
          `csharp`, `swift` and `kotlin`; `js-family` became `javascript` and
          `typescript`. The measurements stand as taken -- the `.java` sample is now the
          `java` row and the `.js` sample the `javascript` row.
TRIAGED:  2026-08-23 -- NOTHING TO RECLASSIFY -- all six boxes are verifiable tasks, and
          the defect was RE-MEASURED live today (see the Objective). ! Kept open and
          noted here because the staleness sweep ranked this file second-highest on
          retired-word count, which was a FALSE POSITIVE: every "block" in it is the
          LANGUAGE sense, a block comment, and not the retired noun. The file is about
          /* */ reaching reviewers as prose.
Moved:    2026-08-23 -- the two halves left `census.py` for `lexer.py` in the lexer/page
          split, so the line citations are restated: `_join` is `lexer.py:532`,
          `block_text` is `lexer.py:609`, and the openers are built at `lexer.py:999`
          and passed at `:1145`. The code is unchanged.
Split:    2026-08-23 -- 6 boxes became 10. The stripping box held the opener and the
          continuation; the fixture box held a source rule and a missing fixture; the
          last box held two languages, which this repo never allows in one row.
Updated:  2026-08-28 — 2026-08-28 triage: re-verified live. paragraphs_lexical
          (src/comment_review/reading/lexer.py) on a Java-like fixture with a Javadoc
          block and a plain block comment still returns paragraph text carrying the
          block markers and the interior asterisk on each continuation line -- e.g. a
          docstring text of '/** * Small arithmetic helpers. * @param a the first
          operand */'. lexer.py builds the openers passed to _join from
          lang.line_comment alone (openers = tuple(sorted(lang.line_comment, key=len,
          reverse=True))); block_comment openers are never stripped there or anywhere
          else in the file. None of T1-T10 are done: corpora/corpora.toml carries no
          entry for any of the eleven pinned files (option.rs, axios, Optional.java,
          etc). Roy's 2026-08-28 assessment (certainly not true anymore) does not hold;
          the defect measured 2026-08-17 is still present today at the census-reading
          stage, upstream of the galley and compositor. Stays open as filed, 0 of 10.
Updated:  2026-08-28 — tests/test_reading.py now carries
          test_a_block_comment_reaches_the_page_WITHOUT_its_markers, xfail(strict=True),
          asserting the WANTED behaviour on an invented Java Javadoc snippet -- the
          census text a reviewer reads should carry no /**, no */ and no leading
          interior * on a continuation line. Stays xfail until T1 and T2 land.
          Strictness proved live: with _join changed to also strip block markers and the
          interior *, the test XPASSes as a FAILURE under strict; the source change was
          reverted after.
```

## Objective

**`_join` strips a language's LINE comment openers and nothing else, so `/*`, `*/` and the
per-line `*` of a Javadoc or JSDoc block reach the reviewers as prose.**

Measured on eleven files, one per language record, each fetched at a pinned tag.

!! **RE-MEASURED 2026-08-23, in-tree.** `lexer.paragraphs_lexical` on
`tests/fixtures/sample.java` returns two `docstring` paragraphs whose `text` is
`'/** Small arithmetic helpers. */'` and `'/** Returns the sum of a and b. */'` -- markers and
all. ! And the fixture does NOT exercise the expensive half: it has no multi-line Javadoc, so
the continuation `*` never appears in it. A fixture can resemble its language without testing
the shape the defect needs.

! **The examples below are INVENTED**, per `docs/limitations.md`, and they are the shape the
measurement found rather than a quotation from it. The sources are third-party code under their
own licences; nothing from them is reproduced here or vendored anywhere in this repo.

```
c-family   docstring   '/** * The retry budget. * * @param verb the idempotent verb * @re'
js-family  docstring   '/** * Build a client. * * @param {Object} config the caller optio'
c-family   comment     '/* * Ownership: the scheduler owns this queue once start() returns'
```

| | prose blocks | carrying a block marker |
| --- | --- | --- |
| **c-family** (`.java` sample) | 25 | **24** |
| **js-family** (`.js` sample) | 13 | **5** |
| rust * go * ruby | 490 | 6 |
| lua * shell * sql * toml-ini * yaml * python | 284 | 0 |
| **total** | **812** | **36** |

!! **Read the concentration, not the total.** 4% of all blocks, and **96% of the c-family
ones** -- Javadoc and JSDoc are the dominant doc styles across `.java .cs .swift .kt .cpp .ts
.tsx .jsx`, which is the largest group of extensions this system claims.

## Why it is `_join`, not the scanner

`lexer.py:999` builds the openers it strips from `lang.line_comment` alone:

```python
openers = tuple(sorted(lang.line_comment, key=len, reverse=True))
...
text=_join(raw, openers)
```

**Seven language records declare a `block_comment` pair and one is never stripped:**
rust, go, c-family, js-family, sql `/* */`; ruby `=begin/=end`; lua `--[[ ]]`. The scanner
FINDS these runs correctly -- the blocks and their line ranges are right -- and only the prose
extraction leaves the markers in.

! The continuation `*` is the larger half, and it is the part a naive fix misses: a Javadoc
block is `/**` once and ` * ` on every line after it, so stripping the opener and closer still
leaves a 20-line doc comment reaching a reviewer with twenty asterisks in the middle of its
sentences.

! **AND THE CODE ALREADY SAYS SO.** `block_text`'s own `Args:` (`lexer.py:630-633`) reads: *"The
language's LINE comments only, because that is what the census passed -- a set that also
stripped `/**` would produce prose the census never stored."* That sentence is the reason the
two halves must move together.

## Why the two halves move in one commit

`_join` (`lexer.py:532`) and `block_text` (`lexer.py:609`) are the two halves of the block
protocol and they agree today. **A fix to one alone refuses every c-family and js-family block
instead of merely polluting it** -- which is the exact shape of the defect that refused 73% of a
run on 2026-08-17.

## What it costs

- **The reviewers read it.** The prose IS the census `text`; four roles rule on that string.
- **Stage 3 resolves against it.** `annotate.py` matches paths, symbols and counts in this text,
  so a marker sits inside phrases the annotation regexes scan.
- **A transcription has to reproduce it.** `BLOCK` carries the block's original and
  `address_problem` compares it to `text`, so a reviewer must copy the asterisks back in.
  ! It does round-trip today -- `block_text` reproduces the census exactly, 812 of 812 -- so
  this is a QUALITY defect, not a refusal. Fixing `_join` without fixing both sides would turn
  it into one.

## The corpus, so the measurement is re-runnable

!! **CITED, never copied.** Each row is a third-party file under its own licence -- GPL+CPE,
BSD, MIT, Apache, the PostgreSQL licence. **None is vendored, and none may be**: the files were
fetched into a scratch directory outside this repo, read by the census, and left there. What is
recorded below is the ADDRESS, which is a fact about where to look, not their text.

! This is why `corpora/` fetches and never vendors, and the reason is not only tree size. The
manifest names a repository and a ref; the fetch is the reader's, on their machine, under the
upstream licence. Adding these eleven there keeps that property -- pasting them into `tests/`
would not. Every ref below is a tag, so the fetch is reproducible.

! **The corpus and the unit fixtures answer different questions, from different sources.** The
corpus answers *does this hold on real code*; a unit test asserting an exact string would paste
third-party prose into `tests/`, which `docs/limitations.md` already forbids for its own reason.
! And a test that fails for want of a third-party checkout is a test that gets deleted, which is
why the corpus test skips rather than fails when nothing has been fetched. ! The in-tree round
trip covers Python only -- the one language that cannot exercise a block comment at all.

One heavily-documented file per record, each at a pinned tag. ! None of them is in
`corpora/corpora.toml` today -- MEASURED 2026-08-23, 18 `[[corpus]]` entries and no hit for
`option.rs`, `Optional.java`, `axios`, `create_table.sql` or `git-sh-setup`.

| record | source |
| --- | --- |
| python | this repo's own `scripts/repo.py` |
| rust | `rust-lang/rust@1.83.0` `library/core/src/option.rs` |
| go | `golang/go@go1.23.0` `src/net/http/server.go` |
| c-family | `openjdk/jdk@jdk-21+35` `src/java.base/share/classes/java/util/Optional.java` |
| js-family | `axios/axios@v1.7.7` `lib/core/Axios.js` |
| ruby | `ruby/ruby@v3_3_0` `lib/set.rb` |
| shell | `git/git@v2.47.0` `git-sh-setup.sh` |
| sql | `postgres/postgres@REL_17_0` `src/test/regress/sql/create_table.sql` |
| lua | `neovim/neovim@v0.10.2` `runtime/lua/vim/_editor.lua` |
| toml-ini | `rust-lang/cargo@0.83.0` `Cargo.toml` |
| yaml | `actions/checkout@v4.2.2` `.github/workflows/test.yml` |

## Why Ruby and Lua are decided separately

Both declare a block form -- `=begin`/`=end` and `--[[ ]]` -- and **neither appeared in the
sampled files**, so the measurement says nothing about them. ! An unmeasured fix is how this
defect got here, and this repo's rule is that a language row takes its definition from its own
grammar and never from a neighbour's, so the two are decided one at a time.

## Tasks

- [ ] T1 -- Strip the `block_comment` and `doc_block` opener and closer in `_join`.
      Verify: a `.java` docstring's census `text` holds no `/**` and no `*/`.
- [ ] T2 -- Strip the interior continuation marker as well. Verify: a multi-line Javadoc's
      census `text` carries no leading `*` on any line after the first.
- [ ] T3 -- Change `block_text` (`lexer.py:609`) in the SAME commit as each `_join`
      change. Verify: the round trip is green on that commit.
- [ ] T4 -- Add the eleven pinned files above to `corpora/corpora.toml` as a `public`
      corpus. Verify: `fetch_corpora.py` materialises all eleven.
- [ ] T5 -- Make the round trip a test over that corpus, one case per language record.
      Verify: it fails while a marker survives into `text` and passes once T1 to T3 land.
- [ ] T6 -- Make that test SKIP when the corpus has not been fetched. Verify: with the
      corpus directory absent, `uv run pytest -q` reports a skip and no failure.
- [ ] T7 -- Write the unit fixtures for the fix from INVENTED text, not from the corpus.
      Verify: no assertion under `tests/` quotes a line from any file in the table above.
- [ ] T8 -- Add a multi-line Javadoc to `tests/fixtures/sample.java`. Verify: the fixture
      carries a continuation `*` on three or more lines.
- [ ] T9 -- Decide whether a Ruby `=begin`/`=end` block gets the same stripping. Verify:
      the answer and its measurement are written into this file.
- [ ] T10 -- Decide the same for a Lua `--[[ ]]` block, from Lua's own grammar and not
      Ruby's. Verify: the answer and its measurement are written into this file.
## Related

- [`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md) -- the other half of "what this
  system can actually read".
