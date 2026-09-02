# Eighteen defects in binder.py, and `read` admits four shapes it exists to refuse

```
Status:   open
Progress: 0 of 18 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-30 (2026-08-30, a code review of `binder/binder.py` run against its
          own docstrings -- eighteen tasks, and no TODO on the board is a home for that
          module)
```

## Objective

Eighteen defects in `binder/binder.py`, found on 2026-08-30 by running `read` against
the shapes its own docstrings say it refuses.

!! **THESE LAND TOGETHER, AND THAT IS WHAT EARNS THE FILE.** The module makes ONE
claim about itself -- `binder.py:239-242`, *"WHAT IS CHECKED IS WHAT IS CONSUMED and
no more"* -- and every admission below it is licensed by that sentence. M1 measures
that the sentence is written against a STALE inventory of consumers, so closing the
duplicate cue, the missing `path`, the missing `rows`, the boolean `revise`, the empty
`root` or the duplicate page one at a time leaves the rule that admitted the next one
standing. Landing any one without the others leaves the objective -- *`read` refuses
what its docstring says it refuses* -- unmet, which is the dependency test
`docs/conventions.md` sets.

## What was measured, by running it

- two rows carrying one `cue` on one page: `read` answers `''`,
  `desk/collator.py:119-123` keeps only the last row as `base_texts`,
  `flows/distribute.py:99-106` seeds both as marks at one address, and `drift_in`
  reports a role as drifted for returning the `raw_text` it was handed -- on which
  `commands/collate.py` exits DRIFT (5)
- a page with no `path`: `read` answers `''`, `rows_of` composes `""` for every
  address, `known_addresses` is empty, `drift_in` is a no-op, and a substantive mark
  refuses with a message blaming the ROLE for an address `seed` never gave it
- a page with no `rows`: `read` returns `(binder, '')` and a page whose rows array was
  lost reviews as a page with no prose, at exit 0
- `"revise": true` passes the guard, and a master_proof stamped `revise: true`
  compares equal in Python to a first edit_copy stamped `revise: 1`
- `{"root": "", "revise": 0}` passes, past a check whose own message asks which tree
  was censused, against `bind`'s argument that there is no default that would not be a
  fabrication
- two pages naming one `path` read with no refusal; `seed` produces `[('m.py', 'a'),
  ('m.py', 'b')]` while `flows/carry.py:124-128` breaks on the FIRST match and
  silently picks one

!! **AND `unaddressed` IS WHAT MAKES THE MISSING `path` SILENT RATHER THAN LOUD.**
`binder/addresses.py:177-187` names *"the collator before it certifies"* as a caller
and says *"IT IS ASKED AT BOTH ENDS ON PURPOSE"*; `grep -rn unaddressed
src/comment_review/` returns only `commands/census.py:334` and
`commands/addresser.py:131,257`. The collate path never asks.

! **THE PROSE TASKS ARE THE SAME MODULE'S SENTENCES ABOUT THOSE SAME GUARDS**, and
they go stale again the moment the guards move -- the SIX-fields header (`git log -S`
gives `7b26835`, where the row carried six), the `VERSION` comment true for exactly
one commit (`30b25c3`, corrected by `2226315`), the `CANNOT READ THE BINDER` citation
whose only hit today is `commands/carry.py:61`, and `rows_of` saying it puts a row's
`path` back when the dict union OVERRIDES it.

! **`_read_from_problem` IS SHARED ACROSS AREAS AND ITS MESSAGE IS NOT.** Three of its
five call sites are not binders, and `desk/collator.py:63` and `desk/containers.py:48`
each import the underscored name. That seam is also
[`containers-and-verification-are-unwired`](containers-and-verification-are-unwired.md)
task 5's, but the fix for these two lands in `binder/binder.py`.

## Tasks

- [ ] T1 | Implement a refusal in `binder.read` for two rows carrying one `cue`
      on one page. Verify: a page with rows `[{"cue":"b1","raw_text":"# FIRST"},
      {"cue":"b1","raw_text":"# SECOND"}]` returns a named `why`; today `read`
      answers `''`, `desk/collator.py:119-123` keeps only the last row as
      `base_texts`, `flows/distribute.py:99-106` seeds both as marks at one
      address, and `drift_in` reports a role as drifted for returning the
      `raw_text` it was handed, on which `commands/collate.py` exits DRIFT (5).
      The test goes red today.
- [ ] T2 | Implement the `path` check in `binder.read`, requiring a non-empty
      string on every page, on the terms `pages` already has at `binder.py:253`.
      Verify: a page carrying `{"sha": "abc", "rows": [...]}` and no `path` is
      refused by name; today `read` answers `''`, `rows_of` composes `""` for
      every address via `address_for("", cue)`, `known_addresses` is empty,
      `drift_in` is a no- op, and a substantive mark refuses with `mark 1:
      correct needs the address, copied from the row` -- which blames the ROLE
      for an address `seed` never gave it.
- [ ] T3 | Implement the `rows` presence check in `binder.read` at
      `binder.py:261`, so a page whose `rows` key is absent is refused rather
      than defaulting to `[]`. Verify: `read('{"read_from": {"root": ".",
      "revise": 0}, "pages": [{"path": "m.py"}]}')` is refused by name; today it
      returns `(binder, '')` and a page whose rows array was lost reviews as a
      page with no prose, at exit 0.
- [ ] T4 | Update the "WHAT IS CHECKED IS WHAT IS CONSUMED" paragraph at
      `binder.py:239-242`, which names `proof_setter.run` as a binder consumer.
      Verify: every consumer the paragraph names resolves --
      `flows/proof_setter.py:116` is `def run(docket: dict, repo: Path, into:
      Path)` and takes no binder -- and the live readers of a page's
      `path`/`sha` are named instead: `flows/distribute.py:88,98`,
      `flows/carry.py:125,137` and `flows/fan_out.py:99,120`.
