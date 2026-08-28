# A comment INSIDE a line makes the whole file unprovable

```
Status:   open
Progress: 2 of 7 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-17 (Roy, on the fixture for the fix that landed the same day:
          "Is this actually possible in code? int x = /* why */ 5; That is crazy
          - I have never seen someone put a comment in the middle of the
          expression")
Unblocked: 2026-08-19 — Requires-Roy cleared: the one ruling this file needed was MADE,
           and 2026-08-19 settled the rest -- an intermediate comment is not censused at
           all. The flag means a DECISION is owed; work still remaining is what the
           unchecked boxes already say.
TRIAGED:  2026-08-23 — Status was DEFERRED and the file's own text says the first task is
           NOT deferred and fires on this author's files. It is `open`, with the model
           change deferred per-task. RE-VERIFIED: `prove_unchanged` still returns
           `unprovable` with an EMPTY cause at four refusal sites. ! And the C++ corpus
           the count needs now EXISTS as a row -- `corpora/corpora.toml:289`, `llvm` --
           though it is not fetched, so T3 became actionable and stays deferred by
           choice rather than for want of a corpus.
Updated:  2026-08-28 — 2026-08-28 triage: re-verified against the current tree.
          code_fingerprint and _without_comments in
          src/comment_review/results/prove_unchanged.py still return unprovable with an
          empty-string cause at every refusal site (no language record, reader
          exception, unterminated-paragraph-comment, spanning_quotes, four line-
          placement failures, all-comment file). commands/prove_unchanged.py prints one
          generic UNPROVABLE message for all of them -- T2 and T3 (distinct causes) not
          done. corpora/corpora.toml still has no llvm files fetched, so no C++
          measurement exists -- T4-T6 remain deferred. Roy's 2026-08-28 assessment
          (pretty certain this one is closed) does not hold on this evidence; the file
          stays open as filed.
Updated:  2026-08-28 — 2026-08-28 vocabulary pass: reworded one retired-word use. 'an
          unterminated block' (Requires-Roy background) now reads 'an unterminated
          paragraph comment', matching this file's own term for the same annotation used
          twice elsewhere in the Objective (unterminated-paragraph-comment). The file's
          one other block use -- 'a block comment can also sit in the MIDDLE' -- is the
          language sense, a /* */ block comment, and was left unchanged. No task box
          affected.
```

## * RULED 2026-08-17: build it when someone needs it

Roy: *"we are going to wait for a pull request to implement it. If I am the only one that ever
uses this project that is a non-op always so why."*

**The measurement below is the argument for the ruling, not against it.** The shape is zero in
Rust, Go, Java and JS and concentrated in C-family application code; this project's author works
in Python and Rust. A model change that buys back the code check for a language nobody here
writes is cost with no reader.

!! **What is NOT deferred is saying WHY a file was refused.** `prove_unchanged` returns
`unprovable` with no cause, and that fires for THIS author today -- the `spanning_quotes`
refusal added 2026-08-17 catches any JS file holding a template literal, which is most of them.
A user cannot currently tell a mid-line comment from an unterminated paragraph comment from a
language with no record. That is the cause-reporting work below and it stands on its own.

## Objective

**The census has three positions for a comment on a line -- the whole line, a prefix, a suffix --
and a block comment can also sit in the MIDDLE.** That fourth shape cannot be split into code
and prose without losing one of them, so the lexical reader keeps the line whole and
`prove_unchanged` routes the file to `unprovable`.

That is the SAFE direction and it is deliberate: cutting at the opener drops the trailing `5;`
in `int x = /* why */ 5;`, so `5` and `7` compare equal and the proof reports PROVEN on changed
executable code. ! **Do not "fix" this by cutting.** It was written that way once and the
existing midline test caught it.

But safe is not useful. On a file carrying the shape, stage 7b's code check is unavailable and
four reviewers are handed a line of executable code as prose.

## The eight refusals, and where the cause is thrown away

MEASURED 2026-08-23: `code_fingerprint` returns `("unprovable", "")` at `prove_unchanged.py:183`
and `:188`, and the cause is thrown away at FOUR distinguishable sites inside
`_without_comments` -- no language record (`:118`), a reader exception (`:122`), an
`unterminated-paragraph-comment` annotation (`:124`), a `spanning_quotes` delimiter anywhere in
the text (`:139`) -- plus the line-placement failures at `:149`, `:154`, `:159` and the
all-comment file at `:184`.

! The `spanning_quotes` refusal catches every JS file holding a template literal, so this is
reachable today without a single line of C++.

! **ONE CLANG FILE IS NOT A MEASUREMENT OF C++.** MEASURED 2026-08-23: `corpora/corpora.toml:289`
now carries an `llvm` row and `corpora/llvm` is not fetched, so the corpus the count needs exists
as a declaration and not yet as files. The count is deferred because the model change it feeds is
deferred -- not for want of a corpus.

