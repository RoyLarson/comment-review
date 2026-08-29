"""B1 -- ISOLATE: the snapshot is taken at a ref, and a mismatch is detectable.

! THE FIXTURE IS THIS REPO, not a constructed one. The trap B1 names -- an
ANNOTATED tag resolving to the tag object rather than the commit -- only exists
where the tags are real, and every tag here is annotated. A repo built in
`tmp_path` for the occasion would be shaped by what this test already expects,
which is the failure `tests/README.md` was written after.
"""

import pathlib
import subprocess

import snapshot_plugin

REPO = pathlib.Path(__file__).resolve().parents[2]

# `v0.2.3` is an annotated tag: the tag object is 6acb9e1, the commit is 3e1fedf.
TAG = "v0.2.3"
TAG_OBJECT = "6acb9e16b83b4b4e5362e9494f4fdfb531bf1946"
TAG_COMMIT = "3e1fedfe20f0da79bc8470a86ac62e7e6756ff18"


def test_an_annotated_tag_resolves_to_its_commit_not_the_tag_object(tmp_path):
    """The trap `isolate-the-codes-contribution` calls the first one anyone hits.

    `git rev-parse v0.2.3` returns the TAG OBJECT. A snapshot recording that as
    its provenance names something that is not a commit, so no later reader can
    diff against it.
    """
    manifest = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")

    assert manifest.commit == TAG_COMMIT
    assert manifest.commit != TAG_OBJECT
    assert manifest.ref == TAG


def test_the_manifest_holds_every_path_git_lists_at_that_commit(tmp_path):
    """The whole plugin travels, and the check is against git rather than a count.

    B1: `agents/` and `scripts/` have to be captured at ONE ref, or the two
    things `isolate-the-codes-contribution` exists to separate are mixed at the
    point of capture. Asserting a NUMBER here would pass a snapshot that took
    the right many of the wrong files.
    """
    manifest = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")

    listed = subprocess.run(
        ["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", TAG_COMMIT,
         "--", snapshot_plugin.PLUGIN_PATH],
        capture_output=True, text=True, check=True,
    ).stdout.split()

    agents = f"{snapshot_plugin.PLUGIN_PATH}/agents/"

    assert sorted(manifest.files) == sorted(listed)
    assert any(p.startswith(agents) for p in manifest.files)
    assert any("/scripts/" in p for p in manifest.files)


def test_an_edited_snapshot_is_detected(tmp_path):
    """The box is PROVING the run used the snapshot, not taking one.

    A run that silently scored a tampered -- or stale -- tree reports a grade
    for something other than the ref it names.
    """
    manifest = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")
    assert snapshot_plugin.verify(manifest) == []

    victim = f"{snapshot_plugin.PLUGIN_PATH}/agents/comment-review-block-context.md"
    path = manifest.root / victim
    path.write_bytes(path.read_bytes() + b"\ntampered\n")

    assert snapshot_plugin.verify(manifest) == [victim]


def test_a_file_removed_from_the_snapshot_is_detected(tmp_path):
    """A missing file is a different code path from a changed one.

    A digest comparison that only walks what is ON DISK cannot see a deletion --
    it is the absence that has to be noticed.
    """
    manifest = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")

    victim = f"{snapshot_plugin.PLUGIN_PATH}/agents/comment-review-block-context.md"
    (manifest.root / victim).unlink()

    assert snapshot_plugin.verify(manifest) == [victim]


def test_a_file_added_to_the_snapshot_is_detected(tmp_path):
    """A fifth agent dropped into the snapshot is a different tree from the ref.

    Walking the manifest alone cannot see this one -- every recorded path still
    matches -- so it is the case that decides whether `verify` answers "is this
    the tree I took" or only "is what I took still here".
    """
    manifest = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")

    intruder = f"{snapshot_plugin.PLUGIN_PATH}/agents/comment-review-fifth-role.md"
    (manifest.root / intruder).write_text("not at this ref\n", encoding="utf-8")

    assert snapshot_plugin.verify(manifest) == [intruder]


def test_the_manifest_survives_the_process_that_wrote_it(tmp_path):
    """B1 says the RUN records the ref, which an in-memory value does not do.

    The grade outlives the session that took it, so the provenance has to be an
    artifact a later reader can open -- and `verify` has to work off that
    reloaded copy, or the check only ever runs where it is least needed.
    """
    manifest = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")
    written = snapshot_plugin.write_manifest(manifest, tmp_path / "snapshot.json")

    reloaded = snapshot_plugin.read_manifest(written)

    assert reloaded == manifest
    assert snapshot_plugin.verify(reloaded) == []

    victim = f"{snapshot_plugin.PLUGIN_PATH}/agents/comment-review-block-context.md"
    (manifest.root / victim).unlink()
    assert snapshot_plugin.verify(reloaded) == [victim]
