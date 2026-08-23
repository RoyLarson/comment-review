# `ownership-context` is read FIRST, and nothing in the run makes that true

```
Status:   open
Progress: 3 of 10 tasks done
Owner:    agents
Requires-Roy: false
Raised:   2026-08-16 (Roy: "Does this require a 4a, b, c -- 4a the ownership run,
          b the resolution and update to the pieces made by the reviewer so the
          other contexts can have a correct run, c the other reviewers run?")
Unblocked: 2026-08-19 — Requires-Roy cleared: its own Owner field reads 'serialisation
           and 4b ruled 2026-08-17; the rest is build', and Roy re-stated it 2026-08-19:
           ownership-context is the 1 required role, the other 3 optional and only after
           it has had its say. The flag means a DECISION is owed; work still remaining
           is what the unchecked boxes already say.
```

## Objective

**SKILL.md says `ownership-context` is read FIRST because a claim attached to the wrong scope
is measured against the wrong code and `correct`ed into a falsehood. Three mechanisms could
deliver that, and none did.**

| mechanism | what it does today |
| --- | --- |
| dispatch order | **parallel.** *"Dispatch all four in ONE message so they run concurrently."* Ownership does not run first in time |
| synthesis order | in-code `move` was applied **LAST**, after `correct` and `patch` -- the text was corrected at the old anchor, then relocated |
| the join | `contradictions()` keyed on `drop` alone, so `move` + `correct` passed in silence |

! **Two of the three are fixed; the first is not.** Roy ruled *"moves first"* -- the synthesis
order now settles placement at step 2, before `correct` at step 3 -- and ruled the join should
flag `move` against `correct`/`patch`, which it now does. **Both act AFTER the reviewers have
read.** They catch a claim measured at the wrong anchor; they do not stop it being measured
there.

! **What is left is the reading itself.** All four reviewers read the same census concurrently,
so `block-context` measures a misplaced claim against whatever code it sits with, and spends a
verdict on it, before anything knows the placement is wrong. The join now sends that block back
-- which is a round trip, not a prevention.

## !! WHY 4a/b/c EXISTS AT ALL, stated 2026-08-18 with the consequences known

Roy: this role is the reason for the split. The two rulings that make it concrete arrived two
days after the shape was sketched, and the role file now carries both.

**IT RULES ON TRUTH, and the truth is PRIOR.** Roy, 2026-08-18: it settles *"is this statement
specifically about this piece of code"* and *"is this statement about any specific piece of
code or documentation in this project"*. Both are propositions that can be false and are
settled by evidence. What it does not rule on is the truth of what the sentence ASSERTS -- the
count, the bound, the worked example -- which is the other three's, each at its own scope.
**Yours is the truth of the ANCHORING; theirs is the truth of the ASSERTION.**

! The role file had understated this as *"You do not rule on whether the claim is TRUE ... You
rule on whether truth is assessable here at all."* Assessability IS a truth ruling. Corrected
in place, together with the frontmatter a dispatcher reads.

**AND IT IS NEVER DROPPED.** Ruled 2026-08-18: a run may omit `block-context`,
`function-context` or `module-context` and still be a review; omitting this one leaves every
remaining verdict resting on an assumption nobody made. So the legal sets are
`{ownership-context}` plus any subset of the other three -- which is the same asymmetry 4a/b/c
encodes in TIME, now stated as a property of the ROLE.

! **The two are the same fact seen from two sides.** 4a/b/c exists because the other three
cannot correctly read until this one has answered; the never-dropped rule exists because they
cannot correctly read if it never answers at all. A run that keeps all four but reads them
concurrently has the ordering defect this file is about; a run that drops this one has the
population defect. Both end with a claim measured against code it does not belong to.

! **The scope widened with the restatement, and that is worth flagging rather than burying.**
The file asked whether a block would be truthy *"in the right place"* with the surrounding text
file-scoped -- *"equally useful anywhere in the FILE"*. Roy's second proposition is
project-wide and names documentation, so the role file now says the right place is anywhere in
the PROJECT. That changes a verdict: prose about nothing in the project is a `drop`, prose
about something elsewhere in it is a `move`, and reaching for `drop` because the subject is not
in THIS file is how a true sentence gets deleted.

