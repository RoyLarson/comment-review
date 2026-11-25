# Topology defects

```
Status:   open
Progress: 4 of 10 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-04 (decision-log sweep, 2026-11-04: Process #50)
```

## Objective

Topology defects.

## Tasks

- [ ] T1 | Build a topology's carries, per Process #50
- [ ] T2 | Refuse an empty stage and a role named twice in `compose`
- [ ] T3 | Fix `_toml_string`, which escapes a character above the BMP as a
      surrogate pair TOML refuses
- [x] T4 | topology, gather and referrers write --out only on exit 0 | bf44bb44 | Write
      --out only after the run is decided in commands/topology.py:83, gather,
      referrers
        > 2026-11-22 Check (M35): a failed rebuild leaves the verified T.toml intact
- [ ] T5 | Refuse a reads value not of the form revise:<stage> at
      desk/topology.py:108
        > 2026-11-22 Check (M42): reads = 'Revise:4' is refused
- [ ] T6 | Refuse two [[stage]] tables with one name at desk/topology.py:188
        > 2026-11-22 Check (M43): two stages named '4' are refused
- [x] T7 | A non-string stage kind is refused | a0c1ce9e | Refuse a non-string
      stage kind at desk/topology.py:97 instead of raising TypeError
        > 2026-11-22 Check (M44): kind = ['editorial'] gives a named refusal
- [ ] T8 | Escape the stage name in reads = revise:<previous> at
      flows/topology.py:100
        > 2026-11-22 Check (M86): --stage 'a"b=ownership-context' builds valid TOML
- [x] T9 | An unreadable --verify file exits 2 with a message | 9ad77036 | Refuse
      an unreadable topology file with exit 2 in commands/topology.py --verify
        > 2026-11-23 Today: Path.read_text unguarded; exits 1 with a traceback
- [-] T10 | distribute has taken no --topology since da0196df; the jacket carries it | 5a6ed001 | Refuse
      an unreadable --topology file with exit 2 in commands/distribute.py
        > 2026-11-23 Today: Path.read_text unguarded; exits 1 with a traceback
