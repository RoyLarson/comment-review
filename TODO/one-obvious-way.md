# One obvious way

```
Status:   open
Progress: 4 of 40 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-11-05 (Process #281 and the three flow audits, 2026-11-05)
```

## Objective

Every job in the flows is done one way: one implementation is kept and the
others are removed (Process #281).

Three read-only audits on 2026-11-05 found jobs done by two or more code paths.
The highest risks are where two stages can disagree about the same file or
address: whether an address is real (verify, fill and held_at decide it three
ways), how a flattened name becomes a path (real_path, printed_name, fill's
_sheet_for, master_proof), and whether a file outside --repo is in the run
(gather admits it, prove_unchanged refuses it). The rest are artifact loading
and saving, root handling, refusal reporting, and logic that sits in commands
instead of flows. The audits read the code and reproduced nothing; each task's
evidence is checked when the task is worked.

## Tasks

- [ ] T1 | Make fill read the page an address names through page_named
- [ ] T2 | Make held_at refuse a cue its page lacks instead of returning empty
      text
- [-] T3 | SUPERSEDED by T39 (folded or exact) and T40 (applying it) | 12128409 | Make
      one rule, folded or exact, decide an address's path half for verify,
      transcribe, fill, bus and check
- [ ] T4 | Make master_proof and fill invert a flattened name through real_path
- [ ] T5 | Make gather refuse a file outside --repo, as prove_unchanged does
- [ ] T6 | Make fill split an address with cue_of
- [ ] T7 | Make page.py and paragraph.py read a cue with cue_of
- [ ] T8 | Make carry print addresses with address_for
- [ ] T9 | Make the compositor, prove_unchanged and taken_in read a file through
      one page reader
- [ ] T10 | Make fill's quoted_sources use the collator's line reader
- [ ] T11 | Make every command save its JSON through proof_io
- [ ] T12 | Add load_topology to proof_io for collate, distribute and topology
- [ ] T13 | Make the answers file read through proof_io with READ_ERRORS
- [ ] T14 | Make every command resolve its repo root once, from the binder's
      root where it has one
- [ ] T15 | Move the exit codes and refusal printing into one console module
- [-] T16 | SUPERSEDED by T22: 82cee747 removed the collate/bus repeats; only the carry command repeats | 22c3a0abcbc86509c74296319ce5b719a43338ca | Remove
      the reading-context checks repeated in bus, the carry command and the
      collate command
- [ ] T17 | Move the flow logic out of the commands into flows
- [ ] T18 | Remove stable() from binder/addresses
- [ ] T19 | Add load_docket to proof_io
- [ ] T20 | Make proof load its proof, copy and docket through proof_io
- [x] T21 | Ruled: flows return (result, reasons), filed as T23; Process #353 | 4e5eaa107e34071d082f7b76568d207f176bb478 | Decide
      how a flow reports a refusal
        > 2026-11-05 Today: raise, return a reason tuple, or emit events
        > 2026-11-22 Outcome: flows return (result, reasons) (Process #353)
- [ ] T22 | Remove commands/carry.py's binder_reading_contexts call, which
      flows/carry.py repeats
        > 2026-11-22 Check: binder_reading_contexts runs once per carry
- [ ] T23 | Convert the flows that raise a refusal to return (result, reasons),
      as Process #353 rules
        > 2026-11-22 Check: no flow raises CannotTranscribe or AddressesMoved
- [ ] T24 | Resolve path arguments against --repo, not the cwd, in
      commands/referrers.py:51, prove_unchanged, compositor, taken_in
        > 2026-11-22 Check (M4): referrers from outside the root lists the 8 referrers
        > 2026-11-23 comment-review 2026-11-23: every path outside --repo from elsewhere
- [ ] T25 | Fold the address half like the page name in binder/addresses.py:46
      addresses resolve
        > 2026-11-22 Check (M25): addresses resolve M.py@b1 names the real place
- [ ] T26 | Pass the copy's read_from root to fill when mark runs without
      --repo, at commands/mark.py:248
        > 2026-11-22 Check (M30): compact.md:36-38 as written exits 0
- [ ] T27 | Make constants.py:134 utf8_console set stderr to UTF-8 as it does
      stdout
        > 2026-11-22 Check (M32): piped stderr of a non-ASCII NOT GATHERED line is UTF-8
- [ ] T28 | Refuse a POSIX name holding a backslash at flows/gather.py:198,
      which flattens it onto the slash path's address
        > 2026-11-22 Check (M52): a repo with a\b.py beside a/b.py is refused at gather
- [ ] T29 | Stop reading/addresser.py:931 folded using full casefold, which
      merges Strasse.py with its sharp-s spelling
        > 2026-11-22 Check (M83): Strasse.py and its sharp-s spelling get two addresses
- [ ] T30 | Sort an address-less entry beside its page in flows/mark_errors.py
        > 2026-11-23 where spells the path with /, an address with :; key misorders
- [ ] T31 | Name the unreadable-context refusal in flows/revise.py apart from
      AddressesMoved
        > 2026-11-23 Missing context, unreadable page also raise AddressesMoved
        > 2026-11-23 commands/proof.py prints all as "the address space moved"
- [x] T32 | Ruled: commands invoke flows, flows chain flows; work is T38 | 0ae9cbb99461eeae2b3f7e5b5932918a6269e958 | Decide
      where the commands' own file reads and writes belong
        > 2026-11-23 topology --verify/--out, proof read_text+json.dumps, report
        > 2026-11-23 carry/gather/distribute binder json.dumps; see T11 T12 T13 T20
        > 2026-11-23 Options: move the I/O into flows, or restate the commands fence
        > 2026-11-23 Outcome: commands invoke flows, flows chain flows; #383
- [ ] T33 | Add one helper for enum-class membership, which raises on Python
      3.11
        > 2026-11-23 Sites: desk/proof/mark.py x4, desk/stages.py x2, desk/topology
        > 2026-11-23 Sites: flows/proof_setter.py, __main__.py
- [ ] T34 | Give the null sha folded to an empty string one owning function
        > 2026-11-23 Sites: Sheet.seed, Sheet.deserialize, binder/page.py, docket.py
- [ ] T35 | Give the read_from copy one owner beside read_from_problem
        > 2026-11-23 Sites: bind, Binder.deserialize, Binder.serialize, EditCopy.seed
        > 2026-11-23 Sites: EditCopy.deserialize, EditCopy.serialize, bus._on_copies
- [ ] T36 | Make flows/fill.py marks_on reuse sheet.py _sorted_entries' split
        > 2026-11-23 Both skip untouched entries, read_mark the rest
- [ ] T37 | State the checked: dict ty workaround's reason in one place
        > 2026-11-23 Stated in docket, answers, edit_copy, binder; two reasons differ
- [ ] T38 | Move each command's file reads and writes into the flow it invokes
- [?] T39 | Decide whether an address's path half is matched folded or exact
- [ ] T40 | Make the matching T39 chooses decide an address's path half for
      verify, transcribe, fill, bus and check
