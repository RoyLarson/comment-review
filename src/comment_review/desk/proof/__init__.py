"""The master proof's objects -- its containers and the records a fold decides.

    sheet.Sheet               one PAGE's marks, with that page's path and sha
    edit_copy.EditCopy        one ROLE's sheets, with the binder it was seeded from
    master_proof.MasterProof  one STAGE's edit_copies, places and moves
    place.Place, place.Filed  one address and everything filed or ruled at it
    move.Move, move.Placement one placement claim over two places
    state.State               the state a place is in once evaluated
    wire                      the seed half of the round trip, for Sheet and EditCopy

Each object's `deserialize` is the boundary parse for it and everything under
it. The verbs that build, fold and read these objects live elsewhere in `desk`
and in `flows`; this package holds the objects alone.

!! THE TYPE IS THE DEFINITION AND THERE IS NO MARKDOWN SOURCE, ruled
`decision-log.md Vocabulary: #30`. `docs/the-mark.md` exists because an agent
AUTHORS a mark, so a mark's shape must be published to a role. No agent ever
authors a container, so the type is where the shape lives, the way
`desk/marks/mark.py` defines `Mark`.

    write   flows.distribute.seed, flows.places.chief_copy_of,
            flows.bus
    read    commands/collate.py, at its inbound boundary, and
            flows.proof_io.load_proof

`collate` runs `EditCopy.deserialize` over every returned copy, and `turn`,
`disposition` and `proof` run `MasterProof.deserialize` over every proof they
read, so every refusal these parses declare can fire.

!! THIS DOCSTRING STATES WHAT THE TWO BOUNDARIES ARE, AND NOTHING ELSE RESTATES
IT. A container guards the **ENVELOPE** -- is this document the shape a copy
must be -- while `flows.mark_errors` rules on the **CONTENTS**, so each per-mark
problem routes back to the role that wrote it. They are not competing
contracts, and both run. ! `commands/collate.py` owns the ORDER and the RESPONSE
(envelope first; reported, not raised) and cites this paragraph rather than
repeating it -- a rule in two places is a rule that will disagree with itself.
"""
