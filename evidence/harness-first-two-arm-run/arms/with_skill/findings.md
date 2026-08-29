# block-context -- findings

Role: BLOCK-CONTEXT. File under review:
`plugins/comment-review/skills/comment-review/scripts/galley.py` (paths below are
relative to that repo root, as the census prints them).

Eleven census entries hold prose; every one carries a record below.

| index | address | lines | kind | verdict |
| --- | --- | --- | --- | --- |
| 107 | `@a0` | 1-33 | docstring | `query` |
| 113 | `@c5` | 42 | trailing-comment | `clean` |
| 115 | `@a1` | 46-51 | docstring | `clean` |
| 118 | `@a2` | 56-70 | docstring | `clean` |
| 127 | `@a3` | 81-85 | docstring | `correct` |
| 134 | `@a4` | 94-99 | docstring | `correct` |
| 145 | `@a5` | 112 | docstring | `correct` |
| 146 | `@b33` | 113 | comment | `clean` |
| 172 | `@b58` | 142-145 | comment | `clean` |
| 201 | `@b86` | 176-177 | comment | `clean` |
| 220 | `@b104` | 198-199 | comment | `clean` |

---

## WHERE THE CENSUS AND THE BRIEF DISAGREE

Stated rather than guessed past, per the run instruction. None of these changed a
verdict; all of them changed how a field had to be written.

1. **`block` vs `paragraph`.** The brief and my role file rule on a *block*; this
   census counts *paragraphs* ("223 paragraphs censused") and gives each one a cue
   address (`@a0`, `@b33`, `@c5`) in addition to the running index. `BLOCK`'s
   documented shape -- `index | path:start-end` -- has nowhere to carry the cue, so
   the cue is in the table above and not in the records.

2. **`BLOCK` cannot be checked against this census.** The brief says all three parts
   of `BLOCK` are "CHECKED against the census", and that the block's transcribed text
   is what a later reader recovers. This census prints only the ANCHOR line in
   parentheses (e.g. `(def main() -> int:)`), never the paragraph's own text. The
   transcriptions below therefore come from the file, and nothing in the census can
   verify them.

3. **`interval` vs the doubled listing.** Indices 1-104 are the empty intervals
   (`@b0`-`@b107`, all `0-0`), and the four `@b` numbers that hold prose -- `b33`,
   `b58`, `b86`, `b104` -- are omitted there and listed later with real ranges. That is
   consistent, but the brief's "an `interval` block holds nothing" reads as though
   intervals are interleaved rather than listed first as a separate run.

