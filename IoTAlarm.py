import machine
from machine import Pin, I2C
import utime
import network
import _thread
from umqtt.simple import MQTTClient
from buzzer import play_notes
import ssd1306

SSID = ""
PASSWORD = ""

MQTT_SERVER = ""
MQTT_PORT = 8883
MQTT_USER = ""
MQTT_PASSWORD = ""

pir = machine.Pin(5, machine.Pin.IN)
led = machine.Pin(8, machine.Pin.OUT)

button = Pin(21, Pin.IN, Pin.PULL_UP)   # press = 0
switch = Pin(9, Pin.IN, Pin.PULL_UP)

previous_switch_state = switch.value()
last_message = ""
is_armed = False

i2c = I2C(0, scl=Pin(12), sda=Pin(11))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

mqtt_client = None
wlan = network.WLAN(network.STA_IF)

def connect_to_wifi():
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Trying to connect to wi-fi...")
        utime.sleep(2)
    print("Wi-Fi connected, IP:", wlan.ifconfig()[0])

def on_message_received(topic, msg):
    global last_message, is_armed
    """
    umqtt.simple gives you BYTES for both topic and msg.
    """
    global last_message
    print("Received:", topic, msg)

    if topic != b"IoTAlarm":
        return
    
    try:
        text = msg.decode().strip().lower()
    except:
        text = str(msg).strip().lower()
    
    last_message = text
    
    # update the armed state
    if text == "arm":
        is_armed = True
        print("System Armed")
        return
    elif text == "disarm":
        is_armed = False
        print("System Disarmed")
        return
    
    # react to motion only is armed
    if text == "motion" and is_armed:
        print("Motion while armed -> Buzzer ON")
        play_notes()



def motion_handler(pin):
    print("Motion Detected")
    if mqtt_client is not None:
        mqtt_client.publish(b"IoTAlarm", b"motion")
    else:
        print("MQTT client is not connected")

def connect_mqtt(device_id, callback):
    global mqtt_client
    while mqtt_client is None:
        try:
            print("Trying to connect to MQTT server...")
            mqtt_client = MQTTClient(
                device_id,
                MQTT_SERVER,
                MQTT_PORT,
                user=MQTT_USER,
                password=MQTT_PASSWORD,
                ssl=True,
                ssl_params={"server_hostname": MQTT_SERVER},
            )
            mqtt_client.set_callback(on_message_received)
            mqtt_client.connect()
            mqtt_client.subscribe(b"IoTAlarm")
            print("Connected to MQTT Server")
        except Exception as e:
            mqtt_client = None
            print("Failed to connect to MQTT Server, retrying...", e)
            utime.sleep(3)

def connection_status():
    while True:
        if wlan.isconnected():
            if mqtt_client is not None:
                led.on()  # steady on
                utime.sleep(1)
            else:
                led.on()
                utime.sleep(0.5)
                led.off()
                utime.sleep(0.5)
        else:
            led.on()
            utime.sleep(1)
            led.off()
            utime.sleep(1)

def display_status():
    global last_message
    is_armed = False
    while True:
        display.fill(0)

        msg_line = "MQTT Connected" if mqtt_client else "MQTT Waiting"
        display.text(msg_line, 0, 0)

        if last_message == "arm":
            is_armed = True
        elif last_message == "disarm":
            is_armed = False

        display.text("Status: Armed" if is_armed else "Status: Disarmed", 0, 20)
        display.text("Msg: " + last_message, 0, 40)
        display.show()
        utime.sleep(1)

def main():
    global last_message, previous_switch_state

    button_start_time = None

    connect_to_wifi()
    connect_mqtt("IoTAlarmSystem", on_message_received)

    # Start background threads AFTER wifi/mqtt init
    _thread.start_new_thread(connection_status, ())
    _thread.start_new_thread(display_status, ())

    # PIR interrupt
    pir.irq(trigger=machine.Pin.IRQ_RISING, handler=motion_handler)

    while True:
        # --- Button: hold 1 second => arm ---
        if button.value() == 0:
            if button_start_time is None:
                button_start_time = utime.ticks_ms()
            else:
                elapsed = utime.ticks_diff(utime.ticks_ms(), button_start_time)
                if elapsed >= 1000:
                    if mqtt_client:
                        mqtt_client.publish(b"IoTAlarm", b"arm")
                        last_message = "arm"
                    button_start_time = None
        else:
            # released, reset timer
            button_start_time = None

        # --- Switch change => disarm ---
        current_switch_state = switch.value()
        if current_switch_state != previous_switch_state:
            if mqtt_client:
                mqtt_client.publish(b"IoTAlarm", b"disarm")
                last_message = "disarm"
            previous_switch_state = current_switch_state

        # --- Process incoming MQTT ---
        try:
            if mqtt_client:
                mqtt_client.check_msg()
        except Exception as e:
            print("Error checking MQTT message:", str(e))
            utime.sleep(1)

        utime.sleep(0.1)

main()
