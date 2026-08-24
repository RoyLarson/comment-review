# A docstring whose closing `"""` carries a trailing comment is owned twice

```
Status:   blocked (python-cannot-read-python -- the lexical Python reader)
Progress: 0 of 1 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the compositor round trip over `corpora/`, 2026-08-21 -- one of 7
          files that lose or invent a line)
Evidence: 2026-08-22 — THE ONE FILE THAT WILL NOT ROUND TRIP IS THE ARGUMENT FOR THIS
          TODO. Roy, 2026-08-22: *"it actually is the thing that puts python in the
          lexer category. They will get lost without it. Your numpy tests prove it."*
Updated:  2026-08-23 — its own last two boxes say it needs nothing of its own, and Roy
          ruled 2026-08-21 that the numpy case falls out automatically with the Python
          branch. Blocked, not closed: deferred is not done
TRIAGED:  2026-08-23 — ALL ELEVEN BOXES WERE RECORDS -- one measurement, three
          consequences, two rulings, five arguments about the lexical reader. None could
          be ticked by anyone, so the file advertised 0 of 11 on work it does not own.
          They are ticked as the record of how the ruling was reached and moved into the
          objective. ONE TASK REMAINS and it is this file's own: the re-measurement that
          closes it. ! RE-VERIFIED LIVE the same day -- see below.
```

## Objective

A docstring whose closing `"""` carries a trailing comment is owned twice.

!! **VERIFIED LIVE 2026-08-23, not merely re-read.**
`census.py --json --repo . corpora/numpy/numpy/exceptions.py` still returns two paragraphs over
line 246:

```
corpora:numpy:numpy:exceptions.py@a9  docstring         201-246  raw_lines[-1] == '    """  # NOQA'
corpora:numpy:numpy:exceptions.py@c38 trailing-comment  246-246  raw_lines[-1] == '  # NOQA'  anchor '    """'
```

and `compositor.lossless(Path("corpora/numpy/numpy/exceptions.py"))` returns
`line invented: '    """  # NOQA'`.

**SO THE FILE COMES BACK ONE LINE LONGER.** The compositor walks the reading order and asks each
place what it holds, so line 246 is emitted twice: 247 lines in, 248 out. That is a line
INVENTED, which breaks the invariant `lossless` exists to hold -- and `lossless` is what found it.

! **IT BREAKS THE TILING**, which is the property everything else rests on: every line belongs to
exactly ONE place. Same class as the `f0`-inside-`b0` overlap fixed the same day, but between an
`a` and a `c`, and with the text stored twice rather than the range merely overlapping.

! **IT IS A `paragraphs_stdlib` DEFECT -- the PYTHON reader.** The lexical tier already cuts a
trailing comment at its opener and stores the code separately in `anchor`; the docstring path
keeps its closing line whole and lets the `c` claim the same line's comment half.

**MEASURED 2026-08-22: of 3,228 files across ten languages, exactly ONE differs** -- this one.
3 of the 7 files that failed `lossless` over 3,082 are this shape:
`numpy/numpy/exceptions.py`, `numpy/.venv/Lib/site-packages/_virtualenv.py` and
`numpy/.venv/Scripts/activate_this.py`. The other 4 are the unparsed-page case, guarded in
`3ce4e4c`.

## Which one owns it -- ANSWERED, and by the reader that does not have the seam

**RULED by Roy, 2026-08-21:** *"the numpy one will fall out automatically with the python one
because that is an artifact of using the ast to get docstrings instead of the lexer which would
ignore that."*

!! **CHECKED AT ROY'S REQUEST, AND IT DOES FALL OUT -- the first check was mine and was wrong.**
MEASURED 2026-08-21 by reading the numpy shape through `paragraphs_lexical` with `"""` as a
delimiter: ONE paragraph, `docstring` 2-5, `raw_lines[-1] == '    """  # NOQA'`, and line 5 owned
ONCE. The trailing comment RIDES ALONG on the closing line as part of the run, and no `c` place
claims it. Roy: *"it also automatically eats the # NOQA at the end of the line instead of having
to figure out how to attach those back."*

! **WHAT THE FIRST CHECK ACTUALLY FOUND was an obstacle to the lexical reader EXISTING**, not a
reason this defect survives it: Python's language row has no `"""` delimiter, and `_strip_strings`
blanks the spanning quote before the comment-opener test. Both must be answered for a lexical
Python reader -- and once one works, this defect is gone by construction rather than fixed.

!! **`"""` IS BOTH PYTHON'S STRING QUOTE AND ITS DOC DELIMITER, which is the real work in
`python-cannot-read-python` and not in this TODO.** Its row lists `('"""', "'''")` under
`spanning_quotes`, and `_strip_strings` blanks a spanning quote BEFORE the comment-opener test --
by design, so a `//` inside a string cannot open a comment. A docstring is a STRING in a
particular POSITION, and stating that position is what replaces the parser.

! **A `c` IS THE ROOM BESIDE A LINE OF CODE, and a docstring's closing `"""` is not code** -- so
`# NOQA` beside it may not be a trailing comment at all. `prove_unchanged._delimiter_shares_the_line`
(`prove_unchanged.py:79`) already refuses a paragraph-comment delimiter sharing a line with code;
this is the same shape at a docstring's closing quote and has no such guard. **The lexical answer
settles it without a guard: the run owns the whole closing line.**

## Tasks

- [ ] **T1 -- RE-MEASURE when the lexical Python reader lands, and close this file.** It is the
      only thing this TODO owns; the reader itself is
      [`python-cannot-read-python`](python-cannot-read-python.md). Verify, in this order:
      `compositor.lossless(Path("corpora/numpy/numpy/exceptions.py"))` returns `None`; the census
      of that file gives line 246 exactly ONE address; and the same holds for
      `numpy/.venv/Lib/site-packages/_virtualenv.py` and `numpy/.venv/Scripts/activate_this.py`.
      ! Both halves currently FAIL -- re-verified 2026-08-23, output in the objective -- so this
      box can fail today, which is what makes ticking it an observation.
