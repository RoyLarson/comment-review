# Removal map: ruling #259 (Python and Rust only, the rest freeform)

Checkout: `feat/python-and-rust-only` at `a02a4030`. Read-only. All paths are relative to
`src/comment_review/` unless they begin `tests/`, `docs/`, `scripts/`, `src/plugin/`.

## How this was measured

- Name users: word-boundary search over `src/`, `tests/`, `scripts/`, `evals/`, then read by hand
  (false hits removed: `_Grammar` in Rust, `_leading`, `_gaps`, `BLANK` as a word in comments).
- **Uninstall probe.** `git archive HEAD` into the scratchpad; `READER_METADATA` emptied in
  `reading/language.py` of the copy only, so only Python and Rust install. Full suite run there.
  Baseline copy: 6467 passed, 1 skipped. Probe: 915 failed + 6 errors = 921, 5504 passed,
  2 skipped; 42 ids gone from collection (6468 -> 6427 net).
  It simulates uninstalling; it does not delete a module, so import breakage in section 7 is static.
- CLI behaviour below marked MEASURED was run on small git repos against HEAD and the probe.

## Summary of findings that change the plan

1. **Python and Rust never touch `Language`, `read_lexical` or `declarations()`.** No file under
   `reading/python/` or `reading/rust/` imports `reading.lexer`, `reading.stripped` or
   `reading.language`'s rows. They reach `lexer.py` only through three indirect surfaces:
   `Paragraph.text` -> `comment_form`, `desk/marks/rules.py` -> `comment_form`,
   `binder/page.py` -> `leading_between`. Plus `NAMED_DEFS` in `concordance/`.
2. **A freeform-only binder is refused today.** MEASURED: `topology --build` over a zero-page
   binder exits 2, `stage '4': 'ownership-context' split 1 ways over 0 pages`
   (`flows/topology.py:100-102`). Compose must count freeform paths.
3. **The summary line would say "proven" over a freeform file.**
   `commands/prove_unchanged.py:43,48` prints `len(args.paths)` as "paths proven". Counting
   freeform in `unchecked` with no other change breaks "never PROVEN". The summary needs its own
   count.
4. **Follow-on orphans.** `PythonRead` and `RustRead` both answer `a_series` True and
   `closing_docstring` False (`reading/python/records.py:301-314`,
   `reading/rust/records.py:383-397`). So after removal `a_series=False`, `closing_docstring=True`,
   `Cues.closing_documentation`, the `a` at `<eof>` and the `b.anchor == EOF` branch at
   `binder/page.py:770-771` have no input. Note `cue()` DEFAULTS `closing_docstring=True`
   (`reading/addresser.py:751`), a default no real read uses.
5. **Open decisions**: section 10. The largest is what "the rest" means for `.md`, lockfiles and
   binaries; the literal reading sends every non-code file to four reviewers.

---

## 1. `reading/lexer.py`, each top-level name

Nothing in `results/compositor.py` imports from lexer (its only `BLANK` hit is a comment word at
`:87`). `flag_structural_docs`: not in `src/`; it survives only in the old `plugins/` copy,
`prototype/`, `docs/` and `TODO/`.

