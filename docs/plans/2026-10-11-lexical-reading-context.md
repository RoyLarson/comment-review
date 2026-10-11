# Language registry and saved reading context

```
Status:   in-progress
Progress: 0 of 3 TODO tasks closed
Plan-tasks: 5 of 26 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-11 (founded by move-t from 2026-10-11-lexical-readers)
```

## Objective

Implement the approved P4-P6 decomposition from
docs/superpowers/specs/2026-10-11-lexical-readers-design.md on
feat/lexical-reading-context, based on feat/lexical-readers. This child builds
shared language-definition loading, registry selection and saved reading
compatibility. The parent retains each language's dated spec, definition file
and new recognition implementation. Parent P4 is replaced by separate shared
machinery and per-language completion steps; parent P5 and P6 use this child.
Return by no-ff merge after verification and Roy's integration choice.

The controller reads this plan and the approved design. Executors receive only
task-specific requirements, interfaces, files and checks. They do not receive
internal plans, specs, TODOs, decision logs or development history. Runtime
prose and examples describe current behavior and use invented source examples.
Plan approval authorizes recording these tasks, not starting implementation.
Preserve Roy's chosen execution method when execution is requested.

Global constraints: Python 3.11 and standard-library-only runtime; no added
dependency. Each language owns its rules, without family defaults or inherited
configuration. Existing recognition algorithms, whole comment sections, source
SHA, exact source bytes and a/b/c/f address semantics remain unchanged here.
Config/data, document and standalone markup files are outside the code-reader
registry. JSX/TSX retain their existing programming-language classification;
registration does not establish new grammar coverage. Full name harvesting, AST
replacement, language algorithms, operational-agent prose, formatting policy and
release assembly remain parent or separately owned work.

Architecture: reading owns immutable definitions, registry values, contexts,
pure TOML decoding and compatibility rules. Machine owns filesystem bytes; flows
acquire definitions and source, assemble installed readers, select settings and
enforce admission. Binder, desk and docket containers retain context without
finding files or consulting installed reader state. Commands parse inputs and
present flow outcomes. Runtime compatibility checks happen in flows before saved
addresses are resolved, compared, counted for coverage or used to mutate a run;
wire-shape decoding remains independently testable.

Definitions are local configuration for installed implementations, not an
executable plugin format. Reader identifiers resolve against an explicit binding
map, never arbitrary imports from TOML. Actual language TOML files are added
with their language's own spec and implementation. This child tests the loader
with invented definitions and registers existing readers from their existing
language records. It does not duplicate those grammar values into a second table
or claim the separate-definition goal is complete.

Shared interfaces: new reading/definitions.py defines frozen
LanguageDefinition(language: str, suffixes: tuple[str, ...], reader: str,
revision: str, capabilities: tuple[str, ...], defaults: Mapping[str, str],
choices: Mapping[str, tuple[str, ...]], rules: Mapping[str, object]). Mappings
and nested rule values are defensively copied and made recursively immutable;
rules allow TOML strings, integers, booleans, arrays and tables, preserving
their types and order where meaningful. Dates and floats are refused in this
configuration contract. Each setting is a named string choice; each key has
explicit allowed choices and an explicit default, including an empty choice only
when declared. Unknown top-level keys and inheritance keys are refused.
Language-owned validators determine required/unknown grammar rule fields.

The definition wire has format = 1 plus every named record field, using
suffixes/capabilities as arrays and defaults/choices/rules as tables. Empty
tables and arrays are explicit values, not substitutes for absent fields.
decode_definition(text: str) -> LanguageDefinition | ReadFailure is pure.
Definition acquisition belongs to flows/language_definitions.py:
load_definitions(paths: Sequence[Path]) -> tuple[LanguageDefinition, ...] |
ReadFailure. Preserve acquisition/decode stages and use SELECT diagnostics
invalid-language-definition, duplicate-language, ambiguous-language or
unavailable-reader for their corresponding conditions. Retain originating
definition paths in flow diagnostics. Never publish a partial registry.

