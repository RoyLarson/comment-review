# The middle chain smoke: implementation plan

> **For agentic workers:** the required sub-skill is `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans`. Implement this plan task by task; steps use checkbox syntax for tracking.

**Goal:** Repair the six defects that stop the middle composing, then build a PowerShell script that drives `gather` through `proof` with every decision planted, so the chain is shown to work before an agent's reasoning is added to it.

**Architecture:** Tasks 1 to 6 are repairs, each landing with a test that fails first. Tasks 7 to 10 build the smoke script, which writes its own fixture tree, drives the real console face of every command, and asserts two things: every stage exits 0, and the diff of the original tree against the proof is exactly what was planted.

**Tech Stack:** Python 3.11, pytest, PowerShell 7, `uv` for every invocation.

**Spec:** [`docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`](../specs/2026-09-08-the-middle-chain-smoke-design.md)

## Global Constraints

- **Run everything through `uv run`.** The project is pinned to Python 3.11 in `.python-version` and `[project] requires-python`. A bare `python` re-opens the gap pinning closed.
- **ASCII only**, in files and terminal output. `--` not an em dash, `->` not an arrow.
- **No heredocs and no `sed`,** anywhere. A multi-line value reaches a command through a file and `@path`, never through the shell. `~/.claude/hooks/shell-eats-text.py` refuses both.
- **Prose carries no bang prefix and no run of capitalised words.** `~/.claude/hooks/emphasis-guard.py` refuses a markdown write that does, including a commit message file. It refused this plan's own header once.
- **A commit message goes in a file**, then `git commit -F <file>`.
- **The word `cap` means one thing:** the constraint on how long and wide prose can be. The turn limit is **max turns**; the chief's command is **`disposition`**.
- **After each unit: commit the work, then tick its board task in a later commit naming the work's sha.** The board is `job-board --plans-dir docs/plans`.
- **Gates, in order:** `uv run ruff check .`, then `uv run ruff format .`, then `uv run ruff check .` again, then `uv run ty check`, then `uv run pytest -q`.

---

## File Structure

| file | responsibility | tasks |
| --- | --- | --- |
| `src/comment_review/flows/fill.py` | resolving a mark's address against its page, and seeding an absent place from it | 1, 2 |
| `src/comment_review/flows/collate.py` | refusing a mark whose address resolves against no page | 3 |
| `src/comment_review/flows/turn.py` | a recast keeping the instruction the roles filed | 4 |
| `src/comment_review/results/galley.py` | vacating a place without touching its leading | 5 |
| `src/comment_review/results/compositor.py` | deciding a vacated place's leading at set time | 6 |
| `scripts/smoke_fixture.py` | writing the fixture tree and the planted text files | 7 |
| `scripts/smoke_middle.ps1` | driving the chain, the whole instrument | 8, 9, 10 |

`scripts/smoke_fixture.py` exists because the fixture's comment text is multi-line and must not cross a shell. The PowerShell script calls it, then passes the files it wrote with `@path`.

---

### Task 1: `fill` refuses an address the page does not carry

**Files:**
- Modify: `src/comment_review/flows/fill.py`
- Test: `tests/test_fill.py`

**Interfaces:**
- Consumes: `flows.page_for.page_of(source, rel=..., source=...) -> tuple[Page | None, str]`
- Produces: `fill(copy, entry, root)` refusing an address whose cue names no place on its page, with a reason containing `names no place on that page`.

- [x] **Step 1: Write the failing test**

```python
def test_a_cue_the_page_does_not_have_is_refused(tmp_path):
    """The page carries every place, absent and present, so a cue it does
    not have names nothing. `decision-log.md Process: #111`."""
    tree = a_small_real_tree(tmp_path)
    copy = seed(binder_of(tree, 0), "block-context")
    got, why = fill(copy, {"address": "m.py@b9999", "instruction": "clean"}, tree)
    assert got is None
    assert any("names no place" in reason for reason in why)
```

- [x] **Step 2: Run it and watch it fail**

Run: `uv run pytest -q tests/test_fill.py -k cue_the_page_does_not_have`
Expected: fail. Today `fill` checks the path half only, so the mark is accepted and a seed is manufactured for it.

- [x] **Step 3: Resolve the address against its page**

In `fill()`, after `_sheet_for` finds the sheet and before the seed is built:

```python
    # `_sheet_for` already resolves the path half through `unflatten`; return
    # that path alongside the marks list so this does not resolve it twice.
    page, why_page = page_of(root / rel, rel=rel)
    if page is None:
        return None, [f"{address}: {why_page}"]
    if address.partition("@")[2] not in page.cues.places:
        return None, [f"{address} names no place on that page"]
