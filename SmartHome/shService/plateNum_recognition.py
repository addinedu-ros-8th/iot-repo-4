import easyocr
import cv2
import matplotlib.pyplot as plt


reader = easyocr.Reader(['ko', 'en']) # 한국어, 영어, 숫자 인식

img_path = '/home/lsy/dev_ws/245우9315.png' # 사진 경로
img = cv2.imread(img_path)

# Grayscale 변환 (흑백 처리)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Adaptive Thresholding (이진화 처리)
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 11, 2)

# OCR 실행
result = reader.readtext(thresh)

# 결과 출력
for (bbox, text, prob) in result:
    print(f"인식된 텍스트: {text} (정확도: {prob:.2f})")
    top_left, top_right, bottom_right, bottom_left = bbox
    top_left = tuple(map(int, top_left))
    bottom_right = tuple(map(int, bottom_right))

    # 번호판 영역 박스로 표시
    cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
    cv2.putText(img, text, top_left, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

plt.figure(figsize=(10, 10))
plt.imshow(img[:, :, ::-1])
plt.axis('off')
plt.show()

# result = reader.readtext(img_path)
result  # 이미지좌표, OCR, 예측정확도