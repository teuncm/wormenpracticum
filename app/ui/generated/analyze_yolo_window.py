# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyze_yolo_window.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_AnalyzeYoloWindow(object):
    def setupUi(self, AnalyzeYoloWindow):
        if not AnalyzeYoloWindow.objectName():
            AnalyzeYoloWindow.setObjectName(u"AnalyzeYoloWindow")
        AnalyzeYoloWindow.resize(481, 304)
        self.flowLayout = QHBoxLayout(AnalyzeYoloWindow)
        self.flowLayout.setObjectName(u"flowLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.title_controls = QLabel(AnalyzeYoloWindow)
        self.title_controls.setObjectName(u"title_controls")

        self.leftLayout.addWidget(self.title_controls)

        self.amplitudeLabel = QLabel(AnalyzeYoloWindow)
        self.amplitudeLabel.setObjectName(u"amplitudeLabel")

        self.leftLayout.addWidget(self.amplitudeLabel)

        self.amplitudeSpinBox = QDoubleSpinBox(AnalyzeYoloWindow)
        self.amplitudeSpinBox.setObjectName(u"amplitudeSpinBox")
        self.amplitudeSpinBox.setDecimals(6)
        self.amplitudeSpinBox.setMinimum(0.000001000000000)
        self.amplitudeSpinBox.setMaximum(1000000.000000000000000)
        self.amplitudeSpinBox.setSingleStep(0.010000000000000)
        self.amplitudeSpinBox.setValue(1.000000000000000)

        self.leftLayout.addWidget(self.amplitudeSpinBox)

        self.pinsLabel = QLabel(AnalyzeYoloWindow)
        self.pinsLabel.setObjectName(u"pinsLabel")

        self.leftLayout.addWidget(self.pinsLabel)

        self.pinsLineEdit = QLineEdit(AnalyzeYoloWindow)
        self.pinsLineEdit.setObjectName(u"pinsLineEdit")

        self.leftLayout.addWidget(self.pinsLineEdit)

        self.stimuliLabel = QLabel(AnalyzeYoloWindow)
        self.stimuliLabel.setObjectName(u"stimuliLabel")

        self.leftLayout.addWidget(self.stimuliLabel)

        self.stimuliLineEdit = QLineEdit(AnalyzeYoloWindow)
        self.stimuliLineEdit.setObjectName(u"stimuliLineEdit")

        self.leftLayout.addWidget(self.stimuliLineEdit)

        self.detectionStartLabel = QLabel(AnalyzeYoloWindow)
        self.detectionStartLabel.setObjectName(u"detectionStartLabel")

        self.leftLayout.addWidget(self.detectionStartLabel)

        self.detectionStartLayout = QHBoxLayout()
        self.detectionStartLayout.setObjectName(u"detectionStartLayout")
        self.detectionStartLineEdit = QLineEdit(AnalyzeYoloWindow)
        self.detectionStartLineEdit.setObjectName(u"detectionStartLineEdit")

        self.detectionStartLayout.addWidget(self.detectionStartLineEdit)

        self.showDetectionStartCheckBox = QCheckBox(AnalyzeYoloWindow)
        self.showDetectionStartCheckBox.setObjectName(u"showDetectionStartCheckBox")
        self.showDetectionStartCheckBox.setChecked(True)

        self.detectionStartLayout.addWidget(self.showDetectionStartCheckBox)

        self.showStimulusStartsCheckBox = QCheckBox(AnalyzeYoloWindow)
        self.showStimulusStartsCheckBox.setObjectName(u"showStimulusStartsCheckBox")
        self.showStimulusStartsCheckBox.setChecked(True)

        self.detectionStartLayout.addWidget(self.showStimulusStartsCheckBox)


        self.leftLayout.addLayout(self.detectionStartLayout)

        self.detectionEndLabel = QLabel(AnalyzeYoloWindow)
        self.detectionEndLabel.setObjectName(u"detectionEndLabel")

        self.leftLayout.addWidget(self.detectionEndLabel)

        self.detectionEndLayout = QHBoxLayout()
        self.detectionEndLayout.setObjectName(u"detectionEndLayout")
        self.detectionEndLineEdit = QLineEdit(AnalyzeYoloWindow)
        self.detectionEndLineEdit.setObjectName(u"detectionEndLineEdit")

        self.detectionEndLayout.addWidget(self.detectionEndLineEdit)

        self.showDetectionEndCheckBox = QCheckBox(AnalyzeYoloWindow)
        self.showDetectionEndCheckBox.setObjectName(u"showDetectionEndCheckBox")
        self.showDetectionEndCheckBox.setChecked(True)

        self.detectionEndLayout.addWidget(self.showDetectionEndCheckBox)


        self.leftLayout.addLayout(self.detectionEndLayout)

        self.regionErrorLabel = QLabel(AnalyzeYoloWindow)
        self.regionErrorLabel.setObjectName(u"regionErrorLabel")
        self.regionErrorLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.regionErrorLabel)

        self.selectionErrorLabel = QLabel(AnalyzeYoloWindow)
        self.selectionErrorLabel.setObjectName(u"selectionErrorLabel")
        self.selectionErrorLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.selectionErrorLabel)

        self.extremaLayout = QHBoxLayout()
        self.extremaLayout.setObjectName(u"extremaLayout")
        self.minCheckBox = QCheckBox(AnalyzeYoloWindow)
        self.minCheckBox.setObjectName(u"minCheckBox")
        self.minCheckBox.setChecked(True)

        self.extremaLayout.addWidget(self.minCheckBox)

        self.maxCheckBox = QCheckBox(AnalyzeYoloWindow)
        self.maxCheckBox.setObjectName(u"maxCheckBox")
        self.maxCheckBox.setChecked(True)

        self.extremaLayout.addWidget(self.maxCheckBox)


        self.leftLayout.addLayout(self.extremaLayout)

        self.recordingStatusLabel = QLabel(AnalyzeYoloWindow)
        self.recordingStatusLabel.setObjectName(u"recordingStatusLabel")
        self.recordingStatusLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.recordingStatusLabel)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer_2)


        self.flowLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.title_overview = QLabel(AnalyzeYoloWindow)
        self.title_overview.setObjectName(u"title_overview")

        self.rightLayout.addWidget(self.title_overview)


        self.flowLayout.addLayout(self.rightLayout)

        self.flowLayout.setStretch(0, 3)
        self.flowLayout.setStretch(1, 5)

        self.retranslateUi(AnalyzeYoloWindow)

        QMetaObject.connectSlotsByName(AnalyzeYoloWindow)
    # setupUi

    def retranslateUi(self, AnalyzeYoloWindow):
        AnalyzeYoloWindow.setWindowTitle(QCoreApplication.translate("AnalyzeYoloWindow", u"Analyze Yolo", None))
        self.title_controls.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Controls", None))
        self.amplitudeLabel.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Total visible amplitude", None))
        self.amplitudeSpinBox.setSuffix(QCoreApplication.translate("AnalyzeYoloWindow", u" V", None))
        self.pinsLabel.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Pins on display", None))
        self.pinsLineEdit.setPlaceholderText(QCoreApplication.translate("AnalyzeYoloWindow", u"All (e.g. 1,3,5-8)", None))
