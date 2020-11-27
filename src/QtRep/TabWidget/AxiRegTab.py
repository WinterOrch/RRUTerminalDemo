import typing
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QModelIndex, Qt, QVariant, QThreadPool
from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

from src.QtRep.NonQSSStyle import NonQSSStyle
from src.Telnet import JsonRep
from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.Runnable.TelnetWorker import WorkerSignals, TelnetWorker
from src.Tool.ValidCheck import ValidCheck

valueEditStyle = "height: 22px"
setButtonStyle = "width: 30px; height: 90px"

buttonWidth = 80
pubSpacing = 10
mainSpacing = 20

TEST = False


class AxiRegTab(QtWidgets.QWidget):
    deviceTranSignal = pyqtSignal(str)
    deviceRvdSignal = pyqtSignal(str)

    warningSignal = pyqtSignal(str)

    connectionOutSignal = pyqtSignal()

    def __init__(self, parent):
        super(AxiRegTab, self).__init__()
        self.parentWidget = parent

        self._setup_ui()
        self._add_signal()

        self.set_cmd_pool = []
        self.refresh_cmd_pool = []
        self._init_cmd()

    def _setup_ui(self):
        if TEST:
            self.dataMap = {
                "header": ['Addr', 'Reg Value'],
                "data": [['0x40000002', '0x00000002'], ['0x40000003', '0x00000002'], ['0x40000004', '0x00000002'],
                         ['0x40000005', '0x00000002'], ['0x40000006', '0x00000002'], ['0x40000007', '0x00000002']]
            }
        else:
            self.dataMap = {
                "header": ['Addr', 'Reg Value'],
                "data": []
            }
        self.regModel = AxiEditModel(self.dataMap.get('data'), self.dataMap.get('header'))

        self.axiTableView = QtWidgets.QTableView()
        self.axiTableView.setModel(self.regModel)
        self.axiTableView.verticalHeader().hide()
        self.axiTableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        '''
        icon_add = QtGui.QIcon()
        icon_add.addPixmap(QtGui.QPixmap('../../Icon/add.jpg'))
        icon_del = QtGui.QIcon()
        icon_del.addPixmap(QtGui.QPixmap('../../Icon/del.jpg'))
        icon_push = QtGui.QIcon()
        icon_push.addPixmap(QtGui.QPixmap('../../Icon/push.jpg'))
        icon_get = QtGui.QIcon()
        icon_get.addPixmap(QtGui.QPixmap('../../Icon/get.jpg.jpg'))
        '''

        self.addButton = QtWidgets.QPushButton("ADD")
        self.addButton.setFlat(True)
        self.refreshButton = QtWidgets.QPushButton("REFRESH")
        self.refreshButton.setFlat(True)
        self.sendButton = QtWidgets.QPushButton("SEND")
        self.sendButton.setFlat(True)
        self.delButton = QtWidgets.QPushButton("DELETE")
        self.delButton.setFlat(True)
        self.buttonLayout = QtWidgets.QGridLayout()
        self.buttonLayout.addWidget(self.addButton, 0, 0)
        self.buttonLayout.addWidget(self.sendButton, 0, 1)
        self.buttonLayout.addWidget(self.delButton, 0, 2)
        self.buttonLayout.addWidget(self.refreshButton, 0, 3)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.axiTableView)
        mainLayout.addLayout(self.buttonLayout)
        mainLayout.addSpacing(pubSpacing)
        self.setLayout(mainLayout)

    def _add_signal(self):
        self.addButton.clicked.connect(self._add_axi)
        self.sendButton.clicked.connect(self._send_change)
        self.delButton.clicked.connect(self._del_row)
        if not TEST:
            self.refreshButton.clicked.connect(self.refresh_axi)
        else:
            self.refreshButton.clicked.connect(self.test)
        self.regModel.sigSendConfig.connect(self._store_change)
        self.regModel.sigWarning.connect(self.warning)
        self.refreshButton.clicked.connect(self.regModel.resort)

    def _init_cmd(self):
        self.set_cmd_pool.clear()
        self.regModel.addr_in_change.clear()
        self.sendButton.setEnabled(False)

    def _console_slot(self, case, msg):
        if case == WorkerSignals.TRAN_SIGNAL:
            self.deviceTranSignal.emit(msg)
        elif case == WorkerSignals.RECV_SIGNAL:
            self.deviceRvdSignal.emit(msg)

    def slot_connection_out_signal(self):
        self.connectionOutSignal.emit()

    @staticmethod
    def info(info):
        msgBox = QtWidgets.QMessageBox()

        msgBox.setWindowTitle('Info')
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText(info)

        msgBox.exec()

    def warning(self, info):
        self.warningSignal.emit(info)

    def turn(self, switch, initialized=False):
        self._init_cmd()

        self.addButton.setEnabled(switch)
        self.delButton.setEnabled(switch)
        self.refreshButton.setEnabled(switch)

        if not switch:
            if not initialized:
                if 0 != len(self.regModel.axi_data):
                    self.json_save()
            else:
                self.json_save()
            self.regModel.clear()
        else:
            self.regModel.clear()
            self.json_read()

    def json_read(self):
        json_data = JsonRep.AxiJson.read_axi()
        for ele in json_data:
            self.regModel.append_data([ele[JsonRep.AxiJson.AXI_ADDR], ele[JsonRep.AxiJson.AXI_REG]])

    def json_save(self):
        json_data = []
        for ele in self.regModel.axi_data:
            json_data.append({JsonRep.AxiJson.AXI_ADDR: take_addr(ele), JsonRep.AxiJson.AXI_REG: take_value(ele)})
        JsonRep.AxiJson.save_axi(json_data)

    def test(self):
        """
        self.regModel.addr_in_change.append('0x40000006')

        test_1 = "read axi reg 0x400000c0:0x00000005"
        self.get_resp_handler(RRUCmd.GET_AXI_REG, test_1)
        test_2 = "read axi reg 0x400000c4:0x00000006"
        self.get_resp_handler(RRUCmd.GET_AXI_REG, test_2)
        """
        self.json_read()

    def _del_row(self):
        r = self.axiTableView.currentIndex().row()
        self.regModel.remove_row(r)

    def _store_change(self, change: list):
        addr = take_addr(change)
        i = 0
        new_addr = True
        while i < len(self.set_cmd_pool):
            if take_addr(self.set_cmd_pool[i]) == addr:
                self.set_cmd_pool[i][1] = take_value(change)
                new_addr = False
                break
            else:
                i += 1
        if new_addr:
            self.set_cmd_pool.append(change)
        self.sendButton.setEnabled(True)

    def _send_change(self):
        if len(self.set_cmd_pool) != 0:
            cmd = RRUCmd.set_axis_reg(self.parentWidget.get_option(), self.set_cmd_pool.pop(0)[1])

            print("Generate CMD: " + cmd)

            thread = TelnetWorker(RRUCmd.SET_AXI_REG, cmd)
            thread.signals.connectionLost.connect(self.slot_connection_out_signal)
            thread.signals.result.connect(self.set_resp_handler)
            thread.signals.consoleDisplay.connect(self._console_slot)
            QThreadPool.globalInstance().start(thread)
        else:
            self.sendButton.setEnabled(False)

    def set_resp_handler(self, case, resp: str):
        if case == RRUCmd.SET_AXI_REG:
            if RespFilter.resp_check(resp):
                match = RespFilter.axi_read_filter(resp)
                if match is not None:
                    res = match.group().split(":")

                    addr = res[0]
                    reg = res[1]

                    n_addr = int(addr, 16)
                    n_reg = int(reg, 16)

                    found = False

                    if addr in self.regModel.addr_in_change:
                        self.regModel.addr_in_change.remove(addr)

                    i = 0
                    while i < len(self.regModel.axi_data):
                        if int(take_addr(self.regModel.axi_data[i]), 16) == n_addr:
                            if not found:
                                found = True
                                if int(take_value(self.regModel.axi_data[i]), 16) == n_reg:
                                    self.info("内存 {addr} 成功写入为 {reg}".format(addr=addr, reg=reg))
                                else:
                                    self.regModel.change_value(i, reg)
                                    self.info(
                                        "内存 {addr} 未成功写入, 当前值为 {reg}".format(addr=addr, reg=reg))
                            else:
                                self.regModel.remove_row(i)
                        i += 1

                    if not found:
                        self.regModel.append_data([addr, reg])
                        self.info("RegAddr {addr} Written Finished, Now Read as {reg}".format(addr=addr, reg=reg))
                else:
                    self.info("Axi Reg Config Complete But Value Cannot Be Read.")
            else:
                self.warning("Axi Reg Config Failed!")
        self._send_change()

    def _add_axi(self):
        addr, okPressed = QtWidgets.QInputDialog.getText(self, "Get Addr",
                                                         "Axi Offset Addr:", QtWidgets.QLineEdit.Normal, "")
        match = ValidCheck.filter(ValidCheck.HEX_RE, addr)
        if okPressed and match is not None:
            cmd = RRUCmd.get_axis_reg(self.parentWidget.get_option(), match.group())

            thread = TelnetWorker(RRUCmd.GET_AXI_REG, cmd)
            thread.signals.connectionLost.connect(self.slot_connection_out_signal)
            thread.signals.result.connect(self.get_resp_handler)
            thread.signals.consoleDisplay.connect(self._console_slot)
            QThreadPool.globalInstance().start(thread)
        elif okPressed and match is None:
            self.warning("Invalid Offset Address")

    def get_resp_handler(self, case, resp: str):
        if case == RRUCmd.GET_AXI_REG:
            if RespFilter.resp_check(resp):
                match = RespFilter.axi_read_filter(resp)
                if match is not None:
                    res = match.group().split(":")

                    addr = res[0]
                    reg = res[1]

                    if addr in self.regModel.addr_in_change:
                        self.regModel.addr_in_change.remove(addr)

                    i = 0
                    new_addr = True
                    while i < len(self.regModel.axi_data):
                        if take_addr(self.regModel.axi_data[i]) == addr:
                            self.regModel.change_value(i, reg)
                            new_addr = False
                            break
                        else:
                            i += 1
                    if new_addr:
                        self.regModel.append_data([addr, reg])
            else:
                self.warning("Axi Reg cannot be read properly")

        self._pop_and_refresh()

    def refresh_axi(self):
        self.sendButton.setEnabled(False)
        self.set_cmd_pool.clear()
        self.regModel.addr_in_change.clear()

        self.regModel.resort()

        for ele in self.regModel.axi_data:
            self.refresh_cmd_pool.append(RRUCmd.get_axis_reg(
                self.parentWidget.get_option(), ValidCheck.addr_transfer(take_addr(ele), RRUCmd.SET_AXI_REG)))

        self.regModel.clear()
        self._pop_and_refresh()

    def _pop_and_refresh(self):
        if len(self.refresh_cmd_pool) != 0:
            cmd = self.refresh_cmd_pool.pop(0)

            thread = TelnetWorker(RRUCmd.GET_AXI_REG, cmd)
            thread.signals.connectionLost.connect(self.slot_connection_out_signal)
            thread.signals.result.connect(self.get_resp_handler)
            thread.signals.consoleDisplay.connect(self._console_slot)
            QThreadPool.globalInstance().start(thread)


