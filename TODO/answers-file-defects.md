# Answers files are admitted with answers a turn drops or refuses

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-22 (code review 2026-11-22, merged findings)
```

## Objective

A turn's answers file and the human's answers file are accepted with content
that is later dropped without a word or refused a step later: flows/answers.py
drops an answer with a null instruction and commits a composition that is blank,
`check --answers` never asks about a correction at an f place, and
flows/human.py reads a misspelled `[[answers]]` table as no answers at all. Each
is a read of an answers file that admits what the next step cannot use.

Found by the code review of 2026-11-22 (M29, M48, M51, M85).

## Tasks

- [ ] T1 | Make commands/check.py:359 check --answers ask corrections_in_answers
      as well as queries_in_answers
        > 2026-11-22 Check (M29): f0 patch in a turn answer counts as a human question
- [ ] T2 | Refuse a turn answer with a null instruction but a filled change at
      flows/answers.py:205
        > 2026-11-22 Check (M48): null-instruction answer makes check --answers exit 1
- [ ] T3 | Apply the change-must-be-filled rule to rewrites that compose to
      blank text at flows/answers.py:291
        > 2026-11-22 Check (M51): two corrects composing to blank text are refused
- [ ] T4 | Refuse an answers TOML that holds no [[answer]] table at
      flows/human.py:192
        > 2026-11-22 Check (M85): an [[answers]] typo is refused, not read as no answers
