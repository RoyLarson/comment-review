# The emitted vocabulary can collide with the reviewed repo's own terms

```
Status:   open
Progress: 1 of 6 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17 (a run declared the collision in its style sheet without being asked:
          "block collides (training block / comment run) and stays collided")
Triaged:  2026-08-23 -- the counts were re-taken and the worked example is retired.
          `block` no longer ships; the collision it demonstrated is now demonstrated
          by the words that replaced it
Split:    2026-08-23 -- 4 boxes became 6. The style-sheet box held the section and the
          rule it must state; the reviewer box held a decision and the sentence it fixes
Roy, 2026-08-28: 2026-08-28 — Ruled: stays open. Yes -- still requires a fix to get the
                 local repo's own semantics separated from comment-review's semantics.
                 Re-verified against the tree the same day: vocabulary.toml still holds
                 59 definitions (0 holes, 0 duplicates, 0 drift, 0 retired-word uses per
                 check_vocabulary.py); per-role counts unchanged at 43/42/43/46; all ten
                 example collision terms (page, census, record, sentence, statement,
                 series, cue, owner, anchor, mark) are still defined and still given to
                 ownership-context; SKILL.md 1.5's style sheet section (247-274) still
                 has no COLLISIONS subsection, so T2-T5 are still not done. New since
                 the last triage: the delivery mechanism T5 targets, vocabulary.py,
                 moved to prototype/ on 2026-08-25 and is not shipped or run -- SKILL.md
                 now says handing over a role's vocabulary by command is absent, tracked
                 in the-skill-names-commands-that-moved-to-prototype.md. A fix to T5 has
                 to land wherever that TODO decides the vocabulary reaches a role now,
                 not by editing the retired prototype file.
```

## Objective

**Every reviewer is handed a vocabulary and told *"These words have one meaning in this
system."* Nothing checks those words against the repo being reviewed.**

MEASURED 2026-08-23: `references/vocabulary.toml` holds 59 definitions, and
`vocabulary.terms_for` gives `ownership-context` 43, `block-context` 42, `function-context` 43
and `module-context` 46 of them. `vocabulary.py:72-73` renders the header verbatim into each
prompt: *"These words have one meaning in this system. Where you are unsure what a word means,
it is here; where it is not here, it is ordinary English."*

! **The 2026-08-17 worked example is retired and the hazard is not.** `block` was the term that
collided on a training-plan codebase, where it means a training block. It is no longer emitted
-- `paragraph` replaced it, and `scripts/check_vocabulary.py`'s RETIRED check refuses its return
(*"`block` survived in 298 places after `paragraph` replaced it"*). The words that ship in its
place are the same kind of word: measured against `vocabulary.toml`, the emitted set includes
`page`, `census`, `record`, `sentence`, `statement`, `series`, `cue`, `owner`, `anchor`
and `mark` -- each of which an ordinary codebase can use for something else, and all ten
verified 2026-08-23 as terms `ownership-context` is GIVEN rather than merely defined.

! `scripts/check_vocabulary.py` proves the shipped tree consistent with itself -- 59 definitions
across 6 roles, 0 holes, 0 defined twice, 0 roles drifted, 8 retired words unused. It says
nothing about the tree under review, correctly: it is a repo tool and the review happens
elsewhere.

! `SKILL.md:257-264` asks the style sheet for *"terms of art with a fixed meaning"* -- the
REPO's terms. It does not ask which of them collide with ours, and the collision is the
dangerous half.

## ! What LOOKING for collisions would cost, and the recommendation

Looking is cheap and mechanical -- the emitted set is a fixed list of at most 46 keys per role
and the tree is greppable -- **but it will surface words like `record`, `page` and `owner` on
almost any codebase, and a list of forty near-misses is noise.** ! Recommendation: grep the keys
against IDENTIFIERS only, not prose, so a hit means the repo has a symbol by that name.

## !! Declared polysemy is the settled answer, and the sheet is where it goes

`docs/vocabulary.md`: *"Polysemy is allowed when it is DECLARED and the contexts do not
overlap"* -- `opener`, `annotations`, `node`. The same rule covers this, one level out: a term
this system emits and the repo also uses is polysemous **across** the two vocabularies, and an
undeclared collision is the defect.

! The 2026-08-17 run reached that on its own and wrote *"stays collided"* -- declaring it rather
than resolving it, which is right. Neither vocabulary may be renamed to suit the other, so the
only useful move is telling the reader both meanings are live.

!! **AND A REPO TERM MUST NOT BE ADDED TO `vocabulary.toml`.** That file holds what agents are
GIVEN across every run, and `check_vocabulary.py`'s drift check refuses a term no role's text
uses -- so a repo's term would fail the gate on the next run against a different repo. A repo's
term belongs to the repo's sheet. This is settled, it is already ENFORCED, and it is not work.

## Tasks

- [ ] T1 -- * Rule whether stage 1 must LOOK for collisions or only record one a reviewer
      trips over. Verify: the answer is written into this file.
- [ ] T2 -- Add a COLLISIONS section to the style sheet at `SKILL.md:257-264`. Verify: a
      run over a repo defining an emitted term as a symbol lists it.
- [ ] T3 -- State in that section that a collision is DECLARED rather than resolved.
      Verify: the section says neither vocabulary may be renamed to suit the other.
- [ ] T4 -- Decide whether a declared collision reaches the REVIEWERS; the sheet is in the
      stage-4 packet, so today it would. Verify: the answer is written into this file.
- [ ] T5 -- Fix `vocabulary.py:73`, whose *"it is ordinary English"* is wrong for a
      collided term. Verify: the header names COLLISIONS or the term carries both.
- [x] T6 -- Not a task, and now in the Objective: adding a repo term to `vocabulary.toml`
      is a rule nobody ticks and is already enforced.