New reading/registry.py defines frozen LanguageRegistry with definitions:
tuple[LanguageDefinition, ...] over unique definitions, with for_path(path:
Path) -> LanguageDefinition | None and for_language(name: str) ->
LanguageDefinition | None. Case normalization follows the existing lower-case
suffix selection; duplicate claims are rejected after normalization. Name lookup
is by the declared exact language identity. Existing language_for and tier_for
callers migrate through one facade, with one owner for selection and advertised
coverage. A registry does not import lexer, binder, flow, results or machine
code. New reading/readers.py owns binding composition and the current
paragraph-reader dispatch; it can import existing lexer algorithms without a
reverse import. A ParagraphReader accepts (path: Path, text: str, lang:
Language) and returns list[Paragraph] | ReadFailure. Move the current
read_paragraphs boundary into this owner when needed to avoid a registry/lexer
cycle, updating its concrete callers together. Do not fabricate SourceStructure
from the current paragraph result. New SourceRead implementations integrate in
their separate language tasks.

New reading/context.py defines frozen ReadingContext(language: str, reader: str,
compatibility: str, settings: tuple[tuple[str, str], ...]). Settings have unique
sorted names and are the effective values, not overrides. compatibility is a
SHA-256 digest of canonical effective definition data, reader semantic revision,
shared placement revision and any reader-declared runtime grammar dependency.
Sort table keys while preserving ordered arrays and value types; exclude TOML
formatting, paths, source text, source SHA and unrelated registry entries. A
reader semantic change requires changing its explicit revision. A shared
address-rule change changes the placement revision. The current Python binding
includes implementation and interpreter version while its runtime parser remains
relevant. Other bindings include no invented runtime dependency. This identity
is neither a release number nor a source hash.

resolve_context(definition: LanguageDefinition, overrides: Mapping[str, str], *,
placement_revision: str, grammar_identity: str) -> ReadingContext | ReadFailure
rejects unknown keys/values and applies only declared defaults.
compatible_contexts(saved: ReadingContext, current: ReadingContext) -> bool
requires all context fields to agree. New reading/context_io.py provides
context_to_wire(context) -> dict and context_from_wire(where: str, value:
object) -> tuple[ReadingContext | None, list[str]]. Wire shape is {format: 1,
language: str, reader: str, compatibility: str, settings: object}. Validate
exact types, nonempty identities, digest syntax, key uniqueness and unknown
fields; reject booleans as version integers. Runtime admission derives the
current identity from installed definitions and supplied saved settings; it
never treats the supplied digest as proof of its own compatibility.

Every serialized Page, RedactedPage, Sheet and Schedule carries a required
reading field containing that context. Binding/redaction/seed/copy operations
copy it from the supplying page, never synthesize it from a filename. A
MasterProof carries page_readings keyed by real page path for all reviewed and
additionally acquired destination pages. It retains existing page_shas and must
keep the two destination records consistent. Repeated records for one page must
agree with each other and with sheets. Empty sheets retain context. Unknown or
missing saved context requires regathering; there is no compatibility default or
automatic upgrade. Binder wire VERSION becomes 3 for this required shape;
version 2 artifacts get a regather message. Other containers validate their
required reading fields without introducing a system-wide version scheme.

New flows/reading_context.py supplies reading_problems(saved: Mapping[Path,
ReadingContext], current: Mapping[Path, ReadingContext]) -> list[str]. Its flow
caller derives current contexts from installed definitions/bindings and saved
effective settings; missing current paths refuse. It validates only metadata
before any consumer touches saved addresses. Context contradictions are errors
even when paths, SHA or address strings match. Admission also covers in-memory
objects built without deserialization. Page acquisition accepts explicit
effective settings/context; supplying held Source prevents reacquisition as it
does now. Caches retain source identity and context; a cache hit cannot silently
reinterpret a page. Initial source SHA checks remain before parsing, and context
checks precede address use.

