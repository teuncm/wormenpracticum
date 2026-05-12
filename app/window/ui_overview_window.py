# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'overview_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QFormLayout,
    QHBoxLayout, QLabel, QSizePolicy, QSlider,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_OverviewWindow(object):
    def setupUi(self, OverviewWindow):
        if not OverviewWindow.objectName():
            OverviewWindow.setObjectName(u"OverviewWindow")
        OverviewWindow.resize(562, 317)
        self.flowLayout = QHBoxLayout(OverviewWindow)
        self.flowLayout.setObjectName(u"flowLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.title_filter = QLabel(OverviewWindow)
        self.title_filter.setObjectName(u"title_filter")

        self.leftLayout.addWidget(self.title_filter)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.lowPassLabel = QLabel(OverviewWindow)
        self.lowPassLabel.setObjectName(u"lowPassLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lowPassLabel)

        self.doubleSpinBox = QDoubleSpinBox(OverviewWindow)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.doubleSpinBox)

        self.suppress50HzLabel = QLabel(OverviewWindow)
        self.suppress50HzLabel.setObjectName(u"suppress50HzLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.suppress50HzLabel)

        self.suppress50HzCheckBox = QCheckBox(OverviewWindow)
        self.suppress50HzCheckBox.setObjectName(u"suppress50HzCheckBox")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.suppress50HzCheckBox)

        self.removeDCOffsetLabel = QLabel(OverviewWindow)
        self.removeDCOffsetLabel.setObjectName(u"removeDCOffsetLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.removeDCOffsetLabel)

        self.removeDCOffsetCheckBox = QCheckBox(OverviewWindow)
        self.removeDCOffsetCheckBox.setObjectName(u"removeDCOffsetCheckBox")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.removeDCOffsetCheckBox)


        self.leftLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer)

        self.title_options = QLabel(OverviewWindow)
        self.title_options.setObjectName(u"title_options")

        self.leftLayout.addWidget(self.title_options)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.channelLabel = QLabel(OverviewWindow)
        self.channelLabel.setObjectName(u"channelLabel")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.channelLabel)

        self.channelSlider = QSlider(OverviewWindow)
        self.channelSlider.setObjectName(u"channelSlider")
        self.channelSlider.setOrientation(Qt.Orientation.Horizontal)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.channelSlider)

        self.amplitudeLabel = QLabel(OverviewWindow)
        self.amplitudeLabel.setObjectName(u"amplitudeLabel")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.amplitudeLabel)

        self.ampSlider = QSlider(OverviewWindow)
        self.ampSlider.setObjectName(u"ampSlider")
        self.ampSlider.setOrientation(Qt.Orientation.Horizontal)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.ampSlider)


        self.leftLayout.addLayout(self.formLayout_2)


        self.flowLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.title_response = QLabel(OverviewWindow)
        self.title_response.setObjectName(u"title_response")

        self.rightLayout.addWidget(self.title_response)


        self.flowLayout.addLayout(self.rightLayout)

        self.flowLayout.setStretch(0, 3)
        self.flowLayout.setStretch(1, 5)

        self.retranslateUi(OverviewWindow)

        QMetaObject.connectSlotsByName(OverviewWindow)
    # setupUi

    def retranslateUi(self, OverviewWindow):
        OverviewWindow.setWindowTitle(QCoreApplication.translate("OverviewWindow", u"Form", None))
        self.title_filter.setText(QCoreApplication.translate("OverviewWindow", u"Filter options", None))
        self.lowPassLabel.setText(QCoreApplication.translate("OverviewWindow", u"Low pass (Hz)", None))
        self.suppress50HzLabel.setText(QCoreApplication.translate("OverviewWindow", u"Suppress 50 Hz", None))
        self.removeDCOffsetLabel.setText(QCoreApplication.translate("OverviewWindow", u"Remove DC offset", None))
        self.title_options.setText(QCoreApplication.translate("OverviewWindow", u"Plot options", None))
        self.channelLabel.setText(QCoreApplication.translate("OverviewWindow", u"Channel", None))
        self.amplitudeLabel.setText(QCoreApplication.translate("OverviewWindow", u"Gain", None))
        self.title_response.setText(QCoreApplication.translate("OverviewWindow", u"Evoked response overview plot", None))
    # retranslateUi

