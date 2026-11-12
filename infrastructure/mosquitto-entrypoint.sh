#!/bin/sh
set -e

# Generate authenticated password file for Mosquitto
PASS_FILE="/mosquitto/config/passwords"
mkdir -p /mosquitto/config

touch "$PASS_FILE"
chmod 0600 "$PASS_FILE"

# Provision default backend and device accounts with passwords from environment
BACKEND_PASS="${MQTT_BACKEND_PASSWORD:-tnx_backend_secure_2026}"
DEVICE_PASS="${MQTT_DEVICE_PASSWORD:-tnx_secure_field_pass_2026}"

mosquitto_passwd -b -c "$PASS_FILE" terranexus_backend "$BACKEND_PASS"
mosquitto_passwd -b "$PASS_FILE" tnx_field_gateway "$DEVICE_PASS"

# Seed default test device credentials for immediate edge simulation
mosquitto_passwd -b "$PASS_FILE" esp32-node-001 "$DEVICE_PASS" || true
mosquitto_passwd -b "$PASS_FILE" esp32-B8D61A2B3C4D "$DEVICE_PASS" || true

echo "[Mosquitto Init] Provisioned accounts: terranexus_backend, tnx_field_gateway, edge nodes"
exec /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
