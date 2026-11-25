"""The checkout indexed, so a claim on a page can be resolved against it.

    code_names   every name the tree DEFINES
    referrers    who NAMES the files under review
    names        what COUNTS as a name

!! THE FIRST TWO ARE INVERSES, AND THAT IS WHY THEY SIT TOGETHER. `referrers`
gives the names by which another tracked file would cite a file under review;
`code_names` gives the names the tree defines. One indexes occurrences, the
other definitions.

!! AND BOTH EXIST BECAUSE A PAGE CANNOT CORROBORATE ITSELF. A corpus built from
the text under review contains the comments being checked, so every obituary
resolves against itself and the check always passes. Both read the WHOLE
CHECKOUT and never the pages under review.

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
