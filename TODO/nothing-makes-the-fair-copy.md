# Nothing turns the collated marks into the paragraph the galley writes

```
Status:   open
Progress: 1 of 13 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-24 (Roy: the galley only really needs this address gets this paragraph,
          and the system assumes verdicts and records are what it writes from)
Updated:  2026-08-24 — THE CHAIN IS RULED END TO END -- decision-log.md Process: #14.
          Roy, 2026-08-24: 'The binder goes to the agents the agents make there marks on
          something (I am think notations) the desk system takes the notations and the
          binder and emits an update {address: new paragraph}. The galley gets a list of
          the updates (list is loose here it needs more like the page sha). The workflow
          reloads the page sends the page through the galley with the updates. Then
          after the updates finished sends that to the compositor. Sends that through
          the page system again to make certain that the agents put the right comments
          in the right places. The that gets shown to the human.' So what carries an
          answer IS {address: new paragraph}, emitted by the DESK, and the galley needs
          the page SHA beside it. The name for what an agent emits -- 'notations' -- is
          proposed, not settled. NOTHING TRANSFERS FROM THE BINDER TO THE END: the write
          path reloads the page from disk and takes only the address, which is a key
          rather than data.
Updated:  2026-08-26 — THE SHA'S PROVENANCE BECAME UNENFORCED ON 2026-08-26, and this
          TODO is where it is fixed. The docket now carries each page's path and sha, so
          proof_setter.run no longer takes a binder -- decision-log.md Vocabulary: #14.
          Roy asked the right question of it: "how did the transfer happen?" IT DOES
          NOT. MEASURED: nothing in src/ or scripts/ writes the nested shape; the only
          two files naming it are the reader and the command's help string. A docket is
          written by hand today. WHAT THAT COSTS: _one compares the schedule's recorded
          sha against the page it reads from disk now. If the desk -- or a human --
          computes that sha from the FILE at docket-writing time rather than taking it
          from the binder the agents read, the comparison asks whether the file equals
          itself and CANNOT FAIL. That is the shape docs/gates.md records the round trip
          scoring 699 of 699 on, and it is the failure Roy's own sha ruling exists to
          prevent: "we can't assume that the file didn't change between original read
          and loading to write and so getting it out of the json blob is important." !
          NEITHER FORM WAS ENFORCED -- a binder is also just JSON on disk -- but the
          binder has a PRODUCER (census) and the docket has none, so the earlier shape
          had a path by which a correct sha arrived and this one does not. ! ROY ALREADY
          RULED WHO DOES THE TRANSFER, 2026-08-24, quoted in this file's own Updated
          note: "the desk system takes the notations and the binder and emits an update
          ... it needs more like the page sha." So the desk reads the BINDER for the sha
          and copies it onto the schedule. That is a constraint on the producer this
          TODO is about, which is why it is recorded here rather than as its own file.
```

## Objective

!! **THERE IS A HOLE IN THE CHAIN AND BOTH SIDES OF IT DESCRIBE IT DIFFERENTLY.** Roy,
2026-08-24: *"the system assumes that verdicts and records are what is used to write from the
galley, but the galley only really needs this address gets this paragraph and that replaces the
current page paragraph. So we have a missing piece in the chain."*

```
census -> record -> collate -> [ NOTHING ] -> galley -> compositor -> prove
```

! **THE GALLEY'S CONTRACT IS ALREADY RIGHT AND MINIMAL.** `galley.py:5`: `--edits` is
`{"<address>": "<the replacement text>"}`. It does not want verdicts, records, roles or reasons
-- an address and a paragraph.

!! **WHAT IS MISSING IS ANYTHING THAT PRODUCES THAT FILE.** MEASURED 2026-08-24: outside
`galley.py` itself, `edits.json` appears **once** in the tree -- `SKILL.md:919`, the command line
that CONSUMES it. **No module writes it, no gate checks it, and no test builds one.**

!! **AND THE TWO SHIPPED STATEMENTS ABOUT IT CONTRADICT EACH OTHER.**

| where | what it says |
| --- | --- |
| `SKILL.md:925` | *"the same address the record carries, so **nothing between stage 5 and the galley converts**"* -- the task agent types it |
| `galley.py:173` | *"`--edits` is **machine-written** from approved text"* -- a producer that is not in this tree |

! **The galley's comment is the one that is false**, and it is load-bearing: the paragraph under
it refuses a non-string replacement precisely because *"a key whose value failed to serialise
arrives as `null`"* -- reasoning about a serialiser nobody wrote.

### What the missing piece does

**For one address, it states the paragraph that replaces what is there, and names the marks that
paragraph answers.** It carries no reasoning, no role and no verdict onward -- those stay on the
proof.

