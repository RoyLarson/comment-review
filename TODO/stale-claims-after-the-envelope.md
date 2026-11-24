# Shipped prose still describes formats and flags this branch deleted

```
Status:   open
Progress: 7 of 20 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
Re-checked: 2026-08-23 -- one of the four is fixed: `addresser.py` no longer names
          `--repo` anywhere. The other three are live, and every line number in the
          file had moved.
SPLIT:    2026-08-23 -- the boxes were cut to two lines each. Old T1 held the record
          format AND the `--seed` self-contradiction, and old T3 held the re-take AND
          naming the command that produced the cues; four tasks became six
```

## Objective

**Shipped prose still describes formats and flags this branch deleted.** These are the obituary
class `block-context` is chartered to catch, shipping inside the tool that catches it. Re-taken
2026-08-23; the citations below are today's.

### What the boxes carried -- the citations, moved out of the tasks

! **T1 -- the second record format, four sites in `record.py`.** `:6-11` says a record *"used to
travel as prose that `verdicts.py` reconstructed a table from by guessing where each field
ended"*; `:518` returns *"the rendered claim for a text record"*; `:573-584` explains *"the
marker form the text record carried"* and what *"the old format carried"*. ! The fifth site,
said to be in `desk.py`, was NOT found on re-read: its history lines (`:130`, `:207`) are about
`desk`'s own behaviour, not a second record format. ! `uv run pytest -q` must stay green.

! **T2 -- the same paragraph contradicts itself.** `record.py:14` says `--seed` writes a slot
with *"`paragraph` and `address` already in it"*, while `record.SEEDED` is `("place", "anchor")`
and `:699` reads *"THE ADDRESS AND NOTHING ELSE"*.

! **T3.** `addresser.py`'s module usage line named `--repo`, which argparse rejects.

! **T4 and T5 -- the uniqueness example.** `docs/addressing.md:142` states *"Every ADDRESS is
unique -- measured `a0 b1 b2 b3 c1 c2`"* over the five-line example directly above it. MEASURED
2026-08-23: `addresser.py:85` rules that **every series starts at 0**, and `f0` -- the file's own
matter -- is a fourth series that the cue emits at the module (`:78`, `:176`), so the cited
spelling cannot be what that example yields. ! `CLAUDE.md` calls this file the crux, and the
command that produced the cues has to be named beside them.

! **T6 -- the record envelope.** `reviewer-brief.md:93-107` shows a bare `{page, records}` while
`record.seed()` writes `{record_version, reviewer, allowed, pages, code_concerns}`
(`record.py:873-883`), with the pages under `pages` -- and the brief is a reviewer's only spec
for the shape this branch changed.

## Tasks

- [-] T1 | record.py and its second-format prose left src/ in b50e7a43; grep of src/ for that prose is empty | b50e7a43 | T1
      -- Take the second record format out of `record.py`'s prose -- :6-11, :518
      and :573-584. Verify: no shipped script describes a record format the code
      cannot read.
- [-] T2 | SUPERSEDED -- record.py left src/ for prototype/original/, so the two paragraphs that disagree are not in shipped code | b50e7a4 | T2
      -- Settle what `--seed` writes: `record.py:14` says `paragraph` and
      `address`, `record.SEEDED` and :699 say the address alone. Verify: the two
      agree.
- [x] T3 | FINISHED | unknown | T3 -- FINISHED. `addresser.py`'s usage line no
      longer names `--repo`. RE-MEASURED 2026-08-23: zero occurrences, and `:3`
      reads the `--census --anchor --series` form.
- [-] T4 | SUPERSEDED by T10: the example moved to docs/addressing.md:141; the census is now the gather | 22c3a0abcbc86509c74296319ce5b719a43338ca | T4
      -- Re-take the uniqueness cues at `docs/addressing.md:142`; `a0 b1 b2 b3
      c1 c2` cannot be what that example yields. Verify: the cues are what a
      census prints.
- [-] T5 | SUPERSEDED by T11: the sentence moved from docs/addressing.md:142 to :141 | 22c3a0abcbc86509c74296319ce5b719a43338ca | T5
      -- Name the command that produces those cues beside the sentence at
      `docs/addressing.md:142`. Verify: running it prints the cues the sentence
      states.
- [x] T6 | d34f4a29 gave the brief its envelope; reviewer-brief.md:121 shows role/read_from/sheets as edit_copy.serialize writes | d34f4a29 | T6
      -- Give the record shape in `reviewer-brief.md:93-107` its envelope.
      Verify: `record.py --check` accepts a file filled to match the brief's
      JSON.
- [ ] T7 | T7 -- Update the two false claims in
      `src/comment_review/docket/__init__.py`. Verify: `grep -rn
      "addresser\\|address_for\\|cue_of" src/comment_review/docket/` matches no
      code, so line 14-15 no longer claims the package reads an address with the
      addresser; and line 16 no longer says the desk that fills the docket does
      not exist -- `desk/collator.py:982` `docket_from` fills it and
      `tests/test_docket.py:181-293` exercises it through seven cases.
- [-] T8 | SUPERSEDED by T12: the docket's role is written by flows/transcribe.py, not desk/collator.py:1021 | 22c3a0abcbc86509c74296319ce5b719a43338ca | T8
      -- Update the claim at `src/comment_review/commands/taken_in.py:11-12`,
      printed to the user at line 120, that a docket carries a `role` field and
      "no docket does yet". Verify: the sentence agrees with
      `desk/collator.py:1021`, which writes `"role": role`, and with
      `tests/test_docket.py:184`; the rest of the paragraph -- that this command
      receives two bare directories and so has no `Pulled` -- is unchanged.
- [ ] T9 | Delete the sentences naming `galley` as the old name of `proof`
        > 2026-11-22 Check: no src/ comment calls `galley` a name of `proof`
- [ ] T10 | Correct the cues at docs/addressing.md:141 to what gather yields for
      that example
        > 2026-11-22 Check: the stated cues match a gather of the example
- [ ] T11 | Name the command that yields the cues beside docs/addressing.md:141
        > 2026-11-22 Check: running it prints the cues the sentence states
- [ ] T12 | Correct commands/taken_in.py:11-12, which says no docket carries
      `role` yet
        > 2026-11-22 Check: the sentence agrees with docket.Schedule's role field
- [ ] T13 | Remove carry from the module inventory in flows/__init__.py
- [ ] T14 | Correct concordance/__init__.py, which says the gather resolves what
      a comment cites
- [ ] T15 | Remove results/prove_unchanged and flows/carry from
      docs/design/README.md
- [ ] T16 | Remove prove_unchanged.py from docs/design/results/README.md
- [ ] T17 | Update docs/vocabulary.md's annotation entries, now that the gather
      attaches none
- [ ] T18 | Remove the deleted annotate.py and Paragraph.annotations from
      test_docket.py and test_binder.py
- [ ] T19 | Correct binder/__init__.py's annotation entry, which vocabulary.toml
      contradicts
- [ ] T20 | Correct test_binder.py's redaction docstring, which names Paragraph
      fields that are gone
