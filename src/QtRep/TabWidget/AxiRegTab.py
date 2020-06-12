import typing
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QModelIndex, Qt, QVariant
from PyQt5 import QtCore

from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.Thread.WorkThread import WorkThread
from src.Tool.ValidCheck import ValidCheck

valueEditStyle = "height: 22px"
setButtonStyle = "width: 30px; height: 90px"

buttonWidth = 80
pubSpacing = 10
mainSpacing = 20


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
        self.refreshButton.clicked.connect(self.refresh_axi)
        self.regModel.sigSendConfig.connect(self._store_change)
        self.regModel.sigWarning.connect(self.warning)
        self.refreshButton.clicked.connect(self.regModel.resort)

    def _init_cmd(self):
        self.set_cmd_pool.clear()
        self.sendButton.setEnabled(False)

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

    def turn(self, switch):
        self._init_cmd()

        self.addButton.setEnabled(switch)
        self.delButton.setEnabled(switch)
        self.refreshButton.setEnabled(switch)

        if not switch:
            self.regModel.clear()

    def test(self):
        self.regModel.clear()
        self.regModel.append_data(['0x40000000', '0x30000000'])

    def _del_row(self):
        r = self.axiTableView.currentIndex().row()
        self.regModel.remove_row(r)

    def _store_change(self, change: str):
        self.set_cmd_pool.append(change)
        self.sendButton.setEnabled(True)

    def _send_change(self):
        if len(self.set_cmd_pool) != 0:
            cmd = RRUCmd.set_axis_reg(self.parentWidget.get_option(), self.set_cmd_pool.pop(0))

            print("Generate CMD: " + cmd)

            thread_dl_offset_Set = WorkThread(self, RRUCmd.SET_AXI_REG, cmd)
            thread_dl_offset_Set.sigConnectionOut.connect(self.slot_connection_out_signal)
            thread_dl_offset_Set.sigSetOK.connect(self.set_resp_handler)
            thread_dl_offset_Set.start()
            thread_dl_offset_Set.exec()
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

                    i = 0
                    while i < len(self.regModel.data):
                        if int(take_addr(self.regModel.data[i]), 16) == n_addr:
                            if not found:
                                found = True
                                if int(take_value(self.regModel.data[i]), 16) == n_reg:
                                    self.info("内存 {addr} 成功写入为 {reg}".format(addr=addr, reg=reg))
                                else:
                                    self.regModel.change_value(i, reg)
                                    self.info(
                                        "内存 {addr} 未成功写入, 当前值为 {reg}".format(addr=addr, reg=reg))
                            else:
                                self.regModel.remove_row(i)

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

            thread_dl_offset_Set = WorkThread(self, RRUCmd.GET_AXI_REG, cmd)
            thread_dl_offset_Set.sigConnectionOut.connect(self.slot_connection_out_signal)
            thread_dl_offset_Set.sigGetRes.connect(self.get_resp_handler)
            thread_dl_offset_Set.start()
            thread_dl_offset_Set.exec()
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

                    self.regModel.append_data([addr, reg])
            else:
                self.warning("Axi Reg cannot be read properly")

        self._pop_and_refresh()

    def refresh_axi(self):
        self.sendButton.setEnabled(False)
        self.set_cmd_pool.clear()

        self.regModel.resort()

        for ele in self.regModel.data:
            self.refresh_cmd_pool.append(RRUCmd.get_axis_reg(
                self.parentWidget.get_option(), ValidCheck.addr_transfer(take_addr(ele), RRUCmd.SET_AXI_REG)))

        self.regModel.clear()
        self._pop_and_refresh()

    def _pop_and_refresh(self):
        if len(self.refresh_cmd_pool) != 0:
            cmd = self.refresh_cmd_pool.pop(0)

            thread_dl_offset_Set = WorkThread(self, RRUCmd.GET_AXI_REG, cmd)
            thread_dl_offset_Set.sigConnectionOut.connect(self.slot_connection_out_signal)
            thread_dl_offset_Set.sigGetRes.connect(self.get_resp_handler)
            thread_dl_offset_Set.start()
            thread_dl_offset_Set.exec()


class AxiEditModel(QtCore.QAbstractTableModel):
    sigSendConfig = pyqtSignal(str)
    sigWarning = pyqtSignal(str)

    def __init__(self, data: list, header):
        super(AxiEditModel, self).__init__()
        self.data = data
        self.header = header

    def clear(self):
        for i in range(self.rowCount()):
            self.remove_row(self.rowCount() - 1)

    def append_data(self, x):
        self.data.append(x)
        self.layoutChanged.emit()

    def change_value(self, idx, s_value):
        self.data[idx][1] = s_value
        self.layoutChanged.emit()

    def remove_row(self, row):
        if len(self.data) != 0:
            self.data.pop(row)
            self.layoutChanged.emit()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.data)

    def columnCount(self, parent=None, *args, **kwargs):
        if len(self.data) > 0:
            return len(self.data[0])
        return 0

    def fetch_data(self, index: QModelIndex):
        return self.data[index.row()][index.column()]

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            print("行或者列有问题")
            return QVariant()
        elif role != Qt.DisplayRole:
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            else:
                return QVariant()
        return QVariant(self.data[index.row()][index.column()])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header[section]
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if role == Qt.EditRole:
            if index.column() == 1:
                if value != self.data[index.row()][index.column()] \
                        and ValidCheck.filter(ValidCheck.HEX_RE, value) is not None:
                    print("Origin:" + self.data[index.row()][index.column()] + " to " + value + " Changed and valid")
                    self.data[index.row()][index.column()] = value
                    self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
                    self.sigSendConfig.emit(RRUCmd.change(
                        ValidCheck.addr_transfer(self.data[index.row()][0], RRUCmd.SET_AXI_REG), value))

                elif ValidCheck.filter(ValidCheck.HEX_RE, value) is None:
                    self.sigWarning.emit("Input Should be in HEX format!")
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def resort(self):
        self.data.sort(key=take_addr)
        self.data = remove_duplicated(self.data)
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
