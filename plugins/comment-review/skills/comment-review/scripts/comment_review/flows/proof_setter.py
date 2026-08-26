"""From the reviewers' notations to a file a human can read.

    notations + the saved binder
        -> resolve each address                    -> path + cue
        -> reload the page FROM DISK                page_of
        -> the sha is the one the binder recorded
        -> galley          the marks are put on the page
        -> compositor      the page is set as text
        -> draft           a temporary file, never the original
        -> read it back    each notation is at the cue it was given
        -> prove           only comments changed
        -> the human

!! IT STOPS AT THE TEMPORARY FILE. Roy, 2026-08-25: *"The workflow stops at
making a temporary file for the human to review. The final human-review
human-edit machine-review machine copy is its own workflow."* So `approve` is
not called here, and neither is anything transactional -- the per-page state,
the manifest and the resumable retry all belong to that second workflow.

!! NOTHING TRANSFERS FROM THE BINDER TO THE END EXCEPT TWO VALUES. Roy,
2026-08-24: *"Nothing will transfer from the binder to the end."* The ADDRESS
crosses as a key, and the SHA crosses as the thing the verification compares.
No paragraph text, kind or anchor does -- the page is read again from disk.

! THE PAGE PATH IS THE OTHER HALF OF THE ADDRESS, not a third value. Roy,
2026-08-25, ruling what may reach here: *"besides reading the sha and file
path/name you should not be assuming any binder things make it this far."* An
address carries the FLATTENED path, so `run` reads the binder's page paths to
`unflatten` it -- the same paths it already reads for the sha.

! THE ORDER LIVES HERE AND NOWHERE ELSE. The galley edits, the compositor sets,
and neither knows what runs next. `STEPS` names that sequence as DATA; nothing
in `run()` reads it back -- `test_the_chain_IS_this_list` pins it against a
second literal, so a step dropped from the tuple shows up as a diff against
that pin, not as a call somebody forgot to make.
"""

from pathlib import Path
from typing import NamedTuple

from comment_review.desk import notations as notations_mod
from comment_review.flows.page_for import page_of
from comment_review.machine import constants
from comment_review.machine.repo import read_source, undraftable
from comment_review.reading.addresser import address_for, cue_of, unflatten
from comment_review.results import compositor, galley
from comment_review.results.prove_unchanged import code_fingerprint

#: The chain, as data -- read only by `test_the_chain_IS_this_list`, which
#: pins it against a second literal; `run()` itself never consults `STEPS`.
#: ! "set" NAMES A PIPELINE STAGE WITH NO `Refusal` OF ITS OWN: no site in
#: this module builds a `Refusal("set", ...)`. "draft" is not that anymore --
#: `67b8c9b`'s containment guard in `_one` builds `Refusal("draft", ...)` for a
#: `rel` that would resolve outside `into`, and `test_proof_setter.py` asserts
#: `refused[0].step == "draft"` against it.
STEPS = ("read", "verify", "edit", "set", "draft", "reread", "prove")


class Refusal(NamedTuple):
    """One reason the run stopped, and where.

    ! A REFUSAL NAMES ITS STEP. `census.py:204` catches a bare `Exception`
    too, and prints the path, the exception type and its message -- but
    nothing that says which of several steps failed. `step` is what a caller
    of this chain gets that a caller of `census.py` does not.
    """

    step: str
    path: str
    why: str


class Drafted(NamedTuple):
    """One page set into a temporary file, and the bytes it was reviewed at."""

    path: str
    draft: Path
    sha: str


