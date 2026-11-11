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
char tenantId[64] = DEFAULT_TENANT_ID;
char farmId[64] = DEFAULT_FARM_ID;
char mqttUser[64] = DEFAULT_MQTT_USER;
char mqttPass[64] = DEFAULT_MQTT_PASS;
char topicTelemetry[128];
char topicCommands[128];
char topicCommandAck[128];
char topicHeartbeat[128];

volatile bool emergencyStopActive = false;
bool pumpIsActive = false;
unsigned long pumpStartTime = 0;
unsigned long lastPumpStopTime = 0;
unsigned long commandDurationMillis = MAX_CONTINUOUS_RUN_SEC * 1000UL;
unsigned long lastTelemetryMillis = 0;
unsigned long lastHeartbeatMillis = 0;
unsigned long sequenceCounter = 0;
unsigned long lastCommandSequence = 0;

// Closed-Loop Flow & Dry-Run Safety State
volatile unsigned long flowPulseCount = 0;
bool closedLoopActive = false;
float targetVolumeLitres = 0.0f;
float deliveredVolumeLitres = 0.0f;
unsigned long lastFlowCheckMillis = 0;
unsigned long flowPulsesAtLastCheck = 0;
float currentFlowRateLPM = 0.0f;
bool dryRunFaultActive = false;

// Interrupt Service Routine for Water Flow Pulse Counter
void IRAM_ATTR handleFlowPulse() {
    flowPulseCount++;
}

// Interrupt Service Routine for Emergency Stop Button
void IRAM_ATTR handleEmergencyStop() {
    emergencyStopActive = true;
    digitalWrite(PIN_RELAY_PUMP, HIGH);  // Active-LOW relay OFF
    digitalWrite(PIN_RELAY_VALVE, HIGH); // Solenoid valve CLOSED
    pumpIsActive = false;
    closedLoopActive = false;
}

void loadProvisioningConfig() {
    if (SPIFFS.exists("/provisioning.json")) {
        File file = SPIFFS.open("/provisioning.json", "r");
        if (file) {
            JsonDocument pDoc;
            if (!deserializeJson(pDoc, file)) {
                if (pDoc["organisation_id"].is<const char*>()) {
                    strncpy(tenantId, pDoc["organisation_id"].as<const char*>(), sizeof(tenantId) - 1);
                }
                if (pDoc["farm_id"].is<const char*>()) {
                    strncpy(farmId, pDoc["farm_id"].as<const char*>(), sizeof(farmId) - 1);
                }
                if (pDoc["mqtt_user"].is<const char*>()) {
                    strncpy(mqttUser, pDoc["mqtt_user"].as<const char*>(), sizeof(mqttUser) - 1);
                }
                if (pDoc["mqtt_pass"].is<const char*>()) {
                    strncpy(mqttPass, pDoc["mqtt_pass"].as<const char*>(), sizeof(mqttPass) - 1);
                }
            }
            file.close();
        }
    }
}

