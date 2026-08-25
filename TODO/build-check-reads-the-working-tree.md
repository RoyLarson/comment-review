# build --check reads the working tree, so committed drift is invisible to it

```
Status:   open
Progress: 0 of 4 tasks done
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
