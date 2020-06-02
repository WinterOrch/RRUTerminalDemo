import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QListWidget, QStackedWidget
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QHBoxLayout

from PyQt5.QtCore import QSize, Qt

from src.QtRep.LoginWidget import LoginWidget
from src.QtRep.OperateWidget import OperateWidget
from src.QtRep.TerminalWidget import TerminalWidget
from src.Telnet.TelRepository import TelRepository
from src.Telnet.Telnet import Telnet


class LeftTabWidget(QWidget):

    def __init__(self):
        super(LeftTabWidget, self).__init__()
        self.setObjectName('LeftTabWidget')

        self.setWindowTitle('TerminalDemo')
        with open('../Qss/QListWidgetQSS.qss', 'r') as f:
            self.list_style = f.read()

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QListWidget()
        self.left_widget.setStyleSheet(self.list_style)
        self.main_layout.addWidget(self.left_widget)

        self.right_widget = QStackedWidget()
        self.main_layout.addWidget(self.right_widget)

        self._setup_ui()

        self.resize(600, 500)

    def _setup_ui(self):

        self.left_widget.currentRowChanged.connect(self.right_widget.setCurrentIndex)

        self.left_widget.setFrameShape(QListWidget.NoFrame)

        self.left_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.left_widget.setIconSize(QtCore.QSize(48, 58))
        self.left_widget.setViewMode(QtWidgets.QListView.IconMode)

        item_terminal = QtWidgets.QListWidgetItem()
        icon_terminal = QtGui.QIcon()
        icon_terminal.addPixmap(QtGui.QPixmap('../Icon/console-mod.png'))
        item_terminal.setIcon(icon_terminal)
        self.left_widget.addItem(item_terminal)
        item_login = QtWidgets.QListWidgetItem()
        icon_login = QtGui.QIcon()
        icon_login.addPixmap(QtGui.QPixmap('../Icon/login-mod.png'))
        item_login.setIcon(icon_login)
        self.left_widget.addItem(item_login)
        item_setting = QtWidgets.QListWidgetItem()
        icon_setting = QtGui.QIcon()
        icon_setting.addPixmap(QtGui.QPixmap('../Icon/setting-mod.png'))
        item_setting.setIcon(icon_setting)
        self.left_widget.addItem(item_setting)

        self.terminalWidget = TerminalWidget()
        self.right_widget.addWidget(self.terminalWidget)
        self.loginWidget = LoginWidget(self)
        self.right_widget.addWidget(self.loginWidget)
        self.settingWidget = OperateWidget()
        self.right_widget.addWidget(self.settingWidget)
        '''Signal'''
        self.loginWidget.loginSignal.connect(self.settingWidget.set_connected)
        self.settingWidget.operateSignal.connect(self.terminalWidget.show_response)
        self.loginWidget.loginWarningSignal.connect(self.terminalWidget.show_response)
        ''''''

        self._retranslate_ui()

    def _retranslate_ui(self):
        up_list_str = ['Terminal', 'Connect', 'Setting']
        for i in range(3):
            self.item = self.left_widget.item(i)
            self.item.setText(up_list_str[i])
            self.item.setSizeHint(QSize(110, 90))
            self.item.setTextAlignment(Qt.AlignCenter)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if Telnet.isTelnetOpened:
            TelRepository.telnet_instance.logout()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    main_wnd = LeftTabWidget()
    main_wnd.show()

    app.exec()


if __name__ == '__main__':
    main()
