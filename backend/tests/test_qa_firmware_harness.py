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
        self.button_physically_held = False
        self.last_command_sequence = 0
        self.spool_buffer = []
        self.max_spool_records = 500

    def convert_adc_to_moisture_pct(self, raw_adc: int) -> float:
        """Converts raw ADC value (12-bit 0-4095) to calibrated moisture percentage."""
        # Active capacitive sensor: lower ADC = wetter soil, higher ADC = dry soil
        clamped = max(min(raw_adc, self.air_cal), self.water_cal)
        pct = (self.air_cal - clamped) / (self.air_cal - self.water_cal) * 100.0
        return round(pct, 2)

    def trigger_emergency_stop_isr(self, physically_held: bool = True):
        """Simulates GPIO 14 hardware interrupt service routine."""
        self.emergency_latched = True
        self.button_physically_held = physically_held
        self.relay_state = False  # Instant hardware cutoff
        self.watchdog_timer = 0

    def reset_emergency_stop(self):
        """Verifies physical button is released before clearing latch."""
        if self.button_physically_held:
            return False, "BUTTON_PHYSICALLY_HELD_DOWN"
        self.emergency_latched = False
        return True, "EMERGENCY_STOP_SAFELY_RESET"

    def process_command(self, cmd: dict):
        """Processes incoming hardware commands with replay protection."""
        seq = cmd.get("sequence", 0)
        if seq > 0:
            if seq <= self.last_command_sequence:
                return False, "REPLAY_DETECTED_SEQUENCE_STALE"
            self.last_command_sequence = seq

        action = cmd.get("command_type") or cmd.get("action", "")
        if action == "reset_emergency_stop":
            return self.reset_emergency_stop()

        if self.emergency_latched:
            return False, "EMERGENCY_STOP_ACTIVE"

        if action in ("turn_on", "start_irrigation", "start_closed_loop"):
            payload = cmd.get("payload") or {}
            duration = (
                payload.get("duration_seconds")
                or payload.get("max_duration_seconds")
                or cmd.get("max_duration_seconds")
                or cmd.get("duration_sec", 300)
            )
            if duration > self.max_watchdog_sec or duration <= 0:
                return False, "RUNTIME_LIMIT_EXCEEDED"
            self.relay_state = True
            self.watchdog_timer = duration
            return True, "closed_loop_executing" if action == "start_closed_loop" else "executing"
            return True, "executing"
        elif action in ("turn_off", "stop_irrigation"):
            self.relay_state = False
            self.watchdog_timer = 0
            return True, "completed"
        return False, "UNKNOWN_COMMAND_TYPE"

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

def test_tc_edge_005_emergency_stop_physical_reset_and_replay_protection():
    """Verify physical button release requirement and command sequence replay protection."""
    sim = ESP32EdgeSimulator()

    # 1. Trigger E-stop with button physically held down
    sim.trigger_emergency_stop_isr(physically_held=True)
    assert sim.emergency_latched is True

    # Remote reset attempt while button is physically held down must fail
    success, reason = sim.reset_emergency_stop()
    assert success is False
    assert reason == "BUTTON_PHYSICALLY_HELD_DOWN"
    assert sim.emergency_latched is True

    # Release physical button and reset again
    sim.button_physically_held = False
    success, reason = sim.reset_emergency_stop()
    assert success is True
    assert reason == "EMERGENCY_STOP_SAFELY_RESET"
    assert sim.emergency_latched is False

    # 2. Command Sequence Replay Protection
    # Valid initial command (seq=10)
    ok, status = sim.process_command({"action": "turn_on", "sequence": 10, "duration_sec": 60})
    assert ok is True
    assert status == "executing"

    # Replay attack with same sequence (seq=10) must be rejected
    ok2, status2 = sim.process_command({"action": "turn_on", "sequence": 10, "duration_sec": 60})
    assert ok2 is False
    assert status2 == "REPLAY_DETECTED_SEQUENCE_STALE"

    # Older sequence (seq=5) must be rejected
    ok3, status3 = sim.process_command({"action": "turn_on", "sequence": 5, "duration_sec": 60})
    assert ok3 is False
    assert status3 == "REPLAY_DETECTED_SEQUENCE_STALE"

    # Monotonically higher sequence (seq=11) must be accepted
    ok4, status4 = sim.process_command({"action": "turn_off", "sequence": 11})
    assert ok4 is True
    assert status4 == "completed"

def test_tc_edge_006_canonical_command_schema_and_duration_contracts():
    """Verify canonical command schema contract, duration fields, and sequence tracking."""
    sim = ESP32EdgeSimulator(max_watchdog_sec=1800)

    canonical_cmd = {
        "schema_version": "1.0",
        "command_id": "cmd-test-1234",
        "sequence": 42,
        "device_id": "esp32-node-01",
        "command_type": "start_closed_loop",
        "payload": {
            "target_volume_litres": 1200.0,
            "max_duration_seconds": 900
        },
        "max_duration_seconds": 900,
        "dispatched_at": "2026-11-12T00:00:00Z",
        "expires_at": "2026-11-12T00:16:00Z"
    }

    ok, status = sim.process_command(canonical_cmd)
    assert ok is True
    assert status == "closed_loop_executing"
    assert sim.relay_state is True
    assert sim.watchdog_timer == 900
    assert sim.last_command_sequence == 42

    # Reject duration exceeding hardware watchdog limit (1800s)
    violating_cmd = {
        "schema_version": "1.0",
        "command_id": "cmd-test-1235",
        "sequence": 43,
        "device_id": "esp32-node-01",
        "command_type": "start_irrigation",
        "payload": {"duration_seconds": 3600},
        "max_duration_seconds": 3600
    }
    v_ok, v_status = sim.process_command(violating_cmd)
    assert v_ok is False
    assert v_status == "RUNTIME_LIMIT_EXCEEDED"


