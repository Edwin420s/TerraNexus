#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ----------------- Pin Assignments -----------------
// Sensors
#define PIN_SOIL_MOISTURE_ADC   34  // Analog input ADC1_CH6 (Capacitive sensor 1)
#define PIN_SOIL_MOISTURE_ADC2  35  // Analog input ADC1_CH7 (Capacitive sensor 2)
#define PIN_DHT22_DATA          4   // Digital 1-wire for DHT22 Temperature/Humidity
#define PIN_BATTERY_VOLTAGE_ADC 36  // Analog input VP / ADC1_CH0 (1:2 voltage divider)

// Actuators & Relays (Active LOW optocoupled relay board)
#define PIN_RELAY_PUMP          26  // Relay Channel 1: Primary Irrigation Pump
#define PIN_RELAY_VALVE         27  // Relay Channel 2: Solenoid Drip Valve

// Physical Safety Interlocks & Indicators
#define PIN_EMERGENCY_STOP_BTN  14  // Hardware E-Stop button with internal pullup
#define PIN_STATUS_LED          2   // On-board LED indicator

// ----------------- Safety Constraints -----------------
// Absolute hardware timeout limit (in seconds) - cut off pump even if cloud drops connection
#define MAX_CONTINUOUS_RUN_SEC  1800  // 30 minutes absolute maximum
#define MIN_COOLOFF_SEC         120   // 2 minutes minimum pause between runs

// ADC Calibration values (0-4095 for ESP32 12-bit ADC)
#define SOIL_CALIB_AIR_VALUE    3200  // Sensor in dry air (0% moisture)
#define SOIL_CALIB_WATER_VALUE  1400  // Sensor in cup of water (100% moisture)

// ----------------- Network & Telemetry Defaults -----------------
#define DEFAULT_WIFI_SSID       "TerraNexus-Field-WiFi"
#define DEFAULT_WIFI_PASS       "TerraAgri2026"
#define DEFAULT_MQTT_SERVER     "192.168.1.100" // Or terranexus cloud host
#define DEFAULT_MQTT_PORT       1883

#define TELEMETRY_INTERVAL_MS   30000 // Send telemetry every 30 seconds
#define HEARTBEAT_INTERVAL_MS   15000 // Send heartbeat every 15 seconds

#define FIRMWARE_VERSION        "1.0.0"
#define HARDWARE_REVISION       "esp32-wroom-32-v1"

#endif // CONFIG_H
