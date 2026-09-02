# A revise copies the whole tree, so one pull moves 284MB to change 4MB of source

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28 (2026-08-28, verifying task 8 of the mark-and-the-revise SP --
          `pull` calls `shutil.copytree(repo, into)` with no filter, and `proof` routes
          through it at task 12)
Measured: 2026-08-28 — 2026-08-28, a code review over the branch, re-measuring what was
          filed earlier the same day. THE GATE DOUBLES THE COST, which the original
          filing missed: `assert_addresses_held` censuses BOTH trees in full, and
          `walk_files` yields 5,650 files on this checkout of which 3,341 have a
          language record and **3,153 are under `corpora/`** -- so numpy, sentry and
          pymc sources are read TWICE per pull. `copytree` additionally copies what the
          walk excludes: `corpora` 178MB, `.venv` 71MB, `.git` 13.6MB, `.codegraph`
          12.9MB -- roughly 283MB and 7,500 files. !! AND IT IS A CORRECTNESS SURFACE,
          NOT ONLY A COST. `.venv` on Windows holds junctions and locked files, and
          `shutil.copytree(symlinks=False)` raises `shutil.Error` on a broken link -- so
          a pull can fail for a reason that has nothing to do with the review. ! IT IS
          ALSO LIVE NOW: task 12 routed `commands/proof.py` through `revise.pull`, so
          `proof --repo . --out ../r1` over a one-comment docket takes this path today,
          where it previously wrote a single drafted page.
```

## Objective

A revise copies the whole tree, so one pull moves 284MB to change 4MB of source.

## Tasks

- [ ] T1 | Decide what a revise root holds, and write the decision where `pull`
      can be read against it. The candidates are: every tracked file (`git
      ls-files`), everything not ignored, or everything. Verify:
      `flows/revise.py` states the rule and cites where it was decided.
- [ ] T2 | Make `pull` copy that set. ! `a_small_real_tree` in
      `tests/helpers.py` is NOT a git checkout, so a `git ls-files`
      implementation needs a path for a plain directory -- name it rather than
      letting the tests pick it silently. Verify: a `pull` over this repo copies
      no `.git`, `.venv` or `corpora` entry.
- [ ] T3 | Measure it again after the change. Verify: the byte count copied for
      one revise over this repo is recorded here, against the 284MB measured
      2026-08-28.
- [ ] T4 | Check what the address-invariance gate was comparing.
      `assert_addresses_held` censuses both roots; if the revise held `corpora/`
      and the original did too, the gate was walking 197MB of other people's
      repositories on every pull. Verify: the address sets the gate compares are
      named, and hold only files under review.
