#By SOHAN VICHARE and ABHINAV AYALUR 2016
#import required libraries and dependencies
import numpy as np
from collections import deque
import cv2
from video import create_capture
from common import clock, draw_str
import itertools as it
import sys
import operator
import time
import imutils
import math

from picamera.array import PiRGBArray
from picamera import PiCamera
camera = PiCamera()
rawCapture = PiRGBArray(camera)
pts = deque(maxlen=242)
def detect():
	while True:
		camera.capture(rawCapture, format="bgr")
                frame = rawCapture.array #Image Resizing and Color Thresholding
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		lower_color = np.array([0, 130, 140])
		upper_color = np.array([30, 255, 255])
		mask = cv2.inRange(hsv, lower_color, upper_color)
		mask = cv2.dilate(mask, None, iterations=2)
		cv2.imshow("mask frame", mask) #Show the masked frame
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = None
		if len(cnts) > 0: #Checks for contours and circle
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			if radius > 10 and radius < 300:
				cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame, center, 5, (0, 0, 255), -1)
				pts.appendleft(center)
				print(geometry([x,y,radius]));
		for i in xrange(1, len(pts)):
			if pts[i - 1] is None or pts[i] is None:
				continue
			thickness = int(np.sqrt(242 / float(i + 1)) * 2.5)
			cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
		cv2.imshow("Frame", frame) #Shows the final image with radius and circle
                rawCapture.truncate(0)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break


def auto_canny(image, sigma=0.33): #Uses algorithm to scan for circles
	v = np.median(image)
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
	return edged

def distance(radius): #product of pixel radius and distance is constant; inverse
	return 2000/radius

def geometry(point): #Precalibrated value lets us find distance and angleS
        returnval = [0]
        if point[2] != 0:
                calVal = (1.875)/1000
                x = point[0]
                y = point[1]
                r = point[2]
	
                dInInches = distance(r)
                offCenter = x-456
                inchesOffCenter = calVal*dInInches*offCenter
                print(inchesOffCenter)
                print(dInInches)
                print(inchesOffCenter/dInInches)
                angle = math.asin(inchesOffCenter/dInInches)
                print (angle)
                angle = angle*180/math.pi
                returnval = [dInInches, angle]
	return returnval

capture = cv2.VideoCapture(0)

# allow the camera to warmup
time.sleep(0.1)

#begin capturing video using video.py to deal with dropped frames
cam = create_capture(0)

#run main detection method
detect()

cam.release()

cv2.destroyAllWindows()
