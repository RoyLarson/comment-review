# BLOCK-CONTEXT -- plugins/comment-review/skills/comment-review/scripts/galley.py

## Census disagreement -- reported, not guessed

The brief says: *"You are given a numbered census and the mechanical resolutions for it. Read it
start to finish and return at least one RECORD for EVERY numbered block."*

The census supplied numbers **223 paragraphs**, and **212 of them carry `0L` -- zero prose
lines**. They are `interval`, `margin` and `dark-matter` rows whose payload is a line of *code*
(`@b0` ... `@b32`, `@b34` ... `@b107`, `@f0`, `@f1`, `@c0` ... `@c106`). There is no comment or
docstring at those addresses to rule on, so a verdict on them would be a verdict on the program,
which the brief forbids ("The subject is the prose, not the program").

**Eleven paragraphs hold prose**, and each has at least one RECORD below:

| index | address | kind | lines |
| --- | --- | --- | --- |
| 107 | `@a0` | docstring | 1-33 |
| 113 | `@c5` | trailing-comment | 42 |
| 115 | `@a1` | docstring | 46-51 |
| 118 | `@a2` | docstring | 56-70 |
| 127 | `@a3` | docstring | 81-85 |
| 134 | `@a4` | docstring | 94-99 |
| 145 | `@a5` | docstring | 112 |
| 146 | `@b33` | comment | 113 |
| 172 | `@b58` | comment | 142-145 |
| 201 | `@b86` | comment | 176-177 |
| 220 | `@b104` | comment | 198-199 |

Two further format disagreements, stated rather than guessed:

1. **The `BLOCK` field is ambiguous in this census.** Every paragraph carries BOTH a sequential
   index (1-223) and an address (`@a5`, `@b58`). The brief's example (`BLOCK 17`) knows only the
   index. I emit the index in `BLOCK` and repeat the address in `LOCATION`, so a joiner reading
   either can attribute the record.
2. **The census reports its own name corpus as unreliable.** Its `NOT CHECKED` section says the
   corpus was built by *walking the tree*, and that *"A file missing from the name corpus turns
   every symbol defined only there into a false obituary."* Every `UNRESOLVED symbol` note it
   carries is therefore a CANDIDATE I am not permitted to settle: my file list is one file and I
   may not open the wider repo. Those become `query`, not `correct` and not `clean`.

The brief specifies a text RECORD shape and no JSON, so no `record.json` is written.

---

## RECORDS

```text
--- RECORD
BLOCK       145
VERDICT     correct
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:112 (@a5)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:195
QUOTE       written += 1
SUMMARY     "Write a galley of every file an edit touches" || a galley is written for a file only after it survives three refusal paths, so the population is files an edit touches MINUS unreadable files, files with overlapping edits, and files with a stale range
FINDING     "every file an edit touches" over-claims: three `continue` paths in `main` skip a file before it is ever written
CHANGE      false: "a galley of every file an edit touches" / true: "a galley of every file whose edits all still match the census and share no line" -- settled by the three `continue` statements in `main` (unreadable source, `clash`, `stale`), each of which runs before `target.write_text`
---
```

The census itself flags this paragraph `counted` and instructs *"RE-COUNT, and name the
population: 'every file'"*. Enumerated over the population **files reaching `by_path`**: a file
leaves the loop unwritten if `source.read_text` raises `READ_ERRORS`, if `overlaps(ranges)`
returns a pair, or if `stale` is non-empty. Only the fall-through reaches `written += 1`. The
sentence also states the refusal behaviour ("and report what refused"), which is true -- `main`
prints a `REFUSED` line on every one of those paths -- so the correction touches the first clause
only.

```text
--- RECORD
BLOCK       115
VERDICT     correct
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:46-51 (@a1)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:52
QUOTE       return "\r\n" if "\r\n" in text else "\n"
SUMMARY     "The ending this text uses" || the function returns CRLF when the text contains ANY CRLF and LF in every other case; it can never return the bare CR that `splice` in this same file treats as a line terminator
FINDING     the summary line states a fact about the text; the code states a two-way test, and the two disagree on a mixed-ending file and on a CR-only file
CHANGE      false: "The ending this text uses, as the joiner a rewrite must use." / true: "CRLF if this text contains any CRLF, otherwise LF -- the joiner a rewrite must use." -- settled by the `return` in `line_endings`, whose conditional has exactly two arms
---
```

