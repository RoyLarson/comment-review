# The reviewer prose is rules and punishments, not guidance toward a good result

```
Status:   open
Progress: 9 of 17 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-09-06 (Roy, 2026-09-06, on reading the ownership-context agent file and
          the brief as dispatched in a live run over src/: it is so uselessly verbose it
          is disgusting; full of comments and commands about what it should not do that
          distract from the things that matter to accomplishing the goal; written as
          rules and punishments, not as something to guide towards a good result)
```

## Objective

The reviewer prose is rules and punishments, not guidance toward a good result.

## Tasks

- [ ] T1 | Measure the brief and the four role files: lines, marked lines, and
      sentences that prohibit against sentences that describe a good mark.
        > 2026-09-06 The 2026-09-06 prompt was 47,000 characters per role.
- [x] T2 | Brief rewritten to 371 lines, stated positively; pytest green | a9d9de96 | Rewrite
      reviewer-brief.md to guide a role toward a good mark: what to read, what a
      finding is, then the format; each gate stated once.
- [x] T3 | Four role files rewritten positively, each opening with its desk; pytest green | 1563fc58 | Rewrite
      comment-review-ownership-context.md the same way, then the other three
      role files.
- [ ] T4 | Measure the rewrite on the same target as the 2026-09-06 run: the
      same binder, the four copies compared to that run's.
        > 2026-09-06 Copies of that run: the scratchpad run-2026-09-06 directory.
        > 2026-09-07 The Sonnet ownership copy is all clean; compare to the forks' parts
- [x] T5 | the brief tells a role to fill its one copy itself: no sub-agent, no part file, no other copy | e0af5df1 | Update
      the brief so a role does not fork itself into sub-agents writing part
      files outside its one copy.
        > 2026-09-07 2026-09-06: all four roles forked; 0 of 3,552 slots reached a copy.
        > 2026-09-07 Sonnet run: two roles wrote 60 and 35 scripts under the scratchpad
- [x] T6 | Sonnet cleaned all 888; 64 of 64 places the forks marked are real at ab0f9266 | cc699ff0 | Measure
      the Sonnet ownership-context copy: clean x888 against 64 places the Fable
      forks marked, two verified by grep
        > 2026-09-07 compare_oc.py lists the 64; docket_of and the #12 paste verified
- [-] T7 | superseded by Process 162: a change to the prototype mark contract, not made now | 9519ead5 | Update
      the clean row so it owes a reason naming what the role checked under its
      remit, so a clean certifies a read
        > 2026-09-07 Roy 2026-09-07: the system encourages skipping paragraphs
- [x] T8 | The brief says a role RETURNS one file; the script clause is gone | 51977c79 | Update
      the brief so the one-file rule governs what a role RETURNS, not every file
      it writes anywhere
        > 2026-09-07 Roy: the rule was for the source code, extended for no reason
- [x] T9 | The paragraph states the consequence; the shouting markers are gone | 47d31f7a | Update
      the brief's return paragraph to state the consequence plainly, without the
      shouting markers
- [ ] T10 | Update the four role files so each leads with its question and reads
      the whole file. Verify: no role file names a list of parts to read
        > 2026-09-07 module-context is told to read five parts; a body is not one
- [ ] T11 | Update function-context and module-context to say they judge
      composition, whether the parts fit together. Verify: both name that
      question
- [ ] T12 | Delete the prohibitions in the role files that carry no consequence,
      keeping the checklists. Verify: each remaining one names what follows
- [ ] T13 | Verify each instruction for each stage for each role against the
      cli-flow's actual inputs and results. Verify: each disagreement is named
        > 2026-09-08 The brief asked for leading the compositor supplies; no gate saw it
- [-] T14 | SKILL.md rewritten in five parts at 376 lines, accepted by Roy; test_skill_commands green | c68a61a4 | Rewrite
      SKILL.md in five parts, about 250 lines, each thing stated by what it
      does; verify wc -l and test_skill_commands green
- [x] T15 | 7a and 7b name proof --proof and --only; residue-check.md removed by Roy | e0b63f48 | Update
      write.md, review.md, compact.md, residue-check.md to the commands' --help;
      verify 7a and 7b name proof --proof and --only
- [ ] T16 | Add a gate that 7a and 7b prose invoke proof with --proof, not
      --copy; verify it fails on the current SKILL.md first
- [ ] T17 | Update ownership-context to rule a correct or patch on text it
      moves, once mark-defects T27 lands; verify its file names both
