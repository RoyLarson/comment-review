# Vocabulary — every term of art, and what it means at each use

**What this system's own vocabulary does today.** Where each term is stated, where it
is used, and the sense it carries at each site. Not a record of prose defects in a
reviewed codebase — those are `evidence/`.

Collected 2026-08-15 by twelve agents, one per bundle, over the tree at commit
`802a574` on `feat/angle-scope-rename`. Scope excludes `evidence/`,
`docs/superpowers/`, `corpora/`, `.venv/` as historical or vendored.

**This document records observations, not judgments** about whether any difference
between sites is a defect. Which of them are defects, and what to do about each, is
[`TODO/eight-terms-have-no-definition-and-angle-means-five-things.md`](../TODO/eight-terms-have-no-definition-and-angle-means-five-things.md).
As each term is settled there, its entry here becomes a statement of what the term
means rather than a survey of what it does, and this file and
[`vocabulary-inventory.md`](vocabulary-inventory.md) converge on one `vocabulary.md`.

⚠ **Line anchors are as of `802a574` and drift.** Every collecting agent found
`SKILL.md`'s anchors had moved one to three lines since the term list was built.
Verify one against the file before acting on it.

⚠⚠ **TWO TERMS HAVE BEEN RETIRED SINCE THE COLLECTION, AND THE QUOTATIONS BELOW PREDATE
THEM.** Every quotation in this file is verbatim as of `802a574`. Where one contains a
retired word, the quotation is a historical record, not a live citation — read it through
this table:

| collected as | now | where |
| --- | --- | --- |
| `sweep` (stage 7b) | **WRITE** | retired as APPLY, then renamed WRITE when APPLY moved to stage 5; see [sweep](#sweep--settled-2026-08-15-not-a-term-stage-7b-is-apply) |
| `EDIT` (stage 5) | **APPLY** | applying a MARK produces the text; `references/apply.md` is now `references/write.md` |
| `angle` (the scope, the agent) | **editorial role** | prose everywhere; see [angle](#angle--settled-2026-08-15-retired-in-favour-of-editorial-role) |
| `--angles` | `--reviewers` | `verdicts.py` |
| `ANGLE FILES` | `REVIEWER FILES` | the dispatch packet |
| `angle` (the variable, the report stem) | `reviewer` | `verdicts.py` |
| `reanchor` | **`move`** | one relocation verdict; the destination is payload |
| `HOME` | **owner** | one stem for the relation and the site it selects |
| `Block.owner` | `Block.anchor` | `census.py`, and the census JSON key with it |

Ruled by Roy 2026-08-15. The term of art is **editorial role**; the identifiers say
**reviewer**, because `role` alone would also cover the task agent and the absent author.

Term list and bundle map: [`vocabulary-inventory.md`](vocabulary-inventory.md).

---

## Bundle 5 — census tiers and language support

### tier

- Stated at `SKILL.md:89-96` — "The model is the tree; the implementation depends on nothing... Both tiers find the same blocks and differ only in what else they can say," followed by a table: `tokenized` needs "a lexer + AST (Python: the stdlib)", answers "blocks, marks, **docstring** owners", cannot answer "a **comment's** owner"; `lexical` needs "a comment-syntax record, nothing else", answers "blocks, marks", cannot answer "any owner; a marker inside an exotic string."
- Stated at `scripts/census.py:1-24` (module docstring) — "The census is built at the TIER available for each file's language. Both tiers find the same blocks; they differ only in what else they can say": `tokenized` = "a lexer + AST (Python, from the stdlib) + DOCSTRING owners"; `lexical` = "a comment-syntax record, nothing else — blocks and marks."
- Stated at `scripts/census.py:300-306` — code comment + dict: "The ladder is named by the QUESTION each rung answers, not by the library that happens to answer it. Only the top rung knows which declaration a block belongs to, which is why ownership-context is the one angle that degrades below it." `TIER_ANSWERS = {"tokenized": "blocks, marks, and DOCSTRING owners", "lexical": "blocks and marks only"}`.
- Stated (mechanism) at `scripts/census.py:858-864`, `tier_for(lang)` — "The highest rung reachable for this language, here and now... One definition, read by the dispatcher and by `--languages`, so what the listing advertises cannot drift from what a run actually does." Body: `return "tokenized" if lang.name == "python" else "lexical"`. **The sole site where tier is decided at runtime**; every other site is prose describing the same two values.
- Stated at `CLAUDE.md:122-131` — same two-row table (needs / answers / cannot-answer) reproduced verbatim in structure.
- Stated at `docs/parsing.md:1-24` — frames tier as one of **two axes, not one ladder**: Axis 1 (FIND, required, deterministic) yields `tier: tokenized` for `.py`, `tier: lexical` for any suffix in `LANGUAGES`; Axis 2 (ENRICH, optional) is explicitly *not* a tier — LSP enrichment adds ownership/liveness but does not change a file's tier. Also: "Tier counts are AGGREGATED over the run, not reported per file. On a polyglot run you cannot tell which file reached which tier."
- Used at `scripts/census.py:189-199` — `Block.tier` field, default `"lexical"`, set per-block at `:880` (`b.tier = tier_for(lang)`). Meaning: a per-block stamp recording which tier produced it.
- Used at `scripts/census.py:867-881`, `census_for()` — dispatches on tier: python → `blocks_stdlib` (tokenized), else → `blocks_lexical` + `flag_structural_docs` (lexical).

**One meaning throughout** — a two-value ladder naming which question set a file's census can answer. Stated at four sites. `docs/parsing.md` alone frames it as one of two orthogonal axes rather than a single ladder; `census.py:858-864` alone is where the value is computed rather than described.

### `tokenized`

- Stated at `SKILL.md:95` — needs "a lexer + AST (Python: the stdlib)"; answers "blocks, marks, **docstring** owners"; cannot answer "a **comment's** owner."
- Stated at `scripts/census.py:23` — "a lexer + AST (Python, from the stdlib) + DOCSTRING owners."
- Stated at `scripts/census.py:304` — `TIER_ANSWERS["tokenized"] = "blocks, marks, and DOCSTRING owners"`.
- Stated at `scripts/census.py:864` — `tier_for` returns `"tokenized"` only when `lang.name == "python"`.
- Stated at `CLAUDE.md:129` — "a lexer + AST (Python, stdlib) | blocks, marks, docstring owners | a comment's owner."
- Used at `scripts/census.py:874-875` — selects `blocks_stdlib(path, text)`, the tokenize+ast implementation.

**One meaning throughout** — the tier reached only by Python, via `tokenize`+`ast`, which additionally resolves docstring owners but never comment owners.

### `lexical`

- Stated at `SKILL.md:96` — needs "a comment-syntax record, nothing else"; answers "blocks, marks"; cannot answer "any owner; a marker inside an exotic string."
- Stated at `scripts/census.py:24` — "a comment-syntax record, nothing else — blocks and marks."
- Stated at `scripts/census.py:305` — `TIER_ANSWERS["lexical"] = "blocks and marks only"`.
- Stated at `scripts/census.py:864` — the fallback branch of `tier_for` for every non-Python language.
- Stated at `CLAUDE.md:130` — "a comment-syntax record, nothing else | blocks, marks | any owner."
- Used at `scripts/census.py:189,199` — `Block.tier`'s default value.
- Used at `scripts/census.py:347-361`, `blocks_lexical()` — "the FLOOR tier," a hand-rolled scanner over `Language.line_comment`/`block_comment`; "It cannot answer OWNERSHIP, so no block gets an owner."
- Used at `docs/parsing.md:91-93` — "The `lexical` tier fakes string-awareness with a hand-rolled quote skipper that is wrong on heredocs, raw strings and template nesting."

**One meaning throughout** across `SKILL.md` / `census.py` / `CLAUDE.md`. `docs/parsing.md` additionally records an implementation weakness (the string-skipper's failure modes) not mentioned where the tier itself is defined.

### the LANGUAGES record (and "adding a language is a data row")

- Stated at `scripts/census.py:234-260`, `class Language` — "What the LEXICAL tier needs to find prose in a language it cannot parse. Adding a language is this record and nothing else — no code — which is the point: the floor has to be cheap enough that a contributor supplies data." **The docstring names "Five fields"; the dataclass declares eight** (`name`, `extensions`, `line_comment`, `block_comment`, `doc_line`, `doc_block`, `doc_is_structural`, `quotes`).
- Stated at `scripts/census.py:265-296` — `LANGUAGES` tuple, eleven rows: python, rust, go, c-family, js-family, ruby, shell, sql, lua, toml-ini, yaml. Comment at `:262-264` — "Ordering inside a field is significant: openers are matched longest-first."
- Stated at `SKILL.md:115-117` — "**Adding a language is a row of data in `LANGUAGES`** — `python <skill>/scripts/census.py --languages` lists what is known. A suffix with no record is **reported as unreviewable, never silently skipped.**"
- Stated at `CLAUDE.md:132-133` — "Adding a language is a data row, not new code."
- Stated at `docs/parsing.md:33-35` — "Adding a language is a row in `LANGUAGES` — data, not code — which is what keeps the floor cheap enough to be worth having."
- Stated at `docs/parsing.md:67-79` — worked (invented) example `Language("zig", (".zig",), ("//",), doc_line=("///",))` — four arguments.
- Used at `scripts/census.py:298` — `BY_EXT = {ext: lang for lang in LANGUAGES for ext in lang.extensions}`, the lookup the tier system keys from.
- Used at `scripts/census.py:904-909` — `--languages` iterates `LANGUAGES` printing `{name, tier_for(lang), extensions}`.
- Used at `scripts/census.py:931-933` — the per-run gate: `language_for(path)` returning `None` appends the path to `unreadable` with note `(no language record for its suffix)`.

**One meaning throughout** for "adding a language is a data row" (four sites agree). Separately: the record's own docstring says "Five fields" while the dataclass declares eight, and the worked examples populate between four and seven per row. Which subset of the eight the count of five refers to is not stated at any site.

### `doc_is_structural`

- Stated at `scripts/census.py:246-248` (`Language` docstring) — "the doc is a string in a declaration's body (Python) or the run above a declaration (Go) — neither is decidable without structure, so this tier reports `comment` and says so."
- Stated at `scripts/census.py:258` — dataclass field, `doc_is_structural: bool = False`.
- Set `True` on three of eleven rows: `:266` python, `:274` go, `:290` ruby. Default `False` on the other eight.
- Used at `scripts/census.py:453-454`, `flag_structural_docs()` — `if not lang.doc_is_structural: return`.
- Used at `scripts/census.py:877-878`, in `census_for()` — `flag_structural_docs(got, text, lang)` is called only in the non-python branch, i.e. only at the lexical tier. Python files take `blocks_stdlib` at `:874-875` and never reach `:878`, so **python's `doc_is_structural=True` is never read by this consumer**, though the field's docstring at `:246` names Python as one of the two languages the concept applies to.

**No stated definition** of that asymmetry — it is visible only by tracing `census_for`'s branching, and is not stated at any site.

### `doc-kind-unresolved`

- Stated at `scripts/census.py:433-475`, `flag_structural_docs()` — "Go and Ruby attach documentation by POSITION... nothing in the text distinguishes it from any other run... the block is marked as an OPEN QUESTION instead." Applied when `block.kind == "comment"` and the next source line (immediately after the run, not the next non-blank one) is non-blank. Note: "NOT counted against the cap. Confirm the kind before compacting."
- Used at `references/compact.md:75-93` — table row: "`comment` with `doc-kind-unresolved` | governed by UNKNOWN — the census could not tell | what this pass may do: nothing. Ask, or carry it at length"; prose at `:89-93` — "A block whose kind is UNRESOLVED is not a block whose kind is `comment`... Do not infer it from the text, and do not cut it: carry it at length and say why. Measured: a three-line Go export doc counted as over a cap of two."
- Used at `docs/parsing.md:81-87` — "The census marks `doc-kind-unresolved` and excludes the block from the cap tally instead. Measured 2026-08-15: without it, a three-line `// Add returns…` run above `func Add` reported `over cap (2): 1`, and `compact.md` routes on KIND, so the cap would have cut an export doc." Same worked example as `compact.md`'s, restated with the measurement date.

**One meaning throughout** — a mark on a `comment`-kind block meaning the lexical tier could not tell whether it is documentation (Go/Ruby position-based convention) or an ordinary comment, exempting the block from cap-cutting in COMPACT.

### `unterminated-block-comment`

- Stated at `scripts/census.py:347-361`, `blocks_lexical()` — "A block opener with no closer swallows every remaining line into one run, so the code below it is censused as prose. That block is STAMPED `unterminated-block-comment` rather than returned looking ordinary: a consumer cannot otherwise tell a long comment from a lexer that lost the rest of the file, and `prove_unchanged.py` refuses the whole file on this mark rather than comparing a residue the code never reached."
- Applied at `scripts/census.py:420-429` — when the scan ends with `in_block is not None`. Note: "UNTERMINATED {opener}: no closing {closer} before end of file, so every line below the opener was swallowed into this run. Code down there was NOT censused as code."
- Used at `scripts/prove_unchanged.py:25-30` — "An UNTERMINATED block comment makes the whole file UNPROVABLE... the residue is merely SHORT — not obviously wrong... this refuses the file on the mark, rather than on a residue that only LOOKS like a proof."
- Used at `scripts/prove_unchanged.py:108-126` — enforced at `:125-126`: `if any("unterminated-block-comment" in b.marks for b in blocks): return None`.

**One meaning throughout** — a mark on the final block of a lexically-scanned file whose block-comment opener was never closed before EOF, meaning everything after the opener was swallowed into that block and the file cannot be residue-proven.

### unreviewable

- Stated at `SKILL.md:115-118` — "A suffix with no record is **reported as unreviewable, never silently skipped.**"
- Stated at `CLAUDE.md:132` — "A language with no record is reported as unreviewable, never silently skipped."
- Used at `scripts/census.py:904-909`, the `--languages` exit path — prints "A suffix not listed is REPORTED as unreviewable, never skipped." The word appears verbatim; **the sentence drops "silently"**, present at both prose sites.
- Used (concept, not the word) at `scripts/census.py:931-933` — the per-run gate for an unknown suffix: the path is appended to a list named `unreadable` with note `(no language record for its suffix)`.
- Used (concept, not the word) at `scripts/census.py:1022-1030` — the printed header for that list at run time is `NOT CHECKED — these are gaps, not passes:`.

**Three labels for one condition.** The word `unreviewable` appears at three sites (`SKILL.md`, `CLAUDE.md`, `--languages` helptext) carrying one meaning: a suffix with no `LANGUAGES` record. The live per-file run never prints that word — the same condition surfaces under the Python identifier `unreadable` and the printed header `NOT CHECKED`. The three labels are not reconciled to each other at any site.

---

## Bundle 9 — proof and residue

### AST proof

- Stated at `scripts/prove_unchanged.py:11` — "Two proofs, because two tiers: `ast` Python. Parse both, blank every docstring, compare `ast.dump`. Comments never reach the AST, so anything else that differs fails." Implemented as the `"ast"` branch of `code_signature`, `:150-176`.
- Used at `SKILL.md:86-87` — "the edits are applied to NODES, so 'never change a line of code' holds by construction — the AST proof in `apply.md` confirms that rather than being the only thing enforcing it." **Names `apply.md` as where the AST proof lives; `apply.md` does not define it** — it invokes `prove_unchanged.py` and describes the output.
- Used at `references/apply.md:52` — "It carries the AST proof for Python, a comment-stripped byte comparison for every other language with a `LANGUAGES` record, and the line-ending check against an untouched sibling." Names one of the two proof kinds the script runs.
- Used at `references/apply.md:118` — "the AST-identity proof and how you ran it."
- Used at `references/compact.md:130` — "No AST-identity proof here — nothing has been written yet. That proof belongs to the sweep (stage 7b)."

**One meaning throughout** — the `ast.dump`-comparison branch of `code_signature` for Python files. **Two surface forms:** "AST proof" (`SKILL.md:87`, `apply.md:52`) and "AST-identity proof" (`apply.md:118`, `compact.md:130`), used interchangeably; no site distinguishes them.

### code signature

- Stated at `scripts/prove_unchanged.py:150-161` — "A value equal for two texts exactly when their executable code matches. ... Returns: `(kind, signature)`. `kind` is 'ast', 'residue' or 'unprovable'; an unprovable file carries an empty signature and must never be reported as proven."
- Used at `scripts/prove_unchanged.py:286-287` — the two calls whose comparison drives PROVEN/FAIL/UNPROVABLE.
- Used throughout `tests/test_prove_unchanged.py` (`:86,92,96,104,110,114,120,124,150-151,159,166,174,180,193,198-199,490`) — exercised directly per language and edge case.
- Used at `tests/test_prove_unchanged.py:445` — "`code_signature` alone cannot catch this: the bug is not in comparing two in-memory strings, it is in how `_show` turns `git show`'s bytes into one." Scopes what the function covers.

**One meaning throughout** — the function and its return value. **Named only in the script and its tests.** The prose reference files (`apply.md`, `residue-check.md`, `SKILL.md`) describe the two proof *kinds* without ever using the identifier "code signature".

### residue — two senses

**Sense A — the comment-stripped byte comparison in `prove_unchanged.py`:**

- Stated at `scripts/prove_unchanged.py:13-15` — "residue: Any language with a `LANGUAGES` record. Delete every comment block the census finds, compare what remains, byte for byte."
- Implemented at `scripts/prove_unchanged.py:101-147`, `_residue(text, path)`.
- Used at `scripts/prove_unchanged.py:27-30` — "the residue is merely SHORT — not obviously wrong, and equal across two files whose code differs."
- Used at `scripts/prove_unchanged.py:115`, `:158`, `:166-176` — the `"residue"` kind and local variable; guards an all-comment file's empty residue from falsely proving identity.
- Used at `scripts/census.py:360` — "mark rather than comparing a residue the code never reached."
- Used at `references/apply.md:52-53` — describes sense A *without using the word*: "a comment-stripped byte comparison for every other language with a `LANGUAGES` record."
- Used throughout `tests/test_prove_unchanged.py` (`:59,71,75-77,115,123,125,143,164-165,170-181,185-199,354`).

**Sense B — THE RESIDUE CHECK, the stage-level procedure:**

- Stated at `references/residue-check.md:1` (title) and `:15-26` — the five-step per-block procedure run at stages 5, 6 and 7b: copy the original block, write the new comment, ask of each original sentence whether it is true & necessary & checkable and absent from the new text, repeat until nothing is missing.
- Used at `SKILL.md:35,608-613` — "Load `references/residue-check.md` before you write anything — the check is defined there... Then emit the replacement and run the residue check on the whole synthesised block once."
- Used at `references/compact.md:64-68` — stage 6's re-application.
- Used at `references/apply.md:10-14` — stage 7b's re-application: "Both are defined in `residue-check.md`... this pass runs the SAME check against the SAME original."
- Used at `references/apply.md:91,102` — "The residue check cannot see any of it, because it only asks what was LOST"; "The residue check is inbound-only."
- Used at `references/review.md:25-28,36-39` — contrastive: "The proof pass is not the residue check. The residue check is inbound and per-block — did this block lose something? This asks does the finished page read?"
- Used at `CLAUDE.md:137`, `docs/limitations.md:37` — listed among per-stage reference files.

**Both senses use the bare word without a disambiguating marker at the point of use.** Which is meant is inferred from context — a lowercase noun alongside `_residue`/`code_signature`/`prove_unchanged.py`, versus "the residue check" as a named procedure tied to `residue-check.md`. No site found uses it where either sense could be read; the two vocabularies do not co-occur in a sentence anywhere.

### THE RESIDUE CHECK

Same sites as residue sense B. Additionally: the file's own title at `references/residue-check.md:1` is "# The RESIDUE CHECK — loaded at stage 5, used at 5, 6 and 7b," stating the stage span directly; `SKILL.md:609` restates that span in prose.

### PROVEN / FAIL / UNPROVABLE / UNCHECKED

- Stated at `scripts/prove_unchanged.py:5,16-18` — "Exits nonzero unless EVERY path is proven... A file this cannot prove is REPORTED as unprovable, never passed. A proof that quietly degrades to 'looks fine' is worse than no proof, because the report still says PROVEN."
- Emitted at `scripts/prove_unchanged.py:270-320`, four literal print prefixes:
  - `UNPROVABLE` at `:276,290` — no `--base:rel` found; or either signature kind is `"unprovable"`
  - `FAIL` at `:282,296,301,318` — read error; proof kind changed between before/after; executable code differs; line-ending mismatch
  - `PROVEN` at `:304` — kinds match and signatures equal
  - `UNCHECKED` at `:308` — no readable untouched sibling for the line-ending check
- Consequences stated at `references/apply.md:57-62` — "A `FAIL` or `UNPROVABLE` line is a stop, not a note... **An `UNCHECKED` line does not stop the run** — it means the line-ending check had no untouched sibling to compare against, not that it passed — but report it verbatim too."
- Used at `tests/test_prove_unchanged.py:144,171,188,317,351,355,378-379,439` — asserts stdout contains these exact strings.

**One meaning throughout** — four literal report-line prefixes emitted by `main()`, consumed as instructions in `apply.md`. `FAIL` and `UNPROVABLE` both increment `failures` (`:262,271,277,283,293,299,302,319,322-323`) and cause nonzero exit; `UNCHECKED` increments a separate `unchecked` counter (`:263,309,325-329`) and does not affect the exit code.

### the line-ending check (dominant ending, untouched sibling)

- Stated at `scripts/prove_unchanged.py:20-23` — "Line endings are checked against an UNTOUCHED SIBLING, never against the stored blob: under `core.autocrlf` the blob is always LF, so normalising to it leaves the working tree inconsistent with every file the sweep did not touch — and `git diff` hides it. Measured four times."
- Implemented at `scripts/prove_unchanged.py:179-185`, `dominant_ending` — "Which line ending this text mostly uses: 'crlf', 'lf' or 'none'."
- Implemented at `scripts/prove_unchanged.py:216-243`, `_sibling` — "A READABLE tracked file beside `target` that this sweep did not edit."
- Applied at `scripts/prove_unchanged.py:306-319` — both sides guarded against `"none"` (`:313-317`): "A single-line file with no trailing newline has no ending to measure, so it reads 'none' and would FAIL against any CRLF sibling — a file whose endings are not wrong, only absent."
- Used at `references/apply.md:52-62`.
- Used at `tests/test_prove_unchanged.py:18,130-136,381-412`.

**One meaning throughout.** Companion function `_read_raw` (`:188-204`) reads a file's own bytes with `newline=""` so `dominant_ending` sees actual endings rather than universal-newline-translated ones; its docstring notes the Python-3.13-only `Path.read_text(newline=...)` pitfall against the shipped 3.9 floor.

### the four refusals

- Named at `references/apply.md:10` — heading "## The residue check, and the four refusals" — and `:12`: "Both are defined in `residue-check.md`, loaded back at stage 5. They are not restated here."
- **The referent in `references/residue-check.md:40-54` is headed differently:** "## ⚠⚠ Four removals the three conjuncts miss" — "Refuse a removal unless **all four** also hold..." followed by four bullet conditions.
- Used at `references/compact.md:61-68` — "⚠ The four refusals still bind... does the condensed version still pass the four refusals (not the only record of its fact; not what makes a surviving claim falsifiable; not a positional refusal aimed at a future editor; and what remains is still a proposition)?" Restates all four inline, compressed relative to `residue-check.md`'s bullets.
- Used at `agents/comment-review-compact.md:23` — "⚠⚠ **The four refusals in `compact.md` bind here without exception.**" **Attributes the term's home to `compact.md`**, not to `residue-check.md` where the four-condition list is defined. `compact.md` itself attributes it onward to `residue-check.md` at its own `:12`, and separately restates the four conditions at `:66-68`.

**The phrase "the four refusals" is not textually present in the file it points to.** `residue-check.md:40-54` names the same list "Four removals" (heading) and "Refuse a removal unless all four also hold" (body). The fixed phrase appears only at the three citing sites (`apply.md:10`, `compact.md:61,66`, `agents/comment-review-compact.md:23`), each treating it as defined elsewhere. A reader assembling it from `residue-check.md` alone has to infer that "refusals" names the four bullets that section calls "removals."

---

## Bundle 2 — the finding record and its fields

### finding

- Stated at `references/reviewer-brief.md:39` — "Every finding is a RECORD, and it is parsed."
- Stated at `references/reviewer-brief.md:97-100` — "A verdict is a recommendation the task agent will combine with the other angles' and synthesise into one comment. It is only usable if it carries its payload, so **a verdict without its payload is not a finding**."
- Used at `scripts/verdicts.py:207-260` (`parse_report`) — a `Finding` dataclass instance built by regex-parsing report text. Existence as a finding here is **purely syntactic** (a `RECORD` block with a decimal `BLOCK`), independent of later admissibility.
- Used at `scripts/verdicts.py:1,18-30` — the thing the gate can catch fabrication of: "a fabricated FINDING" vs "a fabricated CLEAN," which it structurally cannot.
- Used at `SKILL.md:548` — "A finding whose evidence does not resolve is not a finding — except a `query`."
- Used at `SKILL.md:568` — "Two findings quoting the same sentence in different files are ONE finding." Counted/deduplicated conceptually, a step above the per-record sense; the same passage says the join "cannot see this for you."
- Used at `SKILL.md:633` — "THE SENTENCE YOU PROPOSE TO KEEP IS A FINDING YOU HAVE NOT RAISED." An **unraised judgement** about kept text, not a literal RECORD.
- Used at `README.md:132,136,145-146,151-153` — an aggregate counted statistic ("97" findings, a "Findings" column, "one finding in four was worth acting on immediately").

**One meaning at the mechanical/gate level** across brief, `verdicts.py` and `SKILL.md`: real only if it resolves under the gate's checks. `SKILL.md:633` uses it for an unmade judgement; `README.md` uses it as a counted statistic.

### RECORD (the `--- FINDING` block)

- Stated at `references/reviewer-brief.md:39-56` — the worked example, introduced by "Emit findings in exactly this shape."
- Stated at `scripts/verdicts.py:73` — `RECORD = re.compile(r"^---\s*FINDING\s*$(.*?)^---\s*$", re.M | re.S)`. Comment at `:74-79` explains the non-greedy-match failure mode: an unterminated record's opener swallows the next record's fields, silently overwriting them.
- Used at `scripts/verdicts.py:80` (`OPENER`) — a *count* of `--- FINDING` openers regardless of closure, used only to detect that swallow by comparing counts (`:220-229`).
- Used at `scripts/verdicts.py:207-260` — the unit `RECORD.findall(text)` returns.

**One meaning throughout.** Anchor correction: the inventory's `:73-83` should be split — `:73` is the regex, `:74-79` the explanatory comment, `:80` the distinct `OPENER` check.

### VERDICT

- Stated at `references/reviewer-brief.md:61` — "`VERDICT` | one of the nine, and one your LEVEL carries."
- Used at `scripts/verdicts.py:82` — one of eight recognized field names.
- Used at `scripts/verdicts.py:147,242` — `Finding.verdict`, lower-cased at parse time.
- Used at `scripts/verdicts.py:546-553` — checked twice: membership in `VERDICTS`, and `allowed()` for the run's `--level`.
- Used at `SKILL.md:698` — one of five fields surviving into stage 7a; `BLOCK`, `EVIDENCE`, `QUOTE` are dropped there because they "exist only for the join's mechanical checks."

**One meaning throughout.**

### LOCATION

- Stated at `references/reviewer-brief.md:62` — "`file:start-end` of the prose" — where the *prose* sits, contrasted with `EVIDENCE`, where the *code* sits.
- Used at `scripts/verdicts.py:404-416` (`location_problem`) — same `_resolve_lines` machinery as `EVIDENCE` but `allow_range=True`, so `LOCATION` may carry a range. Exempted for `verdict == "clean"` (`:411-412`).
- Used at `scripts/verdicts.py:319-333` — "only LOCATION may carry `file:start-end`" — the range distinction is enforced here, not merely stated in prose.
- Used at `SKILL.md:698` — shown to the human at 7a.
- Used at `SKILL.md:571` — "`contradictions()` keys on the census BLOCK index," clarifying that two findings citing the same `LOCATION` in different files are **not** merged, because the join never reasons over `LOCATION` text.

**One meaning throughout.**

### EVIDENCE

- Stated at `references/reviewer-brief.md:63` — "`file:line` you opened to settle the claim — **verified to exist**." Single line, contrasted with `LOCATION`'s permitted range.
- Used at `scripts/verdicts.py:362-401` — `_resolve_lines(..., allow_range=False)` at `:383`; exempted for `clean` and `query` at `:381-382`, matching the brief's "`query` carries no EVIDENCE... by construction" (`reviewer-brief.md:165-168`).
- Used at `scripts/verdicts.py:394-400` — anchors the window `QUOTE` is searched within.
- Used at `SKILL.md:543-546` — restates the `query` exemption.
- **Not shown at 7a** — absent from `SKILL.md:698`'s five fields.

**One meaning throughout.**

### QUOTE

- Stated at `references/reviewer-brief.md:64` — "the text at that line, **VERBATIM** and at least 12 characters. Required for every verdict except `clean` and `query`."
- Stated at `references/reviewer-brief.md:79-83` — "`QUOTE` is the forcing function, and it is CHECKED. The cited line is read out of the file and your `QUOTE` must appear within three lines of it." With the measured motivation: "one graded run had fabricated 5 of its 7 reviewer reports, and a self-certified confidence label ran at 97% across 298 findings."
- Used at `scripts/verdicts.py:386-400` — whitespace-normalized needle; empty, shorter than `MIN_NEEDLE`, or `needle[:40].lower()` not found within `EVIDENCE_WINDOW` lines are each a distinct rejection.
- Used at `agents/comment-review-block-context.md:64-68` — narrowed to a specific instance: "Report the enforcing line as your `QUOTE`" for a numeric/boundary constraint.
- Used at `SKILL.md:543-546`.

**One meaning throughout.**

### SUMMARY (left half quoted, right half DERIVED)

- Stated at `references/reviewer-brief.md:65` — "the claim as written, quoted `||` what you DERIVED from the evidence."
- Stated at `references/reviewer-brief.md:69-71` — "For a count, give the number **and the population you counted over** in `SUMMARY`'s right half... a count with no stated population cannot be re-derived."
- Stated at `references/reviewer-brief.md:85-88` — "`SUMMARY`'s right half is DERIVED, and is not checked verbatim... checking the derived statement against the code made every counted claim inadmissible: the block-context angle's own category, refused by the gate."
- Used at `scripts/verdicts.py:369,392-393` — **the only mechanical check on `SUMMARY` is that the right half is non-empty.** The left half is parsed but never verified against any file.

**One meaning throughout**, with the split explicit at every site.

### FINDING (the field)

- Stated at `references/reviewer-brief.md:66` — "what is wrong, one clause." **One stated site, no restatement anywhere.**
- Used at `scripts/verdicts.py:135-153` — parsed at `:247` and stored. **The dataclass is also named `Finding`** — the record-level Python type and the field share the name. `_malformed` (`:161-178`) maps its `why` parameter into `finding=why`, so **`Finding.finding` carries two different kinds of text** depending on whether `block == -1` (a diagnostic string) or a real block (the reviewer's clause).
- **Never independently validated** — no function in `main()` checks this field's content or non-emptiness for a well-formed record; only `CHANGE` is payload-checked.
- Used at `SKILL.md:698` — shown at 7a.

### CHANGE

- Stated at `references/reviewer-brief.md:67` — "the payload the verdict table requires."
- Used at `scripts/verdicts.py:283-316` (`payload_problem`) — checked per verdict: `query` must match `QUERY_ATTEMPTED` and `QUERY_SETTLES` (`:291-298`); `correct` must contain both `"false:"` and `"true:"` (`:299-300`); `add` must contain `"anchor"`, `"above"` or `"below"` (`:301-307`); `move` must contain `"->"` or `" to "` (`:308-309`); `reanchor` non-empty (`:310-311`); `split` must contain a `"/"` (`:312-313`); every other non-`clean` verdict non-empty (`:314-315`).
- Used at `scripts/verdicts.py:125-132` — for `query`, `CHANGE` is where the forcing function relocates: "the forcing function has to land somewhere else, and it lands on the PAYLOAD" (`:105-108`).
- Used at `SKILL.md:698`, and per `:704-706` this is also the literal replacement text the author approves and 7b applies verbatim for `correct`/`patch`/`add`.

**One meaning throughout.**

### BLOCK (the census-index field)

- Stated at `references/reviewer-brief.md:60` — "the census INDEX. This is how coverage is checked; a finding without it is unattributable."
- Stated at `references/reviewer-brief.md:35-37,90-93` — "Every census index must appear exactly once across your findings and your clean ranges."
- Used at `scripts/verdicts.py:236-252` — must be `.isdecimal()` or the record is `_malformed(angle, "a record with no BLOCK index")`.
- Used at `scripts/verdicts.py:263-275` (`coverage_gaps`), `:419-428` (`contradictions`), `:539-545,579-583` (range check and STANDS UNCHANGED).
- Used at `SKILL.md:571` — "`contradictions()` keys on the census BLOCK index, and the same sentence copied into two files is two different blocks it can never relate."

**One meaning throughout** at the sites owned here: a 1-based integer index, the sole key the join reasons over. Adjacent and distinct: `agents/comment-review-block-context.md:7` uses "BLOCK-CONTEXT" as an angle name; "block" as the census unit belongs to bundle 4.

### the CLEAN range line

- Stated at `references/reviewer-brief.md:73-77` — "account for every remaining block on one line: `CLEAN 1-16,18,20-45,47`".
- Stated at `references/reviewer-brief.md:90-93` — "`CLEAN` is a range list, not an invitation to skip... The join reports any index you did not account for as a COVERAGE GAP against your angle by name."
- Used at `scripts/verdicts.py:89` — `CLEAN_LINE` uses `[ \t]` rather than `\s`, per the comment at `:84-88`, to stop a wrapped `CLEAN` line's greedy match swallowing a following line into its range ("1-9" + "50" parsing as "1-950"), "because a wrapped CLEAN line must fail LOUD (an unaccounted block is a coverage gap) rather than SILENT (a false clean)."
- Used at `scripts/verdicts.py:181-204` (`_expand`) — unparseable parts (reversed ranges `"9-2"`, below-floor `"0-3"`) are collected as `bad` and returned, never silently dropped or admitted.
- Used at `scripts/verdicts.py:254-259` — each unparseable fragment becomes a `_malformed` finding.

**One meaning throughout.**

### EVIDENCE_WINDOW / MIN_NEEDLE

- Stated at `scripts/verdicts.py:95-98` — `EVIDENCE_WINDOW = 3`: "How far from the cited line the quoted text may sit. Prose wraps and code moves; a hard equality would reject honest citations, and a wide window would accept a fabricated one."
- Stated at `scripts/verdicts.py:100-103` — `MIN_NEEDLE = 12`: "A needle shorter than this could match almost any file by accident... The forcing function only forces if the quote is long enough to have required reading the line."
- **No stated definition under these names in prose.** The brief states the same two numbers without naming the constants: `reviewer-brief.md:64` ("at least 12 characters") and `:79-81` ("within three lines of it").
- Used at `scripts/verdicts.py:390-397`.

**One meaning throughout**; the same rule is stated in prose under no formal name and enforced in code under a named constant.

### CODE CONCERNS

- Stated at `references/reviewer-brief.md:249-262` — "Code problems get **one line each** in a separate `CODE CONCERNS` section at the end, with no verdict," followed by a table pairing each COMMENT finding with its corresponding CODE finding.
- Used at `agents/comment-review-function-context.md:29` — "Report the prose, name the split in `CODE CONCERNS`."
- Used at `agents/comment-review-function-context.md:79` — "Proposing *'make this a hard check'* is a behaviour change: name it in `CODE CONCERNS`, leave the prose..."
- **Absent from `verdicts.py` entirely** — not in the `FIELD` regex, not parsed, not gated.

**One meaning throughout:** an out-of-band, unchecked section outside the RECORD format and outside the join.

### coverage gap

- Stated at `references/reviewer-brief.md:92` — "The join reports any index you did not account for as a COVERAGE GAP against your angle by name."
- Stated at `scripts/verdicts.py:1-18` — listed as a mechanical check; `:18` "Exits nonzero on a coverage gap or an unverifiable citation."
- Used at `scripts/verdicts.py:88`, `:263-275` (`coverage_gaps`, docstring "A gap is not a pass"), `:524-532` (printed as "COVERAGE GAPS — a block nobody mentioned is a gap, not a pass:").
- Used at `SKILL.md:535`; `tests/test_verdicts.py:538,542`.

**One meaning throughout**, always fatal, always framed as "not a pass."

### admissible / admissibility

- Stated at `scripts/verdicts.py:22-23` — "It cannot tell a correct verdict from an incorrect one. It tells you which findings are ADMISSIBLE."
- Stated at `SKILL.md:560-561` — "The tool rules on ADMISSIBILITY, not on truth... Synthesis, and the order below, remain yours."
- Used at `scripts/verdicts.py:324` — "both are inadmissible on exactly the same grounds."
- Used at `scripts/verdicts.py:372` and `references/reviewer-brief.md:88` — **design-rationale usage**, a hypothetical: checking `SUMMARY`'s right half against code "made every counted claim structurally inadmissible."
- Used at `scripts/verdicts.py:408` — **historical usage**: "A fabricated prose location used to be admissible while a fabricated citation was not."
- Used at `scripts/verdicts.py:602,606` — the live terminal message: "Every finding is admissible. Stage 5 may rule."
- Used at `README.md:140` — names `verdicts.py`'s checks collectively as "an admissibility gate."

**One meaning throughout** — passes the gate's mechanical checks — repeatedly contrasted with "true" or "correct." Three registers of use: live check outcome, design rationale, and historical description of a closed gap.

---

## Bundle 11 — concepts belonging to individual editorial roles

Anchor drift from the inventory is noted per term.

### HOME — three senses

- Stated at `agents/comment-review-ownership-context.md:60-65` — "Where the same proposition appears at several sites, name which site is its HOME — **the correct existing anchor point among the sites where the claim is already stated, not the function that implements the rule** — and `drop` the rest, or `reanchor` the claim to that home." (Inventory said `:60-69`; the definition is `:60-65`, `:67-69` is the module-context split note.)
- Stated at `references/reviewer-brief.md:277` — table row: `ownership-context` asks "which of these sites is this claim's HOME?", verdict shape "`reanchor` the claim to its owner, `drop` the copies." (Inventory said `:278-282`.)
- Used at `agents/comment-review-ownership-context.md:58` — lowercase: "A block that would be equally useful anywhere in the file is not anchored to anything, and its home is **the declaration it actually constrains**."
- Used at `references/reviewer-brief.md:280-281` — "A claim with a home in the wrong place is `ownership-context`'s; a rule with no home in the CODE is `module-context`'s."
- Used at `references/reviewer-brief.md:120` — the destination of a relocation.
- Used at `agents/comment-review-function-context.md:119` — "where that angle names a home outside it, that one governs."
- Used at `README.md:70`.

**Three senses coexist.** At `:60-65` HOME is **an existing site among those where the claim is already written**, and the file explicitly rules out "the function that implements the rule." At `:58` a block's home is **the declaration it constrains**, which need not be a site where the claim already appears. At `reviewer-brief.md:281` "a rule with no home in the CODE" means **a function that would hold the rule** — the thing `:63` says HOME is not. Nothing at any site cross-references the others on this point.

### owning function

- Stated at `agents/comment-review-module-context.md:71-82` — "The same rule explained across several modules usually means **the rule has no owning function**... NAME THE OWNER — the function that produces the artifact the rule constrains. A width budget is owned by the function that composes the text; a unit by the function that returns the number; an ordering by the function that sorts."
- Stated at `references/reviewer-brief.md:278` — table row: "does the rule have no OWNING FUNCTION, so each site re-explains it?" (Inventory said `:279`.)
- Used at `agents/comment-review-module-context.md:3`.
- Used at `references/compact.md:107-110` — the same diagnosis reached at COMPACT rather than MARK: "A block that cannot be made both correct and short is a finding about the CODE — usually a rule with no owning function... Report it, name the owner if you can see one, and leave it." **Not in the inventory.**
- Used at `references/reviewer-brief.md:260` — the phrase appears as "the rule needs an owning **type**", not function, in the COMMENT-vs-CODE table. **Not in the inventory.**
- Used at `README.md:100-101`.

**One meaning throughout** — the function (at `reviewer-brief.md:260`, the *type*) that produces the artifact the rule constrains.

### module-level state

- Stated at `agents/comment-review-module-context.md:65-69` — "For each module-level mutable binding, ask whether the docstring says **who writes it, when, and what depends on it having been written**. Import-order dependencies and caches are the shapes that break silently — an undocumented one is `add`, not `clean`." (Inventory said `:67-70`.)
- Used at `agents/comment-review-module-context.md:3`; `README.md:96-97` (worded "the module's mutable state").

**One meaning throughout.**

### reachability

- Stated at `agents/comment-review-function-context.md:32-36` — "Does the constant have a reader? Does the function have a caller **outside the tests**?... a function with thirty references, all of them under `tests/`, is not 'widely used'."
- Used at `agents/comment-review-function-context.md:3`; `README.md:87` (without the term).

**One meaning throughout.** The definition covers two things — a *constant with a reader* and a *function with a caller* — while the gloss used everywhere else names only the function case. The word appears at only the two function-context sites; `census.py:859` ("reachable for this language") and `SKILL.md:200` ("The cap is reachable again") use "reachable" in unrelated senses.

### the running-commentary read (SEQUENCES vs CONSTRAINS)

- Stated at `agents/comment-review-function-context.md:104-110` — "**A comment that SEQUENCES rather than CONSTRAINS is a finding** (*'now I need to…'*, *'then we…'*): a constraining comment goes visibly wrong if its line moves, a sequencing one goes nowhere, because it was never about the line. Read a body's comments in order — a run of them narrates what the function actually does, and if that is more than the name claims, the docstring is describing the first few lines only." (Inventory said `:105-116`; `:112-116` is a **separate** heading, "Comments in the body are read IN ORDER," stating a different rule.)
- Used at `agents/comment-review-function-context.md:3` — **the ordering half only**; the frontmatter does not carry the SEQUENCES-vs-CONSTRAINS test.
- Used at `README.md:44-45`, `:86` — **the ordering half only**.

The section carries two ideas: (a) a *test* — does the comment constrain its line or merely narrate sequence; (b) a *reading procedure* — read body comments in order against the docstring and name. **Only (b) reaches the frontmatter and README**; (a) is stated in the agent body and nowhere else.

### state / constraint / worked example

- Stated at `agents/comment-review-block-context.md:18-24` — "**State** — does it describe the program as it is NOW... **Constraint** — does it state the bound the code enforces, on every axis under *A constraint is checked against the code that enforces it*. Stated loosely it is wrong, not vague: *'must be positive'* against `if x > 10` is a finding. **Worked example** — does the example still produce what it claims. Run it."
- Stated at `CLAUDE.md:112-114`; `README.md:42-43`.
- Expanded at `README.md:72-81` — the same three unrolled into **five** bullets, adding quantified/exclusivity claims and cited paths/guards.
- Used at `agents/comment-review-block-context.md:3` — names the three, then **adds** quantified/exclusivity claims and cited paths/guards.
- Elaborated at `agents/comment-review-block-context.md:64-68` (the four constraint axes: VALUE, DIRECTION, UNITS, boundary), `:77-83` (a worked example is executed, never read; unrunnable from the checkout is `query`, not `clean`), `:88-90`, `:92-97`.
- Used at `SKILL.md:464` — the angle's one-liner; the three kinds are not named.

**One meaning per kind throughout.** What varies is the **enumeration's completeness**: the agent body says the three are the whole scope ("You rule on the three kinds above, nothing else," `:88-89`) while the same file's frontmatter and its `:47-62` and `:70-75` sections assign two more. `CLAUDE.md` and `README.md:42-43` list three; `README.md:72-81` lists five.

Separately, "constraint" is used in the ordinary English sense at `reviewer-brief.md:109,111`, `SKILL.md:55,127`, `agents/comment-review-ownership-context.md:51,58,74`, `compact.md:45`, `CLAUDE.md:154` ("Shipped-code constraint"). The claim-kind sense is carried only where the triple appears together.

### label — three senses (the inventory recorded two)

**Sense A — acquittal label.**

- Stated at `references/reviewer-brief.md:215` — "**`label`** — one or two lines naming the line it sits on, claiming nothing else." One of five entries under "The acquittal list — the ONLY reasons to pass a block over" (`:211-226`). (Inventory said `:216`.)
- Used at `agents/comment-review-module-context.md:100` — "**Return `clean` and name the reason as 'outside my angle'** rather than reaching for a substantive acquittal label."
- Used at `agents/comment-review-module-context.md:111` — "a plausible label on any of them."

**Within sense A, a further split:** `reviewer-brief.md:215` uses `label` as the name of **one specific acquittal**; `module-context.md:100,111` use it as the **generic word for any acquittal-list entry** (the label at `:109` is `derivation`). Both readings sit adjacent on the same list; nothing distinguishes them.

**Sense B — review-round label.**

- Stated at `agents/comment-review-block-context.md:28-29` — "Dated rulings, review-round labels (*'fix round 2'*, *'finding B4'*)..."
- Detected at `scripts/census.py:161-164` — the `NARRATIVE` key `"a review label"`, matching `fix (wave|round)`, `finding [A-Z]?\d`, `review finding`, `round \d`, `CRITICAL [A-Z0-9]`.
- Used at `agents/comment-review-block-context.md:3`; `SKILL.md:509`; `README.md:74`.

**Senses A and B are opposite in consequence:** an acquittal label is a reason to **pass a block over**; a review-round label is a reason to **flag it**.

**Sense C — the narrative-class name, in code.**

- Used at `scripts/census.py:848,854` — loop variable `label` over `NARRATIVE.items()`, holding class names `"a date"`, `"a review label"`, `"a retraction"`, `"a rejected alternative"`, emitted into `block.notes`. The string it holds is **sometimes itself sense B**.

**Adjacent, distinct uses (recorded, not claimed as senses):** `reviewer-brief.md:82` and `README.md:216` — a reviewer's self-reported confidence marker. `reviewer-brief.md:116` — "mislabelling one as the other" (verdict misassignment). `run_context.py:210` — packet-line syntax ("bare, bulleted, or labelled"). `evals/generator_split.py:124`, `scripts/README.md:36`, `tests/*` — authorship-classification and test-output senses.

### banner / section banner

**No stated definition.** No site says what a banner is.

- Used at `agents/comment-review-module-context.md:3` — an object of module-context's reading, and a finding shape ("banners reading as chapter breaks").
- Used at `agents/comment-review-module-context.md:18` — "Read the module docstring, the section banners, and the top-of-file commentary."
- Used at `agents/comment-review-module-context.md:24` — the finding shape: "section banners reading like chapter breaks in a book rather than parts of one argument."
- Used at `agents/comment-review-module-context.md:98` — "You are scoped to a small slice — module docstrings, banners, top-of-file prose."

One sense throughout, inferrable but never stated: a comment block that titles or divides a section of a file. A reader must infer that a banner is (a) a comment, (b) within the file body rather than at the top, (c) serving as a divider — none of which is written. The `:24` finding rule presupposes the reader can identify one.

**The term appears in no other file in the live tree** — not `SKILL.md`, not `reviewer-brief.md`, not `census.py` (there is no banner mark or detector), not `README.md`. The inventory recorded `README.md:93` as a paraphrase; that line now reads "Is the module/package level documentation one set of ideas, not several unrelated subjects," which paraphrases the *multi-subject* finding, not the banner one.

### assessability gate

**No stated definition.** The phrase appears exactly once and is never explained.

- Used at `agents/comment-review-ownership-context.md:3` — "Decides whether a block is truthy where it sits (**the assessability gate the other three angles' verdicts depend on**)."

The idea is stated in the same file **without the phrase**:

- `agents/comment-review-ownership-context.md:23-28` — "A claim attached to the wrong scope gets measured against the wrong code — a comment about `parse()` sitting above `render()` is checked against `render()`, found false, and CORRECTED into a falsehood. **Your verdict decides which code the other three read.**"
- `agents/comment-review-ownership-context.md:30-38` — the gate as two ordered questions: would this be TRUTHY where it sits; and if it were in the right place, would it be truthy THERE.
- `agents/comment-review-ownership-context.md:40-41` — "You do not rule on whether the claim is TRUE... **You rule on whether truth is assessable here at all.**" The only other occurrence of the word-stem.

(Inventory said `:30-42`; it is `:30-41`, and `:23-28` carries the causal half.)

Two further sites state the dependency without the phrase or the word: `SKILL.md:190-192` and `README.md:59-61`. The term `truthy` that the gate turns on **is** stated, at `reviewer-brief.md:173-180`.

A reader meeting "the assessability gate" in frontmatter must infer it names the `:30-41` procedure; nothing links the two except adjacency in one file.

### acquittal rate

**No stated definition.** Used as a measured quantity; no script computes it.

- Used at `agents/comment-review-module-context.md:96` — "⚠⚠ Your acquittal rate will run high, and that is a trap," explained by scope at `:98-100`.
- Used at `agents/comment-review-module-context.md:109` — "Measured: a coherence reviewer facing 548 blocks it was not reading for filed them as `derivation`, **publishing a 95% acquittal rate** and corrupting the summary." (Inventory said `:110`.)

Both uses carry the same sense but **neither states a denominator**. At `:96` the rate runs high legitimately, and the instructed response is `clean` with the reason "outside my angle" (`:99-100`). At `:109` a 95% figure is a corruption — the same blocks filed under a substantive acquittal. A reader must infer whether "clean — outside my angle" counts toward the rate; neither site says, and the distinction between the legitimate high rate and the corrupt one turns on it. `:102-106` adds that inventing a tenth verdict word is forbidden, because "a block stands unchanged only when every angle that RAN returned `clean`, and a word outside the nine counts as neither."

The term appears nowhere else in the live tree; `verdicts.py` computes no such statistic (its clean-arithmetic at `:576-583` is a per-block STANDS UNCHANGED determination, not a rate).

---

## Bundle 1 — the eight verdicts and their payloads

⚠ **SETTLED 2026-08-15: `reanchor` collapsed into `move`, so there are eight, not nine.**
Ruled by Roy. A relocation is ONE judgment — whether the prose belongs ten lines down,
in another file, or out of the code entirely is the DESTINATION, which the payload already
carries, and the reason it belongs there is `FINDING`, which every record already has.
The split was encoding in a second verdict word what the record has fields for.
**Availability and synthesis order now key on the destination:** only a destination outside
the code can be ruled unavailable at 1.4, and only such a `move` is applied at synthesis
step 2; a relocation inside the code is always available and waits until step 6. That is
what removed the measured loss recorded below, rather than warning about it.
Quotations below predate the collapse.

Anchors shifted since the scout pass: brief "clean is scoped to YOU" now `:138-142`; "reach by NOT deciding" `:144-147`; `CLAUDE.md` per-angle bullet `:202-206`; function-context clean `:122-125`; ownership-context clean `:92-97`, reanchor-vs-move `:71-84`; `SKILL.md` MOVE DESTINATION `:249-260`, clean-arithmetic `:604-606`, contradiction `:624-629`, laundering `:63-66`; brief query section `:149-168`; `verdicts.py` clean-arithmetic `:575-587`.

### `clean` — eight sites state something about it

- **`SKILL.md:48`** (to the task agent) — "nothing to report **from this angle** … nothing. Not a pass, and not a claim the block is correct — it is one angle having no finding, **including when the block is outside what that angle reads**." A null input to synthesis, defined by what it does *not* license.
- **`references/reviewer-brief.md:104`** (to reviewers) — "nothing to report FROM YOUR ANGLE"; payload "nothing — **name your angle**, nothing else." An emission obligation.
- **`CLAUDE.md:202-206`** (to whoever edits the repo) — "`clean` is reserved, not a synonym for 'vaguely good' … each angle's `clean` asserts something specific — read what, in that angle's own file." Defines `clean` only by deferral.
- **`agents/comment-review-ownership-context.md:92-97`** — "**EVERY SENTENCE in the block belongs to the line it sits on** — each is about that code, no other site states it, and someone changing that code would decide worse without it. A block whose sentences belong to different code is `split`, not `clean`." Three conjuncts.
- **`agents/comment-review-block-context.md:92-97`** — "**EVERY SENTENCE in the block is true of the code beside it**… A block holding one true sentence and one false one is not `clean`: the false sentence is `correct`, the true one is `clean`. Two sentences, two verdicts."
- **`agents/comment-review-function-context.md:122-125`** — "**name, signature, docstring, comments and body agree, and nothing the signature cannot express is missing from the prose**." One sentence, no per-sentence decomposition.
- **`agents/comment-review-module-context.md:113-115`** — "**the module docstring accounts for the exposed surface and reads as one set of ideas** — you enumerated the surface and walked it. `clean` because a block is outside your angle is a **different statement**, and must name that reason." The only angle file splitting `clean` into two assertions under one word.

Further senses:

- `SKILL.md:198`, `:252-253`; `reviewer-brief.md:123-125` — **a destination for a converted verdict.** "its blocks become `clean`, never `drop`." A real `move` finding existed and is relabelled; the brief states the same as a loss: an in-file relocation called `move` "gets it converted to `clean` and the finding is LOST."
- `reviewer-brief.md:131-136` — what a reviewer must emit when its level lacks the right verdict. For block/function/module-context a true-but-misplaced block is `clean`; for ownership-context the same shape is `query`.
- `reviewer-brief.md:138-142` — "Nothing you emit can bless a block; only a `clean` from every angle that ran can, and **the task agent computes that — you do not assert it**."
- `reviewer-brief.md:144-147` — the only verdict reachable by inaction: "a block left alone is indistinguishable from a block checked and acquitted."
- `reviewer-brief.md:162-163` — "`clean` certifies; `query` asks."
- `reviewer-brief.md:170-171` — sentence-scoped: "a single `clean` sentence must not launder the ones around it."
- `SKILL.md:620` — precedence: "Any `correct` outranks every `clean`."
- `SKILL.md:653` — run-level outcome quality: "A run that returns mostly `clean` is a good outcome."
- `SKILL.md:700` — a report count category ("raised / clean").
- `verdicts.py:314` — the only verdict permitted to carry no payload; `:376,381,411` — exempt from EVIDENCE/QUOTE and LOCATION checks; `:581` — operationally the verdict that does **not** put a block into `ruled`.
- `verdicts.py:26-30,114` — the fabrication leaving no artifact ("a fabricated CLEAN").

**Non-verdict uses of the word** (recorded, not judged; `CLAUDE.md:202` states a repo rule against these): `residue-check.md:54` ("the check reports clean"), `:43` ("cleanly"); `README.md:225,28`; `docs/parsing.md:26` ("a clean fallback"); `census.py:677,920`; `grade_hazards.py:20`; `tests/test_referrers.py:155`; `scripts/README.md:36`; and `--clean` as a `fetch_corpora.py` CLI flag (`CLAUDE.md:29`, `scripts/README.md:14`).

### `query`

- **`SKILL.md:49`** — "unsettled | resolve it or escalate it. **It blocks every other verdict on that sentence**."
- **`reviewer-brief.md:105`** — payload is "the claim, the check you ATTEMPTED, and what WOULD settle it — the ATTEMPTED and WOULD-settle halves are **CHECKED (as shape, not as truth)**; the claim itself is checked by nothing."
- `reviewer-brief.md:149-160` — "for a claim you could not settle — **not one you did not try to settle**." Three shapes: outside your angle / outside the checkout / outside the code, the third reaching the author at 7a.
- `reviewer-brief.md:165-168` — carries no `EVIDENCE` and no `QUOTE` by construction; its `CHANGE` is what the gate reads.
- `agents/comment-review-ownership-context.md:76-77,83-84` — the substitute for `reanchor` at `fact-check`; **a `query` carrying a placement destination.**
- `agents/comment-review-block-context.md:83` — the verdict for a worked example that cannot be executed from the checkout.
- `SKILL.md:165` — what a meaning-change without evidence must become; `:277` — what a wrong style sheet is; `:542-546` — the one verdict the citation check does not touch; `:594` — synthesis step 1.
- Non-verdict sense at `scripts/README.md:52` (a GitHub search query).

### `drop`

- **`SKILL.md:50`** — "**true** but not worth keeping | delete the sentence."
- **`reviewer-brief.md:106`** — "the sentence should not exist at all"; payload "the sentence, **verbatim**."

`SKILL.md:50` scopes `drop` to sentences that are TRUE; the brief states only that the sentence should not exist. `SKILL.md:583-586` closes the gap from the other side: "The matrix only runs on sentences you have already established are TRUE."

- `SKILL.md:581` — **two distinct grounds, one word**: *checkable + not necessary* ("narrates what the code already says") and *not checkable + not necessary* ("history").
- `SKILL.md:565` — the wrong routing for a block ending mid-clause, overridden to `correct`; `:596` — synthesis step 2; `:253` — the forbidden disposal when `move` is unavailable.
- `agents/comment-review-ownership-context.md:38,64-65,71` — what a misplaced-but-relocatable block is **not**; and what the non-home copies of a multi-sited claim are.
- `agents/comment-review-block-context.md:38,90`; `agents/comment-review-module-context.md:56`.
- `verdicts.py:12,419-428` — one half of the contradiction pair.
- Non-verdict: `verdicts.py:182-188`, `docs/parsing.md:112`, `apply.md:113`.

### `correct`

- **`SKILL.md:51`** — "**FALSE** | apply the true/false pair. **Always before any `patch`**." `:63-66` — "`correct` says the sentence is wrong; `patch` says it is right and reads badly."
- **`reviewer-brief.md:107`** — payload "the false clause **and** the true one, **plus the line that settles it**." `:114-118` — "If you are unsure which applies, you have not settled the claim — that is `query`."

**Payload component count differs across three sites:** the brief names three (false clause, true clause, settling line); `SKILL.md:68` names one ("carries a pair"); `verdicts.py:299-300` checks two (`"false:"` and `"true:"` present in `CHANGE`). The settling line is checked separately as `EVIDENCE`/`QUOTE`, not as part of this payload.

- `SKILL.md:563-566` — mandated for a block ending mid-clause, overriding the matrix; `:584`; `:599` — synthesis step 3; `:620`; `:622`; `:624-629` — contradiction partner.
- `reviewer-brief.md:180`; `:205-209` — the verdict for an unparseable-but-resolving citation, "never `drop`".
- `apply.md:41-43` — "**A `correct` on a claim inside a string literal is REPORTED, never applied**."
- **Ordinary-adjective sense** (a state a block reaches at the end of stage 5, not a ruling): `apply.md:23,28`; `compact.md:27,40,44`; `residue-check.md:25`; `SKILL.md:673,676`; `README.md:86,122,224`; `evals/discriminators.md:38`; `grade_hazards.py:18,57,116`; `tests/test_run_context.py:136`.

### `patch`

- **`SKILL.md:52`** — "**TRUE**, badly worded | apply the rewrite."
- **`reviewer-brief.md:108`** — payload "the rewrite."
- `SKILL.md:187` — the verdict `full` adds and no lower level carries; `:600` — synthesis step 4, "⚠ Never before step 3"; `:622,624-629`; `:633-634`.
- `review.md:34` — a better wording found at stage 8 becomes "next run's `patch`".
- `agents/comment-review-module-context.md:41-42`.
- **Different sense**: `unittest.mock.patch` at `tests/test_census_names.py:7,158,162,170`, `tests/test_referrers.py:194-195`.

### `add`

- **`SKILL.md:53`** — "missing entirely | insert the text at the anchor named with it."
- **`reviewer-brief.md:109`** — "a **constraint** exists in code and nowhere in prose"; payload "the text **and its anchor** — which declaration, above or below."

**Scope differs.** `SKILL.md:53` says "missing entirely" without saying missing *what*; the brief restricts the trigger to a **constraint**. The angle files widen it: `module-context.md:55` (an unaccounted name in the module surface), `:69` (undocumented module-level state), `:81` (a rule with no owning function); `function-context.md:82` (four absence-question shapes); `ownership-context.md:49-52` (a non-obvious constraint with no comment). Whether "missing entirely" covers the module-surface and module-state cases, which are not constraints, is not stated.

- `SKILL.md:186`; `:601` — synthesis step 5; `review.md:16`; `apply.md:103`.

### `move`

- **`SKILL.md:54`** — "true, and **not code's to hold at all** | extract verbatim OUT of the code, to the destination resolved at 1.4."
- **`reviewer-brief.md:110`** — payload "the destination **and** the verbatim extract."

`SKILL.md:69` restates the payload as "a source and destination"; `verdicts.py:308-309` checks only for `"->"` or `" to "` in `CHANGE`.

- `SKILL.md:581` — the matrix routing for *not checkable + necessary*, "real rationale, unverifiable in place."
- `SKILL.md:596`; `:618` — one of two placement verdicts ownership-context governs; `:648-649` — "**`move` has no truth check on its path** — 'write the destination verbatim' copies a falsehood somewhere harder to find."
- `SKILL.md:564`; `:691`; `compact.md:17`; `review.md:18-19`; `apply.md:74-76` ("**Extract before you cut**").
- `agents/comment-review-ownership-context.md:79-84` — the word the ownership reviewer is told **not** to use for an in-file relocation.
- **Non-verdict sense**: `docs/parsing.md:67` ("The legitimate **move** on an unknown language is to propose a `LANGUAGES` row").

### `reanchor`

- **`SKILL.md:55`** — "true and code's to hold, but **attached to the wrong line** | re-attach the block, unchanged, to the declaration it constrains **in the same file**." `:58-61` — "1.4 never withholds it."
- **`reviewer-brief.md:111`** — payload "the declaration it constrains, **in this file**." (`verdicts.py:310-311` checks only non-emptiness.) `:120-125` — "`move` leaves the code; `reanchor` stays in the file… at `fact-check` the verdict set carries no `reanchor` and the same finding is `query` instead, never `clean`."
- `agents/comment-review-ownership-context.md:71-84` — "The finding is where it BELONGS, not that it is misplaced."
- `agents/comment-review-function-context.md:112-120` — **a line inside this function**, for a body comment describing a step performed elsewhere; explicitly subordinate: "where that angle names a home outside it, that one governs."
- `SKILL.md:597` — "`reanchor` does NOT belong here: it removes nothing"; `:602-603` — synthesis step 6; `:618`.

### `split`

- **`SKILL.md:56`** — "two claims in one block."
- **`reviewer-brief.md:112`** — "one block holds **two unrelated notes**"; payload "each fragment **and its own anchor**."
- **`agents/comment-review-ownership-context.md:96-97`** — a third framing: "A block whose **sentences belong to different code** is `split`, not `clean`" — the trigger is divergent ownership rather than unrelatedness or count.
- `verdicts.py:312-313` — payload checked as `change.count("/") >= 1`.
- **Different senses**: "the split" as the ownership/module division of duty (`reviewer-brief.md:270-282`, `ownership-context.md:67`, `module-context.md:94`); splitting a *function* (`function-context.md:23-30`, a CODE CONCERN); splitting a comment *run* (`SKILL.md:386-390`); the authorship split (`generator_split.py`, `CLAUDE.md:187`); Python `str.split()`.

### verdict (the set as a concept)

- **`SKILL.md:41-71`** — "**The nine verdicts.** … you receive one per angle per block and must synthesise ONE, so what matters here is what each obliges *you* to do." Third column = task-agent obligations.
- **`reviewer-brief.md:95-112`** — "A verdict is a **recommendation** the task agent will combine…" Third column = the payload; second = reviewer triggers.

**The two tables are the same nine words with different column semantics.** `README.md:110-120` reproduces the `SKILL.md` shape.

Other senses: `reviewer-brief.md:99` ("a verdict without its payload is not a finding"); `:136` ("not a finding; it is scope you were not given"); `:250` (`CODE CONCERNS` carries none); `apply.md:4,6,71,112-113`; `review.md:32`; `census.py:15,1034,26,996`; `census.py:827` — used loosely for a classification (`UNVERIFIABLE` vs `UNRESOLVED`), not one of the nine; `docs/parsing.md:21`; `verdicts.py:49-59,546`.

**Manifest divergence:** `plugins/comment-review/.claude-plugin/plugin.json:3` says "Returns a verdict **per finding** for the human to approve"; `SKILL.md` and the brief say one verdict per angle per block, synthesised to one per block.

### payload

- **`reviewer-brief.md:95-112`** — the table's third column; "*'correct the count'* hands the judgement back; *'replace X with Y'* is the finding." Carried in `CHANGE` (`:67`).
- **`SKILL.md:68-71`** — "That contract is the **reviewers'** … you enforce it at stage 5 by refusing a verdict that arrives without one."
- **Enforced at `verdicts.py:283-316`** — per-verdict shape tests on lower-cased `CHANGE`. **`drop` and `patch` have no row of their own**; they fall through to the non-empty check.
- Each angle file at `:12-13` directs the reviewer to the brief for "the nine verdicts and the payload each one must carry."
- Non-verdict sense at `census.py:17` ("a payload rather than a symbol").

### the `add` payload — an anchor

- `reviewer-brief.md:109`; `SKILL.md:53,69`.
- **Enforced at `verdicts.py:302-307`** — passes if `CHANGE` contains the literal substring `anchor`, `above`, or `below`. **The word, not the referent**: a `CHANGE` naming a declaration without any of those three tokens fails; one containing the bare word "anchor" passes. `tests/test_verdicts.py:173-175`.
- `agents/comment-review-module-context.md:81` calls the anchor **a destination**.

### the `correct` payload — the true/false pair

- `reviewer-brief.md:107`; record example at `:54` — `CHANGE  false: "twenty call sites want this" / true: "31 callers, all in tests/"`.
- `SKILL.md:51,68,165`.
- **Enforced at `verdicts.py:299-300`** — two labelled substrings in either order; the settling line is not checked here.

### `QUERY_ATTEMPTED` / `QUERY_SETTLES`

- **`verdicts.py:105-132`** — "⚠ This is, and can only ever be, a **SHAPE check**: it cannot tell a real grep from the word 'grepped', and it is not trying to — its job is to remove the query that names nothing at all." `grep` is deliberately left unanchored on its left so "ripgrep" counts.
- Consumed at `verdicts.py:291-298`.
- Prose at `reviewer-brief.md:105` ("**the claim itself is checked by nothing**"), `:165-168`; `SKILL.md:542-546`.
- `tests/test_verdicts.py:179-313` records the substring-matching history: `\bran\b` must not hit "branch"/"range"/"transfer"; `\block\w*` must not admit "locked".

**The identifiers appear only in `verdicts.py`**; the prose sites name the concepts in capitals without them.

### escalated `query`

- **`compact.md:30-35`** — the only site using the phrase. "**An ESCALATED `query` does not block this pass, and must not.** Its destination is the author, who is first reached at 7a — *after* this stage… Compact the blocks whose verdicts are closed; carry an escalated query's block at its full length and say why."
- The verb form appears at `SKILL.md:49,594` and `README.md:113` without naming the resulting state; `reviewer-brief.md:159-160` describes the destination without the word.
- **No field of the RECORD marks a `query` as escalated, and `verdicts.py` does not distinguish escalated from unescalated queries.** Where the escalation decision is recorded must be inferred.

### `MOVE DESTINATION` and `move` UNAVAILABLE

- **`SKILL.md:249-260`** — "⚠⚠ **If the destination tree is absent, `move` is UNAVAILABLE for this run — and its blocks become `clean`, never `drop`.** Say so HERE, in the stage 1 report, and again at 7a." Closing: "**Keeping true prose in place costs a cap violation you can report. Dropping it costs the only copy.**"
- `SKILL.md:58-61`; `:197-201` ("**If `move` is unavailable, NO level reaches the cap**"); `:102`.
- **Packet section at `run_context.py:45`**, hint at `:61` — "the tree, or `UNAVAILABLE` — say which here, not at stage 6." **One of the eight sections `run_context.py` does not machine-check** (`:26-28,230-235`): the literal string `UNAVAILABLE` is not validated; any alphanumeric content satisfies `_answered`.
- `tests/test_run_context.py:32-33,151-152` — one test exists specifically to confirm an em-dash answer counts as answered.
- `agents/comment-review-ownership-context.md:79-81` — the reviewer-facing consequence: the finding is "**converted to `clean` and vanishes**."

### clean-arithmetic

- **Named only at `verdicts.py:575-583`** — "With coverage gaps and out-of-range indices already reported as fatal above, '**no angle ruled on it**' and '**every angle cleaned it**' are the same set — so this subtraction **is** the clean-arithmetic, not an approximation of it." `clean` is not counted; it is inferred from the absence of any other verdict, **conditional on the fatal checks above having fired**.
- Invoked unnamed at `SKILL.md:604-606` ("⚠ *Every angle that RAN*, not four"); `reviewer-brief.md:140-142`; `agents/comment-review-module-context.md:102-106`.
- `SKILL.md:540` — the one prose site using the hyphenated term.

**Wording differs:** `reviewer-brief.md:141-142` calls an invented word "a ninth word"; `module-context.md:105` calls the same thing "a tenth verdict word."

### STANDS UNCHANGED

- `verdicts.py:15`; printed at `:584-590`. **`M` is `len(ran)` where `ran` is the angles observed in the reports, not the angles `--angles` expected.** The line is printed even when `fatal > 0`.
- `SKILL.md:540`; `:604-606` (lower-case prose form); `agents/comment-review-module-context.md:105`; `tests/test_verdicts.py:495`.
- Related non-verdict "stands": `compact.md:40`, `SKILL.md:574`, `grade_hazards.py:133`.

### contradiction

- **`SKILL.md:624-629`** — "**`drop` against `correct` OR `patch` on the same sentence is a contradiction**, not a merge… ⚠ **Do not let the synthesis order decide it.** Step 2 applies `drop` before step 3 and 4, so deletion would win silently — and if the dropped sentence carries a fact the survivor does not, that is a meaning change made on an absent author's behalf, which CONSERVATIVE ON MEANING forbids."
- **`verdicts.py:419-428`** — keys on **`f.block`**, not on the sentence; skips `block < 0`.
- `verdicts.py:12-14` — "NOT counted fatal, but named in the closing line"; printed at `:567-573`; exit code remains 0.

**Scope differs:** `SKILL.md:624` says "on the same **sentence**"; `verdicts.py` detects per **block**. `SKILL.md:568-572` states the limit explicitly for the cross-file case.

- `SKILL.md:508-511` gives three other re-review triggers.

### laundering — three shapes, not cross-referenced

- **`SKILL.md:63-66`** and **`reviewer-brief.md:114-118`** — mislabelling `correct` as `patch`: "polishes the wording of a falsehood and retires the finding — **the laundering failure in its purest form**."
- **`SKILL.md:633-648`** — the *trim-around-the-claim* failure: "A block trimmed around an unchecked claim is **laundered, not reviewed**." The reviewer keeps the load-bearing-sounding clause and cuts the provenance, producing prose "shorter, cleaner, in-cap, and **strictly harder to falsify than what it replaced**." Worked example at `:638-643`.
- **`reviewer-brief.md:170-171`** — verb form, a third shape: "a single `clean` sentence must not **launder** the ones around it."

---

## Bundle 3 — the four editorial roles and the level ladder

Anchors: `SKILL.md`'s have shifted up one line — "four visitors over one tree" is `:85`; the level table `:183-188`; rows `:185`-`:188`. Agent-file, `CLAUDE.md`, `verdicts.py:66-71` and `run_context.py:89-91` anchors are exact.

**Old angle names** (`locality`, `currency`, `functionality`, `module-coherence`) appear at **zero sites** in the live tree. Every hit is in `evidence/` or `docs/superpowers/plans/`, both excluded. Two live artifacts outside the tree still carry them, recorded as observations: this session's installed-plugin agent registry, and the rename plan itself at `docs/superpowers/plans/2026-08-15-angle-scope-rename.md:64-67`.

### angle — SETTLED 2026-08-15, retired in favour of **editorial role**

Ruled by Roy. The word was borrowed from the `/simplify` skill, which uses it for the focuses
that pass works at; it stopped fitting once these became agents with scopes, and it was the
most-used undefined term in the tree — nothing anywhere said what an angle *was*. The nearest
was `SKILL.md:85`, "the four angles are four visitors over one tree", which says angles are
plural readers of one structure, not what distinguishes one.

**Two words replace it, and the split is deliberate.** The term of art in prose is **editorial
role** — the scope a reviewer reads for. The identifiers say **reviewer** (`--reviewers`,
`REVIEWER FILES`, `reviewer = path.stem`) because `role` unqualified would also cover the task
agent and the absent author, who are roles in `SKILL.md`'s own cast; naming the four `role`
would reinstall the polysemy this entry exists to remove.

⚠ The heading here read "five senses" while listing **six** (A–F). Corrected. The senses were
not five competing meanings needing five different words — four of the six are the editorial
role itself, and the remaining two are that role's *name* and its *file*:

| sense | collected as | resolved to |
| --- | --- | --- |
| A — a scope a claim is measured against | `SKILL.md:190-192`, `reviewer-brief.md:155` | the editorial role |
| B — a reviewer agent, the actor | `SKILL.md:459-466`, `verdicts.py:7,16` | the editorial role; `reviewer` in code |
| C — a string, the stem of a report filename | `verdicts.py:487` `angle = path.stem` | the role's NAME, in a filename slot — `reviewer = path.stem` |
| D — a file on disk (the agent definition) | `reviewer-brief.md:3`, `run_context.py:17-21` | the role's FILE — packet key `REVIEWER FILES` |
| E — a category of defect | `verdicts.py:372-373` | the role's category — "the block-context role's own category" |
| F — a closed slot in a fixed set | `reviewer-brief.md:295`, `SKILL.md:210` | "one of the four editorial roles" |

⚠ **`--reviewers` was always a role check, which is what made the rename correct rather than
cosmetic.** `verdicts.py:16` names it "every expected reviewer actually reported"; `:32-34`
calls a reviewer that never reported "the easier version of the fabrication this whole script
exists to catch". The file stem is the identifier it uses, not a different concept. Still true
after the rename, and still unenforced: nothing checks a stem against the four published role
names — see the enforcement-gap task in the TODO.

The collected sense analysis follows, verbatim as of `802a574`, as the evidence for that
resolution.

**Sense A — a scope a claim is measured against.** `SKILL.md:190-192` — "The other three check a claim against the code at their scope"; here **angle ≡ scope**, the two words used interchangeably. Also `agents/comment-review-ownership-context.md:25-28`; `reviewer-brief.md:155` ("outside your angle — what settles it belongs to another scope"); `README.md:60-61`; `census.py:302`.

**Sense B — a reviewer agent, the actor.** `SKILL.md:459-466` (the dispatch table), `:26`; `verdicts.py:7,16,437,491,500,512`; `SKILL.md:604-606` and `verdicts.py:575-586` ("every angle that RAN" — a countable participant); `reviewer-brief.md:97,140,287`.

**Sense C — a string, the stem of a report filename.** `verdicts.py:487` — `angle = path.stem`. **Nothing validates it against the four published names.** Also `:145,213,267-274`; `tests/test_verdicts.py:45,61,73-74,154-156`.

**Sense D — a file on disk (the agent definition).** `reviewer-brief.md:3` ("with one **angle file** each"), `:146`; `docs/limitations.md:22,36`; `SKILL.md:287-289`; `run_context.py:17-21,47,63-65`; `CLAUDE.md:205`. ⚠ Recorded as-is: `run_context.py:63-65`'s hint reads "absolute path per angle, **the brief, and the compact + review agents**," so `ANGLE FILES` holds paths for six files while "angle" elsewhere names four things. The four line counts in `docs/limitations.md:22` (101/101/129/120) were verified against `wc -l` and match exactly.

**Sense E — a category of defect, and a property of a `clean`.** `SKILL.md:48`; `README.md:112`; `reviewer-brief.md:104,138-142`; `agents/comment-review-module-context.md:99-100`; `CLAUDE.md:204-205`; `verdicts.py:372-373`, `reviewer-brief.md:88`, `tests/test_verdicts.py:397,682` ("the block-context angle's own category", where an angle names a class of claim); `evals/discriminators.md:45` ("module-context overclaim"); `CLAUDE.md:198-199`.

**Sense F — a closed slot in a fixed set.** `reviewer-brief.md:295` — "Length is not one of the four angles"; `SKILL.md:210` — "Length is not an angle."

**Undetermined at its site:** `README.md:151,231` say "the four **reading** angles," a qualifier used nowhere else, distinguishing them from "the mechanical detectors."

### ownership-context

- Stated at `agents/comment-review-ownership-context.md:2,3,7,16` — **"does this comment belong to the line it sits on?"** Refined at `:18` ("You read a comment against its *position*"); the operative content at `:30-41` is an assessability gate; `:40-41` — "You rule on whether truth is assessable here at all."
- `SKILL.md:463` — the dispatched agent, same question.
- `SKILL.md:99-101` — **the angle whose verdicts have no census field to rest on.**
- `SKILL.md:104-107`, `census.py:302,351-352`, `docs/parsing.md:62`, `README.md:239` — the only angle degraded by a missing owner.
- `SKILL.md:190-192,195` — runs at **every** level including `fact-check`.
- `SKILL.md:391`; `SKILL.md:618` and `reviewer-brief.md:288` — the angle whose destination governs; `agents/comment-review-function-context.md:118-120` states the same precedence from the other side.
- `reviewer-brief.md:272-282` — one half of the restatement split.
- `agents/comment-review-ownership-context.md:92-97` — what its `clean` asserts.

**One meaning throughout,** with a consistent secondary role at `SKILL.md:99-107`, `census.py:302,351`, `docs/parsing.md:62`, `README.md:239`: not the question but *the angle the tooling cannot support*.

### block-context

- Stated at `agents/comment-review-block-context.md:2,3,7,16` — **"is every claim in this block true of the code it sits with?"** Three claim kinds at `:18-24`; obituaries `:31-45`; quantified/exclusivity `:47-62`; cited paths and guards `:70-75`; negative boundary `:85-90`.
- `SKILL.md:464`; `:104` (never asks where a block belongs); `:185-187`.
- `reviewer-brief.md:70,88`, `verdicts.py:372-373`, `tests/test_verdicts.py:397,682` — **a category of claim** ("the block-context angle's own category"), invoked to explain why `SUMMARY`'s right half is exempt from the verbatim check.
- `reviewer-brief.md:132-133`.
- `apply.md:78` — "Re-read what you wrote, against the block-context rule." **The angle's criterion applied by the task agent to its own output, at a stage no reviewer runs in.**
- `agents/comment-review-module-context.md:27` — "A module docstring also gets the Block-Context and Function-Context **lenses**." A fifth informal word for angle, used once.

### function-context

- Stated at `agents/comment-review-function-context.md:2,3,7,16` — **"does the commentary match what the function is FOR?"**
- `SKILL.md:465`; `:104-106` ("function-context's ordering read takes its structure from the body rather than from a census field"); `:185-187`.
- `reviewer-brief.md:286-291` — the angle that can place a block and be overruled on destination; `agents/comment-review-function-context.md:118-120` states its own deference.
- `reviewer-brief.md:132`; `agents/comment-review-module-context.md:27` (as a "lens").
- `agents/comment-review-function-context.md:123-125` — what its `clean` asserts.

### module-context

- Stated at `agents/comment-review-module-context.md:2,3,7,16` — **"do the comments say this is ONE module?"** `:18-19` — "the only angle reading a file as a single argument rather than as a list of blocks."
- `SKILL.md:466`; `:104`.
- `SKILL.md:187` — **the only angle added by a level**: `full` adds it; it does not run at `fact-check` or `line`.
- `reviewer-brief.md:272-282` — the other half of the restatement split.
- `reviewer-brief.md:132` — misplacement is `clean` for it at `fact-check`, **a level at which, per `SKILL.md:185`, it does not run.**
- `evals/discriminators.md:45`.
- `agents/comment-review-module-context.md:96-115` — a scope-specific instruction found nowhere else, and what its `clean` asserts.

### level — three stating sites, three different things

**1. `SKILL.md:181-188`** — the argument and table. `:181` "how deep to edit, declared before starting. Default `full`." Both columns written as **deltas** for the lower rungs. `:194-195` — "**The ladder changes shape and that is the point.** It used to add an ANGLE at each rung; now `line` adds only VERDICTS, because `ownership-context` already ran at `fact-check`." `:203-206` — level as a **budget-management** device.

**2. `verdicts.py:61-71`** — `LEVELS`, a dict of verdict sets. `:61-65` — "these are **cumulative sets, not the deltas the table reads as**. `allowed()` is a membership test against one entry, so an entry listing only what its level ADDS would reject `correct` at `full`." Meaning: **level ≡ a verdict vocabulary, and nothing else.** This site says nothing about which angles run. Recorded without comment: at `level=proof` the set is empty, so every finding in any report would be refused as not carried.

**3. `run_context.py:89-91`** — `LEVELS`, a tuple of names. Meaning: **one of four legal name strings**, checked as a spelling. ⚠ Recorded as-is: the comment at `:90` says an out-of-set level "dispatches **four** reviewers," while `SKILL.md:183-188` has three of the four levels dispatching fewer than four.

Other uses: `reviewer-brief.md:4` (level = angle count, delivered via the packet); `:131-136` (verdict vocabulary); `agents/comment-review-ownership-context.md:3,75-77,82-84` (level determines whether the same finding is `reanchor`, `query`, or converted to `clean`); `SKILL.md:197,701`; `CLAUDE.md:50`; `tests/test_run_context.py:164,198-204`; `tests/test_verdicts.py:318-325,470-477`.

**A separate, unrelated sense in live files:** `README.md:39` — "I broke down the comment review into four **levels**/categories," followed by the list of the four **angles**. Here `level` names an angle. `README.md` does not use `level` in the ladder sense anywhere; the ladder is not documented in `README.md` at all. Ordinary-English suffix uses: `README.md:93`, `CLAUDE.md:140`, `tests/test_verdicts.py:591-592`, `tests/test_prove_unchanged.py:354`, `tests/fixtures/sample.rs:1`.

### `fact-check`

- `SKILL.md:185` — angles `ownership-context, block-context, function-context`; verdicts `correct · query · clean`. `:190-192`, `:203-206`, `:533`, `:606` ("requiring four would make a block unblessable at that level").
- `verdicts.py:67` — the verdict set only; **the three-angle fact is not encoded.**
- `run_context.py:53,91`; `reviewer-brief.md:131-135`; `agents/comment-review-ownership-context.md:3,75-77,83-84`; `tests/test_verdicts.py:318-325`.

**One meaning throughout.**

### `line`

- `SKILL.md:186` — angles "the same three"; verdicts `+ drop · move · reanchor · split · add`. `:194-195`.
- `verdicts.py:68` — the cumulative set, eight verdicts; `patch` is the one absent.
- `run_context.py:53,91`.

**One meaning throughout.** Recorded as an inference a reader must make: `:186` states `line`'s angles only as "the same three" — the reader carries the names down from the `fact-check` row.

⚠ The word `line` is heavily used in its ordinary sense across every file. The ladder sense is distinguished only by backtick formatting and by sitting in the level table or a `--level` argument.

### `full`

- `SKILL.md:187` — the only rung that adds an angle; `:181` default; `:520,533`.
- `verdicts.py:69` — all nine; `:439` default.
- `run_context.py:53,91`; `reviewer-brief.md:4`; `CLAUDE.md:50`; `tests/test_verdicts.py:470`.

**One meaning throughout.**

### `proof` — three unrelated things called proof

**As a level:** `SKILL.md:188` ("**none** — stage 8 (REVIEW) only… ⚠ It has no 7b to complete, so it loads `review.md` directly"); `verdicts.py:70` (`set()`, with `:64-65` explaining the empty set); `run_context.py:53,91`; `tests/test_run_context.py:202-204`.

**As the name of a stage-8 pass:** `review.md:25` — "**The proof pass is not the residue check.**"; `residue-check.md:7` — "It is NOT stage 8's proof pass."; `agents/comment-review-review.md:7` — the agent is named **PROOFREADER**.

**As a byte/AST identity claim:** `SKILL.md:87`; `apply.md:45,52,65,118`; `compact.md:130`.

The level takes its name from the second; nothing states that, and a reader must infer it from `SKILL.md:188`.

### `--angles` — SETTLED 2026-08-15, now `--reviewers`

Renamed with [angle](#angle--settled-2026-08-15-retired-in-favour-of-editorial-role). The
observation below stands unchanged and remains open: the declared strings are still never
checked against the four published role names.

- **`verdicts.py:441-449`** — "comma-separated expected angle names, matched against each report file's **STEM**." Enforced `:508-517`; when omitted the absence is **announced**, not swallowed (`:518-522`). Rationale at `:504-507` — "Without `--angles`, a reviewer that never reported at all is invisible: 'every angle' silently means 'every file I was handed'."
- `SKILL.md:524-533` — "**NAME EACH REPORT FILE AFTER ITS ANGLE**… a report saved as `report1.md` is an angle nobody expected and every expected angle reads as missing. Two files with the same stem are refused outright."
- `CLAUDE.md:47-52`; `tests/test_verdicts.py:481-482,545-552,559-562`.

**One meaning throughout:** a declared list of expected report-file stems. Recorded without judgement: **the strings are never checked against the four published angle names** — `verdicts.py:487` takes whatever stem it is given. Which angles a given `--level` should have run is stated in prose at `SKILL.md:533` and is not encoded anywhere a script reads.

---

## Bundle 4 — census structure

Anchor drift table at the end of this bundle.

### census — five senses, none enumerated at any site

- Stated at `scripts/census.py:1-18` — two outputs: "`CENSUS` every comment run and every docstring, numbered, with the marks attached to it. The reviewers walk this list; a block missing from it is a block nobody reviews" and "`RESOLUTION` the questions a symbol table and a filesystem can settle." Also "Read-only, and always exits 0 — this is an input to a review, not a gate."
- Stated at `SKILL.md:24-25` (stages 2 and 3); prose section `SKILL.md:338-364`.
- Used at `scripts/census.py:918,940-987` — the in-memory `list[Block]`.
- Used at `scripts/census.py:1012` — the printed numbered listing.
- Used at `SKILL.md:354` — a file on disk.
- Used at `scripts/verdicts.py:3,438,456-471` — JSON read back, whose 1-based positions are the index space findings join against.
- Used at `run_context.py:46,62,243-246` — a packet field holding an absolute path.
- Used at `reviewer-brief.md:33-37` — the reviewer's worklist.
- Used at `compact.md:76,83,90` — the stamping process that supplies KIND.
- Used at `scripts/prove_unchanged.py:14,28,88-91,112,145` — the comment locations used to strip prose ("the census and the file disagree; do not reconcile").
- Used as a **verb** at `scripts/census.py:428,1034`, `scripts/fetch_corpora.py:76`, `scripts/README.md:32`.
- `docs/parsing.md:1,53-60,84`; `CLAUDE.md:122-134`; `README.md:229-241`.

**Senses in play:** the script, the run's in-memory block list, the printed listing, the file artifact, and the index space. Each site fixes which by context; no site enumerates the set.

### block — SETTLED 2026-08-15 for the census-unit sense; four senses remain

**Roy's definition: a block is the INTERVAL BETWEEN TWO LINES OF CODE.** The bounding code
lines define it, not its contents — only code is a boundary, so a blank line and a work marker
both sit inside one block. ⚠ **The implementation already did this; only the prose did not.**
Measured: for `a = 1` / blank / `# first half` / blank / `# second half` / `b = 2` the census
returns `start=3, end=5, counted=2, raw_lines=['# first half', '# second half']` — the span
covers the interior blank and the cap charges only the prose. `start`/`end` were always the
interval; `raw_lines`/`lines` were always what a cap charges for. Calling a block "one comment
run" conflated the two, which is why `add` had no block to cite and why three rules had to be
stated where one definition does the work.

⚠ **The worked example could not produce the number it claimed.** `SKILL.md`'s example
annotated itself in `#` syntax, so its own annotations sat inside the interval it described:
run literally it censused as **one block of 4 counted lines** where the text said 3. Rewritten
without inline annotations, it now returns exactly 3. Verified by extracting the fenced block
from `SKILL.md` and running `census.py` on it.

- Stated at `scripts/census.py:190` (was "One comment run or one docstring").
- Stated at `SKILL.md`'s "What counts as ONE block".
- **As an integer index:** `reviewer-brief.md:60` ("the census INDEX"); `verdicts.py:137,146,162-172,420-428,471,535-551` (`block=-1` sentinel for a record attributable to no real block); `verdicts.py:15,575-588`.
- **As a container of sentences:** `reviewer-brief.md:170` — "**Rule on SENTENCES, not blocks.** A container of six sentences can hold six verdicts."
- **As the prose unit** across `agents/comment-review-ownership-context.md:30,33,45,56-58,94-96`; `agents/comment-review-block-context.md:16,89,94-96`; `compact.md:48-100`; `residue-check.md:4,17-25`; `review.md:12,25-26,36-38`; `apply.md:6,32,35,96-99,108-110,118-121`.
- **As a syntactic form — block comment:** `scripts/census.py:255` (`block_comment` field), `:366,394-410` (`in_block`), `:420-429`; `tests/test_census_blocks.py:63-97`; `docs/parsing.md:111`.
- **As a fenced record:** `verdicts.py:73-83` parses the `--- FINDING` block; `reviewer-brief.md:45-56`.

Note the angle named **block-context** uses the same word for its *scope* ("the code it sits with"), not for the census unit.

### comment run

- Stated at `SKILL.md:384-385` — "**Only code ends a run.** A blank line does not. Split on blanks and a 9-line block reads as `6 + 3` and passes a cap of 6." Also `:359-361`.
- Implemented at `scripts/census.py:414` (lexical, "⚠ CODE ends a run; a blank line does not"), `:505-524` (tokenized), `:509-515` ("A trailing comment CLOSES its run").
- Stated at `scripts/census.py:211-222` (`_join`) — "A comment run as ONE normalised string… Matching line-by-line reports the fragment instead of the claim."
- `scripts/census.py:5,190,348,479`; `:1000` and `:986` — "longest comment run" computed over `b.kind == "comment"` only, excluding `trailing-comment` and `docstring`.
- `CLAUDE.md:92`; `SKILL.md:24,75`; `evals/evals.json:9,17,25`; `evals/generator_split.py:8`; `evals/grade_hazards.py:15`.

**Bare "run" collides with an unrelated sense throughout: one invocation of the skill** — `SKILL.md:354,252`; `apply.md:8,58-62,94`; `review.md:22,33,44`; `census.py:31`. Both appear in the same paragraphs (`compact.md:32` "a capped run"; `:81` "the cap counts lines in one `#` run"). A third sense at `census.py:365-419`: the local variable `run` holding accumulating lines.

### counted lines

- Stated at `scripts/census.py:100-111` — "Lines a cap should charge for: a marker LINE itself is free… Six lines plus a `TODO:` is six."
- Worked example at `SKILL.md:368-381`.
- Carried as `Block.lines` — `census.py:196` declared, `:386,498` set from `counted_lines`, **`:553,593` docstring blocks set `lines` from `len(splitlines())`, i.e. not through `counted_lines`**, `:534` `unparsed` sets `lines=0`.
- Consumed at `census.py:977-984` (over-cap tally); printed at `:1016` as `{b.lines}L`; asserted at `tests/test_census_blocks.py:27-32`.

**Distinct from the mark named `counted`** (`census.py:130-135,835-837`; `SKILL.md:402`), which is about a quantified *claim*. The two words appear in adjacent columns of the same census output line.

### KIND

- Stated at `scripts/census.py:195` — `kind: str  # "comment" | "docstring"`. **The inline comment enumerates two values; the code emits four.**
- Stated at `compact.md:75-93` — the routing table: `comment`/`trailing-comment` → LENGTH → may be cut; `docstring` → FORMAT → nothing; `comment` with `doc-kind-unresolved` → UNKNOWN → nothing.
- Stated at `SKILL.md:145-148`, `:660-663` ("**Acquit on KIND, never on LENGTH**").
- `census.py:433-475`; `agents/comment-review-compact.md:3,10,14`; `README.md:251-253`; `docs/parsing.md:87`.
- **Emitted values:** `comment` (`:379,497`), `trailing-comment` (`:379,497`), `docstring` (`:377,553,592`), `unparsed` (`:534`). `compact.md:76` enumerates the first three; **`unparsed` appears in no KIND enumeration outside `census.py`.**

### `comment` (as a kind)

- Assigned at `census.py:379,497`. Stated at `compact.md:81` — governed by LENGTH.
- **Cap-tally and longest-run filters at `census.py:979-986` use `kind == "comment"`, which excludes `trailing-comment`. `compact.md:81` groups the two together under LENGTH; the census counts only `comment`.**
- Gate for `flag_structural_docs` at `census.py:459`, with the reason at `:457-458`.
- `compact.md:83,89`.

The ordinary word *comment* is used constantly everywhere; only the sites above use it as a KIND value.

### `docstring` (kind, and general sense)

**As a KIND value:** assigned at `census.py:373-377` (lexical — a Rust `///` run and a JSDoc `/** */` block carry KIND `docstring`), `:553` (tokenized, from `ast.get_docstring`, with `owner` set at `:556`), `:592` (a PEP 727 `Doc()` string inside `Annotated[...]`, **with no owner**). Consumed at `compact.md:82,85-87`; `census.py:847-855` (`narrative-in-docstring` fires only for this kind); `:979-986` (excluded from both tallies).

**As the ordinary word:** `SKILL.md:3,10,24,75,245-247,267,489`; `agents/comment-review-function-context.md:18-25,61,110,124`; `agents/comment-review-module-context.md:18,23,27-56,62,67,98,113`; `prove_unchanged.py:11,58-62,164`; `apply.md:40-42,88,103-104,109`; `docs/limitations.md:38`; `README.md`, `CLAUDE.md`, `pyproject.toml:36`, `evals/discriminators.md:21,46-47`.

**The two senses coexist without a stated boundary:** `SKILL.md:145-148` and `compact.md:82` use "docstring" as the KIND while arguing about docstring FORMAT conventions, which are the general sense.

### `trailing-comment`

- Stated at `SKILL.md:393-394` — "**A trailing comment is its own block**, one line, owned by the line it sits on."
- Assigned `census.py:379,418` (lexical), `:497,507` (tokenized). `:509-515` — "Its code sits before it, so no later token flushes it, and it silently absorbed the next leading block across two blank lines." `:484-491` — "PROSE comes from the comment token; WIDTH from the physical line."
- `compact.md:76,81`; excluded at `census.py:459,979-986`; `prove_unchanged.py:106`.
- `agents/comment-review-ownership-context.md:45-47`, `:86-90` ("Report it as FORMATTING, not as misplaced"); `SKILL.md:665`.

**Ownership direction differs from the general rule:** a block "belongs to the code BELOW it" (`SKILL.md:391`); a trailing comment is "owned by the line it sits on" (`SKILL.md:393`, `census.py:418`).

### `unparsed`

- **Stated only at `scripts/census.py:526-539`** — on `SyntaxError`, one `Block` with `kind="unparsed"`, `lines=0`, text `"UNPARSED ({msg}) — no docstrings censused, no names harvested"`. Comment runs found before the failure are still returned; the function returns early, so no docstrings and no `Doc()` blocks are added.
- **No other live site names it.** Absent from `compact.md`'s KIND table, from `SKILL.md`, from the agent files, and from the tests. A consumer routing on KIND meets a fourth value no stated table lists.
- What a reader must infer: how COMPACT should treat it, and that `lines=0` means it can never be over cap.

### orphan / orphan run — two senses

- **Mechanical:** `scripts/census.py:461-465` — "The IMMEDIATELY next line, not the next non-blank one… a blank line between them means the run documents nothing, which is an ORPHAN — an ownership-context finding, and emphatically not a doc comment to be exempted from the cap." Consequence at `:466-468`: such a run never gets `doc-kind-unresolved`. Fixture `tests/fixtures/sample.go:12`; test `tests/test_census_doc_kind.py:25-28`.
- **A reviewer judgement:** `agents/comment-review-ownership-context.md:34` ("sits orphaned between definitions is making no proposition about the code beside it"); `README.md:66`; `evals/grade_hazards.py:17-20,55-58` ("orphanhood is positional — a correct repair RELOCATES the sentence, so the text survives either way and no probe can separate fixed from ignored"); `evals/discriminators.md:72`.

Nothing states that the first is a special case of the second. **The census never emits an "orphan" mark or field**, so nothing downstream can read the mechanical condition.

### owner / OWNERSHIP

- Stated at `scripts/census.py:198` — "the declaration it annotates, when structurally known."
- Stated at `scripts/census.py:26-29` — "⚠ NO COMMENT carries an owner at either tier, so every ownership-context verdict rests on a reviewer READING the file… Treat placement findings as CANDIDATES."
- Stated at `SKILL.md:98-102` — same, plus "a judgement no field records and nothing downstream can check."
- Stated at `SKILL.md:391-392` — "**A block belongs to the code BELOW it**, which is what makes ownership-context answerable."
- Stated at `docs/parsing.md:130-134` — "⭐ **Ownership is a CONVENTION, not a parse result.** Even a perfect CST hands comments back as siblings… tree-sitter does not solve it, and neither does `documentSymbol`."
- **Set in code only at `census.py:556`** for AST docstrings. `_annotated_docs` (`:564-598`) sets none; `blocks_lexical` sets none.
- Printed at `census.py:1015`; tier claims at `:23,302-306,871-872`, `SKILL.md:95-96`, `CLAUDE.md:129-130`; `census.py:351-353`; LSP route at `SKILL.md:301,416-418`, `docs/parsing.md:19,31-33`; standing caveat printed at `census.py:995-999`; `docs/parsing.md:62-65,126-127`; `tests/test_census_blocks.py:39-41`.

**A second, unrelated sense — which angle owns a finding, and which function should own a rule:** `reviewer-brief.md:70,270-282`; `agents/comment-review-ownership-context.md:60-69`; `agents/comment-review-module-context.md:79,94`; `compact.md:19-20,109`; `SKILL.md:658`; `agents/comment-review-function-context.md:100`. **A third:** `.claude-plugin/marketplace.json:5` (the plugin's publisher); `SKILL.md:272`, `run_context.py:10` ("nothing owned consistency").

### node — two senses

**Prose-tree node — no stated definition.** Nearest: `SKILL.md:75-76` — "Every comment run and every docstring is a node, attached to the declaration it annotates, with every reference it makes already resolved."

- `SKILL.md:24,25,26,80-86,349,381,413`; `CLAUDE.md:92,93,95`.
- `SKILL.md:381` — "Four physical comment lines, **one** node" — *node* and *block* denote the same thing here.
- **`SKILL.md:443`** — "a config, data or documentation file carrying prose that justifies a value is **a node like any other**." Here the thing called a node is a *file*; whether this means the file's blocks are nodes or the file itself occupies the tree must be inferred.
- **No code uses "node" for a census block.** `census.py` calls them `Block`/`blocks`/`census`; `verdicts.py` calls them blocks and indices. The word is confined to the Markdown.

**Python AST node:** `census.py:541-547,556,574-586,654-667`; `referrers.py:71-73`; `prove_unchanged.py:65-70`. **At `census.py:541-556` both senses meet in one loop:** the AST `node` supplies the `owner` of the prose-tree node being constructed.

### work marker

- Stated at `scripts/census.py:87-97` — "Free markers point OUTWARD, at work that is not done, so they are not the explanation and must not spend its budget." `MARKERS` at `:90`; `LEAD_PUNCT` at `:92-97` — "Anchoring on `#` made the exemption Python-only… a `// TODO:` was charged to the cap."
- Stated at `census.py:100-111`; `SKILL.md:386-390` — "Both halves matter: if it counted, the cheapest route to green would be deleting a pointer to filed work; if it split, a block could be made compliant by adding one. ⚠ **A marker's CONTINUATION lines still count.**"
- **`SKILL.md:240-243`** — "⚠ **Ask which markers the repo exempts from the cap** (`TODO`, `FIXME`, `HACK`, `XXX`, `BUG` is the common set)." Here the set is the repo's to declare and `census.py`'s list is called "the common set"; **`census.py:90` hard-codes it and exposes no flag to change it.**
- `census.py:512`; `tests/test_census_blocks.py:27-32`; fixture `tests/fixtures/sample.py:7`.
- **`evals/grade_hazards.py:51` and `evals/discriminators.md:64` use `TODO/` as a directory path, not a work marker.**

**"marker" alone carries three further senses in the same script:** a **comment opener** (`census.py:211-231,249,315`; `SKILL.md:96`); a **list marker** (`run_context.py:93`); a **contrast marker** in prose (`review.md:13`). At `census.py:249,315` the word means a comment opener while `census.py:90-111`, thirty lines above, fixes it as `TODO`/`FIXME`/etc.

### Anchors that moved since the inventory

| term | inventory | on disk |
|---|---|---|
| block (unit) | `census.py:189` | docstring `:190` (class `:188`) |
| node (prose tree) | `SKILL.md:76` | sentence begins `:75` |
| comment run / "What counts as ONE block" | `SKILL.md:368-392` | section `:366-394`, example `:368-379` |
| `trailing-comment` | `SKILL.md:395-396` | `:393-394` |
| owner | `SKILL.md:99-101`, `:393-394` | `:98-102`, `:391-392` |
| work marker | `SKILL.md:242-244`, `:388-392` | `:240-243`, `:386-390` |
| `docstring` (kind) | `SKILL.md:146-149`, `:659-662` | `:145-148`, `:660-663` |
| orphan | `census.py:461-466` | `:461-465` |
| census (SKILL prose) | `SKILL.md:340-367` | `:338-364` |

Unchanged and verified: `census.py:5-7`, `:26-29`, `:100-111`, `:195`, `:198`, `:528-539`; `compact.md:75-93`; `docs/parsing.md:130-134`.

---

## Bundle 6 — marks

### mark (the concept) — four senses

- Stated at `SKILL.md:83` — "the marks are annotations on a node, so a reviewer receives resolved references instead of re-deriving them."
- Stated at `SKILL.md:396-405` — the six-row table, prefaced at `:407-408` by "⚠⚠ The last four are where the defects are. Check the CLAIM, not the CITATION."
- Stated at `scripts/census.py:114-116` — "Each is located here and RESOLVED below. Locating is most of the work; the resolution is what stops a reviewer treating a citation as a verified claim."
- Emitted at `census.py:805-855` — attaches to `block.marks` (a `set[str]`, `:200`) and appends a resolution string to `block.notes`. **This function also emits `narrative-in-docstring` (`:853`), a mark not in `SKILL.md`'s six-row table.**
- Printed at `census.py:1012-1019`.
- **Asymmetry stated at `census.py:1033-1039`** — "`names-a-symbol` and `counted` are CANDIDATES a reviewer confirms; the resolved paths are facts about the filesystem that a reviewer should not re-derive." `coverage-claim`, `forbids-a-literal`, `repeated-literal` are not mentioned either way.
- `census.py:15-18`; `SKILL.md:423-425`.
- **Sense 2 — the stage-4 MARK pass's completeness:** `SKILL.md:81` — "*a block nobody mentioned is a gap in the mark, not a block that passed*." **The same sentence appears elsewhere as "gap in the review"**: `census.py:1012` and `reviewer-brief.md:36-37`. Only `SKILL.md:81` substitutes "mark".
- **Sense 3 — a synonym for "detector":** `reviewer-brief.md:233-237` — "Where a **mechanical mark** fires broadly, report it as a **batch to triage**."
- **Sense 4 — a block selected for the approved sweep:** `apply.md:6-8` — "Apply only what was approved, and **only what was marked**. ⚠ An unmarked block is never swept. If the sweep wants to touch something **the mark did not reach**, that is a finding for the next run." Not `census.py`'s `block.marks`.
- `SKILL.md:138-139` (marks as EDIT's input, excluded from COMPACT's contract); `reviewer-brief.md:33-37` (calls them "mechanical resolutions", not marks); `prove_unchanged.py:113,125`.
- **Not read at all by `verdicts.py`** — no `.marks` reference in that file. The join operates on RECORD findings and census indices.

### `counted`

- Stated `SKILL.md:402` — "re-derive the POPULATION, then count it."
- Emitted `census.py:130-135` (regex: a number word or digit + a population noun) and `:835-837` (note: "RE-COUNT, and name the population").
- `census.py:1033-1039` — grouped with `names-a-symbol` as a CANDIDATE.
- `agents/comment-review-block-context.md:47-53` — the same shapes, restating the resolution **without using the term**.
- `reviewer-brief.md:69-71,188-192,196-197`; `README.md:79-80,151-153` ("counted claims", plural unhyphenated, in a measured-generalization context).
- **Unrelated ordinary-English use:** `compact.md:93` ("counted as over a cap of two").

### `coverage-claim`

- Stated `SKILL.md:403` — "does the guard exist — **can it fail**, and does it pass with its exemptions OFF?"
- Emitted `census.py:136-140,838-842`.
- Used verbatim (two words, unhyphenated) at `agents/comment-review-function-context.md:3,38-50` — restates `SKILL.md:403` almost word for word, with the measured 0-vs-2,026 pair.
- `README.md:88`.
- **Not found in `reviewer-brief.md` under `coverage-claim` or "coverage claim".** The brief's **coverage gap** (`:92`, `verdicts.py:263-275,524-532`) is a different, gate-level term — a census index with no verdict from an angle. The two share the word "coverage" but resolve at different stages (mark: 2-3; gap: 5) and about different subjects (a claim's guard vs. a reviewer's accounting).

### `names-a-symbol`

- Stated `SKILL.md:401` — "`workspaceSymbol` where 1.7 found a server, else the AST corpus."
- **A second definition site not in the inventory:** `SKILL.md:419-425` — "the mark stays a CANDIDATE a reviewer confirms, exactly as when the AST answered it. What changes is the cost of checking, not who decides."
- Emitted `census.py:118-129,811-820`.
- `census.py:15-18,1033-1039` — explicitly a CANDIDATE list.
- **`docs/parsing.md:19-21,45-49`** adds a measured claim absent from `SKILL.md` and `census.py`: "`names-a-symbol` … was measured as one of the weakest detectors outside the codebase it grew in."
- `README.md:151-155` — grouped anonymously as "symbol liveness".

### `cites-a-path`

- Stated `SKILL.md:400` — "tracked in the tree? ⚠ present-but-untracked is **unverifiable**, not dangling."
- Emitted `census.py:118,822-833` — **three distinct outcomes**: `UNVERIFIABLE path (untracked/derived)`, `UNRESOLVED path`, and `cites {path}::{member} — confirm the test exists`.
- `census.py:1033-1039` — its resolved paths are "facts about the filesystem", contrasted with the CANDIDATE marks.
- `SKILL.md:407-408`; `reviewer-brief.md:182-186` (restates the principle **without the term**); `README.md:81,151-153`.

**The three-way outcome appears only in `census.py`**; `SKILL.md` states only the tracked/untracked distinction.

### `forbids-a-literal`

- Stated `SKILL.md:404` — "grep the forbidden literal across that file."
- Emitted `census.py:141-144,843-845`.
- `agents/comment-review-function-context.md:52-56` — the worked example matches the regex shape exactly, and **adds the CODE-vs-COMMENT split**: a broken rule is a code concern; a false claim about the rule is the comment finding.
- `README.md:89`.
- **Not found under the hyphenated term outside `SKILL.md` and `census.py`;** every other site uses "prohibition".

### `repeated-literal`

- Stated `SKILL.md:405` — "where else is this number written? one source at both ends of a round trip?"
- Emitted `census.py:145-156` (`NUMBER`, `prose_numbers()`, with `DATEISH` stripped first — "Left in, every `2026-08-09` contributes three 'repeated' numbers, and the detector drowns in its own noise") and **`:945-959` as an explicit second pass over the whole census**: a block is marked only if `seen[n] > 1 and len(where[n]) > 1`.
- **Not referenced or paraphrased anywhere else in the swept tree** — no agent file, no `README.md`, no `reviewer-brief.md`.

**Anchor drift:** the `SKILL.md` table header is now `:398` and the six rows run `:400-405` (inventory cited `:402-407`). `census.py`'s ranges match exactly.

---

## Bundle 7 — the pipeline stages

Anchors shifted ~1-3 lines: PROJECT DETERMINATION `:23,212`; MARK `:26,119-120,457`; EDIT `:27,122-124,513`; COMPACT `:28,126-148,670-693`; APPROVAL `:29-30,150,695,714`; REVIEW `:31,152-153,723`; re-review `:508-511,623-629`; the join `:515,570,699`.

### PROJECT DETERMINATION (1)

- `SKILL.md:23` (stage table); `:212` (section, substeps 1.1-1.8 at `:214-336`).
- `CLAUDE.md:84,89`.
- **`README.md:105`** — "Language, documentation style, project rules." **A shorter list than either of the above** (no merge base, no cap/width, no style sheet, no agent probe, no LSP probe, no name corpus).
- Referred to as "stage 1" at `SKILL.md:102,201,253,283` and `run_context.py:61`.

### ANNOTATE (2)

- `SKILL.md:24`; `:338` (heading "Stages 2–3", never separated below it — one `census.py` invocation performs both).
- `census.py:1` — "Stages 2-3 … ANNOTATE, then FIND REFERENCES." Its two outputs `CENSUS` and `RESOLUTION` (`:5-10`) map to the two stages without saying so.
- `CLAUDE.md:92`; `README.md:106` (**actor unnamed here**; elsewhere always `census.py`).

### FIND REFERENCES (3) — two halves under one stage number

- **Outbound:** `SKILL.md:25` ("every reference each node makes, resolved — paths, symbols, counts"); `CLAUDE.md:93`; `README.md:107`.
- **Inbound:** `SKILL.md:432-433` ("this is the INBOUND half of stage 3"); `referrers.py:1,115`; `tests/test_referrers.py:1`; `CLAUDE.md:43`.

`SKILL.md:25`, `CLAUDE.md:93` and `README.md:107` each carry **only the outbound sense**.

### MARK (4)

- `SKILL.md:26`; `:119-120` ("**MARK (4) is separate from EDIT (5)** because a reviewer that fixes what it finds has destroyed the finding"); `:457`; `:515-516`.
- `CLAUDE.md:95,119`; `run_context.py:6`; `SKILL.md:413,442`.

**Where the stage name and the annotation sense meet:** `SKILL.md:83`; `SKILL.md:396-407` — **the marks table sits inside the "Stages 2–3" section, i.e. marks are emitted one stage before the stage called MARK**; `SKILL.md:138-139`; **`README.md:108`** — "Provide appropriate **editorial marks**", a third phrasing (elsewhere stage 4's output is *findings*/*verdicts*, and *marks* are the census's mechanical annotations); `apply.md:6-8`; `census.py:5,114,805`; `grade_hazards.py:15`.

### EDIT (5)

- `SKILL.md:27`; `:122-124` ("**writes at FULL LENGTH and is not allowed to consider the cap.** … Length is not one of its questions"); `:513`.
- `verdicts.py:23,593,603,606`; `compact.md:12,24,27-28,39,44-46` ("If any block is still marked incorrect or misplaced, stage 6 has not started yet. Finish stage 5."); `apply.md:28`; `review.md:32`; `residue-check.md:1,11`; `reviewer-brief.md:127`; `CLAUDE.md:96`; `README.md:122`.

**One meaning throughout.**

### COMPACT (6)

- `SKILL.md:28`; `:126-148`; `:670-693` ("⚠⚠ **This pass is not yours to run.**").
- `compact.md:1-10`; `agents/comment-review-compact.md:3`.
- `reviewer-brief.md:127-129`; `apply.md:28,32`; `review.md:32`; `run_context.py:61`; `CLAUDE.md:97`; `README.md:123`.

**Two statements of who acts:** `SKILL.md:28` and `CLAUDE.md:97` name the **task agent**; `SKILL.md:675-684`, `compact.md:98-100` and the agent file require a **separate subagent**, with `SKILL.md:684` requiring the report to say so if the task agent ran it itself. `compact.md:3` says "Loaded by the task agent", which is the loading actor rather than the condensing actor.

### APPROVAL / 7a / 7b

- `SKILL.md:29` (7a, "the run stops here"); `:30` (7b — **the "who acts" cell names the author first, then the task agent**); `:150` (stage 7 undivided); `:695-712`; `:714-721`.
- `apply.md:1`; `prove_unchanged.py:1`; `SKILL.md:188,253,609-610`; `compact.md:31,131-132`; `reviewer-brief.md:160`; `review.md:3,23,32`; `residue-check.md:1,11-13`; `CLAUDE.md:98`.
- **`README.md:124`** — "7) APPROVAL - Agent proposes the change to you." **No a/b split; the applying half is not mentioned in README's numbered list.**

### REVIEW (8)

- `SKILL.md:31`; `:152-153` ("the only stage that reads the artifact against itself"); `:723-737` ("⚠⚠ This pass is not yours to run either"; "⚠ Fix only what THIS pass created").
- `review.md:1-8`; `agents/comment-review-review.md:3`; `apply.md:125-126`; `CLAUDE.md:99`; `README.md:125`.
- **`residue-check.md:7`** — "⚠ **It is NOT stage 8's proof pass.**" — **naming stage 8 "the proof pass"**, while `prove_unchanged.py` (stage 7b) is separately called "the AST proof"/"the proof" at `SKILL.md:87` and `apply.md:45`.

**Two statements of its precondition:** `review.md:3` and `SKILL.md:725` say it runs only after 7b has written; `SKILL.md:188` says the `proof` level runs stage 8 with **no 7b at all**. **Two statements of who acts:** `SKILL.md:31`/`CLAUDE.md:99` say task agent; `SKILL.md:725-731` and the agent file require the separate subagent.

### re-review — two triggers, two stages

- **`SKILL.md:508-511`** — the fullest statement: a return to stage 4, on three triggers (angles contradict; a citation resolves to a *different* thing than the prose implies; you cannot write the replacement text).
- `SKILL.md:539,570,625-629`; `verdicts.py:12-14,420,569-573,596-604`; `tests/test_verdicts.py:624,650-651`.
- **`apply.md:70`** — a different trigger, at stage 7b: "⚠ **A non-unique match is a re-review, not a `replace_all`.** N identical matches means N blocks, and they may not deserve the same verdict." **No statement of which stage it returns to.**

### the join — no stated definition

Nearest anchor `SKILL.md:515-516` — "⚠⚠ **Run the join before you rule on anything.** It is the gate between MARK and EDIT:" followed immediately by the `verdicts.py` invocation. It names position and referent; it never says what the word means.

- `SKILL.md:515` — the act/tool; `:570-573` — the running program, referred to by a capability it lacks; `:699` — the program as a reader of the finding format ("the fields only the join reads").
- `reviewer-brief.md:41-43` — **verb form**, and **the tool is unnamed**: "A tool joins your report against the census…" Reviewers never see `verdicts.py`'s name. `:91-93` — noun.
- `CLAUDE.md:46`; `verdicts.py:1,460`; `tests/test_verdicts.py:1`.

**One operative sense throughout**, carried sometimes as noun, sometimes as verb. **Unrelated string collision:** `SKILL.md:360` "matched as ONE joined string"; `"".join(...)` throughout.

### the seven undefined terms — SETTLED 2026-08-15

Settled together, none needing a ruling: each was stated where a reader already meets it, or
deleted. **No new sections were added** — every statement went into a sentence that already
described the thing without naming it, which is why the two landing in
`comment-review-module-context.md` are line-neutral against that file's budget.

| term | outcome |
| --- | --- |
| **prose tree**, **node** | Stated together at `SKILL.md:76`. The tree is every comment run and docstring in the files under review; each is a node attached to the declaration it annotates. ⚠ The Python AST `node` in three scripts is a different sense and stays — an implementation identifier, not a term of art. |
| **the join** | Named at first use, `SKILL.md:526`: `verdicts.py`, reading every reviewer's report against the census and against the others', refusing what it cannot verify. |
| **detector** | `reviewer-brief.md:235`: a census mark read as a signal, its PRECISION being how often it is right. Placed in the section already headed "reasons to distrust a DETECTOR". |
| **banner / section banner** | `module-context.md:18`: comment lines dividing a file into named parts. |
| **assessability gate** | **Deleted.** One use, in frontmatter, and the idea was already stated without the phrase at `:30-42`. |
| **acquittal rate** | **Deleted.** A measured quantity no site gave a denominator for — the collection flagged exactly that. Both uses now name the population instead. `acquittal list` is a different term, is defined, and is unaffected. |

⚠ Two were DELETED rather than defined, which is the repo's own rule for prose nothing
consumes. A term used once and stated nowhere is not a vocabulary gap; it is a word that has
not earned a definition.

### CODE CHECK — SETTLED 2026-08-15

Stage 7b's gate, `prove_unchanged.py`. Proves **the parser reads the file the same** before
and after the write; reports UNPROVABLE rather than passing when it cannot.

- **Python** — the language's own parser, docstrings blanked. Reformatting passes.
- **Any other `LANGUAGES` record** — this repo's comment lexer; remaining lines, right-stripped,
  blanks dropped.
- **No record** — unprovable.

⚠ That should mean the code says the same, and for Python it does. Elsewhere it rests on a
lexer built from a data row, so where that lexer is unsure it refuses rather than guesses.
⚠ It compares a projection, not the file. Line endings need their own check.

Roy ruled the name over `proof`, which the editorial metaphor had already given to stage 8: in
publishing a PROOF is a trial copy read for errors, which is what stage 8 does and why its
agent is `PROOFREADER`. 7b's was a logical proof — the same spelling, an unrelated word. Roy
also caught that "identity" overstates it: *"identity is the goal, idempotent is going to be
the reality."* The code agreed — `_residue()` right-strips every line and drops blanks before
comparing, so the script's own "byte for byte" and "code identical" were wrong and are fixed.

### mark — SETTLED 2026-08-15. The census's are ANNOTATIONS; `mark` is editorial

`mark` named four things. Roy ruled the split by the metaphor the system already runs on: in
publishing, **editorial marks are what an editor writes on a manuscript** — delete, transpose,
insert, stet. That is a verdict, and it is what stage 4 emits. The census's things are
mechanical observations about the text, so they were the ones misnamed.

⚠ **The tell was in the numbering.** The marks table sat inside `SKILL.md`'s *"Stages 2–3 —
ANNOTATE, then FIND REFERENCES"* section, so the marks were made one stage BEFORE the stage
called MARK — and `SKILL.md` already called them *"annotations on a node"* while stage 2 is
literally named ANNOTATE.

| was | now | made at |
| --- | --- | --- |
| a census mark — `block.marks`, `mark()`, the `"marks"` JSON key, `names-a-symbol`, `cites-a-path`, `counted`, `coverage-claim`, `forbids-a-literal`, `repeated-literal`, `narrative-in-docstring` | **annotation** — `block.annotations`, `annotate()`, `"annotations"` | stages 2–3 |
| stage 4's name, and what it emits | **MARK**, emitting **edit marks** | stage 4 |
| "only what was marked", "an unmarked block is never written" | unchanged for now — the edit-mark sense | stage 5 |
| a work MARKER (`TODO`, `FIXME`, `HACK`, `XXX`, `BUG`) | unchanged — the `-er` keeps it apart | — |

⚠ **`"marks"` was a published JSON key.** Anything reading a saved census breaks. 25 code sites
across `census.py`, `prove_unchanged.py`, two test files and `evals/generator_split.py`.

### pCST — pseudo Concrete Syntax Tree

What the census builds: **every interval between two lines of code, as a node**. *Pseudo*
because it comes from a comment-syntax record and a lexer, not from the language's own grammar
— it knows where prose sits, not what the code means. Only Python reaches a real parser, and
only for the CODE CHECK.

Roy, ruling that every interval is a block including the empty ones: *"I don't see a way around
this pseudo-concrete syntax tree and I don't think it matters."*

⚠ Not a synonym for **prose tree**. The prose tree is the census as it stands — a node per
comment run and per docstring, so an interval holding nothing produces nothing. The pCST is
what it becomes once empty intervals are enumerated too, which is
[`an-empty-interval-has-no-census-index`](../TODO/an-empty-interval-has-no-census-index.md) and
is not done.

### obituary / tombstone — SETTLED 2026-08-16, one thing under two words

**A comment naming a symbol, file, test or flag that no longer exists anywhere.** Stated at
`agents/comment-review-block-context.md:31`, whose heading now declares the synonym:
*"## Obituaries — also called TOMBSTONES"*.

Roy's reason for declaring rather than deleting the second word, which is why this is not the
same call as `assessability gate`: *"the latest training has put those words together recently
and I don't want an agent to classify something as a tombstone and go looking for what to do
and not realize the link."* The term has to be findable by the word an agent REACHES FOR, not
only by the one this system picked. `tombstone` had appeared exactly once (`:44`, in a
measurement) with nothing tying it to the rule.

⚠ Declared in the HEADING to stay line-neutral — `comment-review-block-context.md` is at its
101-line budget, and raising that number is a ruling under `docs/limitations.md`, not a side
effect of declaring a synonym.

⚠ Observation for the distribution pass, NOT a move: `census.py` uses "obituary" eight times,
plus `write.md`, `module-context.md` and `SKILL.md` — none of which load block-context.

### load-bearing — SETTLED 2026-08-16, already clear

**A block is load-bearing at a site when someone changing THAT code would make a worse decision
without it.** Stated at `agents/comment-review-ownership-context.md:56`. No change needed: the
definition is unambiguous and the term carries one sense everywhere.

⚠ Observation for the distribution pass, NOT a move: three of its four readers cannot load that
file — `module-context.md:91`, `compact.md:40`, and the task agent at `SKILL.md:125,654,670`.

### guard / invariant — SETTLED 2026-08-16, and they were the same word

Two referents wore `guard`, and side by side they inverted:

- `function-context.md:41` — *"A guard that cannot fail is not a guard."* Here a guard is the
  TEST OR ASSERTION cited as covering a claim, and it must be able to fail.
- `reviewer-brief.md:224` (was) — *"if a test does fail it is a time-saver, not a guard."* Here
  the guard was THE COMMENT — the only thing between a reader and a wrong move, precisely
  because no test catches it.

**Roy's split:**

> **guard** — code that protects against wrong output. Weakest to strongest: `if`/`else` and
> `match`/`case`; `assert` (bypassable — `-O` strips it); raise/exception.
> **invariant** — a property the code is supposed to hold. When no guard enforces it, a comment
> is the only thing carrying it.

⚠ He first proposed `assertion` for the second. It collides: `assert` is in his own guard list,
and `function-context.md:41-42` already uses "assertion" for the code kind **in the sentence
after the guard rule**. `invariant` was taken instead — not because it was free, but because
`function-context.md:43,73,76` already used it in exactly this sense.

**What the split buys a reviewer, which is why it was worth doing.** It turns "keep or drop"
into one test: **does a guard enforce this invariant?** If yes, the comment DESCRIBES a guard —
check value, direction, units, boundary, and it is droppable if it adds nothing. If no, the
comment IS the invariant's only carrier: keep it, load-bearing wherever it sits. Roy's case: a
renderer had to hold lines to 42 characters because that is what fits his phone, the comment sat
far from the renderer, and it still had to be there with the why.

And *"a guard that cannot fail is not a guard"* stops being a rival rule — it is the **test for
which branch you are in**. A cited guard that cannot fail means there is no guard, so the
comment is load-bearing after all.

**`only-guard` is renamed `unguarded-invariant`**, which its four siblings' naming already
implied (`names-its-line`, `states-the-signature`, `derivation`, `names-its-expiry`). The old
name read as "the only CODE guard" — the opposite of what it acquits.

### own / owner / ownership — SETTLED 2026-08-16 for the placement sense; HOME retired

**The OWNER of a comment is the anchor with the best justification for the comment being
attached to it.** Roy, 2026-08-16, on which of several candidates wins: *"there is one place
where it should have already been used"* — the site where the constraint is ENFORCED.

| the code | the owner | what has to be stated |
| --- | --- | --- |
| has a GUARD | the guard | the guard's WHY |
| has no guard but is still expected to hold the invariant | that code | the invariant AND the why |

⚠ That is the `guard` / `unguarded-invariant` pair settled the same day. The acquittal already
names the second row, so the tie-breaker resolves against vocabulary that is already on the
floor rather than needing new machinery.

**Three words, no overlap:**

| word | names |
| --- | --- |
| **anchor** | the code position a comment is attached to — mechanical, whatever is there |
| **ownership** | the relation: which anchor has the best justification |
| **owner** | the anchor that wins it |

⚠ **HOME is retired.** It named the same site under a second stem. Roy: *"I would rather have
own(s)/owner as the word because the fall out of the definition of ownership and keeps the stem
of the word the same."* Six sites across three files, all line-neutral: the ownership-context
frontmatter, its `:60-65` section and `:82`, `reviewer-brief.md:279,282`, `README.md:70-71`
(whose *"reanchored"* went with it).

⚠ **The section at `:60-65` was REPLACED, not word-swapped.** It read *"the correct existing
anchor point among the sites where the claim is already stated, not the function that implements
the rule"* — which excludes exactly what the ruling names, and limited the candidates to sites
already carrying prose. The enforcing site owns the claim whether or not prose sits there today.

⚠ **`Block.owner` became `Block.anchor`.** Roy: *"fix the census.py to be anchor(s) because that
is what it is capable of doing. It finds the comment sections and ties it to the anchors."* The
field held the declaration on the line after the run ends — a position, not a judgement, and
ownership is a judgement. 12 sites in `census.py`, 6 in `SKILL.md`, 1 test. ⚠ The census emits
`vars(b)`, so this changes a published JSON key, as `marks` → `annotations` did.

⚠ **The jurisdiction sense lost the word.** A ROLE's categories of claim are its
**JURISDICTION** — stated at `reviewer-brief.md:71`, the sentence that already described it.
Roy first proposed `verify`; it collides, already naming the ACT of settling one claim against
the code (`reviewer-brief.md:184-185`) and the citation state `UNVERIFIABLE`. Jurisdiction is
which claims are a role's; verification is what it does to them. 5 sites, all line-neutral.

⚠ **The ownership/module split is PRESENCE, not shape.** Roy, 2026-08-16:
*"ownership-context is about comments that exist and where they belong — module context is
stating something about this is missing appropriate documentation."* Prose exists → whose it is
and where it goes is `ownership-context`. Prose absent → `module-context`. That is already the
verdict shapes: `move`/`drop` against `add`.

⚠ **`agents/…-ownership-context.md:51-52` went with it.** It gave ownership-context an `add`
for *"a line carrying a non-obvious constraint with no comment at all"* — missing prose, under
the role the rule assigns to existing prose. Roy: *"that statement is module-context and
function-context, not ownership-context."* Deleted, losing nothing: the case is already covered
where the constraint is enforced — `function-context.md:82-94` (*"a policy wearing arithmetic …
the code IS the decision, so nothing in it can say why that number and not another"*) and
`module-context.md:55,69` for the module surface. Ownership-context is 101 → 96 lines.

⚠ **JURISDICTIONS OVERLAP BY DESIGN.** Roy: *"different contexts can have similar requirements
in their jurisdiction because of the bottom up/top down look through the system."* The brief
already said two roles may place the same block and neither defers; it now says WHY, at
`reviewer-brief.md:286-291`. ⚠ That costs the brief one line — the largest file a reviewer
loads, ×4 per run.

### HOME / anchor / owning function — SETTLED 2026-08-16, three questions had one word

⚠ **SUPERSEDED the same day**: `HOME` is retired and the word is **owner**. The split below —
three questions, three words — stands; only the middle word changed. See
[own / owner / ownership](#own--owner--ownership--settled-2026-08-16-for-the-placement-sense-home-retired).

`home` carried three readings, and two of them sat SIX LINES APART in the same file, inverted:

- `ownership-context.md:58` — *"its **home** is the declaration it actually constrains"* — a
  place in the CODE.
- `ownership-context.md:63` — *"name which site is its **HOME** — the correct existing anchor
  point among the sites where the claim is already stated, **not the function that implements
  the rule**"* — expressly NOT the code.
- `reviewer-brief.md:283` — *"a rule with no **home in the CODE**"* — the owning function, which
  `:63` had just ruled out. And that is the file whose job is to settle the split between the
  two roles reading it.

**Roy's assignment, which is the one the system already used:**

| word | means | already used that way at |
| --- | --- | --- |
| **anchor** | the code fragment a block attaches to — declaration, assignment, expression | `add` and `split` payloads (`reviewer-brief.md:110,112`), `SKILL.md:53,55`, and enforced at `verdicts.py:308` |
| **home** | which site a duplicated claim survives at | `ownership-context.md:60-65` |
| **owning function** | the code that SHOULD hold a rule and does not | `module-context`; `reviewer-brief.md:280` |

Three questions, three kinds of answer: a **position**, a **choice among existing sites**, and a
**missing owner**.

⚠ I first proposed the opposite — `home` for the code position, a new word for the prose site.
Roy checked it against `anchor` and it was wrong: `anchor` is already the code position at four
sites and in the stage-5 gate, so `home` could only be the surviving site.

Fixed: `ownership-context.md:58` now says ANCHOR; `reviewer-brief.md:283` says OWNING FUNCTION;
and `:279` said *"`move` the claim to its **owner**"* — a fourth word, and `owner` is the
census's term for the declaration a block annotates — now HOME, matching the rule it summarises.

### budget — SETTLED 2026-08-15, split three ways. ⚠ MISSED BY THE COLLECTION

⚠ **Not in either table of `vocabulary-inventory.md` as first produced.** Twelve agents over the
whole tree did not surface a term of art used at 18 sites in four senses. **The 108-term count is
a floor, not a census** — other terms may be missing the same way, and this one was found by Roy
reading a justification, not by the sweep.

Traced to origin: the word entered on **2026-08-11**, in `redacted_corpus`'s `REDACTED_SHA_C7`,
meaning the REVIEWER's — and that first use survives verbatim today at `census.py:9`:

> a reviewer that spends its budget confirming a file exists has spent it badly

**Roy's ruling: the only real budget is what a shipped instruction file costs everyone to
load.** Not the reviewer's runtime — that reading is what justified the level ladder, and it is
the sense that loses the word. Measured 2026-08-15:

| what a run loads | bytes |
| --- | ---: |
| one reviewer — its role file + the brief | ~26,000 |
| of which the SHARED BRIEF | 18,343 (70%) |
| four reviewers in parallel | ~101,000 |
| of which FOUR COPIES of the same brief | 73,372 |
| `SKILL.md`, the task agent's | 47,438 |
| everything shipped | 224,199 |

⚠ **`docs/limitations.md` budgets the four role files only** — 28 KB of 224 KB, and not the two
largest files every run loads. Recorded there as a measured gap.

| sense | now called | where |
| --- | --- | --- |
| what a shipped file costs to load | **`budget`** | `docs/limitations.md:9` (declared), `CLAUDE.md:184` |
| a comment's line limit | **`cap`** | was `compact.md:41`, `reviewer-brief.md:294`, `SKILL.md:677`, `census.py:88,104` — `cap` was already defined at `SKILL.md:178-180` |
| the reviewer's runtime | **no term** | `census.py:9` now says "spends its READING" |
| subject matter in an example | — | `reviewer-brief.md:178`, `SKILL.md:643-649`, `module-context.md:79`. An example may be about anything |

⚠ **One site is left deliberately.** `SKILL.md:205` quotes a real run — *"I ran out of budget,
not justification"* — as the level ladder's only justification. It is a QUOTATION and is not
rewritten; the ladder itself is a separate decision, outside the vocabulary work.

### sweep — SETTLED 2026-08-15: not a term. Stage 7b is APPLY

Ruled by Roy. `sweep` was never the stage's name — `SKILL.md:16-17` (the pipeline diagram),
`SKILL.md:30` (the stage table, "APPROVAL — apply") and the reference filename `apply.md` all
said APPLY throughout. ⚠ **Later the same day APPLY moved to stage 5 and 7b became WRITE** —
applying a MARK is what stage 5 does; see the `apply` entry. Every "APPLY" below therefore
names what is now WRITE. `sweep` was a synonym surviving from `sweep.py`, the module now called
`census.py`: the word outlived its referent, which is the same failure as the dead import below.

The former senses and where each went:

**A. The applying pass (stage 7b) → APPLY**, at `compact.md:131`, `apply.md:6-8`,
`prove_unchanged.py:1,22,219,323`, `agents/comment-review-review.md:3`, `README.md:6`,
`CLAUDE.md:10,58`, `.claude-plugin/marketplace.json:12`.

**B. The place consistency is enforced → APPLY**, at `SKILL.md:273`. It was the only site
capitalising the word and the only one treating it as a named locus rather than an event.

**C. Ordinary-English "a scan over files" → KEPT, and no longer ambiguous.** Once the stage is
only ever APPLY there is no name for the plain verb to collide with, so `apply.md:67`,
`apply.md:88` ("do NOT sweep the file for departures from it" — formerly 81 lines from the same
file's stage sense), `evals/discriminators.md:58` and `CLAUDE.md:210` (this repo's own
exploration-budget rule) stand unchanged. `census.py:183` moved to APPLY instead: it names the
pass that writes, not a scan.

**D. A script name that no longer existed → `census`.** `evals/generator_split.py:37` did
`import sweep` with `sys.path` pointing at the skill's scripts directory, **which holds no
`sweep.py`**; the five attributes used at `:99-101,116-117` are all in `census.py`
(`:671,601,764,478,805`). The import could not resolve, so the script did not run. Fixed, and
`evals/grade_hazards.py:15` with it. Verified: the script now runs.

### input contract (COMPACT's narrow input)

- `compact.md:95-100` — "⚠ **This is the input contract, and it is deliberately narrow**… An agent that never saw the argument cannot keep a sentence because it remembers writing it — which is what makes this pass safe."
- `SKILL.md:138-143` — the same five items without the phrase.
- **`SKILL.md:676`** — "dispatch … with the narrow input contract **below**". **The five-item enumeration is above at `:139-141` and in `compact.md:95-96`; nothing between `:677` and `:693` enumerates it.**
- `agents/comment-review-compact.md:3,13-16`; KIND argued separately at `SKILL.md:145-148`, `compact.md:75-93`.

**The five items are identical at all four sites.** The only variance is the pointer word at `SKILL.md:676`.

### Cross-cutting, recorded without judgement

1. **The no-cap bypass arrow lands on different stages in different diagrams.** `SKILL.md:16-18` and `CLAUDE.md:84-86` run it from inside "5 EDIT" to the start of "7b APPLY"; `README.md:8-12` runs it from "edit" to "APPROVAL". The prose (`SKILL.md:28,670-673`; `compact.md:39-42`) says a no-cap run goes "straight to approval" (7a).
2. **Stages 2 and 3** have separate rows and names but a single section and a single tool invocation; `census.py:1` treats them as one unit.
3. **Two named "proof passes."** `residue-check.md:7` and `review.md:25` call stage 8 the proof pass; `SKILL.md:87` and `apply.md:45-49` call `prove_unchanged.py` (stage 7b) "the proof". Nothing distinguishes them.
4. **`README.md:105-125`** omits 7a/7b, names no actors, and describes stage 4's output as "editorial marks".

---

## Bundle 8 — the dispatch packet and its sections

### packet (run context)

- Stated at `run_context.py:1` — "The packet four reviewers are dispatched with, and its gate."
- Stated at `SKILL.md:468-470` — "You supply the run context as a PACKET, and the packet is checked before anyone is dispatched." **The two names used interchangeably in one sentence.**
- `tests/test_run_context.py:1`.

**Scope is stated narrower than its use.** `run_context.py`'s docstring calls it "the packet four reviewers are dispatched with" (stage 4 only), and `SKILL.md:457` places its construction entirely inside "Stage 4 — MARK". But two of its values are read again downstream: `SKILL.md:519` (stage 5) invokes `verdicts.py --census <census>.json --level <level>` — the same CENSUS path and LEVEL the packet carried — and `:530` calls it "this LEVEL ran" when deriving `--angles` for the same command. Whether "the packet" extends to that reuse, or is consumed with its values carried forward by hand, is not stated at either site.

### `ANGLE FILES` — SETTLED 2026-08-15, now `REVIEWER FILES`

Renamed with [angle](#angle--settled-2026-08-15-retired-in-favour-of-editorial-role). The
payload observation below stands unchanged and remains open.

- Stated at `run_context.py:47,63-65` — hint: "absolute path per angle, **the brief, and the compact + review agents**." **By the hint text the payload is SEVEN paths — the four role files, `reviewer-brief.md`, and the compact and review agent files — not the four the name suggests.**
- Stated at `run_context.py:17-21` — "ANGLE FILES carries ABSOLUTE paths on purpose. The plugin agents are namespaced and resolve only if the plugin was installed before the session started… the sanctioned fallback… is a substitution, not an improvisation."
- Checked at `run_context.py:192-204,247-250` — `_resolves()`: `Path.is_absolute() and path.exists()`; **every non-blank line is checked, not just the first.**
- `SKILL.md:279-289` — describes the fallback in terms of **the four reviewer agents specifically**, a narrower framing than the hint's payload.
- `SKILL.md:480-483` — restates the machine-checked half only.
- `tests/test_run_context.py:180-227` — a relative path is tested for CENSUS but not for ANGLE FILES; both bulleted (`- /abs/path`) and labelled (`ownership-context: /abs/path`) lines resolve.
- **Not stated in `reviewer-brief.md`** — that file never uses the literal term, saying instead (`:3`) "with one angle file each," a lowercase singular-per-reviewer phrasing that does not correspond to the section's apparent multi-file payload.

### `CENSUS`

- Stated at `run_context.py:46,62` — "absolute path, unique to THIS run." Checked at `:243-246`.
- `SKILL.md:481`; `:519` (the same value handed to the stage-5 gate, outside the packet's stated stage-4 scope).
- Related, different register: `SKILL.md:354` calls the file "the census" (lowercase); `verdicts.py:3` uses `--census census.json`, a plain argument name.

### `CAP` — SETTLED 2026-08-15: REMOVED from the packet

The collection flagged this and could not resolve it: *"Whether the packet's CAP section is
covered by 'never passed to a reviewer' is not stated… a reader must infer whether 'passed to a
reviewer' means 'used as an editing constraint' rather than 'present in the packet text.'"*

**Roy ruled it: reviewers do not get a cap.** *"They might cut something that needs to stay to
make the whole statement true."* Which is what `reviewer-brief.md:292-296` already said — an
agent that knows the cap writes to the cap, and a length-driven cut keeps the confident
assertion and drops the evidence for it.

So this was not an ambiguity but a contradiction, and the script held the wrong side: `--check`
**refused** a packet whose `CAP` was blank, enforcing the opposite of the stated rule. `CAP` and
`WIDTH` are out of `REQUIRED`; the packet is 9 sections, 6 of them unverifiable. `WIDTH` went
under the same existing rule — "Length is not an editorial role" — not a new one.

The cap still reaches stage 6 through `compact.md`'s own input contract, which is where it was
always consumed. `census.py --cap` is unaffected: a stage 2-3 CLI flag, not a reviewer's input.

### `LEVEL`

- Stated at `run_context.py:39,53,91,239-242` — checked against the `LEVELS` tuple, lower-cased and stripped.
- `SKILL.md:480-481`; `:519`; `:530`.

**One meaning throughout**, but as with CENSUS its packet-section identity is reused verbatim at stage 5, past the boundary the packet's own docstring states.

### `DOC CONVENTION`

- Stated at `run_context.py:42,56` — "google | numpy | sphinx | none found, plus a template." Not machine-checked.
- `SKILL.md:23` calls it "doc convention" (lowercase); `SKILL.md:245-247` calls the substep that produces it "doc style."
- **Not stated anywhere in `reviewer-brief.md`** — the shared brief never mentions doc convention, google/numpy/sphinx, or a template.
- **`SKILL.md:488`** gives the stated reason the section is in the packet: "The template matters because **reviewers write replacement text**. A correct sentence in the wrong docstring convention is a finding the human has to redo by hand." This sits against `SKILL.md:26-27` (MARK = "read-only, nothing written"; EDIT = the task agent writes the replacement text), the file's own frontmatter, and `reviewer-brief.md:6-10` ("A reviewer that fixes what it finds has destroyed the finding"). The packet's documented purpose (`run_context.py:6`) is stage-4-scoped, yet `SKILL.md:488` attributes this section's importance to reviewers writing text — an activity every other cited site assigns to the task agent at stage 5.

### `LSP LANGUAGES`

- Stated at `run_context.py:44,58-60` — "which answered, which had no server, or `no LSP tool — no probe possible`." Not machine-checked.
- **The literal string appears nowhere in `SKILL.md` or `reviewer-brief.md`** (confirmed by grep; the only live-tree matches are `run_context.py` and its test). The concept is stated under a different name: `SKILL.md:291` ("Probe for a LANGUAGE SERVER"), three-state table `:311-323`; `reviewer-brief.md:23-31` ("If the run context says a LANGUAGE SERVER answered…").
- **No site states that this packet section is what carries stage 1.7's three-state finding forward**, or that the brief's "the run context says" is reading it. The mapping between the field name and the concept's three-state vocabulary must be inferred.

### `FILES UNDER REVIEW`

- Stated at `run_context.py:48,66` — "one per line — the ONLY files a verdict may target." Not machine-checked.
- Stated near-verbatim at `reviewer-brief.md:17`.
- **The literal term does not appear in `SKILL.md`**, which never spells out how the list is assembled — contrast `REFERENCE ONLY`, which gets an explicit selection rule at `SKILL.md:495-502`. The nearest construction rule is 1.1's merge-base scope (`SKILL.md:214-216`) plus the `target` argument (`:180`); neither uses the term.

### `REFERENCE ONLY` — four characterizations of one section

1. **`reviewer-brief.md:15-22`** — "everything else in the repo. Read them to settle a claim. Never propose a change to them. Without this you will either treat the whole repo as in scope or, more commonly, stop reading at the boundary." The *complement* of FILES UNDER REVIEW.
2. **`referrers.py:5-13`** — "Every line it prints is a CANDIDATE. A file that names a token is a file to READ, not a file with a defect." Unvetted candidates from inbound naming.
3. **`SKILL.md:439-450`** — "It prints every tracked file that NAMES one of [the files under review]… Those files **are** the REFERENCE ONLY list you hand the reviewers at stage 4." A direct handoff of those candidates.
4. **`SKILL.md:495-502`** — "REFERENCE ONLY is a **SELECTION, not a leftover.** Name the files that settle claims code cannot: the repo's decision record…, any authority document holding dated facts, and — where the repo stages prose out of code — the extracted/mirror copy." A hand-curated selection **by document type**, explicitly rejecting the "everything else"/"leftover" framing the brief gives reviewers.
- `run_context.py:49,67` — hint matches the brief's rule, omitting the "everything else" framing.

**No site cites another to reconcile them.**

### STYLE SHEET

- Stated at `run_context.py:43,57` — "path to it, or `new — started this run`."
- Stated at `SKILL.md:262-277` — "the copy-editor's artifact and **the only thing in this skill that PERSISTS between runs**… It is binding, not advisory."
- `SKILL.md:708`; `apply.md:85`; `agents/comment-review-compact.md:13-16` (received via COMPACT's own contract, **not via the stage-4 packet**).

**One meaning throughout**, but its lifecycle spans more of the pipeline than the packet's stated stage-4 scope: read at 1.5, entered into the packet at 4, reused directly at 6, enforced at 7b, updated and handed back at 8. **No single site states the full lifecycle**; a reader assembles it from five stage sections.

### DISPATCHABLE / namespaced agent

- Stated at `SKILL.md:279-281` — "Verify the four reviewer agents are DISPATCHABLE, before anything else depends on them. They are plugin agents and their names are NAMESPACED — `comment-review:comment-review-*` — and they resolve only if the plugin was installed before this session started."
- `SKILL.md:283-289` — "Measured on all three verification runs: every one failed at stage 4 with `Agent type 'comment-review-ownership-context' not found`."
- Restated **without the word** at `run_context.py:17-21` — same fact and fallback, justifying the packet's ANGLE FILES design rather than a stage-1 verification step.
- `CLAUDE.md:107-109` — states the namespacing fact but **not** the verification step, the installed-before-session precondition, the measured 3-of-3 failure, or the fallback.
- **`DISPATCHABLE` as a capitalised term appears exactly once**, at `SKILL.md:279`, and is not reused anywhere in the live tree — defined by the sentence it introduces rather than cited as a term.

---

## Bundle 10 — the vocabulary reviewers use to judge prose

Anchors all resolve; most shifted 1-5 lines. Verified positions below.

### `truthy`

- Stated at `reviewer-brief.md:173-180` — "A sentence is **truthy** when it states one checkable proposition about the code it is attached to — a subject, a referent, and a claim that some line, symbol or run can settle." Plus: "Truthy is a property of FORM, not of truth. *'The retry budget is 40'* is truthy and false; *'this is robust'* is neither. A sentence that is not truthy cannot be `correct`ed… it is `drop` or `query`."
- Used at `agents/comment-review-ownership-context.md:32-38` — the same form-property made into two ordered questions, **acquiring a positional index the brief's definition does not carry**: truthy-*here* vs truthy-*there*, routing the difference to `reanchor` rather than `drop`.
- `agents/comment-review-ownership-context.md:3`, `:40-41`.
- **Sense carried without the word** at `README.md:64` ("is it a checkable claim about the code beside it"); the word appears nowhere in `README.md`.
- **No use in any script.** Never a parsed token.

### CHECKABLE

- Stated at `SKILL.md:574` — "confirmable from the code as it stands."
- `SKILL.md:580-581` (matrix row labels); `:255,257`; `:565`.
- **`residue-check.md:23,43,46`** — one of three conjuncts in the fixed phrase `true & necessary & checkable`, **evaluated in the opposite direction**: SKILL.md asks whether a sentence earns its place; the residue check asks whether something with the property was removed. `:43` states the conjunction is insufficient.
- `compact.md:65` — the same phrase re-run on condensed text.
- **`compact.md:58,61`** — a **gradient, not a binary**: "remove the single **least-checkable** line"; ":61 the least-checkable line is often a block's only refusal or the evidence for its surviving claim." At `SKILL.md:574-581` and in the residue check it is two-valued.
- `agents/comment-review-ownership-context.md:32,36,38` — predicated of a *proposition's form* rather than of an already-true sentence.
- **`reviewer-brief.md:206`** — "rewrite it into the checkable form", of an unparseable citation: a property of a *citation's legibility*, not of a sentence's confirmability.
- **`reviewer-brief.md:220`** — "Pure arithmetic over committed values is checkable without judgement": mechanically re-derivable.
- **`docs/parsing.md:73`** — of a proposed `LANGUAGES` row: verifiable by inspection, unrelated to the matrix.
- `CLAUDE.md:102`.

**Scope precondition stated only at `SKILL.md:583-586`:** CHECKABLE is asked only of sentences already established TRUE. A reader meeting the word at `compact.md:58` or `residue-check.md:23` without that paragraph must infer it; those files do not restate it.

### NECESSARY

- Stated at `SKILL.md:574-576` — "would someone changing this code make a **worse decision** without it?"
- `SKILL.md:578-581,255,565`; `residue-check.md:23,43,46`; `compact.md:65`; `reviewer-brief.md:230`; `CLAUDE.md:102`.
- **`residue-check.md:46`** records the conjunct misleading: "A true, checkable, apparently-unnecessary sentence can be the one place a live-but-unread config key is recorded as dead."
- **The same test stated without the word** at `agents/comment-review-ownership-context.md:56-58` and `README.md:68` — verbatim the NECESSARY question, but **named load-bearing there**.
- **Reviewers are never given the word.** `NECESSARY` does not appear in `reviewer-brief.md` or any agent file as the matrix axis. The matrix is a task-agent instrument only.

### the matrix

- Stated at `SKILL.md:574-586` — two questions, a 2×2 table at `:578-581`, scope warning at `:583-586`. Cells: checkable+necessary → "it stays"; checkable+not necessary → `drop` ("narrates what the code already says"); not-checkable+necessary → `move` ("real rationale, unverifiable in place"); not-checkable+not-necessary → `drop` ("history").
- Named "the matrix" at `SKILL.md:254,257`; `:565`; `:583`; `CLAUDE.md:102`.
- **Not named or reproduced in `reviewer-brief.md`, in any agent file, or in any script.** Reviewers emit `drop` and `move` from the verdict table's own one-line criteria, with no reference to the matrix; **nothing states whether the two descriptions are intended to coincide.**

### load-bearing

- Stated at `agents/comment-review-ownership-context.md:54-58` — "A block is load-bearing **at a site** when someone changing THAT code would make a worse decision without it. A block that would be equally useful anywhere in the file is not anchored to anything." A **positional** property.
- `agents/comment-review-ownership-context.md:3`; `README.md:68`.
- **`reviewer-brief.md:288`** — "two angles reaching one block is evidence it is load-bearing." Inferred from **reviewer behaviour**, not from the site test; no location indexed.
- `SKILL.md:123,651` — one of three properties: "true, **local** and load-bearing" — where "local" carries the positional half the angle file builds into load-bearing itself.
- **`SKILL.md:635`** — the *appearance* of the property as a failure mode: "The reviewer keeps the load-bearing-*sounding* clause — which is the claim, which is what is wrong — and cuts the **provenance** around it."
- **The triple differs by site:** `apply.md:24` "true, current and load-bearing"; `SKILL.md:123,651` "true, local and load-bearing"; `compact.md:40` "true, current, local and load-bearing" (four).
- `compact.md:40` couples load-bearing to the removal of what is *unnecessary*, treating the NECESSARY axis as what produces it.
- **`agents/comment-review-module-context.md:91`** — "Treat a heavily restated rule as load-bearing until shown otherwise, never as noise." **A different subject** (a rule, tree-wide) and **a different evidence base** (author repetition) from the ownership-context definition (a block, at one site, tested by decision quality).
- `README.md:122`; `scripts/README.md:76` (general-English use about repo rules).

### obituary

- Stated at `agents/comment-review-block-context.md:31-39` — "A comment naming a symbol, file, test or flag that **no longer exists anywhere**," plus the pointer-vs-subject test and `:41-45` "Grep the STEM, not the identifier."
- **`agents/comment-review-module-context.md:56`** — "A name in the docstring that is not in the surface is an obituary." **The reference class narrows** from "exists nowhere in the tree" to "not in this module's exposed surface" — a name present elsewhere in the repo but absent from the module's surface is called an obituary here. The pointer-vs-subject test is not invoked.
- `README.md:75`.
- **`README.md:256,273`** — a **tooling artifact**: "a vendored or gitignored tree can no longer donate its namespace and mask an obituary"; "liveness checks against the working tree **manufacture** obituaries."
- `census.py:80-82,121`; **`:607-615`** — three senses in one paragraph: a true obituary silently passed, a **false obituary** that fails loud-and-wrong, and "it can only ever suppress an obituary, never manufacture one." `:632` (emitted warning), `:696`, `:817`, `:1028`.
- `tests/test_census_names.py:53,75`; `SKILL.md:364`.
- **`evals/discriminators.md:56,68-69`** — D9 extends it to a dead name **inside a string literal**, which the block-context definition ("a comment naming…") does not cover in its own words.
- `apply.md:79` — the applying agent *authoring* obituaries ("a pass that cut seven obituaries wrote seven new ones").
- **`docs/limitations.md:7`** — applied reflexively to the skill's own prose, about a quotation that will go stale rather than a name that no longer exists.

### guard

- Stated at `agents/comment-review-function-context.md:38-50` — "does that guard exist — **and would it fail if the claim were false?** A guard that cannot fail is not a guard… Run the guard with its EXEMPTIONS OFF, and read its EXCLUSION list," with the measured 0-vs-2,026 pair.
- `agents/comment-review-function-context.md:3`; `SKILL.md:403` (the same three-part test as a mechanical resolution); `README.md:88`.
- Emitted at `census.py:839-842`; the `COVERAGE` regex at `:136-140`. **The regex's trigger set is wider than the definition's three examples and includes exclusivity phrasings that `agents/comment-review-block-context.md:47-53` owns as quantified claims.**
- **`agents/comment-review-block-context.md:70-75`** — a different test: **existence plus semantic drift** ("that the path still means what the prose says. A citation that resolves into an archive or `completed/` directory while the prose frames the gap as still open is a finding"). **The could-it-fail half is not part of this version.**
- **`SKILL.md:228-238`** — subject is the *repo's published cap/width convention* at stage 1.2, not a comment's coverage claim; **only the existence half is asked**, and the consequence is run-wide rather than a per-block verdict.
- `prove_unchanged.py:313`, `tests/test_prove_unchanged.py:77,189` — "the empty-residue guard", ordinary programming sense.

### prohibition

- Stated at `agents/comment-review-function-context.md:52-56` — "If the comment says *never a literal 65*, grep `65` in that file. A disagreement means the code broke the rule — that half is a code concern — **but a comment claiming a rule the file does not follow is a comment finding**."
- `agents/comment-review-function-context.md:3`; `README.md:89`.
- **`SKILL.md:404`** uses the mark name `forbids-a-literal`; **the word "prohibition" is not used there.** Emitted at `census.py:141-144,843-845`.
- **`agents/comment-review-block-context.md:39`** — a prohibition as a reason a dead name **legitimately survives** in prose: **the opposite disposition** from function-context, where a prohibition is the thing being tested.
- `evals/discriminators.md:29`; `evals/grade_hazards.py:55-57` (the case function-context calls "a code concern").
- **`agents/comment-review-review.md:10,18`** — "the two prohibitions" means rules binding the **stage-8 agent**, not prohibitions stated in reviewed prose.

### population

- Stated at `reviewer-brief.md:69-71` — "give the number **and the population you counted over**… a count with no stated population cannot be re-derived."
- Stated at `reviewer-brief.md:188-192` — "re-derive the POPULATION too, not only the count. Measured twice on the very claim that motivated the rule: the population was named correctly and the count was still wrong, and the population was named precisely and its size was wrong."
- `agents/comment-review-block-context.md:52-53`.
- **`agents/comment-review-module-context.md:42-43`** — "The population is the module's own AST, not sites elsewhere in the tree." **Fixed by the angle** rather than re-derived from the claim's wording. `:58-60` — **a declared choice among named alternatives** (public / private / both).
- `SKILL.md:402` — ordering stated explicitly, population first. Emitted at `census.py:835-837`.
- `verdicts.py:139-141` — the reason `SUMMARY`'s right half is exempt from verbatim checking; prose at `reviewer-brief.md:85-88`.
- **Nothing parses or validates a stated population.** The requirement is prose-enforced only.

### the existence grep

- Stated at `reviewer-brief.md:188-192` — "An existence grep passes every counted claim. The symbol is right there, so the grep returns clean and you report the file clean."
- Named "the brief's existence-grep trap" at `agents/comment-review-block-context.md:52-53`; `:3`.
- **`agents/comment-review-module-context.md:59-60`** — different wording ("existence **check**", not grep), same structure, applied to docstring coverage rather than a count.
- **The same rule stated unnamed** at `SKILL.md:407-408` ("Check the CLAIM, not the CITATION"); the brief states it under that same heading at `:182-186`, with the grep case as the counted-claim instance.
- **A related inversion**, `agents/comment-review-block-context.md:55-58`: "Finding a reader **REFUTES** a *'no reader'* claim — it never satisfies the check." The same trap under a negated claim; the term is not used.

### the acquittal list

- Stated at `reviewer-brief.md:211-231` — "the ONLY reasons to pass a block over. Closed list. If none applies, the block gets a finding." Five entries at `:215-226`. Closing at `:228-231`: "Nothing is acquitted for being SHORT, TRUE, WELL WRITTEN, NEW, or under a `⚠`… Truth least of all."
- Referenced identically at all four angle files, line 13; **no angle file restates the list or adds to it.**
- `reviewer-brief.md:235` — the boundary against the suppression list.
- **The relation to `clean` is not stated in the list itself.** `reviewer-brief.md:144-147` uses "acquitted" for the act the list governs, but the list never says which verdict an acquittal produces, nor whether an acquittal-list entry is reported. **`agents/comment-review-module-context.md:100`** treats the entries as things a reviewer *writes*, implying they are reported alongside the verdict; **the record format at `reviewer-brief.md:58-67` has no slot for one, and `verdicts.py` provides no field.**
- **`SKILL.md:662-663`** — "**Acquit on KIND, never on LENGTH**": a sixth acquittal criterion, stated to the task agent and **absent from the brief's closed list**. Whether "closed" binds the task agent as well as reviewers is not stated at either site.
- `SKILL.md:585` (verb form, about the matrix).

### states-the-signature

- Stated at `reviewer-brief.md:216-217` — "short, present tense, matches name/args/return, cites nothing outside itself." **"Short" is undefined here, and `:228` separately forbids acquitting anything *for being* short.**
- **Zero occurrences anywhere else** in the plugin tree, `README.md`, `CLAUDE.md`, `docs/`, `evals/`, `tests/`, `scripts/`. Not a token any script reads.
- The nearest use is `agents/comment-review-function-context.md:18-21`, which lists the disagreements between name, signature, docstring and body **without naming this entry** — the angle that would apply the acquittal states its inverse and never names it.

### derivation

- Stated at `reviewer-brief.md:218-222` — "a hand-worked calculation whose digits stop an assertion being an echo. ⚠ **Not an acquittal until you have re-run the arithmetic**… Measured: one worked example was wrong, its first correction was *also* wrong, and all three versions rounded to the same asserted value."
- **`agents/comment-review-module-context.md:108-111`** — `derivation` used as **a label a reviewer emits per block**, misapplied at scale. **This is the only evidence in the live tree that an acquittal entry is written down per block; the brief does not say so.**
- **Related without the term:** `agents/comment-review-block-context.md:24,77-83` reaches the same object (a hand-worked calculation) from the finding side — a claim to execute and `correct` if wrong. **Neither site cross-references the other.**

### only-guard

- Stated at `reviewer-brief.md:223-224` — "a warning against a plausible wrong move where **nothing goes red** if someone makes it. Verify that; if a test does fail it is a time-saver, not a guard." **The disqualifying case is stated but the consequent verdict is not named.**
- **No use anywhere else.**
- The same shape appears un-named and **from the opposite direction** at `agents/comment-review-function-context.md:64-77`: "enforced by… nothing at all → the prose owes **everything.** Unwritten means nonexistent"; "A deliberately unenforced rule is indistinguishable from an oversight." There an unenforced-but-real rule generates an `add`; in the acquittal list an existing warning about an unenforced wrong move is a reason to pass the block over. **Neither file names the other.**

### names-its-expiry

- Stated at `reviewer-brief.md:225-226` — "states the condition under which it stops being wanted. ⚠ Not an acquittal once that condition has already been met."
- **No use anywhere else.**
- Adjacent content carrying the sense without the word: `census.py:87-90` and `SKILL.md:240-243` on work markers (a pointer to filed work rather than a stated expiry condition, handled by cap exemption not acquittal); `agents/comment-review-block-context.md:28-29` lists dated rulings as *findings* — a dated ruling whose date has passed is the lapsed case of this acquittal, **but the two are not connected in either file.**

### the suppression list

- Stated at `reviewer-brief.md:233-246` — "reasons to distrust a DETECTOR. The acquittal list excuses a *block*. It can never silence a *detector*, and a noisy one buries its own hits." Four measured entries at `:239-243`: a date/path inside a runnable command line (4/4 false); a bare identifier that is also a module stem (8/8); a warning glyph as such (45/0, "the single largest class in one run, zero defects"); a repo-relative path resolved only against the repo root (80/84, 18/20, 2/2).
- **`census.py:147-149`** — cites the list as the rationale for a **mechanical** suppression already implemented (`DATEISH` stripped before `NUMBER`). The brief's list is a reviewer-side reporting instruction; this site is the code pre-empting one of those shapes so the reviewer never sees it.
- **`census.py:760-780`** — the fourth entry's underlying fix, carrying **the same three measured ratios**. The brief presents them as a reason to distrust the detector; the script presents them as why the detector was changed. **Nothing states whether the brief's entry is still live now that suffix indexing exists.**
- **Not referenced by name in any agent file, in `SKILL.md`, or in `README.md`.** The four angle files reach it only through the blanket pointer at line 13, which names the acquittal list and not this one.

### batch to triage

- Stated at `reviewer-brief.md:236-237,245-246` — "**A detector below roughly 10% precision is a batch, not a finding.** Reporting it raw spends the human's attention on a list they will learn to skip, which is how a real hit gets lost." **The threshold is hedged ("roughly") and the precision is to be measured by the reviewer on its own run; no site says against what baseline, nor over what sample size.**
- **No other use of the phrase in the live tree.** **No record field carries a batch** — `reviewer-brief.md:45-56` and `verdicts.py:73-83,207-260` define only `--- FINDING` records and `CLEAN` ranges. A batch has no `VERDICT`, so **how a batched block is accounted for against the coverage check at `reviewer-brief.md:90-93` is not stated**; a reader must infer that batched blocks go into `CLEAN` ranges, or that a batch is reported outside the record format the way `CODE CONCERNS` is.
- Adjacent measurement without the term: `README.md:141-152` reports ~70 firings producing ~2 real findings across seven corpora — roughly 3%.

### CONSERVATIVE ON MEANING / FREE ON FORM

- Stated at `SKILL.md:161-165` — "An editor rules on form; the author rules on what a sentence claims. With the author not reading, you may fix wording, placement and length on your own judgement — but every change to what a sentence CLAIMS needs evidence in hand, or it is a `query`." Premise at `:157-159`.
- `SKILL.md:629` — invoked as a prohibition on letting the synthesis order resolve a contradiction.
- **The same principle without the phrase** at `reviewer-brief.md:114-118`. **Reviewers get the mechanism but never the name or the absentee-author premise**; the phrase appears in no agent file, no reference file, no script, and not in `README.md`.
- Applied form at `apply.md:40-43`.
- **Tension recorded, not judged:** `SKILL.md:164` grants freedom over "wording, placement and length on your own judgement", while `SKILL.md:276-277` makes the style sheet "binding, not advisory" over wording and `apply.md:90-93` puts "a change no verdict asked for… a re-spelling, a dialect harmonisation, a de-personalisation, an alignment with the neighbours" out of scope. FREE ON FORM and the out-of-scope rule describe the same class of edit with opposite permissions; **the reconciling clause is at `apply.md:85-88`** — form freedom applies "only inside blocks a verdict already opened."

**Inventory accuracy note:** the inventory marks `truthy`, CHECKABLE, NECESSARY, the matrix, load-bearing, obituary, the acquittal list, the four acquittal entries, the suppression list, batch to triage and CONSERVATIVE ON MEANING as ONE. On the tree as it stands, **CHECKABLE, NECESSARY, load-bearing and obituary each appear at many sites beyond their stated one.** `states-the-signature`, `only-guard` and `names-its-expiry` appear at exactly one site each and nowhere else.

---

## Bundle 12 — roles, corpus, infrastructure, run arguments

Anchor drift (all `SKILL.md` anchors ~1-3 lines high): editorial board `:10-13,161`; author `:157-159`; task agent `:167-171`; REVIEWERS `:173`; cap `:177-179`, applied `:209-210`; `target` `:180`; merge base `:214-216`; width `:218-226`; LSP `:291-323` (table `:313-317`) plus `:410-430`; liveness `:302-303,419-421`; name corpus `:325-336`; FLOOR `check_shipped_syntax.py:23-27`.

### editorial board

- Stated at `SKILL.md:10-13` — "Four editors read the same manuscript from four angles, a copy editor writes one set of edits, a condenser cuts them to fit, the author approves **that** text, and the page is proofed."
- Stated at `SKILL.md:161` — "an editorial board with an absentee author, and one principle follows."
- `CLAUDE.md:8-11`; `README.md:3-6`; `.claude-plugin/marketplace.json:12`.

**One meaning throughout. The role labels inside the metaphor are not stable:** `SKILL.md:10-13` names four editors, a copy editor and a condenser; `:162` uses "editor" for the role that rules on form; `:264` calls the style sheet "the copy-editor's artifact"; `README.md:4` calls the same actor "an editor". All refer to the task agent.

### author — four referents

**(a) the human who approves the run.** Stated at `SKILL.md:157-159` — "The HUMAN is the AUTHOR, and is absent. They approve almost everything, quickly, unaudited — a direction, not a diff. So every proposal must be safe to approve blindly. Their disagreement is valuable; it is not a safety mechanism and must never be used as one." Also `:29-30,36,132-136,161-163,628,686-688,702,705-706,721`; `compact.md:3,7,31,132`; `apply.md:29-30,122`; `review.md:32-34`; `reviewer-brief.md:160`; `README.md:5,15`.

**`README.md:124`** characterises the same person differently: "APPROVAL - Agent proposes the change to you - they messed it up for me so I don't trust them to do it twice." `SKILL.md:157-159` characterises them as approving "almost everything, quickly, unaudited."

**(b) the writer of the prose being measured** — `evals/generator_split.py:8,11,86,122`; `corpora/corpora.toml:47-51`; `agents/comment-review-module-context.md:90`.

**(c) the developer of this repo** — `scripts/check_shipped_syntax.py:6`; `scripts/README.md:73`; `CLAUDE.md:159`.

**(d) manifest metadata** — `plugins/comment-review/.claude-plugin/plugin.json:4`.

**As a verb, "write from scratch", contrasted with cutting:** `compact.md:57,59` ("Cut, do not re-author"); `apply.md:102-104` ("2 of 28 authored docstrings were confirmed false").

### task agent

- Stated at `SKILL.md:167-171` — "**The TASK AGENT — you.** … You are the only participant that writes, and only after approval… 'compact + correct' is not a finding."
- `SKILL.md:23,27,28,29,30,31,33,3`; `CLAUDE.md:9,80,89,96,97,99`; `apply.md:3`, `compact.md:3`, `review.md:3` (each says "never by a reviewer"); all six agent files at `:9`; `reviewer-brief.md:97,115,123,141,156`; `agents/comment-review-module-context.md:104`; `verdicts.py:5`.

**One meaning throughout.** Two other names for the same actor in the metaphor register: "the copy editor" / "an editor."

### REVIEWERS

- Stated at `SKILL.md:173` — "read-only, one angle each, and never see this file."
- Stated at `reviewer-brief.md:3,6-13`.
- `SKILL.md:26,119-120,279,354-356,413,457,483,488,590,712`; the four agent files at `:3,7`; both manifests.

**Sites where the word carries a different referent:**

- `SKILL.md:273` ("no fifth reviewer for this") and `apply.md:86` ("no copy-editing reviewer") — establishes reviewer = angle agent specifically.
- `agents/comment-review-compact.md` and `-review.md` are dispatched agents **never called reviewers**; `compact.md:4` says "Never by a reviewer."
- **`docs/limitations.md:5,31-33`** — a **human** reading a change to the skill's own files.
- `reviewer-brief.md:237` — a reviewer on a *later run*.
- **`reviewer-brief.md:81` and `SKILL.md:550`** — "fabricated **5 of its 7** reviewer reports." **The count is seven; every other site fixes the reviewer population at four (or fewer at a restricted level). Nothing at either site says what the seven were.**

### prose tree — no stated definition

Nearest: `SKILL.md:24` and `:75-88`, which describe the thing without defining the phrase. `:75-76` — "Every comment run and every docstring is a node, attached to the declaration it annotates"; `:80-88` — "coverage is a tree walk"; "four visitors over one tree"; `:89` — "The model is the tree."

- `CLAUDE.md:9,92,124`; `README.md:4`.
- **Both manifests carry the phrase in the text a user sees at install time** — `.claude-plugin/marketplace.json:12`, `plugins/comment-review/.claude-plugin/plugin.json:3` — **and neither they nor any file reachable from them defines it.**

What a reader must infer at every site: that "tree" is the block/owner structure `census.py` prints as **a numbered flat list** (`N  file:start-end  kind  lines  marks  (owner)`, `census.py:1013-1016`) — **the output is a list, and the word "tree" appears nowhere in `census.py`'s own prose**. Also that "node" is a *block*, not the Python AST node the same scripts manipulate.

**Bare "tree" carries other senses nearby:** the filesystem/source tree (`census.py:604,631,765,777`); the `move` **destination tree** (`SKILL.md:59,252`; `reviewer-brief.md:123`; `agents/comment-review-ownership-context.md:80`).

### name corpus

- Stated at `SKILL.md:325-336` — "This substep CHOOSES the source; the corpus itself does not exist until stage 3, because `census.py` builds it." Construction rules at `:333-336`: from the AST never raw text ("text contains the comments being checked, so everything passes"), skip `pyvenv.cfg` dirs, never harvest string constants from tests, exclude `.md`/`.txt`, resolve a dotted name on its head segment.
- Stated at `census.py:601-668` — "Every name the tree DEFINES, from the AST — never from raw text." **Adds two properties not in `SKILL.md`:** unreadable files are *returned* not dropped (`:607-609`), and **tracked files only** where git can answer (`:611-616`, measured: "`asanyarray` resolved ALIVE in a repo that does not define it because a fetched corpus sat in the working tree — SILENT and one-sided").
- `census.py:79-82` (POISONED by a virtualenv), `:631-633` (degraded-mode string), **`:694` — the variant term "live-name corpus" for the same object**, `:1027-1030`.
- `SKILL.md:363-364`; `README.md:139,254`; `tests/test_census_names.py:1`.

**Entirely distinct from corpus/corpora below; the two are never disambiguated at any site, and `census.py:611-616` uses both in one paragraph** ("TRACKED files only … because a fetched **corpus** sat in the working tree").

### liveness

- Stated at `SKILL.md:302-303` (the LSP table row) and `:419-421` — "`workspaceSymbol` answers whether the name exists at all… `findReferences` answers whether anything uses it, which is the stronger claim a comment usually makes." **So liveness covers two different questions, and the text distinguishes them.**
- `SKILL.md:322,325`; `docs/parsing.md:20,39,45-49,146-149`; `README.md:152,272-273`.
- **`agents/comment-review-block-context.md:55-58`** — a **different sense**: a property *the prose claims*, not a check. "This checklist is naturally better at prose over-claiming LIVENESS than DEADNESS."

### tracked

- Stated at `census.py:732-744` — "**None is a THIRD state, not an empty list**: 'this is not a git checkout' and 'this checkout tracks nothing' lead to different fallbacks." `:756-761`.
- `census.py:611-616` (name-corpus boundary); **`:777-781`** (citation-resolution boundary, a distinct consequence: "a citation into gitignored runtime state is UNVERIFIABLE… a different finding from a citation that resolves nowhere. Measured on one repo, 6 of 20 'dangling' reports were gitignored state"); `:829`.
- `SKILL.md:400`; `referrers.py:1,14,114-116,169`; **`prove_unchanged.py:217-236,261`** (a different purpose for the same boundary: choosing an untouched sibling).
- `SKILL.md:439`; `CLAUDE.md:43`; `README.md:139,254`; `tests/test_census_names.py:1`.

**One meaning throughout: in `git ls-files`.** What differs by site is what the boundary buys. `path_index` (`census.py:792-797`) falls back to a full `rglob` when the list is None **or empty**, and says so at `:787-791`.

### `CANDIDATE`

- Stated at `census.py:15-18` (a backticked token "can name a config key, a record field or an API payload rather than a symbol"), `:26-29` (extended to placement), `:820` (emitted note), `:994-998`, **`:1033-1038`** — the census's own output splits its two kinds: **candidates vs facts**.
- Stated at `referrers.py:11-13`, `:195-196`.
- `SKILL.md:101-102`, `:424-425` ("A server does not settle a claim, it settles a FACT… What changes is the cost of checking, not who decides"); `docs/parsing.md:21`.

**One meaning throughout.** Two object types carry it — a *mark/note* on a block, and a *file*; `SKILL.md:101` and `parsing.md:21` extend it to a *verdict*.

**Separate sense:** `scripts/find_llm_repos.py:11,15-17` and `scripts/README.md:56` use "candidates" for shortlisted repositories; `referrers.py:45-46` for printable per-token hits.

### `NOISE_FLOOR` / SUPPRESSED (the `referrers.py` sense)

- Stated at `referrers.py:14-18` — "A token appearing in more than NOISE_FLOOR tracked files is reported as SUPPRESSED with its hit count, never dumped as a per-file list: past that many files, the token is describing the codebase rather than this one."
- `referrers.py:45-47` (`NOISE_FLOOR = 40`), `:146-148`, `:172-175`; `SKILL.md:440-441`; `tests/test_referrers.py:233,245-247,285-290`.

**The constant is named `_FLOOR` and functions as an upper limit** (`referrers.py:45` calls it "a cap"); **nothing at any site reconciles the name with the direction.**

**Where the words meet other mechanisms:** `reviewer-brief.md:233-247` (the suppression list — a different object and a different actor), pointed at by name from `census.py:148-149`; `census.py:80,615` — suppression as an **accidental failure**, not a designed filter; `agents/comment-review-function-context.md:45` — a guard's exemptions hiding failures; `CLAUDE.md:164`, `scripts/README.md:82` — the linter sense.

### NOT CHECKED

- Stated at `census.py:1022-1030` and `referrers.py:176-193` — **the same header string verbatim**, over different populations with different closing notes.
- `referrers.py:158-167` — an empty `hits` with pending `unsearched` prints a *qualified* absence rather than "none".
- `census.py:677` — "a file the walk never yields cannot appear in the NOT CHECKED list either."
- `tests/test_referrers.py:105,204`.

**One meaning throughout.**

### LANGUAGE SERVER / LSP and its three states

- Stated at `SKILL.md:291-297`, `:299-303` (it buys exactly two things: block ownership and name liveness), `:304-309` ("**LSP RETURNS NO COMMENTS**, so it can never replace `census.py`").
- **The three states at `SKILL.md:311-320`:** (1) a server answered; (2) no server for this language; (3) **no LSP tool at all** — "The third is not the second… Say a probe was impossible. Measured: three runs hit this state and all three had to improvise the distinction."
- `docs/parsing.md:18-22,24-43` — **states two of the three; the "no LSP tool at all" state appears only in `SKILL.md`.**
- `SKILL.md:410-430`; `run_context.py:44,58-60` (the three states as a fill-in hint); `reviewer-brief.md:23-31` ("a server that is ABSENT proves nothing"); `docs/parsing.md:146-149`; `CLAUDE.md:132-134`.

**The three-state distinction is stated in full at exactly one place.**

### detector — no stated definition, two senses

**(a) one mechanical mark and its precision:** `reviewer-brief.md:233-246`; `census.py:148-149` (`repeated-literal`), `:769-771` (the path resolver, 80/84 · 18/20 · 2/2); `docs/parsing.md:45-47` (`names-a-symbol`); `README.md:151-155,258-260`; `corpora/corpora.toml:3`.

**(b) the whole comment-review instrument, as a device being calibrated:** `README.md:130-132,138-143`; `corpora.toml:5-7,58-59,107-110`; `fetch_corpora.py:115-118`.

**`README.md:141` ("a different detector") and `README.md:152` ("the mechanical detectors") are three sentences apart and use the word in the two different senses.** `fetch_corpora.py:115-118` and `corpora.toml:13-16` state the same claim with different subjects — "**the detector** is measuring noise" vs "**the tool** is measuring noise."

### corpus / corpora

- Stated at `fetch_corpora.py:1-14` — "⚠ Every corpus is pinned, and a fetch that lands on a different ref than the manifest names is a hard failure rather than a warning. A moving corpus makes a regression indistinguishable from the corpus having changed underneath the measurement."
- Implemented `:58-68`, `:71-92`, `:135-145` (the pin is re-verified after the fetch: "a tag can move, and `--branch` silently accepts a branch").
- Manifest fields at `corpora.toml:18-22`; `expect` at `:13-16` and `fetch_corpora.py:115-118`; `depth` at `fetch_corpora.py:77-79`.
- `CLAUDE.md:169-176`; `README.md:192-210`; `scripts/README.md:6-36`; `generator_split.py:1,5-9,86,95-97`; `find_llm_repos.py:5-11`; `corpora.toml:31-37,112-165`.

**Two path/label observations at these sites:** `find_llm_repos.py:3` documents its own invocation as `python corpora/find_llm_repos.py` while the file is at `scripts/find_llm_repos.py` (both `scripts/README.md:45` and `CLAUDE.md:37` invoke it as `scripts/`); and **`corpora.toml:22` names the docstring-convention step "stage 0.3" where `SKILL.md` numbers it 1.3.**

### assisted / human / mixed / unknown

- Assigned at `generator_split.py:144-152`; the trailer test at `:39-45` ("Broad on purpose: a false positive dilutes the contrast and understates the effect, which is the safe direction"); reported at `:164-180`.
- Scoped at `:14-20` and `:182-186` — "A trailer means an assistant was involved in the COMMIT, not that it wrote the prose… Read this as a correlation worth following, not a result."
- Invalidation at `:120-140` — >10% of blamed lines on a graft exits 2. Measured: "a depth-2000 checkout put 1177 of one file's 1364 lines on the graft point."
- **`corpora.toml:160-164`** restates the same class of failure with different numbers: "A depth-2000 fetch put 96% of blamed lines on the graft commit… the split reported 1213 assisted blocks against 28 human." (1177/1364 ≈ 86% on one file; 96% overall on sentry.)
- `scripts/README.md:31-36`.

**One meaning throughout.** `unknown` = no blame answer for any line, printed but excluded from the marks table.

### discriminator (D1–D12 / hazard) — two names, nowhere equated

- Stated at `evals/discriminators.md:1-8`; cases at `:12-74`; grading rule at `:78-88`.
- **Called hazards** at `grade_hazards.py:1` (constant `HAZARDS`, `:33-65`); `CLAUDE.md:31,149`; `README.md:187,223`; `corpora.toml:33-34`; `evals/evals.json:3`.

**Base refs for the same base tree differ across sites:** `discriminators.md:3,8` says `REDACTED_SHA_H`; `grade_hazards.py:30` sets `BASE = "REDACTED_SHA_A"`; `evals.json:3` says "a fresh worktree from REDACTED_SHA_A (master)"; `corpora.toml:28` pins at `REDACTED_SHA_A`.

**`evals.json:3` cites pass criteria at `docs/skills/comment-review-triage.md` and `scratchpad/ga/discriminators.md`; neither path exists in this tree** (the file is `evals/discriminators.md`).

**The two files disagree about which cases have no text signature.** `grade_hazards.py:33-65` marks **D3 and D12** non-gradeable and `:55-58` explains both; the module docstring at `:17-20` names only D12. `README.md:223-225` says "Two of the twelve hazards are positional or leave true prose standing."

**Unrelated senses:** `referrers.py:173` ("too common to discriminate"); `README.md:216-217`; **`docs/limitations.md:18`** — "state the rule and its **discriminator**, not the argument for it," where a discriminator is the distinguishing test inside a written rule.

### GONE / REDUCED / SURVIVES / NEEDS-EYES / PROBE-MISS

All five are printed by `grade_hazards.py` and stated only by the code that emits them.

- Scoping precondition `:91-97` — only hazards whose file appears in `git status --porcelain` are considered ("the other eight sit at base, so they 'SURVIVE' trivially and the score is a fiction").
- `PROBE-MISS` `:102-108` (probe text not found in the base blob; not counted in `scored`); `NEEDS-EYES` `:112-118` (non-gradeable-by-text; counted in `eyes`, not `scored`); `GONE` `:120-122`; `REDUCED` `:123-125`; `SURVIVES` `:126-127`.
- Matching is whitespace-normalised with `#` stripped (`:68-70`), "because prose WRAPS."
- Summary `:128-133` — "GONE/REDUCED is necessary, not sufficient — read the replacement to judge whether what now stands is TRUE."
- `README.md:223-225` uses `NEEDS-EYES` in the same sense.

**One meaning throughout.**

### FLOOR

- Stated at `check_shipped_syntax.py:23-27` — "The oldest interpreter a shipped file must parse on. Not a packaging floor -- there is no package here -- so it is stated once, in code, where the check that enforces it can read it."
- `:1-15` (the reason), `:68-98` (enforcement), **`:44-63`** (`runtime_defects` — constructs that *parse* at the floor and fail there at runtime: a PEP 604 union inside `isinstance()`, "TypeError before 3.10, invisible to a syntax check"), `:31-36`, **`:41`** ("a checker that uses the construct it refuses is one formatter run from being the defect").
- `CLAUDE.md:66,74,155-167`; `scripts/README.md:61-86` ("Measured 2026-08-14: three files were already in the unparenthesised form, one of them the census script this skill hands to strangers. Confirmed by mutant").
- Carried in the shipped files as a comment **without the word**: `census.py:52-77`; `run_context.py:82-87`; `referrers.py:31-34`.

**Unrelated senses:** `agents/comment-review-function-context.md:86` (an invented example about rounding direction); `corpora.toml:68` ("A near-floor reading"); `referrers.py:47` (`NOISE_FLOOR`, an upper threshold).

### worktree — three senses (the inventory recorded two)

**(a) corpus isolation:** `fetch_corpora.py:5-7,59,65,68`; `corpora.toml:18-19`; `CLAUDE.md:25,173`; `README.md:204-206`; `scripts/README.md:20-23`.

**(b) eval-run isolation:** `grade_hazards.py:7,11-13,87`; `evals.json:3`; `CLAUDE.md:32`; `README.md:220`.

**(c) the checkout a review is running in** — not in the inventory: `SKILL.md:341`; **all four angle files at `:11`, verbatim** ("take the absolute path from the prompt, because a relative one does not resolve from a worktree"); `census.py:768`; `reviewer-brief.md:194-198` ("an archive absent from every worktree" — here any checkout of the repo).

### cap

- Stated at `SKILL.md:177-179` — "**This skill has no cap of its own** and must not invent one."
- Stated at `SKILL.md:209-210` — "APPLIED IN STAGE 6 AND NOWHERE ELSE… never passed to a reviewer. Length is not an angle."
- Sourced `SKILL.md:218-226`; exemptions `:240-243,386-390`; counting rule `:384-385`.
- Implemented `census.py:100-111`, `:88-96`; applied `:977-984,1001-1007`, `:892`.
- Kind rule `SKILL.md:145-148`; `compact.md:79-93`; `census.py:443-445`; `docs/parsing.md:85-87`.
- **Withheld from reviewers:** `reviewer-brief.md:127-129`, `:293-297` ("**You are not given the cap.** … An agent that knows the budget writes to the budget, and what survives a length-driven cut is the confident assertion, never the evidence that lets a reader test it").
- `SKILL.md:197-201`; stage-6 gate `SKILL.md:670-673`, `compact.md:37-42`; ceiling `compact.md:102-114` ("Between a comment that is over the cap and one that is in-cap and unfalsifiable, the over-cap one is correct and the in-cap one is a defect wearing a passing grade").
- `run_context.py:40,54`; `docs/limitations.md:43-44`.

**One meaning throughout for the run argument.** Two neighbouring uses for other budgets: **`docs/limitations.md:9-14`** deliberately contrasts the skill's own per-file **budget** with "the cap rule for comments" ("a comment must be true about ONE thing, so cutting to fit deletes its evidence; a rule must cover MANY, so cutting to fit forces the covering abstraction"); `referrers.py:45` calls `NOISE_FLOOR` "A cap"; `agents/comment-review-function-context.md:86` uses "the cap" inside an invented example.

### width

- Stated at `SKILL.md:218-226` — "**Two separate questions, and either may be absent.** A cap bounds the LINES in one `#` run; a width bounds the CHARACTERS in one line… Measured: a run chose a width out of a contributing guide on its own judgement, and the census then printed `over width (72): 2` as though it were an established project fact."
- `SKILL.md:453-455`; `census.py:893,985,1008-1009,987,1000`; `:488-490`; `run_context.py:41,55`; `CLAUDE.md:21-22,89`.
- **Different sense** at `agents/comment-review-module-context.md:79` — "A width budget is owned by the function that composes the text": a constraint on an artifact the *reviewed code* produces, used as an example of naming an owner.

### `target` — four senses

**(a) the run argument:** `SKILL.md:180` ("**replaces** the diff scope, never intersects it"), `:8`, `:447-450`; `compact.md:50-53`; `referrers.py:8`.

**(b) the verb — what a verdict may point at:** `reviewer-brief.md:17,185`; `run_context.py:66`; `referrers.py:12,154`.

**(c) a script-local variable:** `referrers.py:131-133,109`; `prove_unchanged.py:217-236,266-312`; `verdicts.py:348-359`; `generator_split.py:95-97`.

**(d) ruff's `target-version`:** `CLAUDE.md:157,165`; `census.py:53`; `check_shipped_syntax.py:32`; `scripts/README.md:69-72`.

### merge base

- Stated at `SKILL.md:214-216` — "`git merge-base HEAD <upstream>`, then `git diff --name-only "$base"..HEAD`. Never `A...B` between two tips, never a `HEAD~1` fallback; both silently narrow."
- **`compact.md:50-53`** — the base is also where the *original* pre-edit prose is read from, and states the case where it does not exist: "`git show HEAD:<path>` when `target` replaced the diff scope, because then 1.1 never ran and `<base>` has no referent."
- `apply.md:48`; **`prove_unchanged.py:3`** — the script names the parameter `ref`, not merge base; `CLAUDE.md:60,89`.

**One meaning throughout**, serving two purposes: the diff that defines scope, and the blob that defines the original text.