| name (line) | used outside by | verdict |
| --- | --- | --- |
| `__all__` (61), re-exports | `tests/test_line_endings.py:14` takes `language_for` through it; `scripts/measure_binder.py:41` takes `Kind` through it | dies; fix both imports (`Kind` -> `reading.series`) |
| `NAMED_DEFS` (69) | `concordance/code_names.py:17`, `concordance/referrers.py:34` | **survives -> `concordance/names.py`**. Both users are concordance, a leaf that area may hold (`names.py` already took `SYMBOLISH` from the lexer the same way). Also closes `lexer-and-language-findings` T42. Comment at `referrers.py:23-33` goes |
| `_join` (80) | `_comment_fragment` only | survives with `comment_form` |
| `COMMENT_SCANNERS` (93) | none | survives with `comment_form`; one entry, may reduce to a direct call |
| `_Grammar` (99) | none (`rust/scanner.py` hits are its own word) | survives; drop field `lang` |
| `_grammar_for` (115) | none | survives; drop `language_for` |
| `comment_form` (133) | `desk/marks/rules.py:30,37`, `reading/paragraph.py:178,180`; tests below | **survives, reduced**. Lines 154-225 become `chunks = [raw_text]`: the row loop runs only when `lang is not None`, which is never true for Python or Rust. See home below |
| `_opens_comment` (233) | none | dies, called only from the row loop |
| `_scanned_form` (240) | none | survives (Rust) |
| `_comment_fragment` (302) | none | survives, minus `:344-359` and `:378-385` (row branches) |
| `ESCAPE_WIDTH`, `_closes_a_character` (508, 511) | none | die with `scan_strings` |
| `BLANK` (548) | `reading/stripped.py` only | dies |
| `scan_strings` (551), `run_ends` (599), `AfterCloser`, `after_closer` (646, 657) | `stripped.py`; `tests/reading/test_lexical.py` | die |
| `_anchor_of` (680) | `paragraph.py:73` names it in a comment only | dies; reword the comment |
| `leading_between`, `_leading` (708, 751) | `binder/page.py:63,743`; `tests/reading/test_lexical.py:13,679-694` | **survives -> `binder/page.py`**, its one caller. Read end may import leaves; it needs only `constants` and `series.Kind`, both imported there already. `reading/python/line_breaks.py:84 _leading` is an unrelated function |
| `_is_doc`, `_opens_doc`, `paragraphs_lexical`, `_joins_its_word`, `_opens_word`, `_line_comment_at` | `paragraphs_lexical`: stripped, one diagnostic test | die |
| `read_lexical` (868) | `reading/readers.py:24,140`; 4 test files | dies |
| `_mark_line_endings`, `_file_edges`, `_one_matter_per_end`, `_code_between`, `_gaps`, `_file_docs`, `_cut_by_place`, `_Group`, `_doc_places`, `_cut_gap`, `_FIRST_WORD`, `_ANNOTATION_NAME`, `_CLOSERS`, `_after_annotations`, `_declares_here` | none (`addresser._gaps` is its own property; `language.py` names `_declares_here` in comments) | die |
| `document_declarations` (1635) | none outside; Python and Rust state documents themselves | dies |
| `declarations` (1724) | none as a function. The hits under `reading/python|rust` are fields and a different word | dies |
| `code_text` (1779) | a comment in `language.py` | dies |
| `LexicalRead` (1832) | `binder/page.py:62,735`, `reading/readers.py:23,38,115,136`; test fakes | dies. Six test files use it as a fake; section 7 |

`reading/matter.py` is NOT lexer-only: both `projection.py` modules call `file_matter`. It stays.
`reading/source.py` (`CodeLine`, `DocPlace`, `lines_of_code`) stays.
`constants.scan_lines` stays: its surviving user is `leading_between` once moved.
`constants.text_lines`, `mark_of`, `line_ending_at`, `without_mark`, `holds_lone_cr` all keep readers.

**Home for `comment_form`: `reading/comment.py`** (recommended). It builds a `Comment`, and that
module defines `Comment`, `CommentSpan`, `Fragment`. Leaf to leaf, so area rules hold.
One constraint: `rust/scanner.py:8` and `docstring.py:8` import `reading.comment`, so a top-level
import of `comment_scanner` from `comment.py` is a cycle. The lazy form already used at
`lexer.py:149,366` covers it: import inside `_grammar_for`. Gain: `comment.py` does not import
`paragraph`, so `paragraph.py:178` can become a top-level import and its "Imported here" comment
goes. Alternative: a new `reading/comment_form.py`, no lazy import, one more module.
`edit-path-isolation` T2 and `lexer-and-language-findings` T44 ask for this move; T44 says "to the
desk", which `paragraph.py` could not import under the area table.

## 2. `reading/language.py`

**Python and Rust do not route through `Language`.** They load from
`references/languages/{python,rust}.toml` via `decode_definition`, into `SHIPPED_DEFINITIONS`
(`:702-722`), and validate with `validate_python`, `validate_rust` (`readers.py:28,32`).
`language_for` answers None for both (`:797-806`). The only reach-through is the `.toml` branch of
`line_comment_markers` and `documents_in_literals`.

| name | remains? |
| --- | --- |
| `Language` (29), `LANGUAGES` (168) | no. Includes toml, ini, yaml rows no reader read |
| `ReaderMetadata`, `READER_METADATA`, `INSTALLED_DEFINITIONS` | no |
| `validate_language_definition`, `language_from_definition`, `BY_EXT`, `language_for` | no. `BY_EXT` already had no reader (`lexer-and-language-findings` T40) |
| `_shipped_definitions`, `SHIPPED_DEFINITIONS` | yes |
| `INSTALLED_REGISTRY` (723) | yes, `LanguageRegistry(SHIPPED_DEFINITIONS)`. Used by `binder/page.py`, `commands/taken_in.py`, `concordance/code_names.py`, `flows/gather.py`, `readers.py`, `scripts/render_page.py` |
| `documents_in_literals` | yes: `flows/proof_setter.py:59,706` and `comment_form` |
| `line_comment_markers` | yes, reduced: drop the `language_for` branch. Only caller is `_grammar_for`, so it can move with it |

