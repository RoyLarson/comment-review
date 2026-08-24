# The corpora are nine Python projects, so every per-language rule is measured on Python and C alone

```
Status:   in-progress
Progress: 3 of 10 tasks done
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
Split:    2026-08-23 -- the one FETCH box named four languages and is now four boxes,
          because a language row takes its definition from its own grammar and never
          from a neighbour's. A second pass found a FETCH task nobody had written: the
          rust row landed and nothing fetches the tree, so rust gained its own box
```

## Objective

The corpora are nine Python projects, so every per-language rule is measured on Python and C alone.

!! **THE MANIFEST IS NO LONGER THE GAP; THE DISK IS.** Ten rows landed 2026-08-22 and one of
them has been fetched. A row pins a ref and proves nothing about a language -- the boundary
table, the leading-edge count and the `a`-series claims are all measured from FILES, and for
nine of the ten there are none.

!! **FOUR LANGUAGES SHIP WITH A KEYWORD LIST AND NO FILES.** csharp, java, kotlin and swift each
carry a keyword list giving them an `a` series, and each is measured against nothing. The
2026-08-22 rows changed WHICH half is wrong: elasticsearch (java), dotnet-runtime (csharp),
kotlin (`corpora.toml:336`) and swift (`:353`) are now IN the manifest, and none is on disk.

! **EACH FETCH BOX HAS THE SAME STANDING ALTERNATIVE**: files on disk, OR the manifest recording
why that language ships unmeasured. Either satisfies the box; nothing else does.

! **THE BOUNDARY DISTRIBUTION INVERTS ACROSS LANGUAGES ALREADY.** The `c`->`a` row goes from
python (0 blanks, 100%) to javascript (1 blank, 100%), which is why the table has to be re-taken
from fetched trees rather than extrapolated.

!! **THE LEADING-EDGE CLAIM RESTS ON 10 OF 17 LANGUAGES.** Measured 2026-08-22: c 48,966 edges,
python 41,356, yaml 4,174, toml-ini 672, cpp 557, javascript 161, typescript 147, shell 7, sql 4,
lua 3. ! rust, go and ruby were checked with HAND FIXTURES when the pair key was cut, and java,
csharp, swift and kotlin have neither corpus nor fixture -- so the claim that `before` alone is
unique rests on ten languages, three of them on single-digit evidence. The re-take is per
language, from FETCHED TREES.

! **THE 2026-08-21 DISTRIBUTION, kept as the record it is**: python 700 files / 43,478
boundaries, c 494 / 244,778, yaml 104, toml-ini 46, javascript 12, typescript 5, shell 5, sql 2
-- and lua, cpp, go, ruby and RUST one file each.

## Tasks

- [x] T1 -- RECORD, not a task. The 2026-08-21 per-language file and boundary counts are
      restated in the Objective.
- [ ] T2 -- Fetch the java corpus. Verify: `fetch_corpora.py --only elasticsearch`
      completes and `corpora/elasticsearch/` holds `.java` files.
- [ ] T3 -- Fetch the csharp corpus. Verify: `fetch_corpora.py --only dotnet-runtime`
      completes and `corpora/dotnet-runtime/` holds `.cs` files.
- [ ] T4 -- Fetch the kotlin corpus (`corpora.toml:336`). Verify: `fetch_corpora.py --only
      kotlin` completes and `corpora/kotlin/` holds `.kt` files.
- [ ] T5 -- Fetch the swift corpus (`corpora.toml:353`). Verify: `fetch_corpora.py --only
      swift` completes and `corpora/swift/` holds `.swift` files.
- [ ] T6 -- Fetch the rust corpus (`corpora.toml:204-208`). Verify: `fetch_corpora.py
      --only rust` completes and `corpora/rust/` holds `.rs` files.
- [x] T7 -- FINISHED. The Rust row is in the manifest at `corpora.toml:204-208`.
- [x] T8 -- FINISHED. Rows for go, ruby, java, csharp, kotlin and swift are all in
      `corpora.toml`.
- [ ] T9 -- Re-take the boundary distribution per language once the corpora are on disk.
      Verify: a per-language table in this file, each row naming its file count.
- [ ] T10 -- Re-take the leading-edge count over the languages it has never seen. Verify:
      an edge count per language for all 17, or a named list of languages it cannot cover.
