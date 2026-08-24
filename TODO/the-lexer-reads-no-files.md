# The lexer reads no files, nine other places do, and the identity passes on translated text

```
Status:   in-progress
Progress: 8 of 15 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21: 'The lexer reads zero files - this is also a
          warning - how did the text get there when I stated that it was the lexers job
          to read the files and the compositors job to write the files')
Triaged:  2026-08-23 -- a DESIGN now answers this file. The eight original boxes were
          measurements and arguments; they are ticked and kept verbatim below, and the
          seven tasks after them are what implementing the design requires
```

## Objective

**The lexer reads no files, nine other places do, and the round-trip identity passes on text it
translated on the way in.**

!! **A DESIGN ANSWERS THIS FILE.** `docs/superpowers/specs/2026-08-23-io-and-the-chain-design.md`,
ruled with Roy in session 2026-08-23, names it as *"the file it answers"*. It proposes one door
(`io.py`) owning the whole byte<->text boundary, and two chains of `Doc -> Doc` steps --
`READ [language, read_text, lexer, addresser, page]` and `WRITE [edit, set, draft, lossless,
identity, prove_unchanged, approve]` -- so the ORDER is a list rather than a convention.
! The spec is not scheduled; whether it joins the 0.2.4 plan is a separate decision, and no task
below waits on that decision.

**What the design gets right about the cause.** `page_for(path, text, lang, rel)` takes TEXT
(`page.py:674`), so by the time anyone reaches the reading code somebody else has already read
the file. The rule -- only the lexer and the compositor touch source -- has no seam that enforces
it, so following it means every author remembering it. Roy, 2026-08-23: *"The fact that claude
stated it made something happen and then didn't tells me there is a design problem because it is
hard to do in the current system."*

!! **ONE CORRECTION TO THE SPEC, AND IT DOES NOT WEAKEN IT.** The spec's evidence table says *"the
newline-safe reader has ZERO callers"*. Measured 2026-08-23, `repo.read_raw` has FOUR call sites
in two modules -- `galley.py:430`, `prove_unchanged.py:254`, `:324` and `:325` -- exactly the two
callers its own docstring names, both *"about comparing a file to itself"*. What is true, and is
what the seam is for, is that **nine reads of SOURCE bypass it**. See T15.

## Tasks

### The measurements this file was filed on -- not tasks, and re-taken 2026-08-23

- [x] T1 -- !! THE LEXER TAKES `text` AND READS NOTHING, so the reading it was given as its job
      happens somewhere else -- nine times. `grep -c "read_text\|open(\|read_raw" lexer.py` returns
      0. The nine, re-verified 2026-08-23: `census.py:177`, `census.py:336`, `compositor.py:304`,
      `compositor.py:335`, `desk.py:277`, `prove_unchanged.py:293`, `referrers.py:122`,
      `run_context.py:314`, `verdicts.py:420`. Roy drew the line at *"lexer and compositor are the
      things that are reading files"*; **seven of the nine sites are in neither.**

- [x] T2 -- !! ALL NINE USE `Path.read_text`, WHICH TRANSLATES LINE ENDINGS. `repo.read_raw`
      exists for exactly this and says so -- *"`Path.read_text` ... applies universal-newline
      translation, collapsing every `\r\n` to `\n` before the caller ever sees it"*. ! The
      2026-08-21 wording said seven others read the translating way; the correction is in the
      Objective -- `read_raw` has both the callers its docstring claims, and the nine source reads
      are a different set.

- [x] T3 -- !! SO `compositor.identity` GIVES A FALSE PASS ON EVERY CRLF FILE. `compositor.py:335`
      reads with `read_text`, so it compares its own translated read against its own translated
      output and both sides lose `\r\n` identically. REPRODUCED 2026-08-23: a file written as
      `b'# a note\r\nx = 1\r\n'` reads as `'# a note\nx = 1\n'`, `identity` returns `None`, and
      `set_page` over that page does NOT equal the bytes on disk -- while the same page built from
      `repo.read_raw` sets back byte-exact. ! The instrument reports agreement it did not test.

- [x] T4 -- !! AND IT IS THE NORMAL CASE, NOT AN EDGE. Re-measured 2026-08-23 over 4,686 text
      files in this checkout: **4,023 hold CRLF**, 549 are LF only, 114 have no line ending at
      all. ! The 2026-08-21 reading was 2,957 of 3,080 over a narrower set; the ratio holds and
      the population does not. Roy works on Windows and `CLAUDE.md` says to assume CRLF unless a
      repo says otherwise.

- [x] T5 -- ! EVERY MEASUREMENT TAKEN 2026-08-21 IS THEREFORE NARROWER THAN IT WAS STATED --
      *3,049 of 3,082 byte-identical* is really *identical after newline translation*. The model
      IS lossless over the translated text, which is where every paragraph rule lives, so the
      findings hold; the WORD `byte-identical` does not. Re-taking the number is T14.

