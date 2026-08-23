# v1.x wants a concrete versioning system on everything that ships

```
Status:   deferred
Progress: 0 of 4 tasks done
Owner:    systems · Roy
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, ruling out any versioning investment before v1)
```

## Objective

v1.x wants a concrete versioning system on everything that ships.

## Tasks

- [ ] * RULED 2026-08-21, DEFERRED TO v1.x. Roy: 'when we get to a v1.X we will
      want a concrete versioning system on everything that ships with v1.X and
      future ... until then nah.' A 0.x states that ALL things are subject to
      shifting -- zero-vers are specifically for that, with no guarantee of any
      stability -- so nothing before v1 owes a compatibility story.
- [ ] ! WHAT EXISTS TODAY IS NOT THAT SYSTEM. `RECORD_VERSION` is one constant on
      one artifact, moved by hand, and 2026-08-21 measured that it does not get
      moved: it stayed put across an incompatible shape change while the comment
      above it described exactly that failure. ! It is kept because it costs a
      line, not because it works.
- [ ] ! AND THE PARSE REFUSAL IS WHAT ACTUALLY CATCHES A WRONG SHAPE. Roy: a loud
      'unable to parse -- unknown format' is enough, and it does not matter
      whether the file is an old version or a current one mangled. A version field
      only adds the case a parse cannot see -- keys in the same places meaning
      something else.
- [ ] ! WHEN IT IS BUILT, IT COVERS EVERYTHING THAT SHIPS, not just the record:
      the census, the record file, the run context, the plugin manifest. One
      scheme, stated once.
