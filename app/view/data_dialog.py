from PySide6.QtWidgets import QFileDialog


def show_save_dialog() -> str | None:
    """Show a save file dialog

    Returns:
        str: The selected file path.
    """
    dialog = QFileDialog()
    dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    dialog.setNameFilter("CSV Files (*.csv)")
    dialog.setDefaultSuffix("csv")
    dialog.setWindowTitle("Save CSV File")

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
        caption="Open CSV File", filter="CSV Files (*.csv)"
    )

    return file_path or None
