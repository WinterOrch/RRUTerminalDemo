import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QThreadPool

from src.QtRep.TabWidget.AxiRegTab import AxiRegTab
from src.QtRep.TabWidget.OffsetTab import OffsetTab
from src.QtRep.TerminalEdit import TerminalEdit
from src.QtRep.TabWidget.DeviceTab import DeviceTab
from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.Runnable.TelnetWorker import TelnetWorker, WorkerSignals
from src.Telnet.TelRepository import TelRepository

mainSpacing = 2

TEST = False


class OperateWidget(QtWidgets.QWidget):
    operateSignal = pyqtSignal(str)
    connectionOutSignal = pyqtSignal()

    option = 0

    def __init__(self):
        super(OperateWidget, self).__init__()

        with open('../Qss/OperatorQSS.qss', 'r') as f:
            self.list_style = f.read()

        '''MANAGE PANE'''
        device_manage_layout = QtWidgets.QGridLayout()

        self.optionLabel = QtWidgets.QLabel("Ant Num")
        self.optionComboBox = QtWidgets.QComboBox()
        for i in range(RRUCmd.ant_num[OperateWidget.option]):
            self.optionComboBox.addItem(str(i))
        self.versionEdit = QtWidgets.QLineEdit()
        self.versionEdit.setEnabled(False)

        self.refreshButton = QtWidgets.QPushButton("Version")
        self.refreshButton.setDisabled(True)
        self.rebootButton = QtWidgets.QPushButton("Reboot")
        self.rebootButton.setDisabled(True)

        device_manage_layout.addWidget(self.optionLabel, 0, 0)
        device_manage_layout.addWidget(self.optionComboBox, 0, 1)
        device_manage_layout.addWidget(self.versionEdit, 0, 2)
        device_manage_layout.addWidget(self.refreshButton, 0, 4)
        device_manage_layout.addWidget(self.rebootButton, 0, 5)
        device_manage_layout.setContentsMargins(7, 7, 7, 7)
        '''END OF MANAGE PANE'''

        self.setStyleSheet(self.list_style)
        tab_widget = QtWidgets.QTabWidget()

        self.device_setting = DeviceTab(self)
        self.device_setting.setDisabled(not TEST)
        self.offset_setting = OffsetTab(self)
        self.offset_setting.setDisabled(not TEST)
        self.axi_reg_setting = AxiRegTab(self)
        self.axi_reg_setting.turn(TEST)  # TODO False if not for DEBUG
        tab_widget.addTab(self.device_setting, "Device")
        tab_widget.addTab(self.offset_setting, "Offset")
        tab_widget.addTab(self.axi_reg_setting, "Axi Reg")

        self.browser = TerminalEdit()

        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.setFlat(True)
        self.delButton = QtWidgets.QPushButton("Clear")
        self.delButton.setFlat(True)
        self.browserButtonLayout = QtWidgets.QGridLayout()
        self.browserButtonLayout.addWidget(self.saveButton, 0, 0)
        self.browserButtonLayout.addWidget(self.delButton, 0, 2)
        self.delButton.clicked.connect(self.browser.all_clear)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(device_manage_layout)
        mainLayout.addWidget(tab_widget)
        mainLayout.addWidget(self.browser)
        mainLayout.addLayout(self.browserButtonLayout)
        mainLayout.setContentsMargins(1, 1, 1, 1)
        mainLayout.setSpacing(mainSpacing)
        self.setLayout(mainLayout)

        '''Slot'''
        self.optionComboBox.currentIndexChanged.connect(self.refresh_ant_num)
        self.rebootButton.clicked.connect(self.reboot)
        self.refreshButton.clicked.connect(self.refresh_version)

        self.device_setting.deviceRvdSignal.connect(self.emit_rvd_signal)
        self.device_setting.deviceTranSignal.connect(self.emit_trans_signal)
        self.offset_setting.deviceRvdSignal.connect(self.emit_rvd_signal)
        self.offset_setting.deviceTranSignal.connect(self.emit_trans_signal)
        self.axi_reg_setting.deviceRvdSignal.connect(self.emit_rvd_signal)
        self.axi_reg_setting.deviceTranSignal.connect(self.emit_trans_signal)

        self.device_setting.warningSignal.connect(self.send_warning)
        self.offset_setting.warningSignal.connect(self.send_warning)
        self.axi_reg_setting.warningSignal.connect(self.send_warning)

        self.device_setting.connectionOutSignal.connect(self.slot_connection_out_signal)
        self.offset_setting.connectionOutSignal.connect(self.slot_connection_out_signal)
        self.axi_reg_setting.connectionOutSignal.connect(self.slot_connection_out_signal)

        self.saveButton.clicked.connect(self.test)
        self.set_logger()

    @staticmethod
    def set_logger():
        logging.basicConfig(filename='../log/' + __name__ + '.log',
                            format='[%(asctime)s-%(filename)s-%(funcName)s-%(levelname)s:%(message)s]',
                            level=logging.DEBUG, filemode='a', datefmt='%Y-%m-%d %I:%M:%S %p')

    def refresh_version(self):
        cmd = RRUCmd.get_version()
        self.emit_trans_signal(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.emit_rvd_signal(res)
        self.versionEdit.setText(res)

    def reboot(self):
        if self.warning("是否进行设备复位？"):
            cmd = RRUCmd.reboot(self.get_option())
            self._process_cmd(RRUCmd.CMD_TYPE_SET, RRUCmd.REBOOT, cmd)

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

    def get_resp_handler(self, case, resp: str):
        pass

    def set_resp_handler(self, case, resp: str):
        if case == RRUCmd.REBOOT:
            if not RespFilter.resp_check(resp):
                self.warning("Frequency cannot be set properly")
            else:
                if self.warning("Reboot Finished, Press YES to Refresh All Value"):
                    self.set_connected(True)

    def _console_slot(self, case, msg):
        if case == WorkerSignals.TRAN_SIGNAL:
            self.emit_trans_signal(msg)
        elif case == WorkerSignals.RECV_SIGNAL:
            self.emit_rvd_signal(msg)

    @staticmethod
    def log_error(t_error: tuple):
        s_error = ""
        for i in t_error:
            s_error += str(i) + " "
        logging.error(s_error)

    @staticmethod
    def warning(info):
        msgBox = QtWidgets.QMessageBox()

        msgBox.setWindowTitle('Warning')
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText('Information')
        msgBox.setInformativeText(info)
        msgBox.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
        no = msgBox.addButton('No', QtWidgets.QMessageBox.RejectRole)
        msgBox.setDefaultButton(no)

        reply = msgBox.exec()
        if reply == QtWidgets.QMessageBox.AcceptRole:
            return True
        else:
            return False

    def test(self):
        self.set_connected(True)

    def send_warning(self, connect):
        self.warning(connect)

    def emit_rvd_signal(self, connect):
        self.browser.flush_response(connect)
        self.operateSignal.emit(connect)

    def emit_trans_signal(self, connect):
        self.operateSignal.emit(connect)

    def set_connected(self, connect):
        self.refreshButton.setEnabled(connect)
        self.rebootButton.setEnabled(connect)

        self.device_setting.setEnabled(connect)
        self.offset_setting.setEnabled(connect)
        self.axi_reg_setting.turn(connect, True)
        self.device_setting.refresh_all(connect)
        self.offset_setting.refresh_all(connect)

    @staticmethod
    def get_option():
        return RRUCmd.cmd_type_str[OperateWidget.option]

    def get_ant_num(self):
        return self.optionComboBox.currentText()

    def set_option(self, connect):
        OperateWidget.option = connect
        self.device_setting.freqEdit.setPlaceholderText(self.device_setting.freqEditTip[connect])
        self.optionComboBox.disconnect()
        self.optionComboBox.clear()
        for i in range(RRUCmd.ant_num[OperateWidget.option]):
            self.optionComboBox.addItem(str(i))
        self.optionComboBox.currentIndexChanged.connect(self.refresh_ant_num)

    def slot_connection_out_signal(self):
        self.connectionOutSignal.emit()

    def refresh_ant_num(self):
        self.device_setting.antenna_index = self.optionComboBox.currentIndex()
        self.offset_setting.antenna_index = self.optionComboBox.currentIndex()

        self.device_setting.refresh_ant_num()
        self.offset_setting.refresh_ant_num()
