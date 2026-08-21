# Outside Python the `a` place is emitted and never filled

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

Outside Python the `a` place is emitted and never filled.

## Tasks

- [ ] !! MEASURED 2026-08-21. `/// The name.` above `pub fn f()` in Rust censuses
      `a1 undocumented declares=1` AND `b0 docstring 'The name.'` -- the place
      says the function is undocumented while its documentation sits in the gap.
      Same for `.go`, `.java`, `.ts`, `.cs`.
- [ ] `Paragraph.declares` is set only in `paragraphs_stdlib` and on synthetic
      empty places. `paragraphs_lexical` never sets it, so `attach` falls through
      to `above()` for every doc comment in every lexical language.
- [ ] ! SO function-context CAN FILE AN `add` FOR PROSE THAT ALREADY EXISTS, and
      ownership-context reads a doc comment as a gap paragraph.
- [ ] ! CLAUDE.md's claim that the keyword lists made an `a` place resolve for
      eleven languages holds for EMITTING the place, not for ever filling it. 16
      of 17 languages are affected.
