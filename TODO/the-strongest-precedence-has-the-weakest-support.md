# The role with verdict precedence has the least mechanical support

```
Status:   decision-needed
Progress: 2 of 4 tasks closed
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17, by the session that ran all eight stages -- "the weakest-verified input
          to the strongest-precedence role"
Re-verified: 2026-08-23 -- the ANCHOR half of this file is out of date. `census.py:454-458`
          now prints "! EVERY address carries an anchor -- the LINE OF CODE it attaches to,
          at both tiers", and `page.py:681` says a page returns a census "addressed and
          anchored". Two tasks that rested on "no anchor exists" are superseded; the
          finding itself survives, restated below
SPLIT:    2026-08-23 -- no box held two tasks. Every box is cut to two lines, the ruling's
          three candidate answers moved into the Objective, and the ruling gained the
          Verify clause it had never carried.
```

## Objective

**`ownership-context` wins every placement contest, and nothing can check the judgement it wins
with.**

- `SKILL.md:844`: *"`ownership-context`'s destination governs. Both findings stand; only the
  destination is ..."* And placement is applied FIRST, so its answer decides what code every
  other role's claim is measured against.
- `census.py:454-458` prints, every run: *"! EVERY address carries an anchor -- the LINE OF CODE
  it attaches to, at both tiers. What still needs READING is whether the prose belongs to it, so
  a placement finding is a CANDIDATE."*

So every `drop` and `move` it emits still rests on a reviewer reading the file. The collator checks
that its citations RESOLVE; nothing checks that the paragraph it says belongs to that anchor
belongs to it.

! It is disclosed rather than hidden -- the census says it in its own header -- but the
consequence was never drawn: the strongest-precedence role has the weakest-verified input.

!! **WHAT CHANGED, AND IT NARROWS THE FILE RATHER THAN CLOSING IT.** This file was written
2026-08-17 against a census that emitted an anchor only for a Python DOCSTRING, from the AST, and
none at the lexical tier -- measured that day on a Rust crate: no language server, no name
corpus, no anchors at all, and `ownership-context` still held the precedence. **Both tiers now
carry an anchor on every address.** What the anchor does NOT settle is whether the prose beside
it is ABOUT it, and that is the judgement the precedence rests on.

! **THE LSP `documentSymbol` ENRICHMENT IS A SEPARATE QUESTION.** It was named by the superseded
anchor task, and `SKILL.md` describes it as the task agent's by hand; it is not what that box
asked for.

## ! What the precedence is FOR, and why removing it is not the answer

The rule exists because a claim measured at the wrong anchor is measured against the wrong code,
and `correct`ing it there writes a falsehood. That reasoning is sound and the run produced
evidence for it -- five of eight placement findings in one pass were prose attached to the wrong
declaration.

!! **SO THE ANSWER IS NOT A TIE-BREAK BY ANOTHER RULE.** That would measure the claim against
whatever anchor won, which is the failure the precedence exists to prevent. The question this
file asks is whether anything can raise the CONFIDENCE of the input the precedence rests on --
not whether the precedence should stand.

## The candidates for the ruling

- **nothing**, and the census disclosure stands;
- **a second role's agreement** required before a `move` OUT of a paragraph;
- **the task agent re-deriving the placement itself** before applying it, which is what
  `write.md` already asks for claims.

! It is the same shape as
[`stage-5-is-the-only-stage-with-no-independent-reader`](stage-5-is-the-only-stage-with-no-independent-reader.md)
and may have the same answer.

## Corroboration is computed nowhere

VERIFIED 2026-08-23: `verdicts.contradictions` at `verdicts.py:225` compares `drop` against
`correct`/`patch` only, and its docstring says *"`move` is absent by ruling"* -- so two roles
agreeing on a destination produces no output at all. MEASURED 2026-08-17: `function-context` and
`ownership-context` agreed on a destination and only the task agent noticed.

## Tasks

- [?] T1 | T1 -- * RULE whether a placement verdict needs a second reader --
      candidates in the Objective. Verify: the ruling is recorded in
      `docs/decision-log.md`.
- [x] T2 | FINISHED | unknown | T2 -- SUPERSEDED. It asked for an anchor the
      census now emits on every address at both tiers -- `census.py:454-458` and
      `page.py:681`. Detail in the Objective.
- [x] T3 | FINISHED | unknown | T3 -- SUPERSEDED. Its premise -- no anchor at
      the `lexical` tier -- is false as of 2026-08-23. What survives is T1's
      question, which does not vary by tier.
- [ ] T4 | T4 -- Make the collator report when two roles independently name the
      SAME destination for one paragraph. Verify: a test hands it two such
      reports and asserts it appears.
