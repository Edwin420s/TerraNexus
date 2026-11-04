#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <FS.h>
#include <SPIFFS.h>
#include "config.h"

// Hardware Sensor Objects
DHT dht(PIN_DHT22_DATA, DHT22);
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Device State
char deviceUID[32];
char topicTelemetry[128];
char topicCommands[128];
char topicCommandAck[128];
char topicHeartbeat[128];

volatile bool emergencyStopActive = false;
bool pumpIsActive = false;
unsigned long pumpStartTime = 0;
unsigned long lastPumpStopTime = 0;
unsigned long lastTelemetryMillis = 0;
unsigned long lastHeartbeatMillis = 0;
unsigned long sequenceCounter = 0;

// Interrupt Service Routine for Emergency Stop Button
void IRAM_ATTR handleEmergencyStop() {
    emergencyStopActive = true;
    digitalWrite(PIN_RELAY_PUMP, HIGH);  // Active-LOW relay OFF
    digitalWrite(PIN_RELAY_VALVE, HIGH); // Solenoid valve CLOSED
    pumpIsActive = false;
}

void setupDeviceUID() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    snprintf(deviceUID, sizeof(deviceUID), "esp32-%02X%02X%02X%02X%02X%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    
    // Construct MQTT topics according to TNX-API-001 Section 35
    snprintf(topicTelemetry, sizeof(topicTelemetry), "tnx/a0000000/farm/c0000000/device/%s/telemetry", deviceUID);
    snprintf(topicCommands, sizeof(topicCommands), "tnx/a0000000/farm/c0000000/device/%s/commands", deviceUID);
    snprintf(topicCommandAck, sizeof(topicCommandAck), "tnx/a0000000/farm/c0000000/device/%s/commands/ack", deviceUID);
    snprintf(topicHeartbeat, sizeof(topicHeartbeat), "tnx/a0000000/farm/c0000000/device/%s/heartbeat", deviceUID);
}

float readSoilMoisture(int pin) {
    int raw = analogRead(pin);
    // Constrain and invert: high ADC = dry, low ADC = wet
    int constrained = constrain(raw, SOIL_CALIB_WATER_VALUE, SOIL_CALIB_AIR_VALUE);
    float moisture = map(constrained, SOIL_CALIB_AIR_VALUE, SOIL_CALIB_WATER_VALUE, 0, 100);
    return moisture;
}

float readBatteryVoltage() {
    int raw = analogRead(PIN_BATTERY_VOLTAGE_ADC);
    // 3.3V reference, 12-bit ADC (4095), 1:2 divider
    float voltage = (raw / 4095.0) * 3.3 * 2.0;
    return voltage;
}

void publishCommandAck(const char* commandId, const char* status, const char* errorMsg = nullptr) {
    JsonDocument doc;
    doc["command_id"] = commandId;
    doc["device_uid"] = deviceUID;
    doc["status"] = status;
    doc["timestamp"] = millis();
    if (errorMsg) {
        doc["error"] = errorMsg;
    }
    
    char buffer[256];
    serializeJson(doc, buffer);
    mqttClient.publish(topicCommandAck, buffer);
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
    char message[512];
    if (length >= sizeof(message)) return;
    memcpy(message, payload, length);
    message[length] = '\0';

    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, message);
    if (err) {
        Serial.println("JSON parse error in command");
        return;
    }

    const char* commandId = doc["command_id"] | "unknown";
    const char* action = doc["command_type"] | doc["action"] | "";

    // Device-local safety checks (Independent of cloud)
    if (emergencyStopActive) {
        publishCommandAck(commandId, "failed", "EMERGENCY_STOP_ACTIVE");
        return;
    }

    if (strcmp(action, "turn_on") == 0) {
        // Check cool-off period
        if (millis() - lastPumpStopTime < (MIN_COOLOFF_SEC * 1000) && lastPumpStopTime != 0) {
            publishCommandAck(commandId, "failed", "PUMP_COOLOFF_ACTIVE");
            return;
        }

        int durationSec = doc["payload"]["duration_sec"] | 300;
        if (durationSec <= 0 || durationSec > MAX_CONTINUOUS_RUN_SEC) {
            publishCommandAck(commandId, "failed", "RUNTIME_LIMIT_EXCEEDED");
            return;
        }

        // Engage relays safely
        digitalWrite(PIN_RELAY_VALVE, LOW); // Open valve first
        delay(200);
        digitalWrite(PIN_RELAY_PUMP, LOW);  // Start pump
        pumpIsActive = true;
        pumpStartTime = millis();

        publishCommandAck(commandId, "executing");
    } 
    else if (strcmp(action, "turn_off") == 0) {
        digitalWrite(PIN_RELAY_PUMP, HIGH); // Stop pump
        delay(200);
        digitalWrite(PIN_RELAY_VALVE, HIGH); // Close valve
        pumpIsActive = false;
        lastPumpStopTime = millis();

        publishCommandAck(commandId, "completed");
    }
    else if (strcmp(action, "reboot") == 0) {
        publishCommandAck(commandId, "acknowledged");
        delay(500);
        ESP.restart();
    }
}

