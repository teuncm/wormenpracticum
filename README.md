# Wormenpracticum

Python rewrite of the UvA Psychobiologie wormenpracticum.

### Requirements

- [uv](http://docs.astral.sh/uv/getting-started/installation/)
- [VSCode](https://code.visualstudio.com/)

### Development

```ini
# Setup
uv sync

# Design UI components
uv run pyside6-designer

# Convert UI components to Python
uv run python -m tools.ui_convert

# Run
uv run python -m main

# Tidy code
uv run ruff check . --fix
```

### Bundling

```ini
# Build (Windows)
.\tools\build.ps1

# Build (Mac/Linux)
./tools/build.sh
```
