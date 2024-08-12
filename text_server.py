# this file creates a server to transimit the text from the iOS app to the LCD
# using wifi

#import the necessary libraries
import network
import socket
import time
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

# initialize the wifi
ssid = 'yourssid'
password = 'yourpassword'

# initialize the LCD
# The PCF8574 has a jumper selectable address: 0x20 - 0x27
DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0, scl=Pin(12), sda=Pin(11), freq=100000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

# try and connect to wifi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print("Connection Successful")
print(station.ifconfig())

#  set up the web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Listening on", addr)

# funct to handle http requests
def web_page(text=""):
    html = f"""
    <html>
    <head>
        <title>ESP32 LCD</title>
    </head>
    <body>
        <h1>ESP32 LCD Text Sender</h1>
        <form action="/" method="post">
            <input type="text" name="text" value="{text}">
            <input type="submit" value="Send to LCD">
        </form>
        <p>Current Text: {text}</p>
    </body>
    </html>
    """
    return html

# listening for incoming connections
while True:
    conn, addr = s.accept()
    print("Got a connection from", addr)
    
    # recieve the http request and decode it to a string
    request = conn.recv(1024)
    request_str = request.decode('utf-8')
    print("request content:", request_str)
    
    # intialize text
    text_start = request_str.find('text=') + 5
    if text_start != -1:
        text_end = request_str.find('&', text_start)
        if text_end == -1:
            text_end = len(request_str)
        text = request_str[text_start:text_end]
        text = text.replace('%20', ' ')  # Replace URL-encoded spaces with actual spaces
    
    # Display on the LCD
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(text[:16])  # Display the first 16 characters on the first line
    
        if len(text) > 16:
            lcd.move_to(0, 1)
            lcd.putstr(text[16:32])
        
        response = web_page(text)
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()