Smallest shape: module docstring, `_shipped_definitions`, the two constants, the two questions.
About 55 lines against 840. `reading/registry.py` is unchanged. `flows/language_definitions.py:16`
becomes `registry_for(SHIPPED_DEFINITIONS)`; `:10,15` lose the rows.

`row-was-never-retired` T5 (the open language-row polysemy ruling) has less to decide once no
row exists.

## 3. `stripped.py`, `proof.py`, `readers.py`, `page.py`, the tier

**`reading/stripped.py`: all dies** (`StrippedRead`, `code_fingerprint`, every helper). Users:
`binder/page.py:70,816`, `reading/proof.py:6` (docstring), tests. Its `_continues` and `_shebang`
name hits in `rust/` are Rust's own functions. #258's refusals go with it, as ruled.

**`reading/proof.py`: stays.** `UNPROVABLE` stays, `rust/records.py:18,354` raises it.
`PreservationResult`, `SourceRead`, `ReaderRecord` stay. Reword `:5-6`. With every read a
`ReaderRecord`, the split of `SourceRead` and `ReaderRecord` loses its reason (`page.Page.read`
may type as one); optional, not required.

**`reading/readers.py`**

| line | change |
| --- | --- |
| `:15-21` | keep `INSTALLED_REGISTRY`; drop `READER_METADATA`, `Language`, `language_from_definition`, `validate_language_definition` |
| `:22-25` | delete lexer import |
| `:36-39,115` | `SourceReader` union loses `LexicalRead` |
| `:96-107 read_paragraphs` | dies. No src caller; takes an unused `lang: Language`; test callers in `tests/test_reading_diagnostics.py` only |
| `:134-169 _read_paragraphs` | dies |
| `:218-228` | delete the `**{...}` block from `INSTALLED_BINDINGS` |
| `:265-271 tier_for` | dies. No src caller; `tests/test_language_definitions.py:885-896` only |
| `:274-295 _paragraph_source_span` | dies; `re`, `partial`, `SourceCoordinates` imports go with it |
| `bind_reader`, `reader_for`, `read_source`, `supported_definitions`, `ReaderBinding` | stay |

**`binder/page.py`**: `:61-64` lexer import, `:70` stripped import, `:731-738` the type test.
After: `record = result; text = record.source.text` unconditionally, and `:816` is `read=record`.
`leading_between` arrives here. Docstring `:15` rewords.

**Tier**

- `TIER_ANSWERS`: no hit in `src/`, `tests/`, `scripts/` or `CLAUDE.md`. Nothing to do.
- `tier_for` and `ReaderMetadata.tier`: die.
- `gather --languages`: `commands/gather.py:56,108-113`. MEASURED under the probe it prints both
  languages with tier `lexical`, so the column says nothing. Recommend dropping it (list language
  and extensions) and rewriting `:113`, which says a missing suffix exits nonzero.
- The word `lexical` also survives legitimately, and is NOT a tier to remove: reader ids
  `python-lexical`, `rust-lexical`; final capability entry validated at
  `reading/python/definition.py:47`, `reading/rust/definition.py:59` and hashed into the
  compatibility digest; `PythonRead.proof == "lexical"` at `reading/python/records.py:280`.

## 4. Gather, binder, reviewers

**Path today for an unsupported suffix**

- Walked: `flows/gather.py:119` `INSTALLED_REGISTRY.for_path(path) is None` and not named ->
  `g.no_record`, printed as `PASSED OVER` by `commands/gather.py:183-205`, exit 0.
- Named: into `g.files`; `_pages` `:140` `context_for` -> `ReadFailure` -> `g.unreadable` ->
  `commands/gather.py:130-132` exit 1.
  MEASURED: `gather b.js r.md` on HEAD: `NOT GATHERED` for `r.md`, exit 1. On the probe `b.js` the
  same, exit 1; `gather .` lists both under `PASSED OVER`, exit 0.
- `flows/page_for.py:71-83` is unreachable: `context_for` at `:33` already fails the same path.
  Existing dead branch, in the way of this change.

**Change**: `_walk` routes every path with no definition to a new `Gathering.freeform: list[str]`
(repo-relative posix) whether named or walked; `no_record` and its `PASSED OVER` print go. Keep
`unreadable` for "matched no files" and for a `.py`/`.rs` that fails to read. Freeform files are
not opened at gather, so a binary cannot fail it. `SEPARATOR` refusal at `:184` is an address rule
and does not apply to a file with no address.