def run(
    notations: dict[str, str | None], binder: dict, repo: Path, into: Path
) -> tuple[list[Drafted], list[Refusal]]:
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

    Args:
        notations: address -> replacement text, or None to delete.
        binder: as `binder.read` returned it.
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
    # ALONE UNTIL 2026-08-25. MEASURED: `run(notations, binder, repo, repo)`
    # answered `refused=[]` and the SOURCE FILE on disk held the replacement --
    # `_one`'s containment check passes when `into == repo`, because the source
    # file IS inside `into`. It is refused before anything is read or written,
    # and the reason it gives is `repo.undraftable`'s, so the rule is written in
    # one place and the commands ask the same function.
    why = undraftable(into, repo)
    if why:
        return [], [Refusal("draft", "", why)]

    grouped, unresolved = notations_mod.by_page(notations)
    if unresolved:
        return [], [Refusal("read", "", why) for why in unresolved]

    # ! THE SHA IS READ OUT OF THE SAVED BINDER, NEVER RECOMPUTED FROM THE FILE.
    # Roy, 2026-08-25: "we can't assume that the file didn't change between
    # original read and loading to write and so getting it out of the json
    # blob is important." A sha derived from the file at write time would only
    # ask whether the file equals itself, which cannot fail.
    recorded = {
        str(page.get("path", "")): str(page.get("sha", ""))
        for page in binder.get("pages", [])
    }
    into.mkdir(parents=True, exist_ok=True)
    drafted: list[Drafted] = []
    refusals: list[Refusal] = []
    # !! ONLY WHAT THIS RUN MADE IS REMOVED. `_discard` used to `rmdir` any
    # empty directory under `into`, which includes ones that were there before
    # -- MEASURED 2026-08-25: a pre-created `<into>/pkg` was gone after a run
    # that refused. `_one` records the directories it is about to create into
    # this set, and `_discard` removes nothing that is not in it.
    created: set[Path] = set()

    # !! THE PAGE PATHS ARE WHAT UNFLATTENS AN ADDRESS. `by_page` keys by the
    # FLATTENED path an address carries -- `pkg:a:util.py` -- and keeps no
    # binder to turn it back. This does: the paths it already read for
    # `recorded` are exactly the set `unflatten` resolves against, so the sha
    # and the file path remain the only two values crossing from the binder.
    paths = list(recorded)
    for name, edits in sorted(grouped.items()):
        # !! `""` MEANS UNKNOWN OR AMBIGUOUS, AND IS NOT A PATH. Reading it as
        # one would ask the filesystem for the repo root itself. Measured
        # 2026-08-25 before `unflatten` ran here: the flattened name was handed
        # to `recorded.get` AND to `page_of`, so a binder keyed `pkg/a/util.py`
        # missed on both and every file below the repo root refused.
        rel = unflatten(name, paths)
        if not rel:
            named = ", ".join(address_for(name, cue) for cue in sorted(edits))
            refusals.append(
                Refusal(
                    "read",
                    name,
                    f"no page in the binder is named by this address ({named})",
                )
            )
            break
        try:
            made, why = _one(rel, edits, recorded.get(rel, ""), repo, into, created)
        except Exception:
            # !! THE CLEANUP COVERS AN EXCEPTION, NOT ONLY A REFUSAL. Measured
            # 2026-08-25: with a later page's draft path pre-occupied, a
            # `PermissionError` from `write_text` escaped as a raw traceback
            # and an earlier page's draft was left on disk -- only the
            # `refusals` branch below unlinked what had been written. The
            # exception still propagates; this removes what the run had
            # already drafted first.
            for made in drafted:
                _discard(made.draft, created)
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
        for made in drafted:
            _discard(made.draft, created)
        return [], refusals
    return drafted, []


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
    rel: str,
    edits: dict[str, str | None],
    recorded: str,
    repo: Path,
    into: Path,
    created: set[Path],
) -> tuple[Drafted | None, Refusal | None]:
    """One page through every step, or the first step that refused."""
    # !! THE READ IS CONTAINED TOO, AND ONLY THE WRITE WAS UNTIL 2026-08-26.
    # MEASURED with `rel = "../escape_repo/sub/util.py"`: the file OUTSIDE the
    # checkout was read, lexed, paged and edited by `galley.reset` before the
    # containment guard below refused at `draft` -- so the refusal named the
    # draft location while the fault is a binder naming a page outside `repo`.
    # ! IT IS THE SAME COMPARISON, ONE STEP EARLIER, so the two guards cannot
    # disagree about what "outside" means.
    source = (repo / rel).resolve()
    if not source.is_relative_to(repo):
        return None, Refusal(
            "read", rel, "names a file outside the repository under review"
        )

    page, why = page_of(source, rel=rel)
    if page is None:
        return None, Refusal("read", rel, why)

    # !! AN ABSENT RECORDED SHA REFUSES; IT DOES NOT PASS. `not recorded` is
    # the first clause on purpose -- a binder page carrying no sha would
    # otherwise compare "" against a real hash, and a future shape that
    # dropped the field would turn this gate off silently rather than loudly.
    # This is also the only check in the tree that catches a reviewer editing
    # the file it was reading: no agent file declares `tools:`, so all six
    # inherit Edit and Write, and "read-only" is prose until this compares.
    if not recorded or page.sha != recorded:
        return None, Refusal(
            "verify",
            rel,
            "the file has changed since it was reviewed -- reviewed at"
            f" {recorded or '<nothing recorded>'}, reads now as {page.sha}",
        )

    placed = galley.reset(page, edits)
    if placed:
        return None, Refusal("edit", rel, "; ".join(placed))

    # !! THE FULL REPO-RELATIVE PATH, NOT JUST THE BASENAME. Measured
    # 2026-08-25: `into / Path(rel).name` flattened `pkg/a/util.py` and
    # `pkg/b/util.py` to the same `<into>/util.py`, so the second page's
    # draft silently overwrote the first's approved text at exit 0.
    # `commands/galley.py`'s `main` already keeps `rel` under its output
    # directory this way -- mirrored here. ! CITED BY NAME, NOT BY LINE: the
    # line that citation carried moved when a guard was inserted above it, and
    # nothing could notice.
    target = (into / rel).resolve()
    # !! REFUSE ANYTHING THAT WOULD LAND OUTSIDE `into`, BEFORE ANY WRITE. A
    # `rel` carrying a `..` segment joins past `into` and, with a matching sha,
    # the draft lands on a file outside the draft directory -- up to and
    # including the source file under review. Measured 2026-08-25: with `rel =
    # "../escape_repo/sub/util.py"`, the join before this check wrote the
    # edited draft onto the source file itself, at exit 0.
    #
    # ! THE READ GUARD ABOVE DOES NOT SUBSUME IT, because `repo` and `into` are
    # different roots at different depths: `sub/../../repo/util.py` resolves
    # INSIDE `repo` and outside `into` when the two are siblings, so the read is
    # legitimate and the draft would still land on the source file.
    if not target.is_relative_to(into):
        return None, Refusal(
            "draft", rel, "would be written outside the draft directory"
        )
    # !! WHAT THE WRITE IS ABOUT TO MAKE, RECORDED BEFORE IT MAKES IT.
    # `compositor.draft` mkdirs with `parents=True`, so this is the last moment
    # at which "did this directory exist already" can be asked. `_discard`
    # removes only what is in this set.
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
    # 2026-08-25. Its mkdir runs before its write, so a write that raised left
    # `<into>/pkg/` behind with no handler that could remove it -- MEASURED
    # with `rel = "pkg/d.py"`: `into.iterdir()` answered `['pkg']`.
    #
    # ! ONE WRITER. `compositor.draft` IS `set_page` plus the mkdir and the
    # `newline=""` write -- load-bearing, since `read_source`'s untranslated
    # read is what `_prove`'s byte-identity comparison depends on. `_one` used
    # to spell those three lines itself, which is two spellings of the only
    # writer: one gets updated and the other does not. The containment refusal
    # above still runs FIRST, so this never writes a target that was not
    # already cleared.
    try:
        compositor.draft(page, target)
        off = _reread(rel, target, edits)
        if off is not None:
            _discard(target, created)
            return None, off

        # !! `read_source`, NOT `read_text`. The translating reader is what this
        # branch exists to remove from the write path -- reading the draft
        # through it here would compare text read one way against text read
        # another.
        unproven = _prove(rel, page.text, read_source(target).text, target)
    except Exception:
        _discard(target, created)
        raise
    if unproven is not None:
        _discard(target, created)
        return None, unproven
    return Drafted(rel, target, page.sha), None