Fresh runs can receive --reading-settings FILE on gather, compositor and
prove_unchanged. The JSON object maps canonical repo-relative paths to setting
objects of string names and values. The flow validates it through the existing
artifact I/O boundary; source readers do no project discovery. Missing entries
use only explicit definition defaults. Refuse invalid paths, conflicting
normalized entries and unsupported settings. Binder/proof-driven commands
consume saved effective settings and do not expose an override that silently
changes them. Existing bindings accept only settings they actually implement;
fixture bindings test transport of independent dialect choices without claiming
new SQL or shell dialect support.

Execution sequence follows the dependencies below, not numeric task IDs. Each
behavior-changing task first adds a meaningful failing regression, observes the
expected failure, implements, then reruns its focused gate. Existing-behavior
fixtures may start green when independently expected values prove their purpose.
For each unit: verified work commit, job-board closure against that commit,
closure commit, next unit. Never close a container task while a concrete caller
still drops its required field; coordinate those constructor/caller adaptations
in the same task. Review each task's changed behavior and current prose, then
review the whole branch after P26. Do not relax gates or add dependencies.

P1: Define LanguageDefinition in reading/definitions.py, with typed immutable
values and constructor validation. Consumes existing Language only through later
adapters. Produces the record above. Add tests/test_language_definitions.py for
required fields, wrong scalar types, explicit empty rules versus missing rules,
nested mutation attempts and no alias to input mappings. Gate: uv run pytest -q
tests/test_language_definitions.py.

P2: Add decode_definition in reading/definitions.py over supplied text using
tomllib. Consume P1; return its record or SELECT/invalid-language-definition.
Test malformed TOML, missing/unknown fields, duplicate TOML keys, empty choices,
undeclared defaults and preserved ordered rule arrays in the same suite. Parsing
never imports a reader or reads a path.

P3: Add flows/language_definitions.py.load_definitions over flows/source.py. Use
exact held snapshots and retain definition-file diagnostic paths; no parser I/O.
Test missing file, invalid UTF-8, valid empty-file syntax failure and later file
failure after an earlier success in tests/test_language_definitions.py. No
partial successful definition collection escapes.

P4: Build LanguageRegistry in reading/registry.py. Consume P1 records; reject
duplicate identities, same-suffix conflicts and unsupported code-file routes.
Test lower-case selection, unknown suffix, supplied empty registry, immutable
lookups and registration-order independence. Keep fixtures invented. Gate: uv
run pytest -q tests/test_language_definitions.py.

P5: Bind reader identifiers in reading/readers.py with explicit installed
callables and language-owned rule validators. Consume P4; produce a validated
selection and its actual capabilities before invoking recognition. Refuse an
unavailable binding or unsupported claimed capability. Test a spy fixture reader
is called once with exact source, unknown identifiers never invoke an import,
and grammar-field validation preserves missing versus empty. Move the existing
paragraph dispatch boundary without changing its algorithms; include
binder/page.py and diagnostic test imports in this coordinated step.

P6: Register existing code readers from reading/language.py in the new binding
composition. Keep each language's configuration independent and materialize its
existing values, not a new family table. Avoid duplicating grammar data; extract
a leaf record or rows module only where needed to keep imports acyclic. Name
every added file in the worker brief. Verify all retained source suffixes and
current refusal/address fixtures in tests/test_reading.py,
tests/test_reading_diagnostics.py and tests/test_language_definitions.py. No
production language TOML or new grammar support is authored here.

P7: Migrate language_for, tier_for, page selection and commands/gather.py
coverage output to the registry/bindings. Audit concrete consumers in reading,
flows, commands and concordance without replacing full name harvesting. Verify
one selection owner and actual reported coverage;
config/data/documents/standalone markup cannot select a code reader. Gates:
tests/test_language_definitions.py, tests/test_gather.py, tests/test_page_for.py
and tests/test_reading.py.

P8: Add immutable ReadingContext in reading/context.py with exact fields above.
Add tests/test_reading_context.py for invalid identities/settings, duplicate
names, sorted effective settings, nested caller mutation and equality. There is
no source SHA or filesystem operation in this value.

