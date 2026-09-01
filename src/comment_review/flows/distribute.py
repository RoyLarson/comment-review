"""DISTRIBUTE -- hand each role an edit_copy to fill.

    seed(binder, role)     one entry per row, ADDRESS ALREADY WRITTEN

!! NAMED FOR THE ACT, NOT THE ARTIFACT, since 2026-08-30. Roy: *"a flow named
mark reads like it is doing something that it is probably not doing"* -- and
*"the broadcasting part seems like distribute, the bringin back together seems
like collate."* `flows/collate.py` is the other half of the round.

!! AND THE CHECK IS NO LONGER HERE. The set-level checks moved
to `desk/collator.py` -- `decision-log.md Process: #54`: a mark answers for
itself, and everything about the SET is the collator's.

!! THE EDIT_COPY IS SEEDED BECAUSE THE ADDRESS IS THE PART ROLES GET WRONG.
MEASURED 2026-08-27: with a one-file binder every fanned-out agent wrote a bare
cue -- 62 of 78 marks -- despite the row carrying the full address and the packet
saying to copy it. With one file in play the path READS as redundant. **A bare
cue collides on merge: `a0` then means four different places**, and the fan-out
results showed zero overlap with the full rounds until the differing form was
noticed. ! Seeding removes the transcription rather than instructing against it.

! A seeded entry's `instruction` is `None` -- not ruled yet. A place left `None`
when the edit_copy comes back is a COVERAGE GAP, which is a different thing from
`clean`: `clean` says a role read this and had nothing to report.

!! AND A COVERAGE GAP IS NOT THE SAME AS A MARK THAT NAMES NO INSTRUCTION.
`desk.mark.untouched` is what tells them apart, and this flow read
`mark.get("mark") is None` until 2026-08-29 -- which said YES to both, so a
filled-in mark whose ruling key the code did not recognise was dropped before
`parse` saw it and recounted as a place nobody looked at.

!! WHAT THIS FLOW DOES NOT DO IS CHECK A CLAIM AGAINST THE PAGE. Whether
`claim.false` appears VERBATIM in the paragraph, whether a `move`'s destination
is addressable -- both need the page the role read, and both belong to
SOURCE-VERIFICATION in `collator`. `desk.mark.parse` says the same about its
own half.
"""

from comment_review.binder.binder import Binder
from comment_review.desk.containers import EditCopy, Sheet
from comment_review.desk.mark import Mark


def seed(binder: Binder, role: str) -> dict:
    """A fillable edit_copy for one role, one sheet per page in the binder.

    Args:
        binder: the deserialized binder, as the command's load produced it.
        role: the editorial role this edit_copy is for.

    Returns:
        `{"role": ..., "read_from": ..., "sheets": [...]}` -- `read_from` is
        copied from the binder as-is, naming the root and revise this
        edit_copy was censused from. Each entry in `sheets` carries one page's `path`
        and `sha`, plus its `marks` -- one per row on that page, holding the
        `address`, `anchor` and `raw_text` copied from the row, and
        `instruction: None` for the role to fill. ! THE SLOT IS BUILT BY
        `desk.mark.Mark.seed`, from the mark's own field names, so a
        renamed field breaks there rather than leaving this module writing
        the old key.

    !! ABSENT IS REFUSED AT THE BOUNDARY, AND WAS DEFAULTED TO `{}` UNTIL
    2026-08-28. `bind` refuses a binder that cannot say which root it read; this
    function read the same key with a `{}` fallback, so a binder that reached it
    by any other path -- an artifact read from disk, a hand-built dict --
    produced an edit_copy whose `read_from` was empty. ! THAT IS THE AMBIGUITY
    THE FIELD WAS ADDED TO REMOVE: a role holding an empty `read_from` cannot
    tell a revise from the original, which is the whole question
    `decision-log.md Process: #34` turns on.

    ! IT RAISED `KeyError` UNTIL 2026-08-31 AND NOW CANNOT. `Binder.deserialize`
    will not build a binder whose `read_from` is absent or misshapen, so by the
    time one is in hand the field is there -- which is what a container is FOR.
    The refusal did not weaken; it moved to the boundary and gained a name.

    !! NESTED BY PAGE SINCE 2026-08-29. A flat row list is what let a fanned-out
    edit_copy lose which page a mark belonged to; this walks the binder's own
    pages so each mark rides inside its own page's sheet, carrying that page's
    `sha`.
    """
    # ! WRITTEN THROUGH THE TYPES, NOT AS LITERALS, since 2026-08-31 --
    # `decision-log.md Process: #64`. `EditCopy.seed` copies `read_from` rather
    # than aliasing it, and `Sheet.seed` normalizes a null `sha`; both rules
    # used to be stated here as well as at the parse, and a rule in two places
    # is a rule that will disagree with itself.
    #
    # !! THE ADDRESS IS THE ROW'S OWN, AND WAS RECOMPOSED HERE UNTIL 2026-08-31.
    # This read `address_for(page["path"], row["cue"])` -- the identical
    # composition a `Paragraph` already carries. A second site computing an
    # address is the defect the binder's own prose records the compositor being
    # MEASURED on for 2026-08-22, and the container is what leaves only one.
    return EditCopy.seed(
        role=role,
        read_from=binder.read_from,
        sheets=[
            Sheet.seed(
                path=page.path,
                sha=page.sha,
                marks=[
                    Mark.seed(b.address, b.anchor, b.raw_text) for b in page.paragraphs
                ],
            )
            for page in binder.pages
        ],
    )
