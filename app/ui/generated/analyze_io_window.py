# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyze_io_window.ui'
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
    QLabel, QLineEdit, QSizePolicy, QSlider,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_AnalyzeIOWindow(object):
    def setupUi(self, AnalyzeIOWindow):
        if not AnalyzeIOWindow.objectName():
            AnalyzeIOWindow.setObjectName(u"AnalyzeIOWindow")
        AnalyzeIOWindow.resize(481, 304)
        self.flowLayout = QHBoxLayout(AnalyzeIOWindow)
        self.flowLayout.setObjectName(u"flowLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.title_controls = QLabel(AnalyzeIOWindow)
        self.title_controls.setObjectName(u"title_controls")

        self.leftLayout.addWidget(self.title_controls)

        self.channelLabel = QLabel(AnalyzeIOWindow)
        self.channelLabel.setObjectName(u"channelLabel")

        self.leftLayout.addWidget(self.channelLabel)

        self.channelSlider = QSlider(AnalyzeIOWindow)
        self.channelSlider.setObjectName(u"channelSlider")
        self.channelSlider.setEnabled(False)
        self.channelSlider.setMinimum(1)
        self.channelSlider.setMaximum(1)
        self.channelSlider.setOrientation(Qt.Orientation.Horizontal)

        self.leftLayout.addWidget(self.channelSlider)

        self.amplitudeLabel = QLabel(AnalyzeIOWindow)
        self.amplitudeLabel.setObjectName(u"amplitudeLabel")

        self.leftLayout.addWidget(self.amplitudeLabel)

        self.amplitudeSpinBox = QDoubleSpinBox(AnalyzeIOWindow)
        self.amplitudeSpinBox.setObjectName(u"amplitudeSpinBox")
        self.amplitudeSpinBox.setDecimals(6)
        self.amplitudeSpinBox.setMinimum(0.000001000000000)
        self.amplitudeSpinBox.setMaximum(1000000.000000000000000)
        self.amplitudeSpinBox.setSingleStep(0.010000000000000)
        self.amplitudeSpinBox.setValue(1.000000000000000)

        self.leftLayout.addWidget(self.amplitudeSpinBox)

        self.detectionStartLabel = QLabel(AnalyzeIOWindow)
        self.detectionStartLabel.setObjectName(u"detectionStartLabel")

        self.leftLayout.addWidget(self.detectionStartLabel)

        self.detectionStartLayout = QHBoxLayout()
        self.detectionStartLayout.setObjectName(u"detectionStartLayout")
        self.detectionStartLineEdit = QLineEdit(AnalyzeIOWindow)
        self.detectionStartLineEdit.setObjectName(u"detectionStartLineEdit")

        self.detectionStartLayout.addWidget(self.detectionStartLineEdit)

        self.showDetectionStartCheckBox = QCheckBox(AnalyzeIOWindow)
        self.showDetectionStartCheckBox.setObjectName(u"showDetectionStartCheckBox")
        self.showDetectionStartCheckBox.setChecked(True)

        self.detectionStartLayout.addWidget(self.showDetectionStartCheckBox)

        self.showStimulusStartsCheckBox = QCheckBox(AnalyzeIOWindow)
        self.showStimulusStartsCheckBox.setObjectName(u"showStimulusStartsCheckBox")
        self.showStimulusStartsCheckBox.setChecked(True)

        self.detectionStartLayout.addWidget(self.showStimulusStartsCheckBox)


        self.leftLayout.addLayout(self.detectionStartLayout)

        self.detectionEndLabel = QLabel(AnalyzeIOWindow)
        self.detectionEndLabel.setObjectName(u"detectionEndLabel")

        self.leftLayout.addWidget(self.detectionEndLabel)

        self.detectionEndLayout = QHBoxLayout()
        self.detectionEndLayout.setObjectName(u"detectionEndLayout")
        self.detectionEndLineEdit = QLineEdit(AnalyzeIOWindow)
        self.detectionEndLineEdit.setObjectName(u"detectionEndLineEdit")

        self.detectionEndLayout.addWidget(self.detectionEndLineEdit)

        self.showDetectionEndCheckBox = QCheckBox(AnalyzeIOWindow)
        self.showDetectionEndCheckBox.setObjectName(u"showDetectionEndCheckBox")
        self.showDetectionEndCheckBox.setChecked(True)

        self.detectionEndLayout.addWidget(self.showDetectionEndCheckBox)


        self.leftLayout.addLayout(self.detectionEndLayout)

        self.regionErrorLabel = QLabel(AnalyzeIOWindow)
        self.regionErrorLabel.setObjectName(u"regionErrorLabel")
        self.regionErrorLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.regionErrorLabel)

        self.extremaLayout = QHBoxLayout()
        self.extremaLayout.setObjectName(u"extremaLayout")
        self.minCheckBox = QCheckBox(AnalyzeIOWindow)
        self.minCheckBox.setObjectName(u"minCheckBox")
        self.minCheckBox.setChecked(True)

        self.extremaLayout.addWidget(self.minCheckBox)

        self.maxCheckBox = QCheckBox(AnalyzeIOWindow)
        self.maxCheckBox.setObjectName(u"maxCheckBox")
        self.maxCheckBox.setChecked(True)

        self.extremaLayout.addWidget(self.maxCheckBox)


        self.leftLayout.addLayout(self.extremaLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer_2)


        self.flowLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.title_overview = QLabel(AnalyzeIOWindow)
        self.title_overview.setObjectName(u"title_overview")

        self.rightLayout.addWidget(self.title_overview)


        self.flowLayout.addLayout(self.rightLayout)

        self.flowLayout.setStretch(0, 3)
        self.flowLayout.setStretch(1, 5)

        self.retranslateUi(AnalyzeIOWindow)

        QMetaObject.connectSlotsByName(AnalyzeIOWindow)
    # setupUi

    def retranslateUi(self, AnalyzeIOWindow):
        AnalyzeIOWindow.setWindowTitle(QCoreApplication.translate("AnalyzeIOWindow", u"Analyze IO", None))
        self.title_controls.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Controls", None))
        self.channelLabel.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Channel: no data", None))
