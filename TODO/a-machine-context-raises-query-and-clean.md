# A machine context raises the queries a script can see, and certifies the rest clean

```
Status:   open
Progress: 0 of 8 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-09-07 (Roy 2026-09-07: a machine-context automatically raises query or
          clean marks which then pass to the other agent contexts)
```

## Objective

A machine context raises the queries a script can see, and certifies the rest clean.

## Tasks

- [ ] T1 | Implement the machine context as a role with its own seeded edit
      copy, filled through mark. Verify: its marks name it as the role
- [ ] T2 | Update annotate so the concordance keeps only names-a-symbol and
      cites-a-path. Verify: it emits no counted or coverage-claim note
- [ ] T3 | Implement the four raising kinds as query marks the machine context
      places. Verify: a count claim returns a query naming the population
        > 2026-09-07 SKILL.md:64 -- a query is unsettled, resolve or escalate
- [ ] T4 | Implement the machine context's clean so it certifies a read. Verify:
      a paragraph holding no checkable assertion carries a reasoned clean
- [ ] T5 | Update the topology so the machine context runs ahead of the agent
      contexts. Verify: topology verify passes over it and the four roles
- [ ] T6 | Update reviewer-brief.md so an agent context is told it may resolve a
      machine-raised query. Verify: the brief names the raiser
- [?] T7 | Decide whether a machine-raised query gates its paragraph, as a
      role's query does
        > 2026-09-07 Every other instruction on that sentence waits on a query
- [?] T8 | Decide the name for this context, inside
      the-roles-are-named-for-what-they-read
        > 2026-09-07 The other four are named for the scope read, not the reader
