from time import sleep_ms, ticks_ms
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd
import network
import time
import urequests
import ujson

# connect to wifi first to be able and call API
SSID = 'yourssid'
PASSWORD = 'yourpassword!'
API_KEY = 'yourapikey'
CITY = 'Los Angeles'

# The PCF8574 has a jumper selectable address: 0x20 - 0x27
DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0, scl=Pin(12), sda=Pin(11), freq=100000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

def connect_to_wifi():
    # create a WLAN station interface
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # connect to the wifi network
    wlan.connect(SSID, PASSWORD)
    print("Connecting to Wi-Fi")
    
    # wait for connection
    while not wlan.isconnected():
        print("Trying to connect to Wi-Fi")
        time.sleep(1)
        print("\nConnected to Wi-Fi")
    print("IP Address:", wlan.ifconfig()[0])

def fetch_weather():
    city_encoded = CITY.replace(" ", "%20") # take away the space or else the link will be invalid, unlike using normal python
    url = f'http://api.openweathermap.org/data/2.5/weather?appid={API_KEY}&q={city_encoded}&units=imperial'
    
    try:
        response = urequests.get(url)
        
        # Print the raw response for debugging
        print("Raw response:", response.text)
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print("Response content:", response.text)
            return None, None
        
        data = response.json()
        response.close()
        
        # Extract relevant data
        temp = data['main']['temp']
        weather_description = data['weather'][0]['description']
        
        return temp, weather_description
    
    except ValueError as e:
        print("Error: Invalid JSON response")
        print("Exception:", e)
        return None, None
    except Exception as e:
        print("Error fetching weather data:", e)
        return None, None
    
# display the weather data on the LCD
def display_weather(temp, description):
    lcd.clear()
    time.sleep(0.1)  # Short delay after clearing the LCD

    # Write temperature to the first line
    lcd.putstr("Temp: {:.1f} F".format(temp))
    time.sleep(0.1)  # Short delay between writes

    # Write description to the second line
    lcd.putstr("\nDes: {}".format(description))

    # Optional: Delay before the next update to give time to read the display
    time.sleep(2)
    
def test_main():
    """Test function for verifying basic functionality."""
    print("Running test_main")
    i2c = I2C(0, scl=Pin(12), sda=Pin(11), freq=100000)
    lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)
    lcd.putstr("Hello World!")
    sleep_ms(3000)

def main():
    connect_to_wifi()
    
    while True:
        try:
            temp, description = fetch_weather()
            display_weather(temp, description)
            time.sleep(600) # Update every 10 mins
        except Exception as e:
            print("Error:", e)
            lcd.clear()
            lcd.putstr("Error fetching\nweather data")
            time.sleep(60) # wait for 1 min before retrying
            
if __name__ == "__main__":
    main()