**Where it is carried: `Binder.freeform: tuple[str, ...]`**, because only the binder crosses into
`topology` and `distribute`. `bind(pages, read_from, absent, freeform=())` at `binder/binder.py:76`;
`serialize` at `:316`; `deserialize` after `_read_from_problem`, refusing a non-list by name.

**Version**: bump `VERSION` to `"4"` at `:73`. The refusal already exists at `:298-303`
(`unsupported binder version ...; regather`), so a v3 binder is refused with no new code.
`:269-273` is the v2 message. Tests take `VERSION` as a constant (`tests/helpers.py:34`,
`tests/test_binder.py:12`), so the bump alone costs almost nothing. Received-binder checks:
`binder_reading_contexts` (`flows/reading_context.py:97`) walks `binder.pages` only, so freeform
paths need no reading context and do not trip `_reading_contexts`. `flows/verify.py:343,349` and
`flows/bus.py:215,233,336` read `binder.pages` only: a freeform path stays invisible to the
coverage count, the sheet check and the root check, which is correct.

**How a reviewer gets pages today**

`commands/distribute.py:171` -> `fan_out.dealt` (`:110`) -> `partition` (`:123`) matches
`dispatch.paths` against `page.path` by `fnmatch`, runs the overlap and uncovered guards, then
`assigned_binder` + `seed` build a received binder and an edit copy of one `Sheet` per page, each
requiring `reading`. `topology.compose` (`flows/topology.py:89,100,106`) sorts `binder.pages`
and deals them round-robin. `fit` (`:59`) runs `partition`. `places.py` builds only from marks on
sheets, so it sees nothing unless a sheet exists.

**Smallest route with no page**

1. `partition`: `all_paths` (`:135`) and the matching include `binder.freeform`. A `Shard` carries
   the freeform paths it matched, as a third element (two unpack sites: `fan_out.py:114,146`, plus
   `tests/test_topology_compose.py:67`). Overlap and uncovered guards apply unchanged.
2. `dealt`: `replace(binder, pages=..., freeform=...)`, so a received binder holds that shard's
   paths. `assigned_binder` keeps the field through its own `replace`.
3. `compose`: `pages = sorted([*page paths, *binder.freeform])` at `:89`. That alone removes the
   zero-page refusal and deals freeform files across shards.
4. `commands/distribute.py:189` adds the freeform count to its line. The reviewer reads
   `copies/binders/<stage>_<role>_<n>.json` as it already does.

No `Sheet`, `EditCopy`, `Place`, `desk/` or `fill` change. Findings on a freeform file are not
marks; ruling #259 keeps them as `path:line` with proposed text, outside the edit copy.

**Rejected: a zero-paragraph `RedactedPage`.** It would need zero `topology`/`fan_out` change but a
fake `ReadingContext` that `context_for` must honour, and every `binder.pages` reader then holds
something that is not a page. A shard that holds only freeform paths seeds a copy with no sheets;
`EditCopy.seed` with no sheets through `check` and `collate` was NOT run; test that first.

## 5. `prove_unchanged` and the write chain on a freeform path

**Today**: `flows/prove_unchanged.py:85-89` `context_for` fails -> `FAIL ... unsupported-language`,
`failures += 1`. MEASURED: `prove_unchanged --base HEAD r.md` prints that, `1 unproven`, exit 1;
the probe gives the same on `b.js`.

**Exit**: `commands/prove_unchanged.py:38-40` failures -> 1. `unchecked` never fails, `:41-49`
exit 0. Today `unchecked` means one thing, no line-ending sibling (`flows/:141-144`).

**Change**: in `run`, after the `outside --repo` check and before `:85`:
`if reader_for(target) is None:` -> `UNCHECKED  {rel}: no reader -- formatter and compiler are the
check`, count it, `continue`. Line endings are not compared for it. `reader_for` returning a
`ReadFailure` still fails. Add `ProofReport.freeform: int` (or similar), because
`commands/prove_unchanged.py:43,48` print `len(args.paths)` as proven; the summary must print
`N proven, M UNCHECKED`, and all-freeform must not say proven at all. `load_settings`
(`flows/reading_context.py:277`) still refuses settings for a freeform path, exit 2, correct.

**Write chain**: each already refuses by name; nothing is needed provided no sheet is seeded.

