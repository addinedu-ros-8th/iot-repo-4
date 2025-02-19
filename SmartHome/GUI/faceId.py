import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import cv2, imutils
import time

import warnings
warnings.filterwarnings('ignore')

from_class = uic.loadUiType("faceId.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self, userId = 0):
        super().__init__()
        self.setupUi(self)

        self.pixmap = QPixmap()

        self.camera = camera(self)
        self.camera.daemon = True

        self.cameraStart()
        self.camera.update.connect(self.updateCamera)

    def cameraStart(self):
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture(-1)

    def cameraStop(self):
        self.camera.running = False
        self.count = 0
        self.video.release

    def updateCamera(self):
        retval, image = self.video.read()
        if retval:
            self.image = image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            h, w, c = image.shape
            qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

            self.label.setPixmap(self.pixmap)

class camera(QThread):
    update = pyqtSignal()

    def __init__(self, sec=0.1, parent=None):
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        count = 0
        while self.running == True:
            self.update.emit()
            time.sleep(0.05)

    def stop(self):
        self.running = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindows = WindowClass()
    mywindows.show()

    sys.exit(app.exec_())