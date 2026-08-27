# notations and annotations are one letter apart and mean different things

```
Status:   in-progress
Progress: 3 of 4 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-25 (backend, 2026-08-25, naming what the agent workflow hands the
          write chain)
Updated:  2026-08-26 — RULED. The name is `alteration`, and the write side gets all
          three containers to mirror the read side's: an ALTERATION is one change at one
          address (row), a SCHEDULE is every alteration for one page with that page's
          path and sha (page), a DOCKET holds every schedule (binder). Roy: "like the
          binder we have three levels of containers -- paragraph, page, binder. We have
          to be able to unwind the alterations pretty close to the same way." Recorded
          in decision-log.md Vocabulary: #14, which supersedes Process: #25 -- the entry
          that named `notations` stays as written, because it is the record of what was
          decided on the 25th. THE INSTINCT BEHIND `notations` WAS RIGHT AND THAT IS WHY
          IT COLLIDED: Roy, "if I was writing between the lines with marks in red pen I
          think of those red marks as notations." The trade calls those proof correction
          marks, and `mark` is already defined here as what stage 4 emits -- so the word
          was reaching for something the register had. What needed a name was the desk's
          OUTPUT. THE FOUR TERMS ARE IN docs/vocabulary.md AND DELIBERATELY NOT IN
          references/vocabulary.toml: check_vocabulary.check_complete counts a
          definition no role is given as a hole (NO RECIPIENT), so the shipped register
          would go red. They cross over the day a role's own prose uses one, which is
          the same reason `binder` has never been in it. THE CODE RENAME HAS NOT
          HAPPENED and is task 3 below -- measured as two import lines, one CLI flag,
          one filename, ~21 descriptive sentences, 5 tool-regenerated README rows, and 4
          quoted-Roy lines that must not be touched.
```

## Objective

RULED 2026-08-26: the name is `alteration`, and the write side takes all three containers so it mirrors the read side. An ALTERATION is one change at one address, mirroring a row; a SCHEDULE is every alteration for one page, carrying that page's path and the sha it was read at, mirroring a page; a DOCKET holds every schedule, mirroring the binder. Roy: *"like the binder we have three levels of containers -- paragraph, page, binder. We have to be able to unwind the alterations pretty close to the same way."*

WHAT THE COLLISION WAS: `notations` sat one letter from `annotations`, which `binder/annotate.py` owns for candidate flags on a paragraph -- two words one letter apart, both meaning marks attached to a paragraph, in adjacent areas.

THE INSTINCT WAS RIGHT AND THAT IS WHY IT COLLIDED. Roy: *"if I was writing between the lines with marks in red pen I think of those red marks as notations."* The trade calls those PROOF CORRECTION MARKS, and `mark` is already defined here as what stage 4 emits -- so the word was reaching for something the register already had. What needed naming was the DESK'S OUTPUT, and a change to type already set is an alteration.

The ruling is `docs/decision-log.md` Vocabulary: #14, superseding Process: #25. The four terms are in `docs/vocabulary.md` and deliberately NOT in `references/vocabulary.toml`, because `check_vocabulary.check_complete` counts a definition no role is given as a hole.

WHAT REMAINS is the code rename and the nested shape -- tasks 3 and 4. Measured cost of the rename: two import lines, one CLI flag, one filename, ~21 descriptive sentences, 5 tool-regenerated README rows, and 4 quoted-Roy lines that must not be touched.

## Tasks

- [x] Relitigate the pair when the middle piece is rewritten -- declare both with
      distinct definitions, or rename one
- [x] Whatever is decided reaches references/vocabulary.toml and
      docs/vocabulary.md in the same change
- [x] Rename notations -> alterations in the code: desk/notations.py, the two
      importers (commands/proof.py and flows/proof_setter.py), the --notations
      flag, and the filename TODO/an-alteration-carries-its-own-indentation.md. The
      four quoted-Roy lines in decision-log.md and nothing-makes-the-fair-copy.md
      stay exactly as written
- [ ] Give the docket the nested shape the ruling names -- pages, each with path,
      sha and its schedule of alterations -- so by_page stops re-deriving the
      grouping from the address, and the write chain stops reading the binder to
      get a sha
