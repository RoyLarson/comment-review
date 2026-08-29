# Only one role's remit is a closed set, and its three terms are undefined

```
Status:   blocked
Progress: 0 of 4 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-29, checking whether `state` was free for the harness to take as a term
Blocked:  on the machinery release closing. `decision-log.md Process: #51` -- a version
          changes the AGENTS or the MACHINERY, never both -- and the current work is the
          machinery half. Roy, 2026-08-29: "those unfortunately cannot land now because
          we are in the middle of the program side update still which excludes changes
          to the agent side changes". ! T4 additionally waits on
          `vocabulary-sweep-reads-a-moved-path`
```

## Objective

**`block-context` is the only role whose remit is a counted closed set, and none of the three
terms in it is defined anywhere.** Found while checking whether the harness could take `state` as
its own word; it could not, and the reason turned out to be a finding rather than a collision.

`comment-review-block-context.md:21-27` states it as a count -- *"Three kinds of claim, and all
three are yours"* -- then lists **State**, **Constraint** and **Worked example**. The other three
roles name their remits as section headings instead:

| role | how the remit is named |
| --- | --- |
| `block-context` | a **counted closed list of three** |
| `function-context` | headings -- *Reachability lives here*, *A coverage claim is CHECKED*, *A prohibition is resolved against its own file*, *The absence question* |
| `module-context` | headings -- *A universal is a CHECKLIST*, *The module's own surface is a CHECKLIST*, *Module level is yours* |
| `ownership-context` | *"You rule on TWO propositions"* -- counted, but propositions rather than claim-kinds |

!! **A COUNTED SET IS SELF-CHECKABLE AND A SET OF HEADINGS IS NOT.** A role told *"three kinds,
all three yours"* can ask whether it considered all three before emitting `clean`; a role whose
remit is section headings cannot, and one it skipped leaves no trace. **Nothing in the record says
the asymmetry was decided** -- which is what T1 is for. It may be right that only
`block-context`'s remit enumerates cleanly; that is an answer, and it is not written down.

!! **AND THE THREE TERMS ARE IN NO VOCABULARY.** MEASURED 2026-08-29: `vocabulary.toml` defines
**51** terms -- `banner`, `laundering`, `truthy`, `obituary`, `invariant` among them -- and
**`state`, `constraint` and `worked example` are not among them.** The closed set a role's whole
`clean` rests on is undefined bolded prose.

! **NO GATE CAN SEE THIS.** `check_vocabulary.py` asks whether every term a role is GIVEN has a
definition, whether a definition was written for nobody, and whether a role was given a term its
text never uses. It passes: `block-context`'s given list does not contain `state`, so there is
nothing to be undefined. **The question it does not ask is whether a term of art IN the text was
ever declared** -- which is `vocabulary_sweep.py`'s, and that has crashed at startup since the
2026-08-24 package move (`vocabulary-sweep-reads-a-moved-path`).

## !! `state` CARRIES FOUR SENSES IN WHAT AN AGENT READS

| site | sense |
| --- | --- |
| `agents/comment-review-block-context.md:23` | the claim-kind -- the program as it is NOW, not as it was or will be |
| `agents/comment-review-block-context.md:99` | RUNTIME state, from another machine |
| `agents/comment-review-module-context.md:66` | MODULE-LEVEL mutable data |
| `references/reviewer-brief.md:121` | the FILE's condition at a moment -- *"the state your `place` and your `anchor` were taken from"* |

Plus the ordinary verb throughout -- *"state the POPULATION you enumerated over"*
(`block-context.md:58`), *"a defect you state in `reason`"* (`reviewer-brief.md:187`).

! **DEFINING THE WORD BEFORE SETTLING THE SENSES WOULD MAKE THREE SITES WRONG**, which is why T3
sits beside T2 rather than after it. A definition picks one sense; the other three then say
something the vocabulary denies.

! **THE HARNESS TOOK `variant` INSTEAD**, and that decision stands whatever this file concludes --
`decision-log.md Vocabulary: #30`. The trade's own word for the thing was `state`, and it was
refused on this collision.

## Tasks

- [ ] T1 -- * RULE whether the other three roles get counted closed sets like
      `block-context`'s three claim-kinds. Verify: the answer is written into this
      file.
- [ ] T2 -- Define `state`, `constraint` and `worked example` -- or whatever
      replaces them -- in `vocabulary.toml`. Verify: `check_vocabulary.py` passes
      and each appears in `block-context`'s given terms.
- [ ] T3 -- Settle the four senses of `state`, so no site uses the word for
      something the definition does not cover. Verify: every remaining use
      resolves to the declared term.
- [ ] T4 -- Rule every row `vocabulary_sweep.py` returns for the four agent files,
      once it runs again. Verify: each row is a term or is recorded as not one.
