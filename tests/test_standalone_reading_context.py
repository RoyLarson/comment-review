import subprocess
import sys
from dataclasses import replace

import pytest
from conftest import SRC, run_command
from test_proof_command import proof_repository

from comment_review.commands import prove_unchanged as command
from comment_review.flows import page_for, prove_unchanged, reading_context
from comment_review.reading.diagnostics import ReadFailure


@pytest.fixture
def installed_choices(monkeypatch):
    actual = reading_context.reader_for

    def selected(path):
        result = actual(path)
        assert result is not None and not isinstance(result, ReadFailure)
        definition, binding = result
        return (
            replace(
                definition,
                defaults={"mode": "plain"},
                choices={"mode": ("plain", "wide")},
            ),
            binding,
        )

    monkeypatch.setattr(reading_context, "reader_for", selected)
    return selected


def test_standalone_cli_proves_mixed_paths_with_distinct_effective_choices(
    tmp_path, monkeypatch, capsys, installed_choices
):
    repo, js = proof_repository(tmp_path, "const value = 1; // old\r\n")
    py = js.with_suffix(".py")
    py.write_bytes(b"value = 1 # old\r\n")
    subprocess.run(
        ["git", "-C", str(repo), "add", "."],
        check=True,
        capture_output=True,
        timeout=30,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-m",
            "Mixed fixture",
        ],
        check=True,
        capture_output=True,
        timeout=30,
    )
    js.write_bytes(b"const value = 1; // new\r\n")
    py.write_bytes(b"value = 1 # new\r\n")
    settings = tmp_path / "settings.json"
    settings.write_text('{"pkg/source.js":{"mode":"wide"}}', encoding="utf-8")
    actual = page_for.page_for
    admitted = []

    def observe(path, text, *args, **kwargs):
        page = actual(path, text, *args, **kwargs)
        assert not isinstance(page, ReadFailure)
        admitted.append((path, text, page.reading))
        return page

    monkeypatch.setattr(page_for, "page_for", observe)
    code, out = run_command(
        monkeypatch,
        capsys,
        command,
        "--repo",
        str(repo),
        "--base",
        "HEAD",
        "--reading-settings",
        str(settings),
        str(js),
        str(py),
    )
    assert code == 0, out
    assert "PROVEN    pkg/source.js" in out
    assert "PROVEN    pkg/source.py" in out
    assert [item[1] for item in admitted] == [
        "const value = 1; // old\r\n",
        "const value = 1; // new\r\n",
        "value = 1 # old\r\n",
        "value = 1 # new\r\n",
    ]
    assert [item[2].settings for item in admitted] == [
        (("mode", "wide"),),
        (("mode", "wide"),),
        (("mode", "plain"),),
        (("mode", "plain"),),
    ]
    assert admitted[0][2] == admitted[1][2]
    assert admitted[2][2] == admitted[3][2]


@pytest.mark.parametrize("settings", [None, [], {"mode": "unsupported"}])
def test_standalone_flow_refuses_invalid_choices_before_source(
    tmp_path, monkeypatch, installed_choices, settings
):
    repo, target = proof_repository(tmp_path, "const value = 1;\r\n")
    monkeypatch.setattr(
        prove_unchanged,
        "revision_source_of",
        lambda *_: pytest.fail("baseline read before settings refusal"),
    )
    report = prove_unchanged.run(repo, "HEAD", [target], settings={target: settings})
    assert report.failures == 1
    assert "invalid-reading-settings" in " ".join(report.messages)
    assert "PROVEN" not in " ".join(report.messages)


@pytest.mark.parametrize("field", ["settings", "revision", "grammar", "definition"])
def test_standalone_equal_source_refuses_context_change_between_snapshot_reads(
    tmp_path, monkeypatch, installed_choices, field
):
    repo, target = proof_repository(tmp_path, "const value = 1;\r\n")
    before = prove_unchanged.revision_source_of

    def changed(path):
        definition, binding = installed_choices(path)
        if field == "settings":
            definition = replace(definition, defaults={"mode": "wide"})
        elif field == "revision":
            binding = replace(binding, revision="changed")
        elif field == "grammar":
            binding = replace(binding, grammar_identity="changed")
        else:
            definition = replace(definition, revision="changed")
        return definition, binding

    def acquire(*args):
        source = before(*args)
        monkeypatch.setattr(reading_context, "reader_for", changed)
        return source

    monkeypatch.setattr(prove_unchanged, "revision_source_of", acquire)
    monkeypatch.setattr(
        prove_unchanged,
        "code_fingerprint",
        lambda *_: pytest.fail("compared equal text before context admission"),
    )
    report = prove_unchanged.run(repo, "HEAD", [target])
    assert report.failures == 1
    assert "reading-context-mismatch" in " ".join(report.messages)
    assert "PROVEN" not in " ".join(report.messages)


def test_standalone_empty_source_accepts_explicit_settings(tmp_path, installed_choices):
    repo, target = proof_repository(tmp_path, "")
    report = prove_unchanged.run(
        repo, "HEAD", [target], settings={target: {"mode": "wide"}}
    )
    assert report.failures == 0
    assert "PROVEN" in " ".join(report.messages)
    assert report.reading_contexts[target].settings == (("mode", "wide"),)


def test_standalone_other_language_change_does_not_invalidate_selected_path(
    tmp_path, monkeypatch, installed_choices
):
    repo, target = proof_repository(tmp_path, "const value = 1;\r\n")
    before = prove_unchanged.revision_source_of

    def changed(path):
        definition, binding = installed_choices(path)
        return (
            replace(definition, revision="changed")
            if path.suffix == ".py"
            else definition,
            binding,
        )

    def acquire(*args):
        source = before(*args)
        monkeypatch.setattr(reading_context, "reader_for", changed)
        return source

    monkeypatch.setattr(prove_unchanged, "revision_source_of", acquire)
    report = prove_unchanged.run(repo, "HEAD", [target])
    assert report.failures == 0
    assert "PROVEN" in " ".join(report.messages)


@pytest.mark.parametrize(
    "contents,code,message",
    [
        ('{"pkg/source.js":{}}', 0, "PROVEN"),
        ('{"pkg/source.js":{"unknown":"on"}}', 2, "unknown setting"),
        ('{"pkg/source.js":null}', 2, "settings must be an object"),
        (None, 2, "settings.json"),
    ],
)
def test_standalone_process_cli_settings_transport(tmp_path, contents, code, message):
    repo, target = proof_repository(tmp_path, "")
    settings = tmp_path / "settings.json"
    if contents is not None:
        settings.write_text(contents, encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(SRC / "comment-review.py"),
            "prove_unchanged",
            "--repo",
            str(repo),
            "--base",
            "HEAD",
            "--reading-settings",
            str(settings),
            str(target),
        ],
        capture_output=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert result.returncode == code, result.stdout + result.stderr
    assert message in result.stdout + result.stderr
    if code:
        assert "PROVEN" not in result.stdout
