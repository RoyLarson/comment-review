"""The rig: lay a variant over a snapshot, run, reset, load the next theory.

`decision-log.md Process: #53` -- the harness is a rig theories are loaded into,
not a comparison of two tags. `Vocabulary: #30` -- the copied-in set is a
`variant`.

!! WHAT THESE TESTS ARE REALLY ABOUT IS THE PROVENANCE. A variant is a DECLARED
mismatch, so `verify` has to keep reporting the undeclared ones. If declaring a
variant switched the tamper check off, the rig would re-create
`marketplace-resolves-live` on purpose -- a run whose tree is not the tree it
names.
"""

import pathlib

import snapshot_plugin

REPO = pathlib.Path(__file__).resolve().parents[2]

TAG = "v0.2.3"
ROLE = "plugins/comment-review/agents/comment-review-block-context.md"
OTHER = "plugins/comment-review/agents/comment-review-module-context.md"


def theory(tmp_path, text: str) -> pathlib.Path:
    """A file standing in for a hand-edited role, outside the snapshot."""
    written = tmp_path / "theory.md"
    written.write_text(text, encoding="utf-8")
    return written


def test_a_variant_is_laid_down_and_declared(tmp_path):
    """The point of the rig: the run reads the theory, not the base."""
    base = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")
    loaded = snapshot_plugin.overlay(base, {ROLE: theory(tmp_path, "a new remit\n")})

    assert (loaded.root / ROLE).read_text(encoding="utf-8") == "a new remit\n"
    assert ROLE in loaded.variant
    assert snapshot_plugin.verify(loaded) == []


def test_the_base_manifest_still_calls_that_file_changed(tmp_path):
    """Declaring is what makes a variant legible -- the bytes alone do not.

    The SAME tree is clean against the manifest that declared the variant and
    dirty against the one that did not. That is the whole distinction between a
    theory and tampering, and it has to be visible from the record.
    """
    base = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")
    snapshot_plugin.overlay(base, {ROLE: theory(tmp_path, "a new remit\n")})

    assert snapshot_plugin.verify(base) == [ROLE]


def test_an_undeclared_change_beside_a_variant_is_still_caught(tmp_path):
    """Loading a theory must not switch the tamper check off for everything else."""
    base = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")
    loaded = snapshot_plugin.overlay(base, {ROLE: theory(tmp_path, "a new remit\n")})

    meddled = loaded.root / OTHER
    meddled.write_bytes(meddled.read_bytes() + b"\nnobody declared this\n")

    assert snapshot_plugin.verify(loaded) == [OTHER]


def test_a_variant_edited_after_it_was_declared_is_caught(tmp_path):
    """A declared path is pinned to the bytes DECLARED, not exempted from checking."""
    base = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")
    loaded = snapshot_plugin.overlay(base, {ROLE: theory(tmp_path, "a new remit\n")})

    (loaded.root / ROLE).write_text("quietly something else\n", encoding="utf-8")

    assert snapshot_plugin.verify(loaded) == [ROLE]


def test_a_variant_may_add_a_file_the_ref_never_had(tmp_path):
    """A fifth role is a theory too, and B1 reports an added file as a mismatch."""
    base = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")
    fifth = "plugins/comment-review/agents/comment-review-fifth-role.md"

    loaded = snapshot_plugin.overlay(base, {fifth: theory(tmp_path, "a fifth hand\n")})

    assert (loaded.root / fifth).is_file()
    assert snapshot_plugin.verify(loaded) == []
    assert snapshot_plugin.verify(base) == [fifth]


def test_reset_returns_the_rig_to_the_ref(tmp_path):
    """"Reset and run a new theory" -- the next run must not inherit the last one.

    ! A FILE THE VARIANT ADDED IS THE CASE THAT DECIDES THIS. Re-extracting over
    the directory would leave it behind, and the next theory would be graded on
    a tree carrying the previous one's fifth role.
    """
    base = snapshot_plugin.snapshot(REPO, TAG, tmp_path / "snap")
    fifth = "plugins/comment-review/agents/comment-review-fifth-role.md"
    loaded = snapshot_plugin.overlay(
        base, {ROLE: theory(tmp_path, "a new remit\n"), fifth: theory(tmp_path, "5\n")}
    )

    clean = snapshot_plugin.reset(REPO, loaded)

    assert clean.variant == {}
    assert not (clean.root / fifth).exists()
    assert clean.files == base.files
    assert snapshot_plugin.verify(clean) == []
