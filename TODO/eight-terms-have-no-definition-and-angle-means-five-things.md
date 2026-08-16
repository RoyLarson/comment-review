# Eight terms have no definition, and `angle` means five things

```
Status:   in-progress
Progress: 11 of 16 tasks done
Owner:    session · Roy (⭐ 4 rulings left)
Raised:   2026-08-15 (a twelve-agent usage collection over the whole live tree)
```

## Objective

The system's own vocabulary is not stated where its readers meet it. NINE terms were used
with a fixed sense and defined nowhere — `angle` was the worst, at roughly forty sites in
`SKILL.md` alone plus every script and agent file, carrying six distinct senses. Fifteen
more words carry two or three meanings each, and a word may do that as long as each meaning
is clarified up front, which none of them are. Roy ruled the first two: **`angle` is retired
in favour of `editorial role`** (identifiers say `reviewer`), and **`sweep` is not a term —
stage 7b is `APPLY`**. Both are applied. The rest is deciding,
per term, whether to state the meaning, split the word, or delete the use.

Current behavior: [`docs/vocabulary-usage.md`](../docs/vocabulary-usage.md) — every stating site
and every use site for all 108 terms, with the sense carried at each. Term list and bundle map:
[`docs/vocabulary-inventory.md`](../docs/vocabulary-inventory.md). Both are surveys of what the
vocabulary does **today**; as each term below is settled, its entry becomes a statement of what
the term means, and the two files converge on one `docs/vocabulary.md`.

⚠⚠ **This file settles MEANINGS, not placement.** Where a term is defined in a file most of its
readers cannot load, that is an observation for the distribution pass, not a move to make here.
See the standing rule in [`README.md`](README.md).

## Tasks

- [x] Rename `angle` → editorial role. **Done 2026-08-15.** Prose says **editorial role**;
      identifiers say **reviewer** — Roy ruled the split because `role` alone would also cover
      the task agent and the absent author. `--angles` → `--reviewers`, `ANGLE FILES` →
      `REVIEWER FILES`, `angle = path.stem` → `reviewer`. Clean break, no alias, CHANGELOG
      entry written. It was SIX senses, not five (the survey's own heading undercounted, now
      corrected), and none needed a different word: four are the role, and the other two are
      the role's NAME and its FILE. ⚠ `angle` still appears in `CHANGELOG.md` (history),
      `docs/vocabulary-*.md` (the retirement records) and this file's name — all deliberate.
      167 tests pass, `ruff check` clean, 5 shipped files parse on 3.9.

- [x] Settle `budget`. **Done 2026-08-15 — Roy's ruling: the only real budget is what a
      shipped instruction file costs everyone to load**, measured in lines per file, declared
      once at `docs/limitations.md:9`. `cap` takes back the five sites meaning a comment's line
      limit (it was already defined; an undefined word was standing in for it). The
      reviewer's-runtime sense loses the word. ⚠ Measured while settling it: the budget covers
      28 KB of the 224 KB shipped, and NOT the two largest files a run loads — a reviewer's own
      role file is ~7 KB against an 18 KB shared brief, so 70% of what it loads is not its role,
      and four parallel reviewers load four copies of that brief. Recorded in
      `docs/limitations.md` as a measured gap. **Superseded my first pass, which gave the bare
      word to the reviewer sense on grounds of it being the original.**

- [x] Define or delete the seven remaining terms used with no definition. **Done 2026-08-15,
      no ruling needed.** Five stated where a reader already meets them, two deleted.
      `prose tree` and `node` together at `SKILL.md:76`; `the join` at `:526`; `detector` at
      `reviewer-brief.md:235`; `banner` at `module-context.md:18`. **Deleted:**
      `assessability gate` (one use, in frontmatter, and the idea was already stated without
      it) and `acquittal rate` (a measured quantity no site gave a denominator for — both uses
      now name the population). ⚠ No new sections: every statement went into a sentence that
      already described the thing without naming it, which is how the two landing in
      `module-context.md` stayed LINE-NEUTRAL against its budget. All four agent files still
      101/101/129/120.

- [x] ⭐ Rule on `sweep`. **Done 2026-08-15 — Roy ruled stage 7b is APPLY and `sweep` stops
      being a name.** It turned out not to need a definition: `SKILL.md:16-17`, `:30` and the
      filename `apply.md` all already said APPLY, so `sweep` was a synonym outliving `sweep.py`.
      Retired at 12 term sites; the 5 plain-English uses stay, and are no longer ambiguous now
      that there is no name to collide with.

- [x] Fix the dead import. **Done 2026-08-15** — `evals/generator_split.py:37` and its five
      uses now read `census`, and `evals/grade_hazards.py:15` cites `census.py`. Verified: the
      script runs. 167 tests pass, `ruff check` clean, 5 shipped files parse on 3.9.

- [ ] ⭐ Rule on `HOME`. `agents/comment-review-ownership-context.md:60-65` defines it as an
      existing site where the claim is already written and explicitly rules out "the function
      that implements the rule"; `references/reviewer-brief.md:281` says "a rule with no home
      in the CODE", meaning that function. `:58` uses a third sense. One word, three readings,
      no cross-reference.

