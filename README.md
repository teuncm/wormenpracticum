# Wormenpracticum

Python rewrite of the UvA Psychobiologie wormenpracticum.

### Requirements

- [uv](http://docs.astral.sh/uv/getting-started/installation/)
- [VSCode (recommended)](https://code.visualstudio.com/)

### Development

```ini
# Setup
uv sync

# Design UI components
uv run pyside6-designer

# Convert UI components to Python
uv run python -m tools.ui_convert

# Run
uv run main.py

# Build (Windows)
.\tools\build.ps1

# Tidy code
uv run ruff check . --fix
```
