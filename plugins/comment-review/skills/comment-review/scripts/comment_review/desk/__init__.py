"""The copy desk: what a role's marks become.

    marks               the shape a role writes, and the rules a mark can be
                         judged by on its own -- no binder, no page -- with
                         the table of rows every reader asks
    answers             what a role hands back in a turn, and its own table
    dispositions        what the chief rules on a place the roles never
                         decided, and its own table
    evaluate            the passes that take a place from the marks filed on
                         it to the state it comes to
    work                the Unit of Work: a fold over the places, which
                         commits or rolls back whole, and the events it emits
    collator            source verification, per mark, against the page it
                         rules on
    proof               the master proof's objects -- its containers, among
                         them every `edit_copy` of one stage, and the records
                         a fold decides
    topology            a run's schedule, read from a TOML file -- which
                         stages run, in what order, and what each dispatches
    external_address    a sketch, not in service -- a coordinate into a file
                         this system does not set
    stages              the mark sequence, as data -- `Kind`, `Role`, and a
                         stage's `dispatches`
    report              the stage reports the commands render: refusals,
                         questions for the human, a rollback, a committed fold

!! This package is the middle: marks in from the roles, a closed master proof out,
from which `flows.transcribe.docket_of_proof` writes the docket.
"""
