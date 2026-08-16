# Vocabulary inventory — every term of art, and where it is stated

**The term list for this system's own vocabulary**, with the site that states each.
What each term means at each of its uses is [`vocabulary-usage.md`](vocabulary-usage.md).

Produced by a scout pass over the live tree on 2026-08-15. Scope: the plugin
tree, `README.md`, `CLAUDE.md`, `docs/`, `evals/`, `tests/`, `scripts/`, both
manifests. Excluded as historical or vendored, not the live system:
`evidence/`, `docs/superpowers/`, `corpora/`, `.venv/`.

⚠ **Anchors predate `802a574` and have drifted** — the collecting pass found
`SKILL.md`'s moved one to three lines. Corrected anchors are in
[`vocabulary-usage.md`](vocabulary-usage.md); verify against the file before acting.

**Path key** — all relative to the repo root:

- `SKILL.md` = `plugins/comment-review/skills/comment-review/SKILL.md`
- `ref/…` = `plugins/comment-review/skills/comment-review/references/…`
- `sk-scripts/…` = `plugins/comment-review/skills/comment-review/scripts/…`
- `agents/…` = `plugins/comment-review/agents/…`

**Count: 110 terms** — `budget` added 2026-08-15, after the collection missed it.

## How to read the multiplicity column

`ONE` — the term is stated at a single site.

`SEVERAL` — the term is stated at more than one site.

`UNDEFINED` — the term is used with a fixed sense but stated at no site.

---

## No stated definition — used as though fixed, stated nowhere

| Term | Nearest thing to a definition | Notes |
|---|---|---|
| ~~**angle**~~ | SETTLED 2026-08-15 — retired | Borrowed from `/simplify`, where it names that pass's focuses. Prose now says **editorial role**; identifiers say **reviewer** (`--reviewers`, `REVIEWER FILES`, `reviewer = path.stem`), because `role` alone would also cover the task agent and the author. Six senses, all resolved: [the ruling](vocabulary-usage.md#angle--settled-2026-08-15-retired-in-favour-of-editorial-role). |
| ~~**budget**~~ | SETTLED 2026-08-15 — `docs/limitations.md:9` | ⚠ **Missed by the twelve-agent collection entirely** — 18 sites, four senses, in neither table. Roy's ruling: **the only real budget is what a shipped instruction file costs everyone to load**, measured in lines per file. `cap` took back the five sites meaning a comment's line limit. The reviewer-runtime sense loses the word. ⚠ Measured: the budget covers 28 KB of the 224 KB shipped, and not the two largest files every run loads. |
| ~~**prose tree**~~ | SETTLED 2026-08-15 — `SKILL.md:76` | Stated where the shape was already explained but unnamed: every comment run and every docstring in the files under review, each one a NODE. Both manifests' user-facing text now names something a reader can look up. |
| ~~**original**~~ | SETTLED 2026-08-16 — stated at `ref/residue-check.md:11-12` | **The text as it stood when THIS RUN began**, not the first version ever written. Roy asked for the statement after all: *"think about stage 8 — it gets an edited file which if it finds and the human agrees needs edits becomes the original on the next round."* So it is relative to the RUN, which is what `ref/compact.md` and `ref/write.md` already rely on without saying |
| **pCST** (pseudo Concrete Syntax Tree) | `vocabulary-usage.md` | Every interval between two lines of code as a node. *Pseudo* because it comes from a comment-syntax record and a lexer, not the language's own grammar. ⚠ NOT a synonym for `prose tree` — the census still enumerates from prose, so an empty interval produces nothing. Building it is [`an-empty-interval-has-no-census-index`](../TODO/an-empty-interval-has-no-census-index.md). |
| ~~**the join**~~ | SETTLED 2026-08-15 — `SKILL.md:526` | Named at first use: `verdicts.py`, which reads every reviewer's report against the census and against the others', and refuses what it cannot verify. |
| ~~**sweep**~~ | SETTLED 2026-08-15 — not a term | Stage 7b is **WRITE** (it was APPLY when `sweep` was retired; APPLY then moved to stage 5). The word was a synonym outliving `sweep.py` (now `census.py`), and the dead `import sweep` with it. Plain-English "sweep the file" stays. |
| ⚠ **detector** — **RE-OPENED** | its only definition was inside the deleted suppression list | Settled 2026-08-15, un-settled 2026-08-16 when the section holding it went. `sk-scripts/census.py:147,770` still use it |
| ~~**banner / section banner**~~ | SETTLED 2026-08-15 — `agents/…-module-context.md:18` | Comment lines dividing a file into named parts. Stated LINE-NEUTRALLY, that file being at its budget. |
| ~~**assessability gate**~~ | SETTLED 2026-08-15 — **DELETED** | Used once, stated nowhere, and the idea was already stated without it at `:30-42`. This repo's own rule: if nothing reads it, delete it. |
| ~~**acquittal rate**~~ | SETTLED 2026-08-15 — **DELETED** | A measured quantity whose denominator no site stated. Both uses now say the population instead: "most of the census you are handed", and "95% of the blocks it was handed". `acquittal list` is unaffected and remains defined at `ref/reviewer-brief.md:211`. |
| ~~**node**~~ | SETTLED 2026-08-15 — `SKILL.md:76` | Stated with `prose tree`, in one sentence. ⚠ The Python AST `node` in three scripts is a genuinely different sense and stays; it is an implementation identifier, not this system's term. |

