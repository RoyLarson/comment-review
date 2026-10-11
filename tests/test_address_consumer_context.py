import json
from dataclasses import replace
from typing import Any

import pytest
from conftest import SAMPLE, build, run_command

from comment_review.binder.binder import bind
from comment_review.commands import addresser, taken_in
from comment_review.commands import carry as carry_command
from comment_review.flows import reading_context, revise
from comment_review.flows.carry import carry
from comment_review.reading.diagnostics import ReadFailure


def held_tree(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    binder = bind([page], read_from={"root": str(root), "revise": 0})
    return root, page, binder


@pytest.mark.parametrize("args", [[], ["--check"], ["--resolve", "m.py@a1"]])
def test_addresser_refuses_installed_identity_change(
    tmp_path, monkeypatch, capsys, args
):
    _, _, binder = held_tree(tmp_path)
    binder = replace(
        binder,
        pages=(
            replace(
                binder.pages[0],
                reading=replace(binder.pages[0].reading, reader="uninstalled-reader"),
            ),
        ),
    )
    artifact = tmp_path / "binder.json"
    artifact.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    code, out = run_command(
        monkeypatch, capsys, addresser, "--binder", str(artifact), *args
    )
    assert code == 2
    assert "regather" in out
    assert "paragraphs addressed" not in out


def test_direct_line_lookup_refuses_saved_context(tmp_path, capsys):
    _, _, binder = held_tree(tmp_path)
    binder = replace(binder, pages=(replace(binder.pages[0], reading=None),))
    assert addresser._at_line(binder, "m.py", 1, "b") == 2
    assert "regather" in capsys.readouterr().out


@pytest.mark.parametrize("side", ["binder", "page"])
def test_direct_carry_admits_both_in_memory_contexts(tmp_path, side):
    _, page, binder = held_tree(tmp_path)
    if side == "binder":
        binder = replace(binder, pages=(replace(binder.pages[0], reading=None),))
    else:
        page.reading = replace(page.reading, reader="uninstalled-reader")
    updated, added, why = carry(binder, page, "m.py", cue="b99")
    assert updated is None and added == ""
    assert "regather" in why


def test_carry_command_refuses_before_read_or_write(tmp_path, monkeypatch, capsys):
    root, _, binder = held_tree(tmp_path)
    artifact = tmp_path / "binder.json"
    wire = binder.serialize()
    wire["pages"][0]["reading"]["reader"] = "uninstalled-reader"
    original = json.dumps(wire)
    artifact.write_text(original, encoding="utf-8")
    monkeypatch.setattr(
        carry_command, "page_of", lambda *a, **k: pytest.fail("read before admission")
    )
    code, out = run_command(
        monkeypatch,
        capsys,
        carry_command,
        "--binder",
        str(artifact),
        "--repo",
        str(root),
        "--path",
        "m.py",
        "--cue",
        "b99",
    )
    assert code == 2 and "regather" in out
    assert artifact.read_text(encoding="utf-8") == original


@pytest.mark.parametrize("consumer", ["taken_in", "revise"])
@pytest.mark.parametrize("equal", [True, False])
def test_fresh_text_comparison_refuses_reader_change(
    tmp_path, monkeypatch, capsys, consumer, equal
):
    root, _, _ = held_tree(tmp_path)
    revised = tmp_path / "revised"
    revised.mkdir()
    (revised / "m.py").write_text(
        SAMPLE if equal else SAMPLE.replace("beside", "changed"),
        encoding="utf-8",
        newline="",
    )
    installed = reading_context.reader_for
    from comment_review.flows import page_for

    actual = page_for.page_for

    def changed(path):
        selected = installed(path)
        assert selected is not None and not isinstance(selected, ReadFailure)
        definition, binding = selected
        return definition, replace(binding, revision="changed-reader")

    def read_then_change(*args, **kwargs):
        page = actual(*args, **kwargs)
        monkeypatch.setattr(reading_context, "reader_for", changed)
        return page

    monkeypatch.setattr(page_for, "page_for", read_then_change)
    if consumer == "taken_in":
        assert (
            taken_in.main(["--original", str(root), "--revise", str(revised), "m.py"])
            == 0
        )
        seen = capsys.readouterr()
        assert seen.out == ""
        assert "reading-context-mismatch" in seen.err
    else:
        with pytest.raises(revise.AddressesMoved, match="reading-context-mismatch"):
            revise.assert_addresses_held(
                root, revise.Pulled(revised, 1, {}, []), ["m.py"]
            )


def test_pull_refuses_direct_schedule_context_before_output(tmp_path):
    from comment_review.docket.docket import Docket, Schedule

    root, page, _ = held_tree(tmp_path)
    invalid: Any = None
    docket = Docket(
        schedules=(
            Schedule(path="m.py", sha=page.sha, reading=invalid, alterations=()),
        )
    )
    output = tmp_path / "missing-parent" / "revise"
    result = revise.pull(docket, root, output, 1)
    assert result.refusals and "regather" in result.refusals[0].why
    assert not output.parent.exists()


def test_direct_saved_gate_refuses_malformed_context(tmp_path):
    root, _, _ = held_tree(tmp_path)
    invalid: Any = None
    with pytest.raises(revise.AddressesMoved, match="regather"):
        revise.assert_addresses_held(
            root,
            revise.Pulled(root, 1, {}, []),
            ["m.py"],
            reading_contexts={"m.py": invalid},
        )


@pytest.fixture
def installed_modes(monkeypatch):
    actual = reading_context.reader_for

    def selected(path):
        result = actual(path)
        assert result is not None and not isinstance(result, ReadFailure)
        definition, binding = result
        return replace(
            definition, defaults={"mode": "plain"}, choices={"mode": ("plain", "wide")}
        ), binding

    monkeypatch.setattr(reading_context, "reader_for", selected)


@pytest.mark.parametrize("consumer", ["line", "carry", "pull"])
def test_saved_consumers_retain_effective_settings(
    tmp_path, monkeypatch, capsys, installed_modes, consumer
):
    from comment_review.docket.docket import Docket, Schedule
    from comment_review.flows import page_for

    root, page, _ = held_tree(tmp_path)
    saved = reading_context.context_for(root / "m.py", {"mode": "wide"})
    assert not isinstance(saved, ReadFailure)
    page.reading = saved
    binder = bind([page], read_from={"root": str(root), "revise": 0})
    actual = page_for.page_for
    admitted = []

    def observe(*args, **kwargs):
        result = actual(*args, **kwargs)
        if not isinstance(result, ReadFailure):
            admitted.append(result.reading.settings)
        return result

    monkeypatch.setattr(page_for, "page_for", observe)
    if consumer == "line":
        assert addresser._at_line(binder, "m.py", 1, "b") == 0
    elif consumer == "carry":
        artifact = tmp_path / "binder.json"
        artifact.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        empty = next(
            p.address.split("@")[-1]
            for p in page.paragraphs
            if p.address and not p.raw_text.strip()
        )
        code, out = run_command(
            monkeypatch,
            capsys,
            carry_command,
            "--binder",
            str(artifact),
            "--repo",
            str(root),
            "--path",
            "m.py",
            "--cue",
            empty,
        )
        assert code == 0, out
    else:
        docket = Docket(
            schedules=(
                Schedule(path="m.py", sha=page.sha, reading=saved, alterations=()),
            )
        )
        output = tmp_path / "revise"
        result = revise.pull(docket, root, output, 1)
        assert not result.refusals
    assert admitted
    assert all(settings == (("mode", "wide"),) for settings in admitted)


def test_direct_carry_refuses_distinct_compatible_settings(tmp_path, installed_modes):
    root, page, binder = held_tree(tmp_path)
    wide = reading_context.context_for(root / "m.py", {"mode": "wide"})
    assert not isinstance(wide, ReadFailure)
    page.reading = wide
    updated, added, why = carry(binder, page, "m.py", cue="b99")
    assert updated is None and not added
    assert "regather" in why and "differs" in why
