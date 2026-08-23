# Six shipped docstrings contradict themselves or their own bodies

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
```

## Objective

Six shipped docstrings contradict themselves or their own bodies.

## Tasks

- [ ] `addresser.py:840-846` says *"SHARED IS NOW A FAULT TOO"*; `:849-851`, same
      docstring, says *"A shared place does not fail the check"*; the code at
      `:890` is `return 1 if unaddressed else 0`. And `:880-884` prints advice to
      *"cite the census index alongside the address"* -- a field retired
      2026-08-19, which `record.slot()` does not emit. `record.py:42` still tells
      a reviewer filing an `add` to write it.
- [ ] `galley.py:253-255` says it reads `original_*`, *"falling back to
      `start`/`end` ... The fallback is why this function is still here"*;
      `:269-273` says *"No fallback ... a missing one here is a bug and should
      raise"*.
- [ ] `lexer.py:118-120` says an empty interval *"reports `(n+1, n)`"*;
      `:152-154`, same comment block, says *"THERE IS NO EMPTY-SLICE SENTINEL ...
      `None` cannot be mistaken for a position."* The code emits `None`.
- [ ] `page.py:102-107` calls `HOLDS_NO_PROSE` *"a DIFFERENT set, and the two are
      not interchangeable"*. `set(OCCUPIES_NOTHING) == set(HOLDS_NO_PROSE)` is
      `True` -- the justification rested on `trailing-comment`, removed from the
      first set on this branch.
- [ ] `record.py:747-751` says an address identifying one paragraph is *"held by
      `foliator.py --check` on every run"*. It is not held -- `--check` reports
      SHARED and returns 0.
- [ ] Retired concepts still named: `desk.py:482` *"the paragraph the census has
      AT THAT INDEX"* (body calls `entry_for(address)`); `desk.py:244` names a
      `LOCATION` field that was dropped; `verdicts.py:117,191,231,255` say
      *"Indices"* where everything is keyed by address; `held.py:526` *"two
      records that share an index"*.
