import paho.mqtt.client as mqtt
import json
import os
from io import StringIO
import csv
import xml.etree.ElementTree as ET


# MQTT configuration
broker = "localhost"
port = 1883
topics = ["+/temperature", "+/pressure"]  # Topics to subscribe to
REGISTRY_DIR = "registry"
DEVICE_REGISTRY = os.path.join(REGISTRY_DIR, "devices.json")

# Ensure registry directory exists
os.makedirs(REGISTRY_DIR, exist_ok=True)

# Ensure registry file exists
if not os.path.exists(DEVICE_REGISTRY):
    with open(DEVICE_REGISTRY, 'w') as f:
        json.dump([], f, indent=2)

# Function to load the device registry
def load_registry():
    try:
        with open(DEVICE_REGISTRY, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        print("Registry file is corrupted. Initializing empty registry.")
        return []

# Function to save the updated registry
def save_registry(registry):
    with open(DEVICE_REGISTRY, 'w') as f:
        json.dump(registry, f, indent=2)


# Function to parse XML data into JSON
def xml_to_json(xml_string):
    root = ET.fromstring(xml_string)
    def parse_element(element):
        return {element.tag: element.text or {child.tag: parse_element(child) for child in element}}
    return json.dumps(parse_element(root))

# Function to parse CSV data into JSON
def csv_to_json(csv_string):
    reader = csv.DictReader(StringIO(csv_string))
    return json.dumps([row for row in reader])

# MQTT callback when a message is received
def on_message(client, userdata, msg):
    print(f"Receiving messages on topic: {msg.topic}")

    try:
        # Decode the message payload
        message = msg.payload.decode()

        # Detect message type and parse accordingly
        if message.startswith("<") and message.endswith(">"):  # XML format
            device = json.loads(xml_to_json(message))
        elif message.startswith("{"):  # JSON format
            device = json.loads(message)
        elif "," in message:  # CSV format (basic check)
            device = json.loads(csv_to_json(message))
        else:
            print("Unsupported format. Ignoring.")
            return

        device = json.loads(message)

        # Extract essential device fields and validate
        essential_device = {
            "device_id": device.get("device_id"),
            "sensor_type": device.get("sensor_type"),
            "location": device.get("location")
        }

        if not all(essential_device.values()):
            print("Missing essential device info (device_id, sensor_type, location). Ignoring.")
            return

        # Load the existing registry and check for duplicates
        registry = load_registry()
        if not any(d["device_id"] == essential_device["device_id"] for d in registry):
            registry.append(essential_device)
            save_registry(registry)
            print(f"New device registered: {essential_device['device_id']}")
        else:
            print(f"Device already registered: {essential_device['device_id']}")

    except json.JSONDecodeError:
        print("Invalid JSON. Ignoring.")
    except Exception as e:
        print(f"Error processing message: {e}")



# Initialize MQTT client
client = mqtt.Client()

# Set up the message callback function
client.on_message = on_message

# Connect to the broker
client.connect(broker, port, 60)

# Subscribe to the topics
for topic in topics:
    client.subscribe(topic)

# Start the MQTT loop to handle incoming messages
client.loop_start()

print(f"Listening for device broadcasts on MQTT topics: {', '.join(topics)}...")

# Keep the program running to listen for messages
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")

client.loop_stop()