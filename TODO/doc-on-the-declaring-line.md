# A docstring written on its declaration's own line takes no address, and the round trip invents a blank line

```
Status:   open
Progress: 2 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (found while fixing the docstring-closing-comment double emission,
          2026-08-29)
```

## Objective

A docstring written on its declaration's own line takes no address, and the round trip invents a
blank line.

!! **THE TITLE AND THE 2026-08-29 MEASUREMENT BELOW ARE BOTH SUPERSEDED, AND ARE KEPT AS THE
RECORD OF WHY THIS WAS FILED.** RE-MEASURED 2026-09-03 through `tests/conftest.build`:

| | 2026-08-29 | 2026-09-03 |
| --- | --- | --- |
| the docstring's address | **(none)** | **`b0`**, kind `docstring` |
| paragraphs on the page | five, two claiming line 1 | four, each its own place |
| `lossless` | *line invented: ''* | **`None`** |
| `set_page` | 1 line in, 2 out | **byte-exact** |

! **SO THE THREE BROKEN INVARIANTS BELOW ARE NO LONGER BROKEN**, and the addressing rebuild is
what fixed them; no box on this file was worked. T1 and T2 are superseded because their verifies
PASS and because `Addressing: #20` then answered the question underneath them.

!! **WHAT SURVIVES IS A DIFFERENT DEFECT THE OLD MEASUREMENT COULD NOT SEE.** `b0` is the GAP
series, whose pair is `comment`/`interval`, and it is holding `docstring` -- the `a` series' kind
-- while `a0` reports `undocumented`. That is
[`a-doc-comment-is-cued-a-and-typed-b`](a-doc-comment-is-cued-a-and-typed-b.md) inverted, and the
strict-xfail tripwire cannot see it for the same reason the original defect survived: the shape
is in neither `SOURCES` nor `FORMS`. **T3 is the live box.**

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

- [-] T1 | SUPERSEDED -- Addressing 20 answers where it goes: the approved a spot below the declaration. It is addressed today at b0, so the verify passed, but b0 was never the right place | a791148 | Give
      the docstring paragraph of a same-line declaration an address, or refuse
      the page. Verify: page_for over 'def f(): """D."""' emits no paragraph
      whose address is empty.
        > 2026-09-03 MEASURED: it IS addressed -- g.py@b0, kind docstring
        > 2026-09-03 so no paragraph has an empty address; this verify passes today
- [-] T2 | SUPERSEDED -- the line is invented DELIBERATELY. Addressing 20 rules the docstring moves below the declaration, so lossless is expected to report on this shape rather than return None | a791148 | Stop
      the round trip inventing a line on that shape. Verify: compositor.lossless
      returns None for it.
        > 2026-09-03 MEASURED: lossless None, set_page byte-exact
        > 2026-09-03 on all three shapes -- one line, one line plus trailing, two line
        > 2026-09-03 held open pending the ruling; Addressing 20 then closed it
- [ ] T3 | Add the shape to tests/test_reading.SOURCES and
      tests/test_compositor.FORMS. Verify: both go red before the two boxes
      above and green after.
        > 2026-09-03 the live one -- the shape is in neither SOURCES nor FORMS
        > 2026-09-03 so the tripwire never sees b0 holding a docstring kind
        > 2026-09-03 Addressing 20 makes this the live box -- the behaviour CHANGES
        > 2026-09-03 so it needs pinning, and nothing sees b0 until the shape is added
