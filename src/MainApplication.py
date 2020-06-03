import sys
import logging

from PyQt5.QtWidgets import QApplication

from src.QtRep.LeftTabWidget import LeftTabWidget

LOG_FILE = '../log/log.log'


def set_logger():
    logging.basicConfig(filename='../log/' + __name__ + '.log',
                        format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level=logging.DEBUG,
                        filemode='a', datefmt='%Y-%m-%d %I:%M:%S %p')


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    set_logger()

    main_wnd = LeftTabWidget()
    main_wnd.show()

    app.exec()


if __name__ == '__main__':
    main()
