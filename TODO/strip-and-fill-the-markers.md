# A role reproduces comment markers and indentation by hand, and that is where it breaks

```
Status:   decision-needed
Progress: 0 of 8 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, Roy, watching three failed edits in a row: "having the
          whole text comment marks and all is brittle and subject to breakage easily. We
          may need to rethink this and strip/fill in the comment marks ourselves else
          the agents are seeing noise and potentially creating trouble.")
Corrected: 2026-08-29 — the '#:' marker question was struck -- the comment token is '#'
           per the language row, and ':' is prose; a session had asserted a semantic the
           lexer does not implement
Measured: 2026-08-29 — the a-place indent rule: anchor+1 level is exact at 276 of 276
          over 52 real files, while the next-b it was to back up is unavailable at 62
          (22%) -- proposal is to invert them
Withdrawn: 2026-08-29 — the anchor+1 proposal is withdrawn: the 62 was a filtering
           artifact (an absent b is still a b), and anchor+1 encodes a Python-only fact
           that is wrong for languages whose doc comment sits above the declaration
Settled:  2026-08-29 — every one of the 276 a places has a following b; the last 10 were
          docstring-only __init__.py files whose b is anchored at the <eof> sentinel,
          which a text search cannot match
```

## Objective

A role is handed a paragraph's raw text **with its comment markers and its indentation**, and
must reproduce both exactly in `change`. Everything the role writes is then placed verbatim.

!! **MEASURED 2026-08-29, and the measurement is that an agent WITH FULL CONTEXT FAILED THREE
TIMES IN A ROW.** Driving the chain end to end, a session tried to make one word's edit to a
docstring and instead:

| attempt | what it did | what it looked like |
| --- | --- | --- |
| 1 | appended past the closing `"""` | **"43 of 43 docstring alterations refused"** |
| 2 | `rstrip()` pulled the closer up a line, renumbering everything below | **"39 refused"** |
| 3 | tested `raw.startswith('\"\"\"')`, missing that a declaration's docstring is INDENTED | **"2 refused"** |

! **EVERY INTERMEDIATE RESULT READ AS A DEFECT IN THE SETTER**, and none was. The correct edit
succeeds at 63 of 63 places. **The failure mode is not that the writer is careless; it is that the
format makes carelessness indistinguishable from a system fault.**

Roy: *"having the whole text comment marks and all is brittle and subject to breakage easily. We
may need to rethink this and strip/fill in the comment marks ourselves else the agents are seeing
noise and potentially creating trouble."*

## The proposal

**The system strips the markers and the indentation before a role sees the paragraph, and fills
them back when it sets one.** A role reads and writes PROSE. It never sees a `#`, a `"""`, or a
leading tab, so it cannot get them wrong.

## The indentation rules, Roy verbatim, 2026-08-29

> *"In Python the tab level for b is the b anchor tab level. For a it is the next b tab level f's
> are always 0, single line c's do not need specified and multline c's keep the anchor's tab
> level."*

| series | fills at |
| --- | --- |
| `b` | its **anchor's** tab level |
| `a` | the **next `b`'s** tab level |
| `f` | **0**, always |
| `c`, single line | not specified -- it rides the code line |
| `c`, multi-line | its **anchor's** tab level |

## What makes it safe, and it is one property

!! **`fill(strip(p)) == p`, BYTE FOR BYTE, FOR EVERY PARAGRAPH THAT DID NOT CHANGE.** That is the
whole safety argument, and it is the kind of check that CAN fail -- run over fetched corpora
rather than hand-authored fixtures. ! `docs/gates.md` records what happens otherwise: the round
trip scored **699 of 699 on its first run** while 157 addresses were held by two paragraphs each,
because it rebuilt each file from positions it had just read out of that file.

## Open -- these are RULINGS, not tasks

1. ~~**Is the marker carried, or chosen?**~~ **SETTLED, and it was never a question.** This read
   *"`#:` and `# ` mean different things here (140 lines of `#:` in `src/`)"* and **that was
   false.** Roy, 2026-08-29: *"technically ':' is part of the prose the comment tag is still `#`.
   That is what python picks up on. It doesn't care that some human or machine likes to add extra
   glyphs to indicate that this is a special comment."* ! `language.py` agrees -- Python's row is
   `line_comment = ("#",)`, and NOTHING in `reading/lexer.py` treats `#:` as anything. The 140
   hits are this repo's own source USING that style; a session read a convention off the corpus
   and asserted it as a semantic the system implements. **The token is what the language row says;
   everything after it is prose, `:` and `!!` included.**
