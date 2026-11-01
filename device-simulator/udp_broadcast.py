import paho.mqtt.client as mqtt
import json
import time
import random
import threading
import requests
import os

# MQTT configuration
broker = "localhost"
port = 1883
base_topic = "{device}/{sensor_type}"  # Topic format for each sensor
subscribe_topic = "+/+"  # Wildcard subscription topic for all devices and sensors

#call api_url to get temperature
# Optional live weather data. Configure credentials outside the source code.
weather_api_key = os.getenv("WEATHER_API_KEY")
weather_location = os.getenv("WEATHER_LOCATION", "London")
temp_celsius = 20.0
if weather_api_key:
    try:
        response = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={"key": weather_api_key, "q": weather_location, "aqi": "yes"},
            timeout=10,
        )
        response.raise_for_status()
        temp_celsius = response.json()["current"]["temp_c"]
    except (requests.RequestException, KeyError, ValueError):
        print("Live weather unavailable; using a 20 Celsius demonstration reading.")
else:
    print("WEATHER_API_KEY is unset; using a 20 Celsius demonstration reading.")

# Devices to broadcast with live-like readings
devices = [
    {
        "device_id": "Device1",
        "location": "Living Room",
        "sensors": [
            {"sensor_type": "pressure", "unit": "hPa"},
            {"sensor_type": "humidity", "unit": "%"}
        ]
    },
    {
        "device_id": "Device2",
        "location": "Room1",
        "sensors": [
            {"sensor_type": "humidity", "unit": "%"},
            {"sensor_type": "temperature", "unit": "Celsius"}
        ]
    },
    {
        "device_id": "API_Device",
        "location": "Outside",
        "sensors": [
            {"sensor_type": "temperature", "unit": "Celsius"},
        ]
    }
]

# Function to generate sensor readings
def generate_reading(device, sensor_type):
    if sensor_type == "temperature":
        if device["device_id"] == "API_Device":
            return round(temp_celsius, 2)
        return round(random.uniform(-20.0, 100.0), 2)
    elif sensor_type == "humidity":
        return round(random.uniform(0.0, 100.0), 2)
    elif sensor_type == "pressure":
        return round(random.uniform(900.0, 1100.0), 2)
    return None

# Function to broadcast sensor data for a device
def broadcast_device(device):
    client = mqtt.Client()
    client.connect(broker, port, 60)
    while True:
        for sensor in device["sensors"]:
            topic = base_topic.format(device=device["device_id"], sensor_type=sensor["sensor_type"])
            data = {
                "device_id": device["device_id"],
                "sensor_type": sensor["sensor_type"],
                "location": device["location"],
                "value": generate_reading(device, sensor["sensor_type"]),
                "unit": sensor["unit"],
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
            message = json.dumps(data)
            result = client.publish(topic, message)
            if result[0] == 0:
                print(f"Published to {topic}: {message}")
            else:
                print(f"Failed to publish to {topic}")
        time.sleep(5)  # Adjust the broadcast frequency as needed

# Function to handle received messages
def on_message(client, userdata, msg):
    print(f"Received message from {msg.topic}: {msg.payload.decode()}")

# Function to subscribe to wildcard topic
def subscribe_to_all():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port, 60)
    client.subscribe(subscribe_topic)
    client.loop_forever()

if __name__ == "__main__":
    # Start a thread for each device simulator
    for device in devices:
        threading.Thread(target=broadcast_device, args=(device,), daemon=True).start()

    # Start the subscriber in the main thread
    subscribe_to_all()