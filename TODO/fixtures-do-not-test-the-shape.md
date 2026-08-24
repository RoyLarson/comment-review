# A per-language fixture can pass without exercising the shape its language is measured on

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    testing
Requires-Roy: false
Raised:   2026-08-23 (2026-08-23, triaging matter-misses-two-languages: censusing the
          fixtures reported a PASS on a defect that is fully live)
Triaged:  2026-08-23 — ALREADY WELL FORMED. Every box is a verifiable checkpoint, so
          nothing changed but the T labels. ! Re-verified in place: `tests/fixtures/`
          holds 18 `sample.*` files, so "the other sixteen" is exact;
          `tests/fixtures/sample.ts` line 1 is `// fx.ts -- one small module.` and
          `tests/fixtures/sample.rs` line 1 is `//! A module-level doc comment.`
SPLIT:    2026-08-23 -- the first box named TWO LANGUAGES, and this repo's rule is that a
          language row takes its definition from its own grammar and never a neighbour's,
          so `sample.ts` and `sample.rs` are two boxes. The ruling gained a Verify clause.
```

## Objective

**A fixture that resembles its language is not a fixture that tests it**, and the difference
is invisible: the run is green either way.

!! **MEASURED 2026-08-23.** `matter-misses-two-languages` says a licence header is unprotected
in Rust and TypeScript. Censusing `tests/fixtures/sample.ts` types `f0` as `matter` -- a PASS --
so the defect reads as fixed. It is not: `sample.ts` opens with a LINE comment, and a `.ts`
opening `/**`, which is what a licence header does, types `f0` `dark-matter`. `sample.rs` opens
with `//!` and fails for a different reason than the one filed.

! **SO THE FIXTURE ANSWERED A QUESTION NOBODY ASKED.** It is a valid TypeScript file with
valid comments; it just never opens the way the defect requires. One line of difference, and
the opposite answer.

!! **THESE ARE LOAD-BEARING.** `test_fixture_identity.py` runs the round-trip identity over
every one, so they are the per-language evidence that the compositor sets a file back. If a
fixture does not carry a language's awkward shape, the identity passes on the easy case and
the corpus is where the defect is found instead -- late, and by hand.

! **AND THE TWO USES PULL OPPOSITE WAYS.** The round trip wants an ORDINARY file; a defect probe
wants the awkward one. If a fixture is both, one file cannot serve and the suite needs a second
set -- which is what the ruling has to settle.

! **This is `docs/gates.md`'s question at the fixture level**: not *does the check pass* but
*could it fail*. A fixture that cannot express the defect cannot fail on it.

## Tasks

- [ ] T1 -- Make `tests/fixtures/sample.ts` open the way a licence header does, or add a
      `.ts` fixture that does. Verify: it reproduces `matter-misses-two-languages`.
- [ ] T2 -- Make `tests/fixtures/sample.rs` open the way a licence header does, or add a
      `.rs` fixture that does. Verify: it reproduces `matter-misses-two-languages`.
- [ ] T3 -- Audit the other sixteen fixtures -- for each language row, name the shape its
      open TODOs are about. Verify: a list of language -> shape -> does it exercise it.
- [ ] T4 -- * RULE what a per-language fixture is FOR -- an ordinary file for the round
      trip, or a defect probe. Verify: the ruling says whether a second set is needed.
- [ ] T5 -- Say in `tests/fixtures/` what each file is a fixture OF, so a reader can tell
      coverage from resemblance. Verify: every `sample.*` names what it exercises.
