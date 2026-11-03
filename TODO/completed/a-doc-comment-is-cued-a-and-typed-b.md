# A doc comment is cued a and typed b in three languages

```
Status:   closed
Progress: 4 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (the shadow suite's first run, 2026-08-25)
```

## Objective

A doc comment is cued a and typed b in three languages.

## Tasks

- [-] T1 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Decide
      whether the lexer types by MARKER or by the place the walk gave it
- [-] T2 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Make
      the kind agree with the cue for go, ruby and lua
- [-] T3 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Remove
      the three strict xfails in tests/test_reading.py once they pass
- [-] T4 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Update
      the retype comment at page.py:1074-1081, which states that kind and series
      must agree while its branch tests one kind of four
        > 2026-09-02 go, ruby and lua put kind=comment on a1; the pair wants docstring
        > 2026-09-02 rust, java and python put docstring on a1 and agree
        > 2026-09-02 MEASURED via tests/conftest.build, the xfailed test's own helper
        > 2026-09-02 four kinds reach an a place; the branch tests matter alone
        > 2026-09-02 so it cannot fire on go, ruby or lua, which arrive as comment
        > 2026-09-02 lexer.py:1263,1565 stamps the cue; _kind_of takes both halves
        > 2026-09-02 but these three doc markers ARE comment markers, so the token
        > 2026-09-02 cannot tell them apart -- tying the cue did not tie the kind
