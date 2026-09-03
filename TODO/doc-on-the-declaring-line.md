# A docstring written on its declaration's own line takes no address, and the round trip invents a blank line

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (found while fixing the docstring-closing-comment double emission,
          2026-08-29)
```

## Objective

A docstring written on its declaration's own line takes no address, and the round trip invents a
blank line.

!! **MEASURED 2026-08-29** on `'def f(): """D."""  # note\n'` -- one line in, TWO out:

```
in : 'def f(): """D."""  # note\n'
out: 'def f(): """D."""  # note\n\n'
lossless: line invented: ''
identity: 1 lines in, 2 out
```

and the page carries FIVE paragraphs, of which two claim line 1 and one has no address at all:

| kind | cue | lines | raw_lines |
| --- | --- | --- | --- |
| `docstring` | **(none)** | 1-1 | `def f(): """D."""  # note` |
| `interval` | `b0` | 1-1 | `def f(): """D."""  # note` |

! **THREE INVARIANTS BREAK AT ONCE**, and each is one this repo states elsewhere. `lossless` is
the one `compositor.py` calls the invariant that must never break. A paragraph carrying neither
an address nor a symbol is what `tests/test_reading.py`'s
`test_a_paragraph_carries_an_ADDRESS_or_a_SYMBOL_and_never_both` forbids. Two paragraphs claiming
one line is what `test_every_line_of_the_file_is_covered_exactly_once` forbids.

!! **AND NO GATE SEES IT, because no source in either suite holds the shape.** The same reason
the docstring-closing-comment defect survived: `test_reading.SOURCES` and
`test_compositor.FORMS` are hand-authored, so a shape nobody thought to write cannot be
expressed. `docs/gates.md`: *"does the check pass" is not the question; "could the check fail"
is.*

! **THE COMMENT IS NOT THE CAUSE.** `'def f(): """D."""\n'` fails the same way -- the trailing
comment above is carried only because it is how the shape was found. What decides it is the
docstring statement sharing a line with the declaration that owns it, so `attach` has a
declaration place and a code line pointing at the same line and resolves to neither.

! **A BODY-LESS ONE-LINER IS FINE**: `'class C: pass\n'` round trips, because nothing claims the
line twice.

## Related, and NOT the same defect

[`census-degrades-silently`](census-degrades-silently.md) T6 records a one-line `def f(): pass`
whose `a1` place writes ABOVE the `def`, turning a proposed docstring into the MODULE's. That is
about a declaration with NO prose and where an `add` would put some. This is about a declaration
that ALREADY HAS its docstring on that line: nothing is added, and the page still cannot be set
back. `systems` owns whether the two are one file.

## Tasks

- [ ] T1 | Give the docstring paragraph of a same-line declaration an address,
      or refuse the page. Verify: page_for over 'def f(): """D."""' emits no
      paragraph whose address is empty.
        > 2026-09-03 MEASURED: it IS addressed -- g.py@b0, kind docstring
        > 2026-09-03 so no paragraph has an empty address; this verify passes today
- [ ] T2 | Stop the round trip inventing a line on that shape. Verify:
      compositor.lossless returns None for it.
        > 2026-09-03 MEASURED: lossless None, set_page byte-exact
        > 2026-09-03 on all three shapes -- one line, one line plus trailing, two line
        > 2026-09-03 NOT closed: lexer-and-language-findings T23 turns this red
- [ ] T3 | Add the shape to tests/test_reading.SOURCES and
      tests/test_compositor.FORMS. Verify: both go red before the two boxes
      above and green after.
        > 2026-09-03 the live one -- the shape is in neither SOURCES nor FORMS
        > 2026-09-03 so the tripwire never sees b0 holding a docstring kind
