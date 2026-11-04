# ESP32 Integration

Initial target: the existing Nexus Group / AgriVerde ESP32-WROOM-32 setup. Before firmware implementation, verify the current board revision, exact pin map, sensor electrical characteristics, pump/relay ratings, power isolation, enclosure and calibration. Historical pin assignments must not be treated as verified wiring.

Firmware responsibilities:
- unique device identity and secure provisioning;
- sensor acquisition and local validation;
- timestamping and monotonic sequence numbers;
- persistent offline telemetry queue;
- authenticated MQTT/HTTPS transport;
- command allow-list and expiry checks;
- device-local interlocks, watchdog and emergency stop;
- command acknowledgement and execution feedback;
- safe boot and safe state on connectivity loss.

Cloud commands are requests, never proof of physical execution. The device must reject commands whenever local safety conditions are not satisfied.