| where | path | result on a freeform path |
| --- | --- | --- |
| `flows/proof_setter.py:398 _one` | `page_of` | `Refusal("read", ...)`, nothing written |
| `flows/proof_setter.py:764 _prove` | `page_of` | `Refusal("prove", ...)` |
| `flows/transcribe.py:163 _pages_of` | `page_named` -> `context_for` fails | reason `:174`, when the name is touched |
| `flows/fill.py:185 place_on_the_page` | `page_of` | `[f"{address}: ..."]`; earlier `:181` "no sheet" fires first |
| `flows/fill.py:387 page_text_at` | `held_at` | `ReadFailure`, a refusal |
| `flows/places.py:51` | `held_at` | failure returned; a `move` INTO a freeform file is refused |
| `flows/on_the_page.py:164-187` | `context_for` | failure held and returned |
| `commands/addresser.py:269`, `commands/carry.py:65` | `contexts` | named refusal, exit 2 |
| `commands/taken_in.py:81-117` | | diff still prints; "addresses not compared" on stderr; exit 0 |
| `desk/marks/rules.py:37` | `comment_form` on an unknown suffix | no crash: chunks are raw text, no markers |

Behaviour change to accept: a `move` from a Python page to a `.js` page works today and refuses
after. It already refuses for `.md`.

## 6. `concordance/`

- `code_names`: `:75` `definition is None or language != "python"` is already the gate. Rust is
  a NO_HARVESTER row and stays one. A `.js` row changes label only. MEASURED:
  `(no name harvester for javascript)` becomes `(no name harvester for unknown)`, the label every
  `.md` already has. Worth one line: `definition.language if definition else "no reader"`, or
  accept it. `evals/generator_split.py:143` counts by that label, but that script already imports a
  module that no longer exists (`census`, `:35`).
- Consequence, already true: a backticked symbol defined only in a non-Python file reads as a
  false obituary. `_passed_over` still says so.
- `referrers.tokens_for`: `:54` tests `.py`/`.pyi` itself; stem and path tokens work for any
  file, unchanged. `commands/referrers.py` reads any text. A freeform target works today.
- `annotate`, `annotations_for`: work over paragraphs only. A freeform file has none, so it gets
  no citation or number annotations. A Python comment citing a `.js` path still resolves:
  `path_index` covers tracked paths.
- Only edit in the package: `NAMED_DEFS`.

## 7. Tests

Split of the 921 probe failures. **Rows drop**: the function keeps a Python or Rust parameter, so
the failing rows are deleted with nothing to port. **Port**: every parameter of the function
failed, so no Python or Rust case exists and the behaviour is general. **Die**: the test's subject
is a lexical row, the stripped proof or a feature only rows had (closing docstring, `line_endings`,
`spanning_quotes`). Port and Die are hand-judged from test names, not from reading every body;
treat them as +/- 15%.

| file | collected | fail | rows drop | port (ids / fns) | die | also, passing but dead |
| --- | --- | --- | --- | --- | --- | --- |
| `tests/reading/test_lexical.py` | 169 | 163 | | | 163 | +6: 4 die; **2 `leading_between` tests move** to the page tests |
| `tests/reading/test_stripped.py` | 77 | 54 | | | 54 | +23 die |
| `tests/test_line_endings.py` | 36 | 26 | | | 26 | +8 die, 2 (`m.py`, `m.rs`) stand |
| `tests/test_compositor.py` | 601 | 268 | 233 | 29 / 15 | 6 | |
| `tests/test_proof_setter.py` | 236 | 123 | 18 | 86 / 18 | 19 | `stripped` monkeypatch at `:324` |
| `tests/test_comment_wrapping.py` | 187 | 60 | 16 | 44 / 15 | | 29 vanish; imports rows and `code_fingerprint` |
| `tests/test_page_addresses.py` | 136 | 74 | 74 | | | 13 vanish; `_sample_for` helper |
| `tests/test_reading.py` | 270 | 57 | 57 | | | SOURCES table; 3 strict xfails are `a-doc-comment-is-cued-a-and-typed-b` T3 |
| `tests/test_page_for.py` | 174 | 21 | 7 | 12 / 9 | 2 | `page_over_read` helper fakes `LexicalRead` |
| `tests/test_proof_command.py` | 46 | 15 | 1 | 10 / 4 | 4 | |
| `tests/test_standalone_reading_context.py` | 14 | 12 | 2 | 10 / 5 | | |
| `tests/test_paragraph_text.py` | 29 | 11 | 5 | 6 / 1 | | |
| `tests/test_addresser_command.py` | 21 | 6 | | 5 / 4 | 1 | `a_closing_binder` fixture |
| `tests/test_language_definitions.py` | 232 | 5 | | | 5 | about 25 more pin rows (`:428,730-896,1153,1176-1263`): most die, a few rewrite |
| `tests/test_reading_diagnostics.py` | 84 | 5 | | | 5 | +4 die |
| `tests/test_topology_compose.py` | 11 | 4 | | 4 / 1 | | |
| `tests/test_reading_context.py` | 221 | 3 | | 3 / 2 | | +5 use `LexicalRead` |
| `tests/test_distribute_command.py` | 18 | 2 | | 2 / 1 | | |
| `tests/test_gather.py` | 9 | 2 | | 2 / 2 | | freeform assertions are new work |
| `tests/test_mark.py` | 106 | 2 | | 2 / 1 | | |
| `tests/test_taken_in.py` | 12 | 2 | 2 | | | |
| `tests/reading/test_matter_across_readers.py` | 1 | 1 | | 1 / 1 | | |
| `tests/reading/test_paragraph.py` | 16 | 1 | 1 | | | imports `lexer` at `:7-8` |
| `tests/test_bus.py` | 112 | 1 | | 1 / 1 | | |
| `tests/test_gather_command.py` | 20 | 1 | | 1 / 1 | | |
| `tests/test_python_lexical_proof.py` | 47 | 1 | | 1 / 1 | | +10 use `StrippedRead` |
| `tests/test_received_binders.py` | 34 | 1 | | 1 / 1 | | |
| **total** | | **921** | **416** | **220 / 83** | **285** | |

