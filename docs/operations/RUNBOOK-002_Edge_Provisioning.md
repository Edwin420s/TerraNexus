# RUNBOOK-002: Edge Node Provisioning

1. Connect ESP32 to USB-C programmer.
2. Flash platformio binary.
3. Calibrate ADC channel 0 and 1.
4. Register device via `POST /api/v1/devices`.
5. Secure MQTT client credentials in SPIFFS.
