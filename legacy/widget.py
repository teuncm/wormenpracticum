# This Python file uses the following encoding: utf-8
import sys
import random
import pickle
import numpy as np
import pyqtgraph as pg
from gui_device_interface import check_if_device_is_connected, get_channels, read_device
from ui_GUI import Ui_Widget
from PySide6.QtWidgets import QApplication, QWidget, QRadioButton, QVBoxLayout, QButtonGroup, QFileDialog, QMessageBox
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QTransform
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsTextItem, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
    
        self.ui.M_buttons.buttonToggled.connect(self.on_radio_button_toggled)
        self.ui.P_buttons.buttonToggled.connect(self.on_radio_button_toggled)
        self.ui.next_button.clicked.connect(self.on_next_button_clicked)
        self.ui.load_button.clicked.connect(self.on_load_button_clicked)
        self.ui.DeviceLink.clicked.connect(self.on_device_link_clicked)
        self.ui.save_button.clicked.connect(self.on_save_button_clicked)
        
        self.setWindowIcon(pg.QtGui.QIcon('appicon.png'))
        
        
        deviceName = check_if_device_is_connected()
        if deviceName:
            self.ui.DeviceLink.setText(f"Device connected")
            self.ui.DeviceLink.setStyleSheet("color: green")
        
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        self.read_data = None
        self.mouse_dots = []
        
        self.start_image()
        self.setup_plotwidget()
        
        QTimer.singleShot(2000, self.clear_no_data_message)
        
        self.ui.set_block_tab.currentChanged.connect(self.on_tab_changed)
        
        self.setup_zoom_sliders()

    def setup_zoom_sliders(self):
        # Use the sliders from the UI, remove locally-created QSliders
        self.ui.x_zoom.setRange(1, 100)
        self.ui.x_zoom.setValue(50)  # 10 -> factor of 1
        self.ui.y_zoom.setRange(1, 100)
        self.ui.y_zoom.setValue(50)

        # Connect signals
        self.ui.x_zoom.valueChanged.connect(self.update_x_zoom)
        self.ui.y_zoom.valueChanged.connect(self.update_y_zoom)
        
    def set_data_range(self):
        if self.read_data is None:
            return
        self.data_x_min = 0
        self.data_x_max = self.read_data.shape[1] - 1
        self.data_y_min = float(np.min(self.read_data))
        self.data_y_max = float(np.max(self.read_data))

        vb = self.ui.plotwidget.getPlotItem().vb
        vb.setXRange(self.data_x_min, self.data_x_max, padding=0)
        vb.setYRange(self.data_y_min, self.data_y_max, padding=0)

    def update_x_zoom(self, value):
        """
        Zoom horizontally based on slider value, relative to data range.
        """
        if self.read_data is None:
            return

        plot_item = self.ui.plotwidget.getPlotItem()
        vb = plot_item.vb
        x_min, x_max = self.data_x_min, self.data_x_max
        x_mid = (x_min + x_max) / 2.0
        half_range = (x_max - x_min) / 2.0

        # Convert slider value into a zoom factor
        factor = value / 50.0  # 50 => factor=1.0
        if factor < 0.1:
            factor = 0.1

        new_half = half_range / factor
        vb.setXRange(x_mid - new_half, x_mid + new_half, padding=0)

    def update_y_zoom(self, value):
        """
        Zoom vertically based on slider value, relative to data range.
        """
        if self.read_data is None:
            return

        plot_item = self.ui.plotwidget.getPlotItem()
        vb = plot_item.vb
        y_min, y_max = self.data_y_min, self.data_y_max
        y_mid = (y_min + y_max) / 2.0
        half_range = (y_max - y_min) / 2.0

        factor = value / 50.0
        if factor < 0.1:
            factor = 0.1

        new_half = half_range / factor
        vb.setYRange(y_mid - new_half, y_mid + new_half, padding=0)
    
    def clear_no_data_message(self):
        self.ui.plotwidget.removeItem(self.logo_item)
        text_item = QGraphicsTextItem("no data")
        text_item.setDefaultTextColor(QColor('grey'))
        text_item.setFont(QFont("Arial", 150))
        text_transform = QTransform().scale(1, -1)
        text_item.setTransform(text_transform)
        self.ui.plotwidget.addItem(text_item)
    
    def setup_plotwidget(self):
        """
        Call this after initializing self.ui.plotwidget.
        """
        # Create a label for coordinates
        self.ui.coords_label = QLabel(self.ui.plotwidget)
        self.ui.coords_label.setStyleSheet("background-color: rgba(255, 255, 255, 200); color: black; border: 1px solid black;")
        self.ui.coords_label.move(10, 10)
        self.ui.coords_label.hide()

        # Connect the mouse-moved signal
        self.ui.plotwidget.scene().sigMouseMoved.connect(self.on_mouse_moved)
        self.mouse_dot = self.ui.plotwidget.plot([0], [0], pen=None, symbol='o', symbolBrush='r')
        self.ui.plotwidget.addItem(self.mouse_dot)
        

    def on_mouse_moved(self, pos):
        plot_item = self.ui.plotwidget.getPlotItem()
        vb = plot_item.vb
        if self.ui.plotwidget.sceneBoundingRect().contains(pos) and self.read_data is not None:
            mouse_point = vb.mapSceneToView(pos)
            idx = int(round(mouse_point.x()))
            if 0 <= idx < self.read_data.shape[1]:
                lines = []
                for i, dot in enumerate(self.mouse_dots):
                    snapped_y = self.read_data[i][idx]
                    dot.setData([idx], [snapped_y])
                    lines.append(f"Y_{i}: {snapped_y:.6g}")
                text_display = f"X: {idx}\n" + "\n".join(lines)
                self.ui.coords_label.setText(text_display)
                self.ui.coords_label.adjustSize()
                self.ui.coords_label.show()
            else:
                self.ui.coords_label.hide()
                for dot in self.mouse_dots:
                    dot.setData([], [])
        else:
            self.ui.coords_label.hide()
            for dot in self.mouse_dots:
                dot.setData([], [])
                
                
        
    def start_image(self):
        self.ui.plotwidget.clear()
        logo_pixmap = QPixmap('appicon.png')
        transform = QTransform().scale(1, -1)
        logo_pixmap = logo_pixmap.transformed(transform)
        self.logo_item = QGraphicsPixmapItem(logo_pixmap)
        self.logo_item.setTransformationMode(Qt.SmoothTransformation)
        self.ui.plotwidget.addItem(self.logo_item)   
        
    def on_radio_button_toggled(self, button, checked):
        if checked:
            button_name = button.objectName()
            button_number = button_name[1:]

            if button_name[0] == "M":
                for btn in self.ui.P_buttons.buttons():
                    if btn.objectName() == f"P{button_number}":
                        corresponding_button = btn
                        break
            else:
                for btn in self.ui.M_buttons.buttons():
                    if btn.objectName() == f"M{button_number}":
                        corresponding_button = btn
                        break
            if corresponding_button.isChecked():
                if button_name[0] == "M":
                    other_buttons = [btn for btn in self.ui.P_buttons.buttons() if btn != corresponding_button]
                else:
                    other_buttons = [btn for btn in self.ui.M_buttons.buttons() if btn != corresponding_button]

                if other_buttons:
                    random_button = random.choice(other_buttons)
                    random_button.setChecked(True)
                    
                    
    def get_selected_button_numbers(self):
        selected_buttons_analyse = []
        selected_buttons_voltage = []
        for btn in self.ui.M_buttons.buttons():
            if btn.isChecked():
                button_number = btn.objectName()
                selected_buttons_voltage.append(button_number)
        for btn in self.ui.P_buttons.buttons():
            if btn.isChecked():
                button_number = btn.objectName()
                selected_buttons_voltage.append(button_number)
        for btn in self.ui.A_buttons.buttons():
            if btn.isChecked():
                button_number = btn.objectName()
                selected_buttons_analyse.append(button_number)
        return [selected_buttons_analyse] + [selected_buttons_voltage]
    
    def on_next_button_clicked(self):
        selected_button_numbers = self.get_selected_button_numbers()
        print("Selected button numbers:", selected_button_numbers)
        if selected_button_numbers[0] == [] or len(selected_button_numbers[1]) < 2:
            QMessageBox.warning(self, "Warning", "Please select a analyse button and at least two voltage buttons.")
            return
        deviceName = check_if_device_is_connected()
        if not deviceName:
            QMessageBox.warning(self, "Warning", "No device connected. Please connect a device to proceed. Otherwise, load a file.")
            self.ui.DeviceLink.setText(f"Disconnected")
            self.ui.DeviceLink.setStyleSheet("color: red")
            return
        print("selected button numbers:", selected_button_numbers)
        self.read_data = np.array(read_device(deviceName, selected_button_numbers))
        self.ui.plotwidget.clear()

        # Create scatter items once, matching the number of channels
        self.mouse_dots.clear()
        for _ in range(len(self.read_data)):
            dot = self.ui.plotwidget.plot(pen=None, symbol='o', symbolBrush='r')
            self.mouse_dots.append(dot)

        colors = ['b','g','r','c','m','y','k','w','d','l','o','p','s','t','v','z']
        for i in range(len(self.read_data)):
            color = colors[i % len(colors)]
            self.ui.plotwidget.plot(self.read_data[i], pen=pg.mkPen(color, width=1), name=f"Channel {i}")
        self.ui.plotwidget.setLabel('left', 'Voltage (V)')
        self.ui.plotwidget.setLabel('bottom', 'Time')
        self.ui.plotwidget.setTitle('Waveform')
        self.ui.plotwidget.addLegend()
        
        self.set_data_range()
        self.ui.x_zoom.setValue(50)
        self.ui.y_zoom.setValue(50)
        
        
        
        
    
    def on_load_button_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Tortured Worm Data(*.twd);;All Files (*)")
        if file_name:
            print(f"Selected file: {file_name}")
            self.ui.plotwidget.clear()
            self.ui.plotwidget.getPlotItem().clear()

            with open(file_name, 'rb') as f:
                self.read_data = np.array(pickle.load(f))

            # Create scatter items once, matching the number of channels
            self.mouse_dots.clear()
            for _ in range(len(self.read_data)):
                dot = self.ui.plotwidget.plot(pen=None, symbol='o', symbolBrush='r')
                self.mouse_dots.append(dot)

            colors = ['b','g','r','c','m','y','k','w','d','l','o','p','s','t','v','z']
            for i in range(len(self.read_data)):
                color = colors[i % len(colors)]
                self.ui.plotwidget.plot(self.read_data[i], pen=pg.mkPen(color, width=1), name=f"Channel {i}")
            self.ui.plotwidget.setLabel('left', 'Voltage (V)')
            self.ui.plotwidget.setLabel('bottom', 'Time')
            self.ui.plotwidget.setTitle('Waveform')
            self.ui.plotwidget.addLegend()
            
            self.set_data_range()
            self.ui.x_zoom.setValue(50)
            self.ui.y_zoom.setValue(50)
            
        else:
            QMessageBox.warning(self, "Warning", "No file selected. Please select a Tortured Worm Data(*.twd) file to load.")
    
    def on_device_link_clicked(self):
        deviceName = check_if_device_is_connected()
        if deviceName:
            self.ui.DeviceLink.setText(f"Device connected")
            self.ui.DeviceLink.setStyleSheet("color: green")
        else:
            self.ui.DeviceLink.setText(f"Disconnected")
            self.ui.DeviceLink.setStyleSheet("color: red")
            
    def on_save_button_clicked(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Tortured Worm Data(*.twd);;All Files (*)")
        if file_name:
            
            with open(file_name, 'wb') as f:
                if self.read_data is not None:
                    pickle.dump(self.read_data, f)
                    QMessageBox.warning(self, "Warning", "Data successfully saved.")
                else:
                    QMessageBox.warning(self, "Warning", "No data to save.")
        else:
            QMessageBox.warning(self, "Warning", "No file selected. Please select a file to save the data.")
            
    def load_tab_ui(self):
        loader = QUiLoader()
        file = QFile("tab.ui")
        file.open(QFile.ReadOnly)
        new_tab = loader.load(file, self)
        file.close()
        return new_tab
    
    def setup_tabs(self):
        first_tab = self.load_tab_ui()
        self.ui.set_block_tab.addTab(first_tab, "Block 1")
    
    def on_tab_changed(self, index):
        # Check if the current tab is the specific tab (e.g., tab at index 0)
        if index == self.ui.set_block_tab.count() - 1:  # Change this to the index of the specific tab
            new_tab = self.load_tab_ui()
            self.ui.set_block_tab.insertTab(self.ui.set_block_tab.count() - 1, new_tab, "Block {}".format(self.ui.set_block_tab.count()))
            self.ui.set_block_tab.setCurrentWidget(new_tab)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    selected_button_numbers = widget.get_selected_button_numbers()
    print(selected_button_numbers)
    sys.exit(app.exec())
