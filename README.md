# PyCycle

PyCycle is a small, offline command‑line tool that scans a Python codebase for import cycles, reports them, and optionally suggests minimal import removals to break the cycles.

## Installation

```bash
pip install git+https://github.com/ScobieWorks/pycycle.git
```

## Usage

```bash
# Scan the current directory for import cycles
pycycle audit .

# Scan and get a list of imports that can be removed to break all cycles
pycycle audit . --suggest
```

## Output

For each detected cycle, PyCycle prints:

* The sequence of modules involved.
* The file paths and line numbers where the imports occur.

When `--suggest` is used, it also prints a list of imports that, if removed, would break all cycles.

## License

MIT License


## Support

If this project saved you time, optional support is welcome: https://paypal.me/Damonwill

<!-- ORION_MONETIZATION_PILOT_START -->

## Python Circular Dependency Audit — Pilot

Using PyCycle on a real Python codebase and want help interpreting the dependency
cycles it finds? For a limited 7-day pilot, ScobieWorks is testing a fixed-scope
**Python Circular Dependency Audit for $149**.

### What the audit includes

- Review of PyCycle results for one Python project
- Prioritized circular-dependency findings and practical break points
- Refactoring recommendations
- Short architecture/remediation summary
- Suggested CI check to help prevent new dependency cycles

A public repository or sanitized PyCycle output can be used for the review.
You do not need to provide credentials or private repository access.

### Pilot scope

- One project and one analysis pass
- Up to two hours of review
- No guaranteed code remediation
- No hosting or SLA
- $149 is an experimental pilot price, not an established market price

Interested in the pilot? Open a GitHub issue in this repository with the title:

**PyCycle Audit Pilot**

Do not include credentials, secrets, or sensitive/private source code in the issue.

<!-- ORION_MONETIZATION_PILOT_END -->
