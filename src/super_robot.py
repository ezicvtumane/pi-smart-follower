from flask import Flask, render_template_string
from gpiozero import Robot
from picamera2 import Picamera2
import cv2
import numpy as np
import threading
import time  # <--- Тот самый пропущенный импорт

app = Flask(__name__)

# --- 1. HARDWARE ---
# Using pins from your assembly
robot = Robot(left=(17, 27), right=(22, 23))
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# --- 2. VISION & SETTINGS ---
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# Global control variables
MODE = "MANUAL" 
BASE_SPEED = 35
STOP_WIDTH = 180
KP = 0.15
CENTER_X = 320

# --- 3. WEB INTERFACE ---
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        .btn { padding: 25px; font-size: 22px; width: 42%; margin: 8px; border-radius: 15px; border: none; font-weight: bold; }
        .stop { background-color: #ff4444; color: white; width: 88%; }
        .mode { background-color: #4444ff; color: white; width: 88%; }
        .dir { background-color: #666; color: white; }
    </style>
</head>
<body style="text-align: center; background-color: #222; color: white; font-family: Arial;">
    <h1>Robot Command Center</h1>
    <button class="btn mode" onclick="fetch('/toggle_mode')">SWITCH MODE (Current: {{mode}})</button><br><br>
    
    <div id="controls">
        <button class="btn dir" onclick="fetch('/forward')">FORWARD</button><br>
        <button class="btn dir" onclick="fetch('/left')">LEFT</button>
        <button class="btn dir" onclick="fetch('/right')">RIGHT</button><br>
        <button class="btn dir" onclick="fetch('/backward')">BACKWARD</button><br>
        <button class="btn stop" onclick="fetch('/stop')">EMERGENCY STOP</button>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, mode=MODE)

@app.route('/toggle_mode')
def toggle():
    global MODE
    MODE = "AUTO" if MODE == "MANUAL" else "MANUAL"
    print(f"System: Mode changed to {MODE}")
    return "OK"

# Manual control routes
@app.route('/forward')
def fwd(): robot.forward(0.5); return "OK"
@app.route('/backward')
def bwd(): robot.backward(0.5); return "OK"
@app.route('/left')
def left(): robot.left(0.4); return "OK"
@app.route('/right')
def right(): robot.right(0.4); return "OK"
@app.route('/stop')
def stop(): robot.stop(); return "OK"

# --- 4. AUTOPILOT THREAD ---
def autopilot_loop():
    global MODE
    while True:
        if MODE == "AUTO":
            # Direct frame capture
            frame = picam2.capture_array()
            if frame is not None:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                corners, ids, rejected = detector.detectMarkers(gray)
                
                if ids is not None:
                    c = corners[0][0]
                    # Distance proxy by marker width
                    width = np.linalg.norm(c[0] - c[1])
                    # Center X for steering
                    marker_x = int((c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4)
                    
                    if width > STOP_WIDTH:
                        robot.stop()
                    else:
                        error = marker_x - CENTER_X
                        steering = (error * KP) / 100.0
                        left = (BASE_SPEED / 100.0) + steering
                        right = (BASE_SPEED / 100.0) - steering
                        robot.value = (max(-1, min(1, left)), max(-1, min(1, right)))
                else:
                    robot.stop()
        time.sleep(0.05) # Loop delay to save CPU

# Start background logic
threading.Thread(target=autopilot_loop, daemon=True).start()

if __name__ == '__main__':
    # Flask launches on your Pi IP: 192.168.0.27
    app.run(host='0.0.0.0', port=5000)
