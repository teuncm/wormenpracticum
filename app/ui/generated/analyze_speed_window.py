# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyze_speed_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QHBoxLayout, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_AnalyzeSpeedWindow(object):
    def setupUi(self, AnalyzeSpeedWindow):
        if not AnalyzeSpeedWindow.objectName():
            AnalyzeSpeedWindow.setObjectName(u"AnalyzeSpeedWindow")
        AnalyzeSpeedWindow.resize(481, 304)
        self.flowLayout = QHBoxLayout(AnalyzeSpeedWindow)
        self.flowLayout.setObjectName(u"flowLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.title_controls = QLabel(AnalyzeSpeedWindow)
        self.title_controls.setObjectName(u"title_controls")

        self.leftLayout.addWidget(self.title_controls)

        self.pinSpacingLabel = QLabel(AnalyzeSpeedWindow)
        self.pinSpacingLabel.setObjectName(u"pinSpacingLabel")
        self.pinSpacingLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.pinSpacingLabel)

        self.stimulusLabel = QLabel(AnalyzeSpeedWindow)
        self.stimulusLabel.setObjectName(u"stimulusLabel")

        self.leftLayout.addWidget(self.stimulusLabel)

        self.stimulusComboBox = QComboBox(AnalyzeSpeedWindow)
        self.stimulusComboBox.setObjectName(u"stimulusComboBox")
        self.stimulusComboBox.setEnabled(False)

        self.leftLayout.addWidget(self.stimulusComboBox)

        self.offsetLabel = QLabel(AnalyzeSpeedWindow)
        self.offsetLabel.setObjectName(u"offsetLabel")

        self.leftLayout.addWidget(self.offsetLabel)

        self.offsetSpinBox = QDoubleSpinBox(AnalyzeSpeedWindow)
        self.offsetSpinBox.setObjectName(u"offsetSpinBox")
        self.offsetSpinBox.setDecimals(6)
        self.offsetSpinBox.setMinimum(0.000001000000000)
        self.offsetSpinBox.setMaximum(1000000.000000000000000)
        self.offsetSpinBox.setSingleStep(0.010000000000000)
        self.offsetSpinBox.setValue(0.100000000000000)

        self.leftLayout.addWidget(self.offsetSpinBox)

        self.extremaLayout = QHBoxLayout()
        self.extremaLayout.setObjectName(u"extremaLayout")
        self.minCheckBox = QCheckBox(AnalyzeSpeedWindow)
        self.minCheckBox.setObjectName(u"minCheckBox")
        self.minCheckBox.setChecked(True)

        self.extremaLayout.addWidget(self.minCheckBox)

        self.maxCheckBox = QCheckBox(AnalyzeSpeedWindow)
        self.maxCheckBox.setObjectName(u"maxCheckBox")
        self.maxCheckBox.setChecked(True)

        self.extremaLayout.addWidget(self.maxCheckBox)


        self.leftLayout.addLayout(self.extremaLayout)

        self.recordingStatusLabel = QLabel(AnalyzeSpeedWindow)
        self.recordingStatusLabel.setObjectName(u"recordingStatusLabel")
        self.recordingStatusLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.recordingStatusLabel)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer_2)


        self.flowLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.title_overview = QLabel(AnalyzeSpeedWindow)
        self.title_overview.setObjectName(u"title_overview")

        self.rightLayout.addWidget(self.title_overview)


        self.flowLayout.addLayout(self.rightLayout)

        self.flowLayout.setStretch(0, 3)
        self.flowLayout.setStretch(1, 5)

        self.retranslateUi(AnalyzeSpeedWindow)

        QMetaObject.connectSlotsByName(AnalyzeSpeedWindow)
    # setupUi

    def retranslateUi(self, AnalyzeSpeedWindow):
        AnalyzeSpeedWindow.setWindowTitle(QCoreApplication.translate("AnalyzeSpeedWindow", u"Analyze speed", None))
        self.title_controls.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Controls", None))
        self.pinSpacingLabel.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Adjacent pin spacing: 3 mm", None))
        self.stimulusLabel.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Stimulus", None))
#if QT_CONFIG(accessibility)
        self.stimulusComboBox.setAccessibleName(QCoreApplication.translate("AnalyzeSpeedWindow", u"Recorded stimulus", None))
#endif // QT_CONFIG(accessibility)
        self.offsetLabel.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Vertical spacing between pins", None))
        self.offsetSpinBox.setSuffix(QCoreApplication.translate("AnalyzeSpeedWindow", u" V", None))
        self.minCheckBox.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Min", None))
#if QT_CONFIG(tooltip)
        self.minCheckBox.setToolTip(QCoreApplication.translate("AnalyzeSpeedWindow", u"Mark the first minimum for each pin in the selected stimulus.", None))
#endif // QT_CONFIG(tooltip)
        self.maxCheckBox.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Max", None))
#if QT_CONFIG(tooltip)
        self.maxCheckBox.setToolTip(QCoreApplication.translate("AnalyzeSpeedWindow", u"Mark the first maximum for each pin in the selected stimulus.", None))
#endif // QT_CONFIG(tooltip)
        self.recordingStatusLabel.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Load a recording with stimulus metadata.", None))
        self.title_overview.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Propagation across pins", None))
    # retranslateUi

