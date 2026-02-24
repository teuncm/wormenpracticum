# Build script for PyInstaller.
uv run pyinstaller --icon ui/icon.ico --noconfirm --windowed --name wormenpracticum --add-data "ui;ui" main.py
