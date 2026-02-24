# Wormenpracticum

Python rewrite of the UvA Psychobiologie wormenpracticum.

### Requirements

- [uv](http://docs.astral.sh/uv/getting-started/installation/)
- [VSCode](https://code.visualstudio.com/)

### Development

```ini
# Setup environment
uv sync

# Design UI components
uv run pyside6-designer

# Convert UI components to Python
uv run python -m tools.ui_convert

# Run app
uv run python -m main

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