- [x] T6 -- ! `draft()` WRITES WITH `newline=""` (`compositor.py:275`), so it emits exactly what
      `set_page` produced -- and `set_page` takes its ending from `page.text`, which arrived
      translated. A run over a CRLF checkout would write LF. ! Invisible in THIS repo, where git's
      `autocrlf` normalises on the way in, and a real change anywhere it does not.

- [x] T7 -- ! IT IS THE SAME CAUSE AS [`bom-is-read-as-source`](bom-is-read-as-source.md), already
      filed: all nine sites read `encoding="utf-8"` where a BOM needs `utf-8-sig`. One decision --
      how to turn bytes into text -- made in nine places, and made the same wrong way in all of
      them. **THAT IS THE ARGUMENT FOR THE LEXER OWNING IT**, rather than tidiness.

- [x] T8 -- * THE SHAPE OF THE FIX follows Roy's own division: the LEXER reads, the COMPOSITOR
      writes and verifies. `page_for` would take a PATH and the lexer would open it -- with
      `repo.read_raw` and `utf-8-sig` -- so encoding, BOM and newline are settled once. Everything
      between carries text it was handed. **RULED 2026-08-23 and written up as a design**; the
      spec goes further, adding the door and the two chains. T9 to T15 are what it takes.

### What implementing the design requires

- [ ] T9 -- **Create `io.py` and move the boundary into it.** The spec names what moves:
      `read_raw` from `repo.py`, `text_lines` and `utf8_console` from `constants.py`, and the
      `newline=""` write from `compositor.py`. `constants.py` keeps `LINE_BREAK` and nothing else
      -- Roy: *"this does not belong in constants.py, just the specific line endings."* Verify:
      `io.py` exists, the four names resolve from it, and `constants.py` exports none of them.

- [ ] T10 -- **Make the rule a GATE, in the family of `check_shipped_syntax.py`.** A match for
      `read_text|write_text|open(` in any shipped script other than `io.py` fails. Verify: the
      check exits nonzero on the tree as it stands, and exits 0 once T11 has landed and the
      remaining readers go through `io.py`. !! This is the task that turns a convention into
      something that can fail, which is the whole point -- see [`docs/gates.md`](../docs/gates.md).

- [ ] T11 -- **Give `page_for` a PATH and let the lexer open it.** `page.py:674` is
      `page_for(path, text, lang, rel=None)` today, so every caller has already read. The lexer
      opens with `io.read_raw` and `utf-8-sig`, and encoding, BOM and newline are settled once.
      Verify: no caller of `page_for` passes text, and every source read in the shipped scripts is
      the lexer's.

- [ ] T12 -- **Fix `compositor.identity` so the round trip is compared in BYTES.** It is the check
      that currently certifies the thing it does not test. Verify with a test that FAILS FIRST: a
      file written `b'# a note\r\nx = 1\r\n'` makes `identity` report a difference before the fix
      and return `None` after, and `set_page` over its page equals the file's bytes.

- [ ] T13 -- **Assert the two chains AS DATA.** Assert the read chain IS
      `[language, read_text, lexer, addresser, page]` and the write chain IS its seven. ! This is
      the test that catches a MISSING check, because the absence is a missing list element rather
      than a forgotten call -- and today `edit`, `set`, `draft` and `approve` are the only write
      steps ever run in sequence, with `lossless`, `identity` and `prove_unchanged` sitting outside
      and nothing calling them between.

- [ ] T14 -- **Re-take the losslessness number through the raw reader before it is quoted again.**
      *"3,049 of 3,082 byte-identical"* was measured over translated text (T5). Verify: the re-run
      reports its population and names the reader that produced it.

- [ ] T15 -- **Correct the spec's `read_raw` row.**
      `docs/superpowers/specs/2026-08-23-io-and-the-chain-design.md:17` states *"the newline-safe
      reader has ZERO callers"*; there are four call sites in two modules. ! The design is
      unaffected -- the seam it argues for is the nine SOURCE reads that bypass `read_raw`, not the
      absence of callers -- but a spec that is wrong about a measurement gets quoted as though it
      were right. Verify: the row names the nine bypassing reads, and `grep -rn "read_raw"` over
      the shipped scripts agrees with it.

## Related

- [`bom-is-read-as-source`](bom-is-read-as-source.md) -- the same nine sites, the same one
  decision, made the same wrong way.
- [`galley-and-compositor-write-path`](galley-and-compositor-write-path.md),
  [`closing-line-deletes-code`](closing-line-deletes-code.md),
  [`computed-and-never-read`](computed-and-never-read.md) and
  [`census-walks-and-flushes`](census-walks-and-flushes.md) -- the other four the design bears on.
- [`lexer-does-not-lex`](lexer-does-not-lex.md) -- the `lexer` -> `TYPECODER` rename, explicitly
  out of the design's scope.
