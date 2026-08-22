# The corpora are nine Python projects, so every per-language rule is measured on Python and C alone

```
Status:   blocked
Progress: 0 of 5 tasks done
Owner:    comment-review
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, on the boundary table: 'Was this language
          agnostic? Do we have enough good Rust libraries in our corpora? What about the
          other languages?')
Updated:  2026-08-21 — Roy, 2026-08-21: 'this can land in another branch later. Probably
          even in a 0.2.5 version release' -- not the folio-placement branch, which
          needs no corpus for the ordering fix
```

## Objective

The corpora are nine Python projects, so every per-language rule is measured on Python and C alone.

## Tasks

- [ ] MEASURED 2026-08-21: python 700 files / 43,478 boundaries, c 494 / 244,778,
      yaml 104, toml-ini 46, javascript 12, typescript 5, shell 5, sql 2 -- and
      lua, cpp, go, ruby, RUST one file each
- [ ] csharp, java, kotlin and swift have NO corpus file at all, yet each carries
      a keyword list giving it an a series
- [ ] Add a Rust corpus to corpora.toml -- the keyword-list work gave Rust an a
      series and one file cannot check it
- [ ] Add corpora for go, ruby, java, csharp, kotlin, swift -- or record in the
      manifest that these languages ship unmeasured
- [ ] Re-take the boundary distribution per language once the corpus covers them;
      the c->a row INVERTS between python (0 blanks 100%) and javascript (1 blank
      100%)