void setupDeviceUID() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    snprintf(deviceUID, sizeof(deviceUID), "esp32-%02X%02X%02X%02X%02X%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    
    // Construct MQTT topics derived dynamically from tenant & farm provisioning
    snprintf(topicTelemetry, sizeof(topicTelemetry), "tnx/%s/farm/%s/device/%s/telemetry", tenantId, farmId, deviceUID);
    snprintf(topicCommands, sizeof(topicCommands), "tnx/%s/farm/%s/device/%s/commands", tenantId, farmId, deviceUID);
    snprintf(topicCommandAck, sizeof(topicCommandAck), "tnx/%s/farm/%s/device/%s/commands/ack", tenantId, farmId, deviceUID);
    snprintf(topicHeartbeat, sizeof(topicHeartbeat), "tnx/%s/farm/%s/device/%s/heartbeat", tenantId, farmId, deviceUID);
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

    // Command Replay Protection (Strict monotonic sequence counter)
    if (doc["sequence"].is<unsigned long>()) {
        unsigned long cmdSeq = doc["sequence"].as<unsigned long>();
        if (cmdSeq > 0) {
            if (cmdSeq <= lastCommandSequence) {
                publishCommandAck(commandId, "failed", "REPLAY_DETECTED_SEQUENCE_STALE");
                return;
            }
            lastCommandSequence = cmdSeq;
        }
    }

    // Handle Reset of Emergency Stop with Physical Verification
    if (strcmp(action, "reset_emergency_stop") == 0) {
        // Physical interlock: Emergency stop button must be physically released (HIGH with pullup)
        if (digitalRead(PIN_EMERGENCY_STOP_BTN) == LOW) {
            publishCommandAck(commandId, "failed", "BUTTON_PHYSICALLY_HELD_DOWN");
            return;
        }
        emergencyStopActive = false;
        dryRunFaultActive = false;
        publishCommandAck(commandId, "completed", "EMERGENCY_STOP_SAFELY_RESET");
        return;
    }

    // Device-local safety checks (Independent of cloud)
    if (emergencyStopActive) {
        publishCommandAck(commandId, "failed", "EMERGENCY_STOP_ACTIVE");
        return;
    }

    if (strcmp(action, "start_closed_loop") == 0) {
        if (millis() - lastPumpStopTime < (MIN_COOLOFF_SEC * 1000) && lastPumpStopTime != 0) {
            publishCommandAck(commandId, "failed", "PUMP_COOLOFF_ACTIVE");
            return;
        }

        float targetLitres = doc["payload"]["target_volume_litres"] | 1000.0f;
        if (targetLitres <= 0.0f || targetLitres > 50000.0f) {
            publishCommandAck(commandId, "failed", "INVALID_TARGET_VOLUME_RANGE");
            return;
        }
        int maxDurationSec = doc["payload"]["max_duration_sec"] | MAX_CONTINUOUS_RUN_SEC;
        if (maxDurationSec > MAX_CONTINUOUS_RUN_SEC) maxDurationSec = MAX_CONTINUOUS_RUN_SEC;
        if (maxDurationSec <= 0) maxDurationSec = MAX_CONTINUOUS_RUN_SEC;

        commandDurationMillis = (unsigned long)maxDurationSec * 1000UL;
        targetVolumeLitres = targetLitres;
        deliveredVolumeLitres = 0.0f;
        flowPulseCount = 0;
        flowPulsesAtLastCheck = 0;
        lastFlowCheckMillis = millis();
        dryRunFaultActive = false;
        closedLoopActive = true;

        // Engage valve first, then pump
        digitalWrite(PIN_RELAY_VALVE, LOW);
        delay(200);
        digitalWrite(PIN_RELAY_PUMP, LOW);
        pumpIsActive = true;
        pumpStartTime = millis();

        publishCommandAck(commandId, "closed_loop_executing");
    }
    else if (strcmp(action, "start_irrigation") == 0 || strcmp(action, "turn_on") == 0) {
        // Check cool-off period
        if (millis() - lastPumpStopTime < (MIN_COOLOFF_SEC * 1000) && lastPumpStopTime != 0) {
            publishCommandAck(commandId, "failed", "PUMP_COOLOFF_ACTIVE");
            return;
        }

        int durationSec = doc["payload"]["duration_seconds"] | doc["payload"]["duration_sec"] | 300;
        if (durationSec <= 0 || durationSec > MAX_CONTINUOUS_RUN_SEC) {
            publishCommandAck(commandId, "failed", "RUNTIME_LIMIT_EXCEEDED");
            return;
        }

        commandDurationMillis = (unsigned long)durationSec * 1000UL;

        // Engage relays safely: open valve first, then start pump
        digitalWrite(PIN_RELAY_VALVE, LOW);
        delay(200);
        digitalWrite(PIN_RELAY_PUMP, LOW);
        pumpIsActive = true;
        pumpStartTime = millis();

        publishCommandAck(commandId, "executing");
    } 
    else if (strcmp(action, "stop_irrigation") == 0 || strcmp(action, "turn_off") == 0) {
        digitalWrite(PIN_RELAY_PUMP, HIGH); // Stop pump
        delay(200);
        digitalWrite(PIN_RELAY_VALVE, HIGH); // Close valve
        pumpIsActive = false;
        closedLoopActive = false;
        lastPumpStopTime = millis();

        publishCommandAck(commandId, "completed");
    }
    else if (strcmp(action, "reboot") == 0) {
        publishCommandAck(commandId, "acknowledged");
        delay(500);
        ESP.restart();
    }
    else {
        publishCommandAck(commandId, "failed", "UNKNOWN_COMMAND_TYPE");
    }
}

