# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'debug_window.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_DebugWindow(object):
    def setupUi(self, DebugWindow):
        if not DebugWindow.objectName():
            DebugWindow.setObjectName(u"DebugWindow")
        DebugWindow.resize(434, 230)
        self.horizontalLayout_2 = QHBoxLayout(DebugWindow)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.title_debug = QLabel(DebugWindow)
        self.title_debug.setObjectName(u"title_debug")

        self.verticalLayout.addWidget(self.title_debug)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(DebugWindow)

        QMetaObject.connectSlotsByName(DebugWindow)
    # setupUi

    def retranslateUi(self, DebugWindow):
        DebugWindow.setWindowTitle(QCoreApplication.translate("DebugWindow", u"Debug", None))
        self.title_debug.setText(QCoreApplication.translate("DebugWindow", u"Debug", None))
    # retranslateUi

