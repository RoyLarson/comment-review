# Vocabulary -- what this system STOPPED saying

!! **STOP. IF YOU ARE CLAUDE, DO NOT READ ON -- ask whether you should.** This file is a record
of words this system no longer uses and of definitions that have since moved. Reading it puts
retired terms and superseded rulings into your context beside the live ones, where nothing tells
them apart. `docs/addressing.md` carries the same warning for the same reason.

!! **THE OFFICIAL DEFINITIONS ARE IN
`plugins/comment-review/skills/comment-review/references/vocabulary.toml`.** They reach an agent
by being EMITTED -- `scripts/vocabulary.py --reviewer <role>` -- and a file that uses a term
states no definition of its own. **Only definitions that have been RETIRED or MODIFIED are
here**, and `scripts/check_vocabulary.py` refuses a live term defined in both places.

## Retired -- do not bring these back

| word | what happened |
| --- | --- |
| `ANNOTATE` (stage 2) | -> **GATHER**, via `COLLATE`. Stage 2 adds no notes; it gathers every position in the file into one ordered tree. It also pointed at two stages -- `annotate.py` performs stage 3 |
| **line address** (`mod.py:1-24`) | -> **address**. True of ONE file state, and this tool edits prose. `addresser.line_address` read it and warned on every call, and was DELETED 2026-08-20 with nothing calling it -- see `docs/history.md` |
| `block` | -> **paragraph**. The register is EDITORIAL, and `block` was the last structural term borrowed from compilers. Its definition -- the interval between two lines of CODE -- is also untrue of a prose file |
| the four KINDS of a line of code | **deleted** -- *statement, expression, declaration, assignment*, shipped to every role and read by nothing. Neither exhaustive nor disjoint, and meaningless in the three data languages |
| **census index** | -> **address**. A position is correct only for the census it was written against; an `add` or a `drop` shifts every index below it |
| `prose tree`, `pCST` | -> **page**. Both named one file's classified lines. `pCST` -- *pseudo Concrete Syntax Tree* -- was borrowed because libcst made moving comments easy in Python, and this is not that. Roy, 2026-08-20: *"it never really fit."* Naming it for a syntax tree invited an apology for not being one |
| `angle` | -> **editorial role** in prose, **reviewer** in identifiers. Six senses, defined nowhere |
| `--angles`, `ANGLE FILES` | -> `--reviewers`, `REVIEWER FILES` |
| `sweep` | not a term. Stage 7b is **WRITE** |
| `reanchor` | -> **`move`**. A relocation is ONE judgment; the destination is payload |
| `HOME` | -> **owner**. It named the same site under a second stem |
| `jurisdiction` | -> **remit**. Judicial on an editorial system |
| `signature` (the CODE CHECK's) | -> **fingerprint**. `signature` means a function's, only |
| `residue` (the string) | -> **stripped**. The prose check keeps the word |
| `owner` (the census field) | -> **anchor**. It is a position, not a judgement |
| `level` | removed ENTIRELY. It gated which verdicts a reviewer could emit and had no provenance. Every verdict is available on every run |
| `FORMATTING` | -> **`move`** to the line above. Never declared in the vocabulary, the brief or the gate, so emitting it would have failed the run |
| `marks` (the census's) | -> **annotations**, including the JSON key |
| `walk` | an editor READS a manuscript and CHECKS a list. `ast.walk` is untouched |
| `detector` | the word is **annotation** |
| `gap` (the module-surface sense) | -> **omission**, which pairs with **obituary**: one is in the code and absent from the prose, the other the reverse |
| `statement` (of prose) | prose units are **sentence** and **clause**. The word names CODE |
| `acquittal list` | **deleted.** It matched a prose SHAPE while every role's `clean` is a truth assertion at that role's scope, so the two disagreed |
| `suppression list` | **deleted.** No provenance, and it suppressed nothing |
| `NOISE_FLOOR` / SUPPRESSED | **deleted** from `referrers.py`. Nothing gets suppressed |
| `CLEAN` range line | **deleted.** Every paragraph is a RECORD now, `clean` included -- a range covered many in one line and cited nothing |
| `assessability gate` | deleted -- used once, stated nowhere, and the idea was already stated without it |
| `acquittal rate` | deleted -- a measured quantity whose denominator no site stated |
| `worktree` | git's word, not this system's. It had been cited as a REASON in six shipped rules, which was a fact about the eval rig |
| `CAP` in the packet | removed -- reviewers are not given a cap |
| `EDIT` (stage 5) | -> **APPLY**. Stage 7b is **WRITE**; `references/apply.md` is `write.md` |
| `folio` | -> **cue**. A folio numbers a LEAF or a PAGE; the `@` half of an address names a position WITHIN a page, so `b3` was never any folio. ! The error shipped as a DEFINITION -- *"a leaf's number in publishing, which is what it is here"* -- and reviewers were given it |
| `foliator.py`, `foliate()`, `Foliation` | -> **`addresser.py`**, **`cue()`**, **`Cues`**. The module supplies both halves of an address and the whole take-apart; `Cues` holds cues, not addresses. See `docs/decision-log.md` Addressing: #6 |
| `leaf`, `leaves` (of a page or a place) | **deleted** in that sense. One sheet carries TWO pages, so it was neither the page nor the cue, and a file has no verso. ! Two shipped definitions disagreed -- one said paragraphs run DOWN a leaf, one said a leaf IS a place. ! The IMPORT-GRAPH sense is a different word and is live -- see the polysemy rule below |

## Held in reserve -- publishing's word for something we already have

!! **RECORDED SO IT CAN BE FOUND LATER, NOT AS WORK.** Roy, 2026-08-21: *"just in case we start
having trouble then I can tell you to find the word when I remember that this was a problem."*
Each row is a real term of the trade that names something this system already does under another
name. **None is adopted, and none is a defect today.**

| publishing's word | what it names there | ours, and why it stands |
| --- | --- | --- |
| **cast off**, **copyfitting** | estimating how much space copy will take, and cutting it to fit the measure | **compact** (stage 6), a computing word. The stage does ONE job and nothing strains, so the swap buys register and no structure |
| **revise** | the second proof, pulled after the marked corrections have been set | a **re-review round** (`references/re-review.md`). One word, no missing part |
| **dead copy** | the original manuscript kept beside the proof, so the setting can be checked against it | **unnamed.** It is `page.text`, which `compositor.identity` compares its output against -- we have the object and use it; only the name is absent |

!! **THE TEST FOR TAKING ONE IS A CATEGORY DOING TWO JOBS -- NOT REGISTER.** That is what
separates these from `matter`/`f`, `leading`/`d` and `stet`, where a part of the page had nowhere
to live and the missing word arrived with the rule attached. ! **A rename is not free**: `clean`
is stated in twelve files, so correcting one word there is a scoped piece of work rather than an
edit. Renaming something that already covers its job spends that for nothing.

! **So the row to act on is the one you reach while stuck** -- when a thing has to belong to
something and the fit is bad. `CLAUDE.md` carries the method under *"it supplies categories, not
only names"*.

## Bringing the marks together -- the words, and what each one would name

!! **RECORDED FOR REFERENCE, NOT ADOPTED.** Raised by Roy, 2026-08-22, on the `verdicts.py`
misnomer: *"Who in publishing brings together all of the different marks and joins them together.
I think that is the editor actually."* The trade splits that sentence into three things, and this
system has a different problem with each.

| publishing's word | what it names there | ours |
| --- | --- | --- |
| **collating** | transferring every hand's marks onto ONE proof. Where two marks conflict, both go down and the conflict is left visible. It decides nothing | `verdicts.py`, which the shipped tree calls **the join** at 43 sites and which rules on nothing by design. `join` is a database word |
| **master proof** | the single copy every mark has been collated onto, and the one the house then works from | **unnamed.** It is what `verdicts.py` prints |
| **editor** | who reads the master proof and decides what stands | **the COPY CHIEF**, ruled 2026-08-23. Stage 5 APPLY, performed by the task agent today and getting an agent file of its own |

! **THE THREE ARE NOT ONE JOB, WHICH IS WHY ONE WORD WOULD NOT FIT.** Collating is mechanical and
answerable by a program; ruling is not. `verdicts.py` checks citations, reports contradictions and
names coverage gaps, and hands every conflict up -- so whatever it is called, it is not the editor.

!! **BOTH CANDIDATE WORDS WERE ALREADY SPOKEN FOR, WHICH IS WHY A RULING WAS NEEDED FIRST:**

- **`collate` is FREE.** Stage 2 was `COLLATE` and is **GATHER** since 2026-08-23, because what
  it does is find every file in scope and put a page for each in the binder -- gathering is the
  binder's own word for collecting sheets into sequence. ! So `collate` is available for its
  trade meaning, transferring every hand's marks onto one proof.
- **`editorial role` is one of the four reviewers.** Calling the joiner `editor` puts two
  different jobs one syllable apart. In the trade the four are the hands that MARK -- a copy
  editor, a proofreader -- and only one hand rules.

!! **RULED 2026-08-23: THE ONE WHO RULES IS THE `copy chief`.** Roy: *"copy chief works. We will
want to have a specific agent file for that separate from the task agent."* In the trade the copy
chief rules over the copy editors' marks -- one level above the four hands, which is exactly the
relation here -- so it names the job without landing a syllable from `editorial role`.

!! **AND THE RULING CARRIES A SHAPE, NOT ONLY A WORD.** The copy chief becomes **its own agent
file**, separate from the task agent. Today stage 5 APPLY is the task agent deciding, which is
why the row above read *"unnamed, and there is no module"* -- the job had no artifact, so nothing
could be given to it, told to it, or checked of it. ! This is the same finding
[`TODO/stage-5-is-the-only-stage-with-no-independent-reader.md`](../TODO/stage-5-is-the-only-stage-with-no-independent-reader.md)
records from the other direction.

! **Do not add `copy chief` to `vocabulary.toml` until that agent file exists** -- the drift check
refuses a term no role uses, and the rule two sections down applies to a term arriving as much as
to one leaving.

! Tracked in [`TODO/verdicts-is-the-join.md`](../TODO/verdicts-is-the-join.md).

## What becomes of a mark -- `taken in`, and `stet`

**Two words, and they answer different questions.** Ruled 2026-08-24, and both are ADOPTED rather
than held in reserve.

| the word | what it names | who says it |
| --- | --- | --- |
| **`taken in`** | the mark was carried into the text. *Taking in corrections* is the compositor's own phrase for making the marked changes on a proof | the piece that composes, mechanically, about every mark |
| **`stet`** | *let this stand.* Emitted where two roles could not agree, and it points at what stands -- the mark it chose, or neither | the **copy chief**, and no one else |

!! **A ROLE CANNOT EMIT A `stet`.** It presupposes two roles that disagreed and a copy chief that
ruled, so no single hand is ever in a position to file one. Roy, 2026-08-24: *"it is the
declaration that the copy chief emits when two editorial roles couldn't agree. It emits on the
one that it chose, or it overrules both."*

! **`the original stands` IS TOO NARROW A GLOSS.** Roy: *"stet -- let this stand."* What it points
at may be the original OR one role's mark; the pointing is the whole of it, and the original is
one of the two things it can point at.

!! **`settled` WAS PROPOSED FOR `taken in` AND MEASURED OUT.** Roy, 2026-08-24: *"close to set but
not confused with set"*, and *"not overly generic like set"* -- the shape is right and the word
fails the second test. MEASURED the same day: `settle` appears **94 times across 19 shipped files
and 35 more in `docs/`**. ! Two of those are collisions with the neighbour: `re-review.md:139`
already writes *"a paragraph stage 5 **settled**"*, which is the `stet` case, and `SKILL.md:68`
lists `query` as **unsettled**, an axis about whether a QUESTION is open rather than whether a
mark reached the text. **`taken in` returns zero occurrences.**

! **And it reads without the trade.** Roy: *"also fits the common use of the word"* -- ordinary
English *take in* is to absorb or incorporate, so a reader who does not know a compositor's
marginal marks still reads it correctly. ! A two-word phrase also cannot drift into general use
the way `set` did.

! Tracked in [`TODO/nothing-makes-the-fair-copy.md`](../TODO/nothing-makes-the-fair-copy.md), and
`stet`'s own build is [`TODO/no-mark-for-let-it-stand.md`](../TODO/no-mark-for-let-it-stand.md) --
which is written on the reading this ruling corrects.

## ownership -- settled, and deliberately not emitted

**The relation: which anchor best justifies holding a comment.** `anchor` is the code position,
`owner` is the anchor that wins it, and **ownership** is the relation between them.

It appears nowhere in the shipped tree except as the root of a role's name, and is kept so the
word cannot return without a ruling behind it.

! **Do not add it to `vocabulary.toml`.** That file holds what agents are GIVEN, and the drift
check refuses a term no role uses. Adding it to tidy the numbers is writing to the check.

## Rules about the words themselves

- **The metaphor is EDITORIAL.** Editorial roles read a manuscript and write editorial marks;
  a PROOFREADER reads the finished proof and says whether it deserves more marks. A new term
  comes from publishing, and is checked against the register **before** it is proposed.
  `CLAUDE.md` carries this rule and the reason.
- **A definition lives in exactly one place and reaches an agent by being EMITTED.** A file that
  uses a term states no definition of its own.
- **A definition states only what is necessary** -- not the measurement that produced it, not the
  date, not what it replaced. Every word in `vocabulary.toml` is shipped into a prompt and
  charged for; this table is where a superseded term stays legible.
- **Polysemy is allowed when it is DECLARED and the contexts do not overlap** -- `opener` (a
  comment delimiter, and a record's `--- RECORD`), `annotations` (the census's, and
  `from __future__`), `node` (a page's node, and an AST node), **`leaf`** (a module that imports
  no sibling, and -- retired -- a sheet of paper).
  - !! **`leaf` IS THE ONE WHERE ONE SENSE WAS RETIRED AND THE OTHER KEPT.** Ruled by Roy,
    2026-08-23. The PAGE sense is gone; the IMPORT-GRAPH sense is his own term from 2026-08-22 --
    *"Constants.py is the ultimate leaf and no other module may reimport from another module"* --
    and it is standard in that domain. ! The two operate on different things, which is the test
    this rule states, and `leaves` is an ordinary English verb besides: measured 2026-08-23,
    retiring the word fired on 15 sentences reading *"leaves it unaccounted for"*.
  - ! **It is confined to `.py` and is checked there**: 10 uses, none in `agents/`, `SKILL.md` or
    `references/`, so nothing an agent is handed carries the ambiguity.
  - !! **`settle` IS THE ONE WHERE THE CONTEXTS DO OVERLAP, AND IT IS OPEN.** Raised by Roy the
    moment `taken in` was ruled, 2026-08-24: *"now we have a polysemy of the word settled and
    that has to get resolved."* Two senses, and they are not confined:

    | sense | what it is about | where |
    | --- | --- | --- |
    | **a CLAIM settled by evidence** | `query` names *what would settle* it; an unsettled claim is an open one | SHIPPED -- `record.py`'s `needs_settles`, the brief's `settles` key, `SKILL.md:68`'s `unsettled` |
    | **a DECISION settled by a ruling** | a term, a definition or a design that is agreed and not reopened | this file, `CLAUDE.md`, `docs/` prose, and 54 shipped uses |

    ! **MEASURED 2026-08-24: 94 uses across 19 shipped files, 35 more in `docs/`.** Of the
    shipped, 40 are the claim sense (`settles` 32, `needs_settles` 6, `unsettled` 2). **43 are
    in what an agent is HANDED** -- `SKILL.md` 15, `reviewer-brief.md` 16, the four role files 7,
    `compact`/`write`/`re-review` 5 -- so this fails the confinement test `leaf` passes.

    ! **AND A THIRD USE IS ALREADY RETIRED BY `stet`**: `re-review.md:139` writes *"a paragraph
    stage 5 settled"*, which is the copy chief's ruling and now has its own word.

- **`clean` is reserved.** It is one of the seven verdicts and is never a loose adjective for
  code, prose, a grep result or a run.
