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

**Count: 109 terms** — `budget` added 2026-08-15, after the collection missed it.

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
| **prose tree** | none; `SKILL.md:24` says "a node on the prose tree" | Appears in both manifests' user-facing descriptions. |
| **the join** | none | Names `verdicts.py`'s stage-5 gate. `SKILL.md:517,540,571,573,697`; `ref/reviewer-brief.md:42,92`; `CLAUDE.md:46`. |
| ~~**sweep**~~ | SETTLED 2026-08-15 — not a term | Stage 7b is **APPLY**, which every canonical naming site already said. The word was a synonym outliving `sweep.py` (now `census.py`), and the dead `import sweep` with it. Plain-English "sweep the file" stays. |
| **detector** | none | Used with a fixed sense (a mechanical mark and its precision) at `ref/reviewer-brief.md:234,236,246`; `sk-scripts/census.py:148,770`; `docs/parsing.md:47`; `README.md:131,141,152,260`. |
| **banner / section banner** | none | `agents/comment-review-module-context.md:3,18,24,98`; `README.md:93` paraphrases without the term. |
| **assessability gate** | none | Appears only in `agents/comment-review-ownership-context.md:3` frontmatter; the idea is stated without the phrase at `:30-42`. |
| **acquittal rate** | none | Used as a measured quantity at `agents/comment-review-module-context.md:96,110`. |
| **node** | implicit at `SKILL.md:76` ("Every comment run and every docstring is a node") | Collides with the Python AST `node` identifiers in three scripts — a different sense. |

## Words carrying more than one meaning

Observed by the scout pass. Recorded as-is.

| Word | Sense A | Sense B |
|---|---|---|
| **residue** | the comment-stripped byte comparison, `sk-scripts/prove_unchanged.py:13-15,101-147` | THE RESIDUE CHECK, a stage-level procedure, `ref/residue-check.md:15-26` |
| **SUPPRESSED / suppression** | the suppression list, `ref/reviewer-brief.md:234-247` | `referrers.py`'s token noise floor, `sk-scripts/referrers.py:15,147,173` |
| **label** | acquittal label, `ref/reviewer-brief.md:216` | review-round label, `agents/comment-review-block-context.md:28-29` |
| **node** | prose-tree node, `SKILL.md:76` | Python AST node, three scripts |
| **worktree** | corpus isolation, `scripts/fetch_corpora.py:5-7` | eval-run isolation, `evals/grade_hazards.py:7-13` |

---

## Full inventory

### The eight verdicts and their payloads

| Term | Defined | Multiplicity |
|---|---|---|
| `clean` | `SKILL.md:48`; `ref/reviewer-brief.md:104,139-148`; per-role at `CLAUDE.md:202-209`, `agents/…-block-context.md:92-97`, `…-function-context.md:118-121`, `…-module-context.md:113-114`, `…-ownership-context.md:97-102` | SEVERAL (6 sites) |
| `query` | `SKILL.md:49`; `ref/reviewer-brief.md:105,150-169`; gate `sk-scripts/verdicts.py:105-132,286-298` | SEVERAL |
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
| `QUERY_ATTEMPTED` / `QUERY_SETTLES` | `sk-scripts/verdicts.py:106-132`; prose at `ref/reviewer-brief.md:105,169`, `SKILL.md:546-548` | SEVERAL |
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
| `CODE CONCERNS` | `ref/reviewer-brief.md:249-262` | ONE |
| coverage gap | `ref/reviewer-brief.md:92`; `sk-scripts/verdicts.py:263-275,524-532` | SEVERAL |
| admissible / admissibility | `sk-scripts/verdicts.py:23`; echoed `SKILL.md:562` | ONE |

### The four editorial roles and the level ladder

