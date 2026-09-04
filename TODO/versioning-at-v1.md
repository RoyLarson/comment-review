# v1.x wants a concrete versioning system on everything that ships

```
Status:   deferred
Progress: 3 of 12 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, ruling out any versioning investment before v1)
Triaged:  2026-08-23 -- three of the four boxes were the ruling itself and the reasoning
          kept with it. They are ticked and stated in the Objective; ONE task remains and
          it does not start before v1.x
Split:    2026-08-23 -- the one open box named four artifacts, a statement and a test, so
          it became six; a second pass split the record field from the `RECORD_VERSION`
          retirement, the manifest from the release gate, and the refusal from the proof
          that it can fail, so six became twelve. Every box is two lines
```

## Objective

**v1.x wants a concrete versioning system on everything that ships. Nothing before v1 owes one.**

!! **RULED 2026-08-21, DEFERRED TO v1.x.** Roy: *"when we get to a v1.X we will want a concrete
versioning system on everything that ships with v1.X and future ... until then nah."* A 0.x
states that ALL things are subject to shifting -- zero-vers are specifically for that, with no
guarantee of any stability -- so nothing before v1 owes a compatibility story. **The event this
waits on is the v1.0 tag, and no box below starts before it.**

! **WHAT EXISTS TODAY IS NOT THAT SYSTEM.** `RECORD_VERSION` is one constant on one artifact,
moved by hand -- verified 2026-08-23 at `record.py:639`, written into a record at `:873` and
compared on read at `:1020-1028`. 2026-08-21 measured that it does not get moved: it stayed put
across an incompatible shape change while the comment above it described exactly that failure.
! It is kept because it costs a line, not because it works.

! **AND THE PARSE REFUSAL IS WHAT ACTUALLY CATCHES A WRONG SHAPE.** Roy: a loud *"unable to parse
-- unknown format"* is enough, and it does not matter whether the file is an old version or a
current one mangled. A version field only adds the case a parse cannot see -- **keys in the same
places meaning something else.** ! That single case is the whole argument for building anything,
and it is why the answer is *later* rather than *never*. **It is the argument the tasks below
have to satisfy.**

! **WHEN IT IS BUILT, IT COVERS EVERYTHING THAT SHIPS**, not just the record: the census, the
record file, the run context, the plugin manifest. **One scheme, stated once.**

! **Deferred is not done.** Roy, 2026-08-18: *"Deferred is not done - just waiting so its status
is still correct."* The boxes below stay unchecked because the work has not started, which is
what an unchecked box already says.

## Tasks

- [ ] T1 | T1 -- **State the one versioning scheme, AFTER v1.0 is tagged and not
      before.** Verify: the scheme is stated in exactly one file, and no second
      file restates it.
- [ ] T2 | T2 -- **The census carries a version field written from T1's
      statement.** Verify: `census.py --json` emits it and its value comes from
      the single statement.
- [ ] T3 | T3 -- **The record file carries a version field written from T1's
      statement.** Verify: a written record holds it.
- [ ] T4 | T4 -- **Retire `RECORD_VERSION` as a constant of its own**
      (`record.py:639`). Verify: nothing in `record.py` carries a hand-moved
      version number.
- [ ] T5 | T5 -- **The run context carries a version field written from T1's
      statement.** Verify: `run_context.py --template` emits it and `--check`
      reads it.
- [ ] T6 | T6 -- **The plugin manifest's version is derived from T1's
      statement.** Verify: `plugin.json`'s version comes from the single
      statement.
- [ ] T7 | T7 -- **Keep the three declarations equal under the derived
      version.** Verify: `uv run pytest -q -k test_release` is green.
- [ ] T8 | T8 -- **Make a reader REFUSE an artifact whose keys sit in the same
      places but mean something else.** Verify: a test hands it one and it is
      refused.
- [ ] T9 | T9 -- **Prove T8's refusal can fail.** Verify: the test fails with
      the version field removed from the artifact.
- [x] T10 | FINISHED | unknown | T10 -- SUPERSEDED. Roy's 2026-08-21 ruling is
      stated in the Objective; a ruling already made carries no box and the
      record stays.
- [x] T11 | FINISHED | unknown | T11 -- SUPERSEDED. The `RECORD_VERSION`
      measurement is in the Objective with its file:line.
- [x] T12 | FINISHED | unknown | T12 -- SUPERSEDED. The reasoning that a loud
      parse refusal already catches a wrong shape is kept in the Objective.
