# v1.x wants a concrete versioning system on everything that ships

```
Status:   deferred
Progress: 3 of 4 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, ruling out any versioning investment before v1)
Triaged:  2026-08-23 -- three of the four boxes were the ruling itself and the reasoning
          kept with it. They are ticked and stated in the Objective; ONE task remains and
          it does not start before v1.x
```

## Objective

**v1.x wants a concrete versioning system on everything that ships. Nothing before v1 owes one.**

!! **RULED 2026-08-21, DEFERRED TO v1.x.** Roy: *"when we get to a v1.X we will want a concrete
versioning system on everything that ships with v1.X and future ... until then nah."* A 0.x
states that ALL things are subject to shifting -- zero-vers are specifically for that, with no
guarantee of any stability -- so nothing before v1 owes a compatibility story. **The event this
waits on is the v1.0 tag.**

! **WHAT EXISTS TODAY IS NOT THAT SYSTEM.** `RECORD_VERSION` is one constant on one artifact,
moved by hand -- verified 2026-08-23 at `record.py:639`, written into a record at `:873` and
compared on read at `:1020-1028`. 2026-08-21 measured that it does not get moved: it stayed put
across an incompatible shape change while the comment above it described exactly that failure.
! It is kept because it costs a line, not because it works.

! **AND THE PARSE REFUSAL IS WHAT ACTUALLY CATCHES A WRONG SHAPE.** Roy: a loud *"unable to parse
-- unknown format"* is enough, and it does not matter whether the file is an old version or a
current one mangled. A version field only adds the case a parse cannot see -- **keys in the same
places meaning something else.** ! That single case is the whole argument for building anything,
and it is why the answer is *later* rather than *never*.

! **WHEN IT IS BUILT, IT COVERS EVERYTHING THAT SHIPS**, not just the record: the census, the
record file, the run context, the plugin manifest. **One scheme, stated once.**

! **Deferred is not done.** Roy, 2026-08-18: *"Deferred is not done - just waiting so its status
is still correct."* The one box below stays unchecked because the work has not started, which is
what an unchecked box already says.

## Tasks

- [ ] T1 -- AFTER v1.0 IS TAGGED, and not before: one versioning scheme covering every shipped
      artifact -- the census, the record file, the run context, the plugin manifest. Verify: the
      scheme is stated in exactly one file; each of the four artifacts carries a version field
      written from that one statement; and a test asserts that a reader handed an artifact whose
      keys sit in the same places but mean something else REFUSES it -- the one case a parse
      cannot see, which is the whole reason to build this.

- [x] T2 -- SUPERSEDED. This box held Roy's 2026-08-21 ruling. A ruling already made carries no
      box; it is stated in the Objective and the record stays.

- [x] T3 -- SUPERSEDED. This box held the `RECORD_VERSION` measurement -- one hand-moved constant
      that stayed put across an incompatible shape change. A measurement is not a task; it is in
      the Objective with the file:line that re-derives it.

- [x] T4 -- SUPERSEDED. This box held the reasoning that a loud parse refusal already catches a
      wrong shape, so a version field buys only the same-keys-different-meaning case. Kept in the
      Objective, where it is the argument T1 has to satisfy.