P9: Implement canonical compatibility derivation in reading/context.py,
consuming P1 and binding semantic/runtime identities. Pin independent digest
input examples and test changed rule order, rule value/type, reader revision,
placement revision and runtime grammar identity. TOML spacing/key order,
definition path and unrelated-language changes leave identity stable. Gate: uv
run pytest -q tests/test_reading_context.py.

P10: Resolve effective per-file settings with resolve_context and add flow-owned
reading-settings JSON validation in flows/reading_context.py. Add the declared
CLI flags at the three fresh-run entry points. Verify mixed files keep their own
values, unsupported/conflicting values refuse, defaults are explicit and saved
context cannot be replaced by a fresh default. Test JSON paths and command
plumbing in tests/test_reading_context.py; reader algorithms remain unchanged.

P11: Implement reading/context_io.py wire encoding/decoding. Test exact literal
wire records, round trips, malformed fields, future/missing format versions,
missing identity, unknown settings shapes and useful regather messages. Pure
decoding checks structure, not installed reader compatibility. Gate: uv run
pytest -q tests/test_reading_context.py.

P12: Add required reading context to binder/page.py Page and RedactedPage and
binder/binder.py binding/serialization. flows/page_for.py supplies the selected
context from the held source and registry. Update concrete constructors/helpers
together; no silent default context. Verify complete, redacted and empty pages,
literal version-3 wire records and version-2 regather rejection in
tests/test_page_for.py, tests/test_binder.py, tests/test_reading_context.py.

P13: Preserve context in desk/proof/sheet.py and edit_copy.py and all seed,
distribution and topology slicing producers. Update flows/distribute.py and
concrete constructor callers together. Test per-page settings, empty sheets,
disjoint shards, copied mappings and serialize/deserialize in
tests/test_fan_out.py, tests/test_topology.py, tests/test_containers.py and
tests/test_reading_context.py.

P14: Admit context during edit-copy load, check and mark/fill operations.
Integrate flows/proof_io.py, flows/fill.py and commands/check.py with the shared
flow guard, preserving role-specific error presentation and raw-copy loading
where required. Verify incompatible copies neither resolve addresses nor write
modified JSON, including in-memory entries, in tests/test_check_command.py,
tests/test_fill.py, tests/test_proof_io.py and tests/test_reading_context.py.

P15: Check returned copies against their own received binders and the stage
binder in flows/verify.py. Inspect per-path context before required_places or
coverage calculations. Verify identical SHA/path with changed settings refuses;
legitimate sharding, distinct languages and empty sheets still work. Gates:
tests/test_fan_out.py, tests/test_bus.py, tests/test_reading_context.py.

P16: Enforce context admission at flows/bus.py initial collation before
copy_problems, texts_at, coverage, bases_and_anchors or fold state is built. Use
a failing spy to prove each dependent operation remains uncalled on a context
mismatch, then run a valid fold to prove it is not simply disabled. Gates:
tests/test_bus.py, tests/test_collate_command.py, tests/test_reading_context.py.

P17: Update flows/on_the_page.py PageCache and concrete page lookup consumers to
retain requested context and source identity. Reuse a held source/page only for
the same identity and settings; refuse inconsistent requests rather than
returning a page read under another mode. Test two settings for one path, a
different supplied source version, one acquisition per held snapshot and cached
read failures in tests/test_reading_context.py and tests/test_page_for.py.

P18: Capture source SHA and ReadingContext when flows/places.py and bus.py first
obtain an ungathered move destination. The saved destination base must share
that snapshot. Test later reader/rule/settings changes with unchanged source,
source changes with unchanged rules, and absent destination context. Gates:
tests/test_bus.py, tests/test_docket.py, tests/test_reading_context.py.

P19: Add MasterProof.page_readings in desk/proof/master_proof.py and migrate
producers/loaders in bus.py and proof_io.py. Include reviewed pages and extra
destinations, retaining existing page_shas. Test consistent duplicate page
records, conflicting sheets, missing destination metadata, empty proofs and
exact save/load preservation before place admission in tests/test_containers.py,
tests/test_proof_io.py and tests/test_reading_context.py.

