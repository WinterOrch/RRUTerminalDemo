from PyQt5 import QtWidgets


valueEditStyle = "height: 22px"
setButtonStyle = "height: 90px"

pubSpacing = 10
mainSpacing = 20


class LoginTab:
    def __init__(self):
        def __init__(self, parent):
            super(LoginTab, self).__init__()
            self.parentWidget = parent

            self.hostnameLabel = QtWidgets.QLabel("Hostname")
            self.hostEdit = QtWidgets.QLineEdit()
            self.hostEdit.setStyleSheet(valueEditStyle)

            device_manage_layout = QtWidgets.QGridLayout()

            device_manage_layout.addWidget(self.hostnameLabel, 0, 0)
            device_manage_layout.addWidget(self.hostEdit, 0, 1)
            device_manage_layout.setSpacing(pubSpacing)

            userPwGroup = QtWidgets.QGroupBox("Save if Login Succeeded")
            userPwGroup.setCheckable(True)
            userPwGroup.setChecked(True)

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
            mainLayout.setContentsMargins(5, 5, 5, 5)
            mainLayout.setSpacing(mainSpacing)
            self.setLayout(mainLayout)
