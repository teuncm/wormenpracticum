# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyze_tetanus_window.ui'
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

class Ui_AnalyzeTetanusWindow(object):
    def setupUi(self, AnalyzeTetanusWindow):
        if not AnalyzeTetanusWindow.objectName():
            AnalyzeTetanusWindow.setObjectName(u"AnalyzeTetanusWindow")
        AnalyzeTetanusWindow.resize(481, 304)
        self.flowLayout = QHBoxLayout(AnalyzeTetanusWindow)
        self.flowLayout.setObjectName(u"flowLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.title_controls = QLabel(AnalyzeTetanusWindow)
        self.title_controls.setObjectName(u"title_controls")

        self.leftLayout.addWidget(self.title_controls)

        self.amplitudeLabel = QLabel(AnalyzeTetanusWindow)
        self.amplitudeLabel.setObjectName(u"amplitudeLabel")

        self.leftLayout.addWidget(self.amplitudeLabel)

        self.amplitudeSpinBox = QDoubleSpinBox(AnalyzeTetanusWindow)
        self.amplitudeSpinBox.setObjectName(u"amplitudeSpinBox")
        self.amplitudeSpinBox.setDecimals(6)
        self.amplitudeSpinBox.setMinimum(0.000001000000000)
        self.amplitudeSpinBox.setMaximum(1000000.000000000000000)
        self.amplitudeSpinBox.setSingleStep(0.010000000000000)
        self.amplitudeSpinBox.setValue(0.100000000000000)

        self.leftLayout.addWidget(self.amplitudeSpinBox)

        self.detectionStartLabel = QLabel(AnalyzeTetanusWindow)
        self.detectionStartLabel.setObjectName(u"detectionStartLabel")

        self.leftLayout.addWidget(self.detectionStartLabel)

        self.detectionStartLayout = QHBoxLayout()
        self.detectionStartLayout.setObjectName(u"detectionStartLayout")
        self.detectionStartLineEdit = QLineEdit(AnalyzeTetanusWindow)
        self.detectionStartLineEdit.setObjectName(u"detectionStartLineEdit")

        self.detectionStartLayout.addWidget(self.detectionStartLineEdit)

        self.showDetectionStartCheckBox = QCheckBox(AnalyzeTetanusWindow)
        self.showDetectionStartCheckBox.setObjectName(u"showDetectionStartCheckBox")
        self.showDetectionStartCheckBox.setChecked(True)

        self.detectionStartLayout.addWidget(self.showDetectionStartCheckBox)

        self.showStimulusStartsCheckBox = QCheckBox(AnalyzeTetanusWindow)
        self.showStimulusStartsCheckBox.setObjectName(u"showStimulusStartsCheckBox")
        self.showStimulusStartsCheckBox.setChecked(True)

        self.detectionStartLayout.addWidget(self.showStimulusStartsCheckBox)


        self.leftLayout.addLayout(self.detectionStartLayout)

        self.detectionEndLabel = QLabel(AnalyzeTetanusWindow)
        self.detectionEndLabel.setObjectName(u"detectionEndLabel")

        self.leftLayout.addWidget(self.detectionEndLabel)

        self.detectionEndLayout = QHBoxLayout()
        self.detectionEndLayout.setObjectName(u"detectionEndLayout")
        self.detectionEndLineEdit = QLineEdit(AnalyzeTetanusWindow)
        self.detectionEndLineEdit.setObjectName(u"detectionEndLineEdit")

        self.detectionEndLayout.addWidget(self.detectionEndLineEdit)

        self.showDetectionEndCheckBox = QCheckBox(AnalyzeTetanusWindow)
        self.showDetectionEndCheckBox.setObjectName(u"showDetectionEndCheckBox")
        self.showDetectionEndCheckBox.setChecked(True)

        self.detectionEndLayout.addWidget(self.showDetectionEndCheckBox)


        self.leftLayout.addLayout(self.detectionEndLayout)

        self.regionErrorLabel = QLabel(AnalyzeTetanusWindow)
        self.regionErrorLabel.setObjectName(u"regionErrorLabel")
        self.regionErrorLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.regionErrorLabel)

        self.extremaLayout = QHBoxLayout()
        self.extremaLayout.setObjectName(u"extremaLayout")
        self.minCheckBox = QCheckBox(AnalyzeTetanusWindow)
        self.minCheckBox.setObjectName(u"minCheckBox")
        self.minCheckBox.setChecked(True)

        self.extremaLayout.addWidget(self.minCheckBox)

        self.maxCheckBox = QCheckBox(AnalyzeTetanusWindow)
        self.maxCheckBox.setObjectName(u"maxCheckBox")
        self.maxCheckBox.setChecked(True)

        self.extremaLayout.addWidget(self.maxCheckBox)


        self.leftLayout.addLayout(self.extremaLayout)

        self.recordingStatusLabel = QLabel(AnalyzeTetanusWindow)
        self.recordingStatusLabel.setObjectName(u"recordingStatusLabel")
        self.recordingStatusLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.recordingStatusLabel)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer_2)


        self.flowLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.title_overview = QLabel(AnalyzeTetanusWindow)
        self.title_overview.setObjectName(u"title_overview")

        self.rightLayout.addWidget(self.title_overview)


        self.flowLayout.addLayout(self.rightLayout)

        self.flowLayout.setStretch(0, 3)
        self.flowLayout.setStretch(1, 5)

        self.retranslateUi(AnalyzeTetanusWindow)

        QMetaObject.connectSlotsByName(AnalyzeTetanusWindow)
    # setupUi

    def retranslateUi(self, AnalyzeTetanusWindow):
        AnalyzeTetanusWindow.setWindowTitle(QCoreApplication.translate("AnalyzeTetanusWindow", u"Analyze tetanus", None))
        self.title_controls.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Controls", None))
        self.amplitudeLabel.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Total visible amplitude", None))
        self.amplitudeSpinBox.setSuffix(QCoreApplication.translate("AnalyzeTetanusWindow", u" V", None))
        self.detectionStartLabel.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Detection start (ms within stimulus)", None))
        self.detectionStartLineEdit.setPlaceholderText(QCoreApplication.translate("AnalyzeTetanusWindow", u"From start", None))
