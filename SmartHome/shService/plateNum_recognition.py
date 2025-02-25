'''
Plate Number detection with Serial Connection
'''

import cv2
import easyocr
import serial
import time
import mysql.connector

# Initialize OCR reader
reader = easyocr.Reader(['en'])

# Define the serial connection to Arduino (adjust COM port as needed)
conn = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Wait for connection to establish

# Find if it's authorized plates

# "SELECT * FROM numberPlates WHERE numberPlate = %s"
authorized_plates = {"ABC123", "XYZ789"}

def openGarage(self):
    return

def closeGarage(self):
    return


def readPlates(self):
    # open the webcam
    # capture and save as jpg
    # easy ocr
    # if it's right -> open
    openGarage()
    # else notify user 'un-authorized plates has been detected'
    return


def detectObstacle(self):
    # if it's closing
    # if obstacle detected
    # stop and open the garage door
    return


def connect(self):
    # connect to serial
    conn = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    return
