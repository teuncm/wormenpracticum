# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QTabWidget, QWidget)

class Ui_AppWindow(object):
    def setupUi(self, AppWindow):
        if not AppWindow.objectName():
            AppWindow.setObjectName(u"AppWindow")
        AppWindow.resize(1602, 991)
        self.actionClear_data = QAction(AppWindow)
        self.actionClear_data.setObjectName(u"actionClear_data")
        self.actionLoad_data = QAction(AppWindow)
        self.actionLoad_data.setObjectName(u"actionLoad_data")
        self.actionSave_data = QAction(AppWindow)
        self.actionSave_data.setObjectName(u"actionSave_data")
        self.actionLoad_metadata = QAction(AppWindow)
        self.actionLoad_metadata.setObjectName(u"actionLoad_metadata")
        self.actionSave_metadata = QAction(AppWindow)
        self.actionSave_metadata.setObjectName(u"actionSave_metadata")
        self.actionAbout = QAction(AppWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionImpulse = QAction(AppWindow)
        self.actionImpulse.setObjectName(u"actionImpulse")
        self.actionProtocol = QAction(AppWindow)
        self.actionProtocol.setObjectName(u"actionProtocol")
        self.actionSmoothing = QAction(AppWindow)
        self.actionSmoothing.setObjectName(u"actionSmoothing")
        self.actionAnalyze = QAction(AppWindow)
        self.actionAnalyze.setObjectName(u"actionAnalyze")
        self.actionRun = QAction(AppWindow)
        self.actionRun.setObjectName(u"actionRun")
        self.actionNew = QAction(AppWindow)
        self.actionNew.setObjectName(u"actionNew")
        self.actionLoad_stimulus = QAction(AppWindow)
        self.actionLoad_stimulus.setObjectName(u"actionLoad_stimulus")
        self.actionSave_stimulus = QAction(AppWindow)
        self.actionSave_stimulus.setObjectName(u"actionSave_stimulus")
        self.actionLoad_protocol = QAction(AppWindow)
        self.actionLoad_protocol.setObjectName(u"actionLoad_protocol")
        self.actionSave_protocol = QAction(AppWindow)
        self.actionSave_protocol.setObjectName(u"actionSave_protocol")
        self.actionExit = QAction(AppWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionDebug = QAction(AppWindow)
        self.actionDebug.setObjectName(u"actionDebug")
        self.actionReset_stimulus = QAction(AppWindow)
        self.actionReset_stimulus.setObjectName(u"actionReset_stimulus")
        self.actionPreferences = QAction(AppWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.actionReset_protocol = QAction(AppWindow)
        self.actionReset_protocol.setObjectName(u"actionReset_protocol")
        self.centralwidget = QWidget(AppWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tabWidget.addTab(self.tab, "")

        self.horizontalLayout_3.addWidget(self.tabWidget)

        AppWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(AppWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1602, 33))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menuBar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        AppWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoad_stimulus)
        self.menuFile.addAction(self.actionSave_stimulus)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoad_protocol)
        self.menuFile.addAction(self.actionSave_protocol)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoad_data)
        self.menuFile.addAction(self.actionSave_data)
        self.menuFile.addAction(self.actionLoad_metadata)
        self.menuFile.addAction(self.actionSave_metadata)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionReset_stimulus)
        self.menuEdit.addAction(self.actionReset_protocol)
        self.menuEdit.addAction(self.actionClear_data)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionPreferences)
        self.menuHelp.addAction(self.actionAbout)
        self.menuView.addAction(self.actionDebug)

        self.retranslateUi(AppWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AppWindow)
    # setupUi

    def retranslateUi(self, AppWindow):
        AppWindow.setWindowTitle(QCoreApplication.translate("AppWindow", u"Wormenpracticum", None))
        self.actionClear_data.setText(QCoreApplication.translate("AppWindow", u"Clear data", None))
        self.actionLoad_data.setText(QCoreApplication.translate("AppWindow", u"Load data...", None))
        self.actionSave_data.setText(QCoreApplication.translate("AppWindow", u"Save data...", None))
        self.actionLoad_metadata.setText(QCoreApplication.translate("AppWindow", u"Load metadata...", None))
        self.actionSave_metadata.setText(QCoreApplication.translate("AppWindow", u"Save metadata...", None))
        self.actionAbout.setText(QCoreApplication.translate("AppWindow", u"About", None))
        self.actionImpulse.setText(QCoreApplication.translate("AppWindow", u"Stimulus...", None))
        self.actionProtocol.setText(QCoreApplication.translate("AppWindow", u"Protocol...", None))
        self.actionSmoothing.setText(QCoreApplication.translate("AppWindow", u"Smooth...", None))
        self.actionAnalyze.setText(QCoreApplication.translate("AppWindow", u"Analyze...", None))
        self.actionRun.setText(QCoreApplication.translate("AppWindow", u"Run...", None))
        self.actionNew.setText(QCoreApplication.translate("AppWindow", u"New", None))
        self.actionLoad_stimulus.setText(QCoreApplication.translate("AppWindow", u"Load stimulus...", None))
        self.actionSave_stimulus.setText(QCoreApplication.translate("AppWindow", u"Save stimulus...", None))
        self.actionLoad_protocol.setText(QCoreApplication.translate("AppWindow", u"Load protocol...", None))
        self.actionSave_protocol.setText(QCoreApplication.translate("AppWindow", u"Save protocol...", None))
        self.actionExit.setText(QCoreApplication.translate("AppWindow", u"Exit", None))
        self.actionDebug.setText(QCoreApplication.translate("AppWindow", u"Debug", None))
        self.actionReset_stimulus.setText(QCoreApplication.translate("AppWindow", u"Reset stimulus", None))
        self.actionPreferences.setText(QCoreApplication.translate("AppWindow", u"Preferences", None))
        self.actionReset_protocol.setText(QCoreApplication.translate("AppWindow", u"Reset protocol", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("AppWindow", u"Vertical tab placeholder (tabs added in controller)", None))
        self.menuFile.setTitle(QCoreApplication.translate("AppWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("AppWindow", u"Edit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("AppWindow", u"Help", None))
        self.menuView.setTitle(QCoreApplication.translate("AppWindow", u"View", None))
    # retranslateUi