#if QT_CONFIG(tooltip)
        self.pinsLineEdit.setToolTip(QCoreApplication.translate("AnalyzeYoloWindow", u"Physical pin IDs. Leave blank to display all available pins.", None))
#endif // QT_CONFIG(tooltip)
        self.stimuliLabel.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Stimuli on display", None))
        self.stimuliLineEdit.setPlaceholderText(QCoreApplication.translate("AnalyzeYoloWindow", u"All (e.g. 1,3,5-8)", None))
#if QT_CONFIG(tooltip)
        self.stimuliLineEdit.setToolTip(QCoreApplication.translate("AnalyzeYoloWindow", u"One-based stimulus numbers. Leave blank to display all available stimuli.", None))
#endif // QT_CONFIG(tooltip)
        self.detectionStartLabel.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Detection start (ms within stimulus)", None))
        self.detectionStartLineEdit.setPlaceholderText(QCoreApplication.translate("AnalyzeYoloWindow", u"From start", None))
#if QT_CONFIG(tooltip)
        self.detectionStartLineEdit.setToolTip(QCoreApplication.translate("AnalyzeYoloWindow", u"Optional inclusive lower time bound. Left click the plot to set it.", None))
#endif // QT_CONFIG(tooltip)
        self.showDetectionStartCheckBox.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Show bound", None))
        self.showStimulusStartsCheckBox.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Stimulus starts", None))
        self.detectionEndLabel.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Detection end (ms within stimulus)", None))
        self.detectionEndLineEdit.setPlaceholderText(QCoreApplication.translate("AnalyzeYoloWindow", u"To end", None))
#if QT_CONFIG(tooltip)
        self.detectionEndLineEdit.setToolTip(QCoreApplication.translate("AnalyzeYoloWindow", u"Optional inclusive upper time bound. Right click the plot to set it.", None))
#endif // QT_CONFIG(tooltip)
        self.showDetectionEndCheckBox.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Show bound", None))
        self.regionErrorLabel.setText("")
        self.selectionErrorLabel.setText("")
        self.minCheckBox.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Min", None))
#if QT_CONFIG(tooltip)
        self.minCheckBox.setToolTip(QCoreApplication.translate("AnalyzeYoloWindow", u"Mark the first minimum per stimulus for every pin.", None))
#endif // QT_CONFIG(tooltip)
        self.maxCheckBox.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Max", None))
#if QT_CONFIG(tooltip)
        self.maxCheckBox.setToolTip(QCoreApplication.translate("AnalyzeYoloWindow", u"Mark the first maximum per stimulus for every pin.", None))
#endif // QT_CONFIG(tooltip)
        self.recordingStatusLabel.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Load a recording to compare responses across all pins.", None))
        self.title_overview.setText(QCoreApplication.translate("AnalyzeYoloWindow", u"Pulse responses across pins", None))
    # retranslateUi

