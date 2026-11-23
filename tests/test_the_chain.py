"""The middle-to-write chain, driven end to end by commands and nothing else.

`P61`, and the verify text of `TODO/no-command-for-the-middle.md` T1, with
stage 2 under its current name: *"with the filled edit_copies of a stage on
disk, the chain gather -> seed -> collate -> <this> -> proof runs with no Python
written by hand."*

!! The `<this>` is gone, which is what T1 was open for. `collate` wrote the copy
chief's `edit_copy` and `proof` read a docket, and nothing turned one into the
other -- `commands/proof.py` would refuse the one given the other. Since `P57`
the transcribe is the proof flow's first step, so the chain is four commands
with no step between them.

!! What this file may and may not do. Every stage runs through that command's
own `main()` over `sys.argv` -- the console face, argument parsing included --
because that is the only thing that catches an argparse flag the body reads
under a different name. `conftest.run_command` is what does it, and its own
docstring carries the measurement.

! The one thing written by hand is a role's ruling, and it has to be: no command
fills a mark, because a reviewer does. `TODO/no-command-for-the-middle.md` T10
is the mark-edit command that would remove even that.

! It is a `backend` test. `docs/lanes.md` files a test under the lane that owns
what it asks, and this asks whether these commands compose -- not whether a role
behaves, which is `agents`', nor how well a run scores, which is `testing`'s.
"""

import json

from conftest import SAMPLE, run_command
from helpers import a_clean, a_correct

from comment_review.commands import collate as collate_command
from comment_review.commands import distribute as distribute_command
from comment_review.commands import gather as gather_command
from comment_review.commands import proof as proof_command

#: The four editorial roles, in the order stage 4 dispatches them -- one alone,
#: then three. This test runs the all-at-once topology, where a single stage
#: carries all four, because it is the one shape needing no revise between
#: stages.
ROLES = (
    "ownership-context",
    "block-context",
    "function-context",
    "module-context",
)


class TestTheChainRunsOnCommandsAlone:
    def test_gather_to_distribute_to_collate_to_proof(
        self, tmp_path, monkeypatch, capsys
    ):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")

        # 1 Gather -- the binder every copy is seeded from.
        binder_path = tmp_path / "binder.json"
        # ! The path is absolute, which `--repo` still accepts: `gather` joins
        # each positional path to `--repo`, and joining an absolute path
        # leaves it as given.
        code, out = run_command(
            monkeypatch,
            capsys,
            gather_command,
            "--repo",
            str(repo),
            "--out",
            str(binder_path),
            str(repo / "m.py"),
        )
        assert code == 0, out
        binder = json.loads(binder_path.read_text(encoding="utf-8"))
        page = binder["pages"][0]
        # ! A row carries its `cue`, not its address. The two are rejoined as
        # `path@cue` when a page is read back, so a test reading the wire form
        # has to rejoin them the same way.
        # ! A comment place, `b` or `c`, first. The file's own matter gets no
        # seeded slot, so `f0` is not a place a role can rule on; and the
        # placeholder change below is a `#` line, which a docstring's place
        # cannot hold.
        addresses = sorted(
            (f"{page['path']}@{row['cue']}" for row in page["rows"]),
            key=lambda a: a.split("@")[-1][0] not in "bc",
        )
        assert addresses, "the gather carried no addressed place to rule on"

        # 2 Mark -- one seeded copy per role, then a ruling written into one.
        copies = []
        for role in ROLES:
            where = tmp_path / f"{role}.json"
            code, out = run_command(
                monkeypatch,
                capsys,
                distribute_command,
                "--seed",
                "--binder",
                str(binder_path),
                "--role",
                role,
                "--out",
                str(where),
            )
            assert code == 0, out
            copies.append(where)

        # !! Every role rules on every place it was handed. A slot left untouched
        # is a coverage problem and `collate` exits nonzero naming it -- "handed
        # to this role and not ruled on" -- which is the check that stops a role
        # answering one place of three and the run reporting OK. `clean` is the
        # ruling for a place with nothing to report; it is one of the seven.
        # ! The read and the write are the caller's, so the two rulings compose
        # in memory. Each used to do its own read-modify-write, which made the
        # order a silent dependency: running the correction alone, or before the
        # cleans, failed only at runtime inside a slot search.
        # !! Every role returns the same correction, since `Process: #89`. One
        # role correcting while three stay clean is a lone mark, and the fold
        # sends it back to the three for a read -- a turn no console command
        # runs yet. Four roles carrying one text agree at the first fold
        # (`#88`), which is what lets this chain finish on commands alone.
        for one in copies:
            document = json.loads(one.read_text(encoding="utf-8"))
            _rule_every_place(document)
            _correct_one_place(document, addresses[0])
            one.write_text(json.dumps(document), encoding="utf-8", newline="")

        # 3 Collate -- the four returned copies folded into a master proof.
        closed = tmp_path / "closed.json"
        argv = ["--stage", "4c", "--binder", str(binder_path)]
        for one in copies:
            argv += ["--edit-copy", str(one)]
        code, out = run_command(
            monkeypatch, capsys, collate_command, *argv, "--proof-out", str(closed)
        )
        assert code == 0, out
        assert closed.exists()

        # 4 Proof -- the master proof, transcribed and set into a revise.
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--proof",
            str(closed),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 0, out

        # !! The page must have changed, not merely exist. `pull` copies the
        # whole tree before it sets anything, so asserting the file is present
        # would pass over an empty docket -- measured on this branch, in
        # `tests/test_proof_command.py`.
        drafted = (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")
        assert drafted != SAMPLE
        # ! And the checkout is untouched, which is the whole promise of a revise.
        assert (repo / "m.py").read_text(encoding="utf-8") == SAMPLE


def _cited() -> list[dict]:
    """A source inside this run's own repo: the page's first line.

    !! The cite must resolve inside the run's own repo. The helpers' marks
    cite `src/comment_review/desk/proof/mark.py`, which is real in this
    checkout and absent from a tmp tree, and `collate` resolves a cite
    against the binder's `read_from.root`.
    """
    return [{"cite": "m.py:1", "verbatim": SAMPLE.splitlines()[0]}]


def _rule_every_place(document: dict) -> None:
    """`clean` in every seeded slot -- this role read the page and reports nothing.

    !! This and `_correct_one_place` are the hand-written step, and it is the
    only one. A mark is a reviewer's act, so no command fills one --
    `TODO/no-command-for-the-middle.md` T10 is the command that would. What they
    must not do is build the copy: the slots come from `distribute --seed`, and
    these fill them.
    """
    for sheet in document["sheets"]:
        for slot in sheet["marks"]:
            slot.update(a_clean(slot["address"]), sources=_cited())


def _correct_one_place(document: dict, address: str) -> None:
    """Turn one of that copy's `clean` slots into the `correct` the revise sets.

    ! The quoted sentence is the page's own. `a_correct` seeds a placeholder,
    and a claim quoting a sentence the paragraph does not hold is what
    `verify_report` refuses -- so `claim.false` is read off the slot the seed
    already carried.
    """
    for sheet in document["sheets"]:
        for slot in sheet["marks"]:
            if slot["address"] != address:
                continue
            mark = a_correct(address)
            mark["claim"] = {
                "false": (slot.get("raw_text") or "").strip().splitlines()[0],
                "true": "the corrected sentence",
            }
            mark["sources"] = _cited()
            mark["change"] = "# set by the chain test\n"
            slot.update(mark)
            return
    raise AssertionError(f"{address} is not a slot in this copy")