## The shape Roy sketched

```
4a  ownership-context runs alone
4b  its placement verdicts are resolved, and the census updated
4c  the other three run against corrected placement
```

### !! SUPERSEDED the same day -- 4b PROPOSES, it does not apply

**Roy backed out of applying edits at all:** *"move is a drop/add from the place that the
comment came from. The only safe automatic verdict is add. The others can cut it back out. I
think somehow we will have to have a prosed-pCST for this or something. or a Tag that states -
proposed."*

!! **A `move` is ONE VERDICT and TWO EDITS, and the earlier ruling priced the verdict.**
`SKILL.md`'s *"a relocation is ONE judgment, and the DESTINATION carries the rest"* is about the
RULING being atomic. Applying it is a delete at the origin and an insert at the destination, and
**the delete half forecloses 4c exactly as a plain `drop` does** -- 4c rules on the prose at its
new owner and can never say it belonged where it was, or that it is false and belongs nowhere.
The reasoning below that called `move` safe is wrong for that reason, and is kept so the error
is legible.

**The rule that replaces it:**

> Any verdict whose application REMOVES something forecloses 4c. `add` is the only purely
> additive verdict, so it is the only one that could be applied automatically -- and a wrong
> `add` is recoverable, because 4c can find the added text false or off-subject and stage 5
> drops it. Nothing was destroyed to learn that.

**So 4b TAGS every ownership verdict as PROPOSED and applies none of them**, `add` included --
uniform, because once the tag exists `add` needs no special case. 4c reads the tree as it IS
plus what is proposed on it, and may contradict the proposal. The objective is still met: the
tag carries the RESOLVED OWNER, so 4c measures the claim against the right code without the
placement being settled.

! **Everything below about POSITION still holds and is why the tag works**: no index moves, no
address moves, one census. What changed is that the owner is now proposed rather than applied.

### Superseded ruling, kept: 4b edits the pCST, not the files

Roy: *"takes the pCST adds- moves - deletes where the ownership context states and then passes
that edited pCST to the 3 editorial reviewers."*

!! **The TREE is edited; nothing on disk is.** *"Nothing is on disk yet"* holds unchanged
through 7b -- 4b rewrites the census, not the source. The rejected alternative was to edit the
working TEXT, which rebuilds the census from shifted line numbers and makes a block index mean
something different at 4a and 4c: ownership's findings would be addressed against one census
and the other three's against another, while `verdicts.py` takes one `--census` and
`contradictions()` keys on the index.

! **An `add` applied here is a capability gain, not just a placement fix.** The proposed text
enters the tree, so 4c FACT-CHECKS prose that does not exist yet -- something no arrangement of
this pipeline has offered before, since an `add`'s text previously reached stage 5 unread by any
role but the one that wrote it.

### !! Applying a `drop` at 4b forecloses the other three

**A `move` leaves the prose in the tree and 4c rules on it at the new anchor. A `drop` removes
the block, so 4c never sees that sentence and cannot contradict the ruling.** Ownership's `drop`
becomes unappealable by construction.

That is the collision `verdicts.py` already refuses to merge -- *"one role says the sentence
should not exist and another says it should exist and be fixed. Nothing composes those"* -- and
it routes to re-review. Deleting the block at 4b means the check stays in the code and goes dark
for the one role that runs first. ! It is the role whose remit is PLACEMENT: `drop` from it
means *not load-bearing at this site*, which is not a finding about whether the sentence is
TRUE, and truth is another role's question.

**RULED 2026-08-17 (Roy: "Agreed"): 4b applies moves and adds; a `drop` is marked PROPOSED and
the block stays visible to 4c.** The drop is then resolved at stage 5, where all four verdicts
meet and the contradiction check already lives. It costs nothing -- a drop reaches disk at 7b
either way.

### What 4b may edit: OWNERSHIP, never POSITION