## It is legal everywhere, and CONVENTIONAL in one place

! Roy's objection was right about his own example and about Rust; it is the general shape that
is common, and only in C-family code. Measured 2026-08-17 over the pinned language corpus:

| file | lines with a closed `/* */` and code after it | rate |
| --- | --- | --- |
| `clang/lib/Sema/SemaDecl.cpp` | **147** of 20307 | 0.72% |
| `llvm/lib/IR/Instructions.cpp` | 4 of 4399 | 0.09% |
| `Optional.java` * `axios.js` * `option.rs` * `server.go` | **0** | 0% |

**It is a NAMED-ARGUMENT convention, and LLVM's coding standards endorse it.** C++ has
positional arguments and no named parameters, so a bare `true` at a call site is unreadable
without one:

```
TypeNameValidatorCCC CCC(/*AllowInvalid=*/true, isClassName,
MarkAnyDeclReferenced(TD->getLocation(), TD, /*OdrUse=*/false);
```

! **Rust and Go score zero for a reason, not by luck.** Rust has named struct fields and a
culture against positional booleans, so the workaround is never needed. The shape is legal
there -- `/* */` is WHITESPACE to the lexer in C, C++, Rust, Java, JS and Go, legal anywhere a
space is legal. Verified rather than assumed: official `rustc` stable compiled and ran
`let x = /* why */ 5;`, and `node v24.11.1` ran the JS equivalent. `SemaDecl.cpp` is Clang's own
source, so C++ settles itself.

**So the cost is concentrated in one language family and absent from the rest** -- which is why
the ruling above defers it. A C++ repository loses the code check entirely; a Rust one never
notices, and nobody writing C++ uses this yet. ! The concentration is the whole finding: read
it as a map of who would be hurt, and by that map nobody currently is.

## Why it is a model change, not a patch

A paragraph records `start`, `end` and `raw_lines`, and every consumer assumes it OWNS the
lines it spans, minus the two edges already handled:

| position | how it is represented today |
| --- | --- |
| whole line | the line is in the paragraph, out of `code_lines` |
| suffix (`x = 1; // note`) | `trailing-comment`; the line stays code |
| prefix (`/* note */ x = 1;`) | stored from `original_column`; the first line stays code |
| **interior** | **no representation** -- the line is kept whole and refused |

An interior comment needs a paragraph that names a SPAN WITHIN a line, and then `code_lines`,
`intervals`, `as_block` and `_without_comments` all have to agree about a line that is partly
each. ! `prove_unchanged` is the one that must not be got wrong: its whole claim is that
executable code is byte-identical.

!! **THE SPAN AND ITS TWO READERS MUST LAND IN ONE COMMIT.** They are the halves of the same
claim, and 2026-08-17 has two separate measurements of what happens when one half moves alone.
They are two boxes because a stranger ticks them separately, not because they may ship apart.

! **The four shapes are pinned by two test classes** -- `TestABlockCommentBesideCode`
(`tests/test_census_blocks.py:1231`) and `TestTheProofFollowsTheBlocks` (`:1293`), verified
present 2026-08-23. They are what caught the cut-at-the-opener fail-open, and an interior-comment
change touches exactly that code, so the model change is verified against them rather than
around them. ! Keeping the four shapes pinned is a standing constraint, true the day it was
written and every day after -- it is not work anyone ticks, and it now sits inside those
verifications, where it can be checked.

## Tasks

- [x] T1 -- RULED 2026-08-17: wait for a pull request. The ruling is above, and there is
      no state in which someone ticks it again.
- [ ] T2 -- Print a DIFFERENT named cause at each of the eight refusal sites listed in the
      Objective. Verify: the eight causes are distinct, and none is the empty string.
- [ ] T3 -- Assert the causes the CLI can reach. Verify: a test asserts the four reachable
      causes named in the Objective, and fails if any two are the same.
- [ ] T4 -- DEFERRED. Count the shape across the corpora before building anything. Verify:
      a per-language rate of a closed `/* */` with code after it, over the corpus.
- [ ] T5 -- DEFERRED, only if the model moves: give a paragraph a COLUMN SPAN. Verify: a
      paragraph names a span WITHIN a line, and both pinned test classes pass unweakened.
- [ ] T6 -- DEFERRED, and in T5's commit: make `code_lines` and `_without_comments` read
      the span. Verify: `int x = /* why */ 5;` changed to `7` reports NOT PROVEN.
- [x] T7 -- NOT A TASK. Keeping the four existing shapes pinned is a standing constraint;
      it now sits inside T5's and T6's verifications. In the Objective.
## Related

- [`block-comment-markers-survive-into-the-prose`](block-comment-markers-survive-into-the-prose.md)
  -- the other defect the language corpus found, in the same `/* */` family.
