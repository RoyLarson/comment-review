"""THE DOCKET: every alteration the write chain is asked to make.

    {"pages": [
        {"path": "pkg/a/util.py",
         "sha":  "e3b0c44298fc",
         "role":  "block-context",
         "alterations": [{"cue": "b1", "text": "# the new comment"},
                         {"cue": "c0", "text": null}]}]}

!! IT IS THE WRITE SIDE'S BINDER, AND THE THREE LEVELS MIRROR IT. Roy,
2026-08-26: *"like the binder we have three levels of containers -- paragraph,
page, binder. We have to be able to unwind the alterations pretty close to the
same way."*

    level       READ                    WRITE
    one place   a Paragraph             an ALTERATION -- a cue, and its text
    one file    a Page / RedactedPage   a SCHEDULE: path, sha, alterations
    the whole   a Binder                a DOCKET: its schedules

!! ALL SIX ARE TYPES SINCE 2026-08-31, and this table stated the pairing while
three of the six were plain dict entries -- `decision-log.md Process: #67`. Each
answers `deserialize` over an already-loaded dict and `serialize` back to one,
so the read side and the write side unwind the same way, which is what Roy asked
for above.

!! THE LOAD IS THE FLOW'S, AND THAT MAKES THREE FAILURES SEPARABLE. Roy,
2026-08-31: *"This also makes file io errors and malformed json load dump errors
an explicit different step in the flow so those can be done without extra
collisions."*

    step           fails on                                  owned by
    read_text      the file is missing, unreadable, undecodable   the flow
    object_of      the text is not JSON, or not an object         the flow
    deserialize    it is an object, and not a docket              the container

! THEY COLLIDED WHILE `read(text)` HELD THE FIRST TWO. It took TEXT and did its
own decode, so "this file is not JSON" and "this JSON is not a docket" came back
as one `(dict, reason)` from one call, and a caller that wanted to answer them
differently had to match on the message. ! The IO failure was already separate
-- it had to be, because `read` could not open a file -- so the split was
one-of-three and looked like two.

! A DOCKET IN PRINT PRODUCTION is the instruction paperwork that travels with a
job, which is what this is: what the desk hands the chain that sets type.

!! THE NESTING IS NOT TIDINESS -- IT REMOVES TWO COUPLINGS. Flat, the docket was
one map from address to text, so the per-page grouping had to be DERIVED by
splitting every address, and the path an address carries is FLATTENED
(`pkg:a:util.py`), so something else had to turn it back. `proof_setter` used
the binder's page paths for that, and for the sha.

    flat    address -> text     grouping derived; path flattened; sha from the binder
    nested  pages -> schedule   grouping structural; path real; sha on the page

! MEASURED, on the flat form: `proof_setter.run` used the flattened key both as
a binder key and as a filesystem path, so every alteration on a file below the
repo root refused -- `repo / "pkg:a:util.py"` is invalid on Windows and missing
on POSIX. Every test hand-wrote its address with `/`, so none could disagree.
The nested form has no flattened path to recover.

!! SO THE BINDER DOES NOT REACH THE WRITE CHAIN AT ALL. Roy, 2026-08-25:
*"besides reading the sha and file path/name you should not be assuming any
binder things make it this far."* The docket carries both, which is what makes
that literally true rather than nearly true.

!! THE SHA IS RECORDED, NEVER RECOMPUTED. Roy, 2026-08-25: *"we can't assume
that the file didn't change between original read and loading to write and so
getting it out of the json blob is important."* A sha taken from the file at
write time would ask whether the file equals itself, which cannot fail.

!! IT WAS `desk/notations.py`, A STAND-IN, AND THE NAME COLLIDED. `notations`
sat one letter from the `annotations` that `binder/annotate.py` owns. ! The
instinct was right and that is why it collided -- Roy, 2026-08-26: *"if I was
writing between the lines with marks in red pen I think of those red marks as
notations."* The trade calls those PROOF CORRECTION MARKS, and `mark` is already
this system's word for what a role emits. What needed a name was what the DESK
makes of those marks. `decision-log.md Vocabulary: #14`.

!! `None` IS THE DELETE AND AN EMPTY STRING IS REFUSED. Roy, 2026-08-25: *"None
is explicit enough."* ! The galley took `""` as its vacation signal until this
landed, and a key whose value failed to serialise arrives looking exactly like
a deliberate deletion. Two spellings for one act is how a bug upstream becomes
a deletion downstream at exit 0.

! `role` IS OPTIONAL AND, WHEN PRESENT, ONE PER PAGE -- the role whose mark
settled every alteration this schedule carries. `desk.collator.docket_from`
is what writes it, from T4.2's settled places; `flows.revise.pull._set_by`
reads it back into `address -> role`, the provenance P6's reversal pairs
against. A docket with no `role` field maps every one of its addresses to
`""`, unchanged from before this field existed.

! SO A PAGE WHOSE PLACES TWO ROLES SETTLED CARRIES NO `role` AT ALL --
`docket_from` omits it rather than naming one of the two, because the field
cannot say more and a reversal routed to a role that never touched the place
is worse than one routed nowhere.
"""

