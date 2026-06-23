# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyze_speed_window.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

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

        self.pushButton = QPushButton(AnalyzeSpeedWindow)
        self.pushButton.setObjectName(u"pushButton")

        self.leftLayout.addWidget(self.pushButton)

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
        AnalyzeSpeedWindow.setWindowTitle(QCoreApplication.translate("AnalyzeSpeedWindow", u"Form", None))
        self.title_controls.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Controls", None))
        self.pushButton.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"PushButton", None))
        self.title_overview.setText(QCoreApplication.translate("AnalyzeSpeedWindow", u"Overview", None))
    # retranslateUi

