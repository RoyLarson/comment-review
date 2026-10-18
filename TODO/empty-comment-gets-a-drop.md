# An empty comment gets a drop mark

```
Status:   open
Progress: 0 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-16 (lexer-python corpus verification, 2026-10-16)
```

## Objective

**A comment or docstring that holds no prose gets a `drop` mark automatically.**
Roy, 2026-10-16 -- `decision-log.md Process: #210`.

An empty docstring occupies a documentation position and tells a reader nothing.
Measured 2026-10-16: numpy's `lib/_user_array_impl.py` holds five `""`
docstrings (lines 227-243). The lexical Python reader reads each as an `a` place
of kind `docstring` with prose `''`.

No role can remove one today:

```text
def f():
    ""
    return 1

drop ""      -> refused: drop needs `claim.drop` to derive its change
drop '""'    -> ('    ""', [])   the paragraph unchanged, no problem reported
galley None  -> 'def f():\n    return 1\n'   the writer deletes it cleanly
```

So the writer can already delete it; what is missing is the mark. The system
raises it, not a role. The silent no-op in `derived_change` is filed separately
on `mark-defects`.

## Tasks

- [ ] T1 | Seed a drop mark at every comment or docstring paragraph whose prose
      is empty
        > 2026-10-16 Check: the f(): "" page seeds a drop at a1; proof writes it removed
        > 2026-10-16 Reason: decision-log Process #210, Roy 2026-10-16
