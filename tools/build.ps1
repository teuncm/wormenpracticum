# Windows build script
uv run pyinstaller --icon app/window/icon.ico --copy-metadata nitypes --copy-metadata nidaqmx --noconfirm --windowed --onefile --name wormenpracticum --add-data "app/window;app/window" main.py
