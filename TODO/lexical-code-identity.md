# Use lexical code identity at both proof boundaries

```
Status:   open
Progress: 4 of 9 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-10 (live-run)
```

## Objective

Use lexical code identity at both proof boundaries.

## Tasks

- [x] T1 | Both gates use lexical source correspondence for doc add and removal | 5564f046 | Replace
      Python AST identity checks with lexical comparison; verify docstring add
      and removal agree at both gates
        > 2026-10-10 Roy chose lexical identity at both code-unchanged boundaries
        > 2026-10-10 Use the owned scanner, independent of the runtime Python grammar
        > 2026-10-10 Formatting follows prose-only proof and precedes presentation
        > 2026-10-10 Reader scope: all languages currently listed by gather --languages
        > 2026-10-10 Code-reader scope excludes config, data and document formats
        > 2026-10-14 Check: both gates accept doc add/drop; proof also requires approval
- [ ] T2 | Preserve literal whitespace in prove_unchanged.py:191-207; verify
      blank-line and trailing-space edits change the fingerprint
- [x] T3 | Selected documentation retains protected directive context; reviewed | 09df3de4 | Retain
      protected directive context when selecting documentation
        > 2026-10-14 Check: selected docs refuse directive spacing or placement changes
        > 2026-10-14 Reason: preservation.py:213 erases protected source context
- [x] T4 | Multiline documentation suffix correspondence passes both directions | 09df3de4 | Match
      retained code after multiline documentation removal
        > 2026-10-14 Check: multiline doc removal retains closing-line code indentation
        > 2026-10-14 Reason: _documentation_span loses the retained suffix context
- [ ] T5 | Compare a shebang no language row names in the stripped proof
        > 2026-10-26 Check: dropping a .rb, .sh or .lua shebang is refused
        > 2026-10-26 Reason: pre-existing; .js, .rs and .py already refuse it
- [ ] T6 | Prove a Lua file whose [[ only opens a --[[ comment
        > 2026-10-26 stripped.py:84: any [[ in text is unprovable; each --[[ hits it
        > 2026-10-30 Part met 91c8e885: a no-code Lua file with --[[ now proves
- [x] T7 | FINISHED: no-code file proves under a language row (#248) | 435fed79 | Prove
      a lexical file that has no line of code
        > 2026-10-27 code_fingerprint: an empty strip is unprovable; at ef037f20
        > 2026-10-27 Blocks #241: filling a no-code file's <eof> a refuses at prove
        > 2026-10-30 #248: only under a language row; no row stays unprovable
- [ ] T8 | Refuse an escape that ends a comment in a row's grammar
        > 2026-10-30 Java \u000a, C *\ newline /, trigraphs; pass beside code too
- [ ] T9 | Add per-row directive forms the proof protects inside comments
        > 2026-10-30 /// <reference> in .d.ts; /*!50000 DROP TABLE */ in .sql; design
