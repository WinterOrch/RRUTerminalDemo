import sys
import time
import traceback

from PyQt5 import QtCore

from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.TelRepository import TelRepository


class WorkerSignals(QtCore.QObject):
    """
    Signals available from a running worker thread.

    """
    TRAN_SIGNAL = 0
    RECV_SIGNAL = 1

    connectionLost = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)

    consoleDisplay = QtCore.pyqtSignal(int, str)

    result = QtCore.pyqtSignal(int, str)


class TelnetWorker(QtCore.QRunnable):
    test_lock = False

    def __init__(self, case, s_cmd):
        super(TelnetWorker, self).__init__()
        self.case = case  # Case Flag from RRUCmd.py
        self.cmd = s_cmd
        self.result = ""
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            if TelRepository.connection_check():
                self.signals.consoleDisplay.emit(WorkerSignals.TRAN_SIGNAL, self.cmd)

                if self.case == RRUCmd.REBOOT:
                    self.reboot(self.cmd)
                elif self.case == RRUCmd.VERSION:
                    self.version(self.cmd)
                elif self.case == RRUCmd.GET_FREQUENCY:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_FREQUENCY:
                    self.set_value(self.cmd)
                elif self.case == RRUCmd.GET_TX_ATTEN:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_TX_ATTEN:
                    self.set_value(self.cmd)
                elif self.case == RRUCmd.GET_RX_GAIN:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_RX_GAIN:
                    self.set_value(self.cmd)
                elif self.case == RRUCmd.GET_TDD_SLOT:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_TDD_SLOT:
                    self.set_value(self.cmd)
                elif self.case == RRUCmd.GET_S_SLOT:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_S_SLOT:
                    self.set_value(self.cmd)
                elif self.case == RRUCmd.GET_UL_OFFSET:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_UL_OFFSET:
                    self.set_value(self.cmd)
                elif self.case == RRUCmd.GET_DL_OFFSET:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_DL_OFFSET:
                    self.set_value(self.cmd)
                elif self.case == RRUCmd.GET_CPRI_STATUS:
                    self.get_cpri(self.cmd)
                elif self.case == RRUCmd.SET_CPRI:
                    self.set_cpri(self.cmd)
                elif self.case == RRUCmd.GET_AXI_OFFSET:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_AXI_OFFSET:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.GET_CPRI_LOOP_MODE:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_CPRI_LOOP_MODE:
                    self.set_value(self.cmd)
                elif self.case == RRUCmd.GET_AXI_REG:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_AXI_REG:
                    self.set_value(self.cmd)
                elif self.case == RRUCmd.GET_IP_ADDR:
                    self.get_value(self.cmd)
                elif self.case == RRUCmd.SET_IP_ADDR:
                    self.set_value(self.cmd)
            else:
                if self.case == RRUCmd.CMD_TYPE_DEBUG:
                    self._debug_test(self.cmd)
                else:
                    self.signals.connectionLost.emit()
        except:
            traceback.print_exc()
            except_type, value = sys.exc_info()[:2]
            self.signals.error.emit((except_type, value, traceback.format_exc()))
        else:
            self.signals.result.emit(self.case, self.result)
        finally:
            self.signals.finished.emit()

    def reboot(self, cmd):
        #   Execute and send Info to Sim-Console
        self.signals.consoleDisplay.emit(WorkerSignals.TRAN_SIGNAL, self.cmd)

        self.result = TelRepository.telnet_instance.execute_command(cmd)

        res_display = RespFilter.trim(self.result)
        self.signals.consoleDisplay.emit(WorkerSignals.RECV_SIGNAL, res_display)

    def version(self, cmd):
        pass

    def _debug_test(self, cmd):
        while TelnetWorker.test_lock:
            time.sleep(0.1)

        TelnetWorker.test_lock = True
        #   Execute and send Info to Sim-Console
        self.signals.consoleDisplay.emit(WorkerSignals.TRAN_SIGNAL, self.cmd)

        time.sleep(0.7)

        self.result = "OK, GOT IT " + cmd

        self.signals.consoleDisplay.emit(WorkerSignals.RECV_SIGNAL, self.result)
        TelnetWorker.test_lock = False

    def get_value(self, cmd):
        #   Execute and send Info to Sim-Console
        self.signals.consoleDisplay.emit(WorkerSignals.TRAN_SIGNAL, self.cmd)

        self.result = TelRepository.telnet_instance.execute_command(cmd)

        res_display = RespFilter.trim(self.result)
        self.signals.consoleDisplay.emit(WorkerSignals.RECV_SIGNAL, res_display)

    def set_value(self, cmd):
        #   Execute and send Info to Sim-Console
        self.signals.consoleDisplay.emit(WorkerSignals.TRAN_SIGNAL, self.cmd)

        self.result = TelRepository.telnet_instance.execute_command(cmd)

        res_display = RespFilter.trim(self.result)
        self.signals.consoleDisplay.emit(WorkerSignals.RECV_SIGNAL, res_display)

    def get_cpri(self, cmd):
        #   Execute and send Info to Sim-Console
        self.signals.consoleDisplay.emit(WorkerSignals.TRAN_SIGNAL, self.cmd)

        self.result = TelRepository.telnet_instance.execute_command(cmd)

        self.signals.consoleDisplay.emit(WorkerSignals.RECV_SIGNAL, self.result)

    def set_cpri(self, cmd):
        #   Execute and send Info to Sim-Console
        self.signals.consoleDisplay.emit(WorkerSignals.TRAN_SIGNAL, self.cmd)

        self.result = TelRepository.telnet_instance.execute_command(cmd)

        res_display = RespFilter.trim(self.result)
        self.signals.consoleDisplay.emit(WorkerSignals.RECV_SIGNAL, res_display)
