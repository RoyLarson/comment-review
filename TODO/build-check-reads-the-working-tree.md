# build --check reads the working tree, so committed drift is invisible to it

```
Status:   open
Progress: 1 of 6 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-08-25 (backend, 2026-08-25, chasing a reviewer note on the write-chain
          branch)
```

## Objective

build --check reads the working tree, so committed drift is invisible to it.

## Tasks

- [ ] T1 | Reproduce it: make src/ and plugins/ agree on disk while their
      committed blobs differ, and confirm --check still exits 0
- [ ] T2 | Decide what the check should compare -- the working tree, the index,
      or HEAD -- and say why in the script
- [ ] T3 | Make it able to see committed drift. Verify: the reproduction above
      turns it red
- [ ] T4 | A test that the check can FAIL on this specific cause, not only on a
      hand- edited file. tests/gates/test_build.py already proves four other
      causes bite
- [x] T5 | FINISHED | unknown | Format the branch's own unformatted work, so a
      bare ruff format . is safe to run again. Verify: MEASURED 2026-08-30 on
      feat/the-mark-and-the-collator, uv run ruff format --check . reported 24
      files would be reformatted, 147 already formatted, spanning src/, tests/,
      scripts/, evidence/ and the built plugins/ copies -- none of which ruff
      check can see. ! THE 24 ARE THIS BRANCH'S OWN WORK, written by an earlier
      session on it, and this task first recorded them as drift the branch did
      not cause. Roy, 2026-08-30: "I cleared the session that wrote those in
      this branch. They get their own commit but they get fixed now not later."
      Done: the repo is formatted once, in its own commit, and ruff check then
      reported one D210 in scripts/render_brief.py that the formatter itself
      created by spacing a docstring which opened on a quoted word.
- [ ] T6 | Update tests/gates/test_build.py so the build-STATE assertion is a
      release gate rather than a per-change one. The file already holds two
      questions on a class boundary: TestTheShippedTreeMatchesTheSource asserts
      the working tree is built right now and is what reddens every suite run,
      while TestTheCheckItselfFires proves the check can bite over four planted
      causes and does not depend on build state at all. Verify: a suite run over
      an unbuilt tree is green, the can-it-fail tests still run in it, and the
      release gate is red until build_plugin.py has run.