**Derived from the brief, not chosen.** A reviewer must transcribe *"the block's text exactly as
the file reads it now"*, and `address_problem` checks that transcription and the
`path:start-end` against the census. So a census re-laid-out at PREDICTED post-move positions
would disagree with the file on every block 4c reads, and every 4c record would fail the address
check. **4b therefore edits what a block BELONGS to, not where it sits.**

| verdict | what 4b does to the node | index | address |
| --- | --- | --- | --- |
| `move` | its resolved owner/anchor changes | same | **unchanged** -- the text has not moved |
| `add` | the cited empty INTERVAL gains the proposed text | same | unchanged -- the interval was already numbered |
| `drop` | flagged PROPOSED, node stays | same | unchanged |

!! **Nothing renumbers, so there is ONE census for the whole run.** An `add` fills a node that
already existed rather than inserting one, which is the reason the census numbers empty
intervals at all. `verdicts.py` keeps taking a single `--census`, ownership's addresses still
resolve at stage 5, and `contradictions()` keeps keying on an index that means the same thing in
both passes. ! The alternative -- two censuses and an index map -- was avoided by this
constraint, not by a preference.

! **A `move`'s owner may be in ANOTHER FILE, and that still works**: the node keeps its own
address and carries the destination, so 4c knows which code to measure the claim against. A
`move` OUT of the code says the block is leaving, which is all 4c needs.

! **What it costs, now that the ruling above has settled what 4b touches:**

- Stage 4 stops being one parallel dispatch. 4a and 4c are serial, so the run's wall-clock
  grows by one agent round trip. **This is the whole remaining cost.**
- A `move` at 4a and a `drop` at 4c on the same block still collide, so the join's
  contradiction check stays either way.

! **One cost listed here before the ruling is GONE, and it was the largest.** It read: *"4b
relocates prose before the author has ruled on anything ... the other three review prose at
positions the author has not approved."* That was true of the rejected reading, where 4b edits
the working TEXT. Under the ruling 4b changes what a block BELONGS to and never where it sits,
so no prose is relocated at 4b and 4c reads every block at the position the file actually has.
**Nothing is proposed to the author that the author has not seen, and nothing moves before 7b.**

## What the four roles are, as editorial desks

Reconstructed 2026-08-17 after a compaction dropped it. Roy confirmed it matched what had been
there, except that `ownership-context`'s desk had never been named -- the other three had one.

| role | the desk | what that desk does |
| --- | --- | --- |
| `module-context` | developmental editor | reads the whole work and asks whether it argues ONE thing |
| `function-context` | line editor | section level -- does this section deliver what its heading announces |
| `block-context` | fact-checker | takes each claim to a source and resolves it; owns nothing about placement |
| `ownership-context` | **notes editor** | checks every note hangs off the sentence it is actually about |

! **The slot that stayed empty is the one asking a different question.** Three of the four ask
*is this text right* -- right as argument, right as section, right as fact -- and each maps onto
a desk that names itself. `ownership-context` asks *is this text HERE*. Placement, not content.

`SKILL.md` spends three further desks elsewhere and none of them collides: copy editor is stage
5, condenser is stage 6, proofreader is stage 8.

### What that argued for, and what was ruled

!! **A house places the notes BEFORE the checker works the copy, and the order is serial.** It
is the same failure this file's objective states -- a checker handed a misfiled note verifies it
against the wrong passage and stamps it true -- reached by the trade long before this system
measured it. **The trade's answer was 4a/4b/4c**, not a parallel read with a later ruling, and
that is what was ruled above.

! **That is an argument, not a measurement, and it did not settle the costs.** It priced
nothing; it removed one READING of the alternative. *"The other three may spend a verdict on a
misplaced block"* is not a cheaper design trading accuracy for speed -- it is the arrangement
the desk exists to prevent. The wall-clock round trip was, and remains, a real cost.

### One desk is a script, and one is absent

`referrers.py` is the INDEX -- which files name the files under review. It is the only editorial
function here automated rather than staffed, and it is currently over-matching: a token like
`run` or `main` returns most of the repo. **An index whose entries point at every page is not an
index**, which is the indexer's own rule and the reason
[`referrers-matches-on-any-public-name`](referrers-matches-on-any-public-name-and-surfaces-the-whole-repo.md)
already prescribes dropping a token by its MEASURED match count rather than by a wordlist.

