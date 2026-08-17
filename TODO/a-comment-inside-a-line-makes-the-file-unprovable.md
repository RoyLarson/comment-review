# A comment INSIDE a line makes the whole file unprovable

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session · Roy (⭐ 1 ruling wanted — task 1)
Raised:   2026-08-17 (Roy, on the fixture for the fix that landed the same day:
          "Is this actually possible in code? int x = /* why */ 5; That is crazy
          - I have never seen someone put a comment in the middle of the
          expression")
```

## Objective

**The census has three positions for a comment on a line — the whole line, a prefix, a suffix —
and a block comment can also sit in the MIDDLE.** That fourth shape cannot be split into code
and prose without losing one of them, so `blocks_lexical` keeps the line whole and
`prove_unchanged` routes the file to `unprovable`.

That is the SAFE direction and it is deliberate: cutting at the opener drops the trailing `5;`
in `int x = /* why */ 5;`, so `5` and `7` compare equal and the proof reports PROVEN on changed
executable code. ⚠ **Do not "fix" this by cutting.** It was written that way once and the
existing midline test caught it.

But safe is not useful. On a file carrying the shape, stage 7b's code check is unavailable and
four reviewers are handed a line of executable code as prose.

## It is legal everywhere, and CONVENTIONAL in one place

⚠ Roy's objection was right about his own example and about Rust; it is the general shape that
is common, and only in C-family code. Measured 2026-08-17 over the pinned language corpus:

| file | lines with a closed `/* */` and code after it | rate |
| --- | --- | --- |
| `clang/lib/Sema/SemaDecl.cpp` | **147** of 20307 | 0.72% |
| `llvm/lib/IR/Instructions.cpp` | 4 of 4399 | 0.09% |
| `Optional.java` · `axios.js` · `option.rs` · `server.go` | **0** | 0% |

**It is a NAMED-ARGUMENT convention, and LLVM's coding standards endorse it.** C++ has
positional arguments and no named parameters, so a bare `true` at a call site is unreadable
without one:

```
TypeNameValidatorCCC CCC(/*AllowInvalid=*/true, isClassName,
MarkAnyDeclReferenced(TD->getLocation(), TD, /*OdrUse=*/false);
```

⚠ **Rust and Go score zero for a reason, not by luck.** Rust has named struct fields and a
culture against positional booleans, so the workaround is never needed. The shape is legal
there — `/* */` is WHITESPACE to the lexer in C, C++, Rust, Java, JS and Go, legal anywhere a
space is legal. Verified rather than assumed: official `rustc` stable compiled and ran
`let x = /* why */ 5;`, and `node v24.11.1` ran the JS equivalent. `SemaDecl.cpp` is Clang's own
source, so C++ settles itself.

**So the cost is concentrated in one language family and absent from the rest** — which is the
argument for fixing it rather than accepting the refusal. A C++ repository loses the code check
entirely; a Rust one never notices.

## Why it is a model change, not a patch

`Block` records `start`, `end` and `raw_lines`, and every consumer assumes a block OWNS the
lines it spans, minus the two edges already handled:

| position | how it is represented today |
| --- | --- |
| whole line | the line is in the block, out of `code_lines` |
| suffix (`x = 1; // note`) | `trailing-comment`; the line stays code |
| prefix (`/* note */ x = 1;`) | stored from the opener; the first line stays code |
| **interior** | **no representation** — the line is kept whole and refused |

An interior comment needs a block that names a SPAN WITHIN a line, and then `code_lines`,
`intervals`, `as_block` and `_without_comments` all have to agree about a line that is partly
each. ⚠ `prove_unchanged` is the one that must not be got wrong: its whole claim is that
executable code is byte-identical.

## Tasks

- [ ] ⭐ **RULE on whether this is worth the model change.** It buys the code check back for
      C-family repositories and nothing for the other seven languages. ⚠ The alternative is
      honest and cheap: keep refusing, and say in the run's report WHY a file was unprovable, so
      a C++ user is told rather than left wondering.

- [ ] **Report the reason today, whatever is decided above.** `prove_unchanged` returns
      `unprovable` with no cause, so a user cannot tell a mid-line comment from an unterminated
      block from a language with no record. That is a one-line change and it is worth having
      even if the model never moves.

- [ ] **Count the shape across the corpora before building anything.** One Clang file is not a
      measurement of C++. `corpora.toml` is where a real sample lives, and the eleven-language
      corpus in
      [`block-comment-markers-survive-into-the-prose`](block-comment-markers-survive-into-the-prose.md)
      is the start of one.

- [ ] **If the model moves: give `Block` a column span, and make `code_lines` and
      `_without_comments` read it.** ⚠ Those two must be changed in ONE commit — they are the
      halves of the same claim, and 2026-08-17 has two separate measurements of what happens
      when one half moves alone.

- [ ] ⚠ **Keep the four existing shapes pinned.** `TestABlockCommentBesideCode` and
      `TestTheProofFollowsTheBlocks` in `tests/test_census_blocks.py` are what caught the
      cut-at-the-opener fail-open, and an interior-comment change touches exactly that code.

## Related

- [`block-comment-markers-survive-into-the-prose`](block-comment-markers-survive-into-the-prose.md)
  — the other defect the language corpus found, in the same `/* */` family.
