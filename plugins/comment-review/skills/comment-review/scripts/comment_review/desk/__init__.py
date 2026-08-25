"""The copy desk: what a role is GIVEN, and what it HANDS BACK.

    outbound    run_context   the dispatch packet a run is checked against
                vocabulary    the terms one role is handed, and no others
    inbound     desk          the text a mark is measured against
                verdicts      the join -- reports against the census, every
                              citation checked

!! THE TWO DIRECTIONS ARE THE SUBJECT, which is why they sit together: a term
this package hands out is a term it must accept back, and the pair going out of
step is what `scripts/check_vocabulary.py` exists to catch.

! WHAT CARRIES A ROLE'S ANSWER TO THE PAGE IS NOT HERE AND IS NOT NAMED. The
galley needs only *this address gets this paragraph*; a verdict and a record are
not that, and inferring the record does it was ruled WRONG. Roy, 2026-08-24:
*"we have a missing piece in the chain."*
"""
