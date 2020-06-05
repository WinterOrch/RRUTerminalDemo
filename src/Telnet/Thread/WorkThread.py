import time

from PyQt5 import QtCore

from src.QtRep.NonQSSStyle import NonQSSStyle
from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.TelRepository import TelRepository


class WorkThread(QtCore.QThread):

    sigConnectionOut = QtCore.pyqtSignal()
    sigSetOK = QtCore.pyqtSignal(int)
    sigGetRes = QtCore.pyqtSignal(int, str)

    def __init__(self, parentWidget, case, cmd):
        super(WorkThread, self).__init__()
        self.parentWidget = parentWidget
        self.case = case
        self.cmd = cmd

    def run(self) -> None:
        if TelRepository.connection_check():
            if self.case == RRUCmd.REBOOT:
                self.reboot(self.cmd)
            elif self.case == RRUCmd.VERSION:
                self.version(self.cmd)
            elif self.case == RRUCmd.GET_FREQUENCY:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_FREQUENCY:
                self.set_frequency(self.cmd)
            # TODO ADD
        else:
            self.sigConnectionOut.emit()

    def reboot(self, cmd):
        pass

    def version(self, cmd):
        pass

    def get_frequency(self, cmd):
        self.parentWidget.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.parentWidget.deviceRvdSignal.emit(res)

        self.sigGetRes.emit(self.case, res)

    def set_frequency(self, cmd):
        self.parentWidget.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        self.parentWidget.deviceRvdSignal.emit(res)
        
        # TODO 预读成功与否
        self.sigSetOK.emit(self.case)


