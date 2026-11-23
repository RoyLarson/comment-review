"""The answer set back into a file, and the line-ending measure its proof uses.

    galley           updates a page with what the marks decided
    compositor       sets that page as text, top to bottom. Decides nothing
    prove_unchanged  the line-ending measure a proof checks against a sibling

Whether the executable code survived is `reading.proof`'s question, asked by
`flows.prove_unchanged`.

!! The galley edits and the compositor sets, and they are two roles. The galley
updates the old page with the marks; the compositor sets that page as the output
text. Keeping them apart is what lets the round-trip identity fail: a module
that rebuilt each file from positions it had just read out of that same file
could not disagree with it.
"""
