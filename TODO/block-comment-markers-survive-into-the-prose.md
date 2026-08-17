# Block-comment markers survive into the prose the reviewers read

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Raised:   2026-08-17 (Roy: "use the github api to find a heavily documented file
          for each of the languages so we can verify that the lexers work for the
          11 languages we claim")
```

## Objective

**`_join` strips a language's LINE comment openers and nothing else, so `/*`, `*/` and the
per-line `*` of a Javadoc or JSDoc block reach the reviewers as prose.**

Measured on eleven files, one per language record, each fetched at a pinned tag:

```
c-family   docstring   '/** * A container object which may or may not contain a non-{@code'
js-family  docstring   '/** * Create a new instance of Axios * * @param {Object} instanceC'
c-family   comment     '/* * Copyright (c) 2012, 2022, Oracle and/or its affiliates. All r'
```

| | prose blocks | carrying a block marker |
| --- | --- | --- |
| **c-family** (`.java` sample) | 25 | **24** |
| **js-family** (`.js` sample) | 13 | **5** |
| rust · go · ruby | 490 | 6 |
| lua · shell · sql · toml-ini · yaml · python | 284 | 0 |
| **total** | **812** | **36** |

⚠⚠ **Read the concentration, not the total.** 4% of all blocks, and **96% of the c-family
ones** — Javadoc and JSDoc are the dominant doc styles across `.java .cs .swift .kt .cpp .ts
.tsx .jsx`, which is the largest group of extensions this system claims.

## Why it is `_join`, not the scanner

`census.py:272` builds the openers it strips from `lang.line_comment` alone:

```python
openers = tuple(sorted(lang.line_comment, key=len, reverse=True))
...
text=_join(raw, openers)
```

**Seven language records declare a `block_comment` pair and one is never stripped:**
rust, go, c-family, js-family, sql `/* */`; ruby `=begin/=end`; lua `--[[ ]]`. The scanner
FINDS these runs correctly — the blocks and their line ranges are right — and only the prose
extraction leaves the markers in.

⚠ The continuation `*` is the larger half. A Javadoc block is `/**` once and ` * ` on every
line after it, so a 20-line doc comment reaches a reviewer with twenty asterisks in the middle
of its sentences.

## What it costs

- **The reviewers read it.** The prose IS the census `text`; four roles rule on that string.
- **Stage 3 resolves against it.** `annotate.py` matches paths, symbols and counts in this text,
  so a marker sits inside phrases the annotation regexes scan.
- **A transcription has to reproduce it.** `BLOCK` carries the block's original and
  `address_problem` compares it to `text`, so a reviewer must copy the asterisks back in.
  ⚠ It does round-trip today -- `block_text` reproduces the census exactly, 812 of 812 -- so
  this is a QUALITY defect, not a refusal. Fixing `_join` without fixing both sides would turn
  it into one.

## The corpus, so the measurement is re-runnable

One heavily-documented file per record, each at a pinned tag:

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

## Tasks

- [ ] **Strip `block_comment` and `doc_block` openers, their closers, and the continuation
      marker.** ⚠ The continuation is the part a naive fix misses: stripping `/**` and `*/`
      still leaves a ` * ` on every interior line.

- [ ] ⚠⚠ **Change `_join` and `block_text` in ONE commit, and re-run the round-trip.** They are
      the two halves of the block protocol and they agree today. A fix to one alone refuses
      every c-family and js-family block instead of merely polluting it -- which is the exact
      shape of the defect that refused 73% of a run on 2026-08-17.

- [ ] **Add these eleven files to `corpora/corpora.toml`** as a `public` corpus, so the lexer
      claim has a fixture instead of a one-off measurement. ⚠ Corpora are FETCHED, never
      vendored; every ref above is a tag, so the fetch is reproducible.

- [ ] **Make the round-trip a test over that corpus**, per language. The in-tree version covers
      Python only, which is the one language that cannot exercise a block comment.

- [ ] ⚠ Decide whether a `=begin`/`=end` Ruby block and a `--[[ ]]` Lua block are worth the same
      treatment. Both are declared and neither appeared in the sampled files, so the measurement
      says nothing about them -- and an unmeasured fix is how this defect got here.

## Related

- [`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md) — the other half of "what this
  system can actually read".
