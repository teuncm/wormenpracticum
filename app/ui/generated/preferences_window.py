# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences_window.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QLabel,
    QSizePolicy, QSpinBox, QWidget)

class Ui_PreferencesWindow(object):
    def setupUi(self, PreferencesWindow):
        if not PreferencesWindow.objectName():
            PreferencesWindow.setObjectName(u"PreferencesWindow")
        PreferencesWindow.resize(637, 405)
        self.horizontalLayout = QHBoxLayout(PreferencesWindow)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.fontSizeLabel = QLabel(PreferencesWindow)
        self.fontSizeLabel.setObjectName(u"fontSizeLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fontSizeLabel)

        self.fontSizeSpinBox = QSpinBox(PreferencesWindow)
        self.fontSizeSpinBox.setObjectName(u"fontSizeSpinBox")
        self.fontSizeSpinBox.setMinimum(9)
        self.fontSizeSpinBox.setMaximum(20)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fontSizeSpinBox)


        self.horizontalLayout.addLayout(self.formLayout)


        self.retranslateUi(PreferencesWindow)

        QMetaObject.connectSlotsByName(PreferencesWindow)
    # setupUi

    def retranslateUi(self, PreferencesWindow):
        PreferencesWindow.setWindowTitle(QCoreApplication.translate("PreferencesWindow", u"Preferences", None))
        self.fontSizeLabel.setText(QCoreApplication.translate("PreferencesWindow", u"Font size", None))
    # retranslateUi

