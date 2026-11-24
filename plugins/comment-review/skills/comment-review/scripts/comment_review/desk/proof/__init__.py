"""The master proof's objects -- its containers and the records a fold decides.

    sheet.Sheet               one page's marks, with that page's path and sha
    edit_copy.EditCopy        one role's sheets, with the binder it was seeded from
    master_proof.MasterProof  one stage's edit_copies, places and moves
    place.Place, place.Filed  one address and everything filed or ruled at it
    move.Move, move.Placement one placement claim over two places
    state.State               the state a place is in once evaluated
    mark.Mark                 one role's ruling at one place, one type per
                              instruction
    source.Source             one source entry a mark carries
    answer.Answer             one role's answer to one question in a turn
    disposition.Disposition   the chief's ruling at a carried-forward place or
                              an open move
    wire                      the seed half of the round trip, for Sheet and EditCopy

Each container's `deserialize` is the boundary parse for it and everything under
it. The verbs that build, fold and read these objects live elsewhere in `desk`
and in `flows`; this package holds the objects alone.

!! The type is the definition and there is no Markdown source. `docs/the-mark.md`
exists because an agent authors a mark, so a mark's shape must be published to a
role. No agent ever authors a container, so the type is where the shape lives,
the way `desk/proof/mark.py` defines `Mark`.

    write   flows.distribute.seed, and flows.proof_io.save_proof
    read    commands/collate.py and commands/check.py, at their inbound
            boundary; commands/proof.py; and flows.proof_io.load_proof

`collate` runs `EditCopy.deserialize` over every returned copy, and `turn`,
`disposition` and `proof` run `MasterProof.deserialize` over every proof they
read, so every refusal these parses declare can fire.

!! This docstring states what the two boundaries are, and nothing else restates
it. A container guards the **envelope** -- is this document the shape a copy
must be -- while `Sheet.deserialize` sorts the **contents** into ruled, unruled
and refused and `flows.mark_errors` reports them, so each per-mark problem routes
back to the role that wrote it. They are not competing contracts, and both run.
! `commands/collate.py` owns the order and the response (envelope first;
reported, not raised) and cites this paragraph rather than repeating it -- a rule
in two places is a rule that will disagree with itself.
"""