void reconnectMqtt() {
    if (!mqttClient.connected()) {
        if (mqttClient.connect(deviceUID)) {
            mqttClient.subscribe(topicCommands);
            digitalWrite(PIN_STATUS_LED, HIGH);
        } else {
            digitalWrite(PIN_STATUS_LED, LOW);
        }
    }
}

void sendTelemetry() {
    float soil1 = readSoilMoisture(PIN_SOIL_MOISTURE_ADC);
    float soil2 = readSoilMoisture(PIN_SOIL_MOISTURE_ADC2);
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    float batt = readBatteryVoltage();

    // Canonical Telemetry Envelope (TNX-API-001 Section 27)
    JsonDocument doc;
    doc["event_id"] = String(deviceUID) + "-" + String(millis());
    doc["schema_version"] = "1.0";
    doc["device_id"] = deviceUID;
    doc["sequence"] = sequenceCounter++;
    doc["battery"] = batt;
    doc["pump_running"] = pumpIsActive;
    doc["emergency_stop"] = emergencyStopActive;

    JsonArray measurements = doc["measurements"].to<JsonArray>();

    JsonObject m1 = measurements.add<JsonObject>();
    m1["type"] = "soil_moisture";
    m1["value"] = soil1;
    m1["unit"] = "%";
    m1["depth_cm"] = 10.0;

    JsonObject m2 = measurements.add<JsonObject>();
    m2["type"] = "soil_moisture";
    m2["value"] = soil2;
    m2["unit"] = "%";
    m2["depth_cm"] = 30.0;

    if (!isnan(temp)) {
        JsonObject m3 = measurements.add<JsonObject>();
        m3["type"] = "ambient_temp";
        m3["value"] = temp;
        m3["unit"] = "°C";
    }

    if (!isnan(hum)) {
        JsonObject m4 = measurements.add<JsonObject>();
        m4["type"] = "relative_humidity";
        m4["value"] = hum;
        m4["unit"] = "%";
    }

    char buffer[1024];
    serializeJson(doc, buffer);

    if (mqttClient.connected()) {
        mqttClient.publish(topicTelemetry, buffer);
    } else {
        // Offline Spooling: store to flash buffer if disconnected
        File file = SPIFFS.open("/telemetry_spool.jsonl", FILE_APPEND);
        if (file) {
            file.println(buffer);
            file.close();
        }
    }
}

void setup() {
    Serial.begin(115200);
    SPIFFS.begin(true);

    // Pin Modes
    pinMode(PIN_RELAY_PUMP, OUTPUT);
    pinMode(PIN_RELAY_VALVE, OUTPUT);
    pinMode(PIN_STATUS_LED, OUTPUT);
    pinMode(PIN_EMERGENCY_STOP_BTN, INPUT_PULLUP);

    // Initial Safe State (Relays OFF)
    digitalWrite(PIN_RELAY_PUMP, HIGH);
    digitalWrite(PIN_RELAY_VALVE, HIGH);
    digitalWrite(PIN_STATUS_LED, LOW);

    // Emergency Stop Button Hardware Interrupt
    attachInterrupt(digitalPinToInterrupt(PIN_EMERGENCY_STOP_BTN), handleEmergencyStop, FALLING);

    dht.begin();
    setupDeviceUID();

    // WiFi Setup
    WiFi.begin(DEFAULT_WIFI_SSID, DEFAULT_WIFI_PASS);
    mqttClient.setServer(DEFAULT_MQTT_SERVER, DEFAULT_MQTT_PORT);
    mqttClient.setCallback(onMqttMessage);
}

void loop() {
    // 1. Hardware Safety Watchdog
    if (pumpIsActive) {
        if ((millis() - pumpStartTime) >= (MAX_CONTINUOUS_RUN_SEC * 1000UL)) {
            // Cutoff triggered by local hardware watchdog timer
            digitalWrite(PIN_RELAY_PUMP, HIGH);
            digitalWrite(PIN_RELAY_VALVE, HIGH);
            pumpIsActive = false;
            lastPumpStopTime = millis();
            publishCommandAck("watchdog_trip", "failed", "WATCHDOG_TIMEOUT_CUTOFF");
        }
    }

    // 2. Network & MQTT Maintenance
    if (WiFi.status() == WL_CONNECTED) {
        if (!mqttClient.connected()) {
            reconnectMqtt();
        } else {
            mqttClient.loop();
        }
    }

    // 3. Periodic Telemetry
    if (millis() - lastTelemetryMillis >= TELEMETRY_INTERVAL_MS) {
        lastTelemetryMillis = millis();
        sendTelemetry();
    }
}
