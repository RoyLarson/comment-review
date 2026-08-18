# comment-review run context

Fill every section; `--check` refuses a blank. Every section is handed to every reviewer EXCEPT the ones marked TASK AGENT ONLY.

## REPO ROOT
C:\Users\Roy\projects\comment-review

## DOC CONVENTION

MEASURED from the ten scripts under `plugins/comment-review/skills/comment-review/scripts/`
on 2026-08-17. Three templates, and the repo is consistent about all three.

MODULE DOCSTRING -- a one-line subject, then paragraphs of prose. The first line NAMES WHAT
THE MODULE IS, not what it contains, and is written as a noun phrase or a `Stage N:` label:

```
"""<one line: the module's ONE subject>.

<paragraphs. A `!` or `!!` prefix on a paragraph marks it load-bearing.>
"""
```

FUNCTION DOCSTRING -- Google sections, `Args:` then `Returns:`, four-space indent, each
parameter on its own line as `name: lowercase sentence.` A `Raises:` section is not used
anywhere in the tree. Prose paragraphs come AFTER the sections, not before:

```
    """<one line: what the return value IS, in backticks where it names a parameter>.

    Args:
        <name>: <lowercase, ends with a full stop>.

    Returns:
        <Capitalised sentence.>

    <optional prose, `!` or `!!` prefixed when load-bearing.>
    """
```

COMMENT FORMAT -- `#` runs on their own line above what they describe, sentence case, full
stops. `!` and `!!` open a run that is load-bearing; `?` is not used. A trailing comment is
short and lower case.

```
# <sentence.>
# !! <sentence a reader must not skip.>
```

## STYLE SHEET
new -- started this run

## LSP LANGUAGES
python -- ANSWERED. `documentSymbol` on the file under review returned 6 functions and their
locals. No other language is in scope this run.

## MOVE DESTINATION
`docs/` -- available for the repo's own development tooling (`scripts/`, `evals/`, `tests/`).

`plugins/comment-review/skills/comment-review/references/` -- available for the SHIPPED tree,
which is where the file under review lives. ! It is the destination for a rule, and
`docs/limitations.md` governs what may be written there: a rule belongs in exactly one file,
and at budget a new rule replaces an existing one rather than accumulating.

! NOT AVAILABLE: prose that is a project decision rather than a rule has no destination
outside `TODO/`, which is a work list and not a documentation tree. Report such a block rather
than moving it.

## CENSUS
C:\Users\Roy\.claude\jobs\98e6ff62\tmp\cycle\census.txt

## REVIEWER FILES
<!-- ! TASK AGENT ONLY -- do not paste this section -->
brief: C:\Users\Roy\projects\comment-review\plugins\comment-review\skills\comment-review\references\reviewer-brief.md
ownership-context: C:\Users\Roy\projects\comment-review\plugins\comment-review\agents\comment-review-ownership-context.md
block-context: C:\Users\Roy\projects\comment-review\plugins\comment-review\agents\comment-review-block-context.md
function-context: C:\Users\Roy\projects\comment-review\plugins\comment-review\agents\comment-review-function-context.md
module-context: C:\Users\Roy\projects\comment-review\plugins\comment-review\agents\comment-review-module-context.md
compact: C:\Users\Roy\projects\comment-review\plugins\comment-review\agents\comment-review-compact.md
review: C:\Users\Roy\projects\comment-review\plugins\comment-review\agents\comment-review-review.md

## FILES UNDER REVIEW
plugins/comment-review/skills/comment-review/scripts/galley.py

## REFERENCE ONLY
plugins/comment-review/skills/comment-review/scripts/record.py
plugins/comment-review/skills/comment-review/scripts/census.py
plugins/comment-review/skills/comment-review/scripts/repo.py
plugins/comment-review/skills/comment-review/scripts/prove_unchanged.py
plugins/comment-review/skills/comment-review/references/re-review.md
plugins/comment-review/skills/comment-review/references/write.md
tests/test_galley.py
TODO/the-record-is-a-parsed-template-and-should-be-a-value.md
docs/limitations.md
