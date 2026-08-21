# A docstring whose closing `"""` carries a trailing comment is owned twice

```
Status:   open
Progress: 0 of 10 tasks done
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
- [ ] !! CHECKED THE SAME DAY AT ROY'S REQUEST, AND IT DOES NOT FALL OUT ON ITS
      OWN. MEASURED: Python's language row has NO delimiters for `"""` --
      `block_comment` and `doc_block` are both empty -- so `paragraphs_lexical`
      produces ZERO paragraphs for a Python file. The lexical reader cannot see a
      docstring at all today.
- [ ] !! AND ADDING THEM COLLIDES WITH `spanning_quotes`. Python's row already
      lists `('"""', "'''")` there, and `_strip_strings` BLANKS a spanning quote
      before the comment-opener test runs -- so giving `"""` a comment delimiter
      still yielded zero paragraphs in the check. A docstring is a STRING in a
      particular position, and the position is what the AST supplies.
- [ ] ! SO IT CLOSES DOWNSTREAM OF A RULE THAT DOES NOT EXIST YET: a spanning
      string immediately after a `declares` line, or at the head of a file, is a
      docstring. That is lexable and is one of the three things `python-cannot-
      read-python` lists the AST as buying. The trailing-comment cut then fixes
      this defect -- but only after it.
