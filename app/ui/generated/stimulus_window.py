# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'stimulus_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QDoubleSpinBox,
    QFormLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_StimulusWindow(object):
    def setupUi(self, StimulusWindow):
        if not StimulusWindow.objectName():
            StimulusWindow.setObjectName(u"StimulusWindow")
        StimulusWindow.resize(703, 424)
        self.flowLayout = QHBoxLayout(StimulusWindow)
        self.flowLayout.setObjectName(u"flowLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.title_stimulus = QLabel(StimulusWindow)
        self.title_stimulus.setObjectName(u"title_stimulus")

        self.leftLayout.addWidget(self.title_stimulus)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.nLabel = QLabel(StimulusWindow)
        self.nLabel.setObjectName(u"nLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.nLabel)

        self.nSpinBox = QSpinBox(StimulusWindow)
        self.nSpinBox.setObjectName(u"nSpinBox")
        self.nSpinBox.setMinimum(1)
        self.nSpinBox.setValue(1)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nSpinBox)

        self.durLabel = QLabel(StimulusWindow)
        self.durLabel.setObjectName(u"durLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.durLabel)

        self.durSpinBox = QDoubleSpinBox(StimulusWindow)
        self.durSpinBox.setObjectName(u"durSpinBox")
        self.durSpinBox.setDecimals(3)
        self.durSpinBox.setMinimum(0.000000000000000)
        self.durSpinBox.setMaximum(1000000.000000000000000)
        self.durSpinBox.setValue(3.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.durSpinBox)

        self.limitLabel = QLabel(StimulusWindow)
        self.limitLabel.setObjectName(u"limitLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.limitLabel)

        self.limitSpinBox = QDoubleSpinBox(StimulusWindow)
        self.limitSpinBox.setObjectName(u"limitSpinBox")
        self.limitSpinBox.setDecimals(3)
        self.limitSpinBox.setMinimum(0.000000000000000)
        self.limitSpinBox.setMaximum(1000000.000000000000000)
        self.limitSpinBox.setValue(1.500000000000000)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.limitSpinBox)


        self.leftLayout.addLayout(self.formLayout)

        self.title_pulse = QLabel(StimulusWindow)
        self.title_pulse.setObjectName(u"title_pulse")

        self.leftLayout.addWidget(self.title_pulse)

        self.add_pulse_button = QPushButton(StimulusWindow)
        self.add_pulse_button.setObjectName(u"add_pulse_button")

        self.leftLayout.addWidget(self.add_pulse_button)

        self.segmentTabWidget = QTabWidget(StimulusWindow)
        self.segmentTabWidget.setObjectName(u"segmentTabWidget")
        self.segmentTabWidget.setMinimumSize(QSize(0, 100))
        self.segmentTabWidget.setAutoFillBackground(False)

        self.leftLayout.addWidget(self.segmentTabWidget)

        self.highlight_selected_pulse_checkbox = QCheckBox(StimulusWindow)
        self.highlight_selected_pulse_checkbox.setObjectName(u"highlight_selected_pulse_checkbox")

        self.leftLayout.addWidget(self.highlight_selected_pulse_checkbox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer)

        self.title_slider = QLabel(StimulusWindow)
        self.title_slider.setObjectName(u"title_slider")

        self.leftLayout.addWidget(self.title_slider)

        self.stepSlider = QSlider(StimulusWindow)
        self.stepSlider.setObjectName(u"stepSlider")
        self.stepSlider.setOrientation(Qt.Orientation.Horizontal)

        self.leftLayout.addWidget(self.stepSlider)


        self.flowLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.title_plot = QLabel(StimulusWindow)
        self.title_plot.setObjectName(u"title_plot")

        self.rightLayout.addWidget(self.title_plot)


        self.flowLayout.addLayout(self.rightLayout)

        self.flowLayout.setStretch(0, 3)
        self.flowLayout.setStretch(1, 5)

        self.retranslateUi(StimulusWindow)

        self.segmentTabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(StimulusWindow)
    # setupUi

    def retranslateUi(self, StimulusWindow):
        StimulusWindow.setWindowTitle(QCoreApplication.translate("StimulusWindow", u"Stimulus Editor", None))
        self.title_stimulus.setText(QCoreApplication.translate("StimulusWindow", u"Stimulus parameters", None))
        self.nLabel.setText(QCoreApplication.translate("StimulusWindow", u"Number of stimuli", None))
        self.durLabel.setText(QCoreApplication.translate("StimulusWindow", u"Total duration (s)", None))
        self.limitLabel.setText(QCoreApplication.translate("StimulusWindow", u"Voltage limit (V)", None))
        self.title_pulse.setText(QCoreApplication.translate("StimulusWindow", u"Pulse parameters", None))
        self.add_pulse_button.setText(QCoreApplication.translate("StimulusWindow", u"Add pulse", None))
        self.highlight_selected_pulse_checkbox.setText(QCoreApplication.translate("StimulusWindow", u"Highlight selected pulse", None))
        self.title_slider.setText(QCoreApplication.translate("StimulusWindow", u"Stimulus slider", None))
        self.title_plot.setText(QCoreApplication.translate("StimulusWindow", u"Stimulus plot", None))
    # retranslateUi

