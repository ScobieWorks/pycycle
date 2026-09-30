"""Unit tests for the core analyzer logic."""

import os
import tempfile
import textwrap
from pathlib import Path

from pycycle.analyzer import (
    build_dependency_graph,
    detect_cycles,
    suggest_breaking_imports,
)


def create_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_cycle_detection(tmp_path: Path) -> None:
    # Create a simple cycle: a.b -> a.c -> a.b
    create_file(tmp_path / "a" / "b.py", "import a.c")
    create_file(tmp_path / "a" / "c.py", "import a.b")

    adjacency, _ = build_dependency_graph(tmp_path)
    cycles = detect_cycles(adjacency)
    assert len(cycles) == 1
    cycle = cycles[0]
    assert set(cycle) == {"a.b", "a.c"}


def test_suggest_breaking_imports(tmp_path: Path) -> None:
    # Same cycle as above
    create_file(tmp_path / "a" / "b.py", "import a.c")
    create_file(tmp_path / "a" / "c.py", "import a.b")

    adjacency, import_map = build_dependency_graph(tmp_path)
    suggestions = suggest_breaking_imports(adjacency, import_map)
    # Expect one suggestion per cycle
    assert len(suggestions) == 1
    frm, to, (file, line) = suggestions[0]
    assert frm in {"a.b", "a.c"}
    assert to in {"a.b", "a.c"}
    assert file.endswith("b.py") or file.endswith("c.py")


def test_no_cycle(tmp_path: Path) -> None:
    create_file(tmp_path / "x.py", "print('hello')")
    adjacency, _ = build_dependency_graph(tmp_path)
    cycles = detect_cycles(adjacency)
    assert cycles == []

