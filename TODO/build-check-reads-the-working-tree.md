# build --check reads the working tree, so committed drift is invisible to it

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-25 (backend, 2026-08-25, chasing a reviewer note on the write-chain
          branch)
```

## Objective

build --check reads the working tree, so committed drift is invisible to it.

## Tasks

- [ ] Reproduce it: make src/ and plugins/ agree on disk while their committed
      blobs differ, and confirm --check still exits 0
- [ ] Decide what the check should compare -- the working tree, the index, or HEAD
      -- and say why in the script
- [ ] Make it able to see committed drift. Verify: the reproduction above turns it
      red
- [ ] A test that the check can FAIL on this specific cause, not only on a hand-
      edited file. tests/gates/test_build.py already proves four other causes bite
- [ ] Update CLAUDE.md's command table, or the repo, so that a bare ruff format .
      is safe to run. Verify: MEASURED 2026-08-30 on feat/the-mark-and-the-
      collator, uv run ruff format --check . reports 24 files would be
      reformatted, 147 already formatted -- the drift spans src/, tests/ and the
      built plugins/ copies, and ruff check does not see any of it. So the command
      CLAUDE.md tells a session to run rewrites 24 files it did not touch,
      including plugins/, which the release rule says is built rather than edited.
      Either the repo is formatted once and the drift goes, or the table says to
      scope the formatter to what the change touched.
