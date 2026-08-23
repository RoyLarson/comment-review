# A directory marketplace resolves the plugin LIVE, so a version-pinned measurement was never pinned

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22: the installed plugin traced itself back up to the
          commit just finished, when he expected v0.2.3 -- the d records gave it away
          because no foliation had a d before this branch)
```

## Objective

A directory marketplace resolves the plugin LIVE, so a version-pinned measurement was never pinned.

## Tasks

- [ ] MEASURED 2026-08-22: known_marketplaces.json has roy-local as
      source=directory with installLocation = C:\Users\Roy\projects\comment-review
      -- the WORKING TREE. A directory marketplace points; it does not copy
- [ ] MEASURED: the cached 0.2.3 holds annotate/census/galley/prove_unchanged/reco
      rd/referrers/repo/run_context/verdicts/vocabulary and NO foliator.py,
      addresser.py, page.py, lexer.py or compositor.py -- those did not exist at
      that tag. So the d series is UNREACHABLE from that cache: no module in it
      can emit one. The run that produced d records was reading the live tree
- [ ] !! IT CONTRADICTS WHAT CLAUDE.md TELLS US ABOUT RELEASES: *the plugin cache
      keys its directory on that version field, so a second different tree
      installed under the same number overwrites the first*. That describes the
      cache half only. It does not say that a directory-source marketplace
      resolves live, which means ANY measurement believed to be pinned to a tag
      was against whatever the tree held at run time
- [ ] * RULING: is the fix to the INSTALL (a marketplace that copies, or
      installing from a tag rather than a path), to the DOCS (say plainly that
      roy-local is live and no local measurement is pinned), or to both? A pin
      that pins nothing and reports as a pin is findings.md section 33
- [ ] Re-check every measurement in docs/ and evidence/ that names a version
      rather than a commit -- each one needs to say which TREE it ran against,
      because the tag did not fix that
