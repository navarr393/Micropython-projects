# MQTT IoT Alarm System (MicroPython + HiveMQ + OLED + Buzzer)

This project is a simple **MQTT-based alarm system** built with MicroPython.  
It uses a PIR motion sensor to publish motion events, an arcade button to arm the system, and a toggle switch to disarm. An SSD1306 OLED shows status and the device plays a buzzer melody when motion is detected **while armed**.

## Features
- ✅ Connects to Wi-Fi (station mode)
- ✅ Connects to a HiveMQ Cloud broker over **TLS (port 8883)**
- ✅ Publishes MQTT messages to topic: `IoTAlarm`
- ✅ Subscribes to `IoTAlarm` and maintains an `is_armed` state
- ✅ PIR interrupt publishes `motion`
- ✅ Hold arcade button for 1s → publishes `arm`
- ✅ Flip switch → publishes `disarm`
- ✅ OLED display shows:
  - MQTT connection status
  - Armed/Disarmed state
  - Last received message
- ✅ Status LED indicates connectivity
- ✅ Plays melody (`play_notes`) when `motion` is received while armed

---

## Hardware Used
- Arduino Nano ESP32 (MicroPython)
- PIR motion sensor
- Arcade push button (switch terminals only)
- Toggle switch
- SSD1306 OLED (128x64) over I2C
- Buzzer (melody handled in `buzzer.py`)

---

## Pinout (as used in the code)

| Component | Pin |
|----------|-----|
| PIR signal | GPIO 5 |
| Status LED | GPIO 8 |
| Arcade button (hold to arm) | GPIO 21 (PULL_UP) |
| Toggle switch (disarm) | GPIO 9 (PULL_UP) |
| OLED SCL | GPIO 12 |
| OLED SDA | GPIO 11 |

> Note: Button and switch are configured with internal pull-ups. Wire each switch **to GND** when pressed/toggled.

---

## MQTT Topic + Messages

**Topic:** `IoTAlarm`

**Payloads:**
- `arm` → arms the system
- `disarm` → disarms the system
- `motion` → motion event (published by PIR)

**Behavior:**
- If `motion` is received while `is_armed == True` → buzzer melody plays.

---

## File Structure
