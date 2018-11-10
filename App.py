import sys

from PyQt5 import QtWidgets
from Gui import Ui_main_window


class App:

    main_object = None
    main_window = None

    def __init__(self):
        self.main_object = QtWidgets.QApplication(sys.argv)
        self.main_window = QtWidgets.QMainWindow()
        ui = Ui_main_window()
        ui.setupUi(self.main_window)
        self.main_window.show()


if __name__ == "__main__":
    app = App()
    sys.exit(app.main_object.exec())
