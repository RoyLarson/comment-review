"""The answer set back into a file, and the proof the code survived.

    galley           updates a page with what the marks decided
    compositor       SETS that page as text, top to bottom. Decides nothing
    prove_unchanged  the executable code is byte-identical

!! THE GALLEY EDITS AND THE COMPOSITOR SETS, AND THEY ARE TWO ROLES. Roy,
2026-08-21: *"galley gets the old page - updates the old page with the
verdict/record/marks and then a page-setter sets the page to rewrite the output
text."* A module that did both was line arithmetic throughout, and splitting it
is what made the round-trip identity ABLE TO FAIL -- it had scored 699 of 699 on
its first run while rebuilding each file from positions it had just read out of
that same file, so it could not disagree.

! `prove_unchanged` HAS ITS OWN CLI AND SHOULD NOT. Roy, 2026-08-24: it *"falls
in with the galley area and the process flow for that side calls it."* P2.
"""
