# Code lines -- a reader hands back each line of code with its documentation place

Rulings: `docs/decision-log.md` Process #224 (a reader hands over only what parsing finds),
#226 (a detached doc is a comment), #228 (this design). Plan:
`docs/plans/2026-10-25-reader-hands-prose-only.md`, which this design amends.

## Intent

A reader hands the page two parallel structures today: `code()`, line number -> the code on
it, and `declarations()`, a list of `DocumentationPlace(line, insert, above)`. Nothing on a
code line says it declares something documentable. The fact is joined back to the line twice
by number -- `binder/page.py documentable` turns each declaring line into a position among the
code lines, and `reading/addresser.py cue` looks that position up while it walks -- and a third
time when a documentation paragraph is linked to its declaration (the reader stamped a cue
before P2; P2's first attempt added a `documents` ordinal to `Paragraph`).

`documentable` also recomputes where a Python docstring is set: from the `insert` line it
searches for the first code line at or after it, a position the Python reader already found
when it located the signature's end. And a declaration whose line is not a code line is dropped
with no word (`if line not in at: continue`); two declarations on one line keep only the last
(`out[at[line]] = ...`).

The fix is one structure carrying the fact on the line it belongs to.

## The shape (decided)

```python
class DocPlace(NamedTuple):
    at: int      # the code line the doc is set against
    above: bool  # True: above that line; False: after it, inside the declaration

class CodeLine(NamedTuple):
    line: int                   # 1-based source line
    code: str                   # the line's code, right-trimmed -- what an anchor is
    documents: DocPlace | None  # set when this line declares something documentable
```

`code` is the line's code with trailing whitespace removed, as every current source of code
lines produces it (`binder/page.py code_lines`, both readers' `code_for`). A string literal's
whitespace at the end of a line is not kept: the audit found the Rust reader keeping it to be
the defect that breaks `anchor + raw_lines[0]`.

- A doc set above its declaration (Rust, Go and every other language with a doc practice):
  `at` is the declaring line itself, `above=True`.
- A Python docstring: `at` is the code line that ends the signature (the declaring line itself
  for a one-line `def`), `above=False`. The reader states it; nothing downstream computes it.
- `CodeLine` holds no prose. A paragraph already holds its prose (`raw_lines`) and names what it
  attaches to (`anchor`, `anchor_line`); an anchor has many addresses and an address one anchor,
  so the link runs paragraph -> line only.
- A documentation paragraph's `anchor_line` is the line of the `CodeLine` whose `documents` it
  fills, set by the reader. `Paragraph` gains no field (P2's `documents` field is removed).

## Which paragraphs document something (decided)

The **kind** says a paragraph documents something: a reader gives every paragraph it decides
documents a declaration or the module `Kind.DOCSTRING` -- a Go or Ruby `//`/`#` run directly
above a `func`/`def` included, which the generic lexical reader types `comment` today. The
`anchor_line` says which: the line of a `CodeLine` whose `documents` is set, or `None` with the
`<module>` sentinel anchor for the module (`a0`). No other field marks it.

Matter (`f`) and the module's doc (`a0`) hang off the two sentinels the addresser already walks
(`<module>`, `<eof>`), not off any `CodeLine`; `CodeLine`s replace only the code-line triggers.
A matter paragraph is `Kind.MATTER` (the reader's, #225) and the page sends it to `f0` or `f1` by
which end it sits at, as today.

## One documentable thing per line (decided)

A line declares at most one documentable thing. When a line holds several declarations
(`fn a() {} fn b() {}`), the **first** takes the line's `DocPlace` and its `a` place. The
documentation written for the rest of the line is part of that first docstring -- one section,
one paragraph at the first declaration's `a` -- and later declarations on the line get no `a`
place. The read prints a `file:line` warning naming the line; nothing else marks it (Roy:
"I expect the agents know").

## Who does what (decided)

| part | does |
| --- | --- |
| each reader (Python, Rust, the generic lexical reader) | returns its `CodeLine`s in place of `code()` and `declarations()`; sets a doc paragraph's `anchor_line`; applies the one-per-line rule and its warning |
| page (`binder/page.py`) | hands the `CodeLine`s to the addresser; attaches each paragraph to its place, a doc by `anchor_line`; computes no code lines and converts no declarations -- `documentable` and the page's own `code_lines` call for building places are deleted |
| addresser (`reading/addresser.py`) | walks the `CodeLine`s; emits an `a` where `documents` is set, at the step `DocPlace.at` and `above` name; `b`, `c` and `f` unchanged |

**Effect on the plan's steps.** P4 ("derive each line's code in the page for every reader") is
superseded: the readers own a line's code, and the page computes none. Its replacement is a step
that makes the readers' code text right, with the audit's two cases as its tests (the Rust
literal's trailing whitespace; Python's invented `\` line after a backslash-continued docstring).
P2 ("assign every address in the page") is reworked onto `anchor_line`; its commit 49389b6f, which
added `Paragraph.documents`, is replaced, not reviewed.

The generic lexical path moves with it: `lexer.declarations(lang, code)` and the code-line
derivation the page runs for it today (`page.py` `places_on`, `page_for`'s lexical branch)
become the lexical reader's, so every reader hands the page the same thing.

## Goals

- One place states, per code line, whether it declares something documentable and where the doc
  is set. No line-number join between two lists, anywhere.
- Every address on every existing test page and corpus page is unchanged, except where a line
  held two declarations.
- `fill_the_gaps` and the addresser read the same code lines by construction.

## Non-goals

- `commentable` / `trailing_commentable` / `matter_able` attributes. The `b`, `c` and `f` rules
  apply to every line today (`addresser.py` `cue` docstring); none is per line. Add one only
  when a line is shown to refuse a place.
- Changing what `comment_form` or the desk does.
- Carrying `CodeLine`s in the binder JSON. Every consumer re-reads the file through `page_of`,
  which runs the reader.

## Anti-goals

- A second way of naming a declaration (an ordinal, a cue string) beside its line.
- The page or addresser recomputing anything a reader stated.

## Constraints

- `reading` is a leaf: `CodeLine` and `DocPlace` live in `reading` (beside or replacing
  `reading/source.py DocumentationPlace`), and `binder` imports them from there.
- Tests check each unit's own behaviour (Roy, 2026-10-25): a reader test checks the `CodeLine`s
  and `anchor_line`s it hands back; an addresser test walks hand-built `CodeLine`s; a page test
  checks attachment. No test checks one unit through another.
- Python reading uses no host parser (`tests/test_python_lexical_proof.py`).

## Builder's call (controller's call, not Roy's -- marked)

- **Guard for the single source of code text.** With the page no longer computing code lines,
  a reader bug in a line's code moves anchors and gap boundaries silently (the audit found two:
  Rust keeps a literal's trailing whitespace; Python invents a `\` line). Proposed: the page
  refuses a page where a code line's `code` plus the prose on that line does not rebuild the
  source line. Controller's call; drop it if it proves to be a second implementation of the
  proof.
- Exact names (`CodeLine`, `DocPlace`, the record method that returns them), whether
  `DocumentationPlace` is renamed or replaced, and how the generic lexical path returns its
  `CodeLine`s alongside its paragraphs.
- Order of landing: P9 (the page drops its detached-documentation placement) first, because it
  removes `record.warning_owners` -> `cues.documents(owner + 1)` (`page.py:967-981`), the one
  other ordinal naming a declaration; then the shape and the two record readers, the lexical
  path, and P2's paragraph link reworked onto `anchor_line`.
- **A one-line Python `def` or `class`** (`def f(): return 1`): `DocPlace(at=that line,
  above=False)` sets its empty `a` after the line, where the docstring goes. Today the `a` is
  released before the line's `b` (`page.py:627-628`, `addresser.py:873`), so `Cues.reading` lists
  it above the `def`. The `a` numbers do not change; the reading order does, and it is named an
  expected difference with its own test.
- **A doc comment inside a line for a later declaration** (`fn a() {} /** b */ fn b() {}`): it
  sits between code on one line, so it cannot join the first declaration's paragraph without
  that paragraph spanning code. It is read as any comment inside a line is read today -- the
  shape `TODO/a-comment-inside-a-line-makes-the-file-unprovable.md` holds -- and this design
  adds no handling for it. The one-per-line rule applies to documentation above the line.

## Checks

- `git grep -n "def documentable\|def declarations\b" -- src/comment_review` returns nothing
  outside the readers' own construction of `CodeLine`s.
- No `documents` field on `Paragraph`; `git grep -n "address=" -- src/comment_review/reading/python src/comment_review/reading/rust` returns nothing.
- Full suite green with no address expectation changed. A before/after dump of every address on
  the fetched corpora (`corpora/`) for at least Python, Rust and two lexical languages shows no
  difference except lines holding two declarations.
- An addresser test: hand-built `CodeLine`s with a `DocPlace(at, above=False)` whose `at` is a
  later line than the declaring line place the `a` after that line.
- A reader test: `fn a() {} fn b() {}` with a doc above it yields one `CodeLine` with
  `documents` set, one documentation paragraph anchored to it, and one warning.
