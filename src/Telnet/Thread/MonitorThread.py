import time

from PyQt5 import QtCore
from src.Telnet.TelRepository import TelRepository

monitorInv = 5


class MonitorThread(QtCore.QThread):
    sinOut = QtCore.pyqtSignal()

    def __init__(self):
        super(MonitorThread, self).__init__()
        self.working = True

    def __del__(self):
        self.working = False

    def run(self) -> None:
        while self.working:
            time.sleep(monitorInv)
            if TelRepository.telnet_instance.isTelnetLogined:
                if not TelRepository.connection_check():
                    self.sinOut.emit()
