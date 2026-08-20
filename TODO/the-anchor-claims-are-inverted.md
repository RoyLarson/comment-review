# The anchor claims in SKILL.md and the brief are inverted

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
```

## Objective

The anchor claims in SKILL.md and the brief are inverted.

## Tasks

- [ ] `SKILL.md:429-434` claims `tokenized` resolves *docstring* anchors but not
      *a comment's*, and `SKILL.md:436` says *"It prints that no comment carries
      an anchor at either tier."* `census.py:401-403` prints the opposite
      unconditionally. Measured: 0 empty anchors in 7,371 paragraphs over 15
      shipped scripts.
- [ ] !! `reviewer-brief.md:107`, READ VERBATIM BY EVERY REVIEWER: *"the `anchor`
      ... names the declaration the census resolved, and is empty where none
      was."* It is never empty, and it is not the declaration --
      `vocabulary.toml:25` defines it as the LINE OF CODE, and observed anchors
      include `        return`.
