# The emitted vocabulary can collide with the reviewed repo's own terms

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session * Roy (* 1 ruling)
Requires-Roy: true
Raised:   2026-08-17 (a run declared the collision in its style sheet without being asked:
          "block collides (training block / comment run) and stays collided")
```

## Objective

**Every reviewer is handed 43 definitions and told *"These words have one meaning in this
system"*. Nothing checks those words against the repo being reviewed.**

Measured: on a training-plan codebase, **`block`** means a training block. The emitted
vocabulary defines it as *"The interval between two lines of CODE."* A reviewer reading prose
about *"the block"* in that repo holds two meanings and was handed one, with an instruction that
sounds authoritative.

! `scripts/check_vocabulary.py` proves the shipped tree consistent with itself -- every key
defined, no definition unused, no role given a term its text never uses. It says nothing about
the tree under review, correctly: it is a repo tool and the review happens elsewhere.

! `SKILL.md` 1.5 asks the style sheet for *"terms of art with a fixed meaning"* -- the REPO's
terms. It does not ask which of them collide with ours, and the collision is the dangerous half.

## !! Declared polysemy is the settled answer, and the sheet is where it goes

`docs/vocabulary.md`: *"Polysemy is allowed when it is DECLARED and the contexts do not
overlap"* -- `opener`, `annotations`, `node`. The same rule covers this, one level out: a term
this system emits and the repo also uses is polysemous **across** the two vocabularies, and an
undeclared collision is the defect.

! The 2026-08-17 run reached that on its own and wrote *"stays collided"* -- declaring it rather
than resolving it, which is right. Neither vocabulary may be renamed to suit the other.

## Tasks

- [ ] * Rule on whether stage 1 must LOOK for collisions, or only record them when a reviewer
      trips over one. ! Looking is cheap and mechanical -- the 43 keys are a fixed list and the
      tree is greppable -- but it will surface words like `block`, `record` and `mark` on almost
      any codebase, and a list of forty near-misses is noise. Recommendation: grep the keys
      against IDENTIFIERS only, not prose, so a hit means the repo has a symbol by that name.

- [ ] Add a COLLISIONS section to the style sheet, beside the terms of art, and state that a
      collision is DECLARED rather than resolved. ! Say why: neither vocabulary may be renamed
      to suit the other, so the only useful move is telling the reader both meanings are live.

- [ ] Decide whether a declared collision reaches the REVIEWERS. The sheet is in the stage-4
      packet, so it would, but the emitted vocabulary says *"where it is not here, it is
      ordinary English"* -- which is wrong for a collided term and is the sentence that makes
      the collision dangerous.

- [ ] ! Do not add repo terms to `vocabulary.toml`. That file holds what agents are GIVEN
      across every run, and the drift check refuses a term no role uses. A repo's term belongs
      to the repo's sheet.