void reconnectMqtt() {
    if (!mqttClient.connected()) {
        bool connected = false;
        if (strlen(mqttUser) > 0) {
            connected = mqttClient.connect(deviceUID, mqttUser, mqttPass);
        } else {
            connected = mqttClient.connect(deviceUID);
        }
        if (connected) {
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

    // Closed-Loop Flow Measurements
    JsonObject m5 = measurements.add<JsonObject>();
    m5["type"] = "water_flow_rate";
    m5["value"] = currentFlowRateLPM;
    m5["unit"] = "LPM";

    JsonObject m6 = measurements.add<JsonObject>();
    m6["type"] = "cumulative_volume";
    m6["value"] = deliveredVolumeLitres;
    m6["unit"] = "L";

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
    pinMode(PIN_FLOW_METER, INPUT_PULLUP);

    // Initial Safe State (Relays OFF)
    digitalWrite(PIN_RELAY_PUMP, HIGH);
    digitalWrite(PIN_RELAY_VALVE, HIGH);
    digitalWrite(PIN_STATUS_LED, LOW);

    // Emergency Stop Button Hardware Interrupt
    attachInterrupt(digitalPinToInterrupt(PIN_EMERGENCY_STOP_BTN), handleEmergencyStop, FALLING);

    // Flow Meter Hall Effect Pulse Interrupt
    attachInterrupt(digitalPinToInterrupt(PIN_FLOW_METER), handleFlowPulse, RISING);

    dht.begin();
    loadProvisioningConfig();
    setupDeviceUID();

    // WiFi Setup
    WiFi.begin(DEFAULT_WIFI_SSID, DEFAULT_WIFI_PASS);
    mqttClient.setServer(DEFAULT_MQTT_SERVER, DEFAULT_MQTT_PORT);
    mqttClient.setCallback(onMqttMessage);
}

void loop() {
    unsigned long now = millis();

    // 0. Calculate Real-Time Water Flow (every 1 second)
    if (now - lastFlowCheckMillis >= 1000UL) {
        unsigned long elapsedMs = now - lastFlowCheckMillis;
        unsigned long currentPulses = flowPulseCount;
        unsigned long deltaPulses = currentPulses - flowPulsesAtLastCheck;
        flowPulsesAtLastCheck = currentPulses;
        lastFlowCheckMillis = now;

        // Pulses to volume (Litres) and flow rate (Litres / min)
        float deltaLitres = deltaPulses / FLOW_PULSES_PER_LITRE;
        deliveredVolumeLitres += deltaLitres;
        currentFlowRateLPM = (deltaLitres / (elapsedMs / 1000.0f)) * 60.0f;

        // 15-Second Dry-Run Interlock: Check flow when pump active
        if (pumpIsActive && (now - pumpStartTime >= (DRY_RUN_VERIFICATION_SEC * 1000UL))) {
            if (currentFlowRateLPM < MIN_EXPECTED_FLOW_LPM && !dryRunFaultActive) {
                // Emergency Dry-Run Cutoff: Protect pump from cavitation / dry well
                digitalWrite(PIN_RELAY_PUMP, HIGH);
                digitalWrite(PIN_RELAY_VALVE, HIGH);
                pumpIsActive = false;
                closedLoopActive = false;
                dryRunFaultActive = true;
                lastPumpStopTime = now;
                publishCommandAck("dry_run_cutoff", "failed", "PUMP_DRY_RUN_DETECTED_NO_FLOW");
            }
        }

        // Closed-Loop Volume Cutoff: Check if target litres reached
        if (closedLoopActive && pumpIsActive) {
            if (deliveredVolumeLitres >= targetVolumeLitres) {
                digitalWrite(PIN_RELAY_PUMP, HIGH);
                delay(200);
                digitalWrite(PIN_RELAY_VALVE, HIGH);
                pumpIsActive = false;
                closedLoopActive = false;
                lastPumpStopTime = now;
                publishCommandAck("closed_loop_target", "completed", "TARGET_VOLUME_DELIVERED");
            }
        }
    }

    // 1. Hardware Safety Watchdog & Command Duration Enforcement
    if (pumpIsActive) {
        if ((now - pumpStartTime) >= commandDurationMillis || (now - pumpStartTime) >= (MAX_CONTINUOUS_RUN_SEC * 1000UL)) {
            // Cutoff triggered by command deadline or maximum hardware watchdog
            digitalWrite(PIN_RELAY_PUMP, HIGH);
            digitalWrite(PIN_RELAY_VALVE, HIGH);
            pumpIsActive = false;
            closedLoopActive = false;
            lastPumpStopTime = now;
            publishCommandAck("duration_watchdog_trip", "completed", "COMMAND_DURATION_OR_WATCHDOG_LIMIT_REACHED");
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
    if (now - lastTelemetryMillis >= TELEMETRY_INTERVAL_MS) {
        lastTelemetryMillis = now;
        sendTelemetry();
    }
}
