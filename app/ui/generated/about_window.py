# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_window.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QPlainTextEdit, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_AboutWindow(object):
    def setupUi(self, AboutWindow):
        if not AboutWindow.objectName():
            AboutWindow.setObjectName(u"AboutWindow")
        AboutWindow.resize(600, 350)
        self.verticalLayout = QVBoxLayout(AboutWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.title_about = QLabel(AboutWindow)
        self.title_about.setObjectName(u"title_about")

        self.verticalLayout.addWidget(self.title_about)

        self.aboutTextEdit = QPlainTextEdit(AboutWindow)
        self.aboutTextEdit.setObjectName(u"aboutTextEdit")
        self.aboutTextEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.aboutTextEdit)

        self.projectLinksLabel = QLabel(AboutWindow)
        self.projectLinksLabel.setObjectName(u"projectLinksLabel")
        self.projectLinksLabel.setOpenExternalLinks(True)
        self.projectLinksLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.LinksAccessibleByKeyboard)

        self.verticalLayout.addWidget(self.projectLinksLabel)


        self.retranslateUi(AboutWindow)

        QMetaObject.connectSlotsByName(AboutWindow)
    # setupUi

    def retranslateUi(self, AboutWindow):
        AboutWindow.setWindowTitle(QCoreApplication.translate("AboutWindow", u"About", None))
        self.title_about.setText(QCoreApplication.translate("AboutWindow", u"About Wormenpracticum", None))
        self.aboutTextEdit.setPlainText(QCoreApplication.translate("AboutWindow", u"This app was made by x y z.\n"
"\n"
"The low-pass filter uses a fourth-order Butterworth algorithm, applied forwards and backwards using SciPy's sosfiltfilt for zero-phase filtering.", None))
        self.projectLinksLabel.setText(QCoreApplication.translate("AboutWindow", u"<a href=\"https://github.com/teuncm/wormenpracticum/issues\">Report a bug</a> \u00b7 <a href=\"https://github.com/teuncm/wormenpracticum\">GitHub project</a>", None))
    # retranslateUi

