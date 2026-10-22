"""Supplementary POSIX checks run by linux_cpu_verify.py against the accepted baseline source.

They are kept out of tests/ because the baseline commit under test must stay exactly as accepted. Each test
asserts that a primitive the CPU baseline relies on really exists and behaves on Linux. On Windows they skip.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap

import pytest

pytestmark = pytest.mark.skipif(os.name == "nt", reason="POSIX-only primitives")


def test_fcntl_flock_backs_the_journal_lock():
    from granthstudio import comfy
    import fcntl
    assert comfy._try_lock.__globals__["fcntl"] is fcntl            # the POSIX branch of comfy.owned is the one in use
    assert not hasattr(comfy, "msvcrt")


def test_dir_fd_primitives_exist_for_reference_creation():
    assert os.open in os.supports_dir_fd and os.mkdir in os.supports_dir_fd and os.unlink in os.supports_dir_fd
    assert hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY")


def test_flock_excludes_a_second_real_process(tmp_path):
    from granthstudio.comfy import owned
    journal = tmp_path / "job.json"
    child = textwrap.dedent("""
        import sys, pathlib
        from granthstudio.comfy import owned
        from granthstudio.errors import JobPending
        try:
            with owned(pathlib.Path(sys.argv[1]), wait_s=0.3):
                print("ACQUIRED")
        except JobPending:
            print("REFUSED")
    """)
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)}
    with owned(journal):
        held = subprocess.run([sys.executable, "-c", child, str(journal)], capture_output=True, text=True, env=env, timeout=60)
    free = subprocess.run([sys.executable, "-c", child, str(journal)], capture_output=True, text=True, env=env, timeout=60)
    assert held.stdout.strip() == "REFUSED", held
    assert free.stdout.strip() == "ACQUIRED", free


def test_symlink_creation_is_possible_and_refused_by_reference_import(tmp_path):
    from granthstudio.errors import ConfigError
    from granthstudio.integrity import create_new_file
    root, outside = tmp_path / "root", tmp_path / "outside"
    root.mkdir(); outside.mkdir()
    (root / "references").symlink_to(outside, target_is_directory=True)
    source = tmp_path / "s.png"; source.write_bytes(b"x")
    with pytest.raises(ConfigError):
        create_new_file(root, "references/ref_a/v1/image.png", source)
    assert list(outside.iterdir()) == []


def test_dangling_symlink_at_the_destination_is_not_followed(tmp_path):
    from granthstudio.errors import ConfigError
    from granthstudio.integrity import create_new_file
    root, outside = tmp_path / "root", tmp_path / "outside"
    (root / "d").mkdir(parents=True); outside.mkdir()
    (root / "d" / "image.png").symlink_to(outside / "created_through_link.png")      # dangling
    source = tmp_path / "s.png"; source.write_bytes(b"x")
    with pytest.raises(ConfigError):
        create_new_file(root, "d/image.png", source)
    assert list(outside.iterdir()) == []
