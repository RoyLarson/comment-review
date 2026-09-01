"""The checkout indexed, so a claim on a page can be resolved against it.

    code_names   every name the tree DEFINES
    referrers    who NAMES the files under review
    names        what COUNTS as a name -- the predicate both sides match on
    annotate     the KEY, built from prose, and looked up against the index

!! THE FIRST TWO ARE INVERSES, AND THAT IS WHY THEY SIT TOGETHER. `referrers`
says it itself: *"The census resolves what a comment CITES. This resolves the
other direction -- who cites the code being edited."* One indexes definitions,
the other occurrences.

!! AND BOTH EXIST BECAUSE A PAGE CANNOT CORROBORATE ITSELF. A corpus built from
the text under review contains the comments being checked, so every obituary
resolves against itself and the check always passes. Both read the WHOLE
CHECKOUT and never the pages under review.

!! `annotate` JOINED THEM 2026-08-31, AND IT IS THE OTHER HALF OF ONE LOOKUP.
Roy: *"it is part of that system ... It does something necessary but in a Broken
way."* An index is only reachable through a key, and `annotate` is what turns a
backticked token in prose into one. ! `names.SYMBOLISH` is the predicate both
ends match on -- if the key-builder and the index-builder disagreed about what a
name looks like, a key could never hit -- and it had nowhere to live while its
two readers sat in two packages. `decision-log.md Process: #70`.

!! **AND IT BREAKS THIS PACKAGE'S OWN TWO PROPERTIES, WHICH IS FILED RATHER THAN
PAPERED OVER.** This paragraph read *"NEITHER IS AN IO OPERATION AND NEITHER
KNOWS WHAT A PAGE IS"* -- true of `code_names` and `referrers`, and false of
`annotate`, which mutates a `Paragraph` and calls `(repo / cited).exists()`.
Roy called that the broken part when he ruled the move.
`TODO/containers-and-verification-are-unwired.md` T35 is the IO half.

! THE ORIGINAL TWO SAT UNPLACED AT THE PACKAGE ROOT UNTIL THE RULING, because
`machine` and `binder` both had to stretch to hold them. Roy, 2026-08-24:
*"concordance -- for the two."*

! A CONCORDANCE is the trade's index of every word in a text and where each
occurs. The name was reached the way `compositor` was: ask what the thing IS,
find the job in the answer, then take the trade's word for that job.

! WHAT IS READ-ONLY HERE IS EVERYTHING. `referrers` always exits 0 and every
line it prints is a CANDIDATE -- a file to READ, never a file an instruction may
target.
"""
