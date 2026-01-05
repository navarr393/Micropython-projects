from m5stack import *
from uiflow import *
from m5mqtt import M5mqtt

HOST = "1a9752b67bde42df8937ae1c6c8b5e53.s1.eu.hivemq.cloud"
PORT = 8883
USER = ""
PASS = ""   # put the real one here

TOPIC = "IoTAlarm"

rgb.setColorAll(0xffff00)  # yellow = starting

def cb(topic_data):
    rgb.setColorAll(0xffff00)  # got something
    try:
        msg = topic_data.decode()
    except:
        msg = str(topic_data)
    msg = msg.strip().lower()

    if msg == "motion":
        rgb.setColorAll(0xff0000)
        wait(2)

    rgb.setColorAll(0x00cccc)
    
m5mqtt = M5mqtt(
    "IoTMatrix",
    HOST,
    port=PORT,
    user=USER,
    password=PASS,
    keepalive=300,
    ssl=True,
    ssl_params={"server_hostname": HOST}
)

m5mqtt.subscribe("IoTAlarm", cb)
m5mqtt.start()
rgb.setColorAll(0x00ff00)  # green = started (connected)

def buttonA_pressFor():
  m5mqtt.publish(str('IoTAlarm'), str('motion'), 0)
  
btnA.pressFor(1, buttonA_pressFor)

while True:
    wait(1)
