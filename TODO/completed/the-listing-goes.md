# The listing goes: gather writes the binder only, and a reviewer is handed the binder and its seeded edit copy

```
Status:   open
Progress: 7 of 7 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-06 (Roy, 2026-09-06, decision-log.md Process: #99: the gather text
          report is not necessary and should go)
```

## Objective

The listing goes: gather writes the binder only, and a reviewer is handed the binder and its seeded edit copy.

## Tasks

- [x] T1 | FINISHED; gather writes the binder only | 36f1e404 | Delete _listing
      and --filtered from commands/gather.py, so gather writes the binder and
      nothing else.
        > 2026-09-06 backend
- [x] T2 | FINISHED; the suite pins the one output path | 36f1e404 | Update the
      five tests that name the listing or --filtered so they pin the binder
      output.
        > 2026-09-06 backend
- [x] T3 | FINISHED; one commit with the rest, gate exits 0 | 5217b3fd | Retire
      listing in vocabulary.toml: delete its definition and its entry in the
      four role lists.
        > 2026-09-06 shared vocabulary; lands with T1
- [x] T4 | FINISHED; one commit with the rest, gate exits 0 | 5217b3fd | Add
      listing to RETIRED in scripts/check_vocabulary.py, replacement binder.
        > 2026-09-06 systems; lands with T3 or the gate reddens
- [x] T5 | FINISHED; one commit with the rest, gate exits 0 | 5217b3fd | Update
      SKILL.md so stage 2 writes only binder.json and the stage-4 packet carries
      BINDER and EDIT COPY.
        > 2026-09-06 agents: 17 sites
- [x] T6 | FINISHED; one commit with the rest, gate exits 0 | 5217b3fd | Update
      reviewer-brief.md so a role reads the binder, and the four agent
      descriptions stop naming a listing.
        > 2026-09-06 agents: 6 sites in the brief, 4 descriptions, 2 in module-context
- [x] T7 | FINISHED; runs over a real file both ways | cedd8bbb | Update
      scripts/measure_binder.py so it measures the binder and not a listing.
        > 2026-09-06 systems
