# Three functions in page.py are permutations of the same two words

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20: every rename is a function-context finding)
Measured: 2026-08-20 — the wrapper is undone by its own callers: nearly every one writes
          `sorted(code_lines(...))`, converting the set back into the ascending list
          `code_lines_of` already returns. One production caller, ~15 in tests. Its only
          reason -- taking Paragraph objects where the other took dicts -- went when the
          page was made to speak dicts throughout.
```

## Objective

!! **THE THREE FUNCTIONS ARE ONE STRUCTURE ASKED THREE WAYS.** Roy, 2026-08-20: *"the fact that
you said 'sets' ... leaves me thinking we have a sorted-dictionary or it should always be a
list."*

| today | returns | the question it answers |
| --- | --- | --- |
| `code_lines_of(text, paragraphs)` | `list[int]` | which lines are code |
| `code_lines(text, prose)` | `set[int]` | the same, for MEMBERSHIP |
| `lines_of_code(text, prose)` | `list[tuple[int, str]]` | each code line WITH its characters |

! **The `set` is the tell.** One caller wants membership, another wants order, so there are two
shapes and a `sorted()` bridging them -- and nearly every call site writes
`sorted(code_lines(...))`, converting the set back into the ascending list the first function
already returns.

## What it should be

**An ordered mapping from line number to the code on that line**, built ascending -- a plain
`dict`, which in Python is insertion-ordered:

```python
{2: "N = 0", 3: "def f():", 5: "    return 1"}
```

One structure answers every consumer:

| consumer | today | with the mapping |
| --- | --- | --- |
| the walk | `lines_of_code(...)` | iterate it |
| occupancy | `code_lines(...)`, a set | `n in code` |
| `documentable` | indices into `lines_of_code` | `enumerate(code)` |
| the line numbers | `code_lines_of(...)` | `list(code)` |
| a line's anchor | a second lookup | `code[n]` |

! **The three functions exist because the structure could not answer both questions.** Fix the
structure and there is one function, and no `sorted()` anywhere.

## Do not repeat the attempt that failed

! An attempt on 2026-08-20 thrashed and was reverted twice. What it did wrong, so the next one
does not:

- **deleted `code_lines` and put an `isinstance` branch in `code_lines_of`** so it took either
  dicts or `Paragraph`s. That is not removing the adapter, it is hiding it -- `code_lines`
  existed BECAUSE something had to convert, and the branch made one function serve two shapes
- **treated the `sorted()` calls as usage rather than residue.** They were necessary when the
  thing was a set; making a list satisfy code written for a set keeps the smell and moves it
- **was about to change an assertion from `{1, 2}` to `[1, 2]`** to make a test pass, which is
  editing the test to fit the implementation

! Roy, on the thrash itself: *"this looks like you are either trying to make stuff work that
doesn't need to work, trying to get something to do something it probably shouldn't do, or the
data structure is inherently the wrong data structure for what is happening. The code smell is
having to run `sorted()` on something even though you stated it should be a no-op."* **The
reverting was the diagnostic**, not the mechanics being hard.

## Tasks

- [ ] !! `code_lines_of` returns `list[int]`, `code_lines` returns `set[int]` --
      THE SAME QUESTION, a different type -- and `lines_of_code` returns
      `list[tuple[int, str]]`, a different question entirely. Three names built
      from the same two words, in one module.
- [ ] `code_lines` is a wrapper over `code_lines_of` that exists only to take
      `Paragraph` objects where the other takes dicts. Since the page speaks dicts
      throughout now, decide whether it earns a name at all.
- [ ] ! A caller cannot tell them apart without opening all three. That is the
      `function-context` question -- do name, signature and body agree -- asked of
      a whole module rather than one function.
- [ ] !! THE STRUCTURE, ruled 2026-08-20: an ORDERED MAPPING from line number to
      the code on that line -- a plain dict built ascending. Roy: 'we have a
      sorted-dictionary or it should always be a list.' It answers every consumer
      at once: iterate it for the walk, `n in code` for occupancy,
      `enumerate(code)` for `documentable`, `list(code)` for the numbers,
      `code[n]` for a line's anchor. ! The three functions exist because the
      structure could not answer both order and membership.
- [ ] ! DO NOT REPEAT THE 2026-08-20 ATTEMPT, which was reverted twice. It deleted
      `code_lines` and put an `isinstance` branch in `code_lines_of` so one
      function took two shapes -- hiding the adapter rather than removing it --
      treated the `sorted()` calls as usage rather than residue, and was about to
      change an assertion from `{1, 2}` to `[1, 2]` to make a test pass. The
      reverting WAS the diagnostic.
