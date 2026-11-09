import pytest
import time

class ESP32EdgeSimulator:
    """Emulates ESP32 C++ firmware runtime logic (TNX-FIRM-001)."""

    def __init__(self, air_cal=3200, water_cal=1400, max_watchdog_sec=1800):
        self.air_cal = air_cal
        self.water_cal = water_cal
        self.max_watchdog_sec = max_watchdog_sec
        self.watchdog_timer = 0
        self.relay_state = False  # active-LOW: False = DE-ENERGIZED (CLOSED)
        self.emergency_latched = False
        self.spool_buffer = []
        self.max_spool_records = 500

    def convert_adc_to_moisture_pct(self, raw_adc: int) -> float:
        """Converts raw ADC value (12-bit 0-4095) to calibrated moisture percentage."""
        # Active capacitive sensor: lower ADC = wetter soil, higher ADC = dry soil
        clamped = max(min(raw_adc, self.air_cal), self.water_cal)
        pct = (self.air_cal - clamped) / (self.air_cal - self.water_cal) * 100.0
        return round(pct, 2)

    def trigger_emergency_stop_isr(self):
        """Simulates GPIO 14 hardware interrupt service routine."""
        self.emergency_latched = True
        self.relay_state = False  # Instant hardware cutoff
        self.watchdog_timer = 0

    def start_actuation(self, requested_duration_sec: int) -> bool:
        """Starts actuation if safety preflights pass."""
        if self.emergency_latched:
            return False
        if requested_duration_sec > self.max_watchdog_sec:
            return False
        self.relay_state = True
        self.watchdog_timer = requested_duration_sec
        return True

    def tick_watchdog(self, elapsed_sec: int):
        """Ticks the hardware watchdog countdown."""
        if self.relay_state:
            self.watchdog_timer -= elapsed_sec
            if self.watchdog_timer <= 0:
                self.relay_state = False  # Watchdog cutoff
                self.watchdog_timer = 0

    def spool_telemetry(self, packet: dict) -> bool:
        """Spools reading to circular flash memory if network is down."""
        if len(self.spool_buffer) >= self.max_spool_records:
            self.spool_buffer.pop(0)  # FIFO discard oldest
        self.spool_buffer.append(packet)
        return True

def test_tc_edge_001_adc_calibration_curve():
    """Verify 12-bit ADC to volumetric moisture conversion."""
    sim = ESP32EdgeSimulator(air_cal=3200, water_cal=1400)
    # Air reading (bone dry) -> 0%
    assert sim.convert_adc_to_moisture_pct(3200) == 0.0
    # Water reading (saturated) -> 100%
    assert sim.convert_adc_to_moisture_pct(1400) == 100.0
    # Mid-range reading (~2300) -> 50%
    mid_pct = sim.convert_adc_to_moisture_pct(2300)
    assert 48.0 <= mid_pct <= 52.0
    # Out of bounds clamping
    assert sim.convert_adc_to_moisture_pct(3500) == 0.0
    assert sim.convert_adc_to_moisture_pct(1000) == 100.0

def test_tc_edge_002_hardware_watchdog_countdown():
    """Verify hardware watchdog automatically trips and de-energizes relay."""
    sim = ESP32EdgeSimulator(max_watchdog_sec=1800)
    # Rejects over-duration command
    assert sim.start_actuation(3600) is False
    assert sim.relay_state is False

    # Accepts valid command (600s)
    assert sim.start_actuation(600) is True
    assert sim.relay_state is True

    # Tick 300s -> still running
    sim.tick_watchdog(300)
    assert sim.relay_state is True
    assert sim.watchdog_timer == 300

    # Tick remaining 300s -> trips and shuts off
    sim.tick_watchdog(300)
    assert sim.relay_state is False
    assert sim.watchdog_timer == 0

def test_tc_edge_003_emergency_stop_isr():
    """Verify hardwired GPIO 14 interrupt immediately cuts off relay."""
    sim = ESP32EdgeSimulator()
    sim.start_actuation(600)
    assert sim.relay_state is True

    # Fire emergency interrupt
    sim.trigger_emergency_stop_isr()
    assert sim.relay_state is False
    assert sim.emergency_latched is True

    # Subsequent actuation rejected
    assert sim.start_actuation(300) is False

def test_tc_edge_004_circular_flash_spooling():
    """Verify circular flash spooling preserves memory limits under prolonged offline mode."""
    sim = ESP32EdgeSimulator()
    sim.max_spool_records = 5  # Mini buffer for test

    for i in range(10):
        sim.spool_telemetry({"seq": i, "moisture": 30.0 + i})

    assert len(sim.spool_buffer) == 5
    # Should contain records 5..9
    assert sim.spool_buffer[0]["seq"] == 5
    assert sim.spool_buffer[-1]["seq"] == 9
