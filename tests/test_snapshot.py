"""
results/latest/ is a bind mount onto the host, so these are about not writing outside
the one directory refresh_latest owns: the guards in both containment directions, the
destination-shape check, symlinks of every kind, and the size caps.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pytest

from src import snapshot
from src.snapshot import refresh_latest, resolve_results_output


def _run_dir(results: Path, name: str = "2026-08-14_181632_cpu") -> Path:
    source = results / "runs" / name
    source.mkdir(parents=True)
    (source / "summary.md").write_text("# Run summary — demo\n\nok\n", encoding="utf-8")
    (source / "manifest.json").write_text('{"run_id": "snapshot content"}', encoding="utf-8")
    return source


def test_comparison_output_must_stay_inside_results_runs(tmp_path):
    expected = tmp_path / "results" / "runs" / "comparison"
    assert resolve_results_output(tmp_path, "results/runs/comparison") == expected

    with pytest.raises(ValueError, match="must be a child"):
        resolve_results_output(tmp_path, "../../host")

    with pytest.raises(ValueError, match="must be a child"):
        resolve_results_output(tmp_path, tmp_path / "README.md")


def test_refresh_latest_writes_readme_and_drops_summary(tmp_path):
    root = tmp_path
    source = root / "run"
    source.mkdir()
    (source / "summary.md").write_text(
        "# Run summary — demo\n\n- **CPU:** 28 threads\n\n## Approach: `baseline`\n\nok\n",
        encoding="utf-8",
    )
    (source / "by_question.md").write_text("q", encoding="utf-8")
    latest = root / "results" / "latest"
    refresh_latest(source, latest)
    readme = (latest / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("<!-- Generated")
    assert "# Latest results — run" in readme
    assert "## Approach: `baseline`" in readme
    assert "- **CPU:** 28 threads" in readme
    assert not (latest / "summary.md").exists()
    assert (latest / "by_question.md").is_file()


def test_refresh_latest_refuses_a_source_containing_the_destination(tmp_path):
    """The repo root as source is what copied the HF cache and results/ into itself."""
    root = tmp_path
    (root / "results").mkdir()
    (root / ".cache" / "huggingface").mkdir(parents=True)
    (root / ".cache" / "huggingface" / "model.safetensors").write_bytes(b"weights")

    with pytest.raises(ValueError, match="inside the source"):
        refresh_latest(root, root / "results" / "latest")

    assert not (root / "results" / "latest").exists()


def test_refresh_latest_copies_no_subdirectory_or_model_weights(tmp_path):
    root = tmp_path
    source = root / "run"
    source.mkdir()
    (source / "summary.md").write_text("# Run summary — demo\n\nok\n", encoding="utf-8")
    (source / "manifest.json").write_text("{}", encoding="utf-8")
    (source / "model.safetensors").write_bytes(b"weights")
    (source / "adapter.gguf").write_bytes(b"weights")
    (source / "nested").mkdir()
    (source / "nested" / "deep.md").write_text("no", encoding="utf-8")

    latest = refresh_latest(source, root / "results" / "latest")

    assert sorted(p.name for p in latest.iterdir()) == ["README.md", "manifest.json"]


def test_export_leaves_no_results_nested_inside_results(tmp_path):
    """Regression: no path under results/ may match results/**/results/**."""
    results = tmp_path / "results"
    source = _run_dir(results)

    refresh_latest(source, results / "latest")

    nested = [p for p in results.rglob("results") if p != results]
    assert nested == [], f"results/ copied into itself: {nested}"


def test_refresh_latest_refuses_transposed_arguments(tmp_path):
    """refresh_latest(run_dir, repo_root) must not rmtree the repo."""
    repo_root = tmp_path / "app"
    source = _run_dir(repo_root / "results")
    (repo_root / "src").mkdir()
    (repo_root / "src" / "run_results.py").write_text("keep me", encoding="utf-8")

    with pytest.raises(ValueError, match="must be a results/latest/ directory"):
        refresh_latest(source, repo_root)

    assert (repo_root / "src" / "run_results.py").read_text(encoding="utf-8") == "keep me"
    assert (source / "summary.md").is_file()


def test_refresh_latest_refuses_a_source_inside_the_destination(tmp_path):
    """Clearing the destination first would delete the source it is about to read."""
    latest = tmp_path / "results" / "latest"
    source = _run_dir(latest)

    with pytest.raises(ValueError, match="source is inside"):
        refresh_latest(source, latest)

    assert (source / "summary.md").is_file()


def test_refresh_latest_leaves_unrelated_files_in_the_destination(tmp_path):
    """Clearing unlinks artifact types, never the directory: no blanket rmtree."""
    results = tmp_path / "results"
    source = _run_dir(results)

    latest = results / "latest"
    latest.mkdir()
    (latest / "stale.json").write_text("{}", encoding="utf-8")
    (latest / "notes.txt.bak").write_text("hand written", encoding="utf-8")
    (latest / "keep_dir").mkdir()

    refresh_latest(source, latest)

    assert not (latest / "stale.json").exists()
    assert (latest / "notes.txt.bak").is_file()
    assert (latest / "keep_dir").is_dir()


def test_refresh_latest_removes_symlinks_of_every_kind(tmp_path):
    """Name and target are irrelevant — no symlink belongs in results/latest/."""
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "keep.txt").write_text("untouched", encoding="utf-8")

    results = tmp_path / "results"
    source = _run_dir(results)
    latest = results / "latest"
    latest.mkdir()
    (latest / "manifest.json").symlink_to(outside_dir / "keep.txt")
    (latest / "unrelated.json").symlink_to(outside_dir / "keep.txt")
    (latest / "weights.safetensors").symlink_to(outside_dir / "keep.txt")
    (latest / "subdir").symlink_to(outside_dir, target_is_directory=True)
    (latest / "dangling.csv").symlink_to(tmp_path / "does_not_exist")

    refresh_latest(source, latest)

    assert [p for p in latest.iterdir() if p.is_symlink()] == []
    assert (outside_dir / "keep.txt").read_text(encoding="utf-8") == "untouched"
    # The link is replaced by the real artifact, not merely removed.
    assert (latest / "manifest.json").read_text(encoding="utf-8") == '{"run_id": "snapshot content"}'
    assert sorted(p.name for p in outside_dir.iterdir()) == ["keep.txt"]


def test_refresh_latest_names_the_residue_it_leaves_behind(tmp_path, caplog):
    """The leave-unrelated-files policy stays; going quiet about it does not."""
    results = tmp_path / "results"
    source = _run_dir(results)
    latest = results / "latest"
    (latest / "results" / "runs").mkdir(parents=True)
    (latest / "notes.bak").write_text("hand written", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger="src.snapshot"):
        refresh_latest(source, latest)

    message = caplog.text
    assert "results/" in message
    assert "notes.bak" in message
    assert "delete them by hand" in message
    # Still left in place, as designed.
    assert (latest / "results").is_dir()
    assert (latest / "notes.bak").is_file()


def test_snapshot_artifacts_sheds_bulk_before_run_identity(tmp_path):
    """The aggregate cap must not drop manifest.json while keeping by_question bulk."""
    source = tmp_path / "run"
    source.mkdir()
    (source / "by_question.json").write_text("x" * 200, encoding="utf-8")
    (source / "manifest.json").write_text("x" * 10, encoding="utf-8")
    (source / "summary.md").write_text("x" * 10, encoding="utf-8")

    kept = snapshot._snapshot_artifacts(source)

    assert [p.name for p in kept][:2] == ["manifest.json", "summary.md"]


def test_snapshot_artifacts_enforces_an_aggregate_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(snapshot, "SNAPSHOT_MAX_TOTAL_BYTES", 10)
    source = tmp_path / "run"
    source.mkdir()
    (source / "a.json").write_text("x" * 8, encoding="utf-8")
    (source / "b.json").write_text("x" * 8, encoding="utf-8")

    kept = snapshot._snapshot_artifacts(source)

    assert [p.name for p in kept] == ["a.json"]


def test_a_symlink_planted_at_the_temp_path_cannot_redirect_the_write(tmp_path, monkeypatch):
    """
    The copy writes through the descriptor mkstemp opened, never through the path.

    Closing that descriptor and reopening the temp file by name only moved the
    write-through window from the destination to the temp path — still inside a
    container-writable bind mount, so still reachable.
    """
    outside = tmp_path / "outside.conf"
    outside.write_bytes(b"ORIGINAL HOST FILE")
    results = tmp_path / "results"
    source = _run_dir(results)

    real_mkstemp = snapshot.tempfile.mkstemp

    def racing_mkstemp(**kwargs):
        fd, name = real_mkstemp(**kwargs)
        os.unlink(name)
        os.symlink(outside, name)
        return fd, name

    monkeypatch.setattr(snapshot.tempfile, "mkstemp", racing_mkstemp)
    refresh_latest(source, results / "latest")

    assert outside.read_bytes() == b"ORIGINAL HOST FILE"


def test_a_crashed_runs_temp_file_is_cleaned_up_not_handed_to_the_user(tmp_path, caplog):
    """A crash between mkstemp and the rename leaves litter this function owns."""
    results = tmp_path / "results"
    source = _run_dir(results)
    latest = results / "latest"
    latest.mkdir(parents=True)
    orphan = latest / ".snapshot-abc123"
    orphan.write_text("half written", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger="src.snapshot"):
        refresh_latest(source, latest)

    assert not orphan.exists()
    assert ".snapshot-abc123" not in caplog.text


def test_a_symlinked_summary_is_not_folded_into_the_readme(tmp_path):
    """read_text follows a link, so a planted summary.md leaks a host file's contents."""
    secret = tmp_path / "host_secret.txt"
    secret.write_text("SUPER SECRET HOST CONTENT", encoding="utf-8")
    results = tmp_path / "results"
    source = _run_dir(results)
    latest = results / "latest"
    latest.mkdir(parents=True)

    real_replace = snapshot._replace_artifact

    def plant_after_copy(src, dest):
        real_replace(src, dest)
        link = latest / "summary.md"
        if not link.is_symlink():
            link.unlink(missing_ok=True)
            link.symlink_to(secret)

    snapshot._replace_artifact = plant_after_copy
    try:
        refresh_latest(source, latest)
    finally:
        snapshot._replace_artifact = real_replace

    assert "SUPER SECRET HOST CONTENT" not in (latest / "README.md").read_text(encoding="utf-8")
    assert secret.read_text(encoding="utf-8") == "SUPER SECRET HOST CONTENT"


def test_a_symlinked_readme_does_not_become_an_arbitrary_host_write(tmp_path):
    """write_text follows a link planted after the clear loop ran."""
    target = tmp_path / "host_file.conf"
    target.write_bytes(b"ORIGINAL HOST FILE")
    results = tmp_path / "results"
    source = _run_dir(results)
    latest = results / "latest"
    latest.mkdir(parents=True)

    real_replace = snapshot._replace_artifact

    def plant_after_copy(src, dest):
        real_replace(src, dest)
        link = latest / "README.md"
        if not link.is_symlink():
            link.unlink(missing_ok=True)
            link.symlink_to(target)

    snapshot._replace_artifact = plant_after_copy
    try:
        refresh_latest(source, latest)
    finally:
        snapshot._replace_artifact = real_replace

    assert target.read_bytes() == b"ORIGINAL HOST FILE"
    assert not (latest / "README.md").is_symlink()
    assert (latest / "README.md").read_text(encoding="utf-8").startswith("<!-- Generated")
