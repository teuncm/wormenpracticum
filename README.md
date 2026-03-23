# Wormenpracticum

Python rewrite of the UvA Psychobiologie wormenpracticum.

### Requirements

- [uv](http://docs.astral.sh/uv/getting-started/installation/)
- [VSCode](https://code.visualstudio.com/)

### Development

```ini
# Setup environment
uv sync

# Design UI components visually as .ui files
uv run pyside6-designer

# Convert UI components to Python
# After editing .ui files, regenerate the generated ui_*.py files.
uv run python tools/ui_convert.py

# Run
uv run python -m main

# Test
uv run python -m pytest

# Tidy code
uv run ruff check . --fix
```

### Packaging

```ini
# Build (Windows)
.\tools\build.ps1

# Build (Mac/Linux)
./tools/build.sh
```
