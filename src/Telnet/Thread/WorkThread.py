from PyQt5 import QtCore

from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.TelRepository import TelRepository


class WorkThread(QtCore.QThread):
    """各功能 Tab 通过创建工作线程实体发送 RRUCmd 并接收反馈。

        Tab 或 Widget 类通过 RRUCmd 类创建指令后通过构造函数交给 WorkThread 。
        WorkThread 只负责收发，不对消息进行处理。
    """

    sigConnectionOut = QtCore.pyqtSignal()

    sigSetOK = QtCore.pyqtSignal(int, str)
    sigGetRes = QtCore.pyqtSignal(int, str)

    def __init__(self, parentWidget, case, cmd):
        super(WorkThread, self).__init__()
        self.parentWidget = parentWidget
        self.case = case    # Case Flag from RRUCmd.py
        self.cmd = cmd

    def __del__(self):
        self.wait()

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
            elif self.case == RRUCmd.GET_TX_ATTEN:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_TX_ATTEN:
                self.set_frequency(self.cmd)
            elif self.case == RRUCmd.GET_RX_GAIN:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_RX_GAIN:
                self.set_frequency(self.cmd)
            elif self.case == RRUCmd.GET_TDD_SLOT:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_TDD_SLOT:
                self.set_frequency(self.cmd)
            elif self.case == RRUCmd.GET_S_SLOT:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_S_SLOT:
                self.set_frequency(self.cmd)
            elif self.case == RRUCmd.GET_UL_OFFSET:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_UL_OFFSET:
                self.set_frequency(self.cmd)
            elif self.case == RRUCmd.GET_DL_OFFSET:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_DL_OFFSET:
                self.set_frequency(self.cmd)
            elif self.case == RRUCmd.GET_CPRI_STATUS:
                self.get_cpri(self.cmd)
            elif self.case == RRUCmd.SET_CPRI:
                self.set_cpri(self.cmd)
            elif self.case == RRUCmd.GET_AXI_OFFSET:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_AXI_OFFSET:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.GET_CPRI_LOOP_MODE:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_CPRI_LOOP_MODE:
                self.set_frequency(self.cmd)
            elif self.case == RRUCmd.GET_AXI_REG:
                self.get_frequency(self.cmd)
            elif self.case == RRUCmd.SET_AXI_REG:
                self.set_frequency(self.cmd)
            elif self.case == RRUCmd.GET_IP_ADDR:
                self.get_ip_addr(self.cmd)
            elif self.case == RRUCmd.SET_IP_ADDR:
                self.set_ip_addr(self.cmd)
            # TODO ADD
        else:
            self.sigConnectionOut.emit()

    def reboot(self, cmd):
        pass

    def version(self, cmd):
        pass

    def get_frequency(self, cmd):
        #   Execute and send Info to Sim-Console
        self.parentWidget.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        res_display = RespFilter.trim(res)
        self.parentWidget.deviceRvdSignal.emit(res_display)
        #   Emit Signal to Trigger Value Refresh in Device Setting Tab
        self.sigGetRes.emit(self.case, res)

    def set_frequency(self, cmd):
        #   Execute and send Info to Sim-Console
        self.parentWidget.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        res_display = RespFilter.trim(res)
        self.parentWidget.deviceRvdSignal.emit(res_display)
        # Emit Signal to Device Setting Tab as Response
        self.sigSetOK.emit(self.case, res)

    def get_cpri(self, cmd):
        #   Execute and send Info to Sim-Console
        self.parentWidget.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        #   Emit Signal to Trigger Value Refresh in Device Setting Tab
        self.sigGetRes.emit(self.case, res)

    def set_cpri(self, cmd):
        #   Execute and send Info to Sim-Console
        self.parentWidget.deviceTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        res_display = RespFilter.trim(res)
        self.parentWidget.deviceRvdSignal.emit(res_display)
        # Emit Signal to Device Setting Tab as Response
        self.sigSetOK.emit(self.case, res)

    def get_ip_addr(self, cmd):
        """Used by LoginWidget to Get Ip Address of RRU Device
        """
        #   Execute and send Info to Sim-Console
        self.parentWidget.ipTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        res_display = RespFilter.trim(res)
        self.parentWidget.ipRecvSignal.emit(res_display)
        self.sigGetRes.emit(self.case, res)

    def set_ip_addr(self, cmd):
        """Used by LoginWidget to Set Ip Address of RRU Device
        """
        #   Execute and send Info to Sim-Console
        self.parentWidget.ipTranSignal.emit(cmd)
        res = TelRepository.telnet_instance.execute_command(cmd)
        res_display = RespFilter.trim(res)
        self.parentWidget.ipRecvSignal.emit(res_display)
        # Emit Signal to LoginWidget as Response
        self.sigSetOK.emit(self.case, res)