4. **Two census annotations misfire on this file**, and I am not ruling on them:
   - `-> a review label: round 2` on `@a0`. My role file's review-round label is
     *"fix round 2"*, *"finding B4"* -- a dated artefact of a past review. Here
     `round 2` is the NAME of one of the two use cases the docstring lists ("Two
     things need it"), i.e. a live re-review of the pipeline. Not a state finding.
   - `-> UNRESOLVED path census.json` / `edits.json` on `@a0`. Both are placeholders
     in the usage line, not citations of tracked files.

5. **The brief's own field order is stated twice, differently.** Its field table runs
   `BLOCK, VERDICT, SOURCES, CLAIM, REASON, CHANGE`; its worked example and its
   "chain of custody" sentence both run `BLOCK, VERDICT, CLAIM, REASON, SOURCES,
   CHANGE`. I followed the example and the chain.

6. **No JSON record shape is specified.** The role file and the brief define one
   format -- the `--- RECORD` text block -- so no `record.json` was written.

---

--- RECORD
BLOCK       145 | plugins/comment-review/skills/comment-review/scripts/galley.py:112-112
            """Write a galley of every file an edit touches, and report what refused."""
VERDICT     correct
CLAIM       false: "Write a galley of every file an edit touches" / true: "Write a galley of every file whose edits all pass"
REASON      Three paths skip a file AFTER its edits have been grouped under that
            file's path -- an unreadable source, an overlapping pair of ranges, and a
            stale range -- and each `continue`s before `target.write_text`, so a file
            an edit touches gets no galley at all whenever any one of its edits
            refuses. The population is not "every file an edit touches" but "every
            file whose edits all pass"; the module docstring of this same file states
            the exception the summary line denies.
SOURCES     plugins/comment-review/skills/comment-review/scripts/galley.py:170 |             print(f"REFUSED  {rel}: {type(e).__name__}")
            plugins/comment-review/skills/comment-review/scripts/galley.py:183 |             print(f"REFUSED  {rel}: edits at {clash[0]} and {clash[1]} share a line")
            plugins/comment-review/skills/comment-review/scripts/galley.py:187 |             print(f"REFUSED  {rel}: {len(stale)} range(s) no longer match the census")
            plugins/comment-review/skills/comment-review/scripts/galley.py:193 |         target.write_text(splice(text, ranges), encoding="utf-8", newline="")
            plugins/comment-review/skills/comment-review/scripts/galley.py:31 | no longer matches the file, or two edits over one line, stops that file rather
CHANGE          """Write a galley of every file whose edits all pass, and report what refused."""
---

--- RECORD
BLOCK       134 | plugins/comment-review/skills/comment-review/scripts/galley.py:94-99
                """Does the file still read the way the census recorded this block?

                ! The census may be older than the file. Splicing a range whose content has
                moved writes the replacement over whatever is there now, which is the one
                failure a galley must not produce quietly.
                """
VERDICT     correct
CLAIM       false: "which is the one failure a galley must not produce quietly" / true: "which is one of the two failures this file refuses over rather than splicing"
REASON      An exclusivity claim, and it is refuted inside its own file. Two
            conditions stop a file before anything is written -- a stale range, and
            two edits over one line -- and both are refused loudly with their own
            `REFUSED` line. The module docstring names them as a pair; `overlaps`
            exists for the second and says the same thing about it ("no defined
            result"). Enumerated over the failures this file guards against, the
            count is two, not one.
SOURCES     plugins/comment-review/skills/comment-review/scripts/galley.py:31 | no longer matches the file, or two edits over one line, stops that file rather
            plugins/comment-review/skills/comment-review/scripts/galley.py:81 |     """The first pair of edits sharing a line, or None.
            plugins/comment-review/skills/comment-review/scripts/galley.py:183 |             print(f"REFUSED  {rel}: edits at {clash[0]} and {clash[1]} share a line")
            plugins/comment-review/skills/comment-review/scripts/galley.py:187 |             print(f"REFUSED  {rel}: {len(stale)} range(s) no longer match the census")
CHANGE          """Does the file still read the way the census recorded this block?

                ! The census may be older than the file. Splicing a range whose content has
                moved writes the replacement over whatever is there now, which is one of
                the two failures this file refuses over rather than splicing.
                """
---

--- RECORD
BLOCK       127 | plugins/comment-review/skills/comment-review/scripts/galley.py:81-85
                """The first pair of edits sharing a line, or None.

                ! Two `CHANGE`s over one line have no defined result: each carries its
                surrounding block, so the second would overwrite context the first wrote.
                """
VERDICT     correct
CLAIM       false: "The first pair of edits sharing a line, or None." / true: "The start lines of the first two edits sharing a line, or None."
REASON      An edit in this module is `tuple[int, int, str]`, and the function's own
            annotation returns `tuple[int, int]` -- it hands back `(a_start, b_start)`,
            two 1-based line numbers, not the two edits. The single caller reads them
            as positions and prints them as such. A reader honouring the summary line
            would unpack the return as edits and get two integers.
SOURCES     plugins/comment-review/skills/comment-review/scripts/galley.py:80 | def overlaps(edits: list[tuple[int, int, str]]) -> tuple[int, int] | None:
            plugins/comment-review/skills/comment-review/scripts/galley.py:89 |             return (a_start, b_start)
            plugins/comment-review/skills/comment-review/scripts/galley.py:183 |             print(f"REFUSED  {rel}: edits at {clash[0]} and {clash[1]} share a line")
CHANGE          """The start lines of the first two edits sharing a line, or None.

                ! Two `CHANGE`s over one line have no defined result: each carries its
                surrounding block, so the second would overwrite context the first wrote.
                """
---

--- RECORD
BLOCK       107 | plugins/comment-review/skills/comment-review/scripts/galley.py:1-33
            """The proposed text, SET AS FILES, so it can be read and censused like any tree.

                python galley.py --repo D --census census.json --edits edits.json --out DIR

            A galley is the trial impression: the text set, but not yet made into pages, so
            that it can be corrected before anything is committed. That is exactly what
            this writes -- every block a stage proposes to change, spliced into a copy of
            its file under `--out`. Nothing under `--repo` is touched.

            !! IT RENDERS; IT DOES NOT RULE. A stage that both produced the galley and
            judged it would be MARK and APPLY in one actor, which is the separation the
            pipeline exists to keep.

            Two things need it, and they needed the same thing:

              round 2   A re-review rules on the SYNTHESISED block -- text on no disk and
                        in no census -- so `address_problem` refuses it and `edit_problem`
                        measures one claim against one edit where the block now holds
                        several. Censusing the galley gives that text a real address and a
                        real transcription, so every check in `verdicts.py` works on it
                        UNCHANGED. The alternatives were a second record shape to hold in
                        sync, or a flag that turns the checks off for the one text the
                        author actually approves.
              stage 7a  What lands at 7b is a block spliced into a file, and the splice is
                        the first time anyone sees the two together. `git diff --no-index`
                        over the galley shows the author what will land, including whether
                        an adjacent block was clipped -- which a `CHANGE` cannot show,
                        because each one carries its own surrounding context.

            ! A SPLICE THAT CANNOT BE MADE IS REPORTED, NEVER GUESSED. A census range that
            no longer matches the file, or two edits over one line, stops that file rather
            than writing a galley nobody can trust.
            """
VERDICT     query
CLAIM       outside the checkout. The claim is that `address_problem` refuses a
            synthesised block, that `edit_problem` measures one claim against one
            edit, and that "every check in `verdicts.py` works on it UNCHANGED" --
            three names this file neither defines nor imports. ATTEMPTED: read the
            whole of galley.py for the three names (it imports only `argparse`,
            `json`, `sys`, `Path` and `READ_ERRORS`), then read the census's own
            mechanical resolutions, which report `address_problem`, `edit_problem`
            and `verdicts.py` UNRESOLVED as symbols and `verdicts.py` UNRESOLVED as a
            path. WOULD settle it: a name corpus built from a full git checkout rather
            than a walked tree -- the census's NOT CHECKED block says its corpus was
            walked and that "a file missing from the name corpus turns every symbol
            defined only there into a false obituary" -- or `verdicts.py` itself in
            this run's file list, read to confirm both function names and that its
            checks still run on a censused galley.
REASON      This run was handed one file, so absence from what I can open is not
            evidence of absence from the tree; and the census's own caveat says its
            UNRESOLVED notes are the weaker direction of exactly this question. So
            the citation can be neither confirmed nor refuted here. It is not `clean`,
            because a docstring licensing a design decision on three names that
            nothing in reach resolves is precisely the citation that rots unnoticed;
            it is not `correct`, because I have not established the names are gone.
SOURCES     plugins/comment-review/skills/comment-review/scripts/galley.py:18 |                       in no census -- so `address_problem` refuses it and `edit_problem`
            plugins/comment-review/skills/comment-review/scripts/galley.py:20 |                       real transcription, so every check in `verdicts.py` works on it
            plugins/comment-review/skills/comment-review/scripts/galley.py:42 | from repo import READ_ERRORS  # noqa: E402  -- path shim must run first
            census.txt:117 |         -> UNRESOLVED symbol `address_problem` (CANDIDATE)
            census.txt:123 |         -> UNRESOLVED path verdicts.py
            census.txt:249 |     !! A file missing from the name corpus turns every symbol defined
---

--- RECORD
BLOCK       113
VERDICT     clean
CLAIM       block-context
REASON      `sys.path.insert` is the line above the import it excuses, so "path shim
            must run first" is true of the code it sits with.
---

--- RECORD
BLOCK       115
VERDICT     clean
CLAIM       block-context
REASON      The return is derived from `text`, never from `os` or `sys`, so "taken
            from the file being spliced, not from the platform" holds; the joiner it
            returns is the one `splice` uses.
---

--- RECORD
BLOCK       118
VERDICT     clean
CLAIM       block-context
REASON      Each claim resolves: the slice is `lines[start - 1 : end]`, so 1-based and
            inclusive; `sorted(edits, reverse=True)` is descending, so order of arrival
            does not matter; and the single caller checks `overlaps` and `continue`s
            before ever reaching `splice`, so "the caller has already refused overlaps"
            is true.
---

--- RECORD
BLOCK       146
VERDICT     clean
CLAIM       block-context
REASON      The comment states why the guard below it exists, and the guard does what
            it says: `sys.stdout.reconfigure` is fetched defensively and, when callable,
            set to utf-8 with `errors="replace"`.
---

--- RECORD
BLOCK       172
VERDICT     clean
CLAIM       block-context
REASON      All three claims hold. The block dict is carried in the fourth slot of each
            tuple; `raw_lines` is the only stored copy of the file as the reviewers read
            it, read by `block_matches` and by nothing else here; and the staleness check
            is below this comment and compares the file against that stored copy rather
            than against itself.
---

--- RECORD
BLOCK       201
VERDICT     clean
CLAIM       block-context
REASON      The comprehension runs `block_matches` over every entry in `file_edits`, and
            both refusals `continue` before `target.write_text`, so "every block is
            checked ... BEFORE anything is written" is true and no half-splice is
            reachable.
---

--- RECORD
BLOCK       220
VERDICT     clean
CLAIM       block-context
REASON      `return 1 if refused else 0` is nonzero exactly when `refused` is nonzero,
            which is the claim; the two `return 2` paths above it are also nonzero and do
            not contradict it.
---

## CODE CONCERNS

- `line_endings` returns `"\r\n"` whenever the file contains one CRLF, so `splice`
  rejoins a mixed-ending file entirely in that ending -- the whole-file rewrite the
  same docstring's rationale gives as the reason not to normalise.
- `stale` is computed before `clash` but reported after it, so a file that is both
  stale and overlapping is only ever reported as overlapping.
