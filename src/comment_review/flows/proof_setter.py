"""From the reviewers' alterations to a file a human can read.

    the docket
        -> one schedule per page                    path + sha + alterations
        -> reread the file FROM DISK                source_of
        -> the sha is the one the SCHEDULE recorded
        -> build the page                           page_of
        -> each alteration carries the page's anchor at its place
        -> galley          the marks are put on the page
        -> compositor      the page is set as text
        -> draft           a temporary file, never the original
        -> read it back    each alteration is at the cue it was given
        -> prove           only comments changed
        -> the human

!! IT STOPS AT THE TEMPORARY FILE. Roy, 2026-08-25: *"The workflow stops at
making a temporary file for the human to review. The final human-review
human-edit machine-review machine copy is its own workflow."* So `approve` is
not called here, and neither is anything transactional -- the per-page state,
the manifest and the resumable retry all belong to that second workflow.

!! THE BINDER DOES NOT REACH HERE AT ALL, SINCE 2026-08-26. Roy, 2026-08-24:
*"Nothing will transfer from the binder to the end."* Two values used to cross
anyway, and `run` took a binder to get them: each page's SHA, and the page paths
`unflatten` needed to turn an address's FLATTENED path back into a real one.

! THE DOCKET CARRIES BOTH NOW -- a schedule states its page's path as the repo
names it, and the sha it was read at. So the ruling is literal rather than
nearly true: Roy, 2026-08-25, *"besides reading the sha and file path/name you
should not be assuming any binder things make it this far."*

! WHAT IS READ FROM DISK IS THE PAGE ITSELF. No paragraph text or kind crosses
from anywhere, and the one anchor that does -- the one an alteration carries --
is checked against the page's and never set from (`decision-log.md Process:
#134`); the sha is what says the file is still the one the agents read.

! THE ORDER LIVES HERE AND NOWHERE ELSE. The galley edits, the compositor sets,
and neither knows what runs next. `STEPS` names that sequence as DATA; nothing
in `run()` reads it back -- `test_the_chain_IS_this_list` pins it against a
second literal, so a step dropped from the tuple shows up as a diff against
that pin, not as a call somebody forgot to make.
"""

from collections.abc import Sequence
from enum import StrEnum, auto
from pathlib import Path
from typing import NamedTuple

from comment_review import constants
from comment_review.binder.page import Page
from comment_review.docket.docket import Alteration, Docket, Schedule
from comment_review.flows.page_for import page_of
from comment_review.flows.read_diagnostics import format_failure
from comment_review.flows.source import source_of
from comment_review.machine.repo import Source, can_escape, sha_of, undraftable
from comment_review.reading.addresser import MODULE, address_for, cue_of
from comment_review.reading.context import ReadingContext
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.python.preservation import compare_preservation
from comment_review.reading.series import Series
from comment_review.results import compositor, galley
from comment_review.results.prove_unchanged import code_fingerprint