from dataclasses import dataclass, field


def _not_a(where: str, noun: str, value: object) -> str:
    """One refusal, naming the JSON type that arrived instead of `noun`."""
    return f"{where}: a JSON {type(value).__name__}, not {noun}"


@dataclass(frozen=True)
class Alteration:
    """One place, and what the chain is to set there.

    Attributes:
        cue: the place on the page -- `b1`, `c0`.
        text: the replacement, or None to DELETE.

    !! `None` IS THE DELETE AND AN EMPTY STRING IS REFUSED -- see this module's
    header. Two spellings for one act is how a serialisation bug upstream
    becomes a deletion downstream at exit 0.

    ! IT IS THE THIRD LEVEL THE HEADER'S TABLE NAMES, and it was a bare
    `dict[str, str | None]` entry inside `Schedule` until 2026-08-31. The table
    said "one place -> an ALTERATION" while the code had no such type; this is
    that row made real -- `decision-log.md Process: #67`.
    """

    cue: str
    text: str | None

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[Alteration | None, list[str]]":
        """One alteration, checked.

        Args:
            where: how to name this alteration in a message.
            data: one entry of a page's `alterations`, as the load produced it.

        Returns:
            `(Alteration, [])` or `(None, [messages])`.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: an alteration must be an object"]
        # ! DECLARED, NOT NARROWED -- an isinstance narrow does not survive the
        # reads below, the same reason desk.containers.EditCopy.deserialize gives.
        checked: dict = data
        cue = checked.get("cue")
        if not isinstance(cue, str) or not cue:
            return None, [f"{where}: every alteration needs a `cue`"]
        if "text" not in checked:
            return None, [f"{where}@{cue}: an alteration needs `text` (null deletes)"]
        text = checked["text"]
        if text is None:
            return cls(cue=cue, text=None), []
        if not isinstance(text, str):
            return None, [
                f"{where}@{cue}: a replacement must be text or null, not"
                f" {type(text).__name__}"
            ]
        if not text:
            return None, [
                f"{where}@{cue}: an empty string is not a delete -- null is."
                " Two spellings for one act is how a serialisation bug"
                " becomes a deletion"
            ]
        return cls(cue=cue, text=text), []

    def serialize(self) -> dict:
        """This alteration as the wire dict."""
        return {"cue": self.cue, "text": self.text}


@dataclass(frozen=True)
class Schedule:
    """One page's alterations, and the page they are checked against.

    Attributes:
        path: as the REPO sees it -- `pkg/a/util.py`, NOT flattened. It is
            joined to the checkout and to the draft directory, so it is the one
            field a containment guard has to rule on.
        sha: of the page's text when the agents read it. `proof_setter` compares
            it against the file it is about to set.
        alterations: one `Alteration` per place, in the order the docket lists
            them.
        role: the role whose mark settled every alteration here, or "" when
            the docket carries none. `proof_setter` does not read this --
            `flows.revise._set_by` does; carried here so a caller unwinding a
            docket sees every field the format defines.
    """

    path: str
    sha: str
    alterations: tuple[Alteration, ...]
    role: str = ""

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[Schedule | None, list[str]]":
        """One page's schedule and every alteration on it, checked.

        ! EVERY BAD ALTERATION IS REPORTED, not the first -- matching
        `binder.page.RedactedPage.deserialize` and
        `desk.containers.EditCopy.deserialize`.
        A schedule with two malformed alterations is two things to fix.

        Returns:
            `(Schedule, [])` or `(None, [messages])`.
        """
        if not isinstance(data, dict):
            return None, [_not_a(where, "a page", data)]
        path = data.get("path")
        if not isinstance(path, str) or not path:
            return None, [f"{where}: every page needs a `path`, as the repo names it"]
        problems: list[str] = []
        sha = data.get("sha")
        if not isinstance(sha, str) or not sha:
            problems.append(f"{path}: every page needs the `sha` it was read at")
        raw_role = data.get("role")
        if raw_role is not None and (not isinstance(raw_role, str) or not raw_role):
            problems.append(f"{path}: `role`, when present, must be a non-empty string")
        raw = data.get("alterations")
        if not isinstance(raw, list) or not raw:
            problems.append(f"{path}: `alterations` must be a non-empty list")
            return None, problems
        alterations: list[Alteration] = []
        # ! ONE ALTERATION PER PLACE. Two would let a later one silently win,
        # and which of them applied would depend on iteration order.
        seen: set[str] = set()
        for one in raw:
            got, why = Alteration.deserialize(path, one)
            if got is None:
                problems += why
                continue
            if got.cue in seen:
                problems.append(f"{path}@{got.cue}: two alterations for one place")
                continue
            seen.add(got.cue)
            alterations.append(got)
        if problems:
            return None, problems
        return (
            cls(
                path=path,
                sha=sha if isinstance(sha, str) else "",
                alterations=tuple(alterations),
                role=raw_role if isinstance(raw_role, str) else "",
            ),
            [],
        )

    def serialize(self) -> dict:
        """This schedule as the wire dict.

        ! `role` IS OMITTED WHEN EMPTY, which is what `desk.collator.docket_from`
        writes: a page whose places two roles settled carries no `role` at all,
        because the field cannot say more and a reversal routed to a role that
        never touched the place is worse than one routed nowhere. Emitting
        `"role": ""` would make an absent field and an empty one look alike on
        the wire.
        """
        out: dict = {
            "path": self.path,
            "sha": self.sha,
            "alterations": [one.serialize() for one in self.alterations],
        }
        if self.role:
            out["role"] = self.role
        return out

    @property
    def edits(self) -> dict[str, str | None]:
        """Cue -> the replacement text, or None to delete.

        ! WHAT `flows.proof_setter._one` CONSUMES. It sets places by cue and
        never asks about order, so the mapping is built once here rather than
        by every caller -- and `deserialize` has already refused a repeated
        cue, which is the one thing that would make this lossy.
        """
        return {one.cue: one.text for one in self.alterations}


@dataclass(frozen=True)
class Docket:
    """Every alteration the write chain is asked to make.

    Attributes:
        schedules: one `Schedule` per page, in the order the docket lists them.

    !! THE FIELD IS `schedules` AND THE WIRE KEY IS `pages`, AND THAT
    DISAGREEMENT IS DELIBERATE. `Binder.pages` holds pages. A
    docket holds SCHEDULES: what to do to a page, which is not a page. Naming
    both `pages` would put two attributes of the same name on the two halves of
    the system returning different kinds of thing, and the write half's would
    be lying about what it holds.

    ! IT WAS `pages` FOR ONE COMMIT, 2026-08-31, and that repeated an error this
    module had already made and fixed. `schedules_of` carried the ruling:
    *"IT IS NAMED FOR WHAT IT PRODUCES. It was `by_page`, which named the
    mechanism."* Deleting that function took the ruling with it, and the field
    that replaced it was named for the WIRE KEY -- the same class of mistake one
    layer down. Roy caught it by asking whether `docket.pages` meant the read
    half's `Page`. It does not, and it never did.

    ! THE WIRE KEEPS `pages`, because the format is not this module's to change:
    a docket arrives from outside the system. `serialize` writes `pages`;
    `deserialize` reads it.

    !! THE LOAD IS NOT HERE, ruled `decision-log.md Process: #67`. Roy,
    2026-08-31: *"all flows start with a load step - not the modules code."*
    `deserialize` takes what the load PRODUCED -- an already-decoded dict -- so
    this module holds no `json.loads` and reaches no path. ! `read(text)` did
    both until 2026-08-31; `machine.json_object.object_of` is that load and
    moved to `commands/proof.py`, the one command that owns one.
    """

    schedules: tuple[Schedule, ...] = field(default_factory=tuple)

    @classmethod
    def deserialize(cls, where: str, data: object) -> "tuple[Docket | None, list[str]]":
        """A docket read back, or every rule it breaks.

        Args:
            where: how to name this docket in a message.
            data: the decoded object, as `machine.json_object.object_of`
                returns one. NEVER text and never a path.

        Returns:
            `(Docket, [])` or `(None, [messages])`.

        !! IT REFUSES RATHER THAN COPING, which is the shape the binder's own
        boundary uses and for the same measured reason: a guess that is wrong
        reads as an EMPTY input, and downstream that is indistinguishable from
        a run with nothing to do.

        !! AN EMPTY DOCKET IS REFUSED BY NAME, the same floor the binder puts
        under a missing `pages` key. Measured 2026-08-25 on the flat form:
        `read("{}")` answered `({}, "")`, `proof_setter.run` drafted nothing
        and `commands/proof.py` printed `0 page(s) drafted for review` at exit
        0.

        !! IT REPORTED ONE REASON AND NOW REPORTS EVERY ONE. `read` returned
        `(dict, str)` and stopped at the first broken rule, so a docket with
        three bad pages took three runs to fix. Every other container in this
        tree returns `(T | None, [messages])`; this is that contract arriving
        here -- Roy, 2026-08-31: *"Every container needs to be wired to do
        this."*
        """
        if not isinstance(data, dict):
            return None, [_not_a(where, "a docket", data)]
        checked: dict = data
        if "pages" not in checked:
            return None, [
                f"{where}: no `pages` key -- a docket names the pages it alters"
            ]
        raw = checked["pages"]
        if not isinstance(raw, list) or not raw:
            return None, [f"{where}: `pages` must be a non-empty list of pages"]
        schedules: list[Schedule] = []
        problems: list[str] = []
        # ! ONE SCHEDULE PER PAGE. Two would let a later one silently win, and
        # which of them applied would depend on iteration order.
        seen: set[str] = set()
        for n, one in enumerate(raw):
            got, why = Schedule.deserialize(f"{where}: page {n}", one)
            if got is None:
                problems += why
                continue
            if got.path in seen:
                problems.append(f"{got.path}: two schedules for one page")
                continue
            seen.add(got.path)
            schedules.append(got)
        if problems:
            return None, problems
        return cls(schedules=tuple(schedules)), []

    def serialize(self) -> dict:
        """This docket as the wire dict."""
        # ! THE WIRE KEY IS `pages` AND THE FIELD IS `schedules` -- see the
        # class docstring. The format is not this module's to rename.
        return {"pages": [one.serialize() for one in self.schedules]}
