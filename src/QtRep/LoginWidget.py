import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLineEdit, QFormLayout, QVBoxLayout, QPushButton, QHBoxLayout

from src.Telnet import JsonRep
from src.Telnet.TelRepository import TelRepository
from src.Telnet.Telnet import Telnet

from PyQt5 import QtWidgets


valueEditStyle = "height: 22px"
setButtonStyle = "height: 90px"

pubSpacing = 10
mainSpacing = 2


class LoginWidget(QWidget):

    loginSignal = pyqtSignal(bool)
    loginWarningSignal = pyqtSignal(str)

    def __init__(self, parent):
        super(LoginWidget, self).__init__()
        self.parentWindow = parent

        with open('../Qss/OperatorQSS.qss', 'r') as f:
            self.list_style = f.read()

        self.setStyleSheet(self.list_style)

        self._setup_ui()
        self._add_signal()

        self._check_json()

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

        self.getRxGainLabel = QtWidgets.QLabel("Password")
        self.passwordEdit = QtWidgets.QLineEdit()
        self.passwordEdit.setStyleSheet(valueEditStyle)

        self.user_pw_layout = QtWidgets.QGridLayout()
        self.user_pw_layout.addWidget(self.getTxGainLabel, 0, 0)
        self.user_pw_layout.addWidget(self.userEdit, 0, 1)
        self.user_pw_layout.addWidget(self.getRxGainLabel, 1, 0)
        self.user_pw_layout.addWidget(self.passwordEdit, 1, 1)
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
        self.loginButton.clicked.connect(self.login)

    def _check_json(self):
        if os.access('../JSON/' + Telnet.json_filename + '.json', os.F_OK):
            data_in_json = JsonRep.read_json(Telnet.json_filename)
            self.hostEdit.setText(data_in_json[0][Telnet.json_dict[0]])
            self.userEdit.setText(data_in_json[0][Telnet.json_dict[1]])
            self.passwordEdit.setText(data_in_json[0][Telnet.json_dict[2]])
            return True
        else:
            return False

    def login(self):
        host = self.hostEdit.text().strip()
        user = self.userEdit.text().strip()
        password = self.passwordEdit.text()
        if TelRepository.telnet_instance.login(host, user, password):
            self.loginButton.setStyleSheet("background-color: green; height: 90px")
            self.loginButton.setText('Connected')

            self.loginSignal.emit(True)

            # Save
            if self.saveCheckBox.isChecked():
                data = [{Telnet.json_dict[0]: host, Telnet.json_dict[1]: user, Telnet.json_dict[2]: password}]
                JsonRep.save_by_json(data)
        else:
            self.loginButton.setStyleSheet("background-color: red; height: 90px")
            self.loginButton.setText('Failed')

            self.loginSignal.emit(False)
            self.loginWarningSignal.emit(TelRepository.telnet_instance.get_warning())

    def test(self):
        host = self.hostEdit.text().strip()
        print(host)
        user = self.userEdit.text().strip()
        password = self.passwordEdit.text()

        JsonRep.save_by_json([{Telnet.json_dict[0]: host, Telnet.json_dict[1]: user, Telnet.json_dict[2]: password}])

    def test_2(self):
        self.loginButton.setStyleSheet("background-color: red; height: 90px")
