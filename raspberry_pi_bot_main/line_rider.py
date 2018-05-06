#!/usr/bin/env python3

from flask import Flask, render_template, Response
import serial, time
import cv2
import threading
import numpy as np
from imutils.video import WebcamVideoStream

port = "/dev/ttyACM0"
ser = serial.Serial(port , 115200, timeout = 1)
time.sleep(5)

speed_go = 0
porog = 500
speed = 155
K = 2
see_red = 0
x = 0
out_old = 0
i_main = 0
i_mail2arduino = 0
i_see_red = 0
i_camera2inet = 0
time_main = time.time()
time_mail2arduino = time.time()
time_see_red = time.time()
time_camera2inet = time.time()
fps_main = 0
fps_mail2arduino = 0
fps_see_red = 0
fps_camera2inet = 0
pixel_ellips = 0

cap = WebcamVideoStream(src=0).start()
for i in range(5): frame = cap.read()
frame = cap.read()
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
frame_gray = cv2.inRange(hsv[420:,:, :], (0, 0, 0), (255, 255, 100))
frame_red = cv2.inRange(hsv[:, 320:, :], (0, 150, 30), (10, 255, 80))

cv2.imwrite('/var/www/html/dgip_gray360.png', frame_gray)
cv2.imwrite('/var/www/html/dgip_frame_all.png', frame)

def mail2arduino_pr1():
    print("Start arduino thread")
    global x, out_old, speed_go, speed, i_mail2arduino, fps_mail2arduino, time_mail2arduino
    while 1:
        local_x = x
        if(local_x >= 0): out = "L"
        else: out = "R"
        local_x = abs(int(local_x*K))

        if(local_x > 90): local_x = 90
        if(local_x < 10): out += "0" + str(local_x)
        else: out += str(local_x)

        if(speed >= 100): out += "F" + str(speed)
        elif(speed >= 10): out += "F0" + str(speed)
        else: out += "F00" + str(speed)

        if(out != out_old):
            ser.write(out.encode())
            time_out = time.time()

        if(time.time() - time_out > 2):
            ser.write("0000000".encode())
            time_out = time.time()
        out_old = out
        i_mail2arduino += 1
        if(time.time() - time_mail2arduino > 1):
            time_mail2arduino = time.time()
            fps_mail2arduino = i_mail2arduino
            i_mail2arduino = 0

def image2jpeg(image):
    ret, jpeg = cv2.imencode('.jpg', image)
    return jpeg.tobytes()

def camera2inet_pr2():
    print("Start inet thread")
    global frame_gray, frame, frame_red, i_camera2inet, time_camera2inet,  fps_camera2inet
    global fps_main, fps_see_red, fps_mail2arduino, fps_camera2inet, pixel_ellips, see_red
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    def gen_gray():
        while True:
            cv2.putText(frame_gray,"fps_main: "+str(fps_main), (0,10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)
            cv2.putText(frame_gray,"fps_see_red: "+str(fps_see_red), (0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)
            cv2.putText(frame_gray,"fps_mail2arduino: "+str(fps_mail2arduino), (0,30), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)
            cv2.putText(frame_gray,"fps_camera2inet: "+str(fps_camera2inet), (0,40), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)

            frameinet = image2jpeg(frame_gray)
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frameinet + b'\r\n\r\n')
    def gen_red():
        while True:
            cv2.putText(frame_red,"red_see: "+str(see_red), (0,10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
            cv2.putText(frame_red,"red_pixel: "+str(pixel_ellips), (0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
            frameinet = image2jpeg(frame_red)
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frameinet + b'\r\n\r\n')

    @app.route('/video_line')
    def video_line():
        return Response(gen_gray(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    @app.route('/video_red')
    def video_red():
        return Response(gen_red(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    time.sleep(0.15)
    i_camera2inet += 1
    if(time.time() - time_camera2inet > 1):
        time_camera2inet = time.time()
        fps_camera2inet = i_camera2inet
        i_camera2inet = 0

    app.run(host='0.0.0.0', debug=False,threaded=True)

def see_red_pr3():
    print("Start see red thread")
    global K, pixel_ellips, see_red, hsv, frame_red, i_see_red, time_see_red, fps_see_red
    print(frame_red.dtype)
    time_last_see_red = time.time()-20
    search = True
    while 1:
        frame_red = cv2.inRange(hsv[:, 320:, :], (0, 120, 30), (10, 255, 255))
        if(search):
            frame_copy = frame_red.copy()
            _, con, hierarchy = cv2.findContours(frame_copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for i in con:
                if len(i)>10:
                    ellipse = cv2.fitEllipse(i)
                    _, y1 = ellipse[0]
                    _, y2 = ellipse[1]
                    pixel_ellips = abs(y2-y1)*0.15 + 0.85 * pixel_ellips
                    if(pixel_ellips > 200):
                        pixel_ellips = 0
                        see_red = 1
                        search = False
                        time_last_see_red = time.time()
                    else: see_red = 0
                    cv2.ellipse(frame_red, ellipse, (255,0,0), 2)
                    break
                else:
                    see_red = 0
        if(time.time() - time_last_see_red <= 10):
            see_red = 1
        if(time.time() - time_last_see_red > 10):
            see_red = 0
            K = 0.1
        if(time.time() - time_last_see_red >= 12):
            K = 1
        if(time.time() - time_last_see_red >= 20):
            search = True

        i_see_red += 1
        if(time.time() - time_see_red > 1):
            time_see_red = time.time()
            fps_see_red = i_see_red
            i_see_red = 0


pr1 = threading.Thread(target=mail2arduino_pr1)
pr1.daemon = True
pr1.start()
pr2 = threading.Thread(target=camera2inet_pr2)
pr2.daemon = True
pr2.start()
pr3 = threading.Thread(target=see_red_pr3)
pr3.daemon = True
pr3.start()

while 1:
    frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frame_gray = cv2.inRange(hsv[420:,:, :], (0, 0, 0), (255, 255, 80))
    if(np.sum(frame_gray) > porog and see_red != 1):
        speed = 255
        moments = cv2.moments(frame_gray, 1)
        dM01 = moments['m01']
        dM10 = moments['m10']
        dArea = moments['m00']

        x = 320 - int(dM10 / dArea)
        y = 120 - int(dM01 / dArea)
    else:
        speed = 0
    i_main += 1
    if(time.time() - time_main > 1):
        time_main = time.time()
        fps_main = i_main
        i_main = 0
