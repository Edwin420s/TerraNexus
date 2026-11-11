"""
TerraNexus Dynamic FAO-56 Agronomic Decision Engine (TNX-AGRO-001)
Implements dynamic soil-water balance continuum calculations based on
FAO Irrigation and Drainage Paper No. 56 (Allen et al., 1998).

Calculates:
- Dynamic Total Available Water (TAW)
- Readily Available Water (RAW) with ETc adjustment
- Multi-depth Root Zone Depletion (Dr)
- Water Stress Coefficient (Ks)
- Gross Irrigation Volume (Litres) and Run Duration (Minutes)
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# ----------------- Soil Hydraulic Property Database -----------------
# Volumetric water content percentages at Field Capacity and Permanent Wilting Point
SOIL_TEXTURE_PROFILES: Dict[str, Dict[str, Any]] = {
    "sand": {
        "name": "Coarse Sand",
        "fc_pct": 10.0,
        "pwp_pct": 4.0,
        "sat_pct": 38.0,
        "bulk_density_g_cm3": 1.60,
        "infiltration_rate_mm_hr": 45.0
    },
    "loamy_sand": {
        "name": "Loamy Sand",
        "fc_pct": 14.0,
        "pwp_pct": 6.0,
        "sat_pct": 40.0,
        "bulk_density_g_cm3": 1.55,
        "infiltration_rate_mm_hr": 30.0
    },
    "sandy_loam": {
        "name": "Sandy Loam",
        "fc_pct": 20.0,
        "pwp_pct": 9.0,
        "sat_pct": 43.0,
        "bulk_density_g_cm3": 1.50,
        "infiltration_rate_mm_hr": 20.0
    },
    "loam": {
        "name": "Medium Loam",
        "fc_pct": 27.0,
        "pwp_pct": 12.0,
        "sat_pct": 46.0,
        "bulk_density_g_cm3": 1.40,
        "infiltration_rate_mm_hr": 15.0
    },
    "silt_loam": {
        "name": "Silt Loam",
        "fc_pct": 30.0,
        "pwp_pct": 14.0,
        "sat_pct": 48.0,
        "bulk_density_g_cm3": 1.35,
        "infiltration_rate_mm_hr": 10.0
    },
    "clay_loam": {
        "name": "Clay Loam",
        "fc_pct": 32.0,
        "pwp_pct": 16.0,
        "sat_pct": 50.0,
        "bulk_density_g_cm3": 1.30,
        "infiltration_rate_mm_hr": 8.0
    },
    "clay": {
        "name": "Heavy Clay / Vertisol",
        "fc_pct": 38.0,
        "pwp_pct": 22.0,
        "sat_pct": 53.0,
        "bulk_density_g_cm3": 1.25,
        "infiltration_rate_mm_hr": 4.0
    }
}

# ----------------- Phenological Crop Profiles -----------------
CROP_PHENOLOGY_PROFILES: Dict[str, Dict[str, Any]] = {
    "tomato": {
        "name": "Tomato (Solanum lycopersicum)",
        "stages": {
            "initial": {"duration_days": 25, "kc": 0.60, "root_depth_m": 0.25, "p_mad": 0.40},
            "development": {"duration_days": 35, "kc": 0.85, "root_depth_m": 0.45, "p_mad": 0.40},
            "mid_season": {"duration_days": 40, "kc": 1.15, "root_depth_m": 0.65, "p_mad": 0.40},
            "late_season": {"duration_days": 25, "kc": 0.80, "root_depth_m": 0.65, "p_mad": 0.50}
        },
        "default_depth_m": 0.60,
        "base_p_mad": 0.40,
        "critical_growth_phases": ["flowering", "fruit_sizing"]
    },
    "maize": {
        "name": "Maize / Corn (Zea mays)",
        "stages": {
            "initial": {"duration_days": 20, "kc": 0.40, "root_depth_m": 0.30, "p_mad": 0.55},
            "development": {"duration_days": 35, "kc": 0.80, "root_depth_m": 0.60, "p_mad": 0.55},
            "mid_season": {"duration_days": 45, "kc": 1.20, "root_depth_m": 0.90, "p_mad": 0.50},
            "late_season": {"duration_days": 30, "kc": 0.60, "root_depth_m": 0.90, "p_mad": 0.60}
        },
        "default_depth_m": 0.80,
        "base_p_mad": 0.50,
        "critical_growth_phases": ["silking", "tasseling"]
    },
    "wheat": {
        "name": "Wheat (Triticum aestivum)",
        "stages": {
            "initial": {"duration_days": 15, "kc": 0.35, "root_depth_m": 0.25, "p_mad": 0.55},
            "development": {"duration_days": 30, "kc": 0.75, "root_depth_m": 0.50, "p_mad": 0.55},
            "mid_season": {"duration_days": 50, "kc": 1.15, "root_depth_m": 0.80, "p_mad": 0.55},
            "late_season": {"duration_days": 30, "kc": 0.40, "root_depth_m": 0.80, "p_mad": 0.65}
        },
        "default_depth_m": 0.70,
        "base_p_mad": 0.55,
        "critical_growth_phases": ["tillering", "heading"]
    },
    "soybean": {
        "name": "Soybean (Glycine max)",
        "stages": {
            "initial": {"duration_days": 20, "kc": 0.40, "root_depth_m": 0.25, "p_mad": 0.50},
            "development": {"duration_days": 30, "kc": 0.75, "root_depth_m": 0.50, "p_mad": 0.50},
            "mid_season": {"duration_days": 45, "kc": 1.15, "root_depth_m": 0.65, "p_mad": 0.50},
            "late_season": {"duration_days": 25, "kc": 0.50, "root_depth_m": 0.65, "p_mad": 0.60}
        },
        "default_depth_m": 0.60,
        "base_p_mad": 0.50,
        "critical_growth_phases": ["flowering", "pod_fill"]
    }
}

class SoilSensorDepthReading(BaseModel):
    depth_cm: float
    moisture_pct: float
    weight: Optional[float] = None

class AgronomicAssessmentRequest(BaseModel):
    crop: str = "tomato"
    growth_stage: str = "mid_season"
    soil_texture: str = "clay_loam"
    soil_readings: Optional[List[SoilSensorDepthReading]] = None
    single_moisture_pct: Optional[float] = 16.2
    et0_mm_day: Optional[float] = 4.5
    field_area_m2: Optional[float] = 1000.0  # 0.1 hectare default
    irrigation_efficiency: Optional[float] = 0.90  # Drip irrigation efficiency
    system_flow_rate_lpm: Optional[float] = 45.0  # Litres per minute

class AgronomicAssessmentResult(BaseModel):
    crop_name: str
    growth_stage: str
    soil_texture_name: str
    pwp_pct: float
    fc_pct: float
    taw_mm: float
    raw_mm: float
    current_depletion_mm: float
    depletion_fraction_pct: float
    mad_threshold_pct: float
    water_stress_ks: float
    etc_mm_day: float
    irrigation_needed: bool
    status_label: str
    net_irrigation_requirement_mm: float
    gross_water_volume_litres: float
    recommended_duration_minutes: int
    explainable_reasoning: str
    execution_mode: str = "rule_based_fao56"

def calculate_dynamic_fao56(req: AgronomicAssessmentRequest) -> AgronomicAssessmentResult:
    """
    Executes complete deterministic FAO-56 soil-water continuum calculation.
    """
    # 1. Resolve soil profile
    soil_key = req.soil_texture.lower().replace(" ", "_")
    soil = SOIL_TEXTURE_PROFILES.get(soil_key, SOIL_TEXTURE_PROFILES["clay_loam"])
    
    # 2. Resolve crop phenology
    crop_key = req.crop.lower()
    crop_profile = CROP_PHENOLOGY_PROFILES.get(crop_key, CROP_PHENOLOGY_PROFILES["tomato"])
    stage_info = crop_profile["stages"].get(req.growth_stage.lower(), crop_profile["stages"]["mid_season"])
    
    root_depth_m = stage_info["root_depth_m"]
    kc = stage_info["kc"]
    base_p = stage_info["p_mad"]
    
    # 3. Calculate Crop Evapotranspiration ETc
    et0 = max(0.5, req.et0_mm_day or 4.5)
    etc_unconstrained = kc * et0
    
    # 4. Total Available Water (TAW)
    # TAW = 1000 * (FC - PWP) * Zr [mm]
    fc = soil["fc_pct"]
    pwp = soil["pwp_pct"]
    awc_volumetric_fraction = (fc - pwp) / 100.0
    taw_mm = round(1000.0 * awc_volumetric_fraction * root_depth_m, 2)
    
    # 5. Adjusted Management Allowed Depletion fraction (p)
    # FAO-56 formula: p = p_table + 0.04 * (5 - ETc)
    p_adj = max(0.15, min(0.80, base_p + 0.04 * (5.0 - etc_unconstrained)))
    raw_mm = round(p_adj * taw_mm, 2)
    
    # 6. Current Root Zone Depletion (Dr)
    if req.soil_readings and len(req.soil_readings) > 0:
        # Weighted multi-depth integration across root profile
        total_weight = sum(r.weight or 1.0 for r in req.soil_readings)
        weighted_moisture = sum(r.moisture_pct * (r.weight or 1.0) for r in req.soil_readings) / total_weight
    else:
        weighted_moisture = req.single_moisture_pct if req.single_moisture_pct is not None else 18.0

    # Ensure moisture is physically bounded
    current_moisture_clamped = max(0.0, min(soil["sat_pct"], weighted_moisture))
    available_moisture = max(0.0, current_moisture_clamped - pwp)
    depletion_fraction = max(0.0, min(1.0, 1.0 - (available_moisture / max(0.01, (fc - pwp)))))
    
    current_depletion_mm = round(depletion_fraction * taw_mm, 2)
    depletion_fraction_pct = round(depletion_fraction * 100.0, 1)
    mad_threshold_pct = round(p_adj * 100.0, 1)
    
    # 7. Water Stress Coefficient (Ks)
    # Ks = (TAW - Dr) / ((1 - p) * TAW) when Dr > RAW, else 1.0
    if current_depletion_mm > raw_mm and taw_mm > raw_mm:
        ks = round(max(0.0, min(1.0, (taw_mm - current_depletion_mm) / ((1.0 - p_adj) * taw_mm))), 3)
    else:
        ks = 1.0
        
    actual_etc = round(ks * etc_unconstrained, 2)
    
    # 8. Decision Gate: Is Dr >= RAW?
    deficit_triggered = current_depletion_mm >= raw_mm
    
    if deficit_triggered:
        status_label = "DEFICIT_TRIGGERED"
        net_irrigation_mm = current_depletion_mm
        # Gross volume (Litres) = (Net mm / 1000) * Area m2 / Efficiency * 1000 L/m3 = (Net mm * Area m2) / Efficiency
        efficiency = max(0.5, min(1.0, req.irrigation_efficiency or 0.90))
        area = max(10.0, req.field_area_m2 or 1000.0)
        gross_volume_litres = round((net_irrigation_mm * area) / efficiency, 1)
        
        flow_rate = max(5.0, req.system_flow_rate_lpm or 45.0)
        duration_minutes = min(90, max(10, int(round(gross_volume_litres / flow_rate))))
    else:
        status_label = "OPTIMAL_MOISTURE"
        net_irrigation_mm = 0.0
        gross_volume_litres = 0.0
        duration_minutes = 0

    reasoning_text = (
        f"[QVAC Agronomic Rule-Based Engine — Dynamic FAO-56 Continuum]\n"
        f"Target Crop: {crop_profile['name']} (Stage: {req.growth_stage}, Root Depth: {root_depth_m}m, Kc: {kc})\n"
        f"Soil Texture: {soil['name']} (PWP: {pwp}%, FC: {fc}%, AWC: {(fc - pwp):.1f}% vol)\n"
        f"Hydraulic Boundaries: Total Available Water (TAW) = {taw_mm} mm | Readily Available Water (RAW) = {raw_mm} mm\n"
        f"Observed Root Moisture: {weighted_moisture:.1f}% | Calculated Depletion (Dr) = {current_depletion_mm} mm ({depletion_fraction_pct}% of TAW)\n"
        f"Management Allowed Depletion Threshold: {mad_threshold_pct}% | Stress Coefficient (Ks): {ks}\n"
        f"Assessment: Status is {status_label}. "
    )
    if deficit_triggered:
        reasoning_text += (
            f"Root water deficit has exceeded allowable buffer. "
            f"Recommended closed-loop irrigation volume: {gross_volume_litres:.1f} Litres "
            f"over approximately {duration_minutes} minutes (Application efficiency: {req.irrigation_efficiency * 100:.0f}%)."
        )
    else:
        reasoning_text += (
            "Soil moisture remains safely within the readily available buffer. "
            "Withhold irrigation to protect root respiration and prevent nutrient leaching."
        )

    return AgronomicAssessmentResult(
        crop_name=crop_profile["name"],
        growth_stage=req.growth_stage,
        soil_texture_name=soil["name"],
        pwp_pct=pwp,
        fc_pct=fc,
        taw_mm=taw_mm,
        raw_mm=raw_mm,
        current_depletion_mm=current_depletion_mm,
        depletion_fraction_pct=depletion_fraction_pct,
        mad_threshold_pct=mad_threshold_pct,
        water_stress_ks=ks,
        etc_mm_day=actual_etc,
        irrigation_needed=deficit_triggered,
        status_label=status_label,
        net_irrigation_requirement_mm=net_irrigation_mm,
        gross_water_volume_litres=gross_volume_litres,
        recommended_duration_minutes=duration_minutes,
        explainable_reasoning=reasoning_text,
        execution_mode="rule_based_fao56"
    )