## Words carrying more than one meaning

Observed by the scout pass. Recorded as-is.

| Word | Sense A | Sense B |
|---|---|---|
| ~~**residue**~~ | SETTLED 2026-08-16 — the PROSE check keeps the word | The CODE CHECK's artifact is now **`stripped`**: `code_fingerprint` returns kind `ast`, `stripped` or `unprovable`, and `_residue()` is `_without_comments()`. `residue` means only the stage-5/6/7b procedure, `ref/residue-check.md` |
| ~~**SUPPRESSED / suppression**~~ | PARTLY SETTLED 2026-08-16 — **nothing gets suppressed** | `NOISE_FLOOR` and the `SUPPRESSED` output are deleted from `referrers.py`; `census.py`'s two uses go with [its own TODO](../TODO/the-shipped-python-does-not-pass-its-own-review.md). Both lists are DELETED as of 2026-08-16 |
| ~~**label**~~ | SETTLED 2026-08-16 by subtraction — ONE sense left | The acquittal sense went with the acquittal list, so `label` means the REVIEW-ROUND label only: `agents/comment-review-block-context.md:28-29`, *"fix round 2"*, *"finding B4"*. `sk-scripts/census.py:161`'s `"a review label"` annotation is the same sense |
| **node** | prose-tree node, `SKILL.md:76` | Python AST node, three scripts |
| ~~**statement**~~ | SETTLED 2026-08-16 — CODE only | The *derived statement* (`SUMMARY`'s right half, `sk-scripts/verdicts.py:369-370`) and the prose proposition at `agents/…-module-context.md:115` are the two uses the ruling leaves unqualified |
| ~~**worktree**~~ | SETTLED 2026-08-16 — **git's word, not a term of art here** | Both collected uses are ordinary git usage in dev tooling that never ships (`fetch_corpora.py` isolates a corpus, `grade_hazards.py` isolates a graded run). The six shipped sites that used it as a REASON were removed 2026-08-16. The one use left in `plugins/` — `ref/reviewer-brief.md:203`, *"an archive absent from every worktree"* — is a MEASUREMENT about a repository, not a rule |
| ~~**template**~~ | SETTLED 2026-08-16 — ONE concept, stated at `SKILL.md:255` | **A shape written out with its slots, not a shape NAMED.** The measured doc format and the dispatch packet are the same concept applied to two documents, so one definition covers both — 19 sites across 5 files, defined nowhere until now. ⚠ C++ `template nesting` at `sk-scripts/census.py:320` is the zero-overlap language construct, kept |
| ⚠ **gap** — SPLIT 2026-08-16, one sense still open | **(1)** the COVERAGE gap is to be DROPPED — Roy: *"if comment blocks are missed by a reviewer then they are returned to the reviewer to rule on"*: [`a-coverage-gap-should-go-back-to-the-reviewer`](../TODO/a-coverage-gap-should-go-back-to-the-reviewer.md) | **(2)** *"NOT CHECKED — these are gaps, not passes"* stands: neither script can silently miss a file, and each cause is named. **(3)** a name in the surface the docstring never accounts for is now an **OMISSION** |
| **opener** | a comment OPENER, the lexer's delimiter (`sk-scripts/census.py:219,354,361`) | a RECORD opener, `--- FINDING` (`sk-scripts/verdicts.py:73`). ⚠ DECLARED 2026-08-16, both kept: Roy — *"one is a programming concept and is separate from the editing concept and so could justify having two definitions because of 0 overlap"* |
| ~~**walk**~~ | RETIRED from the prose 2026-08-16 — **no editorial bent** | Roy: *"I am not comfortable with the way it is being used here … that seems like it is missing the appropriate editorial bent."* An editor READS a manuscript and CHECKS a list; nobody walks a page. 7 sites: `## Read the census end to end`, *"read it start to finish"*, *"a list to check"*, *"read the module docstring against that list"*, *"enumerated the surface and checked it"*, *"coverage is a COMPLETE READ"*. `ast.walk` is untouched |
| **annotations** | the census's, settled 2026-08-15 | `from __future__ import annotations`, in every shipped script. ⚠ DECLARED 2026-08-16, both kept — the same ZERO-OVERLAP case as `opener` and `node`: a language keyword cannot be mistaken for an editorial term |

---

## Full inventory

### The eight verdicts and their payloads

| Term | Defined | Multiplicity |
|---|---|---|
| `clean` | `SKILL.md:48`; `ref/reviewer-brief.md:104,139-153`; per-role at `CLAUDE.md:202-209`, `agents/…-block-context.md:92-97`, `…-function-context.md:118-121`, `…-module-context.md:113-114`, `…-ownership-context.md:97-102` | SEVERAL (6 sites) |
| `query` | `SKILL.md:49`; `ref/reviewer-brief.md:105,155-174`; gate `sk-scripts/verdicts.py:105-132,286-298` | SEVERAL |
| `drop` | `SKILL.md:50`; `ref/reviewer-brief.md:106` | SEVERAL |
| `correct` | `SKILL.md:51,64-67`; `ref/reviewer-brief.md:107,114-118` | SEVERAL |
| `patch` | `SKILL.md:52,64-67`; `ref/reviewer-brief.md:108,114-118` | SEVERAL |
| `add` | `SKILL.md:53`; `ref/reviewer-brief.md:109` | SEVERAL |
| `move` | `SKILL.md:54,57-62`; `ref/reviewer-brief.md:111,120-125`; `agents/…-ownership-context.md:71-84` | SEVERAL — the ONE relocation verdict since 2026-08-15 |
| ~~`reanchor`~~ | SETTLED 2026-08-15 — collapsed into `move` | A relocation is one judgment; the DESTINATION is payload and the reason is `FINDING`. Availability and synthesis order now key on the destination, not on a second word |
| `split` | `SKILL.md:56`; `ref/reviewer-brief.md:112` | SEVERAL |
| verdict (the set) | `SKILL.md:41-72`; `ref/reviewer-brief.md:96-112` | SEVERAL |
| payload | `ref/reviewer-brief.md:96-112`; enforced `sk-scripts/verdicts.py:283-316` | SEVERAL |
| `add` payload — an anchor | `ref/reviewer-brief.md:109`; `sk-scripts/verdicts.py:302-307` | SEVERAL |
| `correct` payload — true/false pair | `ref/reviewer-brief.md:107`; `sk-scripts/verdicts.py:299-300` | SEVERAL |
| `QUERY_ATTEMPTED` / `QUERY_SETTLES` | `sk-scripts/verdicts.py:106-132`; prose at `ref/reviewer-brief.md:105,174`, `SKILL.md:546-548` | SEVERAL |
| escalated `query` | `ref/compact.md:30-35` | ONE |
| `MOVE DESTINATION` / `move` UNAVAILABLE | `SKILL.md:251-262`; packet `sk-scripts/run_context.py:45,61` | SEVERAL |
| clean-arithmetic | `sk-scripts/verdicts.py:576-583`; invoked unnamed at `SKILL.md:605-607`, `ref/reviewer-brief.md:141-143`, `agents/…-module-context.md:104` | ONE (named), SEVERAL (invoked) |
| STANDS UNCHANGED | `sk-scripts/verdicts.py:15,576-587`; `SKILL.md:605-608` | SEVERAL |
| contradiction (drop vs correct/patch) | `SKILL.md:623-628`; `sk-scripts/verdicts.py:419-428` | SEVERAL |
| laundering | `SKILL.md:64-67`; `ref/reviewer-brief.md:114-118` | SEVERAL |

### Record fields — the finding format

| Term | Defined | Multiplicity |
|---|---|---|
| finding | `ref/reviewer-brief.md:39-67`; parsed `sk-scripts/verdicts.py:135-154,207-260` | SEVERAL |
| RECORD (`--- FINDING` block) | `ref/reviewer-brief.md:39-56`; `sk-scripts/verdicts.py:73-83,207-260` | SEVERAL |
| `VERDICT` | `ref/reviewer-brief.md:61` | ONE |
| `LOCATION` | `ref/reviewer-brief.md:62`; enforced `sk-scripts/verdicts.py:404-416` | SEVERAL |
| `EVIDENCE` | `ref/reviewer-brief.md:63`; enforced `sk-scripts/verdicts.py:362-401` | SEVERAL |
| `QUOTE` | `ref/reviewer-brief.md:64,79-83`; enforced `sk-scripts/verdicts.py:362-401` | SEVERAL |
| `SUMMARY` (left half quoted, right half DERIVED) | `ref/reviewer-brief.md:65,69-71,85-88`; `sk-scripts/verdicts.py:369,393` | SEVERAL |
| `FINDING` (one clause) | `ref/reviewer-brief.md:66` | ONE |
| `CHANGE` | `ref/reviewer-brief.md:67` | ONE |
| `BLOCK` (census index) | `ref/reviewer-brief.md:60` | ONE |
| `CLEAN` range line | `ref/reviewer-brief.md:73-79,90-92`; parsed `sk-scripts/verdicts.py:89,254-260` | SEVERAL |
| `EVIDENCE_WINDOW` / `MIN_NEEDLE` | `sk-scripts/verdicts.py:95-103`; prose `ref/reviewer-brief.md:64,79-83` | SEVERAL |
| `CODE CONCERNS` | `ref/reviewer-brief.md:215-228` | ONE |
| coverage gap | `ref/reviewer-brief.md:92`; `sk-scripts/verdicts.py:263-275,524-532` | SEVERAL |
| admissible / admissibility | `sk-scripts/verdicts.py:23`; echoed `SKILL.md:562` | ONE |

### The four editorial roles and the level ladder

| Term | Defined | Multiplicity |
|---|---|---|
| ownership-context | `agents/comment-review-ownership-context.md:2-3,16`; `CLAUDE.md:111` | SEVERAL |
| block-context | `agents/comment-review-block-context.md:2-3,16`; `CLAUDE.md:112-114` | SEVERAL (agent, CLAUDE, README, SKILL table) |
| function-context | `agents/comment-review-function-context.md:2-3,16`; `CLAUDE.md:115` | SEVERAL |
| module-context | `agents/comment-review-module-context.md:2-3,16`; `CLAUDE.md:116` | SEVERAL |
| **remit** | `ref/reviewer-brief.md:71` | ONE — SETTLED 2026-08-16: the CATEGORIES of claim a role rules on, as against `verify`, which is what it does to them. Took the five sites where `own` carried this sense. ⚠ Was `jurisdiction` for one day: a JUDICIAL word on an editorial system, replaced the same day the metaphor became a rule in `CLAUDE.md`. `remit` is publishing's word, and 7 characters shorter at every site |
| level | `SKILL.md:182-208`; `sk-scripts/verdicts.py:61-70`; `sk-scripts/run_context.py:89-91` | SEVERAL (3 sites) |
| `fact-check` | `SKILL.md:186`; verdict set `sk-scripts/verdicts.py:67` | SEVERAL |
| `line` | `SKILL.md:187`; `sk-scripts/verdicts.py:68` | SEVERAL |
| `full` | `SKILL.md:188`; `sk-scripts/verdicts.py:69` | SEVERAL |
| ~~`proof` / PROOFREADER~~ | SETTLED 2026-08-16 — the PRINTING sense | `SKILL.md:189`; empty verdict set `sk-scripts/verdicts.py:64,70`; `agents/comment-review-review.md:7`. A proof is the finished page; the PROOFREADER reads it and decides whether the document deserves more marks; the `proof` LEVEL is the run that does only that. ⚠ `sk-scripts/prove_unchanged.py`'s `PROVEN` / `unprovable` / *"proof kind"* is the EVIDENTIAL sense — observed, not ruled |
| `--reviewers` (declared list) | `sk-scripts/verdicts.py:441-449,508-522` | ONE — `--angles` until 2026-08-15. ⚠ Never checked against the four published role names |

### Census structure

| Term | Defined | Multiplicity |
|---|---|---|
| census | `sk-scripts/census.py:5-7`; `SKILL.md:24-25,340-367` | SEVERAL |
| block (the unit a verdict rules on) | `sk-scripts/census.py:190`; `SKILL.md`'s "What counts as ONE block" | SEVERAL — **the interval between two code lines**, ruled 2026-08-15. The code already did this; the prose said "one comment run" |
| comment run ("only code ends a run") | `SKILL.md:368-392`; impl `sk-scripts/census.py:100-111,347-430,478-524` | SEVERAL |
| counted lines (what a cap charges for) | `sk-scripts/census.py:100-111`; worked example `SKILL.md:376-392` | SEVERAL |
| KIND | `ref/compact.md:75-93` table; `sk-scripts/census.py:195` | SEVERAL |
| `comment` (kind) | `ref/compact.md:81`; `sk-scripts/census.py:195,379,497` | SEVERAL |
| `docstring` (kind; FORMAT not LENGTH) | `ref/compact.md:82`; `SKILL.md:146-149,659-662` | SEVERAL |
| `trailing-comment` | `SKILL.md:395-396`; `sk-scripts/census.py:379,497,509-515`; row `ref/compact.md:81` | SEVERAL |
| `unparsed` | `sk-scripts/census.py:528-539` | ONE |
| orphan / orphan run | `sk-scripts/census.py:461-466` | ONE |
| ~~**owner / own / ownership**~~ | SETTLED 2026-08-16 — `agents/…-ownership-context.md:60-65` | The **anchor with the best justification** for the comment being attached to it; where several compete, the site that ENFORCES the constraint, or the code expected to hold the invariant where nothing enforces it. `HOME` is retired — one stem. `Block.owner` became `Block.anchor`, the census computing a position rather than a judgement. The ROLE's-jurisdiction sense went to **remit**; the ownership/module split is PRESENCE (prose exists → ownership-context; prose absent → module-context or function-context, by scope): [the ruling](vocabulary-usage.md#own--owner--ownership--settled-2026-08-16-for-the-placement-sense-home-retired) |
| node (prose tree) | implicit `SKILL.md:76` | UNDEFINED |
| work marker (`TODO` `FIXME` `HACK` `XXX` `BUG`) | `sk-scripts/census.py:87-111`; `SKILL.md:242-244,388-392` | SEVERAL |

### Tiers and language support

| Term | Defined | Multiplicity |
|---|---|---|
| tier | `SKILL.md:91-97`; `sk-scripts/census.py:20-24,303-306,858-864`; `CLAUDE.md:125-130`; `docs/parsing.md:13-16` | SEVERAL (4 sites) |
| tokenized | `SKILL.md:96`; `sk-scripts/census.py:23,304,864`; `CLAUDE.md:129` | SEVERAL |
| lexical | `SKILL.md:97`; `sk-scripts/census.py:24,305,347-360,864`; `CLAUDE.md:130` | SEVERAL |
| LANGUAGES record ("adding a language is a data row") | `sk-scripts/census.py:234-296` | SEVERAL |
| `doc_is_structural` | `sk-scripts/census.py:246-248,433-453` | ONE |
| `doc-kind-unresolved` | `sk-scripts/census.py:433-475`; consumed `ref/compact.md:83,89-93` | SEVERAL |
| `unterminated-block-comment` | `sk-scripts/census.py:355-360,420-429`; consumed `sk-scripts/prove_unchanged.py:25-30,112-127` | SEVERAL |
| unreviewable | `SKILL.md:118`; `sk-scripts/census.py:909` | SEVERAL |

### Marks

| Term | Defined | Emitted |
|---|---|---|
| annotation (was `mark`) | `SKILL.md`'s annotations table; `sk-scripts/census.py:114-116,805-855` | SEVERAL — renamed 2026-08-15 so `mark` means the editorial sense only. `block.annotations`, `annotate()`, `"annotations"` |
| `counted` | `SKILL.md:404` | `sk-scripts/census.py:130-135,835-837` |
| `coverage-claim` | `SKILL.md:405` | `sk-scripts/census.py:136-140,839-842` |
| `names-a-symbol` | `SKILL.md:403` | `sk-scripts/census.py:811-820` |
| `cites-a-path` | `SKILL.md:402` | `sk-scripts/census.py:823` |
| `forbids-a-literal` | `SKILL.md:406` | `sk-scripts/census.py:141-144,843-845` |
| `repeated-literal` | `SKILL.md:407` | `sk-scripts/census.py:945-959` |

### Stages

| Term | Defined | Multiplicity |
|---|---|---|
| PROJECT DETERMINATION (1) | `SKILL.md:23,214` | SEVERAL |
| ANNOTATE (2) | `SKILL.md:24` | SEVERAL |
| FIND REFERENCES (3) | `SKILL.md:25` | SEVERAL |
| MARK (4) | `SKILL.md:26,120-121,459` | SEVERAL |
| APPLY (5) | `SKILL.md:16,27,120-139,516` | SEVERAL — `EDIT` until 2026-08-15 |
| COMPACT (6) | `SKILL.md:28,127-149,669-692`; `ref/compact.md:1-10` | SEVERAL |
| APPROVAL / 7a / 7b | `SKILL.md:29-30,151,694,713` | SEVERAL |
| REVIEW (8) | `SKILL.md:31,153-154,722`; `ref/review.md:1-10` | SEVERAL |
| re-review | `SKILL.md:510-513,623-628`; `sk-scripts/verdicts.py:12,419-428,569-573` | SEVERAL |
| the join | — | UNDEFINED |
| WRITE (7b) | `SKILL.md:17,30,719`; `ref/write.md:1` | SEVERAL — `sweep` retired 2026-08-15; renamed from APPLY the same day when APPLY moved to stage 5 |
| input contract (COMPACT's narrow input) | `ref/compact.md:95-100`; `SKILL.md:139-149` | SEVERAL |

### The dispatch packet

| Term | Defined | Multiplicity |
|---|---|---|
| packet (run context) | `sk-scripts/run_context.py:1-29,38-68`; `SKILL.md:470-488` | SEVERAL |
| `REVIEWER FILES` (+ absolute-path rule) | `sk-scripts/run_context.py:47,63-65,17-21,247-250` | ONE — `ANGLE FILES` until 2026-08-15. ⚠ The hint's payload is SEVEN paths, not four |
| `CENSUS` | `sk-scripts/run_context.py:46,62`; checked `:243-246` | ONE |
| ~~`CAP`~~ (packet section) | SETTLED 2026-08-15 — REMOVED | Reviewers do not get a cap; the script had been refusing a packet without one, enforcing the opposite of `SKILL.md:211` and `reviewer-brief.md:258`. `WIDTH` removed with it. Packet is 9 sections. `cap` the run argument is unaffected |
| `LEVEL` | `sk-scripts/run_context.py:39,53,91,239-242` | ONE |
| `DOC CONVENTION` | `sk-scripts/run_context.py:42,56`; `SKILL.md:247-249` | SEVERAL |
| `LSP LANGUAGES` | `sk-scripts/run_context.py:44,58-60` | ONE |
| `FILES UNDER REVIEW` | `ref/reviewer-brief.md:17`; `sk-scripts/run_context.py:48,66` | SEVERAL |
| `REFERENCE ONLY` | `ref/reviewer-brief.md:19-22`; `sk-scripts/referrers.py:5-13`; selection `SKILL.md:497-504` | SEVERAL |
| STYLE SHEET | `SKILL.md:264-279` | ONE |
| DISPATCHABLE / namespaced agent | `SKILL.md:281-291` | SEVERAL |

### Proof and residue

| Term | Defined | Multiplicity |
|---|---|---|
| CODE CHECK (7b's gate) | `sk-scripts/prove_unchanged.py:1,150-176`; `ref/write.md:36` | SEVERAL — `AST proof` / `the proof` until 2026-08-15; `proof` now means stage 8's pass only |
| code signature | `sk-scripts/prove_unchanged.py:150-161` | ONE |
| residue (byte comparison) | `sk-scripts/prove_unchanged.py:13-15,101-147` | ONE |
| THE RESIDUE CHECK | `ref/residue-check.md:15-26` | ONE |
| PROVEN / FAIL / UNPROVABLE / UNCHECKED | `sk-scripts/prove_unchanged.py:5,16,158-176,270-318`; consequences `ref/write.md:57-62` | SEVERAL |
| line-ending check / dominant ending / untouched sibling | `sk-scripts/prove_unchanged.py:20-23,179-243` | ONE |
| the four refusals | `ref/residue-check.md:36-50` | ONE |

### Judgment vocabulary

| Term | Defined | Multiplicity |
|---|---|---|
| `truthy` | `ref/reviewer-brief.md:179-186` | ONE |
| **sentence** — the unit a verdict rules on | `ref/reviewer-brief.md:175-176`, *"Rule on SENTENCES, not blocks"*; `truthy` at `:174-181` defines when one can be ruled | SEVERAL (~45 sites) — stated, and the most-used word in the shipped prose after the verdicts. ⚠ Contradicts `:92`'s *"exactly once"*: [`the-unit-of-review-is-the-statement-not-the-block`](../TODO/the-unit-of-review-is-the-statement-not-the-block.md) |
| **clause** — a part of a sentence | `ref/reviewer-brief.md:67` (`FINDING` is *"one clause"*), `:108` (`correct` carries *"the false clause **and** the true one"*) | SEVERAL — the SUB-SENTENCE unit `correct` and `FINDING` work at, so the ruled thing is sometimes smaller than a sentence. ⚠ The `except` clause in four script comments is Python's word for a code construct — the same split as `node` |
| ~~**statement / expression / declaration / assignment**~~ | SETTLED 2026-08-16 — `agents/…-ownership-context.md:55-57` | They name CODE, and they classify an ANCHOR. An OWNER is a judgement about which anchor best justifies the comment, never a syntactic kind. ⚠ `expression` and `assignment` are at ZERO sites — named so the next writer does not reach for them |
| **`signature`** → **`fingerprint`** | `sk-scripts/prove_unchanged.py:162-171` | ONE each since 2026-08-16. `code_signature` returned an `ast.dump` or the comment-stripped text — what 7b compares, which is a fingerprint. `signature` now means a function's, only |
| **argument** | rhetorical: `agents/…-module-context.md:19`, `ref/compact.md:19,98`, `SKILL.md:144,712`; a call's: `agents/…-function-context.md:42`; CLI: `argparse` ×5 | SEVERAL — Roy kept the RHETORICAL sense 2026-08-16. module-context's question is whether a file reads as ONE argument; the two code senses are qualified at every site |
| CHECKABLE | `SKILL.md:576` | ONE |
| NECESSARY | `SKILL.md:576` | ONE |
| the matrix | `SKILL.md:576-588`; named "the matrix" at `:259` | ONE |
| load-bearing | `agents/comment-review-ownership-context.md:56` | ONE — clear as written; three of its four readers cannot load that file (distribution pass) |
| obituary / **tombstone** | `agents/comment-review-block-context.md:31` | ONE — synonym declared in the heading 2026-08-16, so an agent reaching for `tombstone` finds the rule |
| guard / invariant | ⚠ STATED ONLY IN `docs/vocabulary-usage.md` — its shipped statement was the `unguarded-invariant` entry, deleted 2026-08-16 with the acquittal list. `agents/comment-review-function-context.md:39-43,66,69` still USE both words | SEVERAL — split 2026-08-16: a GUARD is code that protects against wrong output; an INVARIANT is what the code should hold, and a comment carries it when no guard does |
| prohibition (grepped against its own file) | `agents/comment-review-function-context.md:45-49` | SEVERAL |
| population (of a counted claim) | `ref/reviewer-brief.md:69-71,196-198` | SEVERAL |
| existence grep (the trap) | `ref/reviewer-brief.md:194-198`; same rule unnamed at `SKILL.md:409-410` | SEVERAL |
| ~~acquittal list~~ | DELETED 2026-08-16 | Matched a prose SHAPE while every role's `clean` is a truth assertion at that role's scope. Its entries are held in [`the-two-lists-were-tuned-to-one-diff`](../TODO/the-two-lists-were-tuned-to-one-diff.md) |
| ~~`label` (acquittal)~~ | DELETED 2026-08-16 with the list | Leaves `label` meaning the review-round label only |
| ~~states-the-signature~~ | DELETED 2026-08-16 | ⚠ It contradicted `function-context`'s absence question, which asks for what the SIGNATURE CANNOT EXPRESS |
| ~~derivation~~ | DELETED 2026-08-16 | A check (re-run the arithmetic) wearing an exemption's name |
| ~~`unguarded-invariant`~~ | DELETED 2026-08-16 with the acquittal list | It was `only-guard` until earlier the same day; the old name read as "the only CODE guard", the opposite of what it excused. ⚠ It carried the guard/invariant DEFINITION, which now has no shipped home |
| ~~names-its-expiry~~ | DELETED 2026-08-16 | A check (has the condition already been met?) wearing an exemption's name |
| ~~suppression list~~ | DELETED 2026-08-16 | No provenance in `evidence/`, and it suppressed nothing. Its content is held in [`the-two-lists-were-tuned-to-one-diff`](../TODO/the-two-lists-were-tuned-to-one-diff.md) |
| ~~batch to triage (<~10% precision)~~ | DELETED 2026-08-16 with the suppression list | Rates were measured on ONE repository — the same one the GA scored against |
| CONSERVATIVE ON MEANING, FREE ON FORM | `SKILL.md:162-166` | ONE |

### Angle-specific concepts

| Term | Defined | Multiplicity |
|---|---|---|
| ~~HOME~~ | RETIRED 2026-08-16 — the word is **owner** | It named the site a duplicated claim survives at, which is what `owner` names. One stem: `anchor` is the code position, `ownership` the relation, `owner` the anchor that wins it |
| owning function (rule with no home in CODE) | `agents/comment-review-module-context.md:71-82`; split restated `ref/reviewer-brief.md:245` | SEVERAL |
| module-level state | `agents/comment-review-module-context.md:67-70` | ONE |
| reachability (a caller outside the tests) | `agents/comment-review-function-context.md:32-36` | ONE |
| running-commentary read (SEQUENCES vs CONSTRAINS) | `agents/comment-review-function-context.md:98-109` | ONE |
| state / constraint / worked example | `agents/comment-review-block-context.md:18-24`; `CLAUDE.md:112-114`; `README.md` | SEVERAL |
| review label / review-round label | `agents/comment-review-block-context.md:28-29`; detected `sk-scripts/census.py:161-164` | SEVERAL |
| banner / section banner | — | UNDEFINED |
| assessability gate | — | UNDEFINED |
| acquittal rate | — | UNDEFINED |

### Roles

| Term | Defined | Multiplicity |
|---|---|---|
| editorial board | `SKILL.md:10-13,162` | SEVERAL |
| author (the HUMAN, absent) | `SKILL.md:158-160` | ONE |
| task agent | `SKILL.md:168-172` | ONE |
| REVIEWERS (read-only, one editorial role each, never see SKILL.md) | `SKILL.md:174` | ONE |
| editorial role | `ref/reviewer-brief.md:3`; `SKILL.md:3,11,33,85`; `CLAUDE.md:106` | SEVERAL — stated 2026-08-15, replacing the undefined `angle` ([ruling](vocabulary-usage.md#angle--settled-2026-08-15-retired-in-favour-of-editorial-role)) |
| prose tree | — | UNDEFINED |

### Corpus, liveness, infrastructure

| Term | Defined | Multiplicity |
|---|---|---|
| name corpus | `SKILL.md:328-338`; `sk-scripts/census.py:601-668` | SEVERAL |
| liveness | `SKILL.md:304,421-423`; `docs/parsing.md:45-49` | SEVERAL |
| tracked (git ls-files as the boundary) | `sk-scripts/census.py:601-668,732-802` | ONE |
| `CANDIDATE` | `sk-scripts/census.py:15-18`; `sk-scripts/referrers.py:11-13` | SEVERAL |
| ~~`NOISE_FLOOR` / SUPPRESSED~~ | DELETED 2026-08-16 from `referrers.py` | Nothing gets suppressed; the test is inverted to assert a token naming 41 files is listed per file |
| NOT CHECKED (gaps, not passes) | `sk-scripts/census.py:1022-1030`; `sk-scripts/referrers.py:159-166` | SEVERAL |
| LANGUAGE SERVER / LSP, three states | `SKILL.md:293-331` (table `:313-319`); restated `docs/parsing.md:17-49` | SEVERAL |
| ⚠ detector | — | **RE-OPENED 2026-08-16** — its only definition went with the suppression list: [`the-two-lists-were-tuned-to-one-diff`](../TODO/the-two-lists-were-tuned-to-one-diff.md) |
| corpus / corpora, `local` vs `public`, pinned ref, MANIFEST | `scripts/fetch_corpora.py:1-14,58-92,105-140`; restated `CLAUDE.md:169-176`, `README.md:192-210` | SEVERAL |
| assisted / human / mixed / unknown | `evals/generator_split.py:151,164` | ONE |
| discriminator (D1–D12 / hazard) | `evals/discriminators.md:1-88`; probes `evals/grade_hazards.py:33-67` | SEVERAL |
| GONE / REDUCED / SURVIVES / NEEDS-EYES / PROBE-MISS | `evals/grade_hazards.py:99-132` | ONE |
| FLOOR (py3.9 shipped-syntax floor) | `scripts/check_shipped_syntax.py:25-29` | SEVERAL |
| worktree | `scripts/fetch_corpora.py:5-7` (corpus); `evals/grade_hazards.py:7-13` (grading) | SEVERAL — two senses |

### Run arguments

| Term | Defined | Multiplicity |
|---|---|---|
| cap | `SKILL.md:178-180`; applied at stage 6 only `SKILL.md:211` | SEVERAL |
| width | `SKILL.md:220-228` | SEVERAL |
| `target` | `SKILL.md:181` | ONE |
| merge base (1.1 scope) | `SKILL.md:216-218` | ONE |

---

## Collection bundles

Twelve bundles for the fan-out. Each agent reads every site for its terms and
records what the term means at each one. Where the meaning differs between
sites, both are recorded. No agent judges whether a difference is a defect —
that comes after the data is in.

1. **The eight verdicts + payloads** — the verdict table above
2. **Record fields** — the finding-format table
3. **Angles + level ladder**
4. **Census structure**
5. **Tiers and language support**
6. **Marks**
7. **Stages**
8. **The dispatch packet**
9. **Proof and residue** (including both senses of `residue`)
10. **Judgment vocabulary**
11. **Angle-specific concepts** (including both senses of `label`)
12. **Roles, corpus, infrastructure, run arguments** (including both senses of `worktree` and of `SUPPRESSED`)

The two tables above — no stated definition, and words carrying more than one
meaning — were read off the tree by the scout pass. The bundles re-cover the
same terms, so each is recorded twice by independent readers.
