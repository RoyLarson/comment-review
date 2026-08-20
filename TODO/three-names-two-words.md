# Three functions in page.py are permutations of the same two words

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20: every rename is a function-context finding)
```

## Objective

Three functions in page.py are permutations of the same two words.

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
