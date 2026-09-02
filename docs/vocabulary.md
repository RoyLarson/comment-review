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
| `join` (the NOUN) | -> **the collator**. A database word, and it carried FIVE referents at once -- see `decision-log.md Vocabulary: #19`. ! The VERB is live: `"".join(...)` is Python's own, and `.join(` is declared in `check_vocabulary.py` |
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
| `verdict` | -> **instruction**. Judicial on an editorial system, the same register error `jurisdiction` made before it became `remit`; and it named the same thing twice -- the object a role returns is a **mark**, its type is an **instruction**. See `decision-log.md Vocabulary: #17` |
| `mark` (the COMMAND, `flows/marks.py`, `Command.MARK`) | -> **`distribute`**, in `6187f71`. The command hands each role an EMPTY `edit_copy` and takes the filled one back; it produces no mark and rules on nothing. One stem named both a role's RULING and the machinery that circulates the forms, so `mark --seed` read as *make a mark* when it means *give out the blanks*. ! The NOUN IS LIVE and is defined in the shipped vocabulary -- this retires the command sense only, which is the shape `owner` (the census field) and `marks` (the census's) took before it |

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
| **collating** | transferring every hand's marks onto ONE proof. Where two marks conflict, both go down and the conflict is left visible. It decides nothing | `collator.py`, ruled 2026-08-23 (`decision-log.md Vocabulary: #11`) and still to be built. It rules on nothing by design |
| **master proof** | the single copy every mark has been collated onto, and the one the house then works from | **`master_proof`**, ruled 2026-08-29 (`decision-log.md Vocabulary: #28`). It is what `verdicts.py` printed before that module left for `prototype/` |
| **editor** | who reads the master proof and decides what stands | **the COPY CHIEF**, ruled 2026-08-23. Stage 5 APPLY, performed by the task agent today and getting an agent file of its own |

! **THE THREE ARE NOT ONE JOB, WHICH IS WHY ONE WORD WOULD NOT FIT.** Collating is mechanical and
answerable by a program; ruling is not. `verdicts.py` checks citations, reports contradictions and
names coverage gaps, and hands every conflict up -- so whatever it is called, it is not the editor.

!! **BOTH CANDIDATE WORDS WERE ALREADY SPOKEN FOR, WHICH IS WHY A RULING WAS NEEDED FIRST:**

- **`collate` is FREE.** Stage 2 was `COLLATE` and is **GATHER** since 2026-08-23, because what
  it does is find every file in scope and put a page for each in the binder. ! So `collate` is
  available for its trade meaning, transferring every hand's marks onto one proof.

  !! **AND IT HAS A SECOND TRADE MEANING THIS SYSTEM DOES NOT USE.** In bibliography, **collation**
  is comparing two states of one text to find where they differ -- the Hinman collator. That is
  exactly what `taken_in` does (original against the revise a role is holding), so the obvious word
  is the wrong one: `collator.py` keeps the copy-desk sense above, and the comparison sense is
  declared here rather than left to be rediscovered. **The undeclared meaning is the defect**, not
  the ambiguity, which is a fact about English older than this repo.
  `decision-log.md Vocabulary: #24`.

  !! **A BINDER HERE IS THE OBJECT, NOT THE TRADE.** Roy, 2026-08-24: *"The gatherer/census hands
  over the binder as in a 3-ring binder full of stuff not binder as the person who bounds
  books."* ! **He has used it that way throughout** -- *"a binder with sticky notes"*, and the
  annotations ruling earlier the same day put the sticky notes ON the pages IN it. ! This
  sentence had justified `GATHER` by calling gathering *"the binder's own word for collecting
  sheets into sequence"*, which is the BOOKBINDER's word -- two senses one clause apart, in the
  file that exists to keep senses apart. The justification is cut rather than repaired: what
  stage 2 does is put a page for each file in the binder, and that reads the same either way.
- **`distribute` is the BROADCAST half, and it pairs with `collate`.** Ruled 2026-08-30. Roy:
  *"the broadcasting part seems like distribute, the bringin back together seems like
  collate."* One round is two acts: `flows/distribute.py` hands each role its own `edit_copy`
  of the binder, `flows/collate.py` folds the filled copies back into one. It was
  `flows/marks.py`, named for the artifact it carried rather than the act it performs -- see
  the retired table, which keeps `mark` the NOUN live and retires only the command sense.

  !! **AND IT IS NOT TAKEN FROM PUBLISHING, WHICH IS THE POINT OF SAYING SO.** In letterpress,
  **distribution** is returning type to the case after a forme is printed -- breaking the
  setting DOWN, close to the opposite of handing copies out. So this is the plain English
  sense, chosen because it pairs with `collate`'s trade sense, and it is recorded here rather
  than in the table above precisely so nobody later reads a compositor's meaning into it.
  ! That table is *publishing's word for something we already have*; a row there would assert
  a provenance this term does not have.
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

