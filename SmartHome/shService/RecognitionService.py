import cv2
import numpy as np
import dlib
from collections import OrderedDict
import torch 
from torch import nn
from torch.utils.checkpoint import checkpoint
import sys
sys.path.append("../GUI/insightface/recognition/arcface_torch")

from backbones.iresnet import iresnet50
import mysql.connector
import json
import socket
import time
import requests

HOST = '192.168.0.11'
PORT = 80

failCount = 0
lockout_time = None  # 인증 차단 시작 시간 (초기값: 없음)
LOCKOUT_DURATION = 3 * 60  # 차단 시간 (초 단위, 3분)

remote = mysql.connector.connect(
    host = "database-1.c7iiuw4kenou.ap-northeast-2.rds.amazonaws.com",
    user = "chillHome",
    password = "addinedu1!",
    database = "chillHome"
)

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

def face_embedding(model, img, dsize=112, device='cuda'):
    img = cv2.resize(img, (dsize,dsize))
    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img).unsqueeze(0).float()
    img.div_(255).sub_(0.5).div_(0.5)
    img = img.to(device)
    embed = model(img).detach().cpu().numpy()
    return l2_norm(embed)

def move_servo(position):
    url = f"http://{HOST}:{PORT}/{position}"
    requests.get(url)

weight_path = "./model/face_recognition.pt"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = iresnet50().to(device)
model.load_state_dict(torch.load(weight_path, map_location = device))
model.eval()

URL = "http://192.168.0.52"

cursor = remote.cursor()
cursor.execute("SELECT embedding FROM faceEmbeddings where userId = 1")
records = cursor.fetchall()
stored_embeddings = [np.array(json.loads(record[0])).reshape(512) for record in records]

cap = cv2.VideoCapture(URL + ":81/stream")

if not cap.isOpened():
    raise RuntimeError("카메라가 열리지 않습니다.")

try:
    while True:
        ret, frame = cap.read()
        frame_height, frame_width = frame.shape[:2]

        if failCount >= 5:
            if lockout_time is None:
                lockout_time = time.time()  # 현재 시간 저장

            elapsed_time = time.time() - lockout_time
            remaining_time = LOCKOUT_DURATION - elapsed_time

            if remaining_time > 0:
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                
                text = f"LockOut: {minutes}:{seconds}"

                # 프레임에 차단 메시지 표시
                cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('FACE ID', frame)
                if cv2.waitKey(1) == 27:
                    break

                continue
            else:
                failCount = 0  # 실패 횟수 초기화
                lockout_time = None  # 차단 해제

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_detection = face_detector(frame, 0)
        
        if len(face_detection) > 0:
            f = face_detection[0]

            x1, y1, x2, y2 = f.left(), f.top(), f.right(), f.bottom()
            faceAligned = fa.align(frame, gray, f)

            known_embed = face_embedding(model, faceAligned, 112).reshape(512) 
            embedding_json = json.dumps(known_embed.tolist())
            

            authentication_success = False

            for record in records:
                stored_embedding = np.array(json.loads(record[0])).reshape(512) 
                similarity = np.dot(known_embed, stored_embedding) / (np.linalg.norm(known_embed) * np.linalg.norm(stored_embedding))

                if similarity > 0.6:
                    authentication_success = True
                    break

            if authentication_success:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                move_servo("DO")

                text = "Auth Success"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                text_x = (frame_width - text_size[0]) // 2
                text_y = frame_height - 50

                cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                time.sleep(0.5)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                move_servo("DC")

                text = "Auth fail"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                text_x = (frame_width - text_size[0]) // 2
                text_y = frame_height - 50

                # 텍스트 출력
                cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 225), 2)
                failCount += 1
                time.sleep(0.2)

        cv2.imshow('FACE ID', frame)

        if cv2.waitKey(1) == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()