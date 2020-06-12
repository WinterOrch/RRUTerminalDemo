import os
import logging

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from src.QtRep.NonQSSStyle import NonQSSStyle
from src.Telnet import JsonRep
from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.TelRepository import TelRepository
from src.Telnet.Telnet import Telnet

from PyQt5 import QtWidgets

from src.Telnet.Thread.MonitorThread import MonitorThread
from src.Telnet.Thread.WorkThread import WorkThread
from src.Tool.ValidCheck import ValidCheck

valueEditStyle = "height: 22px"
setButtonStyle = "height: 90px"

pubSpacing = 10
mainSpacing = 2


class LoginWidget(QWidget):
    sinOption = pyqtSignal(int)
    loginSignal = pyqtSignal(bool)
    loginWarningSignal = pyqtSignal(str)

    ipTranSignal = pyqtSignal(str)
    ipRecvSignal = pyqtSignal(str)

    def __init__(self, parent):
        self.isTelnetLogined = False

        super(LoginWidget, self).__init__()
        self.parentWindow = parent

        with open('../Qss/OperatorQSS.qss', 'r') as f:
            self.list_style = f.read()

        self.setStyleSheet(self.list_style)

        '''Monitor Thread'''
        self.monitorT = MonitorThread()
        ''''''

        self._setup_ui()
        self._add_signal()

        self._check_json()

        self._set_logger()

        # self.ip_config_widget.setDisabled(True)

    def _setup_ui(self):
        self.hostnameLabel = QtWidgets.QLabel("Hostname")
        self.hostEdit = QtWidgets.QLineEdit()
        self.hostEdit.setStyleSheet(valueEditStyle)
        self.saveCheckBox = QtWidgets.QCheckBox("Save   ")
        self.saveCheckBox.setChecked(True)

        device_manage_layout = QtWidgets.QGridLayout()

        device_manage_layout.addWidget(self.hostnameLabel, 0, 0)
        device_manage_layout.addWidget(self.hostEdit, 0, 1)
        device_manage_layout.addWidget(self.saveCheckBox, 0, 3)
        device_manage_layout.setSpacing(pubSpacing)

        userPwGroup = QtWidgets.QGroupBox()

        self.loginButton = QtWidgets.QPushButton("Login")
        self.loginButton.setStyleSheet(setButtonStyle)

        self.getTxGainLabel = QtWidgets.QLabel("Username")
        self.userEdit = QtWidgets.QLineEdit()
        self.userEdit.setStyleSheet(valueEditStyle)

        self.optionComboBox = QtWidgets.QComboBox()
        for i in range(len(RRUCmd.cmd_type_str)):
            self.optionComboBox.addItem(RRUCmd.cmd_type_str[i])

        self.getRxGainLabel = QtWidgets.QLabel("Password")
        self.passwordEdit = QtWidgets.QLineEdit()
        self.passwordEdit.setStyleSheet(valueEditStyle)
        self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Password)

        self.user_pw_layout = QtWidgets.QGridLayout()
        self.user_pw_layout.addWidget(self.getTxGainLabel, 0, 0)
        self.user_pw_layout.addWidget(self.userEdit, 0, 1)
        self.user_pw_layout.addWidget(self.optionComboBox, 0, 3)
        self.user_pw_layout.addWidget(self.getRxGainLabel, 1, 0)
        self.user_pw_layout.addWidget(self.passwordEdit, 1, 1, 1, 3)
        self.user_pw_layout.setSpacing(pubSpacing)

        self.vLineFrame = QtWidgets.QFrame()
        self.vLineFrame.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)

        deviceLayout = QtWidgets.QGridLayout()
        deviceLayout.addLayout(self.user_pw_layout, 0, 0)
        deviceLayout.addWidget(self.vLineFrame, 0, 1)
        deviceLayout.addWidget(self.loginButton, 0, 2)
        userPwGroup.setLayout(deviceLayout)

        '''Ip Address Config Pane'''
        self.ipaddrLabel = QtWidgets.QLabel("IP Address Config")
        self.ipaddrEdit = QtWidgets.QLineEdit()
        self.ipaddrEdit.setStyleSheet(valueEditStyle)
        self.ipAddrRefreshButton = QtWidgets.QPushButton("Refresh")
        self.ipAddrConfigButton = QtWidgets.QPushButton("Config")

        ip_config_layout = QtWidgets.QGridLayout()
        ip_config_layout.addWidget(self.ipaddrLabel, 0, 0)
        ip_config_layout.addWidget(self.ipaddrEdit, 0, 1, 1, 3)
        ip_config_layout.addWidget(self.ipAddrRefreshButton, 0, 4)
        ip_config_layout.addWidget(self.ipAddrConfigButton, 0, 5)
        ip_config_layout.setSpacing(pubSpacing)

        self.ip_config_widget = QtWidgets.QWidget()
        self.ip_config_widget.setLayout(ip_config_layout)
        '''End of ip Address Config Pane'''

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(device_manage_layout)
        mainLayout.addWidget(userPwGroup)
        mainLayout.addWidget(self.ip_config_widget)
        mainLayout.setContentsMargins(10, 20, 10, 20)
        mainLayout.setSpacing(mainSpacing)

        v_layout = QtWidgets.QVBoxLayout()
        v_layout.addLayout(mainLayout)
        v_layout.setContentsMargins(5, 70, 5, 70)

        self.setLayout(v_layout)

    def _add_signal(self):
        self.loginButton.clicked.connect(self.login_onclick)
        self.optionComboBox.currentIndexChanged.connect(self._send_option)
        self.ipAddrRefreshButton.clicked.connect(self.refresh_ip_addr)
        self.ipAddrConfigButton.clicked.connect(self.set_ip_addr)

        self.passwordEdit.textChanged.connect(self.back_normal)
        self.passwordEdit.returnPressed.connect(self.login_onclick)
        self.userEdit.textChanged.connect(self.back_normal)
        self.hostEdit.textChanged.connect(self.back_normal)

        self.monitorT.sinOut.connect(self.health_failure)

        self.setTabOrder(self.hostEdit, self.userEdit)
        self.setTabOrder(self.userEdit, self.passwordEdit)

    def _check_json(self):
        if os.access('../JSON/' + Telnet.json_filename + '.json', os.F_OK):
            data_in_json = JsonRep.read_json(Telnet.json_filename)
            self.hostEdit.setText(data_in_json[0][Telnet.json_dict[0]])
            self.userEdit.setText(data_in_json[0][Telnet.json_dict[1]])
            self.passwordEdit.setText(data_in_json[0][Telnet.json_dict[2]])
            return True
        else:
            return False

    @staticmethod
    def _set_logger():
        logging.basicConfig(filename='../log/' + __name__ + '.log',
                            format='[%(asctime)s-%(filename)s-%(funcName)s-%(levelname)s:%(message)s]',
                            level=logging.DEBUG, filemode='a', datefmt='%Y-%m-%d %I:%M:%S %p')

    def login(self):
        self.back_normal()

        host = self.hostEdit.text().strip()
        user = self.userEdit.text().strip()
        password = self.passwordEdit.text()

        self.isTelnetLogined = TelRepository.telnet_instance.login(host, user, password)
        if self.isTelnetLogined:
            self.loginButton.setStyleSheet("background-color: green; height: 90px")
            self.loginButton.setText('Logout')

            # self.ip_config_widget.setDisabled(False)

            # Save
            if self.saveCheckBox.isChecked():
                data = [{Telnet.json_dict[0]: host, Telnet.json_dict[1]: user, Telnet.json_dict[2]: password}]
                JsonRep.save_by_json(data)

            self.loginSignal.emit(True)

            self.monitorT.start()
        else:
            self.loginButton.setStyleSheet("background-color: red; height: 90px")
            self.loginButton.setText('Failed')

            self.loginSignal.emit(False)
            self.loginWarningSignal.emit(str(TelRepository.telnet_instance.get_warning()))

    def back_normal(self):
        if TelRepository.telnet_instance.isTelnetLogined:
            self.loginButton.setStyleSheet("background-color: green; height: 90px")
        else:
            self.loginButton.setStyleSheet(setButtonStyle)
        self.loginButton.setText("Login")

    def test_login(self):
        self.back_normal()

        host = self.hostEdit.text().strip()
        user = self.userEdit.text().strip()
        password = self.passwordEdit.text().strip()

        self.isTelnetLogined = TelRepository.telnet_instance.login(host, user, password)
        if self.isTelnetLogined:
            self.loginButton.setStyleSheet("background-color: green; height: 90px")
            self.loginButton.setText('Logout')

            # Save
            if self.saveCheckBox.isChecked():
                data = [{Telnet.json_dict[0]: host, Telnet.json_dict[1]: user, Telnet.json_dict[2]: password}]
                JsonRep.save_by_json(data)

            self.monitorT.start()
        else:
            self.loginButton.setStyleSheet("background-color: red; height: 90px")
            self.loginButton.setText('Failed')

    @staticmethod
    def warning(title: str, icon, info):
        msgBox = QtWidgets.QMessageBox()

        msgBox.setWindowTitle(title)
        msgBox.setIcon(icon)
        msgBox.setText('Info')
        msgBox.setInformativeText(info)
        msgBox.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
        no = msgBox.addButton('No', QtWidgets.QMessageBox.RejectRole)
        msgBox.setDefaultButton(no)

        reply = msgBox.exec()
        if reply == QtWidgets.QMessageBox.AcceptRole:
            return True
        else:
            return False

    def login_onclick(self):
        if self.isTelnetLogined:
            info = "Press Yes to log out"
            if self.userEdit.text().strip() != TelRepository.telnet_instance.loginedUserName:
                info = "Press Yes to log out first"
            if self.warning("Warning", QtWidgets.QMessageBox.Information, info):
                if TelRepository.connection_check():
                    TelRepository.telnet_instance.logout()
                    self._loose_login()
                else:
                    self._loose_login()
        else:
            self.login()  # TODO Use self.login() if not for DEBUG

    def _send_option(self):
        self.sinOption.emit(self.optionComboBox.currentIndex())

    def health_failure(self):
        """Shut down all panes and send warning when connection lost
            Connection lost may either be reported by monitor thread or passive touch before sending message
        """
        self._loose_login()

        msgBox = QtWidgets.QMessageBox()

        msgBox.setWindowTitle('Warning')
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText('Connection Lost!')

        msgBox.exec()

    def _loose_login(self):
        self.loginSignal.emit(False)
        # self.ip_config_widget.setDisabled(True)
        self.monitorT.quit()
        self.isTelnetLogined = False
        self.back_normal()

    def refresh_ip_addr(self):
        if self.isTelnetLogined:
            cmd = RRUCmd.get_ipaddr("ipaddr")

            thread_ip_addr_get = WorkThread(self, RRUCmd.GET_IP_ADDR, cmd)
            thread_ip_addr_get.sigConnectionOut.connect(self.health_failure)
            thread_ip_addr_get.sigGetRes.connect(self.refresh_resp_handler)
            thread_ip_addr_get.start()
            thread_ip_addr_get.exec()
        else:
            msgBox = QtWidgets.QMessageBox()

            msgBox.setWindowTitle('Warning')
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText('Login before Refreshing the IP Address')

            msgBox.exec()

    def refresh_resp_handler(self, case, res):
        if case == RRUCmd.GET_IP_ADDR:
            value = RespFilter.ipaddr_read_filter(res)
            if value is not None:
                self.ipaddrEdit.setText(str(value.group()))
            else:
                msgBox = QtWidgets.QMessageBox()

                msgBox.setWindowTitle('Warning')
                msgBox.setIcon(QtWidgets.QMessageBox.Warning)
                msgBox.setText('Cannot get IP Address!')

                msgBox.exec()

    def set_ip_addr(self):
        if self.isTelnetLogined:
            ipaddr2set = ValidCheck.filter(ValidCheck.IPADDR_RE, self.ipaddrEdit.text().strip())
            if ipaddr2set is not None:
                cmd = RRUCmd.config_ipaddr("ipaddr", ipaddr2set.group())

                thread_ip_addr_set = WorkThread(self, RRUCmd.SET_IP_ADDR, cmd)
                thread_ip_addr_set.sigConnectionOut.connect(self.health_failure)
                thread_ip_addr_set.sigSetOK.connect(self.set_handler)
                thread_ip_addr_set.start()
                thread_ip_addr_set.exec()
            else:
                self.ipaddrEdit.setStyleSheet(NonQSSStyle.warningStyle)
        else:
            msgBox = QtWidgets.QMessageBox()

            msgBox.setWindowTitle('Warning')
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText('Login before Setting the IP Address')

            msgBox.exec()

    def ipaddr_edit_back2normal(self):
        self.ipaddrEdit.setStyleSheet(NonQSSStyle.displayValueStyle)

    @staticmethod
    def set_handler(case, resp: str):
        if case == RRUCmd.SET_IP_ADDR:
            if not RespFilter.resp_check(resp):
                msgBox = QtWidgets.QMessageBox()

                msgBox.setWindowTitle('Warning')
                msgBox.setIcon(QtWidgets.QMessageBox.Warning)
                msgBox.setText('IP Address cannot be set properly!')

                msgBox.exec()
