# The vocabulary gate is red, and the test that would say so does not exist

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (both reviews of 2026-08-20; verified in-session)
```

## Objective

The vocabulary gate is red, and the test that would say so does not exist.

## Tasks

- [ ] !! VERIFIED: `uv run python scripts/check_vocabulary.py` EXITS 1. Four roles
      -- `block-context`, `function-context`, `module-context`, `ownership-
      context` -- are handed the term `original`, which their own text never uses.
      `references/vocabulary.toml:128,164,201,240`. Branch-introduced: 1
      occurrence at `7850bbc`, 5 at HEAD.
- [ ] !! AND THE SUITE IS GREEN WITH THE GATE RED. `tests/test_vocabulary.py`
      asserts `check_duplicate() == 0` and `check_retired() == 0` and NEVER
      asserts `check_drift() == 0`. CLAUDE.md requires this gate after any edit to
      an agent file or a reference, and this branch edited all of them.
- [ ] ! I REPORTED THIS GATE AS PASSING THREE TIMES on 2026-08-20 -- in the commit
      messages for 5fd5baf and others -- because I piped it through `tail -2`,
      read the last line, and never checked `$?`. The commit messages are wrong
      where they say `vocabulary gate 0`.
- [ ] `check_vocabulary.py:88`'s retired-word regex uses `\w` boundaries, so
      `block_problem`, `block_text` and `as_block` -- live functions in
      `desk.py`/`lexer.py` -- are invisible to it and the gate prints a false *"0
      uses in the shipped tree"*.
