# terranexus_client.py - MicroPython client for TerraNexus ESP32 Nodes
import time
import json
import machine
from machine import Pin, ADC

class TerraNexusNode:
    def __init__(self, device_uid="esp32-node-001", relay_pump_pin=26, relay_valve_pin=27, soil_adc_pin=34, estop_pin=14):
        self.device_uid = device_uid
        self.soil_adc = ADC(Pin(soil_adc_pin))
        self.soil_adc.atten(ADC.ATTN_11DB) # 0 - 3.6V range
        
        # Relays (Active LOW)
        self.pump_relay = Pin(relay_pump_pin, Pin.OUT, value=1)
        self.valve_relay = Pin(relay_valve_pin, Pin.OUT, value=1)
        
        self.is_running = False
        self.emergency_stop = False
        self.start_time = 0
        self.max_duration_sec = 1800 # 30 min watchdog
        
        # E-stop IRQ
        self.estop_btn = Pin(estop_pin, Pin.IN, Pin.PULL_UP)
        self.estop_btn.irq(trigger=Pin.IRQ_FALLING, handler=self._on_estop)

    def _on_estop(self, pin):
        self.emergency_stop = True
        self.stop_pump("EMERGENCY_STOP_HARDWARE_TRIGGER")

    def read_soil_moisture(self):
        raw = self.soil_adc.read()
        # Calibrate: 3200 air -> 0%, 1400 water -> 100%
        val = max(1400, min(3200, raw))
        moist_pct = ((3200 - val) / (3200 - 1400)) * 100.0
        return round(moist_pct, 1)

    def start_pump(self, duration_sec=300):
        if self.emergency_stop:
            return False, "EMERGENCY_STOP_ACTIVE"
        if duration_sec > self.max_duration_sec:
            return False, "RUNTIME_EXCEEDS_LIMIT"
        
        self.valve_relay.value(0) # Open valve
        time.sleep_ms(200)
        self.pump_relay.value(0)  # Start pump
        self.is_running = True
        self.start_time = time.time()
        return True, "EXECUTING"

    def stop_pump(self, reason="NORMAL_STOP"):
        self.pump_relay.value(1) # Cut pump
        time.sleep_ms(200)
        self.valve_relay.value(1) # Close valve
        self.is_running = False
        return True, reason

    def check_watchdog(self):
        if self.is_running:
            elapsed = time.time() - self.start_time
            if elapsed >= self.max_duration_sec:
                self.stop_pump("WATCHDOG_CUTOFF")

    def build_telemetry_payload(self):
        return {
            "device_id": self.device_uid,
            "schema_version": "1.0",
            "sequence": int(time.time()),
            "measurements": [
                {
                    "type": "soil_moisture",
                    "value": self.read_soil_moisture(),
                    "unit": "%",
                    "depth_cm": 10.0
                }
            ],
            "pump_running": self.is_running,
            "emergency_stop": self.emergency_stop
        }
