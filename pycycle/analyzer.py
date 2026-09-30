"""Core logic for scanning Python files, building a dependency graph, and detecting cycles.

The module exposes:

* :func:`build_dependency_graph` – Walk a directory tree and parse all ``.py`` files.
* :func:`detect_cycles` – Run Tarjan’s SCC algorithm and return cycles.
* :func:`suggest_breaking_imports` – Return a minimal set of imports that, if removed, would break all cycles.
"""

from __future__ import annotations

import ast
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Type aliases for clarity
ModuleName = str
FilePath = str
ImportInfo = Tuple[FilePath, int]  # (file, line)
Edge = Tuple[ModuleName, ModuleName]


def _module_name_from_path(root: Path, file_path: Path) -> ModuleName:
    """Convert a file path to a dotted module name relative to *root*.

    ``__init__.py`` files are treated as the package name of the directory.
    """
    rel = file_path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _resolve_relative_import(current: ModuleName, level: int, module: str | None) -> ModuleName | None:
    """Resolve a relative import to an absolute module name.

    ``level`` is the number of leading dots. ``module`` is the dotted name after the dots.
    Returns ``None`` if the import refers to the current package (e.g. ``from . import x``).
    """
    parts = current.split(".")
    if level > len(parts):
        # Import goes above the root package – ignore
        return None
    base = parts[: -level]
    if module:
        base += module.split(".")
    if not base:
        return None
    return ".".join(base)


def build_dependency_graph(root: str | Path) -> Tuple[Dict[ModuleName, Set[ModuleName]], Dict[Edge, List[ImportInfo]]]:
    """Walk *root* and build a dependency graph.

    Returns a tuple ``(adjacency, import_map)`` where:
    * ``adjacency`` maps a module to the set of modules it imports.
    * ``import_map`` maps an edge (from, to) to a list of ``(file, line)`` tuples.
    """
    root = Path(root).resolve()
    adjacency: Dict[ModuleName, Set[ModuleName]] = defaultdict(set)
    import_map: Dict[Edge, List[ImportInfo]] = defaultdict(list)

    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            file_path = Path(dirpath) / filename
            try:
                source = file_path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(file_path))
            except Exception:
                # Skip files that cannot be parsed
                continue
            module = _module_name_from_path(root, file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        target = alias.name
                        adjacency[module].add(target)
                        import_map[(module, target)].append((str(file_path), node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0:
                        # Absolute import
                        target = node.module or ""
                        if target:
                            adjacency[module].add(target)
                            import_map[(module, target)].append((str(file_path), node.lineno))
                    else:
                        resolved = _resolve_relative_import(module, node.level, node.module)
                        if resolved:
                            adjacency[module].add(resolved)
                            import_map[(module, resolved)].append((str(file_path), node.lineno))
    return adjacency, import_map


def _tarjan_scc(graph: Dict[ModuleName, Set[ModuleName]]) -> List[List[ModuleName]]:
    """Return a list of strongly connected components (SCCs)."""
    index = 0
    indices: Dict[ModuleName, int] = {}
    lowlink: Dict[ModuleName, int] = {}
    stack: List[ModuleName] = []
    result: List[List[ModuleName]] = []

    def strongconnect(v: ModuleName):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)

        for w in graph.get(v, []):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            component: List[ModuleName] = []
            while True:
                w = stack.pop()
                component.append(w)
                if w == v:
                    break
            result.append(component)

    for node in graph:
        if node not in indices:
            strongconnect(node)
    return result


def detect_cycles(adjacency: Dict[ModuleName, Set[ModuleName]]) -> List[List[ModuleName]]:
    """Return a list of cycles, each represented as a list of module names.

    Only SCCs with more than one node or a self‑loop are considered cycles.
    """
    sccs = _tarjan_scc(adjacency)
    cycles: List[List[ModuleName]] = []
    for comp in sccs:
        if len(comp) > 1:
            cycles.append(comp)
        elif len(comp) == 1:
            node = comp[0]
            if node in adjacency.get(node, set()):
                cycles.append(comp)
    return cycles


def suggest_breaking_imports(adjacency: Dict[ModuleName, Set[ModuleName]], import_map: Dict[Edge, List[ImportInfo]]) -> List[Tuple[ModuleName, ModuleName, ImportInfo]]:
    """Return a list of imports that, if removed, would break all cycles.

    The algorithm is a simple heuristic: for each cycle, pick the first edge in the cycle.
    """
    cycles = detect_cycles(adjacency)
    suggestions: List[Tuple[ModuleName, ModuleName, ImportInfo]] = []
    for cycle in cycles:
        # Pick the first edge in the cycle order
        for i in range(len(cycle)):
            frm = cycle[i]
            to = cycle[(i + 1) % len(cycle)]
            edge = (frm, to)
            if edge in import_map:
                # Take the first import occurrence
                info = import_map[edge][0]
                suggestions.append((frm, to, info))
                break
    return suggestions
