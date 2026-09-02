"""The middle-to-write chain, driven end to end by commands and nothing else.

`P61`, and the verify text of `TODO/no-command-for-the-middle.md` T1 word for
word: *"with the filled edit_copies of a stage on disk, the chain census -> seed
-> collate -> <this> -> proof runs with no Python written by hand."*

!! THE `<this>` IS GONE, WHICH IS WHAT T1 WAS OPEN FOR. `collate` wrote the copy
chief's `edit_copy` and `proof` read a docket, and nothing turned one into the
other -- `commands/proof.py` would refuse the one given the other. Since `P57`
the transcribe is the proof flow's first step, so the chain is FOUR commands
with no step between them.

!! WHAT THIS FILE MAY AND MAY NOT DO. Every stage runs through that command's
own `main()` over `sys.argv` -- the console face, argument parsing included --
because that is the only thing that catches an argparse flag the body reads
under a different name. `conftest.run_command` is what does it, and its own
docstring carries the measurement.

! THE ONE THING WRITTEN BY HAND IS A ROLE'S RULING, and it has to be: no command
fills a mark, because a REVIEWER does. `TODO/no-command-for-the-middle.md` T10
is the mark-edit command that would remove even that.

! IT IS A `backend` TEST. `docs/lanes.md` files a test under the lane that owns
what it ASKS, and this asks whether these commands compose -- not whether a role
behaves, which is `agents`', nor how well a run scores, which is `testing`'s.
"""

import json

from conftest import SAMPLE, run_command
from helpers import a_clean, a_correct

from comment_review.commands import census as census_command
from comment_review.commands import collate as collate_command
from comment_review.commands import distribute as distribute_command
from comment_review.commands import proof as proof_command

#: The four editorial roles, in the order stage 4 dispatches them -- one alone,
#: then three. This test runs the ALL-AT-ONCE topology, where a single stage
#: carries all four, because it is the one shape needing no revise between
#: stages.
ROLES = (
    "ownership-context",
    "block-context",
    "function-context",
    "module-context",
)


class TestTheChainRunsOnCommandsAlone:
    def test_census_to_distribute_to_collate_to_proof(
        self, tmp_path, monkeypatch, capsys
    ):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")

        # 1 GATHER -- the binder every copy is seeded from.
        binder_path = tmp_path / "binder.json"
        # ! THE PATH IS ABSOLUTE. `census` resolves its positional paths against
        # the CWD and not against `--repo`, so a bare `m.py` matches no file and
        # the run errors -- "1 of 0 files handed in were not censused".
        code, out = run_command(
            monkeypatch,
            capsys,
            census_command,
            "--repo",
            str(repo),
            "--json",
            "--out",
            str(binder_path),
            str(repo / "m.py"),
        )
        assert code == 0, out
        binder = json.loads(binder_path.read_text(encoding="utf-8"))
        page = binder["pages"][0]
        # ! A ROW CARRIES ITS `cue`, NOT ITS ADDRESS. The two are rejoined as
        # `path@cue` when a page is read back, so a test reading the wire form
        # has to rejoin them the same way.
        addresses = [f"{page['path']}@{row['cue']}" for row in page["rows"]]
        assert addresses, "the census carried no addressed place to rule on"

        # 2 MARK -- one seeded copy per role, then a ruling written into one.
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

        # !! EVERY ROLE RULES ON EVERY PLACE IT WAS HANDED. A slot left untouched
        # is a COVERAGE problem and `collate` exits nonzero naming it -- "handed
        # to this role and not ruled on" -- which is the check that stops a role
        # answering one place of three and the run reporting OK. `clean` is the
        # ruling for a place with nothing to report; it is one of the seven.
        # ! THE READ AND THE WRITE ARE THE CALLER'S, so the two rulings compose
        # in memory. Each used to do its own read-modify-write, which made the
        # ORDER a silent dependency: running the correction alone, or before the
        # cleans, failed only at runtime inside a slot search.
        for one in copies:
            document = json.loads(one.read_text(encoding="utf-8"))
            _rule_every_place(document)
            if one is copies[0]:
                _correct_one_place(document, addresses[0])
            one.write_text(json.dumps(document), encoding="utf-8", newline="")

        # 3 COLLATE -- the four returned copies folded into the chief's.
        chief = tmp_path / "chief.json"
        argv = ["--stage", "4c", "--binder", str(binder_path)]
        for one in copies:
            argv += ["--edit-copy", str(one)]
        code, out = run_command(
            monkeypatch, capsys, collate_command, *argv, "--out", str(chief)
        )
        assert code == 0, out
        assert chief.exists()

        # 4 PROOF -- the chief's copy, transcribed and set into a revise.
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--copy",
            str(chief),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 0, out

        # !! THE PAGE MUST HAVE CHANGED, not merely exist. `pull` copies the
        # whole tree before it sets anything, so asserting the file is present
        # would pass over an empty docket -- measured on this branch, in
        # `tests/test_proof_command.py`.
        drafted = (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")
        assert drafted != SAMPLE
        # ! AND THE CHECKOUT IS UNTOUCHED, which is the whole promise of a revise.
        assert (repo / "m.py").read_text(encoding="utf-8") == SAMPLE


def _rule_every_place(document: dict) -> None:
    """`clean` in every seeded slot -- this role read the page and reports nothing.

    !! THIS AND `_correct_one_place` ARE THE HAND-WRITTEN STEP, AND IT IS THE
    ONLY ONE. A mark is a REVIEWER's act, so no command fills one --
    `TODO/no-command-for-the-middle.md` T10 is the command that would. What they
    must not do is BUILD the copy: the slots come from `distribute --seed`, and
    these fill them.
    """
    for sheet in document["sheets"]:
        for slot in sheet["marks"]:
            slot.update(a_clean(slot["address"]))


def _correct_one_place(document: dict, address: str) -> None:
    """Turn one of that copy's `clean` slots into the `correct` the revise sets.

    ! THE QUOTED SENTENCE IS THE PAGE'S OWN. `a_correct` seeds a placeholder,
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
            # !! THE CITE MUST RESOLVE INSIDE THIS RUN'S OWN REPO. `a_correct`
            # seeds one naming `src/comment_review/desk/mark.py`, which is real
            # in this checkout and absent from a tmp tree -- and `collate`
            # resolves a cite against the binder's `read_from.root`, so it
            # reports "does not resolve -- the file cannot be read" and exits
            # nonzero. Source verification is doing its job; the fixture was
            # pointing outside the world the run was given.
            mark["sources"] = [{"cite": "m.py:1", "verbatim": SAMPLE.splitlines()[0]}]
            mark["change"] = "# set by the chain test\n"
            slot.update(mark)
            return
    raise AssertionError(f"{address} is not a slot in this copy")
