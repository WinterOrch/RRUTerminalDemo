from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton, QVBoxLayout

from src.QtRep.TerminalEdit import TerminalEdit


class TerminalWidget(QtWidgets.QWidget):

    def __init__(self):
        super(TerminalWidget, self).__init__()

        with open('../Qss/TerminalEditQSS.qss', 'r') as file:
            str = file.readlines()
            str = ''.join(str).strip('\n')

        self.setStyleSheet(str)
        self._setup_ui()

    def _setup_ui(self):
        self.textEdit = TerminalEdit()
        self.buttonText = QPushButton('Clear')

        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        layout.addWidget(self.buttonText)

        self.setLayout(layout)

        self.buttonText.clicked.connect(self.onclick_clear_text)

    def onclick_clear_text(self):
        self.textEdit.all_clear()

    def show_response(self, connect):
        self.textEdit.flush_response(connect)
