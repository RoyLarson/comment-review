# The deprecated reader cannot replay a held run, which is the only reason it exists

```
Status:   open
Progress: 3 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
Corrected: 2026-08-19 — The diagnosis was wrong: `parse_report` leaves `address` empty,
           so the join's guard fires correctly and there is no line-address tail to
           ignore. `record.convert` had no index translation at all. And against a
           genuine 0.2.x census -- which carries no addresses -- it fanned out instead
           of dropping: 3,333 blocks and 173 findings gave 29,583 records with no error.
           Both fixed 2026-08-19; `convert` refuses an addressless census.
```

## Objective

!! **`--convert` DROPS 100% OF A HELD 0.2.x REPORT AND EXITS 0.** Measured 2026-08-19: 2 findings
in, 0 filled records out, return code 0.

**Replaying held reports is the only reason the deprecated parser was kept**, and it is how 0.2.1
and 0.2.2 were validated cheaply -- five joins over one set of reports, ~1.6M tokens of review
reused. `record.py` says so at the reader: it exists to parse runs already recorded so
`evidence/` can be compared against the format that replaced it.

**The cause is a guard that never fires.** The 0.2.x `BLOCK` form is
`<index> | <path>:<start>-<end>`, so `parse_report` puts that LINE address into `Finding.address`.
`verdicts.py`'s index translation is written `if not f.address` -- and the field is already full,
of the retired form. So the address reaches `entry_for`, resolves to nothing, and every record
joins as *"names no block"*.

! **`record.convert` keys entirely on `f.address` and never reads `f.block`**, so the bridge
carries nothing across, in silence. ! A held report is a REGRESSION TEST; nothing in the suite
would notice this happening again.

## Tasks

- [x] T1 | FINISHED | unknown | !! **SUPERSEDED 2026-08-19 -- THE OBSERVATION
      WAS WRONG.** Measured on a real held report: `parse_report` leaves
      `address` EMPTY on every 0.2.x record, so there is no line tail to ignore
      and `verdicts.py`'s `if not f.address` guard fires exactly as intended --
      173 of 173 findings translated. The proposed fix would have changed
      nothing. Kept so the error stays legible; the defect is the task below.
      **The original text:** *"A LINE address lands in `Finding.address` and can
      never join. The 0.2.x `BLOCK` form is `<index> \| <path>:<start>-<end>`
      and `parse_report` puts that tail into `address`."*
- [x] T2 | FINISHED | unknown | !! **SUPERSEDED 2026-08-19 -- THE CONVERSION IS
      NOT POSSIBLE, AND `convert` REFUSES.** Roy: *"is it possible to convert
      the old form to the new form at all without the code there next to it? I
      don't think it is. There is not enough definition in the old form to make
      the address."* Both routes are closed. **`BLOCK <index>`** is a position
      in ONE census: that census carries no addresses (0 of 3,333 on a real held
      run -- the field postdates it) and today's census of the same source is a
      different LIST, because the held one has no `margin` and no `undocumented`
      and today's emits one of each per code line and per undocumented
      declaration. Every index shifts. **`LOCATION path:start-end`** is line
      numbers, which need the SOURCE to become an ordinal, and `Finding` does
      not retain the field. ! **The failure it replaces was silent in BOTH
      directions**: against a fresh census every held finding grouped under `""`
      and matched nothing (3 of 3 dropped, rc=0); against the genuine held
      census every block keyed on `""` too, so every record matched every
      finding -- 3,333 blocks and 173 findings produced **29,583 records**, each
      with a verdict, no error. ! An INDEX-to-address translation was written
      and then withdrawn as unsafe: it silently maps a held index onto whatever
      sits at that position in whatever census is passed. `record.address_of`
      keeps the rule for the JOIN alone, where the census IS the one the record
      was written against.
- [x] T3 | FINISHED | unknown | **DONE 2026-08-19 --
      `TestA02xReportCANNOTBeConverted`, six cases.** A held report refused with
      the reason named, the `LOCATION` line shown to be absent from `Finding`,
      the real held run in `evidence/` refused against its own census, and an
      ADDRESSED report still converting -- the bridge carries a run held from
      0.2.4 on. ! **The class that existed was named for this property and never
      called `convert`.** Every case in `TestConvertKeepsAHeldRunReplayable`
      tests `claim_object`, one field at a time -- which is how a bridge that
      carried nothing passed a green suite.
