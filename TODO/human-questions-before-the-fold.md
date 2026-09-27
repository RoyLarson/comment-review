# A human question is asked before the fold

```
Status:   open
Progress: 3 of 6 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-26 (Process 197)
```

## Objective

A human question is asked before the fold.

## Tasks

- [x] T1 | Process 198: TOML answers file, one [[answer]] per query naming the role that asked | 778b93456c5e705408a66aeb2c004bb22c2cfe3f | Decide
      what records the human answer and carries it back to the roles, per
      Process 197
- [x] T2 | collate, turn and check list every human query before the fold; AsksTheHuman | 14c9ddde5fe7350ee3597c053575ecf6a47ce19d | Implement
      a check that lists every human-review query in the returned copies or
      answers before collate or turn folds
- [x] T3 | TOML answers file read by --human; the answer rides on the refusal to the asking role | 14c9ddde5fe7350ee3597c053575ecf6a47ce19d | Implement
      the record of the human answer and its hand-back to the role that asked,
      so it can revise its mark or answer
- [ ] T4 | Update SKILL.md so the task agent asks each human-review query with
      the question tool before collate and turn; agents lane
- [ ] T5 | Delete the write-end refusal of a move open at an unruled end once no
      human-review query reaches the fold
- [ ] T6 | Delete the command-side held-query printing: collate _for_the_human,
      the Unsettlable _lines branch, _counted unsettlable, _unclosed exempt
        > 2026-09-26 files: commands/collate.py and flows/transcribe.py (_unclosed)