## The middle has four containers -- `master_proof`, `edit_copy`, `sheet`, `mark`

**Ruled 2026-08-29** (`decision-log.md Vocabulary: #28`), naming the level the three-container
table below (`binder`/`docket`, `page`/`schedule`, row/`alteration`) has no equivalent for:

    master_proof
      +-- edit_copy        one per role; one per SHARD under fan-out
            +-- sheet      one per page
                  +-- mark one per place

| term | what it is |
| --- | --- |
| **`master_proof`** | holds every `edit_copy` of one stage. Never holds a `sheet` directly |
| **`edit_copy`** | one role's own copy of the pages it was handed -- `{role, read_from, sheets}` |
| **`sheet`** | one page inside an `edit_copy` -- `{path, sha, marks}` |
| **`mark`** | one role's ruling on one place -- a live term, defined in `vocabulary.toml` |

! **`binder` AND `docket` HAVE NO ROLES LEVEL.** Roy: *"They are separate containers, and
calling each of them as having a `master_proof` would be incorrect."* One binder goes out to
every role; in between there are N marked copies, one per role; one docket comes back.

!! **`sheet` CHANGES SENSE, AND THE OLD ONE WAS IN `flows/marks.py`'s OWN PROSE.** It named the
PER-ROLE container there -- *"Hand a role a sheet to fill"* -- while the same docstring also used
it correctly for the page-unit one sentence later: *"one sheet per page."* It now names only the
page-unit; the container is `edit_copy`.

! **`edit_copy` BECAUSE THE REGISTER IS THE COPY DESK, NOT THE BINDERY.** Roy: *"it isn't
overloaded with the other copy's it is adjacent and explicit."* This file already records that
the binder is *"a 3-ring binder full of stuff not binder as the person who bounds books"* (see
`binder`, below), and cut a justification reaching for the bookbinder's `gathering` -- so
`gathering` and `sheaf` were already out of register. `edit_copy` sits beside `copy` and `copy
desk`, the trade's own words, and `copy chief`, ruled above.

## `binder` -- the object, and the one sense it carries

**Ruled 2026-08-24.** Roy: *"The gatherer/census hands over the binder as in a 3-ring binder full
of stuff not binder as the person who bounds books."*

| | |
| --- | --- |
| **binder** | **the ARTIFACT the gatherer hands over** -- a folder of pages, with sticky notes on them |
| NOT | the bookbinder, the trade that sews and cases a book |

! **IT HAS BEEN USED THIS WAY THROUGHOUT** -- *"a binder with sticky notes"* -- and the
`annotation` ruling of the same day put those notes on the pages IN it, which only reads one way.

!! **THE SENSE MATTERS BECAUSE IT DECIDES WHAT THE THING IS FOR.** A bookbinder is a ROLE, and a
role does work; a binder is a CONTAINER, and a container is handed over. Read as the role, the
package looks like a stage that acts on pages -- and every question about it becomes *what does
the binder DO*. Read as the object, the question is the right one: **what is in it, and who is
handed it.** That is what the field cut of 2026-08-24 was answering.

! **NOTHING SHIPPED CARRIES THE WORD.** It appears in package docstrings and in this file, and in
no agent's prose -- so the sense was declared before an agent could learn the wrong one.

## The three containers, on both sides -- `binder`/`docket`, `page`/`schedule`, `paragraph`/`alteration`

**Ruled 2026-08-26.** Roy, naming the write side against the read side already built: *"like the
binder we have three levels of containers -- paragraph, page, binder. We have to be able to unwind
the alterations pretty close to the same way."*

| level | READ side | WRITE side |
| --- | --- | --- |
| one place | a **paragraph** -- the cue and what is there | an **alteration** -- the cue and what it becomes |
| one file | a **page** | a **schedule** |
| the whole | the **binder** | the **docket** |

!! **THIS TABLE SAID `row` IN THE READ SIDE'S TOP SLOT UNTIL 2026-08-31, ONE LINE BELOW THE
RULING THAT SAYS `paragraph`.** `decision-log.md Process: #68`. The quote above is unchanged
and always said paragraph; the table substituted the WIRE KEY -- a binder's JSON nests
`pages -> rows` -- and the header carried it too.

