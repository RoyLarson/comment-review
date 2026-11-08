# Stage 7b -- write

The author has read each page and freeform draft beside its original and accepted all of it, some places, or
none. This stage proves the code in every accepted draft is unchanged, runs the repo's own
check on the drafts, and writes them into the working tree.

## Choose the drafts

- **All of it.** Use the drafts retained at stage 7a, taking the latest draft of
  each page when more than one stage changed it.
- **Some places.** Set those places alone into a fresh directory; its drafts are the ones this
  prints:

  ```bash
  python <skill>/scripts/comment-review.py proof --repo <stage-root> --proof <closed-proof> \
    --only <address> --only <address> --out <run-dir>/accepted
  ```

  Use the closed proof and source root for the stage that produced the proposed
  text. When several stages changed a selected page, compare the new draft with
  the original and confirm every difference is among the author's accepted
  changes before writing it.

  A move is approved as a whole: name both of its ends, or neither. `proof`
  refuses one end named alone. When the author accepts one end, show them both
  and ask.

  The same sentence marked in two files is one finding. When the author accepted it in one
  file and left the other, ask which they want in both.
- **Freeform files.** An accepted file's draft is `<run-dir>/freeform/draft/<path>`, as the author
  left it. The author's edits come after the audit, and step 1 checks them.
- **A `drop` and an `add` that name each other** are approved as a whole. When a selection holds
  one half, show the author both and ask.
- **None.** The run ends here, with the tree as it was.

## Step 1 -- prove unchanged

Set the accepted drafts over the pre-edit tree in a temporary worktree:

1. `git worktree add <run-dir>/build <pre-edit ref>`
2. Run the check command stage 1 recorded in `<run-dir>/build`, and keep its result as the
   baseline.
3. Copy each draft over its `<path>` in `<run-dir>/build`.

Then, from `<run-dir>/build`, prove the code in every draft reads the same as at the pre-edit
ref:

```bash
python <skill>/scripts/comment-review.py prove_unchanged --base <pre-edit ref> --repo . <paths>
```

It prints `PROVEN` for each page whose code is unchanged. When it refuses a page, write nothing:
bring the author what it printed. For a freeform file it prints `UNCHECKED  <path>: no reader --
formatter and compiler are the check`. That is the expected answer, and the report states it as
unchecked, never as proven.

## Step 2 -- validate locally

After `prove_unchanged` succeeds, check whether the project's local tools support compilation or
syntax validation. If available, run the applicable check on the edited result and report the
outcome.

Run it in `<run-dir>/build`. The drafts pass when it passes everything the baseline passed. Where
it fails something the baseline passed, write nothing: bring the author the check's output and
the pages it names. Then `git worktree remove --force <run-dir>/build`.

## Step 3 -- write

Copy each draft over its `<path>` in the working tree.

## Report

- the pages and freeform files written, and the places accepted and left
- what `prove_unchanged` printed
- separately, the check command, its baseline, and its result with the drafts
- each freeform language not verified
- `git diff`, which the author reads to see exactly what the run changed

Stage 8 follows, on the pages and freeform files written.
