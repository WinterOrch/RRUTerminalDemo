import time

from PyQt5 import QtCore

from src.Telnet.Config.TelnetConfig import TelnetConfig
from src.Telnet.TelRepository import TelRepository


class MonitorSignals(QtCore.QObject):
    """
    Signals available from a running monitor thread.

    """
    connectionLost = QtCore.pyqtSignal()


class ConnectionMonitor(QtCore.QRunnable):

    def __init__(self):
        super(ConnectionMonitor, self).__init__()
        self.working = True
        self.signals = MonitorSignals()

    def __del__(self):
        self.working = False

    def run(self) -> None:
        while self.working:
            time.sleep(TelnetConfig.MonitorInterval)
            if TelRepository.telnet_instance.isTelnetLogined:
                if not TelRepository.connection_check():
                    self.signals.connectionLost.emit()
                    self.working = False
            else:
                self.working = False
