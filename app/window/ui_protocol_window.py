# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'protocol_window.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_ProtocolWindow(object):
    def setupUi(self, ProtocolWindow):
        if not ProtocolWindow.objectName():
            ProtocolWindow.setObjectName(u"ProtocolWindow")
        ProtocolWindow.resize(609, 363)
        self.flowLayout = QHBoxLayout(ProtocolWindow)
        self.flowLayout.setObjectName(u"flowLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.title_controls = QLabel(ProtocolWindow)
        self.title_controls.setObjectName(u"title_controls")

        self.leftLayout.addWidget(self.title_controls)

        self.channelFormLayout = QFormLayout()
        self.channelFormLayout.setObjectName(u"channelFormLayout")
        self.positiveChannelLabel = QLabel(ProtocolWindow)
        self.positiveChannelLabel.setObjectName(u"positiveChannelLabel")

        self.channelFormLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.positiveChannelLabel)

        self.positiveChannelComboBox = QComboBox(ProtocolWindow)
        self.positiveChannelComboBox.setObjectName(u"positiveChannelComboBox")

        self.channelFormLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.positiveChannelComboBox)

        self.negativeChannelLabel = QLabel(ProtocolWindow)
        self.negativeChannelLabel.setObjectName(u"negativeChannelLabel")

        self.channelFormLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.negativeChannelLabel)

        self.negativeChannelComboBox = QComboBox(ProtocolWindow)
        self.negativeChannelComboBox.setObjectName(u"negativeChannelComboBox")

        self.channelFormLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.negativeChannelComboBox)


        self.leftLayout.addLayout(self.channelFormLayout)

        self.nidaqStatusLabel = QLabel(ProtocolWindow)
        self.nidaqStatusLabel.setObjectName(u"nidaqStatusLabel")
        self.nidaqStatusLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.nidaqStatusLabel)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer_2)


        self.flowLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.title_lanes = QLabel(ProtocolWindow)
        self.title_lanes.setObjectName(u"title_lanes")

        self.rightLayout.addWidget(self.title_lanes)

        self.pushButton = QPushButton(ProtocolWindow)
        self.pushButton.setObjectName(u"pushButton")

        self.rightLayout.addWidget(self.pushButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.rightLayout.addItem(self.verticalSpacer)


        self.flowLayout.addLayout(self.rightLayout)

        self.flowLayout.setStretch(0, 3)
        self.flowLayout.setStretch(1, 5)

        self.retranslateUi(ProtocolWindow)

        QMetaObject.connectSlotsByName(ProtocolWindow)
    # setupUi

    def retranslateUi(self, ProtocolWindow):
        ProtocolWindow.setWindowTitle(QCoreApplication.translate("ProtocolWindow", u"Protocol Editor", None))
        self.title_controls.setText(QCoreApplication.translate("ProtocolWindow", u"Controls", None))
        self.positiveChannelLabel.setText(QCoreApplication.translate("ProtocolWindow", u"Positive channel", None))
        self.negativeChannelLabel.setText(QCoreApplication.translate("ProtocolWindow", u"Negative channel", None))
        self.nidaqStatusLabel.setText(QCoreApplication.translate("ProtocolWindow", u"Status: NI-DAQ unavailable", None))
        self.title_lanes.setText(QCoreApplication.translate("ProtocolWindow", u"Selected lanes", None))
        self.pushButton.setText(QCoreApplication.translate("ProtocolWindow", u"Run", None))
    # retranslateUi

