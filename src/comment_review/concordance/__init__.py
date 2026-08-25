"""The checkout indexed, so a claim on a page can be resolved against it.

    code_names   every name the tree DEFINES
    referrers    who NAMES the files under review

!! THEY ARE INVERSES, AND THAT IS WHY THEY SIT TOGETHER. `referrers` says it
itself: *"The census resolves what a comment CITES. This resolves the other
direction -- who cites the code being edited."* One indexes definitions, the
other occurrences.

!! AND BOTH EXIST BECAUSE A PAGE CANNOT CORROBORATE ITSELF. A corpus built from
the text under review contains the comments being checked, so every obituary
resolves against itself and the check always passes. Everything here reads the
WHOLE CHECKOUT and never the pages under review.

! NEITHER IS AN IO OPERATION AND NEITHER KNOWS WHAT A PAGE IS, which is why
`machine` and `binder` both had to stretch to hold them, and why they sat
unplaced at the package root from the move until the ruling. Roy, 2026-08-24:
*"concordance -- for the two."*

! A CONCORDANCE is the trade's index of every word in a text and where each
occurs. The name was reached the way `compositor` was: ask what the thing IS,
find the job in the answer, then take the trade's word for that job.

! WHAT IS READ-ONLY HERE IS EVERYTHING. `referrers` always exits 0 and every
line it prints is a CANDIDATE -- a file to READ, never a file a verdict may
target.
"""
