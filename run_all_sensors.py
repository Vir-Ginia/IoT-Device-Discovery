import subprocess
import time

print("Restarting Mosquitto service via Homebrew...")
subprocess.run(["brew", "services", "restart", "mosquitto"])

scripts = [
    "device-simulator/udp_broadcast.py"
]

processes = []

for script in scripts:
    print(f"Starting {script}...")
    p = subprocess.Popen(["python3", script])
    processes.append(p)
    time.sleep(2)  # slight delay between launches


print("All sensor scripts are running. Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping all scripts...")
    for p in processes:
        p.terminate()
    print("All scripts terminated.")
