# Reading settings have no setting

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-04 (Process #280, 2026-11-04: both language definitions have empty
          defaults and choices)
```

## Objective

Reading settings have no setting.

## Tasks

- [ ] T1 | Remove --reading-settings from gather, compositor and
      prove_unchanged, per #280
- [ ] T2 | Remove flows/reading_context.load_settings, per #280
- [ ] T3 | Remove defaults and choices from the language definitions, per #280
- [ ] T4 | Remove the settings a reading context carries, per #280
- [ ] T5 | Determine whether to remove the reading field from every artifact
        > 2026-11-23 Kept for now by #400; revisit after T1-T4 land