P20: Admit saved master-proof context before resumed turns and dispositions
reach address-dependent state, including directly constructed proof objects.
Cover flows/bus.py and commands/turn.py/disposition.py through their shared flow
entry points. Verify refusal leaves the proof, copies and answer state
unchanged; compatible answers still commit. Gates: tests/test_turn_command.py,
tests/test_disposition_command.py, tests/test_bus.py,
tests/test_reading_context.py.

P21: Preserve context in flows/places.py chief-copy production,
flows/transcribe.py and docket/docket.py Schedule. Update all concrete producers
atomically; serialize required reading metadata and retain each destination's
original context. Verify no default-based reconstruction and agreement of saved
proof, chief sheet and schedule in tests/test_docket.py,
tests/test_proof_command.py and tests/test_reading_context.py.

P22: Enforce installed compatibility and saved settings in flows/proof_setter.py
for original admission and drafted rereads. Preserve SHA-before-parse and reuse
held pages. Test mismatch before any set operation and mismatch on a later file
after an earlier draft, asserting exact original bytes and removal of new output
files/directories. Gates: tests/test_proof_setter.py,
tests/test_reading_context.py.

P23: Wire selected settings into flows/prove_unchanged.py and its command so
both exact snapshots use compatible rules. Preserve existing conservative proof
algorithms. Test per-path choices, missing/unsupported values, same-source but
different context refusal and valid empty source. Gates:
tests/test_proof_command.py, tests/test_source_io.py and
tests/test_reading_context.py.

P24: Complete the concrete address-consumer audit in commands/addresser.py,
carry.py, taken_in.py; flows/carry.py, revise.py and compositor.py; and the
render_page caller if its page interface changes. The systems-owned script
adaptation is limited to the changed interface and its normal-command check.
Verify context is checked before reading saved places, equal-text shortcuts
cannot bypass it, and fresh comparisons use one declared context. Run the
existing addresser/carry/taken_in/revise/compositor suites and context tests.

P25: Add end-to-end compatibility fixtures spanning gather, distribute, mark,
collate, turn/disposition, docket and proof. Use real artifact files and literal
expected contexts; fixture reader bindings can demonstrate dialect transport
without claiming unimplemented language coverage. Test missing old fields,
unknown future formats, rule changes with stable source SHA, unrelated-language
changes, mixed languages/settings, empty sheets, additional move destinations
and rollback. Update affected existing fixtures to contain explicitly valid
context; do not inject a default into production deserializers. Gate: uv run
pytest -q tests/test_reading_context.py plus affected command suites.

P26: Run uv run pytest -q tests/test_language_definitions.py
tests/test_reading_context.py and all touched integration suites, then uv run
pytest -q. Run uv run ruff check ., uv run ruff format --check ., uv run ty
check, uv run python scripts/check_shipped_syntax.py and uv run python
scripts/check_vocabulary.py. Confirm standard-library runtime and existing
import/dependency gates unchanged. Independently review the whole branch,
including new admission bypasses and current prose; resolve branch findings
before closing goals. Record skips/xfails separately. No release assembly.

Review focus: reader revisions and host-grammar differences with stable source
SHA (P9/P25); accepted TOML ordering changes versus significant array order
(P2/P9); contexts on empty or redacted pages and shards (P12/P13/P15);
ungathered move destinations surviving resume and transcription (P18-P21);
admission bypassed by equality shortcuts, in-memory objects or cached pages
(P14-P17/P24). Tests belong to those tasks, not only the final review.

Closure mapping: source-reading-contract T2 closes only when P8-P25 preserve and
enforce context throughout the saved workflow. The new
language-registry-contract goals close after P1-P7 and full integration checks.
Parent P5/P6 and the shared P4 replacement close with this child. The parent's
separate language definitions, language specs, suffix consumer replacements tied
to new readers and removal of retired algorithms remain open. Do not close
language-rows-in-toml T17/T18 or obsolete combined-table prescriptions merely
because this machinery exists.

