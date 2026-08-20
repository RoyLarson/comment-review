# Six mutations to shipped code survive the whole suite

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
```

## Objective

Six mutations to shipped code survive the whole suite.

## Tasks

- [ ] !! DELETING `verdicts.py:445-469` ENTIRELY -- the 25 lines that convert a
      reviewer's edit on front matter to a `query`, the one path stopping an edit
      landing on a licence header -- leaves 720 tests OK. The phrase occurs in
      tests only in a class DOCSTRING; no assertion anywhere that a verdict
      becomes `query`.
- [ ] Replacing `beside = c.emit(line)` in `foliate` with the `c` folio COMPUTED
      FROM the `b` folio -- the exact prohibition
      `test_a_folio_is_never_DERIVED_from_another` is named for -- leaves 720
      tests OK. That test asserts the absence of two deleted source strings.
- [ ] Forcing `hits = 0` in `check_vocabulary.py:295`, so the retired-word
      detector can never fire, leaves 720 tests OK.
      `test_a_retired_word_IS_caught` asserts `cv.RETIRED` is truthy; its comment
      says it *"guards the guard"*.
- [ ] Adding `"text": paragraph.get("text","")` to `record.slot()` --
      contradicting its own docstring, *"THE ADDRESS AND NOTHING ELSE"*, and the
      asymmetry the design rests on -- leaves 720 tests OK. The test forbids one
      key NAME, `original`.
- [ ] Replacing the JSON-mode refusal print in `census.py:377` with `pass` leaves
      720 tests OK: it prints to STDERR while the text-mode one prints to stdout,
      so `self._run("--json").stdout` is `''` and the assertion is vacuous.
- [ ] Adding `v = f.verdict` / `if v == "drop"` to `desk.payload_problem` passes
      `test_no_check_branches_on_a_VERDICT_NAME`, whose regex matches only
      `f.verdict ==`. `record.py:885` already binds `verdict =
      rec.get("verdict")`, so the escape is one line away in shipped code.
