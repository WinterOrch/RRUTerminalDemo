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

        deviceLayout = QtWidgets.QGridLayout()
        deviceLayout.addLayout(self.freqLayout, 0, 0)
        deviceLayout.addWidget(self.vLineFrame, 0, 1)
        deviceLayout.addWidget(self.setFreqButton, 0, 2)
        settingGroup.setLayout(deviceLayout)

        '''SLOT PANE'''
        slot_setting_layout = QtWidgets.QGroupBox("Slot Setting")

        self.typeLabel = QtWidgets.QLabel("Slot Set")
        self.typeComboBox = QtWidgets.QComboBox()
        for i in range(len(RRUCmd.slot_type_str)):
            self.typeComboBox.addItem(RRUCmd.slot_type_str[i])
        self.slotEdit = QtWidgets.QLineEdit()

        self.setButton = QtWidgets.QPushButton("Set")

        slot_layout = QtWidgets.QGridLayout()
        slot_layout.addWidget(self.typeComboBox, 0, 0)
        slot_layout.addWidget(self.typeLabel, 0, 1)
        slot_layout.addWidget(self.slotEdit, 0, 2)
        slot_layout.addWidget(self.setButton, 0, 4)
        slot_layout.setSpacing(pubSpacing)
        slot_setting_layout.setLayout(slot_layout)
        '''END OF SLOT PANE'''

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(settingGroup)
        mainLayout.addWidget(slot_setting_layout)
        mainLayout.addSpacing(mainSpacing)
        self.setLayout(mainLayout)

        self.add_signal()

        self.tdd_slot = ''
        self.s_slot = ''
    
    def add_signal(self):
        self.setFreqButton.clicked.connect(self.send)
        self.typeComboBox.currentIndexChanged.connect(self.display_slot)
        self.setButton.clicked.connect(self.set_slot)
        
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

        pass    # TODO Not done yet

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

    def set_slot(self):
        pass    # TODO ADD Valid Check and RRUCmd
        slot2set = self.slotEdit.text().strip()
        if valid_check(slot2set):
            if self.typeComboBox.currentText() == RRUCmd.slot_type_str[0] and slot2set != self.tdd_slot:
                cmd = RRUCmd.set_tdd_slot(self.parentWidget.get_option(), slot2set)
                self.deviceTranSignal.emit(cmd)
                res = TelRepository.telnet_instance.execute_command(cmd)
                self.deviceRvdSignal.emit(res)

                self.refresh_tdd_slot()
            elif self.typeComboBox.currentText() == RRUCmd.slot_type_str[1] and slot2set != self.s_slot:
                cmd = RRUCmd.set_s_slot(self.parentWidget.get_option(), slot2set)
                self.deviceTranSignal.emit(cmd)
                res = TelRepository.telnet_instance.execute_command(cmd)
                self.deviceRvdSignal.emit(res)

                self.refresh_s_slot()

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
        pass    # TODO ADD Valid Check and RRUCmd
        cmd = RRUCmd.get_tx_gain(self.parentWidget.get_option())
        self.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.deviceRvdSignal.emit(res)

        value = re.search(r'\d', res)
        if value is not None:
            self.txGainValueLabel.setText(str(value.group()))
            self.txGainValueLabel.setStyleSheet(displayValueStyle)
            self.txGainEdit.setText(str(value.group()))
        else:
            self.warning("Tx Gain cannot be got properly")

    def refresh_rx_gain(self):
        pass    # TODO ADD Valid Check and RRUCmd
        cmd = RRUCmd.get_rx_gain(self.parentWidget.get_option())
        self.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.deviceRvdSignal.emit(res)

        value = re.search(r'\d', res)
        if value is not None:
            self.rxGainValueLabel.setText(str(value.group()))
            self.rxGainValueLabel.setStyleSheet(displayValueStyle)
            self.rxGainEdit.setText(str(value.group()))
        else:
            self.warning("Rx Gain cannot be got properly")
            
    def refresh_s_slot(self):
        pass    # TODO ADD Valid Check and RRUCmd
        cmd = RRUCmd.get_s_slot(self.parentWidget.get_option())
        self.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.deviceRvdSignal.emit(res)

        value = re.search(r'\d', res)
        if value is not None:
            self.s_slot = value
            self.display_slot()
        else:
            self.warning("Special Slot cannot be got properly")
        
    def refresh_tdd_slot(self):
        pass    # TODO ADD Valid Check and RRUCmd
        cmd = RRUCmd.get_tdd_slot(self.parentWidget.get_option())
        self.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.deviceRvdSignal.emit(res)

        value = re.search(r'\d', res)
        if value is not None:
            self.tdd_slot = value
            self.display_slot()
        else:
            self.warning("TDD Slot cannot be got properly")
        
    def display_slot(self):
        if self.typeComboBox.currentText() == RRUCmd.slot_type_str[0]:
            self.slotEdit.setText(self.tdd_slot)
        elif self.typeComboBox.currentText() == RRUCmd.slot_type_str[1]:
            self.slotEdit.setText(self.s_slot)

    def test(self):
        self.deviceTranSignal.emit(self.parentWidget.get_option())
        self.deviceRvdSignal.emit("I'm fine")

    def warning(self, info):
        self.warningSignal.emit(info)

    def refresh_all(self, connect):
        if connect:
            self.refresh_freq()
            self.refresh_tx_gain()
            self.refresh_rx_gain()
            self.refresh_s_slot()
            self.refresh_tdd_slot()
            # TODO ADD

        self.setEnabled(connect)


# TODO 设定值合法性检验
def valid_check(text):
    if len(text.strip()):
        return True
    else:
        return False
