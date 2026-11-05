#!/usr/bin/env python3
"""
TerraNexus ESP32 Field Node Telemetry Simulator
Emulates an active ESP32 edge node reading soil moisture ADC, DHT22 air climate,
and battery level, publishing canonical JSON telemetry to Mosquitto MQTT broker.
"""

import sys
import os
import time
import json
import random
import uuid
from datetime import datetime, timezone

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_dir)

from app.services.mqtt_consumer import process_telemetry_message

def run_simulation(cycles=5, interval=1):
    print("=" * 60)
    print("TERRANEXUS: ESP32 EDGE NODE TELEMETRY SIMULATOR")
    print("Device: esp32-node-001 | Farm: GreenValley GV-01")
    print("=" * 60)

    device_uid = "esp32-node-001"
    topic = f"tnx/a0000000-0000-0000-0000-000000000001/farm/c0000000-0000-0000-0000-000000000001/device/{device_uid}/telemetry"

    base_moisture = 31.0
    base_temp = 24.0

    for i in range(1, cycles + 1):
        # Emulate gradual moisture evaporation
        moisture_10cm = round(base_moisture - (i * 0.3) + random.uniform(-0.1, 0.1), 1)
        moisture_30cm = round(38.5 - (i * 0.1) + random.uniform(-0.05, 0.05), 1)
        temp = round(base_temp + (i * 0.2) + random.uniform(-0.2, 0.2), 1)
        humidity = round(64.0 - (i * 0.5) + random.uniform(-0.5, 0.5), 1)
        battery = round(94.0 - (i * 0.1), 1)

        payload = {
            "event_id": f"{device_uid}-{int(time.time())}-{i}",
            "schema_version": "1.0",
            "device_id": device_uid,
            "sequence": i,
            "battery": battery,
            "pump_running": False,
            "emergency_stop": False,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "measurements": [
                {"type": "soil_moisture", "value": moisture_10cm, "unit": "%", "depth_cm": 10.0},
                {"type": "soil_moisture", "value": moisture_30cm, "unit": "%", "depth_cm": 30.0},
                {"type": "ambient_temp", "value": temp, "unit": "°C"},
                {"type": "relative_humidity", "value": humidity, "unit": "%"},
                {"type": "battery_voltage", "value": round(battery * 0.042, 2), "unit": "V"}
            ]
        }

        payload_json = json.dumps(payload)
        success = process_telemetry_message(topic, payload_json)
        status_str = "OK (Persisted)" if success else "FAILED"

        print(f" Cycle {i:02d} [{status_str}] -> Soil@10cm: {moisture_10cm}% | Temp: {temp}°C | Humidity: {humidity}% | Battery: {battery}%")
        if i < cycles:
            time.sleep(interval)

    print("=" * 60)
    print("ESP32 SIMULATION CYCLE COMPLETE.")
    print("=" * 60)

if __name__ == "__main__":
    run_simulation(cycles=3, interval=0.5)