Permissions has no counterpart, and needs none -- nobody clears rights on a comment.

! **What would falsify the mapping is a desk with no role or a role with no desk.** As of
2026-08-17 there is one of each and both are accounted for above, so the fit is reported as
four-for-four with one function automated. Re-check it when a fifth role is proposed.

## Tasks

- [x] **DONE 2026-08-18 -- the role file states its remit at full width.** Two propositions
      named, anchoring-truth distinguished from assertion-truth, the never-dropped rule stated,
      and the right place widened from the file to the project. The frontmatter `description`
      carries it too, because that is what a dispatcher reads. ! The frontmatter gate earned
      its place on the way in: the first draft put a colon-space in `description`, which ends a
      plain YAML scalar, and `claude plugin validate` plus `tests/test_frontmatter.py` both
      refused it before it shipped.

- [x] * **RULED 2026-08-17: stage 4 SERIALISES.** Roy, on the desk mapping above: *"I guess
      that means we go back to 4A - ownership runs 4B - marks are applied 4C - the other
      contexts are run."* The rejected alternative was to let the other three spend a verdict on
      a misplaced block and have the widened join catch it.

- [x] * **RULED 2026-08-17, then SUPERSEDED the same day: 4b PROPOSES, it does not apply.**
      The first ruling was *"takes the pCST adds- moves - deletes where the ownership context
      states"*, with `drop` alone held back. It was withdrawn once `move` was seen to decompose
      into a drop and an add: **every removing verdict forecloses 4c, and `add` is the only
      purely additive one.** 4b now tags every ownership verdict PROPOSED and applies none.
      Both rulings are written out above, the superseded one kept legible.

- [ ] **The pCST needs to carry a PROPOSAL.** A node today holds what the file says; it needs
      to also hold what a role proposes for it -- the resolved owner, proposed text, or a
      proposed removal -- without either being applied. ! **Nothing in `census.py` has a place
      to put this**, and it is a second SUBJECT, so it is a second module rather than a flag on
      the census: `module-context` asks of any module that it announce one thing.

- [ ] **Decide what a PROPOSED tag carries, since 4c must act on it.** At minimum the verdict,
      the resolved owner (which may be another file, or out of the code), and the proposing
      role. ! 4c has to be able to MEASURE against the proposed owner while still reading the
      text where it sits -- that is the entire point of the serialisation, and a tag that only
      says "something is proposed here" does not deliver it.

- [ ] **Gate 4b the way 7b is gated.** `prove_unchanged.py` exists because an edit that claims
      to touch only prose has to be checked. The same shape applies here: **census B may differ
      from census A only at the indices `ownership-context`'s report named**, and only in the
      fields its verdict licenses. A 4b that quietly re-anchors a block nobody ruled on is the
      failure this whole file is about, one layer up.

- [ ] **Split stage 4 in `SKILL.md`, and say what 4b may touch.** ! *"Nothing is on disk yet"*
      is stated at stage 6 and must stay true at 4b -- under this ruling it is, and the file
      should say so rather than leave a reader to work it out.

- [ ] **`run_context.py`'s packet is written once per run and handed to four agents.** A
      4a/4c split needs either two packets or one that says which pass it is. ! 4c's packet
      names census B; 4a's names census A. That is the only field that differs, so one packet
      with a PASS line is likely enough -- but `--check` must then refuse a 4c packet pointing
      at census A.

- [ ] **Teach the join the three flags.** `verdicts.py` reads one census and must not treat a
      PROPOSED-drop node as ordinary prose, nor an `add`'s filled interval as a block 4c failed
      to account for. ! Coverage is the specific risk: an interval that gained text is now a
      block a reviewer owes a record for, and one nobody told 4c about is a coverage gap the run
      manufactured for itself.

- [ ] **Re-read `ownership-context`'s own line:** *"Your verdict settles which code every later
      reading measures the claim against."* Under the parallel design that was false -- there
      was no later reading, only a later ruling. **Under this ruling it is exactly true**, and
      it is the sentence the whole serialisation exists to make good on.
