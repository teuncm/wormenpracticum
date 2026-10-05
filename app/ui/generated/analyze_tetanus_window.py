# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyze_tetanus_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

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

        self.offsetLabel = QLabel(AnalyzeTetanusWindow)
        self.offsetLabel.setObjectName(u"offsetLabel")

        self.leftLayout.addWidget(self.offsetLabel)

        self.offsetSpinBox = QDoubleSpinBox(AnalyzeTetanusWindow)
        self.offsetSpinBox.setObjectName(u"offsetSpinBox")
        self.offsetSpinBox.setDecimals(6)
        self.offsetSpinBox.setMinimum(0.000001000000000)
        self.offsetSpinBox.setMaximum(1000000.000000000000000)
        self.offsetSpinBox.setSingleStep(0.010000000000000)
        self.offsetSpinBox.setValue(0.100000000000000)

        self.leftLayout.addWidget(self.offsetSpinBox)

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
        self.offsetLabel.setText(QCoreApplication.translate("AnalyzeTetanusWindow", u"Vertical spacing between pins", None))
        self.offsetSpinBox.setSuffix(QCoreApplication.translate("AnalyzeTetanusWindow", u" V", None))
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

