import sys

from PyQt5.QtWidgets import QApplication

from src.QtRep.LeftTabWidget import LeftTabWidget


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    main_wnd = LeftTabWidget()
    main_wnd.show()

    app.exec()


if __name__ == '__main__':
    main()
