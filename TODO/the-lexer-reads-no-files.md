# The lexer reads no files, nine other places do, and the identity passes on translated text

```
Status:   in-progress
Progress: 8 of 22 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21: 'The lexer reads zero files - this is also a
          warning - how did the text get there when I stated that it was the lexers job
          to read the files and the compositors job to write the files')
Triaged:  2026-08-23 -- a DESIGN now answers this file. The eight original boxes were
          measurements and arguments; they are ticked and kept verbatim below, and the
          seven tasks after them are what implementing the design requires
Split:    2026-08-23 -- every box cut to two lines. The eight measurements moved into the
          Objective; the seven implementation boxes became eleven, one module per task
Re-split: 2026-08-23 -- the nine boxes still over two lines were cut again. `constants.py`
          held TWO moves, `page_for` held a signature change AND the lexer's own open, and
          `identity` held the fix AND its failing-first test -- each is now two boxes
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
what the seam is for, is that **nine reads of SOURCE bypass it**.

## The measurements this file was filed on -- re-taken 2026-08-23, and not tasks

!! **THE LEXER TAKES `text` AND READS NOTHING**, so the reading it was given as its job happens
somewhere else -- nine times. `grep -c "read_text\|open(\|read_raw" lexer.py` returns 0. The nine,
re-verified 2026-08-23: `census.py:177`, `census.py:336`, `compositor.py:304`, `compositor.py:335`,
`desk.py:277`, `prove_unchanged.py:293`, `referrers.py:122`, `run_context.py:314`,
`verdicts.py:420`. Roy drew the line at *"lexer and compositor are the things that are reading
files"*; **seven of the nine sites are in neither.**

!! **ALL NINE USE `Path.read_text`, WHICH TRANSLATES LINE ENDINGS.** `repo.read_raw` exists for
exactly this and says so -- *"`Path.read_text` ... applies universal-newline translation,
collapsing every `\r\n` to `\n` before the caller ever sees it"*. ! The 2026-08-21 wording said
seven others read the translating way; the correction is the one above -- `read_raw` has both the
callers its docstring claims, and the nine source reads are a different set.

!! **SO `compositor.identity` GIVES A FALSE PASS ON EVERY CRLF FILE.** `compositor.py:335` reads
with `read_text`, so it compares its own translated read against its own translated output and
both sides lose `\r\n` identically. REPRODUCED 2026-08-23: a file written as
`b'# a note\r\nx = 1\r\n'` reads as `'# a note\nx = 1\n'`, `identity` returns `None`, and
`set_page` over that page does NOT equal the bytes on disk -- while the same page built from
`repo.read_raw` sets back byte-exact. ! The instrument reports agreement it did not test.

!! **AND IT IS THE NORMAL CASE, NOT AN EDGE.** Re-measured 2026-08-23 over 4,686 text files in
this checkout: **4,023 hold CRLF**, 549 are LF only, 114 have no line ending at all. ! The
2026-08-21 reading was 2,957 of 3,080 over a narrower set; the ratio holds and the population does
not. Roy works on Windows and `CLAUDE.md` says to assume CRLF unless a repo says otherwise.

! **EVERY MEASUREMENT TAKEN 2026-08-21 IS THEREFORE NARROWER THAN IT WAS STATED** -- *3,049 of
3,082 byte-identical* is really *identical after newline translation*. The model IS lossless over
the translated text, which is where every paragraph rule lives, so the findings hold; the WORD
`byte-identical` does not. Re-taking the number is a task below.

! **`draft()` WRITES WITH `newline=""`** (`compositor.py:275`), so it emits exactly what `set_page`
produced -- and `set_page` takes its ending from `page.text`, which arrived translated. A run over
a CRLF checkout would write LF. ! Invisible in THIS repo, where git's `autocrlf` normalises on the
way in, and a real change anywhere it does not.

! **IT IS THE SAME CAUSE AS [`bom-is-read-as-source`](bom-is-read-as-source.md)**, already filed:
all nine sites read `encoding="utf-8"` where a BOM needs `utf-8-sig`. One decision -- how to turn
bytes into text -- made in nine places, and made the same wrong way in all of them. **THAT IS THE
ARGUMENT FOR THE LEXER OWNING IT**, rather than tidiness.

## The shape of the fix -- RULED 2026-08-23

It follows Roy's own division: the LEXER reads, the COMPOSITOR writes and verifies. `page_for`
would take a PATH and the lexer would open it -- with `repo.read_raw` and `utf-8-sig` -- so
encoding, BOM and newline are settled once. Everything between carries text it was handed.
**RULED 2026-08-23 and written up as a design**; the spec goes further, adding the door and the
two chains. The open tasks are what it takes.

! **`constants.py` KEEPS `LINE_BREAK` AND NOTHING ELSE** -- Roy: *"this does not belong in
constants.py, just the specific line endings."*

!! **THE GATE IS THE POINT.** A rule with no seam is a rule every author has to remember; a check
that refuses a shipped read outside `io.py` is one that can FAIL -- see
[`docs/gates.md`](../docs/gates.md). ! It belongs in the family of
`scripts/check_shipped_syntax.py`, which already refuses a shipped file on a mechanical read.

! **THE CHAIN ASSERTIONS CATCH A MISSING CHECK**, because an absent step is a missing list element
rather than a forgotten call. Today `edit`, `set`, `draft` and `approve` are the only write steps
ever run in sequence, with `lossless`, `identity` and `prove_unchanged` sitting outside and
nothing calling them between.

! **THE SPEC'S `read_raw` ROW IS WRONG ABOUT A MEASUREMENT AND THE DESIGN IS UNAFFECTED** -- the
seam it argues for is the nine SOURCE reads that bypass `read_raw`, not the absence of callers --
**but a spec that is wrong about a measurement gets quoted as though it were right.** ! The row
is at `docs/superpowers/specs/2026-08-23-io-and-the-chain-design.md:17`.

## Tasks

- [x] T1 -- MEASUREMENT, not a task: the lexer reads nothing and nine other places do.
      Stated in the Objective, with the nine sites re-verified 2026-08-23.
- [x] T2 -- MEASUREMENT, not a task: all nine read through `Path.read_text`, which
      translates line endings. Stated in the Objective.
- [x] T3 -- MEASUREMENT, not a task: `compositor.identity` gives a false pass on every
      CRLF file, REPRODUCED 2026-08-23. Stated in the Objective.
- [x] T4 -- MEASUREMENT, not a task: 4,023 of 4,686 text files in this checkout hold CRLF,
      so it is the normal case. Stated in the Objective.
- [x] T5 -- MEASUREMENT, not a task: every 2026-08-21 number is narrower than it was
      stated, being identity after newline translation. Stated in the Objective.
- [x] T6 -- MEASUREMENT, not a task: `draft()` writes with `newline=""`, so a CRLF
      checkout would be written back LF. Stated in the Objective.
- [x] T7 -- ARGUMENT, not a task: the same one decision as `bom-is-read-as-source`, made
      nine times the same wrong way. Stated in the Objective.
- [x] T8 -- RULING, 2026-08-23: the lexer reads, the compositor writes and verifies, and
      `page_for` takes a PATH. Stated in the Objective as *The shape of the fix*.
- [ ] T9 -- **Create `io.py` and move `read_raw` into it from `repo.py`.** Verify:
      `io.read_raw` resolves, and `repo.py` defines no reader.
- [ ] T10 -- **Move `text_lines` out of `constants.py` into `io.py`.** Verify: it resolves
      from `io.py`, and `constants.py` no longer defines it.
- [ ] T11 -- **Move `utf8_console` out of `constants.py` into `io.py`.** Verify: it
      resolves from `io.py`, and `constants.py` exports `LINE_BREAK` and nothing else.
- [ ] T12 -- **Move the `newline=""` write out of `compositor.py` into `io.py`.** Verify:
      `grep -n 'newline=' compositor.py` returns nothing.
- [ ] T13 -- **Write the read/write gate**: a shipped `read_text|write_text|open(` outside
      `io.py` fails. Verify: it exits nonzero on the tree as it stands, naming each site.
- [ ] T14 -- **Give `page_for` a PATH instead of text.** Verify: no caller of `page_for`
      passes text, and the signature takes a path.
- [ ] T15 -- **Let the lexer open the file, with `io.read_raw` and `utf-8-sig`.** Verify:
      a CRLF file carrying a BOM reads back with both preserved.
- [ ] T16 -- **Route the nine bypassing source reads through `io.py`.** Verify: T13's gate
      exits 0 on the tree, and every source read in the shipped scripts is the lexer's.
- [ ] T17 -- **Fix `compositor.identity` so the round trip is compared in BYTES.** Verify:
      it reads through `io.read_raw` and not `read_text`.
- [ ] T18 -- **Test `identity` on a CRLF file, FAILING FIRST.** Verify: a file written
      `b'# a note\r\nx = 1\r\n'` reports a difference before the fix and `None` after.
- [ ] T19 -- **Assert the READ chain as data**: it IS `[language, read_text, lexer,
      addresser, page]`. Verify: the test fails when a step is removed from the list.
- [ ] T20 -- **Assert the WRITE chain as data**, the seven steps named in the Objective.
      Verify: the test fails when a step is removed from the list.
- [ ] T21 -- **Re-take the losslessness number through the raw reader.** Verify: the
      re-run reports its population and names the reader that produced it.
- [ ] T22 -- **Correct the spec's `read_raw` row, cited in the Objective.** Verify: the
      row names the nine bypassing source reads rather than an absence of callers.
## Related

- [`bom-is-read-as-source`](bom-is-read-as-source.md) -- the same nine sites, the same one
  decision, made the same wrong way.
- [`galley-and-compositor-write-path`](galley-and-compositor-write-path.md),
  [`closing-line-deletes-code`](closing-line-deletes-code.md),
  [`computed-and-never-read`](computed-and-never-read.md) and
  [`census-walks-and-flushes`](census-walks-and-flushes.md) -- the other four the design bears on.
- [`lexer-does-not-lex`](lexer-does-not-lex.md) -- the `lexer` -> `TYPECODER` rename, explicitly
  out of the design's scope.
