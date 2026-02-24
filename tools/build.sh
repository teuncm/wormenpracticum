# Mac/Linux build script
uv run pyinstaller --icon app/window/icon.ico --noconfirm --windowed --name wormenpracticum --add-data "app/window:app/window" main.py
