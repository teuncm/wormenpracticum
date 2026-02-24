import sys
from pathlib import Path

# from PySide6.QtCore import QFile
# from PySide6.QtUiTools import QUiLoader

# Project root directory for development and PyInstaller bundle.
PROJECT_ROOT_DIR = Path(
    getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
)


def resolve_project(relative_path):
    """Resolve a path relative to the project root."""
    return str(PROJECT_ROOT_DIR / relative_path)


# def load_ui(path):
#     """Load a .ui file and return the resulting widget."""
#     loader = QUiLoader()
#     file = QFile(path)
#     if not file.open(QFile.ReadOnly):
#         raise RuntimeError(f"Cannot open {path}")

#     ui = loader.load(file)
#     file.close()

#     return ui
