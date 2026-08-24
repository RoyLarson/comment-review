# A directory marketplace resolves the plugin LIVE, so a version-pinned measurement was never pinned

```
Status:   decision-needed
Progress: 3 of 5 tasks done
Owner:    systems
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22: the installed plugin traced itself back up to the
          commit just finished, when he expected v0.2.3 -- the d records gave it away
          because no cues had a d before this branch)
RE-MEASURED: 2026-08-23 — both measurements still hold, re-read today.
             `~/.claude/plugins/known_marketplaces.json` still has `roy-local` with
             `"source": "directory"` and `installLocation`
             `C:\Users\Roy\projects\comment-review`, last updated 2026-08-18. And
             `~/.claude/plugins/cache/roy-local/comment-review/0.2.3/` still holds ten
             modules against nineteen in the live tree.
TRIAGED:  2026-08-23 — the first three boxes are MEASUREMENTS and a reading of CLAUDE.md;
          none can be ticked by doing anything, so they are ticked as recorded and their
          content is in the Objective. TWO REAL TASKS remain: the ruling, and the
          re-check of every version-named measurement.
```

## Objective

**A directory marketplace resolves the plugin LIVE, so a version-pinned measurement was never
pinned.** Roy caught it 2026-08-22 when an installed plugin traced itself to the commit just
finished rather than to v0.2.3.

MEASURED 2026-08-22, re-measured 2026-08-23:

| what | what it says |
| --- | --- |
| `~/.claude/plugins/known_marketplaces.json` | `roy-local` is `"source": "directory"`, `installLocation` = `C:\Users\Roy\projects\comment-review` -- **the working tree.** A directory marketplace points; it does not copy |
| `~/.claude/plugins/cache/roy-local/comment-review/0.2.3/` | ten modules -- `annotate`, `census`, `galley`, `prove_unchanged`, `record`, `referrers`, `repo`, `run_context`, `verdicts`, `vocabulary`. **No `addresser.py`, `page.py`, `lexer.py`, `language.py`, `desk.py`, `held.py`, `compositor.py`, `constants.py` or `exceptions.py`** -- nineteen live today, and those nine did not exist at that tag |

!! **SO THE `d` SERIES IS UNREACHABLE FROM THAT CACHE: no module in it can emit one.** The run
that produced `d` records was reading the live tree.

!! **IT CONTRADICTS WHAT CLAUDE.md TELLS US ABOUT RELEASES.** CLAUDE.md says *the plugin cache
keys its directory on that version field, so a second different tree installed under the same
number overwrites the first*. That describes the cache half only. It does not say that a
directory-source marketplace resolves LIVE -- which means **any measurement believed to be
pinned to a tag was against whatever the tree held at run time.**

## Tasks

- [x] T1 -- MEASURED 2026-08-22, re-measured 2026-08-23. Recorded in the Objective:
      `known_marketplaces.json` has `roy-local` as `source=directory` with
      `installLocation = C:\Users\Roy\projects\comment-review`, the working tree.
- [x] T2 -- MEASURED 2026-08-22, re-measured 2026-08-23. Recorded in the Objective:
      the cached 0.2.3 holds ten modules and none of the nine the address system is
      built from, so the `d` series is unreachable from that cache.
- [x] T3 -- READ 2026-08-22. Recorded in the Objective: CLAUDE.md's release section
      describes the cache half only and never says a directory-source marketplace
      resolves live.
- [ ] T4 -- * RULING: is the fix to the INSTALL (a marketplace that copies, or
      installing from a tag rather than a path), to the DOCS (say plainly that
      `roy-local` is live and no local measurement is pinned), or to both? ! The
      original box cited *"findings.md section 33"*; MEASURED 2026-08-23, `find . -name
      findings.md` outside `corpora/` returns nothing, so that citation resolves
      nowhere and is not repeated as a pointer. Verify: the ruling is recorded in
      `docs/decision-log.md`.
- [ ] T5 -- Re-check every measurement in `docs/` and `evidence/` that names a
      VERSION rather than a commit -- each one needs to say which TREE it ran
      against, because the tag did not fix that. Verify: no measurement in `docs/`
      or `evidence/` cites a `vX.Y.Z` without also citing a commit SHA.
