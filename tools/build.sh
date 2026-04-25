# Mac/Linux build script
uv run pyinstaller --icon app/window/icon.icns --noconfirm --windowed --onefile --name wormenpracticum --add-data "app/window:app/window" main.py