#if QT_CONFIG(accessibility)
        self.channelSlider.setAccessibleName(QCoreApplication.translate("AnalyzeIOWindow", u"Measurement channel", None))
#endif // QT_CONFIG(accessibility)
        self.amplitudeLabel.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Total visible amplitude", None))
        self.amplitudeSpinBox.setSuffix(QCoreApplication.translate("AnalyzeIOWindow", u" V", None))
        self.detectionStartLabel.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Detection start (ms within stimulus)", None))
        self.detectionStartLineEdit.setPlaceholderText(QCoreApplication.translate("AnalyzeIOWindow", u"From start", None))
#if QT_CONFIG(tooltip)
        self.detectionStartLineEdit.setToolTip(QCoreApplication.translate("AnalyzeIOWindow", u"Optional inclusive lower time bound. Left click the plot to set it.", None))
#endif // QT_CONFIG(tooltip)
        self.showDetectionStartCheckBox.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Show bound", None))
        self.showStimulusStartsCheckBox.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Stimulus starts", None))
        self.detectionEndLabel.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Detection end (ms within stimulus)", None))
        self.detectionEndLineEdit.setPlaceholderText(QCoreApplication.translate("AnalyzeIOWindow", u"To end", None))
#if QT_CONFIG(tooltip)
        self.detectionEndLineEdit.setToolTip(QCoreApplication.translate("AnalyzeIOWindow", u"Optional inclusive upper time bound. Right click the plot to set it.", None))
#endif // QT_CONFIG(tooltip)
        self.showDetectionEndCheckBox.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Show bound", None))
        self.regionErrorLabel.setText("")
        self.minCheckBox.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Min", None))
#if QT_CONFIG(tooltip)
        self.minCheckBox.setToolTip(QCoreApplication.translate("AnalyzeIOWindow", u"Mark the first occurrence of the minimum voltage in each stimulus.", None))
#endif // QT_CONFIG(tooltip)
        self.maxCheckBox.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Max", None))
#if QT_CONFIG(tooltip)
        self.maxCheckBox.setToolTip(QCoreApplication.translate("AnalyzeIOWindow", u"Mark the first occurrence of the maximum voltage in each stimulus.", None))
#endif // QT_CONFIG(tooltip)
        self.title_overview.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Recorded stimuli", None))
    # retranslateUi