```

- [x] **Step 4: Run it and watch it pass**

Run: `uv run pytest -q tests/test_fill.py -v`
Expected: pass, and all sixteen existing cases still pass. They use real addresses over a real tree, which is why they are unaffected.

- [x] **Step 5: Gates**

Run: `uv run ruff check . ; uv run ruff format . ; uv run ruff check . ; uv run ty check ; uv run pytest -q`

- [x] **Step 6: Commit, then tick in a later commit**

```bash
git add src/comment_review/flows/fill.py tests/test_fill.py
git commit -F <message file>
job-board --plans-dir docs/plans todo close-task mark-defects.md T14 --statement "fill resolves the cue against its page and refuses one it does not carry" --commit <sha>
git add TODO/ ; git commit -F <tick message file>
```

---

### Task 2: `fill` seeds an absent place from its page

**Files:**
- Modify: `src/comment_review/flows/fill.py`
- Test: `tests/test_fill.py`

**Interfaces:**
- Consumes: the `page` lookup Task 1 put in `fill()`.
- Produces: a mark at a place the copy has no slot for, carrying the page's own anchor and an empty `raw_text`, never the entry's anchor.

- [x] **Step 1: Write the failing test**

```python
def test_an_absent_place_is_seeded_from_the_page(tmp_path):
    """The base is the system's, never the party being checked. It is the
    rule `desk/collator.base_texts` states for base texts, one layer up."""
    tree = a_small_real_tree(tmp_path)
    copy = seed(binder_of(tree, 0), "block-context")
    entry = {
        "address": AN_EMPTY_PLACE,
        "instruction": "add",
        "anchor": "a line the role invented",
        "change": "# added\n",
        "reason": "r",
    }
    got, why = fill(copy, entry, tree)
    assert why == []
    placed = [m for s in got["sheets"] for m in s["marks"]][-1]
    assert placed["anchor"] != "a line the role invented"
    assert placed["raw_text"] == ""
```

- [x] **Step 2: Run it and watch it fail**

Run: `uv run pytest -q tests/test_fill.py -k seeded_from_the_page`
Expected: fail on the anchor assertion. Today the no-slot branch reads `Mark.seed(address, str(entry.get("anchor") or ""), "")`.

- [x] **Step 3: Take the anchor from the page**

```python
        seeded = Mark.seed(address, page.cues.anchor_of(address.partition("@")[2]), "")
```

- [x] **Step 4: Run it and watch it pass**

Run: `uv run pytest -q tests/test_fill.py -v`

- [x] **Step 5: Gates, then commit and tick `mark-defects` T15**

Same gate sequence and commit shape as Task 1.

---

### Task 3: the fold reports a mark whose address resolves against no page

**Files:**
- Modify: `src/comment_review/flows/collate.py`
- Test: `tests/test_collate.py`

**Interfaces:**
- Produces: a problem naming the role and the address, so the task agent can route it back. Reported, never raised.

- [x] **Step 1: Write the failing test**

```python
def test_a_mark_at_a_cue_no_page_holds_is_reported(tmp_path):
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
    copies["block-context"]["sheets"][0]["marks"].append(
        {"address": "m.py@b9999", "instruction": "clean", "reason": "r"}
    )
    got = collate("4c", copies, binder, root=REPO)
    assert any("b9999" in p.address for p in got.problems)
```

- [x] **Step 2: Run it and watch it fail**

Run: `uv run pytest -q tests/test_collate.py -k cue_no_page_holds`
Expected: fail. The fold rules on contents and an address nothing holds is not among what it checks today.

- [x] **Step 3: Report it, do not raise**

`desk/containers.py` states the split this obeys: a container rules on the envelope and the run errors out; `problems_in` rules on contents and reports so each routes back to the role that wrote it. An unresolvable address is contents.

- [x] **Step 4: Run it and watch it pass, then the file**

Run: `uv run pytest -q tests/test_collate.py`

- [x] **Step 5: Gates, then commit and tick `collator-defects` T40**

---

### Task 4: a recast keeps the instruction the roles filed

**Files:**
- Modify: `src/comment_review/flows/turn.py`
- Test: `tests/test_turn.py`

**Interfaces:**
- Produces: `rule_at_max_turns(..., Answer.RECAST, ...)` yielding a `Determined` whose mark carries the instruction the roles filed rather than `correct`.

- [x] **Step 1: Write the failing test**

```python
def test_a_recast_of_an_add_stays_an_add(self):
    """Measured 2026-09-07 on claude-settings: a recast of an `add` was
    written as a `correct`, which asserts a sentence is false at a place
    holding no sentence, so the compositor wrote nothing and exited 0."""
    binder, copies, got = _escalated_add()
    ruled = rule_at_max_turns(
        got, AN_EMPTY_PLACE, Answer.RECAST, "", "chief's", turn=0, prose="# mine\n"
    )
    assert ruled.mark.instruction is Instruction.ADD
