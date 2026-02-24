import subprocess
from pathlib import Path

UI_ROOT = Path("app/ui")


def convert_ui_files() -> None:
    """Convert all .ui design files to .py files."""
    ui_files = UI_ROOT.rglob("*.ui")

    for ui_file in ui_files:
        output_file = ui_file.with_name(f"ui_{ui_file.stem}.py")

        print(f"Converting {ui_file} → {output_file}")

        subprocess.run(
            ["pyside6-uic", str(ui_file), "-o", str(output_file)],
            check=True,
        )

    print("Conversion complete.")


if __name__ == "__main__":
    convert_ui_files()