| Term | Defined | Multiplicity |
|---|---|---|
| ownership-context | `agents/comment-review-ownership-context.md:2-3,16`; `CLAUDE.md:111` | SEVERAL |
| block-context | `agents/comment-review-block-context.md:2-3,16`; `CLAUDE.md:112-114` | SEVERAL (agent, CLAUDE, README, SKILL table) |
| function-context | `agents/comment-review-function-context.md:2-3,16`; `CLAUDE.md:115` | SEVERAL |
| module-context | `agents/comment-review-module-context.md:2-3,16`; `CLAUDE.md:116` | SEVERAL |
| level | `SKILL.md:182-208`; `sk-scripts/verdicts.py:61-70`; `sk-scripts/run_context.py:89-91` | SEVERAL (3 sites) |
| `fact-check` | `SKILL.md:186`; verdict set `sk-scripts/verdicts.py:67` | SEVERAL |
| `line` | `SKILL.md:187`; `sk-scripts/verdicts.py:68` | SEVERAL |
| `full` | `SKILL.md:188`; `sk-scripts/verdicts.py:69` | SEVERAL |
| `proof` | `SKILL.md:189`; empty verdict set `sk-scripts/verdicts.py:64,70` | SEVERAL |
| `--reviewers` (declared list) | `sk-scripts/verdicts.py:441-449,508-522` | ONE — `--angles` until 2026-08-15. ⚠ Never checked against the four published role names |

### Census structure

