# A role reproduces comment markers and indentation by hand, and that is where it breaks

```
Status:   decision-needed
Progress: 0 of 8 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-29 (2026-08-29, Roy, watching three failed edits in a row: "having the
          whole text comment marks and all is brittle and subject to breakage easily. We
          may need to rethink this and strip/fill in the comment marks ourselves else
          the agents are seeing noise and potentially creating trouble.")
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

1. **Is the marker carried, or chosen?** `#:` and `# ` mean different things here (140 lines of
   `#:` in `src/`). If fill re-derives the marker, a `#:` silently becomes a `#`. Carrying it as a
   property of the paragraph seems right, but it means a role cannot CHANGE a marker -- which
   forecloses a legitimate edit.
2. **What does `a` fill at when there is no next `b`?** A declaration whose body is only its
   docstring has no following `b`, so the rule has no value to read.
3. **Scope: Python first, or every language?** The rules above are stated for Python. A lexical
   language with block comments (`/* */`) has a different shape, and `f` at column 0 is not
   obviously right for every one.
4. **Does this replace `change` as raw text, or layer under it?** `docs/the-mark.md` rules
   `change` is the updated paragraph AS RAW TEXT. Stripped prose is still raw text, but it is not
   the same bytes -- so that sentence needs to say which.

## Tasks

- [ ] Measure the brittleness before changing anything. Verify: over a real
      corpus, count how many paragraphs a naive edit to `raw_text` can make
      unparseable -- appending past a closing delimiter, moving a closer up a
      line, or missing that a docstring is indented. That number is the case for
      the change and the baseline the fill is measured against.
- [ ] Strip and fill are EXACT INVERSES for an unchanged paragraph. Verify: over
      every paragraph of every corpus file, `fill(strip(p)) == p` byte-for-byte. !
      THIS IS THE WHOLE SAFETY ARGUMENT and it must be able to FAIL -- run it over
      fetched corpora, not hand-written fixtures, per `docs/gates.md`.
- [ ] The marker is carried, never re-derived. Verify: a `#:` paragraph fills back
      as `#:` and not as `# ` -- 140 lines in `src/` alone, and the two mean
      different things.
- [ ] A blank line inside a paragraph survives. Verify: a bare `#` line (140 in
      `src/`) fills back as `#` with no trailing space, and the round trip is
      byte-exact.
- [ ] The indentation rules land, per language. Verify: for Python, a `b` fills at
      its anchor's level, an `a` at the next `b`'s level, an `f` at column 0, a
      multi-line `c` at its anchor's level; a single-line `c` specifies none.
- [ ] Relative indentation INSIDE a paragraph is preserved. Verify: a docstring
      whose body has an indented `Args:` block round-trips with that inner
      indentation intact -- strip removes only the common leading level, never the
      structure under it.
- [ ] What the agent is shown matches what it may write. Verify: the `raw_text` on
      a seeded row is the STRIPPED prose, and a `change` written in that same form
      is accepted -- so a role never sees a delimiter it would have to reproduce.
- [ ] A `change` that would not parse is refused BY NAME before it reaches the
      setter. Verify: the fill is what places delimiters, so a role cannot produce
      a broken file; a paragraph that cannot be filled is a named refusal, never a
      silent skip.