! **THE DOCUMENT WAS ALREADY FLAGGING IT.** `row` was the only term in that header not
backticked, and the only one of the six with no entry in the glossary below: it had never been
ruled, so nothing defined it.

!! **AND THE SENTENCE THAT STOOD HERE WAS NEVER AUTHORISED.** It read *"`row` IS NOT RETIRED,
because it was never a term -- it is the name of a key in a JSON file, and it stays that."*
Nobody ruled that, and it sat one paragraph above the record of Roy catching the same invention.
Roy, 2026-09-02: *"That was strictly not authorized and was supposed to be retired at the same
time as the paragraph name. There was no authorization to keep anything as a row."*

!! **`row` IS RETIRED, EVERYWHERE -- AS A TYPE, AS A JSON KEY, AND IN PROSE.**
`decision-log.md Vocabulary: #31`. The word for one place is **paragraph**.

! **NOTHING COULD HAVE CAUGHT IT.** `scripts/check_vocabulary.py`'s `RETIRED` dict is
hand-maintained and has no `row` entry, so no shipped file was ever tested for the word -- and
the struck sentence supplied a reason for the gap, which is what made the absence read as a
decision. The entry lands with the rename rather than before it, or the gate goes red across 24
files with no rename behind it: `TODO/row-was-never-retired.md`.

!! **AND IT HARDENED INTO A TYPE BEFORE IT WAS CAUGHT.** `BinderRow` and `BinderPage` were
added 2026-08-31 (`1d9314d`) and deleted the same day, after Roy: *"So you invented a term
'row' for something that is a Paragraph."* A `Binder` holds `Page`s or `RedactedPage`s, and
both hold `Paragraph`s.

| term | what it is |
| --- | --- |
| **alteration** | One change at one address: the new text for that place, or `null` to delete what is there. A change to type **already set**, which is what the word means in the trade -- so it is what the compositor acts on, never a proposal. |
| **schedule** | Every alteration for ONE page, carrying that page's path and the sha it was read at. A page holds the prose; a schedule holds what it becomes. |
| **docket** | The artifact the desk hands the write chain: every schedule, one per page. In print production a docket is the instruction paperwork that travels with a job, which is what this is. |

!! **`alteration` REPLACES `notations`, WHICH WAS A STAND-IN AND SAID SO.** Roy, 2026-08-25, when
it was named: *"It is a prototype or stand in for what might need to be built ... We need the
shape not the concrete implementation."* The word collided with `annotation` -- one letter apart,
in adjacent areas, both meaning marks attached to a paragraph -- which is
`TODO/notations-collides-with-annotations.md`. `decision-log.md Vocabulary: #14` supersedes the
ruling that named it.

!! **AND THE INSTINCT BEHIND `notations` WAS RIGHT, WHICH IS WHY IT COLLIDED.** Roy, 2026-08-26:
*"if I was writing between the lines with marks in red pen I think of those red marks as
notations."* The trade calls those **proof correction marks**, and this system already defines
`mark` as *"what stage 4 emits: one role's ruling on one paragraph."* So the word was reaching for
a thing the register had already named. ! What the desk produces from those marks is the thing
that needed a name, and a change to text already set is an **alteration**.

! **THE TRADE DETAIL THAT DECIDED THE LEVELS:** a proof correction is TWO marks -- a **textual
mark** in the line saying *here*, and a **marginal mark** saying *what*. The compositor works from
the margin. An alteration carries both halves in one row, the cue being the textual mark and the
text being the marginal one.

! **WHY THE SHA SITS ON THE SCHEDULE AND NOT THE DOCKET.** It is a fact about ONE file, read once,
and putting it there is what lets the write chain check that the page it is about to set is the
page the agents read -- without consulting the binder at all. Roy, 2026-08-25: *"besides reading
the sha and file path/name you should not be assuming any binder things make it this far."*

!! **NONE OF THE FOUR IS IN `references/vocabulary.toml`, AND THAT IS THE GATE WORKING.**
`check_vocabulary.check_complete` reports `NO RECIPIENT` for a definition no role is given, and
counts it a hole. The toml is what agents are HANDED; this file is the repo's own glossary. A term
crosses over the day a role's prose actually uses it -- which is the same reason `binder` has
never been in it.

## `library` -- every file in the project under review

**Ruled 2026-08-27, in two halves.** Roy: *"Strike `library` because that is not the word I would
have used at any point in time for the concept. I have consistently used the words package,
sub-package, module."* And then: *"I do think library has a useful definition in the system. It is
all of the files in the project being reviewed."*