```

`_escalated_add` is a new helper beside `_escalated`, building two roles' `add` marks at one empty place so the fold carries it forward.

- [x] **Step 2: Run it and watch it fail**

Run: `uv run pytest -q tests/test_turn.py -k recast_of_an_add`
Expected: fail, the instruction reading `correct`.

- [x] **Step 3: Carry the filed instruction through the recast**

`flows/turn.py:561` hardcodes `instruction=Instruction.CORRECT` inside the recast's synthesized
`Mark`, with `claim={"false": first.raw_text, "true": prose}`. Take the instruction from
`first` instead, and shape the claim to it -- an `add` at an empty place has no false clause to
quote, which is exactly why the empty `claim.false` wrote nothing. The claim each instruction
owes is in `desk/mark.py`'s `INSTRUCTIONS` table.

- [x] **Step 4: Run it and watch it pass, then both files**

Run: `uv run pytest -q tests/test_turn.py tests/test_disposition_command.py`

- [x] **Step 5: Gates, then commit and tick `the-chief-has-no-recast-workflow` T1**

Leave its note in place. It records that the `P14` wait was withdrawn rather than satisfied.

---

### Task 5: the galley stops vacating leading

**Files:**
- Modify: `src/comment_review/results/galley.py`
- Test: `tests/test_galley.py`

**Interfaces:**
- Produces: `reset()` emptying the paragraph alone. No leading is written by the galley.

- [x] **Step 1: Write the failing test**

```python
def test_a_drop_leaves_the_leading_alone(self):
    """`Addressing: #22` -- the compositor owns leading, adding and
    dropping, because a fence is a property of the page being laid out
    rather than of the edit being applied."""
    page = a_page(SAMPLE)
    before = dict(page.leading)
    galley.reset(page, {"m.py@b1": None})
    assert page.leading == before
```

- [x] **Step 2: Run it and watch it fail**

Run: `uv run pytest -q tests/test_galley.py -k leading_alone`
Expected: fail. `_vacate` empties the leading the dropped place owns.

- [x] **Step 3: Remove the leading half of `_vacate`**

Delete the branch that empties it. The paragraph is still vacated; the leading is left to the compositor.

- [x] **Step 4: Run the two files and expect red**

Run: `uv run pytest -q tests/test_galley.py tests/test_compositor.py`
Expected: the drop cases now fail on composed output, because nothing drops the leading yet. **Do not commit here.** Tasks 5 and 6 are one unit and land in one commit.

- [x] **Step 5: Go straight to Task 6**

---

### Task 6: the compositor drops a leading whose place is vacated

**Files:**
- Modify: `src/comment_review/results/compositor.py`
- Test: `tests/test_compositor.py`

**Interfaces:**
- Consumes: Task 5's galley, which now leaves `page.leading` untouched.
- Produces: `set_page` omitting the leading of a place whose kind held prose and whose `raw_lines` are now empty.

- [x] **Step 1: Write the failing test**

```python
def test_a_vacated_place_loses_its_leading(self):
    page = a_page(SAMPLE)
    galley.reset(page, {"m.py@b1": None})
    assert "\n\n\n" not in set_page(page)
```

- [x] **Step 2: Run it and watch it fail**

Run: `uv run pytest -q tests/test_compositor.py -k vacated_place_loses`
Expected: fail, the blank standing over whatever follows.

- [x] **Step 3: Mirror the absence rule already there**

`set_page` computes `absent` -- the places whose kind says absence -- for the add rule. The drop is its mirror: a place whose kind held prose and whose `raw_lines` are now empty owes no leading. Key it on the paragraph's state, not on whether a leading was looked up. `Addressing: #19` records that the edge alone fired on modifies and on unedited composes.

