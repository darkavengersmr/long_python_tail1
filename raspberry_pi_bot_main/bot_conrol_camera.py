#!/usr/bin/env python3

import numpy as np
from imutils.video import WebcamVideoStream
import cv2

cap = WebcamVideoStream(src=0).start()
frame = cap.read()
cv2.imwrite('/var/www/html/bot_control_central.png', frame)
cv2.imwrite('/var/www/html/bot_control_central360.png', frame[420:, 120:520, :])

hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

frame_gray = cv2.inRange(hsv[420:, :, :], (0, 0, 0), (255, 225, 50))
cv2.imwrite('/var/www/html/bot_control_gray.png', frame_gray)

frame_blue = cv2.inRange(hsv, (100, 130, 70), (135, 250, 250))
cv2.imwrite('/var/www/html/bot_control_blue.png', frame_blue)

frame_red = cv2.inRange(hsv[:, 320:, :], (0, 150, 30), (10, 255, 255))
cv2.imwrite('/var/www/html/bot_control_red.png', frame_red)

frame_green = cv2.inRange(hsv, (0, 100, 50), (90, 250, 250))
cv2.imwrite('/var/www/html/bot_control_green.png', frame_green)

print("gray -", np.sum(frame_gray))
print("blue -", np.sum(frame_blue))
print("red -", np.sum(frame_red))

