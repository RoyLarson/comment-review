# A per-language fixture can pass without exercising the shape its language is measured on

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    testing
Requires-Roy: false
Raised:   2026-08-23 (2026-08-23, triaging matter-misses-two-languages: censusing the
          fixtures reported a PASS on a defect that is fully live)
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

! **This is `docs/gates.md`'s question at the fixture level**: not *does the check pass* but
*could it fail*. A fixture that cannot express the defect cannot fail on it.

## Tasks

- [ ] Make `sample.ts` and `sample.rs` exercise the matter case, or add fixtures
      that do. MEASURED: `sample.ts` opens with a LINE comment and `sample.rs`
      with `//!`, so neither opens the way a licence header does. Censusing them
      types TS `f0` as `matter` -- a pass -- while a `.ts` opening `/**` types
      `dark-matter`. Verify: the fixture reproduces what `matter-misses-two-
      languages` measures.
- [ ] AUDIT THE OTHER SIXTEEN the same way. For each language row, name the shape
      its open TODOs are about and check the fixture opens that way. Verify: a
      list of language -> shape -> does the fixture exercise it.
- [ ] * RULE what a per-language fixture is FOR. `test_fixture_identity.py` runs
      the round trip over them, which wants an ORDINARY file; a defect probe wants
      the awkward one. If it is both, one file cannot serve and the suite needs a
      second set.
- [ ] Say in `tests/fixtures/` what each file is a fixture OF, so the next reader
      can tell coverage from resemblance.
