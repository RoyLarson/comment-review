# One line ending per file

```
Status:   open
Progress: 1 of 6 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log Process #220, #221)
```

## Objective

A file's line ending is decided once, in `machine/`, when the file is read, and
every function that writes a line break is handed that ending through the flows
(`decision-log.md Process: #220`, `#221`).

Four rules decide it today, each in its own module:

- `results/compositor.line_endings`: CRLF if the file holds any CRLF.
- `results/prove_unchanged.dominant_ending`: the majority ending, compared against an
  untouched sibling file rather than the file's own pre-edit read.
- `reading/python/line_breaks._newline`: the file's first ending.
- the paragraph-local rewraps in `reading/comment.py`, `reading/lexer.py` and
  `reading/docstring.py`, which guess from the paragraph's own text.

The rule, as ruled:

- a file that uses one ending keeps it;
- a file holding a lone CR is refused at the gather, as unreadable;
- a file that mixes CRLF and LF takes the ending git checks that path out with, from its
  attributes, then `core.eol` and `core.autocrlf`; where git applies no conversion to the
  path, the file is refused;
- a file with no line break takes LF.

Measured 2026-10-25: no file in the corpora, the cargo registry or this tree
holds a lone CR or mixes endings, so both refusals are guards on inputs no
current corpus supplies.

## Tasks

- [ ] T1 | Answer each file's line ending from one function in machine/
        > 2026-10-25 Check: a test per case (one, lone CR, mixed, none) fails first
- [ ] T2 | Refuse a file holding a lone CR at the gather
        > 2026-10-25 Check: a lone-CR fixture makes gather exit nonzero, naming it
        > 2026-10-31 Code review: `# x<CR>touch PWNED` proves with a c0 edit
        > 2026-10-31 Code review: `# x<CR>touch PWNED` proves with a c0 edit
- [ ] T3 | Write every line break with the ending decided at the read
        > 2026-10-25 Check: a CRLF page sets back CRLF on drop, move, patch, docstring
- [ ] T4 | Check a written file's ending against its own pre-edit read
        > 2026-10-25 Check: CRLF file beside an LF sibling: kept proves, LF fails
- [-] T5 | SUPERSEDED by T6: reworded, the label read as a ruling owed | 74a033c2 | Remove
      every line-ending rule outside machine/
        > 2026-10-25 Check: no "\r\n"-vs-"\n" choice in src/ outside machine/
- [ ] T6 | Delete each line-ending guess made outside machine/
        > 2026-10-25 Check: no "\r\n"-vs-"\n" choice in src/ outside machine/