- [x] **Step 4: Run the round trip, which is the real gate**

Run: `uv run pytest -q tests/test_compositor.py tests/test_galley.py tests/test_proof_setter.py`
Expected: pass, and **an unedited page still sets back byte-identical.** That is the hazard `Addressing: #19` paid for once already, arriving from the other side.

- [x] **Step 5: Gates, then commit Tasks 5 and 6 together, then tick**

Tick `galley-and-compositor-write-path` T19 and T20 against the one sha.

---

### Task 7: the fixture writer

**Files:**
- Create: `scripts/smoke_fixture.py`
- Test: `tests/gates/test_smoke_fixture.py`

**Interfaces:**
- Produces: `write_fixture(root: Path) -> Path`, the written file's path; and `write_texts(run_dir: Path) -> dict[str, Path]`, the planted comment text files keyed by scenario name.

- [x] **Step 1: Write the failing test**

```python
def test_the_fixture_yields_every_series(tmp_path):
    """A series of one never exercises its ordinals, which is what the
    first two drafts of this fixture got wrong."""
    path = write_fixture(tmp_path)
    page = a_page_over(path)
    assert {"a", "b", "c", "d", "f"} <= {cue[0] for cue in page.cues.places}
    trailing = [p for p in page.paragraphs if p.kind == "trailing-comment" and p.text]
    assert len(trailing) == 3
```

- [x] **Step 2: Run it and watch it fail**

Run: `uv run pytest -q tests/gates/test_smoke_fixture.py`
Expected: fail, the module not existing.

- [x] **Step 3: Write the module**

`write_fixture` writes the file the spec names, verbatim: the recursive Fibonacci with the logging decorator, three trailing comments, three standalone comment runs, two stacked decorators, a nested `def`, and a dunder-main block. `write_texts` writes one file per planted change so no multi-line text crosses a shell.

- [x] **Step 4: Run it and watch it pass**

Run: `uv run pytest -q tests/gates/test_smoke_fixture.py -v`

- [x] **Step 5: Gates, then commit**

---

### Task 8: the script drives gather through distribute

**Files:**
- Create: `scripts/smoke_middle.ps1`

**Interfaces:**
- Produces: a run directory holding `binder.json`, `topology.toml`, and four seeded copies.

- [x] **Step 1: Write the command table and the first stages**

One hashtable at the top, so a renamed command touches one row:

```powershell
$Cmd = @{
    gather = 'gather'; topology = 'topology'; distribute = 'distribute'
    mark = 'mark'; check = 'check'; collate = 'collate'
    disposition = 'disposition'; proof = 'proof'; addresser = 'addresser'
}
```

- [x] **Step 2: Give every invocation an exit check**

Each stage is followed by a check that stops the script, naming the stage and printing the command it ran, so a failure carries its own reproduction.

- [x] **Step 3: Run it as far as distribute**

Run: `pwsh scripts/smoke_middle.ps1 -Stop distribute`
Expected: exit 0, four seeded copies in the run directory.

- [x] **Step 4: Commit**

---

### Task 8a: the script's review findings, before Task 9 builds on it

Added 2026-09-11 on Roy's instruction to do all of `smoke-middle-script` T1-T11 in the order the
plan needs. Task 9 extends the helper and the stage list, so the fixes to both land first. T7 is
not here: it is the header and a note going false as stages are added, so Tasks 9 and 10 each
rewrite them as they add stages.

**Files:**
- Modify: `scripts/smoke_middle.ps1`

Each step is one finding, one commit, and the Task 8 done gate re-run after it:
`pwsh -NoProfile -File scripts/smoke_middle.ps1 -Stop distribute`, exit 0, four copies.

- [x] **Step 1: T4 -- the helper takes the exit code a stage expects, 0 by default**
- [x] **Step 2: T5 -- a one-element command line runs under strict mode**
- [x] **Step 3: T3 -- a missing executable is reported by the helper, naming the stage**
- [x] **Step 4: T2 -- a failed stage prints a command that runs when pasted, and where it runs**
- [x] **Step 5: T9 -- command output goes to the console; the script's own output is the run path**
- [x] **Step 6: T6 -- one ordered table of stages, so a name and its block cannot fall out of step**
- [x] **Step 7: T8 -- the launcher prefix is written once**
- [x] **Step 8: T1 -- a relative `-Run` resolves against the caller, and one inside the repo is refused**
- [x] **Step 9: T10 -- two runs in the same second get different default directories**
- [x] **Step 10: T11 -- an empty `-Stop` is refused**
- [x] **Step 11: Tick** `smoke-middle-script` T1-T6 and T8-T11 against their commits, in a later commit

