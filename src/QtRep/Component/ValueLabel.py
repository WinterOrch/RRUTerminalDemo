from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class ValueLabel(QtWidgets.QLabel):
    refreshSig = QtCore.pyqtSignal(int)

    def __init__(self, txt, cmd):
        super().__init__(txt)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.pop_context_menu)

        self.cmd = cmd

    def pop_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.addAction(QtWidgets.QAction('Refresh', menu))
        menu.triggered.connect(self.action_slot)
        menu.exec_(QtGui.QCursor.pos())

    def action_slot(self, act):
        self.refreshSig.emit(self.cmd)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == QtCore.Qt.LeftButton:
            self.refreshSig.emit(self.cmd)