- [ ] Declare or split the remaining multi-sense words. **Six done 2026-08-15**, each where a
      reader meets it: `block` (Roy's definition, its own commit); **`proof`** — three unrelated
      things, so `write.md:45` now says IDENTITY PROOF and the `proof` LEVEL says it is named
      for stage 8's proof pass; **`level`** — `README.md` called the four roles "levels", and
      `run_context.py` claimed an unknown level "dispatches four reviewers" when three of the
      four run fewer; **`label`** — the acquittal called `label` was the one generic name among
      five descriptive ones and is now `names-its-line`, freeing the bare word for "any
      acquittal-list entry", which is how `module-context` already used it; **`run`** — bare
      `run` means one invocation, the prose sense is always a COMMENT run, stated once and the
      two bare prose uses qualified; **`residue`** — `residue-check.md` now says it is not
      `prove_unchanged.py`'s residue, the two being unrelated remainders (what the edit left of
      the CODE, versus what it lost of the PROSE).
      **`mark` done 2026-08-16** — the census's are ANNOTATIONS, `mark` is editorial. Ruled by
      the metaphor: editorial marks are what an editor writes on a manuscript, which is what
      stage 4 emits; the census's are mechanical observations, made at stages 2-3, and
      `SKILL.md` already called them annotations while stage 2 is named ANNOTATE. 25 code
      sites, including the published `"marks"` JSON key. Unblocks the edit-mark work.
      **Done 2026-08-16:** `worktree` — Roy ruled it needs no definition, it is git's and
      depends on the project running the review; it is now gone from the shipped tree entirely
      (see [`the-harness-leaks-into-the-shipped-rules`](the-harness-leaks-into-the-shipped-rules.md)).
      `target` and `author` — reviewed, no defect: `target` is stated at `SKILL.md:182` and its
      other uses are the ordinary verb; `author` is always the approving human, and *authored*
      is the agent's writing, never called "the author". `load-bearing` — already clear at
      `ownership-context.md:56`, no change. `obituary` — clear, and **`tombstone` is now
      declared as its synonym** in the section heading, at Roy's instruction: recent training
      pairs the two words, and an agent classifying something a tombstone must find the rule.
      Declared in the heading to stay line-neutral against the 101-line budget.
      **Still open: `guard`** — two senses that read as contradicting.

- [x] Reconcile two marks the published table never listed. **Done 2026-08-15** — `census.py`
      emits `narrative-in-docstring` (`:853`) and `SKILL.md`'s six-row marks table did not
      carry it; it has a row now. And `SKILL.md` said "a gap in the mark" where `census.py` and
      the brief both say "a gap in the review" — one sentence, three sites, now one wording.

- [ ] ⭐ Reconcile "5 of its 7 reviewer reports" — the LAST of this group, and the only
      one that is not a fact this session can re-derive. `reviewer-brief.md:82`,
      `SKILL.md:550` and `verdicts.py:19` all cite it; `grade_hazards.py:3-4` says the
      same in words. Every other site fixes the reviewer population at four, and no site
      says what the seven were. Roy ran it; the number is his to confirm or correct.
      **Done 2026-08-15, the other three in this group:** `docs/parsing.md` said "Five
      fields" for a `Language` row that declares eight (three required, five defaulted,
      four supplied in the example) — the phrase was never in `census.py` as the survey
      recorded; `corpora.toml` said "stage 0.3" at two sites where `SKILL.md:245`
      numbers it 1.3; `find_llm_repos.py` documented its own path as `corpora/`.

- [x] Settle the eval base ref. **Done 2026-08-15 — `REDACTED_SHA_A`, at all four sites, at
      full length.** Settled by evidence, not preference: `REDACTED_SHA_H` is an ANCESTOR of
      `REDACTED_SHA_A`, the fetched worktree is checked out at `REDACTED_SHA_A`, and three of the
      four sites already used it. Two hazard signatures (D9, D3) verified present at
      `REDACTED_SHA_A` before `discriminators.md` was moved onto it.

- [x] Point `evals/evals.json:3` at a path that exists. **Done 2026-08-15** — both dead
      paths replaced by `evals/discriminators.md`.

- [x] Agree which hazards have no text signature. **Done 2026-08-15 — two, D3 and D12.**
      The code and `README.md` already said two; only the module docstring undercounted,
      and it now names both with D3's reason.

- [ ] ⭐ Rule on `SKILL.md:488`. It justifies `DOC CONVENTION`'s place in the dispatch packet
      on the grounds that "reviewers write replacement text", against `SKILL.md:26`, the
      frontmatter, and `references/reviewer-brief.md:6-10`, which assign writing to the task
      agent at stage 5. Either the packet section has a different reason or the read-only rule
      has an exception nobody has stated.

- [x] Name "the four refusals" the same thing in both places. **Done 2026-08-15** — the
      heading in `residue-check.md` now reads "The four refusals — removals the three
      conjuncts miss", so the phrase its four citing sites use is textually present in
      the file they point at.

- [x] Give `unparsed` a row in `references/compact.md`'s KIND table. **Done 2026-08-15** —
      it is a diagnostic standing in for a file that would not parse, not a block, so the
      row says COMPACT may do nothing with it but report it. The sentence above the table
      said "the two" while naming three kinds; it now names four.

- [ ] ⭐ Rule on the four enforcement gaps, each a case where a script accepts something the
      prose does not: the `add` payload check passes on the bare word "anchor" and rejects a
      named declaration without it (`verdicts.py:302-307`); `--reviewers` is compared to file
      stems and never to the published role names (`verdicts.py:487`); the `FINDING` field is
      never checked, and `Finding.finding` holds a reviewer clause or a diagnostic string
      depending on `block == -1`; `CODE CONCERNS` is not parsed or gated at all.
