# A docstring whose closing `"""` carries a trailing comment is owned twice

```
Status:   blocked (python-cannot-read-python -- the lexical Python reader)
Progress: 2 of 2 tasks closed
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
SPLIT:    2026-08-23 -- the remaining box carried TWO ARTIFACTS in its Verify -- the
          compositor's round-trip identity and the census's tiling -- so it is two boxes.
          Neither fits in two lines while carrying the other.
Closed:   2026-08-29 — 2026-08-29 -- BOTH VERIFIED, but by the OTHER route. Roy ruled
          2026-08-21 that this falls out of the lexical Python reader; it was fixed in
          the TOKENIZED one instead, and python-cannot-read-python is untouched.
          paragraphs_stdlib no longer returns a second paragraph for a comment on a line
          a docstring owns -- the docstring's raw_lines already set that line back
          verbatim. T1: lossless returns None for all three numpy files. T2: census over
          corpora/numpy/numpy/exceptions.py gives line 246 exactly one address, @a9. !
          The defect ALSO reached the one-line docstring form, where it was invisible:
          code_lines answered correctly by accident of sort order while the addressless
          paragraph was produced either way.
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

! **BOTH HALVES CURRENTLY FAIL**, which is what makes ticking either box an observation rather
than a judgement.

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
`3ce4e4c`. **Those three files are what T1 re-runs.**

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
**That reader is [`python-cannot-read-python`](python-cannot-read-python.md), and it is the only
thing this file waits on; the re-measurement is all this file owns.**

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

- [x] T1 | FINISHED | unknown | T1 -- Re-run `compositor.lossless` over the
      three numpy files named in the Objective once the lexical Python reader
      lands. Verify: it returns `None` for all three.
- [x] T2 | FINISHED | unknown | T2 -- Re-census
      `corpora/numpy/numpy/exceptions.py` and close this file. Verify: line 246
      carries exactly ONE address.