- [ ] T5 | Update the citation in the same paragraph to `commands/proof.py`'s
      promise to print `CANNOT READ THE BINDER: {why}`. Verify: `grep -rn
      "CANNOT READ THE BINDER" src/` returns the file the sentence names --
      today the only hit is `commands/carry.py:61`.
- [ ] T6 | Update the `VERSION` comment at `binder.py:55-58`, which says `read`
      consumes no field and that `seed` is what raises on a missing `read_from`.
      Verify: it agrees with `binder.py:272`, where `read` calls
      `_read_from_problem(loaded)` and returns a named refusal, and with that
      function's own docstring at `binder.py:188-190`; no two comments in the
      file state opposite rules for one code path.
- [ ] T7 | Update `_read_from_problem` so its refusals name the artifact its
      caller handed it and its name matches the reuse across areas. Verify:
      `collator.problems_in({"role": "block-context", "sheets": []})` no longer
      reports `the report's carries no read_from -- a binder written before
      2026-08-28`; the message is a sentence and does not tell an operator to
      re- run `census --json` over a role's edit_copy; and no module under
      `desk/` imports an underscored name from `comment_review.binder.binder` --
      today `desk/collator.py:63` and `desk/containers.py:48` both do.
- [ ] T8 | Update the `revise` check at `binder.py:220` to `type(x) is int`, so
      a JSON boolean is refused. Verify: `_read_from_problem({"read_from":
      {"root": ".", "revise": True}})` returns a named refusal -- today `''` --
      and `desk/containers.py:228` no longer passes a master_proof stamped
      `revise: true` against a first edit_copy stamped `revise: 1`, which
      compare equal in Python.
- [ ] T9 | Implement the read-side `unaddressed` call the collate path is
      missing, at `binder.read` or at `commands/collate.py`'s binder load.
      Verify: `grep -rn unaddressed src/comment_review/` returns a caller on the
      collate path -- today only `commands/census.py:334` and
      `commands/addresser.py:131,257` -- and a binder row whose address composes
      to `""` is reported rather than dropped by `desk/collator.py:99,122`.
- [ ] T10 | Update the module header at `binder.py:33`, which says an agent gets
      SIX fields. Verify: it agrees with `page_row`'s "FIVE FIELDS, RULED ONE BY
      ONE" at `binder.py:65` and the five keys at `:75-103`, and states what a
      role is actually handed -- the four keys `{address, anchor, raw_text,
      instruction}` that `desk/mark.py:326-356` builds.
- [ ] T11 | Update `_read_from_problem` to refuse an empty `root`. Verify:
      `_read_from_problem({"read_from": {"root": "", "revise": 0}})` is refused
      -- today `''` -- and `bind([], {"root": "", "revise": 0})` no longer emits
      `"read_from": {"root": "", ...}`.
- [ ] T12 | Update the missing-`read_from` refusal at `binder.py:210-213` to
      read `loaded["version"]` instead of asserting the artifact is version "1".
      Verify: `read('{"version": "9", "pages": []}')` does not state a version
      it declined to check.
- [ ] T13 | Update every refusal that renders `type(x).__name__` to name the
      JSON type. Verify: `binder.py:216-217,257,260,263,266-267` and
      `machine/json_object.py:47` emit `null`, `string`, `boolean`, `number`,
      `array` or `object`, and `grep -rn "NoneType" src/comment_review/` returns
      no refusal text.
- [ ] T14 | Implement a refusal for two pages naming one `path`. Verify: a
      binder with two pages both `"path": "m.py"`, one `"sha": "a"` and one
      `"sha": "b"`, is refused by name; today it reads with no refusal and
      `seed` produces `[('m.py', 'a'), ('m.py', 'b')]`, while
      `flows/carry.py:124-128` breaks on the FIRST match and silently picks one.
- [ ] T15 | Update `rows_of`'s docstring at `binder.py:294-297` to say it
      OVERRIDES a row's `path` and `address` rather than putting them back.
      Verify: the sentence matches `row \| {"path": path, "address": ...}`,
      whose dict-union order turns a row carrying `{"path": "other.py",
      "address": "other.py@b9"}` into `{'path': 'm.py', 'address': 'm.py@b1'}`.
- [?] T16 | Does `--include-absent` describe the binder ARTIFACT, or only the
      invocation that produced it? Verify: the answer is recorded in
      `docs/decision-log.md`; if it describes the artifact, `read_from` carries
      `absent` and a copy seeded from an include-absent binder then collated
      against a default one is refused rather than reporting every `interval`
      and `margin` mark as naming a place the binder does not carry.
- [ ] T17 | Update `bind`'s `ValueError` docstring at `binder.py:152-156` to
      state that no shipped caller can reach the guard. Verify: it names the
      four internal callers -- `commands/census.py:331`, `flows/revise.py:239`,
      `commands/taken_in.py:94,97` -- and says the guard is depth for an
      importable boundary function, the way `flows/carry.py:97-99` states
      "UNREACHABLE BY CONSTRUCTION ... It is here so a future lookup added
      without its own branch fails loudly".
- [ ] T18 | Update `commands/collate.py:69-81` (`_load`) to call
      `machine.json_object.object_of` instead of restating the
      parse-plus-object- guard preamble. Verify: `grep -rn "not an object"
      src/comment_review/` shows the refusal sentence stated once, and
      `binder.py:22-26`'s claim -- "THE FORMAT IS A CONTRACT AND BELONGS TO
      NEITHER END ... one module both sides import is the fix" -- holds across
      the repo rather than in two of three places.
