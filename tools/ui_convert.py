import subprocess
from pathlib import Path

UI_ROOT = Path("app/ui")
GENERATED_ROOT = UI_ROOT / "generated"


def convert_ui_files() -> None:
    """Convert all .ui design files to .py files."""
    GENERATED_ROOT.mkdir(exist_ok=True)
    ui_files = UI_ROOT.glob("*.ui")

    for ui_file in ui_files:
        output_file = GENERATED_ROOT / f"{ui_file.stem}.py"

        command = ["pyside6-uic", str(ui_file), "-o", str(output_file)]

        print(" ".join(command))

        subprocess.run(
            command,
            check=True,
        )

    print("Conversion complete.")


if __name__ == "__main__":
    convert_ui_files()
