# Nothing turns the collated marks into the paragraph the galley writes

```
Status:   open
Progress: 0 of 9 tasks done
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

!! **RULED 2026-08-24: IT COMPOSES MECHANICALLY, AND ONLY A CONTRADICTION STOPS IT.** Roy:
*"multiple answers can be true, not just either this or that ... where things do not conflict and
come back clean that is probably a single transform from verdict in to something to be written."*
So the marks on one address are applied in the synthesis order `SKILL.md` already states --
`query`, then `move`/`drop`, then `correct`, then `patch`, then `add` -- and several true answers
compose without anyone choosing between them. **The copy chief writes text only where two marks
genuinely contradict.**

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
ruling to execute, it composes, and where it cannot, it refuses.

!! **THE NAME IS ROY'S AND IS NOT SETTLED -- T1.** The slug uses **fair copy**, the trade's term
for the clean corrected text written out for the compositor, as a working candidate ONLY. ! Per
`CLAUDE.md`'s method the name comes LAST: what the thing IS is above, and the trade's word for
that job is what gets ratified -- the way `compositor` was, in two words, after `page-setter`
carried the whole diagnosis.

### !! EVERY MARK GETS A DISPOSITION, AND ONLY ONE OF THE TWO HAS A NAME

Roy, 2026-08-24: *"Marks also compose so multiple patch/add/drop/correct all have to be marked in
some way. Stet is one, I don't know the other."*

**What the job IS:** after N marks are composed onto one paragraph, each mark has ended up in one
of two states, and the proof has to say which.

| the state | what happened | the word |
| --- | --- | --- |
| the mark is IN the text | the composition carried it | **UNNAMED -- T8** |
| the mark was proposed and the original stands | it was refused, and the refusal stays visible | **`stet`** |

! **A CONTRADICTION IS NOT A THIRD STATE.** Two marks that cannot both be true stop the run (T3)
and go back to their filers at stage 5b. Nothing is disposed of; the composition did not happen.

! **AND TWO MARKS PROPOSING THE SAME FIX ARE BOTH IN.** The text satisfies both, so both are
carried -- there is no *redundant* state, which is what makes the pair exhaustive.

!! **THE CANDIDATE FOR THE UNNAMED ONE IS `taken in`**, offered for ratification and not asserted:
*taking in corrections* is the compositor's own phrase for making the marked changes on a proof.
! It is put forward on `CLAUDE.md`'s method -- the JOB is stated above and the trade's word is
looked for afterwards -- and it is checked against the register first: `set` is already the
compositor's word for putting the page into type, so it cannot carry this too.

!! **AND THIS RAISES A QUESTION THAT FILE DOES NOT ASK.**
[`no-mark-for-let-it-stand`](no-mark-for-let-it-stand.md) treats `stet` as an eighth VERDICT --
its T13-T16 ask what each ROLE's own `stet` asserts. **Here `stet` is a DISPOSITION the composing
piece records about a mark it did not carry in.** ! A role proposes; it does not answer its own
proposal, and a disposition presupposes a mark to dispose of. **Whether those are one concept or
two is unsettled and is Roy's** -- T8 asks it, because the answer decides whether `stet` belongs
in `VERDICTS` at all or only on this artifact.

## Tasks

- [ ] T1 -- * Name the artifact and the module that makes it. Verify: the name is in
      `docs/vocabulary.md` and the file is renamed to it.
- [ ] T2 -- Compose the marks on one address in the synthesis order. Verify: two
      non-conflicting marks on one paragraph produce one text carrying both.
- [ ] T3 -- Refuse a contradiction instead of composing it. Verify: `correct` against
      `patch` on one sentence stops the run and names both marks.
- [ ] T4 -- Carry the marks each paragraph answers. Verify: a mark that reaches the
      collator and is named by no paragraph refuses the run.
- [ ] T5 -- Emit what the galley already takes. Verify: the output is `{address: text}`
      and the galley consumes it unmodified.
- [ ] T6 -- Correct `galley.py:173`, which claims `--edits` is machine-written. Verify:
      the sentence describes what exists.
- [ ] T7 -- `agents` -- correct `SKILL.md:925`, *nothing between stage 5 and the galley
      converts*. Verify: it names the piece that does.
- [ ] T8 -- * Name the disposition of a mark that was carried in, `stet` being the other,
      and rule whether `stet` is a verdict or only a disposition. Verify: in the log.
- [ ] T9 -- Record a disposition for every mark on the artifact. Verify: a composed
      paragraph names each mark as carried in or `stet`, and an unmarked one refuses.

## Related

- [`nothing-runs-the-whole-chain`](nothing-runs-the-whole-chain.md) -- the chain this sits in;
  its T6 and T7 are the collation cases this piece consumes
- [`correct-against-patch-is-a-conflict-and-is-not-flagged`](correct-against-patch-is-a-conflict-and-is-not-flagged.md)
  -- the contradiction T3 must refuse, and the ruling on what the copy chief then does
- [`record-and-verdicts-disagree`](record-and-verdicts-disagree.md) -- two modules disagreeing
  about what a valid record is, one stage upstream of this hole
