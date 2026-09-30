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
