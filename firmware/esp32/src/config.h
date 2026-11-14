#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ----------------- Pin Assignments -----------------
// Sensors
#define PIN_SOIL_MOISTURE_ADC   34  // Analog input ADC1_CH6 (Capacitive sensor 1 - Shallow 10cm)
#define PIN_SOIL_MOISTURE_ADC2  35  // Analog input ADC1_CH7 (Capacitive sensor 2 - Deep 30cm)
#define PIN_DHT22_DATA          4   // Digital 1-wire for DHT22 Temperature/Humidity
#define PIN_BATTERY_VOLTAGE_ADC 36  // Analog input VP / ADC1_CH0 (1:2 voltage divider)
#define PIN_FLOW_METER          13  // Digital interrupt pin for Hall-effect water pulse flow meter

// Actuators & Relays (Active LOW optocoupled relay board)
#define PIN_RELAY_PUMP          26  // Relay Channel 1: Primary Irrigation Pump
#define PIN_RELAY_VALVE         27  // Relay Channel 2: Solenoid Drip Valve

// Physical Safety Interlocks & Indicators
#define PIN_EMERGENCY_STOP_BTN  14  // Hardware E-Stop button with internal pullup
#define PIN_STATUS_LED          2   // On-board LED indicator

// ----------------- Closed-Loop & Safety Constraints -----------------
#define MAX_CONTINUOUS_RUN_SEC  1800  // 30 minutes absolute maximum watchdog cutoff
#define MIN_COOLOFF_SEC         120   // 2 minutes minimum pause between runs
#define DRY_RUN_VERIFICATION_SEC 15   // 15 seconds dry-run verification window
#define MIN_EXPECTED_FLOW_LPM   2.0f  // Minimum flow required when pump is active (prevent cavitation)
#define FLOW_PULSES_PER_LITRE   450.0f // Standard YF-S201 Hall sensor pulse constant (pulses/L)

// ADC Calibration values (0-4095 for ESP32 12-bit ADC)
#define SOIL_CALIB_AIR_VALUE    3200  // Sensor in dry air (0% moisture)
#define SOIL_CALIB_WATER_VALUE  1400  // Sensor in cup of water (100% moisture)

// ----------------- Network & Telemetry Defaults (Configurable via Build Flags or NVS) -----------------
#ifndef DEFAULT_WIFI_SSID
#define DEFAULT_WIFI_SSID       "" // Set via build flag -DDEFAULT_WIFI_SSID="..." or NVS
#endif

#ifndef DEFAULT_WIFI_PASS
#define DEFAULT_WIFI_PASS       "" // Set via build flag -DDEFAULT_WIFI_PASS="..." or NVS
#endif

#ifndef DEFAULT_MQTT_SERVER
#define DEFAULT_MQTT_SERVER     "127.0.0.1"
#endif

#ifndef DEFAULT_MQTT_PORT
#define DEFAULT_MQTT_PORT       1883
#endif

#ifndef DEFAULT_MQTT_USER
#define DEFAULT_MQTT_USER       ""
#endif

#ifndef DEFAULT_MQTT_PASS
#define DEFAULT_MQTT_PASS       ""
#endif

// Provisioned Tenancy Identifiers
#define DEFAULT_TENANT_ID       "a0000000-0000-0000-0000-000000000001"
#define DEFAULT_FARM_ID         "c0000000-0000-0000-0000-000000000001"

#define TELEMETRY_INTERVAL_MS   30000 // Send telemetry every 30 seconds
#define HEARTBEAT_INTERVAL_MS   15000 // Send heartbeat every 15 seconds

#define FIRMWARE_VERSION        "1.0.0"
#define HARDWARE_REVISION       "esp32-wroom-32-v1"

#endif // CONFIG_H
