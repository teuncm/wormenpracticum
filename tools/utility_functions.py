import sys
from pathlib import Path

# Project root directory for development and PyInstaller bundle.
PROJECT_ROOT_DIR = Path(
    getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
)


def resolve_project(relative_path):
    """Resolve a path relative to the project root."""
    return str(PROJECT_ROOT_DIR / relative_path)