2. **What does `a` fill at when there is no next `b`?** Roy, 2026-08-29: *"Python gives us the
   second backup for free on this and that is the docstring is in one level from the anchor
   level."*

   !! **MEASURED over `src/comment_review`, 52 files, 276 `a` places -- AND THE BACKUP BEATS THE
   PRIMARY:**

   | rule | result |
   | --- | --- |
   | docstring indent MINUS **anchor** indent | `{0: 52, 4: 224}` -- **exact at 276 of 276** |
   | `a` places with **no following `b`** | **62 (22%)** |

   The 52 zeros are exactly the 52 module docstrings, whose anchor is `<module>` at column 0;
   every one of the 224 declaration docstrings sits one level in. ! **AND THE 62 ARE NOT AN
   EXOTIC CASE.** Only 16 are module docstrings; the other **46 are declarations whose bodies
   hold no blank line and which are last in their file** -- a `b` is the SPACE BETWEEN lines of
   type, so a body of contiguous statements has none inside it. `binder/addresses.py` after `a6`
   carries `c17`-`c24` and no `b` at all, though the file has 26 `b` places earlier.

   !! **THE 62 WAS A MEASUREMENT ARTIFACT, THE THIRD OF THE SAME KIND, AND THE `next b` RULE
   STANDS.** Roy, 2026-08-29: *"Still an absent b is still a b and it still defines the answer
   more appropriately. The indent level of the next piece of code is the correct level else python
   throws a SyntaxError fit itself."*

   ! **AN ABSENT `b` CARRIES ITS ANCHOR** -- the code line it sits against -- and only lacks a
   line SPAN, because it holds no prose. Both earlier runs filtered on `original_start`, which
   discards every one of them; in `binder/addresses.py` **all 26 `b` places are absent**, so the
   filter removed the entire series. Re-measured with them placed by their anchors:

   | | |
   | --- | --- |
   | `a` places with no following `b` | **0**. It read 62, then 10, and both were the measurement |
   | docstring indent MINUS **next-b** indent | `{0: 251, -4: 7, 4: 7, 8: 1}` |

   ! The residual 15 is the re-measurement's own anchor matching finding a duplicate line, not the
   rule failing.

   !! **AND THE LAST 10 WERE THE SENTINEL.** Every one was an `__init__.py@a0` in a package file
   that holds a docstring AND NOTHING ELSE -- `desk/__init__.py` is 66 lines and the docstring is
   lines 1-66. They each carry exactly one `b`, **anchored at `<eof>`**, which a search through
   the file's own lines can never match because it is a sentinel rather than text. ! The rule
   answers correctly there too: a `b` at `<eof>` sits at column 0, which is where a module
   docstring belongs. **Every one of the 276 `a` places has a following `b`.**

   !! **AND THE DECIDING ARGUMENT IS STRUCTURAL, NOT STATISTICAL: the next code line's indent is
   ENFORCED.** Python raises `IndentationError` if it is wrong, so the rule reads a level the
   language already guarantees rather than inferring one.

   !! **THE `anchor + one level` PROPOSAL IS WITHDRAWN, because it would have LOCKED IN A PYTHON
   IDIOSYNCRASY.** Roy: *"we have to make certain that we don't lock in a Python idiosyncrasy on
   accident here."* It is exact at 276 of 276 here ONLY because Python puts the docstring INSIDE
   the block. In Rust, Go, Java and C# the doc comment sits ABOVE the declaration at the SAME
   indent -- there the next code line IS the declaration and gives the right answer, while
   `anchor + one level` indents every doc comment one level too far. **The rule as first stated
   generalizes; the proposed replacement was overfitted to the one language measured.**
3. **Scope: Python first, or every language?** The rules above are stated for Python. A lexical
   language with block comments (`/* */`) has a different shape, and `f` at column 0 is not
   obviously right for every one.
4. **Does this replace `change` as raw text, or layer under it?** `docs/the-mark.md` rules
   `change` is the updated paragraph AS RAW TEXT. Stripped prose is still raw text, but it is not
   the same bytes -- so that sentence needs to say which.

## Tasks

- [ ] T1 | Measure the brittleness before changing anything. Verify: over a real
      corpus, count how many paragraphs a naive edit to `raw_text` can make
      unparseable -- appending past a closing delimiter, moving a closer up a
      line, or missing that a docstring is indented. That number is the case for
      the change and the baseline the fill is measured against.
- [ ] T2 | Strip and fill are EXACT INVERSES for an unchanged paragraph. Verify:
      over every paragraph of every corpus file, `fill(strip(p)) == p`
      byte-for-byte. ! THIS IS THE WHOLE SAFETY ARGUMENT and it must be able to
      FAIL -- run it over fetched corpora, not hand-written fixtures, per
      `docs/gates.md`.
- [ ] T3 | The prose is EVERYTHING after the comment token, and the token is
      what the language row says it is. Verify: `#: x` strips to `: x` and fills
      back to `#: x`; `# x` strips to ` x` and fills back to `# x`. ! Stripping
      an optional space after the token is what breaks this -- `#: x` has none,
      so a fill that re-adds one writes `# : x`.
- [ ] T4 | A blank line inside a paragraph survives. Verify: a bare `#` line
      (140 in `src/`) fills back as `#` with no trailing space, and the round
      trip is byte-exact.
- [ ] T5 | The indentation rules land, per language. Verify: for Python, a `b`
      fills at its anchor's level, an `a` at the next `b`'s level, an `f` at
      column 0, a multi-line `c` at its anchor's level; a single-line `c`
      specifies none.
- [ ] T6 | Relative indentation INSIDE a paragraph is preserved. Verify: a
      docstring whose body has an indented `Args:` block round-trips with that
      inner indentation intact -- strip removes only the common leading level,
      never the structure under it.
- [ ] T7 | What the agent is shown matches what it may write. Verify: the
      `raw_text` on a seeded row is the STRIPPED prose, and a `change` written
      in that same form is accepted -- so a role never sees a delimiter it would
      have to reproduce.
- [ ] T8 | A `change` that would not parse is refused BY NAME before it reaches
      the setter. Verify: the fill is what places delimiters, so a role cannot
      produce a broken file; a paragraph that cannot be filled is a named
      refusal, never a silent skip.
