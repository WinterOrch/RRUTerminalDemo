from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPlainTextEdit

from src.Telnet.TelRepository import TelRepository
from src.Telnet.Telnet import Telnet


class TerminalEdit(QPlainTextEdit):
    startOfValidCmd = 0

    cursorPosCurrent = 0
    cursorPosFormer = 0

    isCmdInput = False

    def __init__(self):
        super(QPlainTextEdit, self).__init__()
        self.textChanged.connect(self.todo_when_text_changed)
        self.cursorPositionChanged.connect(self.todo_when_cursor_pos_changed)
        self.setFont(QFont('sans-serif', 10))

    def keyPressEvent(self, event):
        QPlainTextEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key_Return:
            cursor = self.textCursor()
            cursor.clearSelection()
            cursor.deletePreviousChar()
            self.process_cmd_for_transmitting()

    def test(self):
        self.setPlainText('ERROR\n')
        self.startOfValidCmd = 6

    # Slot for SIGNAL CURSOR POSITION CHANGED
    def todo_when_cursor_pos_changed(self):
        self.cursorPosFormer = self.cursorPosCurrent
        # print('formerPos')
        # print(self.cursorPosFormer)

        self.cursorPosCurrent = self.textCursor().position()
        # print('currentPos')
        # print(self.cursorPosCurrent)

    # Slot for SIGNAL TEXT CHANGED
    def todo_when_text_changed(self):
        if self.cursorPosFormer < self.startOfValidCmd:
            self.startOfValidCmd = self.startOfValidCmd + self.cursorPosCurrent - self.cursorPosFormer
        # print('Valid')
        # print(self.startOfValidCmd)

    def process_cmd_for_transmitting(self):
        content_split = self.toPlainText()[self.startOfValidCmd:].split('\n')
        if content_split[-1] == '':
            return False
        else:
            if self.is_telnet_opened():
                resp = TelRepository.telnet_instance.execute_command(content_split[-1])
                self.flush_response(resp)
            else:
                self.warn_tel_not_opened()

    # TODO: 默认只能通过 telnet open 进行登陆，否则会认为没登陆
    def is_telnet_opened(self):
        return Telnet.isTelnetLogined

    # TODO
    def warn_tel_not_opened(self):
        self.appendPlainText('Telnet not opened')

    # TODO: 检查Edit中显示消息是否过长以致需要删除部分旧消息
    def display_check(self):
        pass

    def new_cmd_check(self):
        if len(self.toPlainText()) > self.startOfValidCmd:
            self.isCmdInput = True
        else:
            self.isCmdInput = False

    def flush_response(self, resp):
        if resp != '':
            resp.replace('\r\n', '\n')
            self.appendPlainText(resp)
            self.display_check()
            self.startOfValidCmd = len(self.toPlainText())

    def all_clear(self):
        self.setPlainText('')
        self.startOfValidCmd = 0
