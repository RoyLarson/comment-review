# A serialisation failure and an approved drop are the same bytes

```
Status:   decision-needed
Progress: 0 of 2 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-25 (xhigh wave C on feat/the-write-chain-of-command, finding 2)
```

## Objective

Roy, 2026-08-25, ruling the vacate signal: *"None is explicit enough."* So `""`
is refused and `None` is the delete, in `docket.read` and in
`results/galley.reset` alike.

**A paragraph recording the hazard was written and then cut**, and it said:
*"A NULL IS NOT A DECISION. `--edits` is machine-written from approved text; a
key whose value failed to serialise arrives as `null`."*

! **THE FLIP FROM `""` TO `None` MADE `null` MEANINGFUL**, which is what closes
the gap between the two. A JSON serialiser that fails on one value writes
`null` for it, and there is no reading of the file that separates that from a
`drop` the human approved. The refusal of `""` says two spellings for one act
are a hazard; `null` is now the only spelling, and it is also the default a
failure produces.

**MEASURED 2026-08-25, after wave C wired `commands/galley.py` through
`docket.read`:** `--edits '{"m.py@b0": null}'` prints `1 page(s) set,
0 edit(s) refused` at exit 0 and the comment is gone -- which is what
`flows/proof_setter.run` does too. ! The two now AGREE, and agreeing is what
this wave fixed; whether what they agree on is right is what is open here.

! **IT IS A DECISION ABOUT THE FORMAT, NOT A DEFECT IN EITHER READER.** Any
distinguishable spelling would do -- an object, a sentinel string, a separate
`drop` list -- and choosing one is a ruling, not a repair. `SKILL.md` does not
document the sentinel at all today, so whatever is ruled has to land there as
well, which is `agents` lane work.

## Tasks

- [ ] Rule whether an approved drop keeps a distinguishable spelling from a JSON
      null
- [ ] If it does, change docket.read to that spelling and pin both the
      accept and the refuse
