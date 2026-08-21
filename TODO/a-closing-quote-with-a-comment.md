# A docstring whose closing `"""` carries a trailing comment is owned twice

```
Status:   open
Progress: 0 of 11 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the compositor round trip over `corpora/`, 2026-08-21 -- one of 7
          files that lose or invent a line)
```

## Objective

A docstring whose closing `"""` carries a trailing comment is owned twice.

## Tasks

- [ ] !! MEASURED 2026-08-21 on `corpora/numpy/numpy/exceptions.py`, whose line
      246 is `    """  # NOQA`. TWO paragraphs own it and BOTH store its text: the
      docstring `a9` covers 201-246 with `raw_lines[-1] == '    """  # NOQA'` --
      the whole line -- and `c38` covers 246-246 at column 8 with `raw_lines[-1]
      == '  # NOQA'` and `anchor == '    """'`.
- [ ] !! SO THE FILE COMES BACK ONE LINE LONGER. The compositor walks the reading
      order and asks each place what it holds, so line 246 is emitted twice: 247
      lines in, 248 out. That is a line INVENTED, which breaks the invariant
      `lossless` exists to hold -- and `lossless` is what found it.
- [ ] ! IT BREAKS THE TILING, which is the property everything else rests on:
      every line belongs to exactly ONE place. Same class as the `f0`-inside-`b0`
      overlap fixed the same day, but between an `a` and a `c`, and with the text
      stored twice rather than the range merely overlapping.
- [ ] ! IT IS A `paragraphs_stdlib` DEFECT -- the PYTHON reader. The lexical tier
      already cuts a trailing comment at its opener and stores the code separately
      in `anchor`; the docstring path keeps its closing line whole and lets the
      `c` claim the same line's comment half. ! Which is the day's theme: a rule
      the lexical reader got right and the Python one did not -- see `python-
      cannot-read-python`.
- [ ] 3 of the 7 files that fail `lossless` over 3,082 are this shape:
      `numpy/numpy/exceptions.py`, `numpy/.venv/Lib/site-packages/_virtualenv.py`
      and `numpy/.venv/Scripts/activate_this.py`. ! The other 4 are the unparsed-
      page case, guarded in 56d52dc.
- [ ] * THE QUESTION IS WHICH ONE OWNS IT. A `c` is the room beside a line of
      code, and a docstring's closing `"""` is not code -- so `# NOQA` beside it
      may not be a trailing comment at all. !
      `prove_unchanged._delimiter_shares_the_line` already refuses a PARAGRAPH-
      comment delimiter sharing a line with code; this is the same shape at a
      docstring's closing quote and has no such guard.
- [ ] * EXPECTED TO CLOSE WITH THE PYTHON BRANCH, ruled by Roy 2026-08-21: *"the
      numpy one will fall out automatically with the python one because that is an
      artifact of using the ast to get docstrings instead of the lexer which would
      ignore that."*
- [ ] !! CHECKED AT ROY'S REQUEST, AND IT DOES FALL OUT -- the first check was
      mine and was wrong. MEASURED 2026-08-21 by reading the numpy shape through
      `paragraphs_lexical` with `"""` as a delimiter: ONE paragraph, `docstring`
      2-5, `raw_lines[-1] == '    """  # NOQA'`, and line 5 owned ONCE. The
      trailing comment RIDES ALONG on the closing line as part of the run, and no
      `c` place claims it. Roy: *"it also automatically eats the # NOQA at the end
      of the line instead of having to figure out how to attach those back."*
- [ ] ! WHAT THE FIRST CHECK ACTUALLY FOUND was an obstacle to the lexical reader
      EXISTING, not a reason this defect survives it: Python's row has no `"""`
      delimiter, and `_strip_strings` blanks the spanning quote before the
      comment-opener test. Both must be answered for a lexical Python reader --
      and once one works, this defect is gone by construction rather than fixed.
- [ ] !! `"""` IS BOTH PYTHON'S STRING QUOTE AND ITS DOC DELIMITER, which is the
      real work in `python-cannot-read-python` and not in this TODO. Its row lists
      `('"""', "'''")` under `spanning_quotes`, and `_strip_strings` blanks a
      spanning quote BEFORE the comment-opener test -- by design, so a `//` inside
      a string cannot open a comment. A docstring is a STRING in a particular
      POSITION, and stating that position is what replaces the parser.
- [ ] ! SO IT CLOSES WHEN THE LEXICAL READER LANDS, and needs nothing of its
      own. The rule that reader needs -- a spanning string immediately after a
      `declares` line, or at the head of a file, is a docstring -- is one of the
      three things `python-cannot-read-python` lists the AST as buying. This
      defect is a consequence of the AST giving a docstring its whole closing
      line while the tokenizer reports a comment on the same line; a reader that
      cuts at the delimiter has neither half to reconcile.
