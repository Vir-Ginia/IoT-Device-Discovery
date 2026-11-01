# IoT Device Discovery Prototype

Python and MQTT project exploring device discovery and structured sensor messages. It simulates temperature, humidity and pressure sensors, publishes readings to a local broker and records discovered devices in a JSON registry.

## Included work

- `device-simulator/udp_broadcast.py`: MQTT publishers and a wildcard subscriber. Despite the filename, the transport used in the source is MQTT.
- `registry/discovery_listener.py`: listens on `+/temperature` and `+/pressure`, validates device metadata and registers previously unseen devices.
- `run_all_sensors.py`: macOS convenience launcher that restarts Mosquitto through Homebrew and starts the simulator.
- `requirements.txt`: Python dependencies.

The supplied source is the Python discovery prototype. Node-RED flows, an InfluxDB configuration and an ontology file were not included in this archive.

## Run locally

Start a local Mosquitto broker on port 1883. Install the Python dependencies, then use two terminals from this repository root:

```bash
python -m pip install -r requirements.txt
python registry/discovery_listener.py
```

```bash
python device-simulator/udp_broadcast.py
```

An optional `WEATHER_API_KEY` environment variable enables live weather readings. With no key, the API device uses a 20 Celsius demonstration reading. `WEATHER_LOCATION` defaults to London. See `.env.example`; export the values in your shell, since the simulator does not load that file automatically.

## Message fields

Messages contain `device_id`, `sensor_type`, `location`, `value`, `unit` and `timestamp`. The listener creates `registry/devices.json` locally and keeps device identifiers unique.

## Implementation notes

The public copy removes the embedded weather-service key, adds a request timeout and a demonstration fallback, and includes the missing `requests` dependency. The supplied listener includes CSV/XML parsing helpers but subsequently reparses the raw payload as JSON, so the demonstrated end-to-end path is JSON. MQTT callbacks retain the original implementation.

Source syntax was checked for this portfolio upload. Live broker and weather-service integration were not exercised here.

Virginia Eduwa — academic project.
