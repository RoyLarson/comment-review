# The role with verdict precedence has the least mechanical support

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session * Roy (* 1 ruling)
Requires-Roy: true
Raised:   2026-08-17, by the session that ran all eight stages -- "the weakest-verified input
          to the strongest-precedence role"
```

## Objective

**`ownership-context` wins every placement contest, and nothing can check the judgement it wins
with.**

- `SKILL.md`: *"Two placement verdicts on one block, naming different destinations:
  `ownership-context`'s destination governs."* And placement is applied FIRST, so its answer
  decides what code every other role's claim is measured against.
- `census.py` prints, every run: *"! NO COMMENT carries an anchor at either tier. A comment's
  anchor comes from READING the file, so a placement finding is a CANDIDATE."*

So every `drop` and `move` it emits rests on a reviewer reading the file. The join checks that
its citations RESOLVE; nothing checks that the anchor it picked is the right one.

! It is disclosed rather than hidden -- the census says it in its own header -- but the
consequence was never drawn: the strongest-precedence role has the weakest-verified input.

!! **And it degrades further than the notice suggests.** At the `tokenized` tier only a
DOCSTRING carries an anchor, from the AST; a comment never does. At the `lexical` tier nothing
does. Measured 2026-08-17 on a Rust crate: no language server, no name corpus, no anchors at
all -- and `ownership-context` still held the precedence.

## ! What the precedence is FOR, and why removing it is not the answer

The rule exists because a claim measured at the wrong anchor is measured against the wrong code,
and `correct`ing it there writes a falsehood. That reasoning is sound and the run produced
evidence for it -- five of eight placement findings in one pass were prose attached to the wrong
declaration.

! So the question is not whether the precedence is right. It is whether anything can raise the
confidence of the input it rests on.

## Tasks

- [ ] * Rule on whether a placement verdict needs a second reader when no anchor is available.
      ! It is the same shape as
      [`stage-5-is-the-only-stage-with-no-independent-reader`](stage-5-is-the-only-stage-with-no-independent-reader.md)
      and may have the same answer. Candidates: nothing, and the disclosure stands; a second
      role's agreement required before a `move` OUT of a block; or the task agent re-deriving
      the anchor itself before applying placement, which is what `write.md` already asks for
      claims.

- [ ] Give the census an anchor wherever one is available and it currently emits none. ! A
      language server answers this -- `documentSymbol` returns the declaration on the line after
      a run ends -- and 1.7 already probes for one. What is missing is the census USING it: the
      enrichment is described in `SKILL.md` and performed by the task agent by hand.

- [ ] Say what a placement verdict is worth at the `lexical` tier, where no anchor exists in
      any language. ! Today it is worth the same as one at `tokenized`, and the precedence
      does not vary by tier.

- [ ] Check whether the join could compare placement verdicts ACROSS roles as a signal. Two
      roles independently naming the same destination is corroboration the run currently
      computes and discards -- measured on 2026-08-17, `function-context` and `ownership-context`
      agreed on a destination and only the task agent noticed.

- [ ] ! Do not resolve this by weakening the precedence. A tie-break by another rule would
      measure the claim against whatever anchor won, which is the failure the precedence exists
      to prevent.
