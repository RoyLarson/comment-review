# Nothing turns the collated marks into the paragraph the galley writes

```
Status:   open
Progress: 0 of 11 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-24 (Roy: the galley only really needs this address gets this paragraph,
          and the system assumes verdicts and records are what it writes from)
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

### !! EVERY MARK GETS A DISPOSITION, AND `stet` IS NOT ONE OF THEM

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
| **disposition** | this piece, mechanically | every mark, every time | the mark is in the text, or it is not |
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

**So the per-mark question is still open, and it is smaller than it looked.** After composition a
mark is IN the text or it is NOT; a contradiction is not a third state because it does not reach
this piece at all -- it goes to revise, twice, and comes back as a `stet`.

!! **THE CANDIDATE FOR THE UNNAMED ONE IS `taken in`**, offered for ratification and not asserted:
*taking in corrections* is the compositor's own phrase for making the marked changes on a proof.
! Checked against the register first, per `CLAUDE.md`'s method: `set` is already the compositor's
word for putting a page into type, so it cannot carry this too.

!! **AND [`no-mark-for-let-it-stand`](no-mark-for-let-it-stand.md) IS BUILT ON THE OTHER READING.**
Its T3 adds `stet` to `record.py`'s `VERDICTS` as an eighth, and its T13-T16 ask what each ROLE's
own `stet` asserts. **A role cannot emit one**: `stet` presupposes two roles that disagreed and a
copy chief that ruled, so no single role is ever in a position to file it. ! That file is
`agents`' and `decision-needed`; the correction is recorded here and in
`decision-log.md`, not written into its boxes from this lane.

## Tasks

- [ ] T1 -- * Name the artifact and the module that makes it. Verify: the name is in
      `docs/vocabulary.md` and the file is renamed to it.
- [ ] T2 -- Compose the marks on one address in the synthesis order. Verify: two
      non-conflicting marks on one paragraph produce one text carrying both.
- [ ] T3 -- Send a contradiction to revise instead of composing it. Verify: `correct`
      against `patch` on one sentence goes back to its filers and composes nothing.
- [ ] T4 -- Carry the marks each paragraph answers. Verify: a mark that reaches the
      collator and is named by no paragraph refuses the run.
- [ ] T5 -- Emit what the galley already takes. Verify: the output is `{address: text}`
      and the galley consumes it unmodified.
- [ ] T6 -- Correct `galley.py:173`, which claims `--edits` is machine-written. Verify:
      the sentence describes what exists.
- [ ] T7 -- `agents` -- correct `SKILL.md:925`, *nothing between stage 5 and the galley
      converts*. Verify: it names the piece that does.
- [ ] T8 -- * Name the disposition of a mark that was carried into the text. Verify: the
      name is defined in `docs/vocabulary.md`.
- [ ] T9 -- Record a disposition for every mark on the artifact. Verify: a composed
      paragraph names each mark as carried or not, and a mark with neither refuses.
- [ ] T10 -- Carry a `stet` onto the artifact. Verify: a paragraph the copy chief ruled
      says so and names the marks that ruling settled.
- [ ] T11 -- Rename `re-review` to `revise` in the 7 shipped files, 23 sites. Verify:
      `grep -rc re-review plugins/` returns nothing.

## Related

- [`nothing-runs-the-whole-chain`](nothing-runs-the-whole-chain.md) -- the chain this sits in;
  its T6 and T7 are the collation cases this piece consumes
- [`correct-against-patch-is-a-conflict-and-is-not-flagged`](correct-against-patch-is-a-conflict-and-is-not-flagged.md)
  -- the contradiction T3 must refuse, and the ruling on what the copy chief then does
- [`record-and-verdicts-disagree`](record-and-verdicts-disagree.md) -- two modules disagreeing
  about what a valid record is, one stage upstream of this hole
