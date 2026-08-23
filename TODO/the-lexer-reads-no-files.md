# The lexer reads no files, nine other places do, and the identity passes on translated text

```
Status:   open
Progress: 0 of 8 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21: 'The lexer reads zero files - this is also a
          warning - how did the text get there when I stated that it was the lexers job
          to read the files and the compositors job to write the files')
```

## Objective

The lexer reads no files, nine other places do, and the identity passes on translated text.

## Tasks

- [ ] !! THE LEXER TAKES `text` AND READS NOTHING, so the reading it was given as
      its job happens somewhere else -- nine times. MEASURED 2026-08-21: `census`
      (2), `compositor` (2), `desk`, `prove_unchanged`, `referrers`,
      `run_context`, `verdicts`. Roy drew the line at *"lexer and compositor are
      the things that are reading files"*; seven of the nine sites are in neither.
- [ ] !! ALL NINE USE `Path.read_text`, WHICH TRANSLATES LINE ENDINGS.
      `repo.read_raw` exists for exactly this and says so -- *"`Path.read_text`
      ... applies universal-newline translation, collapsing every `\r\n` to `\n`
      before the caller ever sees it"* -- and its own docstring records TWO
      callers. Seven others read the translating way.
- [ ] !! SO `compositor.identity` GIVES A FALSE PASS ON EVERY CRLF FILE. It
      compares its own translated read against its own translated output, so both
      sides lose `\r\n` identically and the check passes. MEASURED: a file written
      as `b'# a note\r\nx = 1\r\n'` reads as `'# a note\nx = 1\n'`, `identity`
      answers None, and the same page read with `repo.read_raw` sets back byte-
      exact. ! The instrument reports agreement it did not test.
- [ ] !! AND IT IS THE NORMAL CASE, NOT AN EDGE. MEASURED over 3,080 source files:
      2,957 hold CRLF, 123 are LF only. Roy works on Windows and CLAUDE.md says to
      assume CRLF unless a repo says otherwise.
- [ ] ! EVERY MEASUREMENT TAKEN 2026-08-21 IS THEREFORE NARROWER THAN IT WAS
      STATED -- *3,049 of 3,082 byte-identical* is really *identical after newline
      translation*, for 2,957 of those files. The model IS lossless over the
      translated text, which is where every paragraph rule lives, so the findings
      hold; the WORD `byte-identical` does not. Re-take the number through
      `repo.read_raw` before quoting it again.
- [ ] ! `draft()` WRITES WITH `newline=""`, so it emits exactly what `set_page`
      produced -- and `set_page` takes its ending from `page.text`, which arrived
      translated. A run over a CRLF checkout would write LF. ! Invisible in THIS
      repo, where git's `autocrlf` normalises on the way in, and a real change
      anywhere it does not.
- [ ] ! IT IS THE SAME CAUSE AS `bom-is-read-as-source`, already filed: all nine
      sites read `encoding="utf-8"` where a BOM needs `utf-8-sig`. One decision --
      how to turn bytes into text -- made in nine places, and made the same wrong
      way in all of them. **THAT IS THE ARGUMENT FOR THE LEXER OWNING IT**, rather
      than tidiness.
- [ ] * THE SHAPE OF THE FIX follows Roy's own division: the LEXER reads, the
      COMPOSITOR writes and verifies. `page_for` would take a PATH and the lexer
      would open it -- with `repo.read_raw` and `utf-8-sig` -- so encoding, BOM
      and newline are settled once. Everything between carries text it was handed.