class AxiEditModel(QtCore.QAbstractTableModel):
    sigSendConfig = pyqtSignal(list)
    sigWarning = pyqtSignal(str)

    addr_in_change = []

    dataCount = 0
    editStart = False

    def __init__(self, data: list, header):
        super(AxiEditModel, self).__init__()
        self.axi_data = data
        self.header = header

    def clear(self):
        for i in range(self.rowCount()):
            self.remove_row(self.rowCount() - 1)

    def append_data(self, x):
        self.axi_data.append(x)
        self.layoutChanged.emit()

    def change_value(self, idx, s_value):
        self.axi_data[idx][1] = s_value
        self.layoutChanged.emit()

    def remove_row(self, row):
        if len(self.axi_data) != 0:
            self.axi_data.pop(row)
            self.layoutChanged.emit()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.axi_data)

    def columnCount(self, parent=None, *args, **kwargs):
        if len(self.axi_data) > 0:
            return len(self.axi_data[0])
        return 0

    def fetch_data(self, index: QModelIndex):
        return self.axi_data[index.row()][index.column()]

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if TEST:
            '''
            print("data!" + str(self.dataCount))
            self.dataCount += 1
            print(role)
            '''
            if role == Qt.EditRole:
                print('yeah')
                self.editStart = not self.editStart

            if self.editStart:
                print(role)

        if not index.isValid():
            print("行或者列有问题")
            return QVariant()
        elif role != Qt.DisplayRole:
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            elif role == Qt.BackgroundRole and take_addr(self.axi_data[index.row()]) in self.addr_in_change:
                return QColor(NonQSSStyle.ChangedRowBackgroundInTable)
            elif role == Qt.EditRole:
                # TODO  目前找不到修改表格编辑器内容的方法，因此将内容复制到剪切板先
                clipboard = QApplication.clipboard()
                clipboard.setText(self.axi_data[index.row()][index.column()])
                return QVariant()
            else:
                return QVariant()
        return QVariant(self.axi_data[index.row()][index.column()])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header[section]
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        print("set data!")
        if role == Qt.EditRole:
            if index.column() == 1:
                if value != self.axi_data[index.row()][index.column()] \
                        and ValidCheck.filter(ValidCheck.HEX_RE, value) is not None:
                    value = ValidCheck.reg_format(value)
                    print("Origin:" + self.axi_data[index.row()][index.column()] +
                          " to " + value + " Changed and valid")
                    self.axi_data[index.row()][index.column()] = value
                    self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
                    self.addr_in_change.append(take_addr(self.axi_data[index.row()]))
                    self.sigSendConfig.emit([take_addr(self.axi_data[index.row()]), RRUCmd.change(
                        ValidCheck.addr_transfer(self.axi_data[index.row()][0], RRUCmd.SET_AXI_REG), value)])

                elif ValidCheck.filter(ValidCheck.HEX_RE, value) is None:
                    self.sigWarning.emit("Input Should be in HEX format!")
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def resort(self):
        self.axi_data.sort(key=take_addr)
        self.axi_data = remove_duplicated(self.axi_data)
        self.layoutChanged.emit()


def take_addr(lis):
    return lis[0]


def take_value(lis):
    return lis[1]


def remove_duplicated(lis):
    resultList = []
    for item in lis:
        flag = True
        for it in resultList:
            if take_addr(it) == take_addr(item):
                flag = False
                break
        if flag:
            resultList.append(item)
    return resultList
