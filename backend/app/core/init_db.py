from sqlalchemy.orm import Session
from app.core.database import engine, Base, SessionLocal
from app.core.security import hash_password
from app.models.entities import (
    User, Organisation, Membership, Farm, Field,
    Crop, CropVariety, Device, Sensor, Measurement,
    WaterSource, Pump, IrrigationZone, Task, Equipment,
    InventoryItem, AlertRule, Alert, IntelligenceModel,
    Recommendation, RecommendationEvidence
)

def init_database():
    """Create all tables and seed standard baseline records if not existing."""
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Check if seed user exists
        admin = db.query(User).filter(User.email == "admin@terranexus.org").first()
        if not admin:
            # 1. Organisation
            org = Organisation(
                id="a0000000-0000-0000-0000-000000000001",
                name="Nexus Agri Enterprise",
                organisation_type="commercial_farm",
                status="active"
            )
            db.add(org)
            db.flush()

            # 2. Users
            admin = User(
                id="b0000000-0000-0000-0000-000000000001",
                email="admin@terranexus.org",
                password_hash=hash_password("TerraNexus2026!"),
                first_name="Admin",
                last_name="Nexus",
                display_name="TerraNexus Admin",
                preferred_language="en",
                timezone="Africa/Nairobi",
                account_status="active",
                email_verified=True
            )
            agronomist = User(
                id="b0000000-0000-0000-0000-000000000002",
                email="agronomist@terranexus.org",
                password_hash=hash_password("TerraNexus2026!"),
                first_name="Sarah",
                last_name="Kiprono",
                display_name="Sarah Kiprono (Agronomist)",
                preferred_language="en",
                timezone="Africa/Nairobi",
                account_status="active",
                email_verified=True
            )
            db.add_all([admin, agronomist])
            db.flush()

            # 3. Memberships
            m1 = Membership(
                organisation_id=org.id,
                user_id=admin.id,
                role="owner",
                status="active"
            )
            m2 = Membership(
                organisation_id=org.id,
                user_id=agronomist.id,
                role="agronomist",
                status="active"
            )
            db.add_all([m1, m2])
            db.flush()

            # 4. Farm & Fields
            farm = Farm(
                id="c0000000-0000-0000-0000-000000000001",
                organisation_id=org.id,
                name="GreenValley Demonstration Farm",
                farm_code="GV-01",
                area_hectares=45.5,
                country_code="KE",
                timezone="Africa/Nairobi",
                status="active"
            )
            db.add(farm)
            db.flush()

            f1 = Field(
                id="d0000000-0000-0000-0000-000000000001",
                organisation_id=org.id,
                farm_id=farm.id,
                name="North Plot - Maize Block",
                field_code="NP-01",
                area_hectares=12.5,
                status="active"
            )
            f2 = Field(
                id="d0000000-0000-0000-0000-000000000002",
                organisation_id=org.id,
                farm_id=farm.id,
                name="South Greenhouse - Drip Tomatoes",
                field_code="SG-02",
                area_hectares=2.0,
                status="active"
            )
            db.add_all([f1, f2])
            db.flush()

            # 5. Crops
            c1 = Crop(
                id="11111111-0000-0000-0000-000000000001",
                common_name="Maize",
                scientific_name="Zea mays",
                category="cereal",
                growing_days_min=110,
                growing_days_max=140,
                water_requirement_mm=600.0,
                optimal_ph_min=5.8,
                optimal_ph_max=7.0
            )
            c2 = Crop(
                id="11111111-0000-0000-0000-000000000002",
                common_name="Tomato",
                scientific_name="Solanum lycopersicum",
                category="vegetable",
                growing_days_min=75,
                growing_days_max=110,
                water_requirement_mm=500.0,
                optimal_ph_min=6.0,
                optimal_ph_max=6.8
            )
            db.add_all([c1, c2])
            db.flush()

            # 6. Water Source, Pump & Irrigation Zone
            ws = WaterSource(
                id="e0000000-0000-0000-0000-000000000001",
                organisation_id=org.id,
                farm_id=farm.id,
                name="Main Reservoir Dam",
                source_type="dam",
                capacity_litres=500000.0,
                current_level_litres=420000.0,
                status="operational"
            )
            db.add(ws)
            db.flush()

            pump = Pump(
                id="e1000000-0000-0000-0000-000000000001",
                water_source_id=ws.id,
                name="Primary Solar Pump A",
                pump_type="solar_direct",
                max_flow_rate_lpm=150.0,
                power_source="solar",
                is_running=False,
                max_continuous_runtime_sec=3600
            )
            db.add(pump)
            db.flush()

            zone = IrrigationZone(
                id="e2000000-0000-0000-0000-000000000001",
                organisation_id=org.id,
                farm_id=farm.id,
                field_id=f2.id,
                water_source_id=ws.id,
                pump_id=pump.id,
                name="Greenhouse Tomato Drip Zone",
                zone_code="Z-GH1",
                irrigation_method="drip",
                area_sqm=2000.0,
                flow_rate_lpm=45.0,
                target_soil_moisture_pct=65.0,
                is_active=False
            )
            db.add(zone)
            db.flush()

            # 7. Device & Sensors
            dev = Device(
                id="f0000000-0000-0000-0000-000000000001",
                organisation_id=org.id,
                farm_id=farm.id,
                field_id=f2.id,
                device_uid="esp32-node-001",
                name="ESP32 Soil & Climate Monitor",
                device_type="soil_probe",
                hardware_version="esp32-devkit-v1",
                firmware_version="1.0.0",
                provisioning_status="active",
                connection_status="online",
                battery_level_pct=94.0,
                signal_strength_rssi=-68
            )
            db.add(dev)
            db.flush()

            s1 = Sensor(
                id="f1000000-0000-0000-0000-000000000001",
                device_id=dev.id,
                sensor_index=0,
                sensor_code="soil_moist_10cm",
                measurement_type_code="soil_moisture",
                depth_cm=10.0,
                unit="%",
                status="active"
            )
            s2 = Sensor(
                id="f1000000-0000-0000-0000-000000000002",
                device_id=dev.id,
                sensor_index=1,
                sensor_code="dht22_temp",
                measurement_type_code="ambient_temp",
                unit="°C",
                status="active"
            )
            db.add_all([s1, s2])
            db.flush()

            # 8. Tasks, Equipment, Inventory
            task = Task(
                organisation_id=org.id,
                farm_id=farm.id,
                field_id=f1.id,
                title="Early Scouting for Fall Armyworm",
                description="Inspect maize leaves for egg clusters and early pinhole damage.",
                task_type="scouting",
                priority="high",
                status="in_progress",
                assigned_to=agronomist.id
            )
            equip = Equipment(
                organisation_id=org.id,
                farm_id=farm.id,
                name="John Deere 5075E Tractor",
                equipment_type="tractor",
                status="operational",
                operating_hours=480.5
            )
            inv = InventoryItem(
                organisation_id=org.id,
                farm_id=farm.id,
                item_name="DAP Planting Fertilizer",
                category="fertilizer",
                quantity_on_hand=1200.0,
                unit_of_measure="kg"
            )
            db.add_all([task, equip, inv])
            db.flush()

            # 9. Alert Rules & Intelligence Models
            rule = AlertRule(
                organisation_id=org.id,
                farm_id=farm.id,
                field_id=f2.id,
                name="Low Soil Moisture Warning",
                rule_type="threshold_min",
                measurement_type="soil_moisture",
                conditions={"operator": "<", "threshold": 25.0},
                severity="warning",
                channels=["in_app", "email"]
            )
            model = IntelligenceModel(
                name="FAO-56 Evapotranspiration & Soil Water Balance",
                model_type="irrigation_scheduler",
                version="1.0.0",
                framework="rule_based",
                description="Calculates daily crop water depletion using Penman-Monteith"
            )
            db.add_all([rule, model])
            db.flush()

            # 10. Initial Recommendation
            rec = Recommendation(
                organisation_id=org.id,
                farm_id=farm.id,
                field_id=f2.id,
                category="irrigation",
                title="Schedule 45-minute drip irrigation for Greenhouse Tomatoes",
                summary="Soil volumetric water content at 10cm depth has reached 28.5%, approaching the management allowed depletion (MAD) threshold of 25%.",
                rationale="High solar radiation (820 W/m²) forecast today will accelerate transpiration. An irrigation event of 45 minutes will restore root zone moisture to field capacity (65%).",
                confidence_score=0.92,
                urgency="high",
                proposed_actions=[{"action": "irrigate", "zone_code": "Z-GH1", "duration_minutes": 45}],
                status="proposed"
            )
            db.add(rec)
            db.flush()

            rec_ev = RecommendationEvidence(
                recommendation_id=rec.id,
                evidence_type="sensor_measurement",
                metric_name="soil_moisture_10cm",
                observed_value="28.5%",
                threshold_value="25.0%",
                source_reference="ESP32 Soil Probe f0000000-0000-0000-0000-000000000001"
            )
            db.add(rec_ev)

            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
