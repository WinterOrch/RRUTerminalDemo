from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from src.QtRep.TabWidget.OffsetTab import OffsetTab
from src.QtRep.TerminalEdit import TerminalEdit
from src.QtRep.TabWidget.DeviceTab import DeviceTab
from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.TelRepository import TelRepository

mainSpacing = 2


class OperateWidget(QtWidgets.QWidget):
    operateSignal = pyqtSignal(str)

    connectionOutSignal = pyqtSignal()

    def __init__(self):
        super(OperateWidget, self).__init__()

        with open('../Qss/OperatorQSS.qss', 'r') as f:
            self.list_style = f.read()

        '''MANAGE PANE'''
        device_manage_layout = QtWidgets.QGridLayout()

        self.optionLabel = QtWidgets.QLabel("Option")
        self.optionComboBox = QtWidgets.QComboBox()
        for i in range(len(RRUCmd.cmd_type_str)):
            self.optionComboBox.addItem(RRUCmd.cmd_type_str[i])
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
        self.device_setting.setDisabled(True)
        self.offset_setting = OffsetTab(self)
        self.offset_setting.setDisabled(True)
        tab_widget.addTab(self.device_setting, "Device")
        tab_widget.addTab(self.offset_setting, "Offset")

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
        self.optionComboBox.currentIndexChanged.connect(self.device_setting.refresh_all_value)
        self.rebootButton.clicked.connect(self.reboot)
        self.refreshButton.clicked.connect(self.refresh_version)

        self.device_setting.deviceRvdSignal.connect(self.emit_rvd_signal)
        self.device_setting.deviceTranSignal.connect(self.emit_trans_signal)

        self.device_setting.warningSignal.connect(self.send_warning)

        self.device_setting.connectionOutSignal.connect(self.slot_connection_out_signal)

        self.saveButton.clicked.connect(self.test)

    def refresh_version(self):
        cmd = RRUCmd.get_version()
        self.emit_trans_signal(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.emit_rvd_signal(res)
        self.versionEdit.setText(res)

    def reboot(self):
        if self.warning("是否进行设备复位？"):
            cmd = RRUCmd.reboot()
            self.emit_trans_signal(cmd)
            res = TelRepository.telnet_instance.execute_command(cmd)
            self.emit_rvd_signal(res)
            self.versionEdit.setText(res)

    @staticmethod
    def warning(info):
        msgBox = QtWidgets.QMessageBox()

        msgBox.setWindowTitle('Warning')
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText('Information')
        msgBox.setInformativeText(info)
        yes = msgBox.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
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
        self.device_setting.refresh_all(connect)
        # TODO ADD other tab panes

    def get_option(self):
        return self.optionComboBox.currentText()

    def set_option(self, connect):
        self.optionComboBox.setCurrentIndex(connect)

    def slot_connection_out_signal(self):
        self.connectionOutSignal.emit()
