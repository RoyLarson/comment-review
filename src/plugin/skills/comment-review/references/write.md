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

Set the accepted drafts over the pre-edit tree in a temporary worktree, and on every exit from
this stage, written or refused, remove it with `git worktree remove --force <run-dir>/build`:

1. `git worktree add <run-dir>/build <pre-edit ref>`
2. Run the check command stage 1 recorded in `<run-dir>/build`, and the project's doctests
   where it has them, and keep the results as the baseline.
3. Copy each draft over its `<path>` in `<run-dir>/build`.

Then prove the code in every draft reads the same as at the pre-edit ref, naming each path
under the build root:

```bash
python <skill>/scripts/comment-review.py prove_unchanged --base <pre-edit ref> \
  --repo <run-dir>/build <run-dir>/build/<path> ...
```

It prints `PROVEN` for each page whose code is unchanged. When it refuses a page, write nothing:
bring the author what it printed. For a freeform file it prints `UNCHECKED  <path>: no reader --
formatter and compiler are the check`. That is the expected answer, and the report states it as
unchecked, never as proven.

## Step 2 -- validate locally

After `prove_unchanged` succeeds, check whether the project's local tools support compilation or
syntax validation. If available, run the applicable check on the edited result and report the
outcome.

Run that check, the check command and the doctests in `<run-dir>/build`. The drafts pass when
they pass everything the baseline passed. Where they fail something the baseline passed, write
nothing: bring the author the output and the pages it names.

## Step 3 -- write

Copy each draft over its `<path>` in the working tree.

## Report

- the pages and freeform files written, and the places accepted and left
- what `prove_unchanged` printed
- separately, the check command and the doctests, their baseline, and their result with the drafts
- each freeform language not verified
- `git diff <pre-edit ref> -- <paths written>`, which the author reads to see exactly what the
  run changed

Stage 8 follows, on the pages and freeform files written.
