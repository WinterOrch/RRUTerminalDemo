import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLineEdit, QFormLayout, QVBoxLayout, QPushButton, QHBoxLayout

from src.Telnet import JsonRep
from src.Telnet.TelRepository import TelRepository
from src.Telnet.Telnet import Telnet


class LoginWidget(QWidget):

    loginSignal = pyqtSignal(bool)

    def __init__(self):
        super(LoginWidget, self).__init__()

        with open('../Qss/TerminalEditQSS.qss', 'r') as file:
            str = file.readlines()
            str = ''.join(str).strip('\n')

        self.setStyleSheet(str)

        self._setup_ui()

        if self._check_json():
            print("OK")
            # TODO self.login()

    def _setup_ui(self):
        layout_widget = QWidget(self)
        v_layout = QVBoxLayout(layout_widget)

        self.hostEdit = QLineEdit()
        self.hostEdit.textChanged.connect(self.ready_button)

        self.userEdit = QLineEdit()
        self.userEdit.textChanged.connect(self.ready_button)

        self.passwordEdit = QLineEdit()
        self.passwordEdit.textChanged.connect(self.ready_button)
        self.passwordEdit.setEchoMode(QLineEdit.Password)

        form_layout_widget = QWidget(layout_widget)
        form_layout = QFormLayout(form_layout_widget)
        form_layout.addRow('Host Name', self.hostEdit)
        form_layout.addRow('Username', self.userEdit)
        form_layout.addRow('Password', self.passwordEdit)
        v_layout.addWidget(form_layout_widget)

        button_widget = QWidget(layout_widget)
        button_layout = QHBoxLayout(button_widget)
        self.loginButton = QPushButton(button_widget)
        self.loginButton.setText('Login')
        self.loginButton.clicked.connect(self.test)
        v_layout.addWidget(button_widget)

    def _check_json(self):
        if os.access('../JSON/' + Telnet.json_filename + '.json', os.F_OK):
            data_in_json = JsonRep.read_json(Telnet.json_filename)
            self.hostEdit.setText(data_in_json[0][Telnet.json_dict[0]])
            self.userEdit.setText(data_in_json[0][Telnet.json_dict[1]])
            self.passwordEdit.setText(data_in_json[0][Telnet.json_dict[2]])
            return True
        else:
            return False

    def ready_button(self):
        self.loginButton.setStyleSheet("background: rgb(85, 85, 85)")
        self.loginButton.setText('Login')

    def login(self):
        host = self.hostEdit.text().strip()
        user = self.userEdit.text().strip()
        password = self.passwordEdit.text()
        if TelRepository.telnet_instance.login(host, user, password):
            self.loginButton.setStyleSheet("background-color: green")
            self.loginButton.setText('Connected')

            self.loginSignal.emit(True)

            # Save
            data = [{Telnet.json_dict[0]: host, Telnet.json_dict[1]: user, Telnet.json_dict[2]: password}]
            JsonRep.save_by_json(data)
        else:
            self.loginButton.setStyleSheet("background-color: red")
            self.loginButton.setText('Failed')

            self.loginSignal.emit(False)

    def test(self):
        host = self.hostEdit.text().strip()
        print(host)
        user = self.userEdit.text().strip()
        password = self.passwordEdit.text()

        JsonRep.save_by_json([{Telnet.json_dict[0]: host, Telnet.json_dict[1]: user, Telnet.json_dict[2]: password}])
