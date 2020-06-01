import re

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.TelRepository import TelRepository

displayValueStyle = "color:blue"
displayValueTempStyle = "color:red"
valueEditStyle = "height: 22px"
setButtonStyle = "height: 90px"

pubSpacing = 10
mainSpacing = 2


class DeviceTab(QtWidgets.QWidget):
    deviceTranSignal = pyqtSignal(str)
    deviceRvdSignal = pyqtSignal(str)

    warningSignal = pyqtSignal(str)

    def __init__(self, parent):
        super(DeviceTab, self).__init__()
        self.parentWidget = parent

        settingGroup = QtWidgets.QGroupBox("Device Setting")

        self.getFrequencyLabel = QtWidgets.QLabel("Freq (kHz) ")
        self.setFrequencyLabel = QtWidgets.QLabel("Set Freq")
        self.freqValueLabel = QtWidgets.QLabel("000000")
        self.freqValueLabel.setStyleSheet(displayValueStyle)
        self.freqEdit = QtWidgets.QLineEdit()
        self.freqEdit.setStyleSheet(valueEditStyle)
        self.setFreqButton = QtWidgets.QPushButton("Send")
        self.setFreqButton.setStyleSheet(setButtonStyle)

        self.getTxGainLabel = QtWidgets.QLabel("Tx Gain")
        self.setTxGainLabel = QtWidgets.QLabel("Set Gain")
        self.txGainValueLabel = QtWidgets.QLabel("000000")
        self.txGainValueLabel.setStyleSheet(displayValueStyle)
        self.txGainEdit = QtWidgets.QLineEdit()
        self.txGainEdit.setStyleSheet(valueEditStyle)

        self.getRxGainLabel = QtWidgets.QLabel("Rx Att")
        self.setRxGainLabel = QtWidgets.QLabel("Set Gain")
        self.rxGainValueLabel = QtWidgets.QLabel("000000")
        self.rxGainValueLabel.setStyleSheet(displayValueStyle)
        self.rxGainEdit = QtWidgets.QLineEdit()
        self.rxGainEdit.setStyleSheet(valueEditStyle)

        self.freqLayout = QtWidgets.QGridLayout()
        self.freqLayout.addWidget(self.getFrequencyLabel, 0, 0)
        self.freqLayout.addWidget(self.freqValueLabel, 0, 1)
        self.freqLayout.addWidget(self.setFrequencyLabel, 0, 2)
        self.freqLayout.addWidget(self.freqEdit, 0, 3)
        self.freqLayout.addWidget(self.getTxGainLabel, 1, 0)
        self.freqLayout.addWidget(self.txGainValueLabel, 1, 1)
        self.freqLayout.addWidget(self.setTxGainLabel, 1, 2)
        self.freqLayout.addWidget(self.txGainEdit, 1, 3)
        self.freqLayout.addWidget(self.getRxGainLabel, 2, 0)
        self.freqLayout.addWidget(self.rxGainValueLabel, 2, 1)
        self.freqLayout.addWidget(self.setRxGainLabel, 2, 2)
        self.freqLayout.addWidget(self.rxGainEdit, 2, 3)
        self.freqLayout.setSpacing(pubSpacing)

        self.vLineFrame = QtWidgets.QFrame()
        self.vLineFrame.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)

        '''Signal'''
        self.setFreqButton.clicked.connect(self.send)
        ''''''

        deviceLayout = QtWidgets.QGridLayout()
        deviceLayout.addLayout(self.freqLayout, 0, 0)
        deviceLayout.addWidget(self.vLineFrame, 0, 1)
        deviceLayout.addWidget(self.setFreqButton, 0, 2)
        settingGroup.setLayout(deviceLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(settingGroup)
        mainLayout.addSpacing(mainSpacing)
        self.setLayout(mainLayout)

    def send(self):
        freq2set = self.freqEdit.text().strip()
        if freq2set != self.freqValueLabel.text():
            if valid_check(freq2set):
                self.freqValueLabel.setStyleSheet(displayValueTempStyle)
                cmd = RRUCmd.config_frequency(self.parentWidget.get_option(), freq2set)
                self.deviceTranSignal.emit(cmd)
                res = TelRepository.telnet_instance.execute_command(cmd)
                self.deviceRvdSignal.emit(res)

                self.refresh_freq()

        txGain2set = self.freqEdit.text().strip()
        if txGain2set != self.freqValueLabel.text():
            if valid_check(txGain2set):
                self.txGainValueLabel.setStyleSheet(displayValueTempStyle)
                cmd = RRUCmd.set_tx_gain(self.parentWidget.get_option(), txGain2set)
                self.deviceTranSignal.emit(cmd)
                res = TelRepository.telnet_instance.execute_command(cmd)
                self.deviceRvdSignal.emit(res)

                self.refresh_tx_gain()

        rxGain2set = self.freqEdit.text().strip()
        if rxGain2set != self.freqValueLabel.text():
            if valid_check(rxGain2set):
                self.rxGainValueLabel.setStyleSheet(displayValueTempStyle)
                cmd = RRUCmd.set_rx_gain(self.parentWidget.get_option(), rxGain2set)
                self.deviceTranSignal.emit(cmd)
                res = TelRepository.telnet_instance.execute_command(cmd)
                self.deviceRvdSignal.emit(res)

                self.refresh_rx_gain()

    def refresh_freq(self):
        cmd = RRUCmd.get_frequency(self.parentWidget.get_option())
        self.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.deviceRvdSignal.emit(res)

        value = RespFilter.value_filter(res, RespFilter.FREQUENCY_ASSERTION)
        if value is not None:
            self.freqValueLabel.setText(str(value.group()))
            self.freqValueLabel.setStyleSheet(displayValueStyle)
            self.freqEdit.setText(str(value.group()))
        else:
            self.warning("Frequency cannot be refreshed properly")

    def refresh_tx_gain(self):
        cmd = RRUCmd.get_tx_gain(self.parentWidget.get_option())
        self.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.deviceRvdSignal.emit(res)

        value = re.search(r'\d', res)  # TODO
        if value is not None:
            self.txGainValueLabel.setText(str(value.group()))
            self.txGainValueLabel.setStyleSheet(displayValueStyle)
            self.txGainEdit.setText(str(value.group()))
        else:
            self.warning("Tx Gain cannot be refreshed properly")

    def refresh_rx_gain(self):
        cmd = RRUCmd.get_rx_gain(self.parentWidget.get_option())
        self.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.deviceRvdSignal.emit(res)

        value = re.search(r'\d', res)  # TODO
        if value is not None:
            self.rxGainValueLabel.setText(str(value.group()))
            self.rxGainValueLabel.setStyleSheet(displayValueStyle)
            self.rxGainEdit.setText(str(value.group()))
        else:
            self.warning("Rx Gain cannot be refreshed properly")

    def test(self):
        self.deviceTranSignal.emit(self.parentWidget.get_option())
        self.deviceRvdSignal.emit("I'm fine")

    def warning(self, info):
        self.warningSignal.emit(info)


# TODO 设定值合法性检验
def valid_check(text):
    if len(text.strip()):
        return True
    else:
        return False
