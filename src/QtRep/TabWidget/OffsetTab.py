import re

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

import src.QtRep.OperateWidget
from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.TelRepository import TelRepository

mainSpacing = 2


class OffsetTab(QtWidgets.QWidget):
    deviceTranSignal = pyqtSignal(str)
    deviceRvdSignal = pyqtSignal(str)

    warningSignal = pyqtSignal(str)

    def __init__(self, parent):
        super(OffsetTab, self).__init__()
        self.parentWidget = parent

        offsetGroup = QtWidgets.QGroupBox("Offset Setting")

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(offsetGroup)
        mainLayout.addSpacing(mainSpacing)
        self.setLayout(mainLayout)