Fail with zero failures in the probe, import or fixture only:
`tests/test_sheet_reading.py` (`mixed_binder`, `LexicalRead`, 7 tests),
`tests/test_page_reading_context.py:14`.

**The trap, in numbers.** Tests that use a lexical language as a convenient fixture for general
behaviour and need porting: **about 220 ids in 83 functions**. Largest:
`test_proof_setter.py` (`test_a_draft_is_accepted_on_where_its_text_landed`,
`test_written_text_may_join_a_neighbour_or_read_elsewhere`,
`test_a_merged_paragraph_is_still_checked_line_by_line`, `test_the_reread_asks_the_file_on_disk...`,
the interpreter-line family), `test_comment_wrapping.py` (fragment removal, all on `/* */` shapes,
Rust is the only surviving block-comment language), `test_compositor.py`.
One Rust or Python case per function is the likely shape, not one per id, so the port is nearer
100 new parameters than 220.

**Check before deleting rows**: the 233 `test_compositor.py` rows are the FORMS table. Its `C block`,
`trailing block wrapped` and `C both` rows must have a Rust row of the same shape first, or a
shape silently loses coverage. Not checked row by row.

**Modules that stop importing** (static): `lexer` in `test_lexical`, `test_paragraph`,
`test_line_endings`, `test_language_definitions`, `test_gather_command`,
`test_page_reading_context`, `test_paragraph_text`, `test_page_for`, `test_sheet_reading`,
`test_reading_context`, `test_reading_diagnostics`. `stripped` in `test_stripped`,
`test_comment_wrapping`, `test_proof_setter`, `test_line_endings`, `test_proof_command`,
`test_python_lexical_proof`, `test_standalone_reading_context`. `Language` rows in
`test_comment_wrapping:16`, `test_page_addresses:15`, `test_line_endings:9`.

**Gates**: `tests/gates/` had no failure under the probe. `tests/test_areas.py` names no lexical
module. Scripts:

- `scripts/measure_binder.py:41`: `Kind` import breaks, fix to `reading.series`.
- `scripts/check_vocabulary.py`: no code change. `scripts/retired_words.toml` entries go stale
  without failing, since exemptions are `replace` calls (`check_vocabulary.py:276-277`):
  `block_comment` `:157`, `doc_block` `:163`, `in_block` `:168`, `TEXT BLOCK` `:153`,
  `Java text block` `:176`. `_join` `:139` stays, its `why` says "the lexer's".
- `scripts/render_page.py:65`: unchanged. `test_render_script_reports_failed_page...` uses a
  lexical fixture and is in the port count.
- `evals/generator_split.py`: already broken, see section 6.
- Not run: `ruff`, `ty`, `scripts/smoke_middle.ps1`.

## 8. Docs and prose naming the lexical tier

`CLAUDE.md` and shipped prose need Roy's approval of exact wording.

- `CLAUDE.md:219-302`, the binder section: tier table `:221-224`, `:227` "Adding a LEXICAL
  language is a data row", `:229-243`, keyword-list and no-inheritance material `:246-300`,
  `a` series `:288-300`. The Roy rulings there govern language rows that are gone. Also `:71`.
- `docs/addressing.md:109`, `:238-239` (stage 7b: "Other languages use the existing stripped-text").
- `docs/parsing.md:5,15-16,26,68,84-87,92-115,144-146,176,184,200`. Section *Not built: a real
  lexer for other languages* is superseded by #259.
- `docs/vocabulary.md:533-543`, the `lexer` section; needs a retirement entry. `:61` keeps.
- `src/comment_review/references/vocabulary.toml:29`: "kinds a language offers is whatever its tier
  can resolve. Four of the eighteen..."
