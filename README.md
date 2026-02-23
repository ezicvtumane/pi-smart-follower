Markdown
# Pi-Smart-Follower 🤖

Autonomous mobile robot based on **Raspberry Pi 4** that uses computer vision to track ArUco markers and provides a web-based remote control interface.

## 🌟 Key Features
* **Autonomous Tracking**: Real-time marker detection using OpenCV and the modern `Picamera2` library for Raspberry Pi OS Bookworm.
* **Smart Safety**: Built-in "Auto-Stop" logic that calculates distance based on marker width to prevent collisions.
* **Web Dashboard**: Flask-powered remote control panel accessible via smartphone with live CPU temperature monitoring.
* **Robust Power System**: Custom 2S 18650 battery configuration with a DC-DC Buck converter for maximum stability.

## 🛠 Hardware Architecture
* **Controller**: Raspberry Pi 4 (4GB RAM).
* **Vision**: OV5647 Camera Module (5MP).
* **Power**: 2x 18650 Li-ion cells (7.4V) with integrated protection.
* **Voltage Regulation**: Adjustable Buck Converter set to **5.1V** connected to GPIO Pins 2 & 6.
* **Motor Control**: Dual DC motors connected via GPIO pins 17, 27, 22, 23.

## 📂 Project Structure
* `src/`: Core Python source code including the multi-threaded Flask and CV logic.
* `hardware/`: Electrical schematics, wiring diagrams, and component photos.
* `docs/`: Technical report (PDF) and project presentation for the 10th-grade engineering competition.

## 🚀 Getting Started
1. **System Setup**: Ensure your Raspberry Pi is running the latest OS (Bookworm).
2. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-flask python3-numpy python3-opencv
Run the Project:

Bash
python3 src/super_robot.py
Access the Remote: Navigate to http://<your_pi_ip>:5000 on your smartphone browser.

📝 Developed by a 9th-grade student as an engineering research project in robotics and computer vision.



# Pi-Smart-Follower 🤖

Автономный мобильный робот на базе **Raspberry Pi 4**, использующий компьютерное зрение для следования за объектом (маркером ArUco) с возможностью удаленного управления через веб-интерфейс.

## 🌟 Ключевые возможности
* **Автономное следование**: Распознавание маркеров в реальном времени с использованием OpenCV и современной библиотеки `Picamera2` для ОС Bookworm.
* **Интеллектуальная безопасность**: Алгоритм «автостопа», вычисляющий дистанцию по ширине маркера для предотвращения столкновений.
* **Веб-пульт управления**: Панель управления на Flask, доступная со смартфона, с мониторингом температуры процессора в реальном времени.
* **Стабильное питание**: Кастомная система на базе двух аккумуляторов 18650 и DC-DC преобразователя для защиты от просадок напряжения.

## 🛠 Аппаратная архитектура
* **Контроллер**: Raspberry Pi 4 (4ГБ RAM).
* **Зрение**: Модуль камеры OV5647 (5 Мп).
* **Питание**: 2x Li-ion аккумулятора 18650 (7.4В) со встроенной защитой.
* **Регулировка напряжения**: Понижающий DC-DC модуль, настроенный на **5.1В**, подключенный к пинам GPIO 2 и 6.
* **Привод**: Два мотора постоянного тока, подключенные к GPIO 17, 27, 22, 23.

## 📂 Структура проекта
* `src/`: Основной код на Python (многопоточная логика Flask и OpenCV).
* `hardware/`: Электрические схемы, фотографии модулей и схемы подключений.
* `docs/`: Пояснительная записка (PDF) и презентация для защиты проекта.

## 🚀 Запуск проекта
1. **Настройка системы**: Убедитесь, что на Raspberry Pi установлена актуальная ОС (Bookworm).
2. **Установка зависимостей**:
   ```bash
   sudo apt update
   sudo apt install python3-flask python3-numpy python3-opencv
Запуск:

Bash
python3 src/super_robot.py
Управление: Откройте в браузере смартфона адрес http://<IP_вашей_малины>:5000.

📝 Проект выполнен ученицей 9-го класса в рамках инженерно-исследовательской работы по направлению «Транспортно-логистические системы, морские, авиационные и беспилотные технологии», «Большие данные, искусственный интеллект, автоматизированные системы и информационная безопасность»».