## TODO tasks this plan closes

### A - [2026-10-11-source-reading-contract](../../TODO/2026-10-11-source-reading-contract.md)

- [ ] T2 | Carry reader compatibility and language settings through saved runs;
      verify incompatible contexts refuse before address use

### B - [2026-10-11-language-registry-contract](../../TODO/2026-10-11-language-registry-contract.md)

- [~] T1 | Load strict independent TOML language definitions; verify explicit
      fields, useful errors and no rule inheritance
- [ ] T2 | Select readers through one registry; verify unique routes, actual
      coverage and excluded file categories

## Plan Tasks

- [x] P1 | Immutable definition validation passes 62 tests and independent review | 72ed0aa4 | Define
      immutable language definitions; verify required fields, explicit empties,
      types and copied nested values
- [x] P2 | Strict TOML decoder passes 109 focused tests and independent review | 42806983 | Decode
      TOML definitions without I/O; verify malformed, missing, unknown and
      unsupported fields refuse
- [x] P3 | Definition acquisition preserves source and diagnostic paths; 119 tests and review pass | c2377616 | Acquire
      definition files in flows; verify path-specific failures and no partial
      registry
- [x] P4 | Registry lookup and refusals pass 162 tests and corrected-contract review | 6aaf1f27 | Build
      the language registry; verify duplicate languages and ambiguous suffixes
      refuse
- [x] P5 | Explicit reader bindings and unchanged dispatch pass 541 tests and review | a6f1bf4c | Bind
      reader identifiers to installed implementations; verify unknown readers
      and unsupported capabilities refuse
- [ ] P6 | Register existing readers independently; verify current suffixes,
      recognition and actual capabilities
- [ ] P7 | Route selection and coverage through the registry; verify excluded
      file categories cannot select code readers
- [ ] P8 | Define immutable reading context; verify effective settings, unique
      keys and value equality
- [ ] P9 | Derive reading compatibility identities; verify relevant changes
      invalidate and unrelated or cosmetic changes do not
        > 2026-10-11 Include definition and bound-reader revisions independently
- [ ] P10 | Resolve per-file settings at fresh-run entry points; verify explicit
      defaults, valid modes and independent values
        > 2026-10-11 resolve_context also requires the bound reader_revision keyword
- [ ] P11 | Serialize reading context; verify exact fields and rejection of
      missing, malformed or future formats
- [ ] P12 | Carry context through pages, binders and redaction; verify empty
      pages and old-artifact refusal
- [ ] P13 | Carry context through distribution and shards; verify per-page
      values and empty sheets
- [ ] P14 | Check context before copy load, mark, check and fill address use;
      verify refusal leaves artifacts unchanged
- [ ] P15 | Check returned copies against received binders; verify context
      admission precedes coverage checks
- [ ] P16 | Admit contexts before collation; verify incompatible inputs never
      reach source lookup, coverage or folding
- [ ] P17 | Validate cached pages against source and context; verify
      incompatible requests cannot reuse a cached reading
- [ ] P18 | Capture move destination source and context together; verify
      ungathered destinations retain their original base
- [ ] P19 | Carry page contexts through saved master proofs; verify extra
      destinations and contradictory records
- [ ] P20 | Validate resumed turns and dispositions before mutation; verify
      incompatible proofs leave saved state unchanged
- [ ] P21 | Carry context through chief copies and docket schedules; verify
      agreement with the originating proof
- [ ] P22 | Validate contexts before drafting and rereading; verify exact
      rollback after later-file refusal
- [ ] P23 | Apply compatible per-file settings to standalone proof; verify both
      snapshots use the same declared rules
- [ ] P24 | Admit contexts in remaining address consumers; verify shortcuts and
      in-memory inputs cannot bypass checks
- [ ] P25 | Exercise saved-run migration end to end; verify mixed settings, old
      artifacts, moves and rollback
- [ ] P26 | Verify focused and full suites, lint, typing, syntax and vocabulary;
      independently review the complete branch
