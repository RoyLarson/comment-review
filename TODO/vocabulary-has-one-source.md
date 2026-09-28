# Vocabulary has one source

```
Status:   open
Progress: 1 of 2 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-09-27 (P5 self-run, Roy 2026-09-27)
```

## Objective

Vocabulary has one source.

Three places hold vocabulary today: `docs/vocabulary.md` (the record a person reads),
`src/comment_review/references/vocabulary.toml` (the definitions handed to agents), and the
retired-word tables hard-coded in `scripts/check_vocabulary.py`. Roy, 2026-09-27, on moving
those tables into their own toml: *"scripts/retired_words.toml for now but it should actually
be part of docs/vocabulary.md somehow because now we hae three places that talk vocabularly and
it would be better to have one place and build out the programs context from that during
release which is something we can do now that we have a release program"*.

T1 is the step for now; T2 is the destination.

## Tasks

- [x] T1 | Tables in scripts/retired_words.toml, each entry with a why; gate 16 words, 0 uses; suite green | d336d460133770c007444b2616dfc3f89d788a95 | Move
      RETIRED, MENTION, NOT_THE_TERM and NOQA into scripts/retired_words.toml;
      verify check_vocabulary reads it and its gate tests pass
- [ ] T2 | Make docs/vocabulary.md the one vocabulary source and have release.py
      build vocabulary.toml and the retired words from it
