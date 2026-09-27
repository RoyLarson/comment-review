# Stage 7b -- write

The author has read each page beside its original and accepted all of it, some places, or
none. This stage proves the accepted text still compiles, writes it into the working tree,
and proves the code in every page it wrote is unchanged.

## Choose the drafts

- **All of it.** The drafts are the ones stage 7a's `proof` printed.
- **Some places.** Set those places alone into a fresh directory; its drafts are the ones this
  prints:

  ```bash
  python <skill>/scripts/comment-review.py proof --repo . --proof <run-dir>/final.json \
    --only <address> --only <address> --out <run-dir>/accepted
  ```

  The same sentence marked in two files is one finding. When the author accepted it in one
  file and left the other, ask which they want in both.
- **None.** The run ends here, with the tree as it was.

## Step 1 -- compile

Build the accepted pages in a temporary worktree, with the check command stage 1 recorded:

1. `git worktree add <run-dir>/build <pre-edit ref>`
2. Run the check command in `<run-dir>/build`, and keep its result as the baseline.
3. Copy each draft over its `<path>` in `<run-dir>/build`.
4. Run the check command again.
5. `git worktree remove --force <run-dir>/build`

The drafts compile when the second run passes everything the baseline passed. Where the
second run fails something the baseline passed, write nothing: bring the author the check's
output and the pages it names.

## Step 2 -- write and prove unchanged

Copy each draft over its `<path>` in the working tree, then prove the code in every page you
wrote reads the same as at the pre-edit ref:

```bash
python <skill>/scripts/comment-review.py prove_unchanged --base <pre-edit ref> --repo . <paths written>
```

It prints `PROVEN` for each page whose code is unchanged. Report any page it refuses to the
author, with what it printed.

## Report

- the pages written, and the places accepted and left
- the check command, its baseline, and its result with the drafts
- what `prove_unchanged` printed
- `git diff`, which the author reads to see exactly what the run changed

Stage 8 follows, on the pages written.
