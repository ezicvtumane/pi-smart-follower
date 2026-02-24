import cv2
import numpy as np
from flask import Flask, render_template_string, Response, request
from picamera2 import Picamera2
from gpiozero import Robot
import threading
import time

# Подключаем моторы.
# левый мотор висит на пинах 17 и 27, правый - на 22 и 23.
robot = Robot(left=(17, 27), right=(22, 23))

# Запускаем  камеру 
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Настройки для поиска меток
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# Мои настройки и константы
AUTO_MODE = False  # Со старта робот стоит в ручном режиме
CENTER_X = 320  # Центр экрана (половина от 640)
STOP_WIDTH = 180  # Экспериментально: если ширина метки > 180px, это ~30 см, надо тормозить
KP = 0.01  # Коэффициент для плавного подруливания (П-регулятор)
BASE_SPEED = 0.55  # Базовая скорость моторов

latest_frame = None  # Сюда кадры для веба
frame_lock = threading.Lock()

app = Flask(__name__)


def autonomous_loop():
    """Этот поток отвечает за зрение и езду за меткой"""
    global AUTO_MODE, latest_frame

    while True:
        frame = picam2.capture_array()

        # Переводим в ЧБ, чтобы OpenCV считал быстрее
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = detector.detectMarkers(gray)

        if ids is not None and AUTO_MODE:
            # Рисуем зеленую рамку вокруг метки для красоты в FPV
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            c = corners[0][0]
            marker_width = c[1][0] - c[0][0]
            marker_center_x = int((c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4)

            # Система безопасности
            if marker_width > STOP_WIDTH:
                robot.stop()
            else:
                # Математика П-регулятора
                error = CENTER_X - marker_center_x

                left_speed = BASE_SPEED - (error * KP)
                right_speed = BASE_SPEED + (error * KP)

                # Защита от выхода за пределы (-1.0 ... 1.0)
                left_speed = max(-1.0, min(1.0, left_speed))
                right_speed = max(-1.0, min(1.0, right_speed))

                robot.value = (left_speed, right_speed)

        elif AUTO_MODE:
            # Если метка потерялась - стоим и ждем
            robot.stop()

        # Сохраняем кадр, чтобы сервер Flask мог его забрать
        with frame_lock:
            latest_frame = frame.copy()

        time.sleep(0.05)  # Небольшая пауза, чтобы не перегреть CPU


def generate_mjpeg():
    """Генератор видеопотока для браузера"""
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            ret, jpeg = cv2.imencode('.jpg', latest_frame)
            if not ret:
                continue
            frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/command', methods=['POST'])
def command():
    """Принимаем команды от кнопок на экране смартфона"""
    global AUTO_MODE
    cmd = request.form.get('cmd')

    if cmd == 'switch_mode':
        AUTO_MODE = not AUTO_MODE
        robot.stop()
        return "Mode switched"

    if not AUTO_MODE:
        if cmd == 'up':
            robot.forward(BASE_SPEED)
        elif cmd == 'down':
            robot.backward(BASE_SPEED)
        elif cmd == 'left':
            robot.left(BASE_SPEED)
        elif cmd == 'right':
            robot.right(BASE_SPEED)
        elif cmd == 'stop':
            robot.stop()

    return "OK"


# HTML интерфейс. используем ontouchstart вместо onclick, 
# чтобы на смартфонах не было задержки (пинга) при нажатии.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <title>Alice's Bot Control</title>
    <style>
        body { background-color: #222; color: white; text-align: center; font-family: sans-serif; touch-action: manipulation; }
        img { width: 100%; max-width: 640px; border: 2px solid #555; margin-bottom: 15px;}
        .btn { padding: 20px; margin: 5px; font-size: 18px; background-color: #444; color: white; border: none; border-radius: 10px; width: 80px; }
        .btn-wide { width: 200px; background-color: #3b5998; margin-bottom: 10px;}
        .btn-stop { background-color: #cc0000; width: 200px; }
    </style>
</head>
<body>
    <h2>Alice's Bot - FPV Control</h2>
    <img src="/video_feed" />
    <br>
    <button class="btn btn-wide" onclick="sendCommand('switch_mode')">РУЧНОЙ / АВТО</button>
    <br>
    <table>
        <tr>
            <td></td>
            <td><button class="btn" ontouchstart="sendCommand('up')" ontouchend="sendCommand('stop')" onmousedown="sendCommand('up')" onmouseup="sendCommand('stop')">Вперед</button></td>
            <td></td>
        </tr>
        <tr>
            <td><button class="btn" ontouchstart="sendCommand('left')" ontouchend="sendCommand('stop')" onmousedown="sendCommand('left')" onmouseup="sendCommand('stop')">Влево</button></td>
            <td><button class="btn btn-stop" onclick="sendCommand('stop')">СТОП</button></td>
            <td><button class="btn" ontouchstart="sendCommand('right')" ontouchend="sendCommand('stop')" onmousedown="sendCommand('right')" onmouseup="sendCommand('stop')">Вправо</button></td>
        </tr>
        <tr>
            <td></td>
            <td><button class="btn" ontouchstart="sendCommand('down')" ontouchend="sendCommand('stop')" onmousedown="sendCommand('down')" onmouseup="sendCommand('stop')">Назад</button></td>
            <td></td>
        </tr>
    </table>

    <script>
        function sendCommand(cmd) {
            fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'cmd=' + cmd
            });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


if __name__ == '__main__':
    # Запускаем автопилот в фоновом потоке
    auto_thread = threading.Thread(target=autonomous_loop, daemon=True)
    auto_thread.start()

    # Запускаем сервер на порту 5000
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
