# `ownership-context` is read FIRST, and nothing in the run makes that true

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    Roy (1 ruling) * session
Raised:   2026-08-16 (Roy: "Does this require a 4a, b, c -- 4a the ownership run,
          b the resolution and update to the pieces made by the reviewer so the
          other contexts can have a correct run, c the other reviewers run?")
```

## Objective

**SKILL.md says `ownership-context` is read FIRST because a claim attached to the wrong scope
is measured against the wrong code and `correct`ed into a falsehood. Three mechanisms could
deliver that, and none did.**

| mechanism | what it does today |
| --- | --- |
| dispatch order | **parallel.** *"Dispatch all four in ONE message so they run concurrently."* Ownership does not run first in time |
| synthesis order | in-code `move` was applied **LAST**, after `correct` and `patch` -- the text was corrected at the old anchor, then relocated |
| the join | `contradictions()` keyed on `drop` alone, so `move` + `correct` passed in silence |

! **Two of the three are fixed; the first is not.** Roy ruled *"moves first"* -- the synthesis
order now settles placement at step 2, before `correct` at step 3 -- and ruled the join should
flag `move` against `correct`/`patch`, which it now does. **Both act AFTER the reviewers have
read.** They catch a claim measured at the wrong anchor; they do not stop it being measured
there.

! **What is left is the reading itself.** All four reviewers read the same census concurrently,
so `block-context` measures a misplaced claim against whatever code it sits with, and spends a
verdict on it, before anything knows the placement is wrong. The join now sends that block back
-- which is a round trip, not a prevention.

## The shape Roy sketched

```
4a  ownership-context runs alone
4b  its placement verdicts are resolved, and the census updated
4c  the other three run against corrected placement
```

! **It is not free, and the costs are what the ruling has to weigh:**

- Stage 4 stops being one parallel dispatch. 4a and 4c are serial, so the run's wall-clock
  grows by one agent round trip.
- 4b relocates prose **before the author has ruled on anything**. Nothing reaches disk before
  7b, so this is a change to the census and the working text, not to files -- but it means the
  other three review prose at positions the author has not approved.
- A `move` at 4a and a `drop` at 4c on the same block still collide, so the join's
  contradiction check stays either way.

## Tasks

- [ ] * **Rule whether stage 4 serialises.** The alternative is to accept that the other three
      may spend a verdict on a misplaced block and let the widened join catch it -- cheaper, and
      it is what ships today.

- [ ] If it serialises: split stage 4 in `SKILL.md`, and say what 4b may touch. ! *"Nothing is
      on disk yet"* is stated at stage 6 and must stay true at 4b.

- [ ] If it serialises: `run_context.py`'s packet is written once per run and handed to four
      agents. A 4a/4c split needs either two packets or one that says which pass it is.

- [ ] If it does NOT serialise: `SKILL.md`'s *"`ownership-context` is read FIRST"* has to say
      what it actually means -- a SYNTHESIS precedence, resolved at stage 5 -- because as written
      a reader takes it for a dispatch order.

- [ ] Either way, re-read `ownership-context`'s own line: *"Your verdict settles which code
      every later reading measures the claim against."* Under the parallel design there is no
      later reading, only a later ruling.
