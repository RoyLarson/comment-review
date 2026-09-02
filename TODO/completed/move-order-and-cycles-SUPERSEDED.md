# Nothing orders the settled moves, and nothing refuses a cycle

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (measured 2026-08-30 while specifying SP-1's resolution step; Roy:
          the moves have to be resolved to some sorted order because a double move can
          cause problems, and we cannot allow circles so it has to resolve from a DAG)
```

## Objective

Nothing orders the settled moves, and nothing refuses a cycle.

## Tasks

- [ ] T1 | Implement the topological order over the resolved moves, where an
      edge B to A means B's origin is A's destination so B vacates the address
      before A fills it. Verify: two independent moves emit in an order that
      does not depend on which role's copy was read first, and a move whose
      origin another move fills is emitted first.
- [ ] T2 | Implement the cycle refusal. Verify: a set of moves forming a cycle
      is carried forward as a re-read naming the cycle, driven with a Reconciled
      built directly, since no cycle reaches the resolution step through
      reconcile today.
- [ ] T3 | Implement the test that a chained move does not settle FOR A STATED
      REASON. Verify: giving move a quotes_original key makes the chain settle
      under today's grouping, and the DAG rule refuses it anyway -- so the
      protection does not rest on _sentence_key returning id(mark).
