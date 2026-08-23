# The module is `verdicts.py` and everything calls it the join

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22: the term the agent keeps saying is the join but
          the module is verdicts -- two separate things or one misnomer)
```

## Objective

The module is `verdicts.py` and everything calls it the join.

## Tasks

- [ ] IT IS ONE MISNOMER, MEASURED 2026-08-22. `verdicts.py` does not hold the
      verdicts: `VERDICTS` is defined in `record.py:181` and IMPORTED by
      `verdicts.py`. So the module is named for a table it does not own, while
      every other file calls it by what it DOES.
- [ ] THE TREE ALREADY AGREES ON THE OTHER NAME. `the join` appears 43 times
      across the shipped tree -- 14 in SKILL.md, 9 in `record.py`, 5 in `desk.py`,
      3 in `reviewer-brief.md`, 3 in `held.py`, and only TWICE inside
      `verdicts.py` itself, where it describes what the file is. ! The agent's own
      instructions call it the join; only the filename disagrees.
- [ ] ! AND `desk.py` DRAWS THE LINE BY THAT NAME: *"a question that needs two
      findings -- who contradicts whom, which paragraphs nobody accounted for --
      is the join's, and lives in `verdicts.py`."* The sentence has to name the
      concept AND the file because they are different words for one thing.
- [ ] RENAME TO `join.py`, and the cost is mechanical rather than deep: the
      imports in the modules that take it, the command lines in SKILL.md and
      CLAUDE.md, the test module name, and `docs/`. ! Nothing about the CONTENT
      moves -- this is the file taking the name its own prose already uses.
- [ ] ! IT IS THE SECOND MODULE NAMED FOR SOMETHING IT IS NOT, and the pair is
      worth deciding together: `lexer.py` mostly reads a parse rather than lexing
      -- see `lexer-does-not-lex`. Both are cases of a name that was true when the
      file was created and stopped being true as the split settled.
- [ ] * THE REGISTER SHOULD BE ASKED FIRST, per CLAUDE.md's rule that a new term
      comes from publishing before anywhere else. `join` is a database word. What
      does a copy desk call the step where several marked-up proofs are weighed
      against each other before anyone rules? If publishing has that word, it
      beats `join` -- and it is the same question the SYNTHESIS step needs
      answered, since that has no name at all.
