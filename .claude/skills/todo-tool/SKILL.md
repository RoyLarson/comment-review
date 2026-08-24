---
name: todo-tool
description: Create, edit, check off tasks in, re-file, close, or query TODO/*.md files and TODO/README.md's tables via scripts/todo_tool.py instead of hand-editing them with Read/Edit/Write or grepping/reading every file by hand. Covers BOTH directions — writes (filing a new TODO, ticking or adding a checkbox, changing Owner or Status, closing/superseding, leaving a dated note, rewriting a TODO's Objective) AND read-only queries (what's assigned to a given owner, what's still open/decision-needed/blocked for a role, pulling just the TODOs relevant to a session before starting work). Trigger even when the phrasing doesn't name the tool, doesn't say "list," and reads like an ordinary investigative question — "add this to the TODO list", "mark that task done", "what's assigned to backend", "what's testing still waiting on a decision for", "what does systems still have open", "close out that TODO as superseded" all mean use this skill's `list`/mutation commands, not Read/Grep across TODO/*.md by hand. The tool recomputes Progress:/README N-M counts from the actual checkboxes on every write (the thing a hand-edit gets wrong) and `list` filters TODO/README.md's tables directly (far cheaper than opening every file); prefer it over manual reads or edits for anything it covers.
---

# todo-tool

`scripts/todo_tool.py` is the write-side companion to the read-only
`scripts/tests/test_todo_counts_agree.py` checker. A TODO file's `Progress:`
header line and its row in `TODO/README.md` are both *derived* facts —
they should always equal a recount of the file's own `- [ ]`/`- [x]`
boxes. Hand-editing a TODO with Read/Edit/Write means updating those
derived numbers yourself, which is exactly the kind of arithmetic a
session doing several things at once gets wrong under its own steam. The
tool computes them from the boxes on every write, so that class of bug
can't happen through it. **Reach for this before Read/Edit/Write whenever
the task is something the tool covers** (see the table below) — direct
edits are still the right call for things it doesn't cover (see
*What this tool does not do*).

Run every command as:

```bash
uv run python scripts/todo_tool.py <command> ...
```

All commands accept `--todo-dir PATH` to point at a different directory
than the real `TODO/` — use this for any testing, dry-running, or
exploration so nothing touches the real files. See *Testing against a
scratch copy* below.

**Every write in this tool goes through a crash-safe primitive**, not just
`resync`'s: it writes a same-directory temp file, verifies the write
round-tripped byte-for-byte, and — if the text being written has its own
`Progress:` line — checks it against that text's own checkbox count, before
atomically replacing the target file. That means a disk/handle fault makes
ANY mutating command raise a clean `ValueError` rather than ever leaving a
partial or corrupted file on disk — and a file whose `Progress:` line
already disagrees with its own boxes (e.g. merge drift) makes a
header-only command (`set-owner`, `set-status`, `note`) raise the same
way, since only a command that recomputes `Progress:` from the boxes
before writing (`check`/`uncheck`, `add-task`, `replace-objective`,
`create`) can self-heal that drift instead of tripping over it. See
*Errors* below for what to do when that happens.

## Commands

| Task | Command |
| --- | --- |
| File a new TODO | `create "<title>" --owner OWNER --raised-from TEXT --task "<task 1>" [--task "<task 2>" ...] [--status STATUS] [--summary TEXT] [--slug SHORT-NAME] [--requires-roy]` |
| Check off task *n* | `check <file> <n>` |
| Uncheck task *n* | `uncheck <file> <n>` |
| Add a new task | `add-task <file> "<task text>"` |
| Change who owns it | `set-owner <file> "<owner text>"` |
| Flag / unflag that Roy must act | `set-requires-roy <file> true｜false` |
| Change its status | `set-status <file> <status> [--note TEXT]` |
| Close it | `complete <file> --outcome "<one-line outcome>" [--superseded]` |
| Fix README drift after a merge | `resync [--todo-dir PATH]` |
| Leave a dated note | `note <file> --text "<text>" [--label LABEL] [--date YYYY-MM-DD]` |
| Rewrite its Objective | `replace-objective <file> (--text "<body>" \| --text-file PATH)` |
| List / filter open TODOs | `list [--owner TEXT] [--status STATUS] [--requires-roy] [--notes]` |

`<file>` takes either `some-slug.md` or bare `some-slug` — the tool
normalizes it. Every command that mutates a file also updates its
`TODO/README.md` row and section count in the same write; you never need
a separate step for that.

### `create` — filing a new TODO

```bash
uv run python scripts/todo_tool.py create \
  "A short, specific title naming the actual problem" \
  --owner systems --raised-from "found while reviewing X" \
  --task "First concrete, checkable thing to do" \
  --task "Second thing" \
  --status decision-needed \
  --requires-roy \
  --slug short-problem-name
```

This writes the five-field header (`Status`/`Progress`/`Owner`/`Requires-Roy`/`Raised`),
a one-sentence `## Objective` stub (title + period — write the real prose
afterward with `replace-objective`, the tool doesn't generate it), and a
`## Tasks` section with one `- [ ]` per `--task`. It also inserts the
README row into the right section (mapped from `--status`; see below) and
bumps that section's count. `--summary` is the README row's "what" text
if it should differ from the title; `--status` defaults to `open`.
Requires at least one `--task` — a TODO with zero tasks isn't a TODO.
Refuses to overwrite an existing file with the same slug.

**Always pass `--slug`, and keep it short.** Without it the filename is the
whole slugified title, and a title specific enough to name the actual problem
makes a filename nobody wants to type or read — `TODO/create-todo-derives-progress-from-the-tasks-block-not-the-document.md`
is a real one. The title should stay long and descriptive; the *stem* is what
gets abbreviated. Aim for **three to five words, ~40 characters**, keeping the
subject and the verb that make it findable:

| Title | Good `--slug` | Not this |
| --- | --- | --- |
| The em dash is written two different ways in two references | `em-dash-naming` | `em-dash-is-written-two-ways-in-two-references` |
| `create` derives Progress from the Tasks block, not the document | `create-progress-scope` | `fix-it`, `todo-1` |
| `ruff check` reports 347 pre-existing errors across the repo | `ruff-preexisting-errors` | `ruff` |

Keep it unique and specific enough to still mean something in a list of forty
— `ruff` or `naming` collides with the next one; a bare number or `fix-it`
means the README link tells a reader nothing. The stem is what every other
command addresses the TODO by (`check em-dash-naming 2`) and what the
README row links as, so it is worth ten seconds of thought. It is slugified
for you, and a typed `.md` is dropped, so `--slug "Em Dash Naming.md"`
and `--slug em-dash-naming` land in the same place.

### `check` / `uncheck` — toggling a task

```bash
uv run python scripts/todo_tool.py check speed-strength-backs-off-the-wrong-set 3
```

`<n>` is 1-indexed, counting real (non-fenced) checkboxes in document
order — the same order you'd read them in the file. Recomputes
`Progress:` and the README `N/M` cell from the result.

### `add-task` — appending a task

```bash
uv run python scripts/todo_tool.py add-task some-slug "A newly-discovered thing to do"
```

Appends after the last existing task (and any of its wrapped continuation
lines). There's no command to reword an *existing* task's text — that's
still a direct edit (see below).

### `set-requires-roy` — does Roy have to do something?

```bash
uv run python scripts/todo_tool.py set-requires-roy stet-has-no-mark true
```

`Owner:` and `Requires-Roy:` answer different questions and used to be
crammed into one field. **Owner is whoever ticks the boxes** — the lanes
doing the work, and **`Roy` among them whenever he ticks ANY box**, not
only when the whole file is his. **`Requires-Roy: true` means a DECISION
is owed by Roy** — a ruling, an approval, a call — whoever owns the rest
of the file.

⚠ **Decisions only, and `Owner: Roy` does NOT imply the flag.** Work he
owes, data only he can produce, an analysis only he triggers are real
blockers but are not this flag — `verify-unlabelled-census-rows` is
339 units of his own work with no decision in it, so it is `Owner: Roy`
with the flag FALSE, and `list --owner Roy` is what finds it. Mixing the
two turns the queue into a to-do list instead of the answer to *what am I
blocking*.

⚠⚠ **That makes `Owner:` the ONLY record of work he owes, so never drop
him from it to "clean up" a mixed field.** Removing him while the flag is
correctly false leaves the work in neither query. Three files were lost
this way on 2026-08-16 and had to be restored.

⭐ **SET IT AS SOON AS YOU HIT ONE.** The flag is live, not a
classification made once. Working a TODO and reaching a task you cannot
do because Roy has to rule on something? Set it in that moment, and clear
it when he answers. Hand-unblocking these has cost a session a great deal
of effort and context; a flag set the day the wall is hit is the whole
point of the field.

Writes the file's field and the README's `roy?` cell in one command, and
inserts the field when a file predates it, so a reopened TODO gets one on
the way out. `resync` repairs this cell when the two disagree — as it now
does the owner cell, since both are derived from the file rather than
authored into the table.

⚠ **`complete` clears the flag, and `reopen` brings the file back with it
FALSE.** A closed TODO owes no decision, and whether one is owed again is
a fresh judgment — carrying a stale `true` across a close/reopen would
put a demand back in Roy's queue that he may already have answered.

⚠ **It is a judgment about the TASKS, never a text match on his name.**
`verify-unlabelled-census-rows` is entirely his and says "Roy" in
none of its 339 task lines; other TODOs quote him in `Owner:` saying the
work belongs to a lane. Read what the boxes ask for.

### `set-owner` / `set-status` — header fields

```bash
uv run python scripts/todo_tool.py set-owner some-slug "backend · Roy"
uv run python scripts/todo_tool.py set-status some-slug blocked --note "waiting on the anchor reseed"
```

⚠ **Write the owner as a `·`-separated list, each item starting with its
lane** — `testing (the finding) · backend (the consumers)`.
The README cell is DERIVED from the field: the lanes alone, annotations
dropped. That keeps the table scannable while `list --owner` still finds
every lane the field names, and it is what lets `resync` repair the cell.
Only the LEADING name of a segment counts, so a lane your prose merely
mentions ("Phase A was backend's") is correctly ignored. `·`, `+`,
`→`, `,`, `/` and the word "with" all separate segments; `;` does not,
because every field that uses one uses it as prose. ⚠ A co-owner buried
mid-sentence still will not reach that lane's queue, and nothing can
detect it — write the list, don't narrate it.

`set-owner` takes free text — this repo's Owner field already uses
`·`-joined lists and `→`-chains, so there's no enum to satisfy.
`set-status` rewrites the `Status:` line and, if the new status maps to a
different README section than the one the file is currently filed under,
moves its row there — including creating a `### blocked` section on
demand if none exists yet. `--note`, if given, is shorthand for also
calling `note` (below) with the default label, so a status change can
carry its one-line reason in the same command.

**Status → README section:**

| `set-status` value (or prefix) | Section |
| --- | --- |
| `decision-needed` | `### decision-needed` |
| `in-flight` (any `(who)` suffix) | `### in flight` |
| `blocked` | `### blocked` (created on demand) |
| anything else, including `open` | `### open` |

There is no `done` status — closing a TODO is `complete`, below.

### `complete` — closing a TODO

```bash
uv run python scripts/todo_tool.py complete some-slug --outcome "Fixed by deleting the branch that caused it"
uv run python scripts/todo_tool.py complete some-slug --outcome "Never implemented, no longer needed" --superseded
```

Moves the file to `TODO/completed/`, removes its row from whichever Open
section it was in, and adds a row to the Completed table with the
`--outcome` you give it (the tool never generates this — you write the
one-line summary of what actually happened). `--superseded` renames the
file to `<slug>-SUPERSEDED.md`, for the "never implemented, no longer
needed" case specifically. Does **not** require every checkbox to be
checked — closing an item early or as superseded is a legitimate reason
to complete with open boxes.

### `resync` — fixing README drift after a merge

```bash
uv run python scripts/todo_tool.py resync
```

Recomputes every derived number and placement in `TODO/README.md` from what
is actually on disk: each open TODO's own `Progress:` header (and every
`completed/` file's own `Progress:` header too), the README
`N/M` cell, a missing README row (added from the file's own
`Status:`/`Owner:`/title), a row sitting in the wrong section relative to
its file's own `Status:`, and every `### section (N)` header count. Meant to
run right after any merge that touched `TODO/` — a merge combines edits
from two branches that each recomputed correctly against their own base,
and the union can still disagree even though neither branch was wrong
alone. Safe to run any time; a no-op when everything already agrees.

⚠ **Writes every fix it can make, then raises if any remain.** Four kinds
of problem are left untouched and collected instead of fixed: a README row
(Open or Completed) pointing at a file that no longer exists where the
table says — deciding whether it was closed, renamed, or just lost a
`git mv` needs a human; a `completed/` file with no matching row in the
README's Completed table — the mirror case, invisible rather than wrong
until this scan runs; an open file whose own header `resync` can't read
(no fenced header block, or a header missing its `Status:` field, the
shape a botched merge conflict resolution can leave behind); and a write
that failed its own crash-safety check (a round-trip mismatch, or a
`Progress:` line disagreeing with its own boxes) — covers both a file's
own `Progress:`-header write and `resync`'s own final README write.
`resync` collects all four, applies every other fix first, and only then
raises listing them — the one command in this tool that does not validate
everything before writing anything (every other command aborts with
nothing written on any failure; see *Errors* below).

### `note` — a dated one-liner

```bash
uv run python scripts/todo_tool.py note some-slug --text "scope narrowed to one question after the reseed landed"
uv run python scripts/todo_tool.py note some-slug --text "one of three tasks answered" --label Narrowed
```

Appends `{Label}: {date} — {text}` to the header block, stacking
chronologically under `Raised:`. `--label` defaults to `Updated`; pick a
more specific verb (`Narrowed`, `Reopened`, `Deferred`, ...) when it says
something sharper than "updated." This is a terse, append-only
*consistency* log — see `replace-objective` for the opposite case.

### `replace-objective` — rewriting the Objective wholesale

```bash
uv run python scripts/todo_tool.py replace-objective some-slug --text-file /tmp/new-objective.md
```

Replaces everything between `## Objective` and the next `##` heading with
fresh markdown — tables, bold callouts, multiple paragraphs, whatever the
update needs. Use this instead of `note` when understanding has changed
enough that the *old* Objective is actively misleading, not just
incomplete — a chain of terse notes doesn't leave a reader with a
coherent current picture the way a fresh, complete rewrite does. Prefer
`--text-file` over `--text` for anything beyond a short paragraph: quoting
multi-paragraph markdown (with its own blank lines, backticks, and
quotes) as a single shell argument is exactly the kind of thing that goes
wrong. Write the new body to a scratch file first — that's also a chance
to review it before committing to the rewrite.

### `list` — filtering without opening every file

```bash
uv run python scripts/todo_tool.py list --owner backend
uv run python scripts/todo_tool.py list --status decision-needed --notes
uv run python scripts/todo_tool.py list --requires-roy
```

`--requires-roy` is how Roy pulls his own queue: everything waiting on
him, across every lane and status, whoever owns it. Matching rows print a
`[ROY]` marker after the owner. Combines with the other filters —
`list --requires-roy --status decision-needed` is the subset he is
actively blocking.

Reads only `TODO/README.md`'s tables (fast) unless `--notes` is given, in
which case it additionally opens each *matching* file's header block —
never a file that didn't match the filter. `--owner` matches
case-insensitively as a substring, so `--owner backend` also
matches a cell like `agents · backend`. `--status` matches
against the section a row lives in (the same mapping `set-status` uses),
not a literal string match against the file's own `Status:` text. Use
this at the start of a session to pull just the TODOs relevant to the
role you're working in, instead of reading `TODO/README.md` end to end.

⚠ Because `--status` reads the README's section placement rather than
re-opening each file, it can disagree with a file's own `Status:` line if
the two have drifted apart (e.g. a `Status:` field hand-edited without
going through `set-status`, which is the only thing that also moves the
README row). This has actually happened in this repo's real `TODO/` —
some rows sit in the README's `decision-needed` table while their own
file says `Status: open`. If precision on "still genuinely blocked on a
decision" matters more than speed, use `list --status decision-needed
--notes` to pull the candidates cheaply, then check each match's own
`Status:` line (shown in the `--notes` output) before trusting it — don't
silently assume the two always agree.

## What this tool does not do

Direct Read/Edit/Write is still the right tool for:
- Rewording an *existing* task's text (only appending new ones is
  supported)
- Editing `Raised:` in place, or anything about the header format itself
- Adding/editing a `## Not in scope` section
- The README's free-text "What to do next" narrative at the top, or the
  wording of a Completed-table `outcome` beyond what you pass to
  `--outcome`
- Anything involving `TODO/completed/*-SUPERSEDED.md` naming decisions
  outside the `--superseded` flag's fixed convention

If you're about to open a TODO file or `TODO/README.md` with Edit and the
change is "tick a box," "add a task," "change who owns this," "change its
status," "close it," "leave a note," or "rewrite the objective" — stop and
use the matching command above instead. If it's something else, editing
directly is fine; the tool was built to remove the arithmetic-prone edits,
not to be the only way to touch these files.

## Testing against a scratch copy

Every command takes `--todo-dir PATH`. For anything exploratory — trying
a command to see what it does, testing a workflow, demonstrating the tool
— copy `TODO/` somewhere under a scratch/temp directory first and pass
that as `--todo-dir`, the same way the tool's own test suite never
touches the real directory. Never point `--todo-dir` at the real `TODO/`
for anything other than an intentional, real edit.

## Errors

A failed command (missing file, malformed input, a file with no README
row) prints `error: <message>` to stderr and exits nonzero without
writing anything — mutations are validated before any file is touched, so
a failure never leaves a TODO half-updated. If a command fails, read the
message; it names the file and what was wrong.

Any mutating command can also fail with the crash-safety `ValueError`
described above, not just `resync` — e.g. `set-owner` on a file whose
`Progress:` line already disagrees with its own boxes. That error message
tells you to run `resync` first; do that, then retry the original command.

`resync` is the one exception: it writes every fix it can make
unambiguously, and only afterward raises if any README row still points at
a missing file, any `completed/` file has no matching README row, any open
file's own header couldn't be read, or any write (a file's own
`Progress:`-header write, or `resync`'s own final README write) failed its
own crash-safety check — see its own section above.