A docstring that does not match its own file: `splice`, four functions below, tests
`text.endswith(("\n", "\r"))`, so this module does contemplate a bare CR terminator -- but
`line_endings` cannot report one, and `str.splitlines` in `splice` splits on it. The rationale
sentence beside it (*"Taken from the file being spliced, not from the platform"*) is TRUE and is
`clean`; only the summary line is corrected.

```text
--- RECORD
BLOCK       107
VERDICT     query
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:16-23 (@a0)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:42
QUOTE       from repo import READ_ERRORS  # noqa: E402  -- path shim must run first
SUMMARY     "`address_problem` refuses it and `edit_problem` measures one claim against one edit ... so every check in `verdicts.py` works on it UNCHANGED" || the only module this file imports is `repo`; nothing here defines, imports or calls `address_problem`, `edit_problem` or anything from `verdicts.py`
FINDING     three names and one cited path that this file never touches, and the census resolver reports all four UNRESOLVED
CHANGE      the claim: `address_problem`, `edit_problem` and `verdicts.py` exist and behave as described. ATTEMPTED: read every import and every call in galley.py (only `repo.READ_ERRORS`); read the census's mechanical resolutions, which report `-> UNRESOLVED symbol address_problem`, `-> UNRESOLVED symbol edit_problem`, `-> UNRESOLVED path verdicts.py`. WOULD SETTLE: `findReferences`/`workspaceSymbol` on the two names, or a directory listing beside this script showing whether `verdicts.py` is present -- neither is available: no language server answered, and my file list is this one file
---
```

I cannot upgrade this to a tombstone `correct`. The census's own `NOT CHECKED` block says its
name corpus was built by walking the tree and that a file missing from it *"turns every symbol
defined only there into a false obituary"*, so `UNRESOLVED` here is a weakened signal, not a
death certificate. Marking it `clean` would certify three names I never resolved.

```text
--- RECORD
BLOCK       107
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:30-32 (@a0)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:186
QUOTE       if stale:
SUMMARY     "A census range that no longer matches the file, or two edits over one line, stops that file rather than writing a galley nobody can trust." || both named conditions are computed before any write and each `continue`s past `target.write_text`
FINDING     block-context: the two stated stop conditions match the two guards, and both precede the only write
CHANGE      block-context clean
---
```

Checked as a constraint against the code that enforces it. `stale` is built from `block_matches`
over **every** entry in `file_edits`; `clash` comes from `overlaps(ranges)`. Both land before
`target.write_text(splice(text, ranges), ...)`, and each takes `continue`, so the file is skipped
whole rather than half-spliced. Direction and boundary agree: `stale` is non-empty, `clash` is
not None.

```text
--- RECORD
BLOCK       107
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:6-8 (@a0)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:193
QUOTE       target.write_text(splice(text, ranges), encoding="utf-8", newline="")
SUMMARY     "every block a stage proposes to change, spliced into a copy of its file under `--out`. Nothing under `--repo` is touched." || the module's only write is to `out / rel`; `repo / rel` is opened with `read_text` and never written
FINDING     block-context: the write/read split the sentence asserts is the split the code performs
CHANGE      block-context clean
---
```

Enumerated the population **every write in this module**: one, `target.write_text`, whose target
is rooted at `out`. `target.parent.mkdir` is the only other filesystem mutation and is likewise
under `out`. `repo` appears once, as `source = repo / rel`, read-only.

```text
--- RECORD
BLOCK       107
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:3 (@a0)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:126
QUOTE       ap.add_argument("--out", required=True, help="directory the galley is written to")
SUMMARY     "python galley.py --repo D --census census.json --edits edits.json --out DIR" || `main` declares exactly these four options; `--repo` defaults to "." and the other three are required, so the usage line is a runnable invocation
FINDING     block-context: the worked invocation names every required option and no option the parser does not define
CHANGE      block-context clean
---
```

A worked example is executed, never read -- this one cannot be executed from the checkout, since
it needs a `census.json` and an `edits.json` that no fixture here supplies. What I could check is
its *shape* against the parser, and every flag resolves. The census's
`-> UNRESOLVED path census.json` and `-> UNRESOLVED path edits.json` notes are the resolver
reading placeholder filenames in a usage line as citations; they are not path claims and need no
correction.

```text
--- RECORD
BLOCK       113
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:42 (@c5)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:40
QUOTE       sys.path.insert(0, str(Path(__file__).resolve().parent))
SUMMARY     "path shim must run first" || the `sys.path.insert` two lines above is what puts this script's own directory on the path, and `repo` is importable only from there
FINDING     block-context: the suppression's stated reason is the statement immediately above it, and that statement is present
CHANGE      block-context clean
---
```

