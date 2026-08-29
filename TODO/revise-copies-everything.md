# A revise copies the whole tree, so one pull moves 284MB to change 4MB of source

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28 (2026-08-28, verifying task 8 of the mark-and-the-revise SP --
          `pull` calls `shutil.copytree(repo, into)` with no filter, and `proof` routes
          through it at task 12)
```

## Objective

A revise copies the whole tree, so one pull moves 284MB to change 4MB of source.

## Tasks

- [ ] Decide what a revise root holds, and write the decision where `pull` can be
      read against it. The candidates are: every tracked file (`git ls-files`),
      everything not ignored, or everything. Verify: `flows/revise.py` states the
      rule and cites where it was decided.
- [ ] Make `pull` copy that set. ! `a_small_real_tree` in `tests/helpers.py` is
      NOT a git checkout, so a `git ls-files` implementation needs a path for a
      plain directory -- name it rather than letting the tests pick it silently.
      Verify: a `pull` over this repo copies no `.git`, `.venv` or `corpora`
      entry.
- [ ] Measure it again after the change. Verify: the byte count copied for one
      revise over this repo is recorded here, against the 284MB measured
      2026-08-28.
- [ ] Check what the address-invariance gate was comparing.
      `assert_addresses_held` censuses both roots; if the revise held `corpora/`
      and the original did too, the gate was walking 197MB of other people's
      repositories on every pull. Verify: the address sets the gate compares are
      named, and hold only files under review.