| | |
| --- | --- |
| **library** | **every file in the project being reviewed.** The whole shelf |
| **binder** | the pages this run took OFF that shelf -- the scope the roles were given |
| this program's own parts | **package, sub-package, module.** Python's own words, always |

!! **SO THE LIBRARY IS THE POPULATION AND THE BINDER IS THE SELECTION**, and that names something
this system has needed and not had: **the set of things a mark MAY address.** A `move`
destination, or an `add`, may cite a page the binder never carried -- it is still in the library.
! That is the constraint Roy stated the same day: a destination must be ADDRESSABLE, *"not
necessarily in the binder."*

! **AND IT GIVES THE PULLED-IN PAGE ITS PROVENANCE.** A code file censused mid-run is not
"external" to anything -- it was on the shelf all along. What is true of it is that **the roles
never saw it**, which is a fact about the BINDER, not about the file.

### `pulled` -- the binder's section for a page taken from the library mid-run

**Ruled 2026-08-27.** The binder carries three sections:

    pages        what the ROLES reviewed -- the scope they were given
    pulled       a page taken from the library DURING the run, because a mark
                 needed it. Same shape as a page: path, sha, rows
    references   documents -- `path:line`, no cue series

! **THE NAME IS THE ACTION, AND IT IS ROY'S OWN**: *"an external program file should get a
`page_for` pull."* You pull a book off the shelf; `flows.page_for.page_of` pulls the page and
attaches its sha at the moment of the pull.

!! **THE DISTINGUISHING FACT IS THAT NO ROLE SAW IT**, so no role vouched for it. That is a fact
about the BINDER, not about the file -- which is why `external` was rejected: a page censused
mid-run is not external to anything, it was on the shelf all along.

! **AND IT STAYS TRUE IF THE PAGE IS SET.** A `move` destination may land in `pulled`, so the
section is not read-only; `consulted` was rejected for asserting otherwise, and would have stopped
being true the first time the chain wrote one.

!! **THE TWO PYTHON-PACKAGING USES ARE A DIFFERENT WORD AND ARE NOT COVERED HERE.**
`machine/repo.py`'s *"some library happens to define that name"* and `language.py`'s *"not by the
library that happens to answer it"* mean an INSTALLED package; `CLAUDE.md` and
`test_shipped_imports.py` mean Python's STANDARD LIBRARY. ! Ordinary Python prose, not terms of
art in this system -- but they are a second sense of a word that now has a settled definition, and
whether they get reworded is unruled.

!! **IT WAS NEVER HIS, AND THE RECORD PROVES IT.** MEASURED 2026-08-27: **no quotation from Roy
anywhere in this tree contains the word.** It entered in `decision-log.md Process: #12` -- an
entry attributed to him -- and spread as boilerplate to **ten `commands/*.py` banners**, `src/`'s
own `__init__`, `flows/__init__`, `results/galley.py`, a gate test and a release plan. 16 sites.

! **THE ENTRY'S QUOTATION DOES NOT CONTAIN IT EITHER.** `#12` cites Roy on entry points --
*"the commands run through it not through the scripts that are doing double or triple duty"* --
which says nothing about a layer called a library. **The headline stated more than its
quotation, and the quotation lent authority to the whole sentence.**

! **THE PRINCIPLE UNDER IT IS HIS**, and is quoted twice: *"don't try to make the list generic --
that is a failure of the single responsibility principle"* and *"anything else is failing the SRP
rules"* (both 2026-08-22). ! Both are about LANGUAGE DEFINITION ROWS, not modules -- so even the
supported half was carried across a subject boundary.

!! **IT IS NOT RETIRED, IT IS NARROWED.** `check_retired` scans `plugins/`, and two shipped files
use the word correctly -- `machine/repo.py`'s *"some library happens to define that name"* about
an installed package, and `language.py`'s *"not by the library that happens to answer it"* about a
third-party parser. **Retiring the word would refuse both.** This is declared polysemy of the
same kind as [`leaf`](#) -- one live sense, and a struck one that must not come back.

! **WHAT CAUGHT IT WAS ROY'S MEMORY**, not a gate. Everything in the tree agreed with itself: the
entry cited a real quotation, carried a real measurement, and was cross-referenced from a release
plan. He said *"I don't remember making this rule."* **The decision log is the one file where a
false attribution is most expensive, and it is the file with no reader but him.**

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

- **`clean` is reserved.** It is one of the seven instructions and is never a loose adjective for
  code, prose, a grep result or a run.
