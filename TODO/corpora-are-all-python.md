# The corpora are nine Python projects, so every per-language rule is measured on Python and C alone

```
Status:   in-progress
Progress: 2 of 6 tasks done
Owner:    comment-review
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, on the boundary table: 'Was this language
          agnostic? Do we have enough good Rust libraries in our corpora? What about the
          other languages?')
Updated:  2026-08-21 — Roy, 2026-08-21: 'this can land in another branch later. Probably
          even in a 0.2.5 version release' -- not the folio-placement branch, which
          needs no corpus for the ordering fix
Advanced: 2026-08-22 — Ten corpora added to the manifest 2026-08-22 -- rust, go,
          typescript, elasticsearch (javadoc), dotnet-runtime (xmldoc), llvm (doxygen),
          rails (rdoc), neovim (lua), kotlin, swift -- every tag resolved against the
          remote rather than guessed. ! Only neovim is FETCHED; the rest are rows, so
          the remaining tasks are about measurement and not about the manifest. The one
          fetch immediately found that 2,505 of 2,741 Lua declarations (91%) censused as
          undocumented, which is the whole argument for this TODO.
```

## Objective

The corpora are nine Python projects, so every per-language rule is measured on Python and C alone.

## Tasks

- [ ] MEASURED 2026-08-21: python 700 files / 43,478 boundaries, c 494 / 244,778,
      yaml 104, toml-ini 46, javascript 12, typescript 5, shell 5, sql 2 -- and
      lua, cpp, go, ruby, RUST one file each
- [ ] csharp, java, kotlin and swift have NO corpus file at all, yet each carries
      a keyword list giving it an a series
- [x] Add a Rust corpus to corpora.toml -- the keyword-list work gave Rust an a
      series and one file cannot check it
- [x] Add corpora for go, ruby, java, csharp, kotlin, swift -- or record in the
      manifest that these languages ship unmeasured
- [ ] Re-take the boundary distribution per language once the corpus covers them;
      the c->a row INVERTS between python (0 blanks 100%) and javascript (1 blank
      100%)
- [ ] The LEADING edge was measured 2026-08-22 in ten languages only -- c 48,966
      edges, python 41,356, yaml 4,174, toml-ini 672, cpp 557, javascript 161,
      typescript 147, shell 7, sql 4, lua 3. ! rust, go and ruby were checked with
      HAND FIXTURES when the pair key was cut, and java, csharp, swift and kotlin
      have neither corpus nor fixture -- so the claim that before alone is unique
      rests on 10 of 17 languages, three of them on single-digit evidence