| Term | Defined | Multiplicity |
|---|---|---|
| census | `sk-scripts/census.py:5-7`; `SKILL.md:24-25,340-367` | SEVERAL |
| block (the unit a verdict rules on) | `sk-scripts/census.py:189`; `SKILL.md:368-396` | SEVERAL |
| comment run ("only code ends a run") | `SKILL.md:368-392`; impl `sk-scripts/census.py:100-111,347-430,478-524` | SEVERAL |
| counted lines (what a cap charges for) | `sk-scripts/census.py:100-111`; worked example `SKILL.md:376-392` | SEVERAL |
| KIND | `ref/compact.md:75-93` table; `sk-scripts/census.py:195` | SEVERAL |
| `comment` (kind) | `ref/compact.md:81`; `sk-scripts/census.py:195,379,497` | SEVERAL |
| `docstring` (kind; FORMAT not LENGTH) | `ref/compact.md:82`; `SKILL.md:146-149,659-662` | SEVERAL |
| `trailing-comment` | `SKILL.md:395-396`; `sk-scripts/census.py:379,497,509-515`; row `ref/compact.md:81` | SEVERAL |
| `unparsed` | `sk-scripts/census.py:528-539` | ONE |
| orphan / orphan run | `sk-scripts/census.py:461-466` | ONE |
| owner / OWNERSHIP | `SKILL.md:99-101,393-394`; `sk-scripts/census.py:26-29,198`; "a CONVENTION, not a parse result" `docs/parsing.md:130-134` | SEVERAL |
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
| mark | `SKILL.md:398-407` table; `sk-scripts/census.py:114-116,805-855` | SEVERAL |
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
| EDIT (5) | `SKILL.md:27,122-125,515` | SEVERAL |
| COMPACT (6) | `SKILL.md:28,127-149,669-692`; `ref/compact.md:1-10` | SEVERAL |
| APPROVAL / 7a / 7b | `SKILL.md:29-30,151,694,713` | SEVERAL |
| REVIEW (8) | `SKILL.md:31,153-154,722`; `ref/review.md:1-10` | SEVERAL |
| re-review | `SKILL.md:510-513,623-628`; `sk-scripts/verdicts.py:12,419-428,569-573` | SEVERAL |
| the join | — | UNDEFINED |
| APPLY (7b) | `SKILL.md:16-17,30,714`; `ref/apply.md:1` | SEVERAL — `sweep` retired as a synonym 2026-08-15 |
| input contract (COMPACT's narrow input) | `ref/compact.md:95-100`; `SKILL.md:139-149` | SEVERAL |

### The dispatch packet

| Term | Defined | Multiplicity |
|---|---|---|
| packet (run context) | `sk-scripts/run_context.py:1-29,38-68`; `SKILL.md:470-488` | SEVERAL |
| `REVIEWER FILES` (+ absolute-path rule) | `sk-scripts/run_context.py:47,63-65,17-21,247-250` | ONE — `ANGLE FILES` until 2026-08-15. ⚠ The hint's payload is SEVEN paths, not four |
| `CENSUS` | `sk-scripts/run_context.py:46,62`; checked `:243-246` | ONE |
| ~~`CAP`~~ (packet section) | SETTLED 2026-08-15 — REMOVED | Reviewers do not get a cap; the script had been refusing a packet without one, enforcing the opposite of `SKILL.md:211` and `reviewer-brief.md:292`. `WIDTH` removed with it. Packet is 9 sections. `cap` the run argument is unaffected |
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
| AST proof | `sk-scripts/prove_unchanged.py:11,150-176` | ONE |
| code signature | `sk-scripts/prove_unchanged.py:150-161` | ONE |
| residue (byte comparison) | `sk-scripts/prove_unchanged.py:13-15,101-147` | ONE |
| THE RESIDUE CHECK | `ref/residue-check.md:15-26` | ONE |
| PROVEN / FAIL / UNPROVABLE / UNCHECKED | `sk-scripts/prove_unchanged.py:5,16,158-176,270-318`; consequences `ref/apply.md:57-62` | SEVERAL |
| line-ending check / dominant ending / untouched sibling | `sk-scripts/prove_unchanged.py:20-23,179-243` | ONE |
| the four refusals | `ref/residue-check.md:40-55` | ONE |

### Judgment vocabulary

| Term | Defined | Multiplicity |
|---|---|---|
| `truthy` | `ref/reviewer-brief.md:174-181` | ONE |
| CHECKABLE | `SKILL.md:576` | ONE |
| NECESSARY | `SKILL.md:576` | ONE |
| the matrix | `SKILL.md:576-588`; named "the matrix" at `:259` | ONE |
| load-bearing | `agents/comment-review-ownership-context.md:54-58` | ONE |
| obituary (with the pointer-vs-subject test) | `agents/comment-review-block-context.md:31-45` | ONE |
| guard (exists AND could fail) | `agents/comment-review-function-context.md:38-50` | SEVERAL |
| prohibition (grepped against its own file) | `agents/comment-review-function-context.md:50-56` | SEVERAL |
| population (of a counted claim) | `ref/reviewer-brief.md:69-71,191-193` | SEVERAL |
| existence grep (the trap) | `ref/reviewer-brief.md:189-193`; same rule unnamed at `SKILL.md:409-410` | SEVERAL |
| acquittal list | `ref/reviewer-brief.md:212-231` | ONE |
| `label` (acquittal) | `ref/reviewer-brief.md:216` | ONE |
| states-the-signature | `ref/reviewer-brief.md:217-218` | ONE |
| derivation | `ref/reviewer-brief.md:219-223` | ONE |
| only-guard | `ref/reviewer-brief.md:224-225` | ONE |
| names-its-expiry | `ref/reviewer-brief.md:226` | ONE |
| suppression list | `ref/reviewer-brief.md:234-247` | ONE |
| batch to triage (<~10% precision) | `ref/reviewer-brief.md:237,246` | ONE |
| CONSERVATIVE ON MEANING, FREE ON FORM | `SKILL.md:162-166` | ONE |

### Angle-specific concepts

| Term | Defined | Multiplicity |
|---|---|---|
| HOME (of a claim stated at several sites) | `agents/comment-review-ownership-context.md:60-69`; split restated `ref/reviewer-brief.md:278-282` | SEVERAL |
| owning function (rule with no home in CODE) | `agents/comment-review-module-context.md:71-82`; split restated `ref/reviewer-brief.md:279` | SEVERAL |
| module-level state | `agents/comment-review-module-context.md:67-70` | ONE |
| reachability (a caller outside the tests) | `agents/comment-review-function-context.md:32-36` | ONE |
| running-commentary read (SEQUENCES vs CONSTRAINS) | `agents/comment-review-function-context.md:105-116` | ONE |
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
| `NOISE_FLOOR` / SUPPRESSED | `sk-scripts/referrers.py:14-18,45-47,146-147` | ONE |
| NOT CHECKED (gaps, not passes) | `sk-scripts/census.py:1022-1030`; `sk-scripts/referrers.py:176-193` | SEVERAL |
| LANGUAGE SERVER / LSP, three states | `SKILL.md:293-331` (table `:313-319`); restated `docs/parsing.md:17-49` | SEVERAL |
| detector | — | UNDEFINED |
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
