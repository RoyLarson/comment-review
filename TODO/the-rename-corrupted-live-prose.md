# The block-to-paragraph rename corrupted a verb inside the verdict table

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (both reviews of 2026-08-20)
```

## Objective

The block-to-paragraph rename corrupted a verb inside the verdict table.

## Tasks

- [ ] !! `SKILL.md:68`, INSIDE THE VERDICT TABLE: *"`query` | unsettled | resolve
      it or escalate it. It PARAGRAPHS every other verdict on that sentence"*.
      `git show 7850bbc:...SKILL.md | sed -n 68p` reads *blocks* -- the verb. This
      is the task agent's ONLY statement of what `query` obliges. Introduced by
      a522ba2.
- [ ] Twice more in `references/compact.md:30-31`: *"does not PARAGRAPH this
      pass"* and *"Read as 'unresolved PARAGRAPHS stage 6'"*.
- [ ] !! `agents/comment-review-block-context.md:7-8` TELLS THE AGENT ITS OWN ROLE
      IS `PARAGRAPH-CONTEXT`. `grep -rn "PARAGRAPH-CONTEXT" plugins/ scripts/
      tests/` returns that one line. Its frontmatter, `SKILL.md:565`, `verdicts.py
      --reviewers` and `vocabulary.toml:140` all say `block-context` -- and the
      brief tells it to name its role.
- [ ] `agents/comment-review-module-context.md:77` reads `an if __name__ ==
      "__main__": PARAGRAPH`.
- [ ] `lexer.py:392` and `prove_unchanged.py:128` say *"a Java text PARAGRAPH"*.
      Java's feature is a text BLOCK -- the `"""` delimiter listed at
      `lexer.py:526`. The rename renamed a language feature.
