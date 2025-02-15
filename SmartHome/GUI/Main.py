import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

# UI 파일 로드
from_class = uic.loadUiType("Login.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())
