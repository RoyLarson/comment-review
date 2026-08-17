# REFERENCE ONLY misses the project's own documentation

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session · Roy (1 ruling)
Raised:   2026-08-17 (Roy, during the first full run of 0.1.7: "At some point the
          references also need to include the actual documentation files")
```

## Objective

**A documentation file that documents the code under review, without NAMING it, reaches no
reviewer.** Two mechanisms build the REFERENCE ONLY list and neither finds one:

- `referrers.py` matches on a NAME — the path, the stem, or a public top-level definition. A
  doc that describes what a module does in prose, and cites nothing from it, does not match.
- `SKILL.md`'s REFERENCE ONLY paragraph names three categories to select by hand: the repo's
  **decision record**, an **authority document** holding dated facts, and the **extracted or
  mirror copy** of the files under review. A project's ordinary documentation is none of the
  three.

⚠ **Measured on this repo's own first full run, 2026-08-17.** `docs/parsing.md`,
`docs/vocabulary.md` and `docs/limitations.md` went into the packet because the task agent
chose to put them there. Nothing asked for them, and `referrers.py` returned `scripts/README.md`
alone out of `docs/`.

That matters because a documentation file is where a claim goes to be settled or refuted. A
docstring saying *"the lexical tier cannot answer a comment's owner"* is checkable against
`docs/parsing.md`; a reviewer that never received it has to rule from the code alone, and the
`clean` it returns certifies less than it appears to.

## Tasks

- [ ] Decide what SELECTS a documentation file. Candidates, and they are not exclusive: every
      tracked `.md` outside the diff scope; a named documentation ROOT the way 1.4 finds the
      `move` destination tree; or a fourth category in `SKILL.md`'s REFERENCE ONLY paragraph.
      ⚠ The cost is real — this run's packet already listed 25 reference files, and every one
      of them is a file four reviewers may open.

- [ ] ⭐ Rule on whether the DESTINATION TREE found at 1.4 is automatically REFERENCE ONLY.
      They are the same tree in this repo (`docs/`), and the coincidence is not obviously an
      accident: a repo that stages prose OUT of code has, by construction, put prose there that
      the code no longer states. Roy's ruling, because it decides whether 1.4 gains a second
      output or the two stay separate questions.

- [ ] Say whether `referrers.py` should widen or stay a NAME matcher. ⚠ Recommendation: stay.
      It answers one question — who names these files — and a doc found by SUBJECT rather than
      by name is a different question with a different failure mode. Widening it would make its
      output unfalsifiable, which is the defect `check the CLAIM, not the CITATION` names.

- [ ] Whatever is decided, state it in ONE file. `SKILL.md`'s stage-4 REFERENCE ONLY paragraph
      is the candidate, since that is where the selection is performed and where the three
      existing categories already live.