!! **RULED 2026-08-24: IT COMPOSES MECHANICALLY, AND A CONTRADICTION GOES TO REVISE.** Roy:
*"multiple answers can be true, not just either this or that ... where things do not conflict and
come back clean that is probably a single transform from verdict in to something to be written."*
So the marks on one address are applied in the synthesis order `SKILL.md` already states --
`query`, then `move`/`drop`, then `correct`, then `patch`, then `add` -- and several true answers
compose without anyone choosing between them.

! **CORRECTED SAME DAY: this said *only a contradiction STOPS it*.** A contradiction stops
nothing. It goes back to the roles, at most twice, and returns as a `stet` -- see below.

! **THE UNCONTESTED CASE IS NEARLY IDENTITY.** A record already carries `change`, the full-length
replacement text, so one mark on one address needs no composition at all. That is why this looked
like nothing was missing.

!! **RULED 2026-08-24: EVERY MARK IS NAMED OR THE RUN REFUSES.** The artifact carries address ->
text -> the marks it answers, and a mark that reached the collator and appears in no final
paragraph stops the run. ! **This is the only thing that makes a silently dropped finding
detectable.** Without it, the step between the proof and the galley is where a finding can vanish
with nothing to show it was ever raised -- which is the residue problem one stage earlier than
`residue-check.md` looks.

! **IT DECIDES NOTHING, AND NEITHER DOES THE COLLATOR.** `collating` is *transferring every hand's
marks onto ONE proof ... it decides nothing* (`docs/vocabulary.md`). Ruling belongs to the copy
chief (`decision-log.md Vocabulary: #11`). This piece EXECUTES the ruling; where there is no
ruling to execute it composes, and where it cannot compose it sends the paragraph to revise.

!! **THE NAME IS ROY'S AND IS NOT SETTLED -- T1.** The slug uses **fair copy**, the trade's term
for the clean corrected text written out for the compositor, as a working candidate ONLY. ! Per
`CLAUDE.md`'s method the name comes LAST: what the thing IS is above, and the trade's word for
that job is what gets ratified -- the way `compositor` was, in two words, after `page-setter`
carried the whole diagnosis.

### !! EVERY MARK IS `taken in` OR IT IS NOT -- AND `stet` IS NEITHER OF THOSE

Roy, 2026-08-24: *"Marks also compose so multiple patch/add/drop/correct all have to be marked in
some way. Stet is one, I don't know the other."* -- then, correcting what `stet` is: *"my
understanding of stet is that it is the declaration that the copy chief emits when two editorial
roles couldn't agree. It emits on the one that it chose, or it overrules both, but the goal is
revise (currently re-review) gives the editorial roles two chances to figure out the compromise
with reasons."*

!! **SO `stet` SITS ONE LEVEL UP, AND THIS FILE SAID OTHERWISE FOR AN HOUR.** It was written here
as *the mark was proposed and the original stands* -- a per-mark refusal. **It is not a
disposition at all.** It is what the COPY CHIEF declares after the roles have failed to converge,
and what it names is **what stands**: the mark it chose, or neither.

!! **`stet` IS *LET THIS STAND*, AND THE POINTING IS THE WHOLE OF IT.** Roy, 2026-08-24:
*"stet -- let this stand. That is what I understood when it was proposed."* The copy chief points
at something and declares it stands; **what it points at may be the original or it may be one
role's mark**, and the declaration is the same either way. ! That is why *the original stands* was
too narrow: it is one of the two things `stet` can point at, not the meaning of the word.

| | who emits it | when | what it says |
| --- | --- | --- | --- |
| **`taken in`** | this piece, mechanically | every mark, every time | the mark was carried into the text |
| **`stet`** | the **copy chief** | only where two roles could not agree | **let THIS stand** -- the mark it chose, or neither |

!! **AND THE TWO CHANCES ARE ALREADY RULED AND ALREADY BUILT.**
`references/re-review.md:128`, ruled 2026-08-17: *"AT MOST TWO re-review rounds, and then the
APPLIER judges ... A paragraph may go back twice. If it is still split after the second, stage 5
rules on it."* ! **What is missing is not the bound -- it is the NAME for what stage 5 then
emits.** That file says only *"stage 5 rules on it"*, and a ruling nothing names is a ruling
nothing can record, re-read, or refuse to raise again.

! **AND THE TRADE ALREADY NAMES THE TWO CHANCES.** `docs/vocabulary.md:63` carries **revise** --
*the second proof, pulled after the marked corrections have been set* -- against *"a re-review
round"*. First revise, second revise, then it goes to press: **Roy's two chances ARE the trade's
practice**, and the tree still says `re-review` in **13 files, 41 times** -- measured 2026-08-24,
of which **7 files and 23 occurrences are shipped** under `plugins/`. That split is T11.