class Step(StrEnum):
    """One step of the chain, closed.

    `T1.15` of `docs/plans/0.2.4-the-mark-and-the-collator.md`: value DERIVED
    from the member name via `_generate_next_value_`, never hand-typed.
    `reading.series.Kind` set the StrEnum precedent but hand-types its own
    member values (`TRAILING = "trailing-comment"` is not `name.lower()`), so
    it is not itself an example of this derivation.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower()

    READ = auto()
    VERIFY = auto()
    EDIT = auto()
    SET = auto()
    DRAFT = auto()
    REREAD = auto()
    PROVE = auto()


#: The chain, as data -- read only by `test_the_chain_IS_this_list`, which
#: pins it against a second literal; `run()` itself never consults `STEPS`.
#: ! "set" NAMES A PIPELINE STAGE WITH NO `Refusal` OF ITS OWN: no site in
#: this module builds a `Refusal("set", ...)`. "draft" is not that -- `run`
#: builds one for a draft directory that overlaps the repo, which
#: `test_into_INSIDE_the_repo_refuses` and `test_the_repo_INSIDE_into_refuses`
#: assert against. ! `_one`'s target guard builds one too, and NO TEST REACHES
#: IT since the page paths are ruled on in `run`: what is left to it is a
#: symlink, and see that guard for why it is not verified here.
#: ! `Step`'s companion tuple, in definition order -- membership is asked of
#: this, never of the `Step` class itself.
STEPS = tuple(Step)


class Refusal(NamedTuple):
    """One reason the run stopped, and where.

    ! A REFUSAL NAMES ITS STEP. `flows/gather.py` catches a bare `Exception`
    too, and prints the path, the exception type and its message -- but
    nothing that says which of several steps failed. `step` is what a caller
    of this chain gets that a caller of `gather` does not.
    """

    step: str
    path: str
    why: str


class Drafted(NamedTuple):
    """One page set into a temporary file, and the bytes it was reviewed at."""

    path: str
    draft: Path
    sha: str


def run(docket: Docket, repo: Path, into: Path) -> tuple[list[Drafted], list[Refusal]]:
    """The whole chain, or nothing at all.

    !! A REFUSAL ABORTS THE RUN WHOLE, by ruling. Roy, 2026-08-25: *"fails loud
    amd stops is the right answer for now."* Every draft this run wrote is
    removed on a refusal AND on an exception escaping a page's own step, so a
    stopped run leaves no half-set of files that no page describes. !
    PROVISIONAL: the resumable per-page form belongs to the workflow that
    writes over the real files.

    !! IT STOPS AT THE FIRST REFUSAL, AND WENT ON TO EVERY REMAINING PAGE UNTIL
    2026-08-26. The refusals were collected and the loop continued -- reading,
    editing, drafting, rereading and proving each page after it -- so a LATER
    page that RAISED took the whole run out as a traceback and every refusal
    already recorded was lost, which is the opposite of *stops*.

    !! IT TOOK A BINDER TOO UNTIL 2026-08-26, for exactly two facts: each page's
    sha, and the page paths `unflatten` needed to turn an address's FLATTENED
    path back into a real one. A schedule carries both, so the binder no longer
    reaches the write chain -- Roy, 2026-08-25: *"besides reading the sha and
    file path/name you should not be assuming any binder things make it this
    far."*

    Args:
        docket: the deserialized docket -- pages, each with its path, the
            sha it was read at, and its alterations.
        repo: the checkout the pages are read from.
        into: the directory drafts are written to. Created if absent, and
            RESOLVED here -- see the containment guard in `_one`.

    Returns:
        `(drafted, [])` when every page passed, or `([], refusals)`.
    """
    # !! RESOLVED ONCE, HERE, BECAUSE `_one` COMPARES A RESOLVED TARGET AGAINST
    # IT. Measured 2026-08-25: with `into = Path("out_rel")` every page refused
    # with "would be written outside the draft directory" -- `(into / rel)`
    # resolves to an absolute path and an unresolved `into` is never a prefix of
    # one. `commands/proof.py` happens to resolve before calling, which hid it;
    # `run` is a flow anyone may call. ! Both sides are resolved, so a `..`
    # segment or a symlinked draft directory resolves to the real place the
    # comparisons below then agree on.
    into = into.resolve()
    repo = repo.resolve()
    # !! THE DISJOINTNESS GUARD IS THE FLOW'S, AND IT WAS THE TWO COMMANDS'
    # ALONE UNTIL 2026-08-25. MEASURED, on the signature of the day:
    # `run(..., repo, repo)`
    # answered `refused=[]` and the SOURCE FILE on disk held the replacement --
    # `_one`'s containment check passes when `into == repo`, because the source
    # file IS inside `into`. It is refused before anything is read or written,
    # and the reason it gives is `repo.undraftable`'s, so the rule is written in
    # one place and the commands ask the same function.
    why = undraftable(into, repo)
    if why:
        return [], [Refusal("draft", "", why)]

    # !! THE SCHEDULES ARE THE DOCKET'S OWN, NOT DERIVED. Each carries the page
    # path as the REPO names it and the sha it was read at, so nothing here
    # splits an address or consults a binder. ! The sha is RECORDED, never
    # recomputed -- Roy, 2026-08-25: "we can't assume that the file didn't
    # change between original read and loading to write and so getting it out
    # of the json blob is important." A sha taken from the file at write time
    # would ask whether the file equals itself, which cannot fail.
    schedules = docket.schedules
    # !! THE PAGE PATHS ARE RULED ON ONCE, HERE, BECAUSE THIS IS WHERE THEY
    # ENTER. A constraint asked here holds for every root a path is later joined
    # to. It was asked per file instead, against `repo` and against `into`
    # separately, and each refusal then named where the path landed rather
    # than the page path that could not be placed anywhere.
    outside = sorted(s.path for s in schedules if can_escape(s.path))
    if outside:
        return [], [
            Refusal(
                "read",
                p,
                "the docket names this page by a path that is not relative to"
                " the repository, so it resolves outside whatever root it is"
                " joined to",
            )
            for p in outside
        ]
    seen: set[str] = set()
    for schedule in schedules:
        if schedule.path in seen:
            return [], [Refusal("verify", schedule.path, "two schedules for one page")]
        seen.add(schedule.path)
    into.mkdir(parents=True, exist_ok=True)
    drafted: list[Drafted] = []
    refusals: list[Refusal] = []
    # !! ONLY WHAT THIS RUN MADE IS REMOVED. `_discard` used to `rmdir` any
    # empty directory under `into`, which includes ones that were there before
    # -- MEASURED 2026-08-25: a pre-created `<into>/pkg` was gone after a run
    # that refused. `_one` records the directories it is about to create into
    # this set, and `_discard` removes nothing that is not in it.
    created: set[Path] = set()

    # !! NOTHING RESOLVES A PATH HERE ANY MORE. The flat docket keyed by the
    # FLATTENED path an address carries -- `pkg:a:util.py` -- so `run` read the
    # binder's page paths and called `unflatten` over them to get a real one,
    # and a name that resolved to nothing was its own refusal. A schedule
    # carries the repo's own path, so both went with the shape change.
    for schedule in sorted(schedules, key=lambda s: s.path):
        try:
            made, why = _one(
                schedule,
                repo,
                into,
                created,
            )
        except Exception:
            # !! THE CLEANUP COVERS AN EXCEPTION, NOT ONLY A REFUSAL. Measured
            # 2026-08-25: with a later page's draft path pre-occupied, a
            # `PermissionError` from the draft write escaped as a raw traceback
            # and an earlier page's draft was left on disk -- only the
            # `refusals` branch below unlinked what had been written. The
            # exception still propagates; this removes what the run had
            # already drafted first.
            _discard_all(drafted, created)
            raise
        if why is not None:
            # ! NOTHING BELOW THIS PAGE IS READ. Collecting the refusal and
            # carrying on drafted every remaining page, so the run wrote files
            # for a proposal it had already refused -- and one of those pages
            # raising replaced the refusals with a traceback.
            refusals.append(why)
            break
        if made is not None:
            drafted.append(made)

    if refusals:
        _discard_all(drafted, created)
        return [], refusals
    return drafted, []


def _repeated(schedule: Schedule) -> Refusal | None:
    """The refusal for a schedule holding two alterations at one place, or None.

    `Schedule.edits` keeps the last alteration at a place, so setting such a
    page would drop the others without a word (`docket-defects` T11). Every
    repeated place is named, with what each alteration there would do.
    """
    parts = []
    for at, ones in schedule.repeated.items():
        count = "two" if len(ones) == 2 else str(len(ones))
        doing = "; ".join(_doing(one) for one in ones)
        where = address_for(schedule.path, at)
        parts.append(f"{where}: {count} alterations for one place -- {doing}")
    if not parts:
        return None
    return Refusal(
        "verify",
        schedule.path,
        " / ".join(parts) + " -- and setting the page would keep only the last",
    )


def _doing(one: Alteration) -> str:
    """What one alteration would do to its place, in a few words."""
    if one.text is None:
        return "a delete"
    first = one.text.splitlines()[0] if one.text else ""
    return f"text {first[:60]!r}"


def _discard_all(drafted: list[Drafted], created: set[Path]) -> None:
    """Remove every draft this run wrote, on the way out.

    ! ONE SPELLING FOR TWO EXITS. `run` unwinds twice -- an exception escaping a
    page's own step, and a refusal -- and both leave nothing behind.
    """
    for made in drafted:
        _discard(made.draft, created)


def _discard(draft: Path, created: set[Path]) -> None:
    """Remove a drafted file, and any directory THIS RUN made that it empties.

    !! A STOPPED RUN LEAVES NO TRACE, NOT ONLY NO FILE. `_one`'s
    `compositor.draft` creates `target.parent` with `parents=True`, so a
    nested `rel` -- `pkg/d.py` -- can leave `<into>/pkg/` behind an unlink that
    removes only the file. MEASURED 2026-08-25: a refused run over `pkg/d.py`
    left exactly that directory on disk, against this module's own docstring
    -- *"a stopped run leaves no half-set of files that no page describes."*
    A description of files did not include the directories made to hold them.

    !! AND IT REMOVES ONLY WHAT THE RUN MADE, which the earlier form did not.
    It walked up `rmdir`-ing any empty directory under `into` -- MEASURED
    2026-08-25: a `<into>/pkg` that existed BEFORE the run was gone after a run
    that refused. Its docstring said *"any directory under `into` IT leaves
    empty"*, a narrower promise than the code kept. `created` is what makes the
    promise checkable: `_one` puts a directory in it only when the directory
    did not exist at the moment the draft was about to be written.

    ! `into` ITSELF IS NEVER IN `created` -- `run` makes it before the loop,
    whether or not this run drafts anything into it, so removing it is not
    this function's decision to make.

    Args:
        draft: the file to remove.
        created: the directories this run made, which this may `rmdir` and
            removes from the set as it does.
    """
    draft.unlink(missing_ok=True)
    parent = draft.parent
    while parent in created and parent.is_dir():
        if any(parent.iterdir()):
            break
        parent.rmdir()
        created.discard(parent)
        parent = parent.parent


def _one(
    schedule: Schedule,
    repo: Path,
    into: Path,
    created: set[Path],
) -> tuple[Drafted | None, Refusal | None]:
    """One page through every step, or the first step that refused."""
    rel, recorded = schedule.path, schedule.sha
    # !! LEXICAL CONTAINMENT IS `run`'s, ONE STEP UP: `can_escape` has already
    # refused an absolute, drive-relative, rooted or `..`-walking page path for
    # the whole run. What is left to the two comparisons in this function is the
    # half no check on a STRING can answer -- what the filesystem RESOLVES the
    # resolve under. A symlinked directory under either root sends a well-formed
    # `rel` somewhere else, and only a resolved path can say so.
    #
    # ! WHICH GUARD IS LOAD-BEARING AND WHICH IS DEPTH: `run`'s is what the two
    # measured escapes -- `../escape_repo/sub/util.py` and
    # `sub/../../repo/util.py` -- refuse at. These two are depth, and they are
    # NOT verified on the machine this was written on: creating a symlink there
    # raises `WinError 1314`, the same reason
    # `test_a_DANGLING_SYMLINK_is_not_a_directory` skips.
    source = (repo / rel).resolve()
    if not source.is_relative_to(repo):
        return None, Refusal(
            "read", rel, "names a file outside the repository under review"
        )

    # !! THE SHA IS COMPARED BEFORE THE PARSE. `source_of` is `page_of`'s first
    # step exposed, so the bytes are read once and a file that no longer matches
    # what was reviewed is refused without being lexed or paged. It sat below
    # `page_of` until 2026-08-26, which paid for a page nothing then looked at.
    #
    # !! AN ABSENT RECORDED SHA REFUSES; IT DOES NOT PASS. `not recorded` is
    # the first clause on purpose -- a schedule carrying no sha would
    # otherwise compare "" against a real hash, and a future shape that
    # dropped the field would turn this gate off silently rather than loudly.
    # This is also the only check in the tree that catches a reviewer editing
    # the file it was reading: no agent file declares `tools:`, so all six
    # inherit Edit and Write, and "read-only" is prose until this compares.
    held = source_of(source)
    if isinstance(held, ReadFailure):
        return None, Refusal("read", rel, format_failure(held, path=rel))
    if not recorded or held.sha != recorded:
        return None, Refusal(
            "verify",
            rel,
            "the file has changed since it was reviewed -- reviewed at"
            f" {recorded or '<nothing recorded>'}, reads now as {held.sha}",
        )

    reading = schedule.reading
    if not isinstance(reading, ReadingContext):
        return None, Refusal("read", rel, "malformed saved reading context; regather")
    try:
        ReadingContext(
            reading.language, reading.reader, reading.compatibility, reading.settings
        )
    except (TypeError, ValueError):
        return None, Refusal("read", rel, "malformed saved reading context; regather")
    page = page_of(source, rel=rel, source=held, reading_context=reading)
    if isinstance(page, ReadFailure):
        return None, Refusal("read", rel, format_failure(page, path=rel))
    repeated = _repeated(schedule)
    if repeated is not None:
        return None, repeated
    edits, anchors = schedule.edits, schedule.anchors

    # Every alteration carries the page's anchor at its place, and each is
    # checked against the page's own anchor there, which is what
    # `decision-log.md Process: #134` and `#135` rule the anchor is for. An
    # anchored alteration at a place the page does not carry is left to
    # `galley.reset`, which refuses it by name.
    places = page.cues.places
    for where in edits:
        anchor = anchors.get(where)
        if anchor is None:
            return None, Refusal(
                "verify",
                rel,
                f"{address_for(rel, where)}: the alteration carries no anchor,"
                " and every alteration carries the page's anchor at its place",
            )
        at = places.get(where)
        if at is not None and at != anchor:
            return None, Refusal(
                "verify",
                rel,
                f"{address_for(rel, where)}: the mark's anchor is {anchor!r}, and"
                f" the page's anchor at that place is {at!r}",
            )

    placed = galley.reset(page, edits)
    if placed:
        return None, Refusal("edit", rel, "; ".join(placed))

    # !! THE FULL REPO-RELATIVE PATH, NOT JUST THE BASENAME. Measured
    # 2026-08-25: `into / Path(rel).name` flattened `pkg/a/util.py` and
    # `pkg/b/util.py` to the same `<into>/util.py`, so the second page's
    # draft silently overwrote the first's approved text at exit 0. The galley
    # command already kept `rel` under its output directory this way, and this
    # was mirrored from it before that command was emptied --
    # `docs/history.md`.
    target = (into / rel).resolve()
    # !! REFUSE ANYTHING THAT WOULD LAND OUTSIDE `into`, BEFORE ANY WRITE, for
    # the reason given at the read guard above: a resolved target is the only
    # thing that can say where the path actually went. The outcome it stands
    # against is the one this area was measured on twice -- a draft written over
    # the file under review, at exit 0.
    if not target.is_relative_to(into):
        return None, Refusal(
            "draft", rel, "would be written outside the draft directory"
        )
    # !! WHAT THE WRITE IS ABOUT TO MAKE, RECORDED BEFORE IT MAKES IT.
    # `machine.repo.write_raw` mkdirs with `parents=True`, so this is the last
    # moment at which "did this directory exist already" can be asked.
    # `_discard` removes only what is in this set.
    created.update(
        p
        for p in target.parents
        if p != into and p.is_relative_to(into) and not p.exists()
    )

    # !! EVERY STEP PAST THE GUARD IS COVERED, NOT ONLY THE REFUSALS. `run`'s
    # cleanup unlinks what is in `drafted`, and this page is not in it yet --
    # so before this, a `_reread` or `_prove` that RAISED rather than refusing
    # left `<into>/<rel>` on disk while `run`'s docstring said every draft this
    # run wrote is removed. The three calls below write the draft, read it back
    # and hash it; any of them can raise where none has a `Refusal` for it.
    #
    # !! `compositor.draft` IS INSIDE THE `try`, AND WAS OUTSIDE IT UNTIL
    # 2026-08-25. The mkdir runs before the write, so a write that raised left
    # `<into>/pkg/` behind with no handler that could remove it -- MEASURED
    # with `rel = "pkg/d.py"`: `into.iterdir()` answered `['pkg']`.
    #
    # ! ONE WRITER. `compositor.draft` IS `set_page` plus a call to
    # `machine.repo.write_raw`, which carries the mkdir and the `newline=""` --
    # load-bearing, since `read_source`'s untranslated read is what `_prove`'s
    # byte-identity comparison depends on. `_one` used to spell those three
    # lines itself, which is two spellings of the only writer: one gets updated
    # and the other does not. The containment refusal above still runs FIRST,
    # so this never writes a target that was not already cleared.
    # ! THE `mkdir` MOVED INTO `machine` WITH THE WRITE (`P45`) and the comment
    # above still holds: it runs before the bytes land either way, which is why
    # `created` is recorded first and why this call is inside the `try`.
    try:
        compositor.draft(page, target)
        # The draft is read once. `_reread` hands back the page it read, and
        # `_prove` takes its text and the places the alterations name on it,
        # the approved changes it compares against (`decision-log.md Process:
        # #113`).
        draft, off = _reread(rel, target, edits, reading)
        if draft is None:
            _discard(target, created)
            return None, off

        unproven = _prove(rel, page, draft, target, _approved(page, draft, edits))
    except Exception:
        _discard(target, created)
        raise
    if unproven is not None:
        _discard(target, created)
        return None, unproven
    return Drafted(rel, target, page.sha), None


def _reread(
    rel: str, target: Path, edits: dict[str, str | None], reading: ReadingContext
) -> tuple[Page | None, Refusal | None]:
    """Read the draft back as a page: is each alteration at the cue it was given?

    !! IT IS READ FROM DISK, NOT FROM THE PAGE IN HAND. Roy, 2026-08-24: the
    workflow *"Sends that through the page system again to make certain that
    the agents put the right comments in the right places."* A page still in
    memory would be agreeing with itself -- the shape `docs/gates.md` records
    the round trip scoring 699 of 699 on.

    A failed page read becomes a reread refusal before any alteration is proved.

    Args:
        rel: how the repo names the page this draft was set from.
        target: the draft on disk.
        edits: cue -> replacement text, or None where the place was dropped.
        reading: the saved context used to admit the original page.

    Returns:
        `(the draft's page, None)`, or `(None, the first refusal)`. The page's
        `text` is what `page_of` took from `read_source` -- the untranslated
        read `_prove`'s comparison depends on -- and its places are where
        `_prove` finds, in the draft, the declaration each approved `a`
        alteration documents.
    """
    page = page_of(target, rel=rel, reading_context=reading)
    if isinstance(page, ReadFailure):
        return None, Refusal(
            "reread", rel, f"the draft: {format_failure(page, path=rel)}"
        )
    # !! COLLECTED AS A LIST PER CUE, BECAUSE A COLLISION IS A REFUSAL AND NOT A
    # LAST-ONE-WINS. This was `{cue_of(b.address).cue: b for b in page ...}`,
    # which keeps the LAST paragraph at a cue two paragraphs share and checks
    # the alteration against it -- so a draft holding the approved text at one of
    # them and prose nobody looked at at the other passed. `galley.reset`
    # refuses that shape by name (157 of them measured in one tree on
    # 2026-08-21), and a verification step weaker than the edit step it exists
    # to check cannot report the edit step being wrong.
    placed: dict[str, list] = {}
    for b in page:
        if b.address:
            placed.setdefault(cue_of(b.address).cue, []).append(b)
    for where, replacement in edits.items():
        found = placed.get(where)
        if not found:
            return None, Refusal(
                "reread", rel, f"{where}: the draft carries no such place"
            )
        if len(found) > 1:
            return None, Refusal(
                "reread",
                rel,
                f"{where}: {len(found)} paragraphs share this place in the draft,"
                " so no alteration can be checked against it",
            )
        got = found[0]
        if replacement is None:
            # !! A VACATED `c` READS BACK AS `['']`, NOT AS `[]`, so this asked
            # for a shape no drop can produce. `page.empty_places` stores a
            # margin's prose as `[lines[n - 1][len(code):]]` -- the room beside
            # the statement, which is the empty string when nothing sits there
            # -- while this built `want = []` and compared exactly. MEASURED
            # 2026-08-25 on `tests/conftest.SAMPLE`: `c0`, `c1` and `c2` each
            # refused with "holds [''], was given []", so `drop` was
            # unreachable for the whole `c` series while the galley, the
            # compositor and the draft on disk were all correct.
            #
            # ! WHAT A DROP ASSERTS IS THAT THE PLACE HOLDS NO PROSE, which is
            # the question asked here. It can still fail: a place that kept its
            # paragraph reads back with that paragraph's text in it.
            if any(line.strip() for line in got.raw_lines):
                return None, Refusal(
                    "reread",
                    rel,
                    f"{where}: was dropped, but the draft holds {got.raw_lines!r}",
                )
            continue
        want = constants.text_lines(replacement)
        if got.raw_lines != want:
            return None, Refusal(
                "reread",
                rel,
                f"{where}: holds {got.raw_lines!r}, was given {want!r}"
                f"{_elsewhere(placed, where, want)}",
            )
    return page, None


def _elsewhere(placed: dict[str, list], where: str, want: list[str]) -> str:
    """Which OTHER place in the draft holds this text, as a trailing clause.

    !! TWO PLACES CAN NAME ONE POSITION, and the refusal above named neither
    when they disagreed. `addresser.cue` emits the closing gap and the file's
    back matter at the SAME `<eof>` trigger -- its own comment says so:
    *"both sentinels are shared -- `a0` with `f0` at the head, the closing gap
    with `f1` at the foot."* Which of the two a paragraph attaches to is the
    LEXER's `matter` rule, so an `add` of an ordinary comment at the closing
    gap is set exactly where it was asked for and read back at `f1`.

    ! MEASURED 2026-08-25 on `tests/conftest.SAMPLE`: `{'m.py@b4': '# ADDED'}`
    and `{'m.py@f1': '# ADDED'}` compose the SAME bytes, and the second passes
    the whole chain while the first refused with `b4: holds [], was given
    ['# ADDED']` -- a message that named neither the collision nor the place
    that does hold the text.

    ! IT REPORTS; IT DOES NOT ACCEPT. Naming the other place is what makes the
    refusal actionable. Deciding which of two co-located places owns prose at
    the foot of a file is a page-model ruling -- see
    `TODO/foot-of-file-two-places.md` -- and reading the alteration as
    satisfied because the text is SOMEWHERE would be this step agreeing with
    the edit step instead of checking it.

    ! IT READS THE TABLE `_reread` ALREADY BUILT, rather than walking the page a
    second time and recomputing `cue_of` for every paragraph on it. ! Where
    SEVERAL places hold the text it now names the first such CUE down the page
    rather than the first matching PARAGRAPH; the two differ only when an
    earlier cue's match sits below a later cue's paragraph, and either answers
    the question this returns a clause for.

    Args:
        placed: the draft's paragraphs, grouped by cue, as `_reread` built it.
        where: the cue whose alteration did not read back.
        want: the lines that were asked for there.

    Returns:
        `" -- <cue> holds it"`, or "" when no other place does.
    """
    for cue, found in placed.items():
        if cue != where and any(b.raw_lines == want for b in found):
            return f" -- {cue} holds it"
    return ""


def _approved(
    page: Page, draft: Page, edits: dict[str, str | None]
) -> list[tuple[Paragraph, Paragraph]]:
    """Each approved alteration's place, on the page and in the draft.

    `_prove` compares the draft against these approved changes, not against
    nothing changed (`decision-log.md Process: #113`).

    Keying each page by cue is safe for the cues read here: by the time this
    runs, every cue in `edits` is held by exactly one paragraph on the page --
    `galley.reset` refuses a cue that no paragraph, or more than one, holds --
    and in the draft, where `_reread` refuses the same two shapes.

    Args:
        page: the page the draft was set from. `galley.reset` changes its
            prose, not its anchors or the lines it puts them on, so those
            still describe the text before.
        draft: the draft, as `_reread` read it back.
        edits: cue -> replacement text, or None where the place was dropped.

    Returns:
        `(the place on the page, the same place in the draft)`, per cue.
    """
    was = {cue_of(b.address).cue: b for b in page if b.address}
    now = {cue_of(b.address).cue: b for b in draft if b.address}
    return [(was[where], now[where]) for where in edits]


def _prove(
    rel: str,
    before: str | Page,
    after: str | Page,
    path: Path,
    approved: Sequence[tuple[Paragraph, Paragraph]] = (),
) -> Refusal | None:
    """Prove retained source unchanged after the approved prose alterations.

    Text inputs first enter page admission. Python compares the pages' acquired
    lexical records, preserving executable source, ordinary literals, protected
    directives and their attachments. Ordinary prose may change; documentation
    presence stays fixed except at selected owners named by approved `a` pairs.
    Each pair must identify the same unique owner through admitted source
    positions and anchors. A removed docstring cannot authorize changes to an
    ordinary literal promoted into its place.

    `_reread` checks the requested text at each edited cue; this comparison also
    covers retained source elsewhere in the file. Other languages use their
    existing comment-stripped fingerprint comparison. Failed admission,
    unidentified owners and unprovable comparisons all refuse.
    """
    admitted: list[Page] = []
    for side, value in (("before", before), ("after", after)):
        page = (
            value
            if isinstance(value, Page)
            else page_of(path, rel=rel, source=Source(value, sha_of(value)))
        )
        if isinstance(page, ReadFailure):
            return Refusal("prove", rel, f"{side}: {format_failure(page, path=rel)}")
        admitted.append(page)
    page_before, page_after = admitted
    if (
        page_before.reading.language == "python"
        or page_after.reading.language == "python"
        or page_before.python_read is not None
        or page_after.python_read is not None
    ):
        if page_before.python_read is None or page_after.python_read is None:
            return Refusal("prove", rel, "the proof kind is not what it was")
        owners: set[int | None] = set()
        for was, now in approved:
            if Series.of(cue_of(was.address).cue) is not Series.DECLARED:
                continue
            before_owner = _python_documentation_owner(page_before, was)
            after_owner = _python_documentation_owner(page_after, now)
            if not before_owner or before_owner != after_owner:
                return Refusal(
                    "prove",
                    rel,
                    "the declaration an approved docstring alteration documents "
                    "cannot be identified in the code, so its docstring cannot "
                    "be set aside",
                )
            owners.add(before_owner[0])
        result = compare_preservation(
            page_before.python_read,
            page_after.python_read,
            allowed_documentation_owners=owners,
        )
        if not result.unchanged:
            return Refusal(
                "prove",
                rel,
                "the executable code is not what it was: "
                + format_failure(ReadFailure(result.diagnostics), path=rel),
            )
        return None
    before_text, after_text = (page.text for page in admitted)
    kind, want = code_fingerprint(before_text, path)
    got_kind, got = code_fingerprint(after_text, path)
    if kind != "stripped" or got_kind != "stripped":
        return Refusal("prove", rel, "the code in this file cannot be proven unchanged")
    if want != got:
        return Refusal("prove", rel, "the executable code is not what it was")
    return None


def _python_documentation_owner(
    page: Page, paragraph: Paragraph
) -> tuple[int | None, ...]:
    """Locate one approved owner using the admitted place and declaration position."""
    read = page.python_read
    assert read is not None
    places = [place for place in page if place.address == paragraph.address]
    cue = cue_of(paragraph.address).cue
    if len(places) != 1 or Series.of(cue) is not Series.DECLARED:
        return ()
    if (paragraph.anchor, paragraph.anchor_line, paragraph.anchor_num) != (
        page.cues.anchor_of(cue),
        page.cues.anchor_line(cue),
        page.cues.anchor_num(cue),
    ):
        return ()
    if paragraph.anchor == MODULE and paragraph.anchor_line is None:
        return (None,)
    owners = tuple(
        index
        for index, declaration in enumerate(read.source.declarations)
        if read.source.position(declaration.anchor).line == paragraph.anchor_line
    )
    return owners if len(owners) == 1 else ()
