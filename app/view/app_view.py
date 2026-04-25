from app.view.view_helpers import set_global_plot_config
from app.window.ui_main_window import Ui_MainWindow
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow, QWidget


class AppView(QMainWindow):
    requestDataLoad = Signal()
    requestDataSave = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        set_global_plot_config()

        self.ui.tabWidget.clear()

        self.ui.actionLoad_data.triggered.connect(self.on_load_triggered)
        self.ui.actionSave_data.triggered.connect(self.on_save_triggered)

    def set_tab_views(
        self,
        *,
        stimulus_view: QWidget,
        acquisition_view: QWidget,
        overview_view: QWidget,
        analyze_view: QWidget,
    ):
        """Populate the main window tabs with the application views."""
        self.ui.tabWidget.clear()
        self.ui.tabWidget.addTab(stimulus_view, "Stimulus")
        self.ui.tabWidget.addTab(acquisition_view, "Data acquisition")
        self.ui.tabWidget.addTab(overview_view, "Overview")
        self.ui.tabWidget.addTab(analyze_view, "Analyse")
        self.show_tab(overview_view)

    def show_tab(self, widget: QWidget):
        """Switch to the tab containing widget."""
        index = self.ui.tabWidget.indexOf(widget)
        if index >= 0:
            self.ui.tabWidget.setCurrentIndex(index)

    def on_load_triggered(self, checked=False):
        self.requestDataLoad.emit()

    def on_save_triggered(self, checked=False):
        self.requestDataSave.emit()
