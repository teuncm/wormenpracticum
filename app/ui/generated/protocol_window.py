# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'protocol_window.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_ProtocolWindow(object):
    def setupUi(self, ProtocolWindow):
        if not ProtocolWindow.objectName():
            ProtocolWindow.setObjectName(u"ProtocolWindow")
        ProtocolWindow.resize(739, 512)
        self.flowLayout = QHBoxLayout(ProtocolWindow)
        self.flowLayout.setObjectName(u"flowLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.title_controls = QLabel(ProtocolWindow)
        self.title_controls.setObjectName(u"title_controls")

        self.leftLayout.addWidget(self.title_controls)

        self.sampleRateLayout = QHBoxLayout()
        self.sampleRateLayout.setObjectName(u"sampleRateLayout")
        self.sampleRateLabel = QLabel(ProtocolWindow)
        self.sampleRateLabel.setObjectName(u"sampleRateLabel")

        self.sampleRateLayout.addWidget(self.sampleRateLabel)

        self.maxSampleRateLabel = QLabel(ProtocolWindow)
        self.maxSampleRateLabel.setObjectName(u"maxSampleRateLabel")

        self.sampleRateLayout.addWidget(self.maxSampleRateLabel)

        self.sampleRateDivisionLabel = QLabel(ProtocolWindow)
        self.sampleRateDivisionLabel.setObjectName(u"sampleRateDivisionLabel")

        self.sampleRateLayout.addWidget(self.sampleRateDivisionLabel)

        self.sampleRateDividerComboBox = QComboBox(ProtocolWindow)
        self.sampleRateDividerComboBox.setObjectName(u"sampleRateDividerComboBox")

        self.sampleRateLayout.addWidget(self.sampleRateDividerComboBox)

        self.sampleRateEqualsLabel = QLabel(ProtocolWindow)
        self.sampleRateEqualsLabel.setObjectName(u"sampleRateEqualsLabel")

        self.sampleRateLayout.addWidget(self.sampleRateEqualsLabel)

        self.actualSampleRateLabel = QLabel(ProtocolWindow)
        self.actualSampleRateLabel.setObjectName(u"actualSampleRateLabel")

        self.sampleRateLayout.addWidget(self.actualSampleRateLabel)


        self.leftLayout.addLayout(self.sampleRateLayout)

        self.nidaqStatusLabel = QLabel(ProtocolWindow)
        self.nidaqStatusLabel.setObjectName(u"nidaqStatusLabel")
        self.nidaqStatusLabel.setWordWrap(True)

        self.leftLayout.addWidget(self.nidaqStatusLabel)

        self.pushButton = QPushButton(ProtocolWindow)
        self.pushButton.setObjectName(u"pushButton")

        self.leftLayout.addWidget(self.pushButton)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer_2)


        self.flowLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.title_lanes = QLabel(ProtocolWindow)
        self.title_lanes.setObjectName(u"title_lanes")

        self.rightLayout.addWidget(self.title_lanes)


        self.flowLayout.addLayout(self.rightLayout)

        self.flowLayout.setStretch(0, 3)
        self.flowLayout.setStretch(1, 5)

        self.retranslateUi(ProtocolWindow)

        QMetaObject.connectSlotsByName(ProtocolWindow)
    # setupUi

    def retranslateUi(self, ProtocolWindow):
        ProtocolWindow.setWindowTitle(QCoreApplication.translate("ProtocolWindow", u"Protocol Editor", None))
        self.title_controls.setText(QCoreApplication.translate("ProtocolWindow", u"Stimulation parameters", None))
        self.sampleRateLabel.setText(QCoreApplication.translate("ProtocolWindow", u"Sample rate:", None))
        self.maxSampleRateLabel.setText(QCoreApplication.translate("ProtocolWindow", u"0 Hz", None))
        self.sampleRateDivisionLabel.setText(QCoreApplication.translate("ProtocolWindow", u"\u00f7", None))
#if QT_CONFIG(accessibility)
        self.sampleRateDividerComboBox.setAccessibleName(QCoreApplication.translate("ProtocolWindow", u"Sample rate divider", None))
#endif // QT_CONFIG(accessibility)
        self.sampleRateEqualsLabel.setText(QCoreApplication.translate("ProtocolWindow", u"=", None))
        self.actualSampleRateLabel.setText(QCoreApplication.translate("ProtocolWindow", u"0 Hz", None))
        self.nidaqStatusLabel.setText(QCoreApplication.translate("ProtocolWindow", u"Status: NI-DAQ unavailable", None))
        self.pushButton.setText(QCoreApplication.translate("ProtocolWindow", u"Record", None))
        self.title_lanes.setText(QCoreApplication.translate("ProtocolWindow", u"Pin assignments", None))
    # retranslateUi

