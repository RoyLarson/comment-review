# The stage list is a literal, so every topology is a source edit

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, designing P4 with Roy: *"the order of reviewers and
          revise has to be able to be flexible in the system, from all 4 at the same
          time to all 4 sequentially to fanning out block-context across many agents"*)
```

## Objective

The stage list is a literal, so every topology is a source edit.

## Tasks

- [ ] Define the topology file and its validator -- an ordered list of stages,
      each a list of DISPATCHES. Verify: the three topologies in the spec each
      parse, `paths` on a dispatch fans one role while leaving others whole, and a
      dispatch naming a role outside the closed set is refused.
- [ ] Refuse a forward reference and an unreachable read. Verify: `reads` naming a
      later stage is refused, `reads` naming an `enriching` stage is refused BY
      NAME rather than resolved to the previous editorial one, and `reads =
      "original"` always resolves.
- [ ] Split `STAGES`: the four roles stay in code as a closed `StrEnum`, the
      schedule moves to the file. Verify: `commands/mark.py`'s `--role` draws its
      `choices=` from the enum and not from a run's topology, and the file's
      `role` keys are validated against that enum.
- [ ] Fan a binder out by dispatch. Verify: every page reaches exactly one shard
      of each role, no page reaches two shards of one role, and a dispatch with no
      `paths` gets every page.
- [ ] Accept `carries` in the format and REFUSE a non-empty value. Verify:
      `carries = []` parses, a non-empty `carries` is refused with a reason naming
      it unbuilt, and the refusal is not a silent drop.
