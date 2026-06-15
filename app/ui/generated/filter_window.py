# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filter_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_FilterWindow(object):
    def setupUi(self, FilterWindow):
        if not FilterWindow.objectName():
            FilterWindow.setObjectName(u"FilterWindow")
        FilterWindow.resize(719, 397)
        self.horizontalLayout_2 = QHBoxLayout(FilterWindow)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")

        self.horizontalLayout_2.addLayout(self.formLayout)

        self.plotLayout = QVBoxLayout()
        self.plotLayout.setObjectName(u"plotLayout")

        self.horizontalLayout_2.addLayout(self.plotLayout)

        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 5)

        self.retranslateUi(FilterWindow)

        QMetaObject.connectSlotsByName(FilterWindow)
    # setupUi

    def retranslateUi(self, FilterWindow):
        FilterWindow.setWindowTitle(QCoreApplication.translate("FilterWindow", u"Filter", None))
    # retranslateUi

