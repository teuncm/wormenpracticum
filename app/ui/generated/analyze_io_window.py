# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyze_io_window.ui'
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

        self.pushButton = QPushButton(AnalyzeIOWindow)
        self.pushButton.setObjectName(u"pushButton")

        self.leftLayout.addWidget(self.pushButton)

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
        AnalyzeIOWindow.setWindowTitle(QCoreApplication.translate("AnalyzeIOWindow", u"Form", None))
        self.title_controls.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Controls", None))
        self.pushButton.setText(QCoreApplication.translate("AnalyzeIOWindow", u"PushButton", None))
        self.title_overview.setText(QCoreApplication.translate("AnalyzeIOWindow", u"Overview", None))
    # retranslateUi