**And the per-mark question turned out smaller than it looked.** After composition a mark is in
the text or it is not; **a contradiction is not a third state**, because it never reaches this
piece -- it goes to revise, twice, and comes back as a `stet`.

!! **RULED 2026-08-24: THE OTHER ONE IS `taken in`.** *Taking in corrections* is the compositor's
own phrase for making the marked changes on a proof, and ordinary English *take in* is to absorb
-- Roy, ratifying it: *"also fits the common use of the word."* It reads correctly with or without
the trade, and a two-word phrase cannot drift into general use the way `set` did.

! **`settled` WAS PROPOSED AND MEASURED OUT**, on Roy's own second criterion -- *"close to set but
not confused with set"*, and *"not overly generic like set."* MEASURED the same day: `settle`
appears **94 times across 19 shipped files and 35 more in `docs/`**, and two are collisions with
the neighbour -- `re-review.md:139` already writes *"a paragraph stage 5 settled"*, which is the
`stet` case, and `SKILL.md:68` lists `query` as **unsettled**. **`taken in` returns zero.**
`decision-log.md Vocabulary: #12`.

!! **AND [`no-mark-for-let-it-stand`](no-mark-for-let-it-stand.md) IS BUILT ON THE OTHER READING.**
Its T3 adds `stet` to `record.py`'s `VERDICTS` as an eighth, and its T13-T16 ask what each ROLE's
own `stet` asserts. **A role cannot emit one**: `stet` presupposes two roles that disagreed and a
copy chief that ruled, so no single role is ever in a position to file it. ! That file is
`agents`' and `decision-needed`; the correction is recorded here and in
`decision-log.md`, not written into its boxes from this lane.

## Tasks

- [?] T1 | T1 -- * Decide the artifact's name and the module that makes it. Verify: the
      name is in `docs/vocabulary.md` and the file is renamed to it.
- [ ] T2 | T2 -- Compose the marks on one address in the synthesis order.
      Verify: two non-conflicting marks on one paragraph produce one text
      carrying both.
- [ ] T3 | T3 -- Send a contradiction to revise instead of composing it. Verify:
      `correct` against `patch` on one sentence goes back to its filers and
      composes nothing.
- [ ] T4 | T4 -- Carry the marks each paragraph answers. Verify: a mark that
      reaches the collator and is named by no paragraph refuses the run.
- [ ] T5 | T5 -- Emit what the galley already takes. Verify: the output is
      `{address: text}` and the galley consumes it unmodified.
- [ ] T6 | T6 -- Correct `galley.py:173`, which claims `--edits` is
      machine-written. Verify: the sentence describes what exists.
- [ ] T7 | T7 -- `agents` -- correct `SKILL.md:925`, *nothing between stage 5
      and the galley converts*. Verify: it names the piece that does.
- [x] T8 | FINISHED | unknown | T8 -- NAMED 2026-08-24: a mark carried into the
      text is `taken in`. In `docs/vocabulary.md` and `decision-log.md
      Vocabulary: #12`.
- [ ] T9 | T9 -- Record `taken in` or not, for every mark on the artifact.
      Verify: a mark that is neither taken in nor covered by a `stet` refuses
      the run.
- [ ] T10 | T10 -- Carry a `stet` onto the artifact. Verify: a paragraph the
      copy chief ruled says so and names the marks that ruling settled.
- [ ] T11 | T11 -- Rename `re-review` to `revise` in the 7 shipped files, 23
      sites. Verify: `grep -rc re-review plugins/` returns nothing.
- [ ] T12 | The desk takes each page sha FROM THE BINDER the agents read and
      copies it onto that page schedule -- never from the file at docket-writing
      time, which would make proof_setter staleness check compare the file
      against itself
- [ ] T13 | Pin that with a test the desk fails if it recomputes: build a
      docket, change the file underneath, and assert the run REFUSES at verify

## Related

- [`nothing-runs-the-whole-chain`](nothing-runs-the-whole-chain.md) -- the chain this sits in;
  its T6 and T7 are the collation cases this piece consumes
- [`correct-against-patch-is-a-conflict-and-is-not-flagged`](correct-against-patch-is-a-conflict-and-is-not-flagged.md)
  -- the contradiction T3 must refuse, and the ruling on what the copy chief then does
- [`record-and-verdicts-disagree`](record-and-verdicts-disagree.md) -- two modules disagreeing
  about what a valid record is, one stage upstream of this hole