#if QT_CONFIG(tooltip)
        self.detectionStartLineEdit.setToolTip(QCoreApplication.translate("AnalyzeTetanusWindow", u"Optional inclusive lower time bound. Left click the plot to set it.", None))
#endif // QT_CONFIG(tooltip)
        self.showDetectionStartCheckBox.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Show bound", None))
        self.showStimulusStartsCheckBox.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Stimulus starts", None))
        self.detectionEndLabel.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Detection end (ms within stimulus)", None))
        self.detectionEndLineEdit.setPlaceholderText(QCoreApplication.translate("AnalyzeTetanusWindow", u"To end", None))
#if QT_CONFIG(tooltip)
        self.detectionEndLineEdit.setToolTip(QCoreApplication.translate("AnalyzeTetanusWindow", u"Optional inclusive upper time bound. Right click the plot to set it.", None))
#endif // QT_CONFIG(tooltip)
        self.showDetectionEndCheckBox.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Show bound", None))
        self.regionErrorLabel.setText("")
        self.minCheckBox.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Min", None))
#if QT_CONFIG(tooltip)
        self.minCheckBox.setToolTip(QCoreApplication.translate("AnalyzeTetanusWindow", u"Mark the first minimum per stimulus for every pin.", None))
#endif // QT_CONFIG(tooltip)
        self.maxCheckBox.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Max", None))
#if QT_CONFIG(tooltip)
        self.maxCheckBox.setToolTip(QCoreApplication.translate("AnalyzeTetanusWindow", u"Mark the first maximum per stimulus for every pin.", None))
#endif // QT_CONFIG(tooltip)
        self.recordingStatusLabel.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Load a recording to compare responses across all pins.", None))
        self.title_overview.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Pulse responses across pins", None))
    # retranslateUi

