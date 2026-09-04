# REFERENCE ONLY misses the project's own documentation

```
Status:   decision-needed
Progress: 0 of 4 tasks closed
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17 (Roy, during the first full run of 0.1.7: "At some point the
          references also need to include the actual documentation files")
TRIAGED:  2026-08-23 -- RE-VERIFIED, both mechanisms unchanged. `SKILL.md:649-656` still
          names exactly THREE categories -- decision record, authority document,
          extracted/mirror copy -- and no fourth for ordinary documentation.
          `referrers.py:36` (`tokens_for`) still yields the stem, the posix path with each
          trailing suffix, and public top-level Python definitions, so a doc that names
          nothing still matches nothing. ! ALL FOUR BOXES ARE TASKS, and three of them are
          OWED RULINGS (marked `*`), which is why the Status is `decision-needed` rather
          than `open`: nothing here can be built until the selection rule is chosen.
SPLIT:    2026-08-23 -- no box split; each was already one decision or one edit. What
          moved is the candidate list, the cost measurement and the recommendation, which
          are now in the Objective, and every box gained a Verify clause.
```

## Objective

**A documentation file that documents the code under review, without NAMING it, reaches no
reviewer.** Two mechanisms build the REFERENCE ONLY list and neither finds one:

- `referrers.py` matches on a NAME -- the path, the stem, or a public top-level definition. A
  doc that describes what a module does in prose, and cites nothing from it, does not match.
- `SKILL.md`'s REFERENCE ONLY paragraph (SKILL.md:649) names three categories to select by hand:
  the repo's **decision record**, an **authority document** holding dated facts, and the
  **extracted or mirror copy** of the files under review. A project's ordinary documentation is
  none of the three.

! **Measured on this repo's own first full run, 2026-08-17.** `docs/parsing.md`,
`docs/vocabulary.md` and `docs/limitations.md` went into the packet because the task agent
chose to put them there. Nothing asked for them, and `referrers.py` returned `scripts/README.md`
alone out of `docs/`.

That matters because a documentation file is where a claim goes to be settled or refuted. A
docstring saying *"the lexical tier cannot answer a comment's owner"* is checkable against
`docs/parsing.md`; a reviewer that never received it has to rule from the code alone, and the
`clean` it returns certifies less than it appears to.

### What the three rulings have in front of them

- **What SELECTS a documentation file.** Candidates, and they are not exclusive: every tracked
  `.md` outside the diff scope; a named documentation ROOT the way 1.4 finds the `move`
  destination tree; or a fourth category in `SKILL.md`'s REFERENCE ONLY paragraph. ! The cost is
  real -- this run's packet already listed 25 reference files, and every one of them is a file
  four reviewers may open.
- **Whether the DESTINATION TREE found at 1.4 is automatically REFERENCE ONLY.** They are the
  same tree in this repo (`docs/`), and the coincidence is not obviously an accident: a repo that
  stages prose OUT of code has, by construction, put prose there that the code no longer states.
  Roy's ruling, because it decides whether 1.4 gains a second output or the two stay separate
  questions.
- **Whether `referrers.py` widens or stays a NAME matcher.** ! Recommendation: stay. It answers
  one question -- who names these files -- and a doc found by SUBJECT rather than by name is a
  different question with a different failure mode. Widening it would make its output
  unfalsifiable, which is the defect `check the CLAIM, not the CITATION` names.

## Tasks

- [?] T1 | T1 -- * Rule on what SELECTS a documentation file, from the
      candidates in the Objective. Verify: the rule is written down; T4 is where
      it lands.
- [?] T2 | T2 -- * Rule whether 1.4's destination tree is automatically
      REFERENCE ONLY. Verify: the ruling is recorded here and says whether 1.4
      gains a second output.
- [?] T3 | T3 -- * Rule on whether `referrers.py` widens or stays a NAME
      matcher. Verify: the answer is recorded here, with the reason it was
      decided that way.
- [ ] T4 | T4 -- State what T1 to T3 decide in ONE file, `SKILL.md:649` being
      the candidate. Verify: `grep -rn` for its phrase returns one path.
