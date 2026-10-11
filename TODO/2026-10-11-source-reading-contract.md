# Define shared source reading contracts

```
Status:   open
Progress: 17 of 18 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-11 (2026-10-11 lexical-reader design)
```

## Objective

Define shared source reading contracts.

## Tasks

- [x] T1 | Immutable source representation preserves exact text and classifications; all checks and review pass | 1c455282 | Represent
      source as ordered regions and ownership facts; verify exact reconstruction
      and independently expected classifications
- [ ] T2 | Carry reader compatibility and language settings through saved runs;
      verify incompatible contexts refuse before address use
- [x] T3 | Invalid region kinds raise ValueError; rejection and preservation tests pass review | 1c455282 | Reject
      invalid SourceRegion kinds; verify unknown strings, None and mutable
      values raise ValueError
        > 2026-10-11 Review: source.py:66 accepts mutable and unknown kinds
- [x] T4 | Non-string text raises ValueError before structural validation; focused tests pass review | 1c455282 | Reject
      non-string SourceStructure text; verify lists, bytes and None raise
      ValueError before caching
        > 2026-10-11 Review: source.py:143 accepts mutable text and bytes
- [x] T5 | Immutable outcomes and invalid-state checks verified | 42752127 | Define
      immutable read diagnostics and failures; verify location units, field
      validation and successful empty input
- [x] T6 | Page and proof refusals plus multi-file rollback verified | 9cdff430 | Reject
      failed readings at page and proof admission; verify either-side failures,
      empty success and cleanup
- [x] T7 | Unsupported-syntax fixture runs only on affected interpreter | 2b50b752 | Make
      unsupported-syntax fixtures interpreter-aware; verify valid newer Python
      syntax is not required to fail
        > 2026-10-11 Review: test_reading_diagnostics.py:21 assumes Python 3.11 syntax
- [x] T8 | Normal script imports and page outcomes verified by regression | a8b18c66 | Repair
      render_page package imports and page outcomes; verify its normal command
      on successful and refused source
        > 2026-10-11 Found during migration: render_page imports retired flat modules
- [x] T9 | Sibling docstring describes present selection behavior | 6738562f | Describe
      sibling selection as current behavior; verify its docstring contains no
      incident narrative
        > 2026-10-11 Review: flows/prove_unchanged.py:30 narrates an old incident
- [x] T10 | Equal malformed sources report failed page admission | fd1e56a1 | Admit
      equal taken_in source snapshots before skipping; verify identical
      malformed sources report refusal
        > 2026-10-11 Review: commands/taken_in.py:94 skips equal malformed text
- [x] T11 | Named exception groups retain classification and Python floor | fd1e56a1 | Name
      source acquisition exception groups; verify handlers avoid literal tuples
      and retain failure classification
        > 2026-10-11 Review: flows/source.py:39,51,55 use literal exception tuples
- [x] T12 | Machine supplies hashing to pure compatibility; unchanged import gates pass | 9913333b | Keep
      compatibility hashing behind the machine boundary; verify import gates and
      canonical digests pass
        > 2026-10-11 Review: reading/context.py:6 breaks the hashlib ownership gate
- [x] T13 | Compositor example uses supplied Page; scoped review passes | 843b3d40 | Update
      the compositor page example for required context; verify its call matches
      the current interface
        > 2026-10-11 Review: results/compositor.py:36 omits required page reading
- [x] T14 | Shipped copy example carries explicit context and parses in normal full suite | 9159b117 | Add
      required reading metadata to the reviewer copy example; verify the shipped
      JSON parses as an edit copy
        > 2026-10-11 Review: reviewer-brief JSON example lacks required Sheet reading
- [x] T15 | Returned and stage contexts agree without expanding shard coverage; regression passes | 8532c4f7 | Compare
      extra returned sheets with stage contexts; verify mismatches refuse
      without widening coverage
        > 2026-10-11 Review: verify.py:218 omits returned versus stage comparison
- [x] T16 | Zero-copy binder admission precedes addresses; refusal spies and empty positives pass | 8532c4f7 | Admit
      binder contexts with zero returned copies; verify refusal before coverage
      and valid empty binders
        > 2026-10-11 Review: verify.py:252 skips admission with zero copies
- [x] T17 | Shared page lookup refuses missing context before acquisition; regression and review pass | fe51b684 | Reject
      missing known-page context in resolution lookup; verify no source
      acquisition or cached default
        > 2026-10-11 Review: verify.py:210 defaults a known path missing context
- [x] T18 | Lookup prose describes explicit failures and omitted text; scoped review passes | fe51b684 | Correct
      lookup result prose; verify failure and text omission descriptions match
      current APIs
        > 2026-10-11 Review: fill.py:343 and verify.py:235 describe erased failures