- `README.md:350-356`, *Languages*: "reads fifteen languages, all lexically".
- `docs/design/README.md:66`, `docs/design/results/README.md:94`.
- `docs/the-turn.md:476`, `docs/gates.md:29,53-55,65,103` are history; leave.
- `CHANGELOG.md`: an entry at release.

Code comments naming dead things: `reading/__init__.py:4,10-15` (the whole inventory),
`binder/__init__.py:15`, `reading/addresser.py:49,108-109,159,185,198,257`, `reading/series.py:7`,
`reading/paragraph.py:9-19,73,157,166,177`, `desk/stages.py:71,77,110,138`, `desk/topology.py:19`,
`machine/repo.py:425-426`, `machine/__init__.py:17`, `flows/__init__.py:42`,
`flows/gather.py:28-38`, `commands/gather.py:81-85,125-129`, `flows/language_definitions.py:15`.

`src/plugin/`, list only. The lexical word itself has zero hits; what changes is behaviour:

- `skills/comment-review/SKILL.md:133-134` (gather exits nonzero), `:144-150` (topology `<n>` counts
  files), new freeform stage and cheat sheet, formatter and compiler step.
- `references/write.md:51-61` (prove_unchanged, `PROVEN`, add `UNCHECKED`).
- `references/reviewer-brief.md` (freeform file: `path:line`, proposed text).
- `references/compact.md:29` (documents by a run above: Rust only now; check).
- `agents/*.md`: no hit; they read the brief.

Last by ruling: *"The code lands and is tested before the agents are told."*

## 9. Board (`job-board` read commands only)

Classified from open-task labels; bodies not read except where noted.

**All open tasks die (13 TODOs, 47 tasks)**: `language-reader-c` 2, `-cpp` 2, `-csharp` 2, `-go` 3,
`-java` 5, `-javascript` 5, `-kotlin` 2, `-lua` 8, `-ruby` 7, `-shell` 4, `-sql` 2, `-swift` 3,
`-typescript` 2. #259 states it supersedes #222's plan for them.