---

### Task 9: the script plants the marks and folds them

**Files:**
- Modify: `scripts/smoke_middle.ps1`

**Interfaces:**
- Consumes: Task 8's copies and Task 7's text files.
- Produces: `proof0.json` and the chief's copy.

- [x] **Step 1: Plant the matrix**

One `mark` invocation per ruling per role, covering every row of the spec's matrix: a lone mark, two roles differing, three roles differing, a drop, an add at an empty place, a move, and a query no role can settle. Multi-line text goes as `@path`.

- [x] **Step 2: Run `check` over each of the four copies**

Expected: exit 0 for all four. A refusal here is the second bar failing and stops the script.

- [x] **Step 3: Run `collate`, then `disposition`**

The dispositions file carries a `taken_in` on a role's side, a `taken_in` on `original`, and a `recast` with the chief's own prose.

- [x] **Step 4: Run it as far as the disposition**

Run: `pwsh scripts/smoke_middle.ps1 -Stop disposition`

- [x] **Step 5: Commit**

---

### Task 9a: the plant's landing texts in one place, before Task 10 diffs against them

Added 2026-09-11 on Roy's "Go" to doing `smoke-middle-script` T20 and T32 before Task 10. The
proof refuses Task 9's plant because the `a2` docstring carries no indentation (T20; Addressing
#27 gives indentation to the role), and Task 10's expected diff needs every text that lands in
one place (T32). Moving those texts into files makes `mark` read them as `@path`, which is T30,
and drops the unread `recast_prose.txt`, which is T21. The comments and docstring on the code
this rewrites are T27 and T28.

**Files:**
- Modify: `scripts/smoke_fixture.py`, `scripts/smoke_middle.ps1`

- [ ] **Step 1: One table of the texts that land, written before the marks, read by `mark` as `@path`, `a2` indented**
- [ ] **Step 2: The comments and docstring on that code say what is true of it**
- [ ] **Step 3: Done gate** -- `-Stop disposition` exits 0, and `proof --copy chief-final.json` run by hand on that run exits 0
- [ ] **Step 4: Tick** `smoke-middle-script` T20, T21, T27, T28, T30 and T32 against their commits, in a later commit
- [ ] **Step 5: `add` at several places, filled and absent, across the series** -- Roy, 2026-09-11: *"Test several spots both filled and absent"*. What the proof then refuses is reported, not routed around

---

### Task 10: the proof, and the diff that is the assertion

**Files:**
- Modify: `scripts/smoke_middle.ps1`

- [ ] **Step 1: Run `proof`, then diff the two trees**

```powershell
git --no-pager diff --no-index -- $Original $Proof
```

- [ ] **Step 2: Assert the diff against what was planted**

The script wrote its expected diff at plant time. A difference between expected and actual is the failure, and it prints both.

- [ ] **Step 3: Add the addresser scenario**

Look up the empty place by file and line, take the address that comes back, use it for the `add`, and confirm that comment is in the diff. This is the positive form of the defect that lost a finding on 2026-09-07.

- [ ] **Step 4: Run the whole script from empty**

Run: `pwsh scripts/smoke_middle.ps1`
Expected: exit 0, and the diff matching what was planted.

- [ ] **Step 5: Gates, commit, and report**

Say plainly which of the spec's four bars the run demonstrated and which it did not.

---

## What this plan does not do

Each of these is on the board, and none blocks the script.

- **The brief's leading instruction**, `agents-files-name-the-new-cli` T20. The script is not an agent and plants its own text, so the brief does not reach it. Needed before the live run.
- **The galley pull copying tracked files only**, `galley-and-compositor-write-path` T13 and T14. The fixture is one file, so a wholesale copy costs nothing here. It blocks a live run on a real repository.
- **`galley.py`'s docstring**, T21. The sentence is false and no gate turns on it.
- **The whole-schedule pre-verify**, `containers-and-verification-are-unwired` T47. The per-page check already refuses; this is a reporting improvement.

## After it passes

The instructions are reseeded against the command surface the script proves, and the four roles are dispatched live on a real repository. That run is the baseline, and this script is what makes its failures attributable to the agents rather than to the chain.
