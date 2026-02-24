# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pulse_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget)

class Ui_PulseWindow(object):
    def setupUi(self, PulseWindow):
        if not PulseWindow.objectName():
            PulseWindow.setObjectName(u"PulseWindow")
        PulseWindow.resize(823, 521)
        self.verticalLayout = QVBoxLayout(PulseWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(PulseWindow)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(PulseWindow)

        QMetaObject.connectSlotsByName(PulseWindow)
    # setupUi

    def retranslateUi(self, PulseWindow):
        PulseWindow.setWindowTitle(QCoreApplication.translate("PulseWindow", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("PulseWindow", u"GroupBox", None))
    # retranslateUi

