# A machine context raises the queries a script can see, and certifies the rest clean

```
Status:   closed
Progress: 8 of 8 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-07 (Roy 2026-09-07: a machine-context automatically raises query or
          clean marks which then pass to the other agent contexts)
```

## Objective

A machine context raises the queries a script can see, and certifies the rest
clean.

## Tasks

- [-] T1 | The annotations it would raise are removed; Process #320, #338 and #345 | 8bf4eb6a7c637eba124bdd246f910b0ebdbd031b | Implement
      the machine context as a role with its own seeded edit copy, filled
      through mark. Verify: its marks name it as the role
- [-] T2 | The annotations it would raise are removed; Process #320, #338 and #345 | 8bf4eb6a7c637eba124bdd246f910b0ebdbd031b | Update
      annotate so the concordance keeps only names-a-symbol and cites-a-path.
      Verify: it emits no counted or coverage-claim note
- [-] T3 | The annotations it would raise are removed; Process #320, #338 and #345 | 8bf4eb6a7c637eba124bdd246f910b0ebdbd031b | Implement
      the four raising kinds as query marks the machine context places. Verify:
      a count claim returns a query naming the population
        > 2026-09-07 SKILL.md:64 -- a query is unsettled, resolve or escalate
- [-] T4 | The annotations it would raise are removed; Process #320, #338 and #345 | 8bf4eb6a7c637eba124bdd246f910b0ebdbd031b | Implement
      the machine context's clean so it certifies a read. Verify: a paragraph
      holding no checkable assertion carries a reasoned clean
- [-] T5 | The annotations it would raise are removed; Process #320, #338 and #345 | 8bf4eb6a7c637eba124bdd246f910b0ebdbd031b | Update
      the topology so the machine context runs ahead of the agent contexts.
      Verify: topology verify passes over it and the four roles
- [-] T6 | The annotations it would raise are removed; Process #320, #338 and #345 | 8bf4eb6a7c637eba124bdd246f910b0ebdbd031b | Update
      reviewer-brief.md so an agent context is told it may resolve a
      machine-raised query. Verify: the brief names the raiser
- [-] T7 | Superseded until a machine role exists; Process #338 | 5814f78efbf136da31ec84a22680a6e2be87d1c1 | Decide
      whether a machine-raised query gates its paragraph, as a role's query does
        > 2026-09-07 Every other instruction on that sentence waits on a query
        > 2026-11-22 Outcome: superseded until the role exists (Process #338)
- [-] T8 | The annotations it would raise are removed; Process #320, #338 and #345 | 8bf4eb6a7c637eba124bdd246f910b0ebdbd031b | Decide
      the name for this context, inside the-roles-are-named-for-what-they-read
        > 2026-09-07 The other four are named for the scope read, not the reader
