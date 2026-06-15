# Windows build script
uv run pyinstaller --icon app/ui/icon.ico --copy-metadata nitypes --copy-metadata nidaqmx --noconfirm --windowed --onefile --name wormenpracticum --add-data "app/ui;app/ui" main.py
