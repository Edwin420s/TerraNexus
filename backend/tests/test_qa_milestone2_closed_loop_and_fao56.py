"""
Test Suite for Milestone 2 & 3:
1. Dynamic FAO-56 Soil Physics Modeling (Allen et al. 1998)
2. Closed-Loop Irrigation Automation with 15s Dry-Run Interlock
3. Idempotent Event Log Synchronization & Domain Conflict Policies
4. Kirinyaga County Tomato Pilot & Water Productivity Economics
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.agronomic_engine import (
    calculate_dynamic_fao56,
    AgronomicAssessmentRequest,
    SOIL_TEXTURE_PROFILES,
    CROP_PHENOLOGY_PROFILES
)

client = TestClient(app)

# ----------------- 1. Dynamic FAO-56 Soil Physics Modeling -----------------

def test_tc_agro_001_soil_texture_hydraulic_limits():
    """Verify soil hydraulic properties (PWP, FC, SAT, Infiltration) across textures."""
    assert "clay_loam" in SOIL_TEXTURE_PROFILES
    assert "sand" in SOIL_TEXTURE_PROFILES
    assert "loam" in SOIL_TEXTURE_PROFILES

    sand = SOIL_TEXTURE_PROFILES["sand"]
    clay = SOIL_TEXTURE_PROFILES["clay"]

    # Sand has lower FC and higher infiltration than Clay
    assert sand["fc_pct"] < clay["fc_pct"]
    assert sand["infiltration_rate_mm_hr"] > clay["infiltration_rate_mm_hr"]
    assert sand["fc_pct"] > sand["pwp_pct"]

def test_tc_agro_002_dynamic_taw_raw_calculations():
    """Verify TAW and RAW calculation for tomato in mid-season on clay loam."""
    req = AgronomicAssessmentRequest(
        crop="tomato",
        growth_stage="mid_season",
        soil_texture="clay_loam",
        single_moisture_pct=16.2,  # Close to PWP (16.0%) -> Deficit
        field_area_m2=1000.0,
        irrigation_efficiency=0.90,
        system_flow_rate_lpm=45.0
    )
    result = calculate_dynamic_fao56(req)
    
    assert result.execution_mode == "rule_based_fao56"
    assert result.pwp_pct == 18.0
    assert result.fc_pct == 34.0
    assert result.taw_mm > 0.0
    assert result.raw_mm > 0.0
    assert result.raw_mm < result.taw_mm
    assert result.irrigation_needed is True
    assert result.status_label == "DEFICIT_TRIGGERED"
    assert result.gross_water_volume_litres > 0.0
    assert result.recommended_duration_minutes > 0
    assert "DEFICIT_TRIGGERED" in result.explainable_reasoning

def test_tc_agro_003_optimal_moisture_withholds_irrigation():
    """Verify that moisture above RAW thresholds withholds irrigation to preserve root oxygenation."""
    req = AgronomicAssessmentRequest(
        crop="tomato",
        growth_stage="mid_season",
        soil_texture="clay_loam",
        single_moisture_pct=28.5,  # Close to Field Capacity (32%) -> Optimal
        field_area_m2=1000.0
    )
    result = calculate_dynamic_fao56(req)

    assert result.irrigation_needed is False
    assert result.status_label == "OPTIMAL_MOISTURE"
    assert result.gross_water_volume_litres == 0.0
    assert result.recommended_duration_minutes == 0
    assert "Withhold irrigation" in result.explainable_reasoning

def test_tc_agro_004_api_endpoint_assessment():
    """Verify POST /api/v1/intelligence/agronomic-assessment API endpoint."""
    payload = {
        "crop": "tomato",
        "growth_stage": "mid_season",
        "soil_texture": "clay_loam",
        "single_moisture_pct": 16.2,
        "field_area_m2": 2500.0,
        "irrigation_efficiency": 0.90,
        "system_flow_rate_lpm": 50.0
    }
    resp = client.post("/api/v1/intelligence/agronomic-assessment", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status_label"] == "DEFICIT_TRIGGERED"
    assert data["gross_water_volume_litres"] > 0
    assert data["taw_mm"] > 0
    assert data["raw_mm"] > 0

def test_tc_agro_005_fallback_flagging():
    """Verify unknown crop or soil texture is explicitly flagged as fallback applied and recommendation safely halted."""
    req = AgronomicAssessmentRequest(
        crop="unknown_exotic_crop",
        growth_stage="blooming",
        soil_texture="moon_dust",
        single_moisture_pct=20.0
    )
    result = calculate_dynamic_fao56(req)
    assert result.fallback_applied is True
    assert result.status_label in ("UNSUPPORTED_CROP", "UNSUPPORTED_SOIL_TEXTURE")
    assert result.irrigation_needed is False
    assert len(result.warnings) >= 2
    assert any("moon_dust" in w for w in result.warnings)
    assert any("unknown_exotic_crop" in w for w in result.warnings)

def test_tc_agro_006_synthetic_moisture_flagging():
    """Verify missing soil readings flag synthetic unmeasured data provenance."""
    req = AgronomicAssessmentRequest(
        crop="tomato",
        growth_stage="mid_season",
        soil_texture="clay_loam"
    )
    result = calculate_dynamic_fao56(req)
    assert result.synthetic_moisture_used is True
    assert result.data_provenance == "synthetic_default_unmeasured"
    assert any("synthetic baseline" in w for w in result.warnings)

# ----------------- 2. Closed-Loop Irrigation & 15s Dry-Run Interlock -----------------

def test_tc_irr_005_closed_loop_planning():
    """Verify closed-loop irrigation plan evaluation and water source preflight."""
    # Find active zone
    zones = client.get("/api/v1/irrigation/zones").json()
    assert len(zones) > 0
    zone_id = zones[0]["id"]

    plan_payload = {
        "zone_id": zone_id,
        "crop": "tomato",
        "growth_stage": "mid_season",
        "soil_texture": "clay_loam",
        "current_moisture_pct": 16.5,
        "field_area_m2": 1500.0
    }
    resp = client.post("/api/v1/irrigation/closed-loop/plan", json=plan_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["zone_id"] == zone_id
    assert data["irrigation_needed"] is True
    assert data["target_volume_litres"] > 0
    assert data["dry_run_verification_window_sec"] == 15
    assert data["max_watchdog_cutoff_sec"] == 1800

def test_tc_irr_006_closed_loop_start_and_feedback():
    """Verify closed-loop dispatch and flow telemetry ingestion."""
    zones = client.get("/api/v1/irrigation/zones").json()
    zone_id = zones[0]["id"]

    # Start closed-loop cycle
    start_payload = {
        "zone_id": zone_id,
        "target_volume_litres": 1500.0,
        "max_duration_seconds": 1800,
        "dry_run_cutoff_sec": 15
    }
    start_resp = client.post("/api/v1/irrigation/closed-loop/start", json=start_payload)
    assert start_resp.status_code == 200
    start_data = start_resp.json()
    assert start_data["status"] == "closed_loop_dispatched"
    assert start_data["target_volume_litres"] == 1500.0
    assert start_data["dry_run_interlock_sec"] == 15
    event_id = start_data["event_id"]

    # Ingest feedback: 500L delivered at 42 LPM
    feedback_payload = {
        "zone_id": zone_id,
        "event_id": event_id,
        "current_flow_rate_lpm": 42.0,
        "delivered_volume_litres": 500.0,
        "elapsed_seconds": 720,
        "dry_run_fault": False
    }
    fb_resp = client.post("/api/v1/irrigation/closed-loop/feedback", json=feedback_payload)
    assert fb_resp.status_code == 200
    assert fb_resp.json()["status"] == "tracking"
    assert fb_resp.json()["delivered_volume_litres"] == 500.0

def test_tc_irr_007_dry_run_emergency_cutoff():
    """Verify that a 15-second dry run anomaly triggers immediate fail-closed cutoff."""
    zones = client.get("/api/v1/irrigation/zones").json()
    zone_id = zones[0]["id"]

    start_payload = {
        "zone_id": zone_id,
        "target_volume_litres": 1000.0,
        "max_duration_seconds": 1800
    }
    event_id = client.post("/api/v1/irrigation/closed-loop/start", json=start_payload).json()["event_id"]

    # Trigger dry run fault (no flow detected after 15s)
    cutoff_payload = {
        "zone_id": zone_id,
        "event_id": event_id,
        "current_flow_rate_lpm": 0.0,
        "delivered_volume_litres": 0.0,
        "elapsed_seconds": 16,
        "dry_run_fault": True
    }
    cutoff_resp = client.post("/api/v1/irrigation/closed-loop/feedback", json=cutoff_payload)
    assert cutoff_resp.status_code == 200
    data = cutoff_resp.json()
    assert data["status"] == "emergency_cutoff_enacted"
    assert data["reason"] == "DRY_RUN_PUMP_PROTECTION"
    assert data["pump_shutdown"] is True
    assert data["valve_closed"] is True

# ----------------- 3. Idempotent Event Log Sync & Conflict Handling -----------------

def test_tc_sync_008_idempotent_event_log_deduplication():
    """Verify that repeating the same mutation event does not create duplicate database records."""
    client_uuid = f"client-test-{uuid.uuid4().hex[:8]}"
    entity_id = f"obs-{uuid.uuid4().hex[:8]}"
    op_id = f"op-{uuid.uuid4().hex[:8]}"

    sync_payload = {
        "client_uuid": client_uuid,
        "app_version": "1.2.0",
        "device_model": "Android-Rugged-Tab",
        "operations": [
            {
                "operation_id": op_id,
                "operation_type": "create",
                "entity_name": "field_observation",
                "entity_id": entity_id,
                "client_timestamp": "2026-11-11T02:00:00Z",
                "payload": {
                    "field_id": "d0000000-0000-0000-0000-000000000001",
                    "observation_type": "scouting_canopy",
                    "description": "Healthy vegetative stage, zero pest presence",
                    "severity": "low"
                }
            }
        ]
    }

    # First Push: Applied
    resp1 = client.post("/api/v1/sync/push", json=sync_payload)
    assert resp1.status_code == 200
    assert resp1.json()["applied_count"] == 1
    assert resp1.json()["deduplicated_count"] == 0

    # Second Push of identical payload: Deduplicated (Idempotent)
    resp2 = client.post("/api/v1/sync/push", json=sync_payload)
    assert resp2.status_code == 200
    assert resp2.json()["deduplicated_count"] == 1
    assert resp2.json()["applied_count"] == 0

def test_tc_sync_009_versioned_observation_conflict_audit():
    """Verify that updating field observations preserves revision history via versioned_revision strategy."""
    client_uuid = f"client-test-{uuid.uuid4().hex[:8]}"
    entity_id = f"obs-{uuid.uuid4().hex[:8]}"

    # Initial creation
    client.post("/api/v1/sync/push", json={
        "client_uuid": client_uuid,
        "operations": [{
            "operation_id": f"op-1-{uuid.uuid4().hex[:6]}",
            "operation_type": "create",
            "entity_name": "field_observation",
            "entity_id": entity_id,
            "client_timestamp": "2026-11-11T01:00:00Z",
            "payload": {"description": "Initial scouting note"}
        }]
    })

    # Update: Should trigger versioned_revision conflict audit
    update_resp = client.post("/api/v1/sync/push", json={
        "client_uuid": client_uuid,
        "operations": [{
            "operation_id": f"op-2-{uuid.uuid4().hex[:6]}",
            "operation_type": "update",
            "entity_name": "field_observation",
            "entity_id": entity_id,
            "client_timestamp": "2026-11-11T02:00:00Z",
            "payload": {"description": "Updated scouting note with blossom count"}
        }]
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["conflict_count"] == 1
    assert update_resp.json()["applied_count"] == 1

# ----------------- 4. Kirinyaga County Tomato Pilot & Farm Economics -----------------

def test_tc_pilot_010_kirinyaga_tomato_metrics():
    """Verify empirical metric reporting for the 0.5-ha Kirinyaga County Tomato Pilot."""
    resp = client.get("/api/v1/operations/pilot/kirinyaga-tomato/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "Anna F1" in data["crop_variety"]
    assert "Kirinyaga" in data["location"]
    assert data["treatment_water_litres"] < data["control_water_litres"]
    assert data["treatment_yield_kg"] > data["control_yield_kg"]
    assert data["water_savings_pct"] > 30.0  # ~34.6% water conservation
    assert data["treatment_water_productivity_kg_per_l"] > data["control_water_productivity_kg_per_l"]
    assert data["production_cost_per_kg_treatment"] < data["production_cost_per_kg_control"]

def test_tc_pilot_011_water_efficiency_productivity_summary():
    """Verify farm-wide water productivity calculation connecting yield to water consumed."""
    resp = client.get("/api/v1/operations/productivity/water-efficiency")
    assert resp.status_code == 200
    data = resp.json()
    assert data["water_productivity_kg_per_l"] > 0.0
    assert data["water_intensity_litres_per_kg"] > 0.0
    assert "FAO-56" in data["measurement_standard"]