**All or nearly all open tasks die**: `a-doc-comment-is-cued-a-and-typed-b` T1-T4;
`a-comment-inside-a-line-makes-the-file-unprovable` T2-T6;
`language-rows-in-toml` (T12-T18 named; T14's harvester half stands);
`matter-misses-two-languages` T3; `fixtures-do-not-test-the-shape` T1, T3, T5 (no `sample.*` exists now).

**Partly die**

| TODO | die | stand or re-read |
| --- | --- | --- |
| `lexer-and-language-findings` (44 open) | T2, T3, T6-T11, T14, T17, T34, T36, T40, T41, T43, T45, T46, T52, T54, T55, T58?, T59, T61, T63, T64?, T67 | T19-T24, T29, T50?, T51, T56, T57?, T65, T66, T69, T70; T42 and T44 are done by this work |
| `lexical-code-identity` | T5, T6, T8, T9, T12 | T2 |
| `a-series-never-fills-outside-python` | T18-T21 | T22 |
| `corpora-are-all-python` | T2-T5, T9, T10 | |
| `name-corpus-sees-one-language` | T1, T3, T4 | T5 |
| `one-stem-four-jobs` | T2, T3, T6 | |
| `one-reader-builder` | T3 | T1 needs rewording, others re-read |
| `page-and-addresser-scans` | T5, T13 | |
| `block-comment-markers-survive-into-the-prose` | T5, T7 | T2, T3: Rust `/** */` may still be affected |
| `closing-line-deletes-code` | T7, T8 as a C input | T4: re-rule against Rust block comments |
| `doc-on-the-declaring-line` | T4 | T3 |
| `bom-is-read-as-source`, `census-degrades-silently` | T1 | re-read, cited lines are stale |
| `assertions-that-gate-a-substring` | T3, T8 | |
| `docstrings-need-their-own-address-series` | T8 | T9 |
| `the-code-check-refuses-add-and-drop-on-a-docstring` | T4 | |
| `two-live-runs-proposed-fifteen-changes` | T15 | |
| `edit-path-isolation` | T2 is DONE by this work | |
| `containers-and-verification-are-unwired` | T34 is stale: `SYMBOLISH` already left | |
| `row-was-never-retired` | T5's language-row sense loses its subject | |

**Interacts, needs a ruling first**: `a-prose-file-has-no-blocks` (T1 open, T7),
`a-non-code-document-has-no-read-review-resolve-or-write-chain-of-its-own`,
`a-reference-needs-its-own-write-chain`, `2026-10-11-maintained-source-selection` T1. Freeform
either answers or sharpens these.

**Plans**: `2026-10-11-lexical-readers` is open at 84 of 182 tasks, 40 of 53 steps, 111 reasons;
P38-P50 open. P41 (*Unify both executable comparisons*) dies. P43, P44, P46-P50 need rewording.
It holds about 98 open TODO tasks, many in the lists above, so it cannot close until they are
superseded or moved. `0.2.4-the-agents-read-the-cli` names `a-comment-inside...`; affected lightly.
No plan for this work exists yet under `docs/plans/`.

## Recommended task order

Each step leaves the suite green. Every step before 6 is behaviour-neutral for the lexical
languages or works on paths that are already unsupported (`.md`).

1. **Port the fixture tests** to Python or Rust, one commit per file, no `src` change (about 83
   functions). Add Rust rows for any FORMS shape only C or Java held. Passes against lexical still
   installed, which is the proof the port preserved the assertion.
2. **Move `NAMED_DEFS`** to `concordance/names.py`, **`leading_between`** to `binder/page.py`, with
   its 2 tests. Fix `scripts/measure_binder.py`. No behaviour.
3. **`prove_unchanged` answers UNCHECKED** for a path with no reader; separate summary count.
   Testable on `.md` now; replace the existing FAIL expectations.
4. **`Binder.freeform`, version 4**, written empty, deserialize refusal. No user yet.
5. **`gather` lists freeform, exit 0**; `partition`, `dealt`, `compose`, distribute's print.
   Testable on `.md`. Add the freeform-only binder test, and run `check` and `collate` over a
   no-sheet copy here. Depends on decision 1.
6. **Uninstall**: empty `READER_METADATA`, delete rows-drop and die-group tests, same commit
   (about 700 ids). Suite shows only what step 1 missed. `--languages` loses its tier column.
7. **Delete code**: reduce and move `comment_form` to `reading/comment.py`; delete `lexer.py`,
   `stripped.py`, `Language` and the rows, the `readers.py` lines, the `page.py` branch. Delete
   `read_paragraphs`, `tier_for`, the dead `page_for.py:71-83` guard if agreed.
8. **Follow-on orphans**: `closing_docstring`, `a_series` parameters, `closing_documentation`, the
   `<eof>` `a`, `page.py:770-771`. Separate commit, it touches the addresser.
9. **Prose**: comments in section 8, `docs/`, `vocabulary.md`, `vocabulary.toml`,
   `retired_words.toml`, `README.md`. `CLAUDE.md` wording to Roy.
10. **Board**: supersede with evidence commits; rescope or supersede `2026-10-11-lexical-readers`.
11. **Agents lane**: SKILL, `write.md`, brief, the cheat sheet. Last, per #259.

Between 6 and 7 the lexer is present and unreachable; that state must not merge. Ruff, ty,
`check_shipped_syntax` and `check_vocabulary` belong on each step. `plugins/` stays untouched until
release.

## 10. Could not be established, or needs Roy

1. **What is "the rest"?** The ruling says "lists the rest as freeform". A directory walk holds
   READMEs, images, lockfiles (`flows/gather.py:115-116` says so). Literal reading: all of them go
   to four reviewers, and a measured run had 190 of 196 changed files as `TODO/*.md`
   (`a-prose-file-has-no-blocks`). Options: (a) every file no reader claims; (b) only source files,
   with `registry._EXCLUDED_SUFFIXES` plus binaries staying `PASSED OVER`; (c) named files freeform,
   walked files `PASSED OVER`. Recommend (b): it matches "every other LANGUAGE" and needs one test.
2. **"In the order that the project graph thing says."** No code computes a dependency order.
   `topology.compose` sorts paths alphabetically and deals them round-robin; `topology.toml` order
   is stage and dispatch order. If Roy meant `topology`, the design above holds. If he meant the
   code graph, ordering work is missing from this map.
3. **Where freeform findings live.** #259 gives a shape, not an artifact: no file, schema, or
   approval record exists. Recommended outside the edit copy, but stage 5 and the docket have no
   slot, so `collate`'s report will not mention them. Needs a design.
4. **Stale check on a freeform file.** Pages carry `sha`; freeform paths would not. A file changing
   between review and apply goes unnoticed.
5. **Empty-copy path.** `check` and `collate` over a shard with no sheets, not run.
6. **Port viability.** Whether every ported shape exists in Rust or Python was not tested, notably
   interpreter-line cases (Rust `#!` vs `#![attr]`) and `TestAnInterpreterLineTheRowNames`.
7. **P/D split** is by test name. **Board split** is by label; `?` marks ones I could not place.
8. **The `move` loss** in section 5 is a behaviour change #259 does not mention.
