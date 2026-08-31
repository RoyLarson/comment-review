# The anchor claims in SKILL.md and the brief are inverted

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    agents
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
Triaged:  2026-08-23 -- both claims re-checked against the tree. Both are still false;
          the cited line numbers had drifted and the measurement was re-taken on a
          census that now emits four kinds the 2026-08-20 reading never saw
```

## Objective

**Two shipped files tell a reviewer that an anchor may be absent, and one of them also says an
anchor is a declaration. Neither is true of what `census.py` emits, and the second is read
VERBATIM by every reviewer.**

MEASURED 2026-08-23 -- `census.py --json --repo .` over the 20 shipped scripts: 8,738
paragraphs, **687 of them holding prose (`comment`, `docstring`, `trailing-comment`), and every
one of the 687 carries a non-empty anchor.** The 401 empty anchors in that run are ALL of kind
`leading` -- a zero-line place that holds no prose, carries no address and gets no record slot,
so it reaches no reviewer. **The field a reviewer is handed is never empty.**

! The earlier reading (0 empty in 7,371 paragraphs over 15 scripts) was taken before `leading`
existed. The count changed; the conclusion did not.

! **`anchor` is a LINE OF CODE, not a declaration.** `vocabulary.toml:25`: *"The LINE OF CODE
that an address is attached to -- the exact characters on it."* Observed anchors in the same run
include `        return`, `        continue` and `    try:`.

!! **`census.py` ALREADY PRINTS THE CORRECT CLAIM.** `census.py:454-458` prints
*"! EVERY address carries an anchor -- the LINE OF CODE it attaches to, at both tiers"*,
unconditionally, on every run. The two files below contradict a line the reviewer's own tool
emits, which is why this is worth fixing rather than tolerating.

## The three false sentences

- `SKILL.md:430` puts *"a **comment's** anchor"* in the `tokenized` tier's CANNOT ANSWER column.
- `SKILL.md:433-435` says the census *"prints that no comment carries an anchor at either tier"*
  and builds the CANDIDATE argument on it. The census prints the opposite. ! **Keep the CANDIDATE
  conclusion** -- it is correct and `census.py:456-458` states it -- and drop the false premise
  under it.
- `reviewer-brief.md:126-127`, read verbatim by every reviewer: *"The `anchor` is there to be
  GREPPED -- it names the declaration the census resolved, and is empty where none was."* Two
  errors in one sentence: it is a line of code rather than a declaration, and it is never empty
  in a slot a reviewer receives.

## Tasks

- [ ] T1 | T1 -- Take *"a comment's anchor"* out of the `tokenized` CANNOT
      ANSWER column at `SKILL.md:430`. Verify: no row of that table says a
      comment has no anchor.
- [ ] T2 | T2 -- Drop the false premise at `SKILL.md:433-435`, keeping the
      CANDIDATE conclusion. Verify: no sentence in `SKILL.md` says a comment
      carries no anchor.
- [ ] T3 | T3 -- Correct `reviewer-brief.md:126-127` to say a LINE OF CODE, not
      a declaration. Verify: `grep -rn "names the declaration" plugins/` comes
      back empty.
- [ ] T4 | T4 -- Drop *"and is empty where none was"* from the same sentence --
      a reviewer's slot never is. Verify: `grep -rn "empty where none was"
      plugins/` comes back empty.
