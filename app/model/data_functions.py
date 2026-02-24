import pandas as pd
from PySide6.QtWidgets import QFileDialog


def save_data(file_path, df) -> None:
    """Save experiment data to a Parquet file.

    Args:
        file_path (str): The path to the Parquet file to save.
        df (pd.DataFrame): The DataFrame to save.
    """
    df.to_parquet(file_path, index=False)


def load_data(file_path) -> pd.DataFrame:
    """Load experiment data in Parquet format from file path

    Args:
        file_path (str): The path to the Parquet file to read.

    Returns:
        pd.DataFrame: The DataFrame read from the Parquet file.
    """
    return pd.read_parquet(file_path)


def show_save_dialog() -> str | None:
    """Show a save file dialog

    Returns:
        str: The selected file path.
    """
    dialog = QFileDialog()
    dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    dialog.setNameFilter("Parquet Files (*.parquet)")
    dialog.setDefaultSuffix("parquet")
    dialog.setWindowTitle("Save Parquet File")

    if dialog.exec():
        file_path = dialog.selectedFiles()[0]

        return file_path

    return None


def show_load_dialog() -> str | None:
    """Show a load file dialog

    Returns:
        str: The selected file path.
    """
    file_path, _ = QFileDialog.getOpenFileName(
        caption="Open Parquet File", filter="Parquet Files (*.parquet)"
    )

    return file_path or None
