import sys
from pathlib import Path

# Project root directory for PyInstaller bundle.
PROJECT_ROOT_DIR = Path(
    getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2])
)


def resource_path(relative_path):
    """Resolve a path to a project resource (relative to the project root)."""
    return str(PROJECT_ROOT_DIR / relative_path)
