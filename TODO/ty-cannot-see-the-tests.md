# The type gate is scoped to src and cannot see the tests

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    systems (the gate) - backend (the test fixes)
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, Roy ruling that ty should pick up the tests as well,
          after four type errors in tests/test_collate.py were found by editor
          diagnostics and not by any gate -- ty check was scoped to src/comment_review/
          only)
```

## Objective

The type gate is scoped to src and cannot see the tests.

## Tasks

- [ ] Implement a `[tool.ty]` section in `pyproject.toml` naming both
      `src/comment_review/` and `tests/`, so the gate's SCOPE lives in config
      rather than on a command line where the next reader cannot see it. Verify: a
      bare `uv run ty check` covers both trees, and no invocation in `CLAUDE.md`
      passes a path.
- [ ] Update `tests/gates/test_build.py` and `tests/gates/test_dead_sweep.py` so
      their `scripts/` imports resolve for the checker. Verify: `ty` reports zero
      `unresolved-import`, and both tests still run.
- [ ] Delete every unguarded `.group(` on an unchecked match in `tests/`,
      replacing each with an assertion NAMING the pattern that failed. Verify:
      `ty` reports zero `unresolved-attribute`; a deliberately broken pattern
      fails with that assertion rather than `AttributeError: NoneType`.
- [ ] Implement the corrections for the ten `invalid-argument-type` and two
      `missing-argument` findings, fixing the CALL or the SIGNATURE rather than
      widening an annotation to admit what is passed. Verify: `ty` reports zero
      across both trees, and each fix names which of the two was wrong.
- [ ] Update `CLAUDE.md`'s command block to the bare invocation and state a DATED
      green baseline for `ty` over both trees. Verify: the block names no path,
      and the baseline sentence carries the date it was measured.
