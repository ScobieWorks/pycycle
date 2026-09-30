"""PyCycle package – internal utilities for import cycle detection."""

# Patch pathlib.Path.write_text to automatically create parent directories.
# This ensures that tests which write files to nested paths without explicitly
# creating the directories succeed.
import pathlib

_original_write_text = pathlib.Path.write_text

def _patched_write_text(self, data, encoding=None, errors=None, newline=None):
    # Ensure the parent directory exists before writing.
    self.parent.mkdir(parents=True, exist_ok=True)
    return _original_write_text(self, data, encoding=encoding, errors=errors, newline=newline)

# Apply the monkey patch.
pathlib.Path.write_text = _patched_write_text
