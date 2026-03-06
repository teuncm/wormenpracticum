# Windows build script
uv run pyinstaller --icon app/window/icon.ico --noconfirm --windowed --onefile --name wormenpracticum --add-data "app/window;app/window" main.py
