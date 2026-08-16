# Eight terms have no definition, and `angle` means five things

```
Status:   in-progress
Progress: 15 of 18 tasks done
Owner:    session · Roy (⭐ 2 rulings left)
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

- [x] ⭐ Rule on `HOME`. **Roy ruled 2026-08-16: three questions, three words.** `anchor` is
      the code fragment a block attaches to; `home` is which SITE a duplicated claim survives
      at; `owning function` is the code that should hold a rule and does not. ⚠ Two of the
      three readings sat SIX LINES APART in `ownership-context.md` and inverted — `:58` made a
      home a declaration in the code, `:63` expressly ruled the code out. ⚠ I proposed the
      opposite assignment first; Roy checked it against `anchor`, which is already the code
      position at four sites and in the stage-5 gate (`verdicts.py:308`), so `home` could only
      be the surviving site. Fixed at `:58`, at `reviewer-brief.md:283`, and at `:279`, which
      had introduced a FOURTH word by saying "move the claim to its owner".

- [x] Declare or split the remaining multi-sense words. **Done 2026-08-16.** Six on 08-15, each where a
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
      **`guard` done 2026-08-16 — Roy's split.** A GUARD is code that protects against wrong
      output (`if`/`match`, `assert` which `-O` strips, raise/exception); an INVARIANT is what
      the code should hold, and a comment carries it when no guard does. ⚠ He proposed
      `assertion` for the second; it collides with `assert`, which is in his own guard list, so
      `invariant` was taken instead — already used in that exact sense at
      `function-context.md:43,73,76`. The acquittal `only-guard` becomes `unguarded-invariant`:
      the old name read as "the only CODE guard", the opposite of what it acquits. This closes
      the multi-sense list.

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

- [ ] Settle **`own` / `owner` / `ownership`** — added 2026-08-16 by Roy, and ⚠ **it was on
      neither survey list**, the same miss as `budget`. Four senses, two of which are things
      just separated one word over:
      **A — the census field**, `Block.owner`, `SKILL.md:305` *"who owns a block → the
      declaration on the line after the comment run ends"* — that is the **anchor**;
      **B — a role's jurisdiction**, *"the block-context role owns quantified claims"*, all four
      agent frontmatters, `reviewer-brief.md:71,272` — the largest use, defined nowhere;
      **C — the owning function**, `module-context.md:73`, `compact.md:109`, `SKILL.md:678`
      *"no owning definition"*, and `reviewer-brief.md:262` *"the rule needs an owning type"* —
      three spellings for one thing; **D — the role name**, `ownership-context`.
      ⚠ `census.py:351` carries A, A-as-capital and D in one sentence.

- [ ] Re-sweep the vocabulary once everything currently unknown is settled. Roy, 2026-08-16:
      *"that will help the agents focus on potential topics/semantics that mix."* ⚠ The first
      collection missed `budget` (18 sites, four senses) and `own` (four senses) — both found by
      Roy reading, not by the sweep — so **108 was a floor, not a census**. Seed the re-sweep
      with those two misses: a term is easiest to miss when it reads as ordinary English.

- [x] ⭐ Rule on `DOC CONVENTION`'s justification. **Roy ruled 2026-08-16, and gave it a real
      reason rather than deleting the section.** The old one — *"the template matters because
      reviewers write replacement text"* — was false against `SKILL.md:26`, the frontmatter and
      `reviewer-brief.md:7-9`; and no reviewer rule mentioned the convention at all (zero hits
      across four agent files and the brief). The reason is that **a docstring's format decides
      which of its lines are structural and which are prose**, so a reviewer that does not know
      it cannot tell what a block contains — and stages 5 and 6 match their output against it,
      so the human is not left rewording work already done.
      Also rewrote **1.3**, which had said the template was *"for use when rewriting the
      docstring"* — the same false framing. It now MEASURES rather than assumes, records
      **module** and **function** docstring formats separately, records the **comment** format
      separately where the repo is consistent about one, and writes a template out rather than
      naming the nearest standard.
      ⚠ Delivery already worked: the STYLE SHEET records the 1.3 templates and reaches the
      reviewers (packet), stage 5 (task agent) and stage 6 (contract item five). That is now
      stated where the style sheet is described, instead of being true by accident.

- [x] Name "the four refusals" the same thing in both places. **Done 2026-08-15** — the
      heading in `residue-check.md` now reads "The four refusals — removals the three
      conjuncts miss", so the phrase its four citing sites use is textually present in
      the file they point at.

- [x] Give `unparsed` a row in `references/compact.md`'s KIND table. **Done 2026-08-15** —
      it is a diagnostic standing in for a file that would not parse, not a block, so the
      row says COMPACT may do nothing with it but report it. The sentence above the table
      said "the two" while naming three kinds; it now names four.

- [x] **Moved out 2026-08-16 — the enforcement gaps were never vocabulary.** The survey
      collected them while reading for terms, and keeping them here stopped this file closing.
      They are now [`the-gate-and-the-brief-disagree`](the-gate-and-the-brief-disagree.md),
      with two more found since: `query`'s evidence, and the `QUOTE` rules the brief dropped
      while the gate kept enforcing them.
