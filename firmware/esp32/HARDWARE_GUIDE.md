# TerraNexus ESP32 Hardware Integration & Safety Guide

## 1. Pin Configuration Table

| Function | ESP32 GPIO | Electrical Specs | Hardware Description |
| :--- | :--- | :--- | :--- |
| **Soil Moisture ADC 1** | GPIO 34 | Analog IN (0-3.3V) | Capacitive Soil Moisture Sensor v1.2 (10cm depth) |
| **Soil Moisture ADC 2** | GPIO 35 | Analog IN (0-3.3V) | Capacitive Soil Moisture Sensor v1.2 (30cm depth) |
| **Air Climate (DHT22)** | GPIO 4 | Digital I/O (10k pull-up) | Ambient Air Temperature & Relative Humidity |
| **Battery Level ADC** | GPIO 36 (VP) | Analog IN (0-3.3V) | 1:2 Resistor divider (100k / 100k) from 7.4V/12V |
| **Pump Relay Ch 1** | GPIO 26 | Digital OUT (Active LOW) | Optocoupled Relay driving 12V/24V pump contactor |
| **Valve Solenoid Ch 2**| GPIO 27 | Digital OUT (Active LOW) | Optocoupled Relay driving 12V DC solenoid valve |
| **Emergency Stop Btn** | GPIO 14 | Digital IN (Hardware INT) | Normally-closed industrial mushroom latching button |
| **Status LED** | GPIO 2 | Digital OUT | Onboard blue status indicator (WiFi/MQTT link) |

## 2. Physical Control Safety Interlocks
Cloud commands are requests, never absolute execution authority:
1. **Local Watchdog Timer**: A hardware timer on the ESP32 automatically cuts off the pump relay after a maximum runtime (`MAX_CONTINUOUS_RUN_SEC = 1800s`), even if WiFi or internet connectivity drops.
2. **Active LOW Fail-Safe**: Relay circuits are configured so that upon power loss, brownout, or reboot, the relay defaults to high-impedance / open circuit (pump OFF).
3. **Hardwired Emergency Stop**: GPIO 14 is tied to a hardware interrupt (falling edge). Pressing the emergency stop switch instantly kills pump and valve power directly at the microcontroller interrupt level.
4. **Valve Sequence Timing**: Solenoid valves open 200ms prior to pump motor ignition to avoid hydraulic water hammer damage to driplines.
