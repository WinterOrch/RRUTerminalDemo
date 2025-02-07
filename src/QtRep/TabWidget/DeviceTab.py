import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QThreadPool

from src.QtRep.Component.ValueLabel import ValueLabel
from src.QtRep.NonQSSStyle import NonQSSStyle
from src.RRU.Antenna import Antenna
from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.Runnable.TelnetWorker import TelnetWorker, WorkerSignals
from src.Telnet.TelRepository import TelRepository
from src.Tool.ValidCheck import ValidCheck

pubSpacing = 10
mainSpacing = 2

TEST = False


class DeviceTab(QtWidgets.QWidget):
    deviceTranSignal = pyqtSignal(str)
    deviceRvdSignal = pyqtSignal(str)

    warningSignal = pyqtSignal(str)

    connectionOutSignal = pyqtSignal()

    def __init__(self, parent):
        super(DeviceTab, self).__init__()
        self.parentWidget = parent

        # Setting Flags
        self.mod_dimension = True
        self.auto_fresh = True

        self._init_ui()
        self.add_signal()
        self.set_logger()

        self._init_bean()

        self.debug_counter = 0

    @staticmethod
    def set_logger():
        logging.basicConfig(filename='../log/' + __name__ + '.log',
                            format='[%(asctime)s-%(filename)s-%(funcName)s-%(levelname)s:%(message)s]',
                            level=logging.DEBUG, filemode='a', datefmt='%Y-%m-%d %I:%M:%S %p')

    def _init_ui(self):
        """DEVICE SETTING PANE"""
        settingGroup = QtWidgets.QGroupBox("Device Setting")

        self.getFrequencyLabel = QtWidgets.QLabel("Freq (Hz) ")
        self.setFrequencyLabel = QtWidgets.QLabel("Set Freq")
        self.freqValueLabel = ValueLabel("000000", RRUCmd.GET_FREQUENCY)
        self.freqValueLabel.refreshSig.connect(self.quick_refresh)
        self.freqValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.freqEdit = QtWidgets.QLineEdit()
        self.freqEdit.setStyleSheet(NonQSSStyle.valueEditStyle)
        self.setFreqButton = QtWidgets.QPushButton("Send")
        self.setFreqButton.setStyleSheet(NonQSSStyle.setButtonBigStyle)
        self.freqEditTip = ["(2.565 - 2.625 GHz, Correct to 1 Hz)", "(3.45 - 3.55 GHz, Correct to 1 Hz)",
                            "(4.85 - 4.95 GHz, Correct to 1 Hz)"]
        self.freqEdit.setPlaceholderText(self.freqEditTip[0])

        if self.mod_dimension:
            self.getTxGainLabel = QtWidgets.QLabel("Tx atten (dB)")
        else:
            self.getTxGainLabel = QtWidgets.QLabel("TX atten (mdB)")
        self.setTxGainLabel = QtWidgets.QLabel("Set Gain")
        self.txGainValueLabel = ValueLabel("000000", RRUCmd.GET_TX_ATTEN)
        self.txGainValueLabel.refreshSig.connect(self.quick_refresh)
        self.txGainValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.txGainEdit = QtWidgets.QLineEdit()
        self.txGainEdit.setStyleSheet(NonQSSStyle.valueEditStyle)
        if self.mod_dimension:
            txGainTip = "(-41.95 - 0 dB, Correct to 0.001 dB)"
        else:
            txGainTip = "(-41950 - 0 mdB, Correct to 1 mdB)"
        self.txGainEdit.setPlaceholderText(txGainTip)

        if self.mod_dimension:
            self.getRxGainLabel = QtWidgets.QLabel("RX gain atten (dB)")
        else:
            self.getRxGainLabel = QtWidgets.QLabel("RX gain atten")
        self.setRxGainLabel = QtWidgets.QLabel("Set Gain")
        self.rxGainValueLabel = ValueLabel("000000", RRUCmd.GET_RX_GAIN)
        self.rxGainValueLabel.refreshSig.connect(self.quick_refresh)
        self.rxGainValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.rxGainEdit = QtWidgets.QLineEdit()
        self.rxGainEdit.setStyleSheet(NonQSSStyle.valueEditStyle)
        if self.mod_dimension:
            rxGainTip = "(-30 - 0 dB, Correct to 0.25 dB)"
        else:
            rxGainTip = "(195 - 255, Correct to 0.5)"
        self.rxGainEdit.setPlaceholderText(rxGainTip)

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
        '''END OF DEVICE SETTING PANE'''

        '''SLOT PANE'''
        slot_setting_layout = QtWidgets.QGroupBox("Slot Setting")

        self.typeLabel = QtWidgets.QLabel("Slot Set")
        self.typeComboBox = QtWidgets.QComboBox()
        for i in range(len(RRUCmd.slot_type_str)):
            self.typeComboBox.addItem(RRUCmd.slot_type_str[i])
        self.slotValueLabel = ValueLabel("000000", RRUCmd.GET_TDD_SLOT)
        self.slotValueLabel.refreshSig.connect(self.quick_refresh)
        self.slotValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.slotEdit = QtWidgets.QLineEdit()

        self.setButton = QtWidgets.QPushButton("Set")

        slot_layout = QtWidgets.QGridLayout()
        slot_layout.addWidget(self.typeComboBox, 0, 0)
        slot_layout.addWidget(self.typeLabel, 0, 1)
        slot_layout.addWidget(self.slotValueLabel, 0, 2)
        slot_layout.addWidget(self.slotEdit, 0, 3)
        slot_layout.addWidget(self.setButton, 0, 5)
        slot_layout.setSpacing(pubSpacing)
        slot_setting_layout.setLayout(slot_layout)
        '''END OF SLOT PANE'''

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(settingGroup)
        mainLayout.addWidget(slot_setting_layout)
        mainLayout.addSpacing(mainSpacing)
        self.setLayout(mainLayout)

    def _init_bean(self):
        self.antenna_bean_arr = []
        for i in range(max(RRUCmd.ant_num)):
            self.antenna_bean_arr.append(Antenna())
        self.antenna_index = 0

    def add_signal(self):
        if TEST:
            self.setFreqButton.clicked.connect(self.test)
        else:
            self.setFreqButton.clicked.connect(self.send)
        self.typeComboBox.currentIndexChanged.connect(self.display_slot)
        self.setButton.clicked.connect(self.set_slot)

        self.freqEdit.textChanged.connect(self.freq_back2normal)
        self.freqEdit.returnPressed.connect(self.set_freq)
        self.rxGainEdit.textChanged.connect(self.rx_back2normal)
        self.rxGainEdit.returnPressed.connect(self.set_rx_gain)
        self.txGainEdit.textChanged.connect(self.tx_back2normal)
        self.txGainEdit.returnPressed.connect(self.set_tx_gain)
        self.slotEdit.textChanged.connect(self.slot_back2normal)
        self.slotEdit.returnPressed.connect(self.set_slot)

    def _console_slot(self, case, msg):
        if case == WorkerSignals.TRAN_SIGNAL:
            self.deviceTranSignal.emit(msg)
        elif case == WorkerSignals.RECV_SIGNAL:
            self.deviceRvdSignal.emit(msg)

    def send(self):
        self.set_freq()
        self.set_tx_gain()
        self.set_rx_gain()

    def test(self):
        text = "txAtten0:36000 (mdB)"
        self.get_resp_handler(RRUCmd.GET_TX_ATTEN, text)
        self.display()
        text = "rxGain0:200 (mdB)"
        self.get_resp_handler(RRUCmd.GET_RX_GAIN, text)
        self.display()

    def _debug_send(self):
        cmd = "DEBUG"

        thread = TelnetWorker(RRUCmd.CMD_TYPE_DEBUG, cmd)
        thread.signals.consoleDisplay.connect(self._console_slot)
        thread.signals.connectionLost.connect(self.slot_connection_out_signal)
        thread.signals.error.connect(self.log_error)
        thread.signals.result.connect(self.get_resp_handler)
        QThreadPool.globalInstance().start(thread)

    def _process_cmd(self, cmd_type: int, cmd_case: int, cmd: str):
        thread = TelnetWorker(cmd_case, cmd)
        thread.signals.consoleDisplay.connect(self._console_slot)
        thread.signals.connectionLost.connect(self.slot_connection_out_signal)
        thread.signals.error.connect(self.log_error)

        if cmd_type == RRUCmd.CMD_TYPE_GET:
            thread.signals.result.connect(self.get_resp_handler)
        elif cmd_type == RRUCmd.CMD_TYPE_SET:
            thread.signals.result.connect(self.set_resp_handler)

        QThreadPool.globalInstance().start(thread)

    def set_freq(self):
        freq2set = self.freqEdit.text().strip()
        if freq2set != self.freqValueLabel.text():
            if ValidCheck.freq(self.parentWidget.get_option(), freq2set):
                self.freqValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                cmd = RRUCmd.config_frequency(self.parentWidget.get_option(), freq2set)

                self._process_cmd(RRUCmd.CMD_TYPE_SET, RRUCmd.SET_FREQUENCY, cmd)
            else:
                self.freqEdit.setStyleSheet(NonQSSStyle.warningStyle)

    def set_rx_gain(self):
        rxGain2set = self.rxGainEdit.text().strip()
        if rxGain2set != self.rxGainValueLabel.text() and len(rxGain2set) != 0:
            if self.mod_dimension:
                # Transfer Unit
                match = ValidCheck.filter(ValidCheck.GAIN_RE,
                                          ValidCheck.transfer_attenuation(rxGain2set, RRUCmd.SET_RX_GAIN))
            else:
                match = ValidCheck.filter(ValidCheck.GAIN_RE, rxGain2set)
            if match is not None:
                self.rxGainValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                cmd = RRUCmd.set_rx_gain(self.parentWidget.get_option(), self.parentWidget.get_ant_num(), match.group())
                self.antenna_bean_arr[self.antenna_index].rxGainAttenuationOutDated = True

                self._process_cmd(RRUCmd.CMD_TYPE_SET, RRUCmd.SET_RX_GAIN, cmd)
            else:
                self.rxGainEdit.setStyleSheet(NonQSSStyle.warningStyle)

    def set_tx_gain(self):
        txGain2set = self.txGainEdit.text().strip()
        if txGain2set != self.txGainValueLabel.text() and len(txGain2set) != 0:
            if self.mod_dimension:
                # Transfer Unit
                txGain2set = ValidCheck.transfer_attenuation(txGain2set, RRUCmd.SET_TX_ATTEN)
            if ValidCheck.atten(txGain2set):
                self.txGainValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                cmd = RRUCmd.set_tx_gain(self.parentWidget.get_option(), self.parentWidget.get_ant_num(), txGain2set)
                self.antenna_bean_arr[self.antenna_index].txAttenuationOutDated = True

                self._process_cmd(RRUCmd.CMD_TYPE_SET, RRUCmd.SET_TX_ATTEN, cmd)
            else:
                self.txGainEdit.setStyleSheet(NonQSSStyle.warningStyle)

    def set_slot(self):
        # TODO Valid Check not added yet
        slot2set = self.slotEdit.text().strip()
        if slot2set is not None:
            self.slotValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
            if self.typeComboBox.currentText() == RRUCmd.slot_type_str[0] and slot2set != self.slotValueLabel.text():
                cmd = RRUCmd.set_tdd_slot(self.parentWidget.get_option(), self.parentWidget.get_ant_num(), slot2set)
                self.antenna_bean_arr[self.antenna_index].tddSlotOutDated = True

                self._process_cmd(RRUCmd.CMD_TYPE_SET, RRUCmd.SET_TDD_SLOT, cmd)
            elif self.typeComboBox.currentText() == RRUCmd.slot_type_str[1] and slot2set != self.slotValueLabel.text():
                cmd = RRUCmd.set_s_slot(self.parentWidget.get_option(), self.parentWidget.get_ant_num(), slot2set)
                self.antenna_bean_arr[self.antenna_index].sSlotOutDated = True

                self._process_cmd(RRUCmd.CMD_TYPE_SET, RRUCmd.SET_S_SLOT, cmd)

    def get_resp_handler(self, case, res):
        """Work Thread Get the Value and Send to refresh_resp_handler for displaying
                update data mainly by rewriting antenna_bean and refresh display
                change dimension in the mean time
        """
        if case == RRUCmd.GET_FREQUENCY:
            value = RespFilter.value_filter(res, RespFilter.FREQUENCY_ASSERTION)
            if value is not None:
                self.freqValueLabel.setText(str(value.group()))
                logging.debug("FREQ GET AS" + str(value.group()))
                self.freqValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
                self.freqEdit.setText(str(value.group()))
                self.display()
                if not TEST:
                    self.initialize_update()
            else:
                self.freqValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("Frequency cannot be refreshed properly")
        elif case == RRUCmd.GET_TX_ATTEN:
            value = RespFilter.value_filter_with_ant(res, RespFilter.TX_ATTEN_ASSERTION, self.antenna_index)
            i = 0
            if value is None:
                if self.antenna_index == i:
                    i += 1
                while value is None and i < RRUCmd.ant_num[self.parentWidget.option]:
                    value = RespFilter.value_filter_with_ant(res, RespFilter.TX_ATTEN_ASSERTION, i)
                    i += 1
                i -= 1
            else:
                i = self.antenna_index
            if value is not None:
                res = str(value.group())
                if self.mod_dimension:
                    # Transfer Unit
                    res = ValidCheck.transfer_attenuation(res, RRUCmd.GET_TX_ATTEN)
                self.antenna_bean_arr[i].txAttenuation = res
                logging.debug("TX GET AS" + str(value.group()) + "For Ant" + str(i) + "TRAN TO" + res)
                self.antenna_bean_arr[i].txAttenuation2Set = res
                self.antenna_bean_arr[i].txAttenuationOutDated = False
                self.antenna_bean_arr[i].txAttenuationInitialized = True
                self.display()
                if not TEST:
                    self.initialize_update()
            else:
                self.txGainValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("TX's attenuation cannot be refreshed properly")
        elif case == RRUCmd.GET_RX_GAIN:
            value = RespFilter.value_filter_with_ant(res, RespFilter.RX_GAIN_ASSERTION, self.antenna_index)
            i = 0
            if value is None:
                if self.antenna_index == i:
                    i += 1
                while value is None and i < RRUCmd.ant_num[self.parentWidget.option]:
                    value = RespFilter.value_filter_with_ant(res, RespFilter.RX_GAIN_ASSERTION, i)
                    i += 1
                i -= 1
            else:
                i = self.antenna_index
            if value is not None:
                res = str(value.group())
                if self.mod_dimension:
                    # Transfer Unit
                    res = ValidCheck.transfer_attenuation(res, RRUCmd.GET_RX_GAIN)
                self.antenna_bean_arr[i].rxGainAttenuation = res
                logging.debug("RX GET AS" + str(value.group()) + "For Ant" + str(i) + "TRAN TO" + res)
                self.antenna_bean_arr[i].rxGainAttenuation2Set = res
                self.antenna_bean_arr[i].rxGainAttenuationOutDated = False
                self.antenna_bean_arr[i].rxGainAttenuationInitialized = True
                self.display()
                if not TEST:
                    self.initialize_update()
            else:
                self.rxGainValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("RX's Gain attenuation cannot be refreshed properly")
        elif case == RRUCmd.GET_S_SLOT:
            value = RespFilter.value_filter_with_ant(res, RespFilter.RX_GAIN_ASSERTION, self.antenna_index)
            if value is not None:
                self.antenna_bean_arr[self.antenna_index].sSlot = str(value.group())
                self.antenna_bean_arr[self.antenna_index].sSlot2Set = str(value.group())
                self.antenna_bean_arr[self.antenna_index].sSlotOutDated = False
                self.display()
            else:
                if self.typeComboBox.currentText() == RRUCmd.slot_type_str[1]:
                    self.slotValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("Special Slot cannot be refreshed properly")
        elif case == RRUCmd.GET_TDD_SLOT:
            value = RespFilter.value_filter_with_ant(res, RespFilter.RX_GAIN_ASSERTION, self.antenna_index)
            if value is not None:
                self.antenna_bean_arr[self.antenna_index].tddSlot = str(value.group())
                self.antenna_bean_arr[self.antenna_index].tddSlot2Set = str(value.group())
                self.antenna_bean_arr[self.antenna_index].tddSlotOutDated = False
                self.display()
            else:
                if self.typeComboBox.currentText() == RRUCmd.slot_type_str[0]:
                    self.slotValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("TDD Slot cannot be refreshed properly")

    def initialize_update(self):
        """在初始化自动刷新过程中持续刷新不同天线的收发增益
        每次刷新完收或发增益后都会触发这一方法，以检查是否所有天线的收发增益都经过了初始化
        """
        for i in range(RRUCmd.ant_num[self.parentWidget.option]):
            if not self.antenna_bean_arr[i].txAttenuationInitialized:
                cmd = RRUCmd.get_tx_gain(self.parentWidget.get_option(), str(i))
                self._process_cmd(RRUCmd.CMD_TYPE_GET, RRUCmd.GET_TX_ATTEN, cmd)
                break
            elif not self.antenna_bean_arr[i].rxGainAttenuationInitialized:
                cmd = RRUCmd.get_rx_gain(self.parentWidget.get_option(), str(i))
                self._process_cmd(RRUCmd.CMD_TYPE_GET, RRUCmd.GET_RX_GAIN, cmd)
                break
            # TODO

    def refresh_freq(self):
        cmd = RRUCmd.get_frequency(self.parentWidget.get_option())

        self._process_cmd(RRUCmd.CMD_TYPE_GET, RRUCmd.GET_FREQUENCY, cmd)

    def refresh_tx_gain(self):
        cmd = RRUCmd.get_tx_gain(self.parentWidget.get_option(), self.parentWidget.get_ant_num())

        self._process_cmd(RRUCmd.CMD_TYPE_GET, RRUCmd.GET_TX_ATTEN, cmd)

    def refresh_rx_gain(self):
        cmd = RRUCmd.get_rx_gain(self.parentWidget.get_option(), self.parentWidget.get_ant_num())

        self._process_cmd(RRUCmd.CMD_TYPE_GET, RRUCmd.GET_RX_GAIN, cmd)

    def refresh_s_slot(self):
        cmd = RRUCmd.get_s_slot(self.parentWidget.get_option(), self.parentWidget.get_ant_num())

        self._process_cmd(RRUCmd.CMD_TYPE_GET, RRUCmd.GET_S_SLOT, cmd)

    def refresh_tdd_slot(self):
        cmd = RRUCmd.get_tdd_slot(self.parentWidget.get_option(), self.parentWidget.get_ant_num())

        self._process_cmd(RRUCmd.CMD_TYPE_GET, RRUCmd.GET_TDD_SLOT, cmd)

    def warning(self, info):
        self.warningSignal.emit(info)

    def refresh_all(self, connect):
        if connect:
            for i in range(RRUCmd.ant_num[self.parentWidget.option]):
                self.antenna_bean_arr.append(Antenna())
            self._refresh_all_value()
        else:
            self.antenna_bean_arr.clear()
        self.setEnabled(connect)

    def _refresh_all_value(self):
        if TelRepository.telnet_instance.isTelnetLogined:
            if self.auto_fresh:
                self.refresh_freq()

                self.refresh_tx_gain()
                # TODO ADD 不同天线的数值刷新仅需触发一次，之后会通过 initialize_update 方法自动刷新，遇到失败后会中断，须手动刷新，
                #  因此添加新功能时，为了实现自动刷新需要在 intialize_update 和 get_resp_handler 中进行添加和修改而不是这里

    def set_resp_handler(self, case, resp: str):
        if case == RRUCmd.SET_FREQUENCY:
            if not RespFilter.resp_check(resp):
                self.warning("Frequency cannot be set properly")
            else:
                self.refresh_freq()
        elif case == RRUCmd.SET_TX_ATTEN:
            if not RespFilter.resp_check(resp):
                self.warning("TX Attenuation cannot be set properly")
            else:
                self.refresh_tx_gain()
        elif case == RRUCmd.SET_RX_GAIN:
            if not RespFilter.resp_check(resp):
                self.warning("RX's Gain Attenuation cannot be set properly")
            else:
                self.refresh_rx_gain()
        elif case == RRUCmd.SET_TDD_SLOT:
            if not RespFilter.resp_check(resp):
                self.warning("TDD Slot cannot be set properly")
            else:
                self.refresh_tdd_slot()
        elif case == RRUCmd.SET_S_SLOT:
            if not RespFilter.resp_check(resp):
                self.warning("Special Slot cannot be set properly")
            else:
                self.refresh_s_slot()

    def slot_connection_out_signal(self):
        self.connectionOutSignal.emit()

    def freq_back2normal(self):
        self.freqEdit.setStyleSheet(NonQSSStyle.valueEditStyle)

    def rx_back2normal(self):
        self.antenna_bean_arr[self.antenna_index].rxGainAttenuation2Set = self.rxGainEdit.text()
        self.rxGainEdit.setStyleSheet(NonQSSStyle.valueEditStyle)

    def tx_back2normal(self):
        self.antenna_bean_arr[self.antenna_index].txAttenuation2Set = self.txGainEdit.text()
        self.txGainEdit.setStyleSheet(NonQSSStyle.valueEditStyle)

    def slot_back2normal(self):
        if self.typeComboBox.currentText() == RRUCmd.slot_type_str[0]:
            self.antenna_bean_arr[self.antenna_index].tddSlot2Set = self.slotEdit.text()
        elif self.typeComboBox.currentText() == RRUCmd.slot_type_str[1]:
            self.antenna_bean_arr[self.antenna_index].sSlot2Set = self.slotEdit.text()
        self.slotEdit.setStyleSheet(NonQSSStyle.valueEditStyle)

    def display_slot(self):
        self.slotEdit.textChanged.disconnect()
        if self.typeComboBox.currentText() == RRUCmd.slot_type_str[0]:
            self.slotValueLabel.cmd = RRUCmd.GET_TDD_SLOT
            self.slotValueLabel.setText(self.antenna_bean_arr[self.antenna_index].tddSlot)
            if self.antenna_bean_arr[self.antenna_index].tddSlotOutDated:
                self.slotValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
            else:
                self.slotValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
            self.slotEdit.setText(Antenna.not_none(self.antenna_bean_arr[self.antenna_index].tddSlot2Set))
        elif self.typeComboBox.currentText() == RRUCmd.slot_type_str[1]:
            self.slotValueLabel.cmd = RRUCmd.GET_S_SLOT
            self.slotValueLabel.setText(self.antenna_bean_arr[self.antenna_index].sSlot)
            if self.antenna_bean_arr[self.antenna_index].sSlotOutDated:
                self.slotValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
            else:
                self.slotValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
            self.slotEdit.setText(Antenna.not_none(self.antenna_bean_arr[self.antenna_index].sSlot2Set))
        self.slotEdit.textChanged.connect(self.slot_back2normal)

    def display(self):
        # RX's Gain attenuation
        self.rxGainValueLabel.setText(self.antenna_bean_arr[self.antenna_index].rxGainAttenuation)
        if self.antenna_bean_arr[self.antenna_index].rxGainAttenuationOutDated:
            self.rxGainValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
        else:
            self.rxGainValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.rxGainEdit.setText(Antenna.not_none(self.antenna_bean_arr[self.antenna_index].rxGainAttenuation2Set))
        # TX's attenuation
        self.txGainValueLabel.setText(self.antenna_bean_arr[self.antenna_index].txAttenuation)
        if self.antenna_bean_arr[self.antenna_index].txAttenuationOutDated:
            self.txGainValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
        else:
            self.txGainValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.txGainEdit.setText(Antenna.not_none(self.antenna_bean_arr[self.antenna_index].txAttenuation2Set))
        # Slot
        self.display_slot()

    def refresh_ant_num(self):
        if TelRepository.telnet_instance.isTelnetLogined:
            self.display()

    @staticmethod
    def log_error(t_error: tuple):
        s_error = ""
        for i in t_error:
            s_error += str(i) + " "
        logging.error(s_error)

    def quick_refresh(self, cmd):
        if TelRepository.telnet_instance.isTelnetLogined:
            if cmd == RRUCmd.GET_FREQUENCY:
                self.refresh_freq()
            elif cmd == RRUCmd.GET_TX_ATTEN:
                self.refresh_tx_gain()
            elif cmd == RRUCmd.GET_RX_GAIN:
                self.refresh_rx_gain()
            elif cmd == RRUCmd.GET_S_SLOT:
                self.refresh_s_slot()
            elif cmd == RRUCmd.GET_TDD_SLOT:
                self.refresh_tdd_slot()
