# ESP32 Farm Node Pinout and Electrical Ratings

## Authoritative Hardware Pin Assignment (Production Board Revision 1.0)
- **GPIO 34 (ADC1_CH6)**: Analog input for Soil Probe 1 (Shallow 10cm capacitive sensor)
- **GPIO 35 (ADC1_CH7)**: Analog input for Soil Probe 2 (Deep 30cm capacitive sensor)
- **GPIO 36 (ADC1_CH0 / SENSOR_VP)**: Battery Voltage Divider (1:2 ratio, 0-6.6V scaled to 0-3.3V)
- **GPIO 4**: Digital 1-wire communication for DHT22 Temperature and Humidity sensor
- **GPIO 13**: Digital interrupt input for Hall-Effect Water Pulse Flow Meter (YF-S201)
- **GPIO 26**: Relay Channel 1 Actuator: Primary Irrigation Pump (Active-LOW optocoupled driver)
- **GPIO 27**: Relay Channel 2 Actuator: Solenoid Drip Valve (Active-LOW optocoupled driver)
- **GPIO 14**: Physical Emergency Stop Pushbutton (Hardware ISR with internal pull-up)
- **GPIO 2**: Onboard LED Status Indicator

## Alternate Devkit Pin Mapping (Legacy Prototype Compatibility)
- GPIO 32 / GPIO 33: Alternate ADC1 channels 4/5 for analog soil probes
- GPIO 25 / GPIO 26: Alternate relay driver outputs

