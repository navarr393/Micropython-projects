import requests
import time
from sense_hat import SenseHat

url = "https://api.openweathermap.org/data/2.5/weather"
api_key = ""

location = "Los Angeles"
params = {
    "q": location,
    "appid": api_key,
    "units": "imperial"
}

# create sense object
sense = SenseHat()
sense.set_rotation(180)
last_call_time = time.time() - 350
last_weather_info = ""
last_room_temp = ""
last_cpu_temp = ""

# get cpu temp
def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        return float(f.read()) / 1000.0
    
def c_to_f(celsius):
    fahrenheit = (celsius * (9/5) + 32)
    return fahrenheit


while True:
    current_time = time.time()
    # if 350 seconds have passed then make another call
    if (current_time - last_call_time >= 350):
        
        response = requests.get(url, params=params)
        data = response.json()
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        weather_info = f"Location: {location}: {temperature}F {description}"
        last_weather_info = weather_info
        
        # room temp using sense hat sensors
        sensor_temp_h = sense.get_temperature_from_humidity()
        sensor_temp_p = sense.get_temperature_from_pressure()
        sensor_temp_avg = (sensor_temp_h + sensor_temp_p) / 2
        
        cpu_temp = get_cpu_temp()
        
        estimate_temp_from_sensors = sensor_temp_avg - ((cpu_temp - sensor_temp_avg) / 1.5)
        estimate_temp_in_fahrenheit = c_to_f(estimate_temp_from_sensors) - 10.0
        
        room_temp = f"Estimate Room Temp: {estimate_temp_in_fahrenheit:.1f}F"
        last_room_temp = room_temp
        
        show_cpu_temp = f"CPU Temp: {cpu_temp:.1f}C"
        last_cpu_temp = show_cpu_temp
        
        last_call_time = current_time
    
    # Display all messages every iteration
    sense.show_message(last_weather_info, scroll_speed=0.05, text_colour=[0, 0, 255])
    sense.show_message(last_room_temp, scroll_speed=0.05, text_colour=[0, 255, 0])
    sense.show_message(last_cpu_temp, scroll_speed=0.05, text_colour=[255, 0, 0])
    
    time.sleep(1)
