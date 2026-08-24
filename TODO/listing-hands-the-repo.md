# The listing hands every reviewer the whole repo, four times a page

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (measuring what a reviewer is actually charged for, while scoping
          the binder trim)
```

## Objective

**92% of what a reviewer reads is a list of files it is not reviewing.** MEASURED 2026-08-24,
`census.py --repo . --filtered <one file>`:

| file under review | the census part | the `NOT CHECKED` tail | tail's share |
| --- | --- | --- | --- |
| `repo.py` | 41 lines, 2,716 b | 279 lines, 31,434 b | **92%** |
| `page.py` | 204 lines, 17,371 b | 279 lines, 31,434 b | **64%** |
| `constants.py` | 27 lines, 1,686 b | 279 lines, 31,433 b | **94%** |

!! **IT IS BYTE-IDENTICAL ACROSS ALL THREE, BECAUSE IT IS A FACT ABOUT THE REPO.** Every tracked
file the name harvester cannot read, one per line, at an ABSOLUTE path:

```
NOT CHECKED -- these are gaps, not passes:
    C:/Users/Roy/projects/comment-review/.gitignore (no name harvester for unknown)
    C:/Users/Roy/projects/comment-review/CLAUDE.md (no name harvester for unknown)
```

!! **AND IT IS CHARGED FOUR TIMES A PAGE.** Stage 4 pastes this listing to four roles, so one
page costs **31,434 x 4 = 125,736 bytes** of the same sentence. It grows with the REPO and not
with the work: reviewing a 43-line file, 94% of what each role reads is this list.

! **THE GAP REPORT IS REAL AND MUST NOT SIMPLY BE DELETED.** A reviewer that does not know name
resolution was partial will read an UNRESOLVED annotation as a finding rather than as a gap --
which is the distinction the block's own heading draws, *"these are gaps, not passes."* **What is
wrong is its PLACE, not its existence.** It belongs to the run, stated once.

! **THE ABSOLUTE PATHS ARE A SECOND DEFECT IN THE SAME BLOCK.** Every other position this system
emits is repo-relative -- an address, a citation, a census `path` -- because a reviewer resolves
them against `REPO ROOT`. These name a directory on one machine.

!! **AND THE FILTER IS NOT THE PROBLEM, WHICH IS WHAT THE MEASUREMENT WAS FOR.** `--filtered`
does collapse every no-prose row: `Kind.holds_no_prose` answers True for all 105 of `repo.py`'s
115 non-prose rows. Making it DROP them outright rather than collapse them into run lines was
tried on 2026-08-24 as a temporary edit and saved **3.7%** over three files. ! The run lines are
not where the bytes are, and a trim aimed at them would have been measured against the wrong
thing.

## Tasks

- [ ] T1 -- Record what each part of the listing costs, per page. Verify: the split above
      is re-derivable from one named command.
- [ ] T2 -- State `NOT CHECKED` once per run rather than once per page. Verify: a second
      page's listing does not repeat it.
- [ ] T3 -- Make its paths repo-relative. Verify: no listing holds an absolute path.
- [ ] T4 -- Re-measure the listing after both. Verify: before and after, from named
      commands, are written into this file.

## Related

- [`census-row-carries-empty-fields`](census-row-carries-empty-fields.md) -- the other half of
  what the binder emits: the fields on a row, where this is the block beneath them
- [`the-census-is-mostly-intervals-nobody-rules-on`](the-census-is-mostly-intervals-nobody-rules-on.md)
  -- which ROWS reach a reviewer, where this is what reaches them beside the rows
- [`language-rows-in-toml`](language-rows-in-toml.md) -- T14 gates the harvester on a row field
  rather than on `lang.name`; that changes WHICH files land in this block, not where it is
  printed
