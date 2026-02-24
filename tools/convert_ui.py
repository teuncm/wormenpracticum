import subprocess
from pathlib import Path

from util import resolve_project

UI_ROOT = Path(resolve_project("ui"))


def convert_ui_files() -> None:
    ui_files = UI_ROOT.rglob("*.ui")

    for ui_file in ui_files:
        output_file = ui_file.with_name(f"ui_{ui_file.stem}.py")

        print(f"Converting {ui_file} → {output_file}")

        subprocess.run(
            ["pyside6-uic", str(ui_file), "-o", str(output_file)],
            check=True,
        )


if __name__ == "__main__":
    convert_ui_files()
