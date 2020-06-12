from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from src.QtRep.Component.ValueLabel import ValueLabel
from src.QtRep.NonQSSStyle import NonQSSStyle
from src.RRU.Antenna import Antenna
from src.Telnet.RRUCmd import RRUCmd
from src.Telnet.RespFilter import RespFilter
from src.Telnet.TelRepository import TelRepository
from src.Telnet.Thread.WorkThread import WorkThread
from src.Tool.ValidCheck import ValidCheck

valueEditStyle = "height: 22px"
setButtonStyle = "width: 30px; height: 90px"

buttonWidth = 80
pubSpacing = 10
mainSpacing = 2


class OffsetTab(QtWidgets.QWidget):
    deviceTranSignal = pyqtSignal(str)
    deviceRvdSignal = pyqtSignal(str)

    warningSignal = pyqtSignal(str)

    connectionOutSignal = pyqtSignal()

    def __init__(self, parent):
        super(OffsetTab, self).__init__()
        self.parentWidget = parent

        self._setup_ui()
        self._add_signal()

        self._init_bean()

    def _setup_ui(self):
        """OFFSET SETTING PANE"""
        offsetGroup = QtWidgets.QGroupBox("Frame Offset")

        self.getDlFrameOffsetLabel = QtWidgets.QLabel("Dl Frame Offset")
        self.dlOffsetValueLabel = ValueLabel("00000000", RRUCmd.GET_DL_OFFSET)
        self.dlOffsetValueLabel.refreshSig.connect(self.quick_refresh)
        self.dlOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.setDlFrameOffsetLabel = QtWidgets.QLabel("Set as")
        self.dlOffsetEdit = QtWidgets.QLineEdit()
        self.dlOffsetEdit.setStyleSheet(valueEditStyle)
        self.getUlFrameOffsetLabel = QtWidgets.QLabel("Ul Frame Offset")
        self.ulOffsetValueLabel = ValueLabel("00000000", RRUCmd.GET_UL_OFFSET)
        self.ulOffsetValueLabel.refreshSig.connect(self.quick_refresh)
        self.ulOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.setUlFrameOffsetLabel = QtWidgets.QLabel("Set as")
        self.ulOffsetEdit = QtWidgets.QLineEdit()
        self.ulOffsetEdit.setStyleSheet(valueEditStyle)

        self.getAxisOffsetLabel = QtWidgets.QLabel("Link Delay")
        self.axisOffsetValueLabel = ValueLabel("00000000", RRUCmd.GET_AXI_OFFSET)
        self.axisOffsetValueLabel.refreshSig.connect(self.quick_refresh)
        self.axisOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.axisOffsetEdit = QtWidgets.QLineEdit()
        self.axisOffsetEdit.setStyleSheet(valueEditStyle)

        frameOffsetLayout = QtWidgets.QGridLayout()
        frameOffsetLayout.addWidget(self.getDlFrameOffsetLabel, 0, 0)
        frameOffsetLayout.addWidget(self.dlOffsetValueLabel, 0, 1)
        frameOffsetLayout.addWidget(self.setDlFrameOffsetLabel, 0, 2)
        frameOffsetLayout.addWidget(self.dlOffsetEdit, 0, 3, 1, 3)
        frameOffsetLayout.addWidget(self.getUlFrameOffsetLabel, 1, 0)
        frameOffsetLayout.addWidget(self.ulOffsetValueLabel, 1, 1)
        frameOffsetLayout.addWidget(self.setUlFrameOffsetLabel, 1, 2)
        frameOffsetLayout.addWidget(self.ulOffsetEdit, 1, 3, 1, 3)
        frameOffsetLayout.addWidget(self.getAxisOffsetLabel, 2, 0)
        frameOffsetLayout.addWidget(self.axisOffsetValueLabel, 2, 1, 1, 2)
        frameOffsetLayout.addWidget(self.axisOffsetEdit, 2, 3, 1, 3)
        frameOffsetLayout.setSpacing(pubSpacing)

        vLineFrame = QtWidgets.QFrame()
        vLineFrame.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)

        self.setUlOffsetButton = QtWidgets.QPushButton("Send")
        self.setUlOffsetButton.setStyleSheet(setButtonStyle)
        self.setUlOffsetButton.setMaximumWidth(buttonWidth)

        offsetLayout = QtWidgets.QGridLayout()
        offsetLayout.addLayout(frameOffsetLayout, 0, 0)
        offsetLayout.addWidget(vLineFrame, 0, 1)
        offsetLayout.addWidget(self.setUlOffsetButton, 0, 2)
        offsetGroup.setLayout(offsetLayout)
        """END OF OFFSET SETTING PANE"""

        """CPRI SETTING PANE"""
        cpriGroup = QtWidgets.QGroupBox("CPRI OFFSET")

        self.getCPRIStatusLabel = QtWidgets.QLabel("CPRI Status")
        self.cpriValueLabel = ValueLabel("---- ----", RRUCmd.GET_CPRI_STATUS)
        self.cpriValueLabel.refreshSig.connect(self.quick_refresh)
        self.cpriValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.getCPRIButton = QtWidgets.QPushButton("Refresh Status")
        self.getCPRIButton.setStyleSheet(valueEditStyle)
        self.configCPRIButton = QtWidgets.QPushButton("Set CPRI")
        self.configCPRIButton.setStyleSheet(valueEditStyle)

        self.getCPRILoopModeLabel = QtWidgets.QLabel("CPRI Loop Mode")
        self.cpriLoopModeLabel = ValueLabel("00000000", RRUCmd.GET_CPRI_LOOP_MODE)
        self.cpriLoopModeLabel.refreshSig.connect(self.quick_refresh)
        self.cpriLoopModeLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.setCPRILoopModeLabel = QtWidgets.QLabel("Set as")
        self.cpriLoopModeEdit = QtWidgets.QLineEdit()
        self.cpriLoopModeEdit.setStyleSheet(valueEditStyle)

        cpriLayout = QtWidgets.QGridLayout()
        cpriLayout.addWidget(self.getCPRIStatusLabel, 0, 0)
        cpriLayout.addWidget(self.cpriValueLabel, 0, 1, 1, 2)
        cpriLayout.addWidget(self.getCPRIButton, 0, 3)
        cpriLayout.addWidget(self.configCPRIButton, 0, 4)
        cpriLayout.addWidget(self.getCPRILoopModeLabel, 1, 0)
        cpriLayout.addWidget(self.cpriLoopModeLabel, 1, 1)
        cpriLayout.addWidget(self.setCPRILoopModeLabel, 1, 2)
        cpriLayout.addWidget(self.cpriLoopModeEdit, 1, 3, 1, 2)
        cpriLayout.setSpacing(pubSpacing)

        vLineFrame_2 = QtWidgets.QFrame()
        vLineFrame_2.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)

        self.setCPRIButton = QtWidgets.QPushButton("Send")
        self.setCPRIButton.setStyleSheet(setButtonStyle)
        self.setCPRIButton.setMaximumWidth(buttonWidth)

        cpriSettingLayout = QtWidgets.QGridLayout()
        cpriSettingLayout.addLayout(cpriLayout, 0, 0)
        cpriSettingLayout.addWidget(vLineFrame_2, 0, 1)
        cpriSettingLayout.addWidget(self.setCPRIButton, 0, 2)
        cpriGroup.setLayout(cpriSettingLayout)
        """END OF DEVICE SETTING PANE"""

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(offsetGroup)
        mainLayout.addWidget(cpriGroup)
        mainLayout.addSpacing(mainSpacing)
        self.setLayout(mainLayout)

    def _add_signal(self):
        self.setUlOffsetButton.clicked.connect(self._send)
        self.getCPRIButton.clicked.connect(self._get_cpri_status)
        self.configCPRIButton.clicked.connect(self._set_cpri_status)
        self.setCPRIButton.clicked.connect(self._set_cpri_loop_mode)

        self.axisOffsetEdit.textChanged.connect(self._axi_offset_edit_back2normal)
        self.axisOffsetEdit.returnPressed.connect(self._set_axis_offset)
        self.ulOffsetEdit.textChanged.connect(self._ul_offset_edit_back2normal)
        self.dlOffsetEdit.textChanged.connect(self._dl_offset_edit_back2normal)
        self.cpriLoopModeEdit.textChanged.connect(self._cpri_loop_mode_edit_back2normal)
        self.cpriLoopModeEdit.returnPressed.connect(self._set_cpri_loop_mode)

    def _init_bean(self):
        self.antenna_bean_arr = []
        for i in range(max(RRUCmd.ant_num)):
            self.antenna_bean_arr.append(Antenna())
        self.antenna_index = 0

    def warning(self, info):
        self.warningSignal.emit(info)

    @staticmethod
    def info(info):
        msgBox = QtWidgets.QMessageBox()

        msgBox.setWindowTitle('Info')
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText(info)

        msgBox.exec()

    def refresh_ant_num(self):
        if TelRepository.telnet_instance.isTelnetLogined:
            self.display()

    def display(self):
        """Refresh display of antenna-differed values
        """
        # Ul Frame Offset
        self.ulOffsetValueLabel.setText(self.antenna_bean_arr[self.antenna_index].ulFrameOffset)
        if self.antenna_bean_arr[self.antenna_index].ulFrameOffsetOutDated:
            self.ulOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
        else:
            self.ulOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.ulOffsetEdit.setText(Antenna.not_none(self.antenna_bean_arr[self.antenna_index].ulFrameOffset))
        # Dl Frame Offset
        self.dlOffsetValueLabel.setText(self.antenna_bean_arr[self.antenna_index].dlFrameOffset)
        if self.antenna_bean_arr[self.antenna_index].dlFrameOffsetOutDated:
            self.dlOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
        else:
            self.dlOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
        self.dlOffsetEdit.setText(Antenna.not_none(self.antenna_bean_arr[self.antenna_index].dlFrameOffset))

    def slot_connection_out_signal(self):
        self.connectionOutSignal.emit()
            
    def _send(self):
        self._set_axis_offset()

        # TODO Valid Check not added yet
        ulOffset2set = self.ulOffsetEdit.text().strip()
        if len(ulOffset2set) != 0:
            self.ulOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
            if ulOffset2set != self.ulOffsetValueLabel.text():
                cmd = RRUCmd.set_ul_frame_offset(self.parentWidget.get_option(), 
                                                 self.parentWidget.get_ant_num(), ulOffset2set)
                self.antenna_bean_arr[self.antenna_index].ulFrameOffsetOutDated = True

                thread_ul_offset_Set = WorkThread(self, RRUCmd.SET_UL_OFFSET, cmd)
                thread_ul_offset_Set.sigConnectionOut.connect(self.slot_connection_out_signal)
                thread_ul_offset_Set.sigSetOK.connect(self.set_resp_handler)
                thread_ul_offset_Set.start()
                thread_ul_offset_Set.exec()
        else:
            self.ulOffsetEdit.setStyleSheet(NonQSSStyle.warningStyle)

        # TODO Valid Check not added yet
        dlOffset2set = self.udlOffsetEdit.text().strip()
        if len(dlOffset2set) != 0:
            self.ulOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
            if dlOffset2set != self.dlOffsetValueLabel.text():
                cmd = RRUCmd.set_dl_frame_offset(self.parentWidget.get_option(), 
                                                 self.parentWidget.get_ant_num(), dlOffset2set)
                self.antenna_bean_arr[self.antenna_index].dlFrameOffsetOutDated = True

                thread_dl_offset_Set = WorkThread(self, RRUCmd.SET_DL_OFFSET, cmd)
                thread_dl_offset_Set.sigConnectionOut.connect(self.slot_connection_out_signal)
                thread_dl_offset_Set.sigSetOK.connect(self.set_resp_handler)
                thread_dl_offset_Set.start()
                thread_dl_offset_Set.exec()
        else:
            self.dlOffsetEdit.setStyleSheet(NonQSSStyle.warningStyle)

    def _set_axis_offset(self):
        axiOffset2set = self.axisOffsetEdit.text().strip()
        if axiOffset2set != self.axisOffsetValueLabel.text():
            match = ValidCheck.filter(ValidCheck.HEX_RE, axiOffset2set)
            if match is not None:
                self.axisOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                cmd = RRUCmd.config_axis_offset(self.parentWidget.get_option(), str(match.group()))

                thread_axi_offset_set = WorkThread(self, RRUCmd.SET_AXI_OFFSET, cmd)
                thread_axi_offset_set.sigConnectionOut.connect(self.slot_connection_out_signal)
                thread_axi_offset_set.sigSetOK.connect(self.set_resp_handler)
                thread_axi_offset_set.start()
                thread_axi_offset_set.exec()
            else:
                self.axisOffsetEdit.setStyleSheet(NonQSSStyle.warningStyle)
        
    def _set_cpri_status(self):
        cmd = RRUCmd.get_cpri(self.parentWidget.get_option())

        thread_cpri_set = WorkThread(self, RRUCmd.SET_CPRI, cmd)
        thread_cpri_set.sigConnectionOut.connect(self.slot_connection_out_signal)
        thread_cpri_set.sigGetRes.connect(self.set_resp_handler)
        thread_cpri_set.start()
        thread_cpri_set.exec()
        
    def _set_cpri_loop_mode(self):
        # TODO Valid Check not added yet
        loopMode2set = self.cpriLoopModeEdit.text().strip()
        if loopMode2set != self.cpriValueLabel.text():
            if len(loopMode2set) != 0:
                self.cpriValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                cmd = RRUCmd.config_cpri_loop_mode(self.parentWidget.get_option(), loopMode2set)

                thread_cpri_loop_mode_set = WorkThread(self, RRUCmd.SET_CPRI_LOOP_MODE, cmd)
                thread_cpri_loop_mode_set.sigConnectionOut.connect(self.slot_connection_out_signal)
                thread_cpri_loop_mode_set.sigSetOK.connect(self.set_resp_handler)
                thread_cpri_loop_mode_set.start()
                thread_cpri_loop_mode_set.exec()
            else:
                self.cpriLoopModeEdit.setStyleSheet(NonQSSStyle.warningStyle)

    def _get_cpri_status(self):
        cmd = RRUCmd.get_cpri(self.parentWidget.get_option())

        thread_cpri_get = WorkThread(self, RRUCmd.GET_CPRI_STATUS, cmd)
        thread_cpri_get.sigConnectionOut.connect(self.slot_connection_out_signal)
        thread_cpri_get.sigGetRes.connect(self.get_resp_handler)
        thread_cpri_get.start()
        thread_cpri_get.exec()

    def _get_axi_offset(self):
        cmd = RRUCmd.get_axis_offset(self.parentWidget.get_option())

        thread_axi_offset_get = WorkThread(self, RRUCmd.GET_AXI_OFFSET, cmd)
        thread_axi_offset_get.sigConnectionOut.connect(self.slot_connection_out_signal)
        thread_axi_offset_get.sigGetRes.connect(self.get_resp_handler)
        thread_axi_offset_get.start()
        thread_axi_offset_get.exec()

    def _get_ul_frame_offset(self):
        cmd = RRUCmd.get_ul_frame_offset(self.parentWidget.get_option(), self.parentWidget.get_ant_num())

        thread_ul_frame_offset_get = WorkThread(self, RRUCmd.GET_UL_OFFSET, cmd)
        thread_ul_frame_offset_get.sigConnectionOut.connect(self.slot_connection_out_signal)
        thread_ul_frame_offset_get.sigGetRes.connect(self.get_resp_handler)
        thread_ul_frame_offset_get.start()
        thread_ul_frame_offset_get.exec()

    def _get_dl_frame_offset(self):
        cmd = RRUCmd.get_dl_frame_offset(self.parentWidget.get_option(), self.parentWidget.get_ant_num())

        thread_dl_frame_offset_get = WorkThread(self, RRUCmd.GET_DL_OFFSET, cmd)
        thread_dl_frame_offset_get.sigConnectionOut.connect(self.slot_connection_out_signal)
        thread_dl_frame_offset_get.sigGetRes.connect(self.get_resp_handler)
        thread_dl_frame_offset_get.start()
        thread_dl_frame_offset_get.exec()

    def _get_cpri_loop_mode(self):
        cmd = RRUCmd.get_cpri_loop_mode(self.parentWidget.get_option())

        thread_cpri_loop_mode_get = WorkThread(self, RRUCmd.GET_CPRI_LOOP_MODE, cmd)
        thread_cpri_loop_mode_get.sigConnectionOut.connect(self.slot_connection_out_signal)
        thread_cpri_loop_mode_get.sigGetRes.connect(self.get_resp_handler)
        thread_cpri_loop_mode_get.start()
        thread_cpri_loop_mode_get.exec()

    def get_resp_handler(self, case, res: str):
        """Work Thread Get the Value and Send to refresh_resp_handler for displaying
                update data mainly by rewriting antenna_bean and refresh display
                change dimension in the mean time
        """
        if case == RRUCmd.GET_CPRI_STATUS:
            value = RespFilter.word_value_filter(res, RespFilter.CPRI_STATUS_ASSERTION)
            if value is not None:
                self.cpriValueLabel.setText(str(value.group()))
                self.cpriValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
            else:
                self.cpriValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("CPRI Status cannot be refreshed properly")
        elif case == RRUCmd.GET_AXI_OFFSET:
            value = RespFilter.hex_value_filter(res, RespFilter.AXI_OFFSET_ASSERTION)
            if value is not None:
                self.axisOffsetValueLabel.setText(str(value.group()))
                self.axisOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
                self.axisOffsetEdit.setText(str(value.group()))
            else:
                self.axisOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("Axis Offset Address cannot be refreshed properly")
        elif case == RRUCmd.GET_UL_OFFSET:
            value = RespFilter.value_filter_with_ant(res, RespFilter.UL_OFFSET_ASSERTION, self.antenna_index)
            if value is not None:
                res = str(value.group())

                self.antenna_bean_arr[self.antenna_index].ulFrameOffset = res
                self.antenna_bean_arr[self.antenna_index].ulFrameOffset2Set = res
                self.antenna_bean_arr[self.antenna_index].ulFrameOffsetOutDated = False
            else:
                self.ulOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("Ul Frame Offset cannot be refreshed properly")
        elif case == RRUCmd.GET_DL_OFFSET:
            value = RespFilter.value_filter_with_ant(res, RespFilter.DL_OFFSET_ASSERTION, self.antenna_index)
            if value is not None:
                res = str(value.group())

                self.antenna_bean_arr[self.antenna_index].dlFrameOffset = res
                self.antenna_bean_arr[self.antenna_index].dlFrameOffset2Set = res
                self.antenna_bean_arr[self.antenna_index].dlFrameOffsetOutDated = False
            else:
                self.dlOffsetValueLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("Dl Frame Offset cannot be refreshed properly")
        elif case == RRUCmd.GET_CPRI_LOOP_MODE:
            value = RespFilter.word_value_filter(res, RespFilter.CPRI_LOOP_MODE_ASSERTION)
            if value is not None:
                self.cpriLoopModeLabel.setText(str(value.group()))
                self.cpriLoopModeLabel.setStyleSheet(NonQSSStyle.displayValueStyle)
                self.cpriLoopModeEdit.setText(str(value.group()))
            else:
                self.cpriLoopModeLabel.setStyleSheet(NonQSSStyle.displayValueTempStyle)
                self.warning("CPRI Loop Mode cannot be refreshed properly")
        # TODO ADD
        self.display()

    def set_resp_handler(self, case, resp: str):
        if case == RRUCmd.SET_CPRI:
            if RespFilter.resp_check(resp):
                self.info("CPRI Config Complete!")
            else:
                self.warning("CPRI Config May be Failed")
        elif case == RRUCmd.SET_UL_OFFSET:
            if not RespFilter.resp_check(resp):
                self.warning("Ul Frame Offset cannot be set properly")
            # self._get_ul_frame_offset()
        elif case == RRUCmd.SET_DL_OFFSET:
            if not RespFilter.resp_check(resp):
                self.warning("Dl Frame Offset cannot be set properly")
            # self._get_dl_frame_offset()
        elif case == RRUCmd.SET_AXI_OFFSET:
            if not RespFilter.resp_check(resp):
                self.warning("Axis Offset cannot be set properly")
            # self._get_axi_offset()
        elif case == RRUCmd.SET_CPRI_LOOP_MODE:
            if not RespFilter.resp_check(resp):
                self.warning("CPRI Loop Mode cannot be set properly")
            # self._get_cpri_loop_mode()
        # TODO ADD

    def refresh_all(self, connect):
        if connect:
            for i in range(RRUCmd.ant_num[self.parentWidget.option]):
                self.antenna_bean_arr.append(Antenna())
            self._refresh_all_value()
        else:
            self.antenna_bean_arr.clear()
        self.setEnabled(connect)

    def _refresh_all_value(self):
        if TelRepository.telnet_instance.isTelnetLogined:
            pass
            # self._get_axi_offset()
            # self._get_cpri_status()
            # self.refresh_s_slot()
            # self.refresh_tdd_slot()
            # TODO ADD

    def _ul_offset_edit_back2normal(self):
        self.antenna_bean_arr[self.antenna_index].ulFrameOffset2Set = self.ulOffsetEdit.text()
        self.ulOffsetEdit.setStyleSheet(valueEditStyle)

    def _dl_offset_edit_back2normal(self):
        self.antenna_bean_arr[self.antenna_index].dlFrameOffset2Set = self.dlOffsetEdit.text()
        self.dlOffsetEdit.setStyleSheet(valueEditStyle)

    def _axi_offset_edit_back2normal(self):
        self.axisOffsetEdit.setStyleSheet(valueEditStyle)

    def _cpri_loop_mode_edit_back2normal(self):
        self.cpriLoopModeEdit.setStyleSheet(valueEditStyle)

    def quick_refresh(self, cmd):
        if TelRepository.telnet_instance.isTelnetLogined:
            if cmd == RRUCmd.GET_UL_OFFSET:
                self._get_ul_frame_offset()
            elif cmd == RRUCmd.GET_DL_OFFSET:
                self._get_dl_frame_offset()
            elif cmd == RRUCmd.GET_AXI_OFFSET:
                self._get_axi_offset()
            elif cmd == RRUCmd.GET_CPRI_STATUS:
                self._get_cpri_status()
            elif cmd == RRUCmd.GET_CPRI_LOOP_MODE:
                self._get_cpri_loop_mode()
