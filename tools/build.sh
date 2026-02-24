# Mac/Linux build script
uv run pyinstaller --icon app/ui/icon.ico --noconfirm --windowed --name wormenpracticum --add-data "app/ui:app/ui" main.py
