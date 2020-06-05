import os
import logging

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from src.Telnet import JsonRep
from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.TelRepository import TelRepository
from src.Telnet.Telnet import Telnet

from PyQt5 import QtWidgets

from src.Telnet.Thread.MonitorThread import MonitorThread

valueEditStyle = "height: 22px"
setButtonStyle = "height: 90px"

pubSpacing = 10
mainSpacing = 2


class LoginWidget(QWidget):
    sinOption = pyqtSignal(int)
    loginSignal = pyqtSignal(bool)
    loginWarningSignal = pyqtSignal(str)

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

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(device_manage_layout)
        mainLayout.addWidget(userPwGroup)
        mainLayout.setContentsMargins(10, 20, 10, 20)
        mainLayout.setSpacing(mainSpacing)

        v_layout = QtWidgets.QVBoxLayout()
        v_layout.addLayout(mainLayout)
        v_layout.setContentsMargins(5, 100, 5, 100)

        self.setLayout(v_layout)

    def _add_signal(self):
        self.loginButton.clicked.connect(self.login_onclick)
        self.optionComboBox.currentIndexChanged.connect(self._send_option)

        self.passwordEdit.textChanged.connect(self.back_normal)
        self.userEdit.textChanged.connect(self.back_normal)
        self.hostEdit.textChanged.connect(self.back_normal)

        self.monitorT.sinOut.connect(self.health_failure)

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

            self.loginSignal.emit(True)

            # Save
            if self.saveCheckBox.isChecked():
                data = [{Telnet.json_dict[0]: host, Telnet.json_dict[1]: user, Telnet.json_dict[2]: password}]
                JsonRep.save_by_json(data)

            self.monitorT.start()
        else:
            self.loginButton.setStyleSheet("background-color: red; height: 90px")
            self.loginButton.setText('Failed')

            self.loginSignal.emit(False)
            self.loginWarningSignal.emit(str(TelRepository.telnet_instance.get_warning()))

    def test(self):
        host = self.hostEdit.text().strip()
        print(host)
        user = self.userEdit.text().strip()
        password = self.passwordEdit.text()

        JsonRep.save_by_json([{Telnet.json_dict[0]: host, Telnet.json_dict[1]: user, Telnet.json_dict[2]: password}])

    def back_normal(self):
        self.loginButton.setText("Login")
        self.loginButton.setStyleSheet(setButtonStyle)

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
        yes = msgBox.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
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
        self._loose_login()

        msgBox = QtWidgets.QMessageBox()

        msgBox.setWindowTitle('Warning')
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText('Connection Lost!')

        msgBox.exec()

    def _loose_login(self):
        self.loginSignal.emit(False)
        self.monitorT.quit()
        self.isTelnetLogined = False
        self.back_normal()
