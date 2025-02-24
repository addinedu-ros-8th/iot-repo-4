import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *

from_class = uic.loadUiType("register_rfid.ui")[0]

class Resgiter_RFID(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Resigster RFID")

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = Resgiter_RFID()
    myWindows.show()
    sys.exit(app.exec_())
