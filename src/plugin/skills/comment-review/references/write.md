# Stage 7b -- write

The author has read each page and freeform draft beside the manuscript and accepted all of it, some places, or
none. This stage proves the code in every accepted draft is unchanged, runs the repo's own
check on the drafts, and writes them into the working tree.

## Choose the drafts

- **All of it.** Use the drafts stage 7a wrote, one per page.
- **Some places.** Set those places alone into a fresh directory, naming each by the stage that
  decided it; its drafts are the ones this prints:

  ```bash
  python <skill>/scripts/comment-review.py proof --jacket <run-dir>/jacket.json --repo . \
    --only <stage>:<address> --only <stage>:<address> --out <run-dir>/accepted
  ```

  A later stage read the pages the earlier ones left. Where the author declined an earlier
  stage's place on a page a later stage changed, `proof` refuses, naming that place: show the
  author both and ask whether to accept the earlier change too, or decline the later stage's
  places on that page.

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

Prove the code in every draft reads the same as the file in the working tree, naming each
`<path>` in the working tree, the `--out` that holds the drafts, and the imprimatur `proof` wrote
there:

```bash
python <skill>/scripts/comment-review.py prove_unchanged --drafts <drafts> \
  --imprimatur <drafts>/imprimatur.json \
  --repo . <path> ...
```

It prints `PROVEN` for each page whose code is unchanged. When it refuses a page, write nothing:
bring the author what it printed. For a freeform file it prints `UNCHECKED  <path>: no reader --
formatter and compiler are the check`. That is the expected answer, and the report states it as
unchecked, never as proven.

## Step 2 -- validate locally

After `prove_unchanged` succeeds, check the drafts in a temporary worktree holding the working
tree as it is now, and on every exit from this stage, written or refused, remove it with
`git worktree remove --force <run-dir>/build`:

1. Record the commit `git stash create` prints, or `HEAD` when it prints nothing, and run
   `git worktree add <run-dir>/build <that commit>`.
2. Run the check command stage 1 recorded in `<run-dir>/build`, the project's doctests where it
   has them, and any compilation or syntax check the project's local tools support, and keep
   the results as the baseline.
3. Copy each draft over its `<path>` in `<run-dir>/build` and run the same checks again.

The drafts pass when they pass everything the baseline passed. Where they fail something the
baseline passed, write nothing: bring the author the output and the pages it names.

## Step 3 -- write

For each draft, keep the output of `git diff --no-index <path> <draft>` for the report, then
copy the draft over its `<path>` in the working tree.

## Report

- the pages and freeform files written, and the places accepted and left
- what `prove_unchanged` printed
- separately, the check command and the doctests, their baseline, and their result with the drafts
- each freeform language not verified
- the diffs step 3 kept, which show exactly what the run changed and nothing the author
  changed before it

Stage 8 follows, on the pages and freeform files written.
