import sys
sys.path.append("./insightface/recognition/arcface_torch")

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import cv2
import time
import numpy as np
import dlib 
from collections import OrderedDict

import torch 

from backbones.iresnet import iresnet50
import json
import mysql.connector

import warnings
warnings.filterwarnings('ignore')

from_class = uic.loadUiType("faceId.ui")[0]

weight_path = "./model/face_recognition.pt"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = iresnet50().to(device)
model.load_state_dict(torch.load(weight_path, map_location = device))
model.eval()

class WindowClass(QMainWindow, from_class):
    def __init__(self, userId = 1):
        super().__init__()
        self.setupUi(self)
        self.userId = userId
        self.saved = False
        self.embedding_json = {}

        self.remote = mysql.connector.connect(
            host="database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
            user="chillHome",
            password="addinedu1!",
            database="chillHome"
        )

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
        self.video.release()

        cursor = self.remote.cursor()
        face_sql = "INSERT INTO faceEmbeddings (userId, embedding) VALUES (%s, %s)"
        cursor.execute(face_sql, (self.userId, self.embedding_json))
        self.remote.commit()

        log_sql = "INSERT INTO smartHomeLog (userId, wayId, statusId, logDate) VALUES (%s, %s, %s, NOW())"
        cursor.execute(log_sql, (self.userId, 1 ,9))
        self.remote.commit()
        cursor.close()

        reply = QMessageBox.information(self, "FACE ID", "등록 완료되었습니다.", QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            self.close()


    def updateCamera(self):
        retval, image = self.video.read()
        if retval:
            self.image = image
            gary_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            face_detection = face_detector(gary_image, 0)

            if len(face_detection) > 0 and not self.saved:
                f = face_detection[0]

                x1, y1, x2, y2 = f.left(), f.top(), f.right(), f.bottom()
                faceAligned = fa.align(image, gary_image, f)
                
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                known_embed = face_embedding(model, faceAligned, 112)
                self.embedding_json = json.dumps(known_embed.tolist())

                self.saved = True

            h, w, c = image.shape
            qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

            self.label.setPixmap(self.pixmap)

            if self.saved:
                self.cameraStop()
                return

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

FACIAL_LANDMARKS_68_IDXS = OrderedDict([
	("mouth", (48, 68)),
	("inner_mouth", (60, 68)),
	("right_eyebrow", (17, 22)),
	("left_eyebrow", (22, 27)),
	("right_eye", (36, 42)),
	("left_eye", (42, 48)),
	("nose", (27, 36)),
	("jaw", (0, 17))
])

FACIAL_LANDMARKS_5_IDXS = OrderedDict([
	("right_eye", (2, 3)),
	("left_eye", (0, 1)),
	("nose", (4))
])

FACIAL_LANDMARKS_IDXS = FACIAL_LANDMARKS_68_IDXS

def rect_to_bb(rect):
	x = rect.left()
	y = rect.top()
	w = rect.right() - x
	h = rect.bottom() - y
	return (x, y, w, h)

def shape_to_np(shape, dtype="int"):
	coords = np.zeros((shape.num_parts, 2), dtype=dtype)

	for i in range(0, shape.num_parts):
		coords[i] = (shape.part(i).x, shape.part(i).y)

	return coords

class FaceAligner:
    def __init__(self, predictor, desiredLeftEye=(0.35, 0.35),
        desiredFaceWidth=256, desiredFaceHeight=None):

        self.predictor = predictor
        self.desiredLeftEye = desiredLeftEye
        self.desiredFaceWidth = desiredFaceWidth
        self.desiredFaceHeight = desiredFaceHeight


        if self.desiredFaceHeight is None:
            self.desiredFaceHeight = self.desiredFaceWidth

    def align(self, image, gray, rect):
        shape = self.predictor(gray, rect)
        shape = shape_to_np(shape)

        if (len(shape)==68):
            (lStart, lEnd) = FACIAL_LANDMARKS_68_IDXS["left_eye"]
            (rStart, rEnd) = FACIAL_LANDMARKS_68_IDXS["right_eye"]
        else:
            (lStart, lEnd) = FACIAL_LANDMARKS_5_IDXS["left_eye"]
            (rStart, rEnd) = FACIAL_LANDMARKS_5_IDXS["right_eye"]
            
        leftEyePts = shape[lStart:lEnd]
        rightEyePts = shape[rStart:rEnd]

        leftEyeCenter = leftEyePts.mean(axis=0).astype("int")
        rightEyeCenter = rightEyePts.mean(axis=0).astype("int")

        dY = rightEyeCenter[1] - leftEyeCenter[1]
        dX = rightEyeCenter[0] - leftEyeCenter[0]
        angle = np.degrees(np.arctan2(dY, dX)) - 180

        desiredRightEyeX = 1.0 - self.desiredLeftEye[0]

        dist = np.sqrt((dX ** 2) + (dY ** 2))
        desiredDist = (desiredRightEyeX - self.desiredLeftEye[0])
        desiredDist *= self.desiredFaceWidth
        scale = desiredDist / dist

        eyesCenter = (int((leftEyeCenter[0] + rightEyeCenter[0]) // 2),
            int((leftEyeCenter[1] + rightEyeCenter[1]) // 2))

        M = cv2.getRotationMatrix2D(eyesCenter, angle, scale)

        tX = self.desiredFaceWidth * 0.5
        tY = self.desiredFaceHeight * self.desiredLeftEye[1]
        M[0, 2] += (tX - eyesCenter[0])
        M[1, 2] += (tY - eyesCenter[1])

        (w, h) = (self.desiredFaceWidth, self.desiredFaceHeight)
        output = cv2.warpAffine(image, M, (w, h),
            flags=cv2.INTER_CUBIC)

        return output

predictor_file = "./model/shape_predictor_68_face_landmarks.dat"
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(predictor_file)
fa = FaceAligner(shape_predictor, desiredFaceWidth=112)

def l2_norm(x, axis=1):
    norm = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / norm

def face_embedding(model, img, dsize=112, device='cuda'):
    img = cv2.resize(img, (dsize,dsize))
    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img).unsqueeze(0).float()
    img.div_(255).sub_(0.5).div_(0.5)
    img = img.to(device)
    embed = model(img).detach().cpu().numpy()
    return l2_norm(embed)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindows = WindowClass()
    mywindows.show()

    sys.exit(app.exec_())