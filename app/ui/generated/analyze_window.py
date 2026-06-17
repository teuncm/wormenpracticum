# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyze_window.ui'
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

class Ui_AnalyzeWindow(object):
    def setupUi(self, AnalyzeWindow):
        if not AnalyzeWindow.objectName():
            AnalyzeWindow.setObjectName(u"AnalyzeWindow")
        AnalyzeWindow.resize(481, 304)
        self.flowLayout = QHBoxLayout(AnalyzeWindow)
        self.flowLayout.setObjectName(u"flowLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.title_controls = QLabel(AnalyzeWindow)
        self.title_controls.setObjectName(u"title_controls")

        self.leftLayout.addWidget(self.title_controls)

        self.pushButton = QPushButton(AnalyzeWindow)
        self.pushButton.setObjectName(u"pushButton")

        self.leftLayout.addWidget(self.pushButton)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer_2)


        self.flowLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.title_overview = QLabel(AnalyzeWindow)
        self.title_overview.setObjectName(u"title_overview")

        self.rightLayout.addWidget(self.title_overview)

        self.pushButton_2 = QPushButton(AnalyzeWindow)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.rightLayout.addWidget(self.pushButton_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.rightLayout.addItem(self.verticalSpacer)


        self.flowLayout.addLayout(self.rightLayout)

        self.flowLayout.setStretch(0, 3)
        self.flowLayout.setStretch(1, 5)

        self.retranslateUi(AnalyzeWindow)

        QMetaObject.connectSlotsByName(AnalyzeWindow)
    # setupUi

    def retranslateUi(self, AnalyzeWindow):
        AnalyzeWindow.setWindowTitle(QCoreApplication.translate("AnalyzeWindow", u"Form", None))
        self.title_controls.setText(QCoreApplication.translate("AnalyzeWindow", u"Controls", None))
        self.pushButton.setText(QCoreApplication.translate("AnalyzeWindow", u"PushButton", None))
        self.title_overview.setText(QCoreApplication.translate("AnalyzeWindow", u"Overview", None))
        self.pushButton_2.setText(QCoreApplication.translate("AnalyzeWindow", u"PushButton", None))
    # retranslateUi

