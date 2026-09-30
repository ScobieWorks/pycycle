"""Integration tests for the CLI."""

import subprocess
import sys
import textwrap
from pathlib import Path


def run_cli(args, cwd):
    result = subprocess.run(
        [sys.executable, "-m", "pycycle.cli"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result


def test_cli_no_cycles(tmp_path):
    # Simple file with no imports
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")
    res = run_cli(["audit", "."], tmp_path)
    assert res.returncode == 0
    assert "No import cycles detected." in res.stdout


def test_cli_detect_cycle(tmp_path):
    # Create a cycle a.b -> a.c -> a.b
    (tmp_path / "a" / "b.py").write_text("import a.c", encoding="utf-8")
    (tmp_path / "a" / "c.py").write_text("import a.b", encoding="utf-8")
    res = run_cli(["audit", "."], tmp_path)
    assert res.returncode == 0
    assert "Cycle 1:" in res.stdout
    assert "a.b" in res.stdout and "a.c" in res.stdout


def test_cli_suggest(tmp_path):
    (tmp_path / "a" / "b.py").write_text("import a.c", encoding="utf-8")
    (tmp_path / "a" / "c.py").write_text("import a.b", encoding="utf-8")
    res = run_cli(["audit", ".", "--suggest"], tmp_path)
    assert res.returncode == 0
    assert "Suggested imports to remove" in res.stdout
    assert "import a.c" in res.stdout or "import a.b" in res.stdout

