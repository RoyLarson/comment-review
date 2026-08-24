# The corpora are nine Python projects, so every per-language rule is measured on Python and C alone

```
Status:   in-progress
Progress: 3 of 6 tasks done
Owner:    testing
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, on the boundary table: 'Was this language
          agnostic? Do we have enough good Rust libraries in our corpora? What about the
          other languages?')
Updated:  2026-08-21 — Roy, 2026-08-21: 'this can land in another branch later. Probably
          even in a 0.2.5 version release' -- not the cue-placement branch, which
          needs no corpus for the ordering fix
Advanced: 2026-08-22 — Ten corpora added to the manifest 2026-08-22 -- rust, go,
          typescript, elasticsearch (javadoc), dotnet-runtime (xmldoc), llvm (doxygen),
          rails (rdoc), neovim (lua), kotlin, swift -- every tag resolved against the
          remote rather than guessed. ! Only neovim is FETCHED; the rest are rows, so
          the remaining tasks are about measurement and not about the manifest. The one
          fetch immediately found that 2,505 of 2,741 Lua declarations (91%) censused as
          undocumented, which is the whole argument for this TODO.
TRIAGED:  2026-08-23 — 2026-08-23. T1 is a MEASUREMENT and nobody ticks one; ticked as a
          RECORD and left in place. T2 and T6 were measurements with real work inside
          them and are rewritten as the work, keeping the numbers as their evidence.
          T3 and T4 stay ticked.
RE-VERIFIED: 2026-08-23 — 2026-08-23. `ls corpora/` returns corpora.toml, cpython,
             django, fastapi, flask, meta-package-manager, neovim, numpy,
             photo_organizer, pymc, sentry. So of the ten rows added 2026-08-22 ONLY
             neovim is on disk -- rust, go, typescript, elasticsearch, dotnet-runtime,
             llvm, rails, kotlin and swift are manifest rows and nothing else. The rows
             for kotlin (corpora.toml:336) and swift (:353) do exist, so the old wording
             *"no corpus file at all"* is now half wrong and T2 says which half.
```

## Objective

The corpora are nine Python projects, so every per-language rule is measured on Python and C alone.

!! **THE MANIFEST IS NO LONGER THE GAP; THE DISK IS.** Ten rows landed 2026-08-22 and one of
them has been fetched. A row pins a ref and proves nothing about a language -- the boundary
table, the leading-edge count and the `a`-series claims are all measured from FILES, and for
nine of the ten there are none.

## Tasks

- [x] T1 -- RECORD, not a task. MEASURED 2026-08-21: python 700 files / 43,478
      boundaries, c 494 / 244,778, yaml 104, toml-ini 46, javascript 12, typescript
      5, shell 5, sql 2 -- and lua, cpp, go, ruby, RUST one file each.
- [ ] T2 -- FETCH THE LANGUAGES THAT SHIP WITH A KEYWORD LIST AND NO FILES.
      csharp, java, kotlin and swift each carry a keyword list giving them an `a`
      series, and each is measured against nothing. ! The 2026-08-22 rows changed
      what is wrong here: elasticsearch (java), dotnet-runtime (csharp), kotlin and
      swift are now IN `corpora.toml` -- kotlin at :336, swift at :353 -- and none
      is on disk. MEASURED 2026-08-23 with `ls corpora/`: of the ten rows added,
      only neovim is fetched. Verify: `uv run python scripts/fetch_corpora.py
      --only elasticsearch dotnet-runtime kotlin swift` completes and each
      `corpora/<name>/` holds files, or the manifest records why the language ships
      unmeasured.
- [x] T3 -- FINISHED. Add a Rust corpus to corpora.toml -- the keyword-list work
      gave Rust an `a` series and one file cannot check it. The row is at
      corpora.toml:204-208. ! The TREE is not fetched; that is T2 and T4 territory.
- [x] T4 -- FINISHED. Add corpora for go, ruby, java, csharp, kotlin, swift -- or
      record in the manifest that these languages ship unmeasured. All six rows are
      in `corpora.toml`.
- [ ] T5 -- Re-take the boundary distribution per language once the corpus covers
      them; the c->a row INVERTS between python (0 blanks 100%) and javascript
      (1 blank 100%). Verify: a per-language table in this file taken from fetched
      trees, naming the file count behind each row.
- [ ] T6 -- RE-TAKE THE LEADING EDGE OVER THE LANGUAGES IT HAS NEVER SEEN. It was
      measured 2026-08-22 in ten languages only -- c 48,966 edges, python 41,356,
      yaml 4,174, toml-ini 672, cpp 557, javascript 161, typescript 147, shell 7,
      sql 4, lua 3. ! rust, go and ruby were checked with HAND FIXTURES when the
      pair key was cut, and java, csharp, swift and kotlin have neither corpus nor
      fixture -- so the claim that `before` alone is unique rests on 10 of 17
      languages, three of them on single-digit evidence. Verify: an edge count per
      language from fetched trees for all 17, or a named list of the languages the
      claim does not cover.
