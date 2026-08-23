# Stage 4b is referenced everywhere and defined nowhere

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
```

## Objective

Stage 4b is referenced everywhere and defined nowhere.

## Tasks

- [ ] !! `SKILL.md:549` splits stage 4 into *"4a ownership alone, 4c the other
      three against its RESOLVED PLACEMENT"*, but no `4b` is defined anywhere in
      the shipped tree -- the token appears only in `docs/plans/0.2.4-...md:423`.
- [ ] !! AND NOTHING PRODUCES A RESOLVED PLACEMENT. `SKILL.md:661` seeds all four
      roles from the same `census.json` BEFORE dispatch, and `:606` says all four
      are handed the same stage-2 `dispatch.txt`. So the serialisation only DELAYS
      the three: `block-context` still verifies a misfiled note against the
      passage it was misfiled into, which is the precise failure
      `SKILL.md:555-558` says the ordering prevents.
- [ ] `reviewer-brief.md:446` still tells all four that *"remits overlap by design
      ... two roles can reach different placement decisions"*, and `SKILL.md:3`
      still advertises *"parallel read-only subagents"*.
- [ ] `run_context.py:52` compounds it: `LOOKUP CENSUS` is now in `REQUIRED` so
      `--check` refuses any packet without it, while `SKILL.md` never mentions the
      section and still says it refuses *three* answers. A run following SKILL.md
      fails its own stage-4 gate.
- [ ] * RULING WANTED: what 4b IS. Either it is a real step that resolves
      placement between 4a and 4c, or the split is 4a/4b and the prose is wrong.
      The boxes cannot be checked until the stage exists or the claim goes.
