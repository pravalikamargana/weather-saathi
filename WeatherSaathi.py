import requests
from datetime import datetime, timedelta
from twilio.rest import Client

API_KEY = "7ee2ec905fb7d64ede9bf550b275511c"

TWILIO_SID = "AC1234567890abcdef"
TWILIO_AUTH = "abcd1234xyz"

TWILIO_NUMBER = "+1929343560"  
MY_NUMBER = "+1234567890"      

OUTDOOR_WORDS = ["walk", "walking", "run", "running", "cycle", "cycling", "swim", "swimming",
                 "jog", "jogging", "football", "cricket", "basketball", "outdoor"]

INDOOR_WORDS = ["study", "gym", "coding", "cleaning", "reading", "cooking",
                "movie", "exercise", "indoor"]


def classify_task(task):
    task = task.lower()
    if any(word in task for word in OUTDOOR_WORDS):
        return "OUTDOOR"
    if any(word in task for word in INDOOR_WORDS):
        return "INDOOR"
    return "UNKNOWN"

def get_weather_and_time(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    try:
        weather_main = data["weather"][0]["main"]
        temp = data["main"]["temp"]
        rain = data.get("rain", {}).get("1h", 0)

        timezone_offset = data["timezone"]  # seconds
        utc_now = datetime.utcnow()
        local_time = utc_now + timedelta(seconds=timezone_offset)

        return weather_main, temp, rain, local_time
    except:
        return None, None, None, None

def send_sms(msg):
    client = Client(TWILIO_SID, TWILIO_AUTH)
    message = client.messages.create(
        from_=TWILIO_NUMBER,
        body=msg,
        to=MY_NUMBER
    )
    print("\n📩 SMS Sent!")
    print("Message SID:", message.sid)

print("=== WEATHER AWARE PERSONAL SCHEDULER ===")

city = input("Enter city name: ")
task = input("Enter task: ")
date_input = input("Enter date (YYYY-MM-DD): ")
time_input = input("Enter time (12-hour, e.g., 6 PM): ")

task_type = classify_task(task)

weather, temp, rain, local_time = get_weather_and_time(city)

print("\n--------- REPORT ---------")
print("City       :", city)
print("Task       :", task)
print("Task Type  :", task_type)
print("Date       :", date_input)
print("Time       :", time_input)

if local_time:
    print("Local Time :", local_time.strftime("%Y-%m-%d %I:%M %p"))
else:
    print("Local Time : Could not fetch")

print("Weather    :", weather)
print("Temp (°C)  :", temp)
print("Rain (mm)  :", rain)
print("---------------------------")


# ALERT LOGIC
if weather is None:
    alert = "⚠️ Could not fetch weather. Check city name."
elif task_type == "OUTDOOR" and (weather in ["Rain", "Thunderstorm", "Snow"] or rain > 0):
    alert = f"⚠️ Weather NOT suitable for outdoor task '{task}'."
else:
    alert = f"✅ Task '{task}' is safe under current weather."

print(alert)

send_sms(alert)