```text
--- RECORD
BLOCK       118
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:56-69 (@a2)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:73
QUOTE       for start, end, replacement in sorted(edits, reverse=True):
SUMMARY     "APPLIED IN DESCENDING ORDER" and "1-based and inclusive" || `sorted(edits, reverse=True)` is descending by start, and `lines[start - 1 : end]` is a 1-based inclusive range
FINDING     block-context: value, direction and boundary of the stated contract all match the enforcing lines
CHANGE      block-context clean
---
```

Constraint checked on all four axes. UNITS: line numbers. VALUE and BOUNDARY: `start - 1` as the
slice start and a bare `end` as the slice stop is exactly 1-based-inclusive. DIRECTION:
`reverse=True` is descending, as stated. The reason given for it -- that a replacement of a
different length shifts every range below -- is confirmable from the length-changing slice
assignment in the loop body.

```text
--- RECORD
BLOCK       118
VERDICT     query
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:68-69 (@a2)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:181
QUOTE       clash = overlaps(ranges)
SUMMARY     "The caller has already refused overlaps, so descending order is exact." || within this file `splice` has exactly one call site, in `main`, and it does refuse overlaps first -- but `splice` is a module-level name any other module may import, and I cannot enumerate importers
FINDING     an exclusivity claim ("the caller", singular) whose population I could enumerate inside this file and not outside it
CHANGE      the claim: every caller of `splice` refuses overlapping edits before calling. ATTEMPTED: enumerated call sites of `splice` in galley.py -- one, in `main`, guarded by `overlaps(ranges)` and its `continue`; read the census, which lists no other file. WOULD SETTLE: `findReferences` on `splice`, or a grep of the tree for `splice(` -- neither is available: no language server answered and my file list is this one file
---
```

The brief's warning applies exactly here: grepping the name `splice` and finding the guard above
its one visible call would pass a claim that was never about existence. The claim is **one**, and
one file cannot count it. `splice` carries no guard of its own, so if the claim is false the
function silently produces a wrong file rather than refusing.

```text
--- RECORD
BLOCK       127
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:81-85 (@a3)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:88
QUOTE       if b_start <= a_end:
SUMMARY     "The first pair of edits sharing a line, or None." || the loop walks `sorted(edits)` in ascending start order and returns on the first pair whose successor starts at or before its predecessor's end, otherwise falls through to `return None`
FINDING     block-context: the summary's value, direction and boundary match the comparison that enforces them
CHANGE      block-context clean
---
```

BOUNDARY is the axis worth naming: `<=` means two edits that merely *touch* -- one ending where
the next begins -- are reported as sharing a line, which is what "sharing a line" says, since the
census ranges are inclusive. The named symbol `CHANGE` in this docstring, which the census
reports `UNRESOLVED symbol` and marks a CANDIDATE, is not a program symbol: it is a field of the
record format defined in the shared reviewer brief. That candidate is settled and needs no
verdict.

```text
--- RECORD
BLOCK       134
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:94-99 (@a4)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:106
QUOTE       return [ln.rstrip() for ln in lines[start - 1 : end]] == [
SUMMARY     "Does the file still read the way the census recorded this block?" || the body compares the file's current lines over the recorded range against the block's stored `raw_lines`, both right-stripped
FINDING     block-context: the question the docstring poses is the comparison the body performs, and the rationale beside it describes the failure the comparison prevents
CHANGE      block-context clean
---
```

The rationale -- *"Splicing a range whose content has moved writes the replacement over whatever
is there now"* -- is a claim about what `splice` would do, and it is confirmable: `splice`
performs an unconditional slice assignment with no check of its own. The docstring does not claim
an exact comparison, and the `rstrip` on both sides does not contradict it.

```text
--- RECORD
BLOCK       146
VERDICT     query
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:113 (@b33)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:116
QUOTE       reconfigure(encoding="utf-8", errors="replace")
SUMMARY     "A Windows console is cp1252; one non-ASCII glyph in a report kills the run." || every literal this module prints is ASCII, but its interpolations are not -- the relative path, the out directory, the repr'd key and the JSONDecodeError text can each carry a non-ASCII character
FINDING     the premise is an environment fact about the operator's console, which no reading of the checkout can settle
CHANGE      the claim: a Windows console is cp1252, and an unencodable glyph raises rather than degrades. ATTEMPTED: read every `print` in this module for a non-ASCII literal (none) and for interpolations that could carry one (the relative path, the out directory, the repr'd key, the decode error); confirmed the guard runs before the first `print`. WOULD SETTLE: running this script on a Windows console with a non-ASCII path, which needs an operator and a machine, not a checkout
---
```

Marked `query` rather than `clean` deliberately: the guard's *presence* and *position* are
confirmable and the comment describes them accurately, but the reason it gives -- the encoding a
console defaults to, and that the failure is fatal rather than lossy -- is settled outside the
code. Certifying it would be certifying something I did not check.

```text
--- RECORD
BLOCK       172
VERDICT     query
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:143-144 (@b58)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:103
QUOTE       stored = block.get("raw_lines") or []
SUMMARY     "its `raw_lines` is the only record of what the file said when the reviewers read it" || `raw_lines` is read at exactly one site in this module, in `block_matches`, but whether the census carries a second transcription is a fact about the census producer, which is not in my file list
FINDING     a "single source of truth" claim about a data structure this module only consumes
CHANGE      the claim: the census block's `raw_lines` is the sole surviving transcription of the reviewed text. ATTEMPTED: enumerated every read of `raw_lines` in galley.py -- one, in `block_matches`; enumerated every key this module takes off a block (`path`, `start`, `end`, `raw_lines`). WOULD SETTLE: reading the module that writes the census JSON, to see what other fields a block carries -- not available: my file list is galley.py alone and no language server answered
---
```

```text
--- RECORD
BLOCK       172
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:142-145 (@b58)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:160
QUOTE       by_path.setdefault(block["path"], []).append(
SUMMARY     "Group by file, because a splice is a whole-file rewrite. The CENSUS BLOCK travels with each edit ... comparing the file to itself would make the staleness check below unable to fail." || the dict is keyed on the block's path, the appended tuple's fourth element is the block itself, and `block_matches` compares the file against that carried block rather than against a re-read of the file
FINDING     block-context: the grouping, the carried block and the stated failure mode all match the code
CHANGE      block-context clean
---
```

The last clause is the one worth confirming rather than assuming, because it is a claim about
what a check *could* do rather than what it does: if `stored` were re-read from the current file,
`block_matches` would compare a list against itself and could never return False. That the block
travels in the appended tuple is what prevents it, and it does travel -- the tuple's fourth
element is `block`.

```text
--- RECORD
BLOCK       201
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:176-177 (@b86)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:179
QUOTE       (s, e) for s, e, _, block in file_edits if not block_matches(lines, block)
SUMMARY     "Every block is checked against the file BEFORE anything is written, so one stale range refuses its file rather than half-splicing it." || the comprehension iterates all of `file_edits`, and the only write in the loop body is fourteen lines below, past a `continue`
FINDING     block-context: the quantifier "every" holds -- the comprehension has no early exit and no filter other than the check itself
CHANGE      block-context clean
---
```

Population enumerated: `file_edits`, the whole list, with no `break` and no slice. "BEFORE
anything is written" holds because `target.write_text` is the only write and `if stale:` takes
`continue`. Note that the *order* of the two guards is the reverse of the module docstring's --
`clash` is tested first -- but the comment claims precedence over the WRITE, not over the other
guard, so this is not a finding on the prose.

```text
--- RECORD
BLOCK       220
VERDICT     clean
LOCATION    plugins/comment-review/skills/comment-review/scripts/galley.py:198-199 (@b104)
EVIDENCE    plugins/comment-review/skills/comment-review/scripts/galley.py:200
QUOTE       return 1 if refused else 0
SUMMARY     "Nonzero when anything refused." || `refused` is incremented on all five refusal paths and the return is 1 whenever it is truthy
FINDING     block-context: the exit-code constraint matches the expression that enforces it, on every path that can set the counter
CHANGE      block-context clean
---
```

Enumerated the population **every path that refuses an edit in `main`**: five -- non-integer key,
index outside the census, unreadable source, `clash`, `stale`. Each increments `refused` before
its `continue`, so none can leave the function with `refused` at zero. The two early `return 2`
paths are also nonzero and do not contradict the claim.

---

## CODE CONCERNS

- `line_endings` can never return a bare CR, yet `splice` treats CR as a line terminator in its `endswith` test, so a CR-only file is silently rejoined with LF.
- `block_matches` returns False when a block carries no `raw_lines`, so a census produced without that key refuses every file with no message distinguishing it from a genuinely stale range.
- `main` tests `clash` before `stale`, so a file holding both defects is reported only as an overlap and the stale range is never named.
- `overlaps` compares only adjacent pairs of `sorted(edits)`, which is sufficient only because it returns on the first hit; a change that collected all pairs would need a different walk.
