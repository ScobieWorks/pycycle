"""Command‑line interface for PyCycle.

The CLI exposes a single command ``audit`` that takes a root directory and an optional ``--suggest`` flag.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import (
    build_dependency_graph,
    detect_cycles,
    suggest_breaking_imports,
)


def _format_cycle(cycle, import_map):
    lines = []
    for i in range(len(cycle)):
        frm = cycle[i]
        to = cycle[(i + 1) % len(cycle)]
        key = (frm, to)
        if key in import_map:
            for file, line in import_map[key]:
                lines.append(f"  {file}:{line} imports {to}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Detect import cycles in a Python project.")
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="Scan a directory for import cycles.")
    audit.add_argument("root", help="Root directory to scan.")
    audit.add_argument("--suggest", action="store_true", help="Suggest imports to remove to break cycles.")

    args = parser.parse_args(argv)

    if args.command == "audit":
        root = Path(args.root).resolve()
        adjacency, import_map = build_dependency_graph(root)
        cycles = detect_cycles(adjacency)
        if not cycles:
            print("No import cycles detected.")
            sys.exit(0)
        for idx, cycle in enumerate(cycles, 1):
            print(f"Cycle {idx}: {" -> ".join(cycle)}")
            print(_format_cycle(cycle, import_map))
            print()
        if args.suggest:
            suggestions = suggest_breaking_imports(adjacency, import_map)
            if suggestions:
                print("Suggested imports to remove to break all cycles:")
                for frm, to, (file, line) in suggestions:
                    print(f"  {file}:{line}  (import {to} from {frm})")
            else:
                print("No suggestions available.")


if __name__ == "__main__":
    main()
