"""THE DOCKET: what the desk hands the chain that writes.

    docket    every alteration the run is asked to make, and the interface
              between the middle and the first write to disk

!! IT IS THE WRITE SIDE'S `binder`, AND IT IS ITS OWN AREA FOR THE SAME REASON.
Roy, 2026-08-26: *"this is solid write-side separate module stuff like binder is
a separate module from the middle and the io stuff. It defines an interface
between the middle and the first write-to-disk (though in a temp file)."*

    reading  ->  binder   ->  agents  ->  desk  ->  DOCKET  ->  results
                 what a role reads          the middle        what gets set

! SO IT DEPENDS ON NEITHER SIDE. It reads an address with the addresser and a
JSON object with `machine.json_object`, and nothing else. The desk that fills it
does not exist yet; the chain that drains it is `flows.proof_setter`.

!! IT WAS `desk/notations.py` UNTIL 2026-08-26, and moving it out is the point
rather than a tidy-up: parked in `desk/`, the interface looked like part of the
middle, and the middle is the half that is not designed. `decision-log.md
Vocabulary: #14` carries the naming; `TODO/notations-collides-with-annotations
.md` carries what is left.
"""