def _reread(rel: str, target: Path, edits: dict[str, str | None]) -> Refusal | None:
    """Read the draft back as a page: is each notation at the cue it was given?

    !! IT IS READ FROM DISK, NOT FROM THE PAGE IN HAND. Roy, 2026-08-24: the
    workflow *"Sends that through the page system again to make certain that
    the agents put the right comments in the right places."* A page still in
    memory would be agreeing with itself -- the shape `docs/gates.md` records
    the round trip scoring 699 of 699 on.

    !! IT ASKS `page_of`, AND INLINED THE SAME FOUR CALLS UNTIL 2026-08-26 --
    without the `Refused` and `READ_ERRORS` handling `_one`'s read has. A draft
    tripping `page_for`'s `raise exceptions.Refused` escaped `run()` as a
    traceback, against its documented `(drafted, []) or ([], refusals)`.
    """
    page, why = page_of(target, rel=rel)
    if page is None:
        return Refusal("reread", rel, f"the draft: {why}")
    # !! COLLECTED AS A LIST PER CUE, BECAUSE A COLLISION IS A REFUSAL AND NOT A
    # LAST-ONE-WINS. This was `{cue_of(b.address).cue: b for b in page ...}`,
    # which keeps the LAST paragraph at a cue two paragraphs share and checks
    # the notation against it -- so a draft holding the approved text at one of
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
            return Refusal("reread", rel, f"{where}: the draft carries no such place")
        if len(found) > 1:
            return Refusal(
                "reread",
                rel,
                f"{where}: {len(found)} paragraphs share this place in the draft,"
                " so no notation can be checked against it",
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
                return Refusal(
                    "reread",
                    rel,
                    f"{where}: was dropped, but the draft holds {got.raw_lines!r}",
                )
            continue
        want = constants.text_lines(replacement)
        if got.raw_lines != want:
            return Refusal(
                "reread",
                rel,
                f"{where}: holds {got.raw_lines!r}, was given {want!r}"
                f"{_elsewhere(page, where, want)}",
            )
    return None


def _elsewhere(page, where: str, want: list[str]) -> str:
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
    `TODO/foot-of-file-two-places.md` -- and reading the notation as
    satisfied because the text is SOMEWHERE would be this step agreeing with
    the edit step instead of checking it.

    Returns:
        `" -- <cue> holds it"`, or "" when no other place does.
    """
    for b in page:
        if not b.address:
            continue
        cue = cue_of(b.address).cue
        if cue != where and b.raw_lines == want:
            return f" -- {cue} holds it"
    return ""


def _prove(rel: str, before: str, after: str, path: Path) -> Refusal | None:
    """Is the executable code in the draft the code that was there before?

    !! AN UNPROVABLE FILE IS REFUSED, NOT PASSED. `code_fingerprint` returns an
    EMPTY fingerprint for a file it cannot strip, and two empty strings compare
    equal -- so reading its verdict without reading its KIND proves every
    unprovable file identical to every other.

    ! WHAT THIS CATCHES THAT `_reread` CANNOT. `_reread` checks only the cues a
    notation named, so a notation surviving it was -- by construction -- read
    back as a comment: for the AST tier a comment never enters the fingerprint,
    so a still-a-COMMENT edit can never trip the `want != got` branch below.

    !! THAT SENTENCE STOOD AS THOUGH IT COVERED ANY STILL-PROSE EDIT, AND IT IS
    FALSE OF A DOCSTRING. `prove_unchanged._blank_docstrings` blanks a
    docstring's CONTENT and keeps its NODE, so its PRESENCE is in the
    fingerprint. MEASURED 2026-08-25 on `tests/conftest.SAMPLE`:
    `{'m.py@a0': None}`, `{'m.py@a1': None}` and an `add` at `a2` each trip
    exactly this branch, with `Refusal('prove', ..., 'the executable code is
    not what it was')`. ! SO `add` AND `drop` -- two of SKILL.md's seven
    verdicts -- CANNOT BE WRITTEN ON A DOCSTRING, and the `undocumented` place
    exists precisely so an `add` can cite one.

    !! IT IS NOT FIXED HERE AND THE FINGERPRINT IS NOT WEAKENED, because a
    docstring's presence is genuinely observable: it binds `__doc__`, and SIX
    modules in this package read `ArgumentParser(description=__doc__)`, so
    ignoring presence would certify a real behaviour change as unchanged.
    Whether the proof stays a blanket one or becomes a diff against the
    APPROVED set is a ruling Roy holds --
    `TODO/the-code-check-refuses-add-and-drop-on-a-docstring.md`, task T1, a
    `*` box. `test_a_docstring_DROP_is_STILL_REFUSED_at_prove` and
    `test_a_docstring_ADD_is_STILL_REFUSED_at_prove`, in
    `TestEveryVerdictThePlacesCanEXPRESSGetsThroughTheChain`, pin what happens
    today.

    The residual hazard this branch is for is a notation that breaks its
    comment's RUN and swallows code BEYOND the edited cue -- an edit whose
    comment run closes mid-line, or never closes at all, can delete the code
    that followed it. `_reread` cannot see that: the swallowed code was never
    one of the cues it was asked about. `_prove` compares the WHOLE file's
    fingerprint, which is what catches it. See
    `TODO/closing-line-deletes-code.md`.
    """
    kind, want = code_fingerprint(before, path)
    got_kind, got = code_fingerprint(after, path)
    if kind == "unprovable" or got_kind == "unprovable":
        return Refusal("prove", rel, "the code in this file cannot be proven unchanged")
    if want != got:
        return Refusal("prove", rel, "the executable code is not what it was")
    return None
