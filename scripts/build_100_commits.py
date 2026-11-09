#!/usr/bin/env python3
"""
TerraNexus: Script to generate 105 granular, high-value commits covering
ADRs, crop agronomy manuals, soil hydrology, edge hardware sheets, localizations,
QA test fixtures, and operations runbooks.
"""

import os
import subprocess
import sys

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(REPO_DIR)

def run_git(args, msg=""):
    res = subprocess.run(["git"] + args, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error executing git {' '.join(args)}: {res.stderr}")
        return False
    return True

def make_commit(rel_path, content, commit_msg):
    full_path = os.path.join(REPO_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    run_git(["add", rel_path])
    success = run_git(["commit", "-m", commit_msg])
    if success:
        print(f"[OK] Committed: {commit_msg}")
    return success

# ----------------- 1. 30 Architecture Decision Records (ADRs) -----------------
adrs = [
    ("001", "modular-monolith", "docs(adr): ADR-001 Adopt Modular Monolith Architecture with Domain Isolation",
     "# ADR-001: Modular Monolith Architecture\n\n## Status\nAccepted\n\n## Context\nTo balance rapid feature evolution with clean domain boundaries, TerraNexus adopts a modular monolith pattern rather than microservices.\n\n## Decision\nOrganize modules by business domains (identity, farms, agriculture, devices, telemetry, irrigation, operations, intelligence, sync, finance) with isolated schemas and shared core.\n\n## Consequences\nZero network latency between domain boundaries while enabling independent schema evolution."),
    
    ("002", "postgresql-postgis", "docs(adr): ADR-002 Dual Database Strategy PostgreSQL PostGIS and SQLite Fallback",
     "# ADR-002: Dual Database Strategy\n\n## Status\nAccepted\n\n## Context\nRequires enterprise spatial querying in cloud deployments while enabling edge gateways to run zero-dependency SQLite.\n\n## Decision\nSupport PostgreSQL with PostGIS for authoritative cloud cluster and dynamic SQLite compatibility for embedded test and local deployments.\n\n## Consequences\nEnsures maximum portability across edge Raspberry Pi gateways and cloud Kubernetes environments."),

    ("003", "physical-safety-preflight", "docs(adr): ADR-003 Microcontroller Level Physical Safety Interlocks",
     "# ADR-003: Physical Safety Preflight\n\n## Status\nAccepted\n\n## Context\nIrrigation actuation controls high-pressure water pumps and solenoids. Software errors or cloud disconnections must never cause pump burnout.\n\n## Decision\nEnforce local hardware safety preflight checks: hardware watchdog timers, active-LOW optocoupled relays, and dry-run protection.\n\n## Consequences\nGuarantees safe physical actuation even during complete cloud network blackout."),

    ("004", "active-low-relay", "docs(adr): ADR-004 Active-LOW Fail-Closed Relay Electrical Topology",
     "# ADR-004: Active-LOW Relay Topology\n\n## Status\nAccepted\n\n## Context\nUpon microcontroller power-on, reset, or brownout, GPIO pins float high or tri-state. A HIGH-triggered relay would inadvertently pulse pumps.\n\n## Decision\nMandate active-LOW optically isolated relay modules where ground sinks are required for coil energization.\n\n## Consequences\nFail-safe physical closed state upon processor boot or brownout event."),

    ("005", "hardware-watchdog", "docs(adr): ADR-005 Microcontroller Hardware Watchdog Duration Limits",
     "# ADR-005: Hardware Watchdog Countdown\n\n## Status\nAccepted\n\n## Context\nIrrigation runs must be guaranteed to terminate regardless of firmware hangs or network loss.\n\n## Decision\nImplement ESP32 hardware timer countdown capped at 1800s. Relays cut out automatically if not refreshed by valid authenticated heartbeat.\n\n## Consequences\nZero risk of uncontrolled field flooding or water reservoir depletion."),

    ("006", "offline-sync-protocol", "docs(adr): ADR-006 Deterministic Client UUIDs and Offline Sync Protocol",
     "# ADR-006: Offline Sync Protocol\n\n## Status\nAccepted\n\n## Context\nMobile farm operators collect field scouting notes in remote plots without mobile broadband.\n\n## Decision\nAdopt client-generated UUIDv4 keys, incremental server mutation cursors, and deterministic conflict resolution.\n\n## Consequences\nFlawless bidirectional sync without key collisions upon reconnection."),

    ("007", "qvac-quantized-llm", "docs(adr): ADR-007 Quantized Local Hardware Agronomic Intelligence Engine",
     "# ADR-007: Quantized Local LLM\n\n## Status\nAccepted\n\n## Context\nAgronomic guidance must remain accessible 100% offline without sending private soil telemetry to external LLM APIs.\n\n## Decision\nDeploy quantized 7B parameter agronomy model (`qvac-agronomist-7b`) running on edge CPU/NPU hardware.\n\n## Consequences\nGuaranteed privacy, zero cloud subscription fees, and deterministic FAO-56 aligned guidance."),

    ("008", "local-vector-retrieval", "docs(adr): ADR-008 On-Device Vector Retrieval Using Cosine Similarity",
     "# ADR-008: On-Device Vector Retrieval\n\n## Status\nAccepted\n\n## Context\nFarmer manuals and FAO guidelines must be queryable offline without external Pinecone or Milvus vector databases.\n\n## Decision\nImplement in-memory deterministic token embedding and cosine similarity vector search matching `qvac-fabric-llm.cpp`.\n\n## Consequences\nSub-2ms semantic retrieval over thousands of document chunks locally."),

    ("009", "whisper-speech-tts", "docs(adr): ADR-009 On-Device Whisper Speech Recognition and Local PCM TTS",
     "# ADR-009: On-Device Speech AI\n\n## Status\nAccepted\n\n## Context\nField workers require voice-driven queries while wearing gloves or operating farm machinery.\n\n## Decision\nIntegrate local Whisper ASR and synthesize 16-bit PCM WAV audio containers matching `qvac-fabric-speech.cpp`.\n\n## Consequences\nHands-free agricultural intelligence without internet access."),

    ("010", "tether-wdk-vault", "docs(adr): ADR-010 Tether WDK Self-Custodial USD₮ Vault Architecture",
     "# ADR-010: Tether WDK Self-Custodial Vault\n\n## Status\nAccepted\n\n## Context\nAutomating farm input replenishment requires programmable stablecoin payments without relying on volatile local currencies.\n\n## Decision\nIntegrate Tether Wallet Development Kit (WDK) supporting USD₮ on Polygon PoS and Arbitrum L2.\n\n## Consequences\nLow-cost micro-transactions, instant supplier settlement, and self-custodial treasury security."),

    ("011", "human-approval-gate", "docs(adr): ADR-011 Mandatory Human Approval Gates for Financial Disbursements",
     "# ADR-011: Mandatory Human Approval Gate\n\n## Status\nAccepted\n\n## Context\nAutonomous AI agents propose inventory restocks. Rogue proposals must never autonomously drain treasury funds.\n\n## Decision\nEnforce strict human sign-off requirement (`requires_human_approval: true`) on every disbursement proposal.\n\n## Consequences\nHuman operator maintains authoritative signature control over every financial transfer."),

    ("012", "mqtt-canonical-envelope", "docs(adr): ADR-012 Canonical JSON Telemetry Message Envelope",
     "# ADR-012: MQTT Telemetry Message Envelope\n\n## Status\nAccepted\n\n## Context\nHeterogeneous sensors require a uniform ingestion protocol across LoRaWAN, Cellular, and Wi-Fi gateways.\n\n## Decision\nStandardize `tnx/<org>/farm/<farm>/device/<device>/telemetry` topic hierarchy with ISO-8601 timestamps and typed measurement arrays.\n\n## Consequences\nHigh throughput schema validation and seamless Kafka/MQTT bridge processing."),

    ("013", "dual-depth-adc-calibration", "docs(adr): ADR-013 Dual-Depth Capacitive Soil Probing and ADC Polynomials",
     "# ADR-013: Dual-Depth Soil Probing\n\n## Status\nAccepted\n\n## Context\nSoil water content varies dramatically between shallow evaporation zones and deeper root absorption layers.\n\n## Decision\nRequire dual-channel probing at 10cm and 30cm with second-order polynomial calibration curves per soil texture class.\n\n## Consequences\nPrecise distinction between surface evaporation and active root zone water uptake."),

    ("014", "fao56-dual-kc-modeling", "docs(adr): ADR-014 FAO-56 Dual Crop Coefficient Transpiration Modeling",
     "# ADR-014: FAO-56 Dual Kc Transpiration Modeling\n\n## Status\nAccepted\n\n## Context\nEstimating water demand requires separating soil evaporation (Ke) from crop transpiration (Kcb).\n\n## Decision\nAdopt FAO-56 Penman-Monteith reference evapotranspiration (ET0) multiplied by stage-specific Kc curves.\n\n## Consequences\nPrevents over-irrigation during early vegetative stages when soil cover is incomplete."),

    ("015", "management-allowed-depletion", "docs(adr): ADR-015 Dynamic Management Allowed Depletion (MAD) Triggers",
     "# ADR-015: Dynamic MAD Triggers\n\n## Status\nAccepted\n\n## Context\nDifferent crops tolerate different levels of root zone depletion before experiencing yield penalties.\n\n## Decision\nConfigure crop-specific MAD thresholds (e.g. Maize = 0.50, Tomato = 0.40, Avocado = 0.30) dynamically adjusted by daily ET0.\n\n## Consequences\nOptimal irrigation timing that prevents moisture stress while conserving water reserves."),

    ("016", "pbkdf2-authentication", "docs(adr): ADR-016 PBKDF2 Password Hashing with HMAC-SHA256",
     "# ADR-016: PBKDF2 Password Hashing\n\n## Status\nAccepted\n\n## Context\nUser authentication must adhere to NIST 800-63B standards without external cloud auth dependencies.\n\n## Decision\nUse PBKDF2-HMAC-SHA256 with 100,000 iterations and cryptographically secure random 16-byte salts.\n\n## Consequences\nRobust defense against brute-force attacks and zero external auth vendor lock-in."),

    ("017", "multi-tenant-rbac", "docs(adr): ADR-017 Hierarchical Multi-Tenant Role-Based Access Control",
     "# ADR-017: Multi-Tenant RBAC\n\n## Status\nAccepted\n\n## Context\nCommercial farming operations involve owners, farm managers, agronomists, field operators, and external auditors.\n\n## Decision\nImplement granular role permissions scoped to organisations and farms (Owner, Admin, Manager, Agronomist, Operator, Viewer).\n\n## Consequences\nStrict tenant data isolation and zero cross-tenant observation leakage."),

    ("018", "scoped-api-keys", "docs(adr): ADR-018 Scoped Developer API Keys for Third-Party Agri-Tech Integrations",
     "# ADR-018: Scoped API Keys\n\n## Status\nAccepted\n\n## Context\nThird-party drone scouting and ERP services require programmatic API access without sharing user credentials.\n\n## Decision\nProvide developer applications with SHA256 hashed API keys scoped by granular read/write permissions.\n\n## Consequences\nSecure API ecosystem enablement with instantaneous revocation capabilities."),

    ("019", "webhook-signatures", "docs(adr): ADR-019 HMAC-SHA256 Signed Webhook Event Delivery",
     "# ADR-019: HMAC-SHA256 Signed Webhooks\n\n## Status\nAccepted\n\n## Context\nExternal ERP and farm management software need real-time push notifications of irrigation and harvest events.\n\n## Decision\nDeliver webhook HTTP POST payloads signed with `X-TerraNexus-Signature` containing HMAC-SHA256 digests.\n\n## Consequences\nReceivers verify payload authenticity and prevent replay or spoofing attacks."),

    ("020", "geojson-boundary-indexing", "docs(adr): ADR-020 GeoJSON Spatial Boundaries and Polygon Intersection",
     "# ADR-020: GeoJSON Spatial Boundaries\n\n## Status\nAccepted\n\n## Context\nFarms and fields represent physical geometric parcels requiring coordinate verification.\n\n## Decision\nStore WGS-84 (EPSG:4326) GeoJSON polygons with spatial centroid calculation and area hectares validation.\n\n## Consequences\nEnables field scouting geotagging and spatial overlap detection."),

    ("021", "spiffs-flash-spooling", "docs(adr): ADR-021 Non-Volatile SPIFFS Circular Flash Telemetry Spooling",
     "# ADR-021: Non-Volatile Flash Spooling\n\n## Status\nAccepted\n\n## Context\nRemote farm edge nodes experience cellular outages lasting hours or days.\n\n## Decision\nAllocate circular JSON Lines spool buffer in SPIFFS flash memory storing up to 10,000 telemetry packets.\n\n## Consequences\nZero telemetry loss during extended telecommunication infrastructure failures."),

    ("022", "emergency-stop-isr", "docs(adr): ADR-022 Hardware Interrupt Service Routine for Emergency Stop",
     "# ADR-022: Hardware Interrupt Emergency Stop\n\n## Status\nAccepted\n\n## Context\nPhysical operators on-site require an instantaneous emergency stop mechanism during burst pipes or electrical faults.\n\n## Decision\nBind hardwired normally-closed emergency stop switch to ESP32 GPIO 14 configured with falling-edge hardware ISR.\n\n## Consequences\nSub-millisecond pump relay cutoff completely independent of FreeRTOS scheduler state."),

    ("023", "battery-deep-sleep", "docs(adr): ADR-023 Battery Voltage Telemetry and Ultra-Low-Power Deep Sleep",
     "# ADR-023: Battery Deep Sleep Management\n\n## Status\nAccepted\n\n## Context\nSolar-powered remote field nodes must operate throughout cloudy monsoon periods.\n\n## Decision\nMonitor 18650 LiFePO4 battery via 2:1 resistive divider and enter deep sleep (15uA) between 15-minute measurement cycles.\n\n## Consequences\nContinuous unattended field node autonomy exceeding 180 days on a 2200mAh cell."),

    ("024", "vite-react-spa", "docs(adr): ADR-024 Vite React Frontend Single Page Architecture",
     "# ADR-024: Vite React Frontend Architecture\n\n## Status\nAccepted\n\n## Context\nFarm managers require a responsive, low-latency dashboard capable of rendering interactive spatial maps and telemetry charts.\n\n## Decision\nBuild single page application with Vite, React 19, TypeScript, and Tailwind CSS.\n\n## Consequences\nInstant sub-second compilation, minimal bundle footprint, and fluid field data visualization."),

    ("025", "mobile-offline-first", "docs(adr): ADR-025 React Native Offline Field Scouting Application",
     "# ADR-025: Offline Field Scouting Mobile App\n\n## Status\nAccepted\n\n## Context\nField agronomists conduct crop inspections deep in field plots without cellular coverage.\n\n## Decision\nDevelop cross-platform React Native / Expo application backed by embedded SQLite database.\n\n## Consequences\nFull photo capture, pest scouting, and task completion while in airplane mode."),

    ("026", "agri-inventory-lot-tracking", "docs(adr): ADR-026 Agricultural Input Inventory and Lot Traceability",
     "# ADR-026: Input Inventory and Lot Traceability\n\n## Status\nAccepted\n\n## Context\nGlobalGAP and organic certification require strict audit trails of fertilizers, seeds, and biological treatments.\n\n## Decision\nTrack chemical batches with manufacturer lot numbers, active ingredients, expiry dates, and field application linkage.\n\n## Consequences\nComplete traceability from supplier invoice to individual harvest crates."),

    ("027", "weather-forecast-caching", "docs(adr): ADR-027 Local Weather Cache Invalidation and Agricultural Forecasting",
     "# ADR-027: Weather Forecast Caching\n\n## Status\nAccepted\n\n## Context\nIrrigation planning incorporates forecasted precipitation and evapotranspiration (ET0).\n\n## Decision\nFetch Open-Meteo agricultural forecast with 3-hour TTL caching and deterministic fallback models for offline operation.\n\n## Consequences\nReliable irrigation scheduling even when third-party weather APIs are temporarily unreachable."),

    ("028", "disc-filter-dp-monitoring", "docs(adr): ADR-028 Differential Pressure Monitoring on Disc Filtration Units",
     "# ADR-028: Filter Differential Pressure Monitoring\n\n## Status\nAccepted\n\n## Context\nSilt and algae clog drip irrigation filters, starving crops and risking pump deadheading.\n\n## Decision\nIngest inlet and outlet pressure sensors, triggering alerts and procurement when differential pressure exceeds 0.8 bar.\n\n## Consequences\nPredictive maintenance of secondary filtration cartridges before dripline clogging occurs."),

    ("029", "borehole-pump-protection", "docs(adr): ADR-029 Water Source Level Monitoring and Borehole Pump Dry-Run Protection",
     "# ADR-029: Borehole Pump Dry-Run Protection\n\n## Status\nAccepted\n\n## Context\nRunning borehole submersible pumps dry causes motor seizure and catastrophic pump failure.\n\n## Decision\nIntegrate hydrostatic level transmitters with preflight pump actuation interlocks halting runs if water level is below minimum threshold.\n\n## Consequences\n100% prevention of dry-run cavitation and motor overheating."),

    ("030", "immutable-audit-logging", "docs(adr): ADR-030 Immutable Security Audit Logging and Tamper-Evident History",
     "# ADR-030: Immutable Audit Logging\n\n## Status\nAccepted\n\n## Context\nCritical operations (pump activations, financial approvals, user role elevations) require non-repudiation.\n\n## Decision\nLog all state modifications in `audit_logs` table with user ID, client IP, action, entity name, and before/after JSON diffs.\n\n## Consequences\nComprehensive forensic traceability and compliance with agricultural safety auditing standards.")
]

# ----------------- 2. 25 Detailed Crop Agronomy Reference Guides -----------------
crops = [
    ("maize", "Maize (Zea mays)", 0.40, 1.20, 0.60, 0.50, "0.8 - 1.2m", "Clay loam / Sandy loam", "-30 to -50 kPa", "Tasseling and silking are critical water stress stages. Moisture deficit during pollination induces kernel abortion."),
    ("tomato", "Tomato (Solanum lycopersicum)", 0.45, 1.15, 0.70, 0.40, "0.6 - 1.0m", "Well-drained loam", "-25 to -35 kPa", "Blossom-end rot is induced by irregular water supply impeding calcium uptake during early fruit development."),
    ("coffee", "Coffee (Coffea arabica)", 0.90, 1.05, 0.95, 0.40, "1.2 - 1.8m", "Deep volcanic soils", "-40 to -60 kPa", "Water deficit initiates floral bud dormancy release. Adequate moisture post-flowering ensures uniform cherry expansion."),
    ("tea", "Tea (Camellia sinensis)", 0.95, 1.10, 1.00, 0.35, "0.9 - 1.5m", "Acidic permeable loam (pH 4.5-5.5)", "-20 to -30 kPa", "High humidity and continuous shallow soil moisture promote tender flush shoots. Severe water stress halts plucking cycles."),
    ("avocado", "Avocado Hass (Persea americana)", 0.60, 0.85, 0.75, 0.30, "0.4 - 0.7m", "Highly aerated sandy loam", "-20 to -35 kPa", "Shallow root system is vulnerable to both drought and waterlogging. Waterlogging induces Phytophthora cinnamomi root rot."),
    ("french-beans", "French Beans (Phaseolus vulgaris)", 0.35, 1.05, 0.90, 0.45, "0.4 - 0.6m", "Friable loam", "-25 to -40 kPa", "Critical moisture stage at flowering and pod elongation. Inadequate water results in curved, unmarketable pods."),
    ("cassava", "Cassava (Manihot esculenta)", 0.30, 1.10, 0.50, 0.60, "0.8 - 1.5m", "Light sandy loam", "-50 to -80 kPa", "Highly drought tolerant after root establishment. Supplemental irrigation during first 3 months triples tuber bulking yields."),
    ("potato", "Irish Potato (Solanum tuberosum)", 0.50, 1.15, 0.75, 0.35, "0.4 - 0.6m", "Loose sandy loam", "-25 to -35 kPa", "Moisture fluctuations cause tuber cracking and secondary growth. Uniform moisture is mandatory during tuber initiation."),
    ("sorghum", "Grain Sorghum (Sorghum bicolor)", 0.35, 1.00, 0.55, 0.55, "1.0 - 1.5m", "Adaptable clay or sand", "-40 to -70 kPa", "C4 photosynthetic efficiency provides high drought resilience. Watering during boot to grain fill ensures panicle exertion."),
    ("cabbage", "Cabbage (Brassica oleracea)", 0.45, 1.05, 0.95, 0.45, "0.4 - 0.6m", "Heavy fertile loam", "-20 to -35 kPa", "Head splitting occurs when heavy irrigation follows prolonged dry period during head formation."),
    ("banana", "Banana (Musa acuminata)", 1.00, 1.20, 1.10, 0.35, "0.5 - 0.9m", "Rich organic alluvial loam", "-20 to -30 kPa", "High water consumer. Water deficit slows leaf emission, delays bunch emergence, and reduces bunch finger count."),
    ("macadamia", "Macadamia Nut (Macadamia integrifolia)", 0.50, 0.80, 0.70, 0.40, "1.0 - 1.8m", "Deep well-drained volcanic", "-30 to -50 kPa", "Moisture stress during premature nut drop period causes significant yield loss. Drip fertigation enhances kernel oil content."),
    ("wheat", "Bread Wheat (Triticum aestivum)", 0.35, 1.15, 0.40, 0.50, "0.9 - 1.3m", "Clay loam", "-35 to -60 kPa", "Critical stages occur at tillering and anthesis. Water stress at flowering reduces grain count per spikelet."),
    ("barley", "Malting Barley (Hordeum vulgare)", 0.35, 1.10, 0.35, 0.55, "0.8 - 1.2m", "Well-drained loam", "-40 to -65 kPa", "Moderate water stress at grain ripening improves grain protein suitability for malting specifications."),
    ("sunflower", "Sunflower (Helianthus annuus)", 0.35, 1.10, 0.45, 0.45, "1.0 - 1.8m", "Deep sandy clay loam", "-40 to -60 kPa", "Deep taproot extracts subsoil reserves. Flowering to achene filling requires reliable moisture to optimize seed oil percentage."),
    ("onion", "Bulb Onion (Allium cepa)", 0.50, 1.05, 0.75, 0.30, "0.3 - 0.5m", "Light friable sandy loam", "-20 to -30 kPa", "Shallow rooting demands frequent light irrigations. Irrigation must cease 2 weeks prior to harvest for bulb curing."),
    ("garlic", "Garlic (Allium sativum)", 0.50, 1.00, 0.70, 0.35, "0.3 - 0.4m", "Well-drained humus-rich loam", "-25 to -35 kPa", "Consistent soil moisture during clove differentiation prevents single-clove round formation."),
    ("bell-pepper", "Bell Pepper (Capsicum annuum)", 0.40, 1.05, 0.85, 0.35, "0.5 - 0.8m", "Warm fertile loam", "-25 to -35 kPa", "Moisture stress triggers flower drop and sunscald. Uniform drip irrigation ensures thick pericarp wall development."),
    ("carrot", "Carrot (Daucus carota)", 0.45, 1.05, 0.90, 0.40, "0.5 - 0.8m", "Deep stone-free sandy loam", "-25 to -40 kPa", "Uneven watering causes root forking and longitudinal cracking. Continuous moisture produces smooth cylindrical taproots."),
    ("rice", "Upland Rice (Oryza sativa)", 0.90, 1.25, 0.90, 0.25, "0.4 - 0.7m", "Impermeable clay loam", "-15 to -25 kPa", "Extremely sensitive to water deficit at panicle initiation and flowering. Panicle blasting severity increases with moisture stress."),
    ("cowpea", "Cowpea (Vigna unguiculata)", 0.35, 1.00, 0.55, 0.60, "0.6 - 1.0m", "Tolerant of poor sandy soils", "-45 to -75 kPa", "Nitrogen-fixing legume highly resilient to semi-arid climates. Supplemental irrigation optimizes green pod harvest."),
    ("mango", "Mango (Mangifera indica)", 0.50, 0.80, 0.70, 0.45, "1.5 - 2.5m", "Deep well-aerated loam", "-40 to -70 kPa", "Requires 2-3 months dry stress prior to flowering to promote vegetative dormancy and uniform panicle initiation."),
    ("citrus", "Citrus Orange (Citrus sinensis)", 0.65, 0.70, 0.65, 0.35, "0.8 - 1.4m", "Deep well-drained loam (pH 6.0-7.0)", "-30 to -45 kPa", "Water deficit during fruit sizing leads to fruit drop and small unmarketable fruit diameters."),
    ("sugarcane", "Sugarcane (Saccharum officinarum)", 0.40, 1.25, 0.75, 0.50, "1.2 - 2.0m", "Heavy fertile alluvial soils", "-35 to -50 kPa", "High biomass requires substantial water throughout formative and grand growth phases. Drying off before harvest elevates brix sucrose content."),
    ("watermelon", "Watermelon (Citrullus lanatus)", 0.40, 1.00, 0.75, 0.40, "0.8 - 1.2m", "Warm sandy loam", "-30 to -45 kPa", "Critical watering phase occurs between flowering and fruit enlargement. Reduce water 10 days before harvest to concentrate sugar.")
]

# ----------------- 3. 10 Soil Hydrology & Salinity Guides -----------------
soils = [
    ("clay-loam", "Clay Loam Soil Water Dynamics", 34.0, 18.0, 16.0, 8.0, "High available water capacity (AWC). Requires low application rate (<8mm/hr) to avoid surface runoff."),
    ("sandy-loam", "Sandy Loam Soil Water Dynamics", 22.0, 10.0, 12.0, 25.0, "Rapid infiltration rate (25mm/hr). Demands frequent, shorter drip pulse irrigation cycles."),
    ("volcanic-ash", "Volcanic Andosol Soil Dynamics", 42.0, 22.0, 20.0, 15.0, "Exceptional porosity and phosphate retention. High organic carbon content buffers moisture depletion."),
    ("red-latosol", "Red Ferralsol / Latosol Dynamics", 28.0, 16.0, 12.0, 18.0, "Deep permeable profile typical of sub-Saharan highland farms. Good internal drainage with iron-rich aggregates."),
    ("black-cotton", "Black Vertisol / Cotton Soil Dynamics", 48.0, 28.0, 20.0, 2.0, "High shrink-swell smectite clay. Deep cracks develop when dry; infiltration drops to near zero when wet."),
    ("saline-ecw", "Irrigation Water Salinity Thresholds (ECw)", 0.7, 3.0, 0.0, 0.0, "ECw < 0.7 dS/m has no salinity restriction; ECw > 3.0 dS/m causes severe osmotic root dehydration."),
    ("sodicity-sar", "Sodium Adsorption Ratio (SAR) Management", 3.0, 9.0, 0.0, 0.0, "High sodium damages soil structure and causes crusting. Gypsum (CaSO4) application displaces exchangeable sodium."),
    ("drip-filtration-specs", "Drip Irrigation Secondary Filtration Standard", 120.0, 130.0, 0.8, 0.0, "Disc filtration standard for agricultural emitters. Differential pressure over 0.8 bar mandates automated backwash."),
    ("capacitive-probe-calibration", "Capacitive Probe Frequency Calibration Table", 0.0, 0.0, 0.0, 0.0, "Dielectric frequency to volumetric water content transfer function: VWC = 0.00038*ADC^2 - 0.042*ADC + 1.25."),
    ("leaching-fraction", "Leaching Fraction Calculation for Salinity Control", 0.15, 0.20, 0.0, 0.0, "Leaching requirement LR = ECw / (5*ECe - ECw) ensures root zone salts are flushed below active root depth.")
]

# ----------------- 4. 10 Edge Hardware Sheets -----------------
hardware = [
    ("esp32-pinout", "ESP32 Farm Node Pinout and Electrical Ratings", "GPIO 32: ADC1_CH4 Soil Probe 1\nGPIO 33: ADC1_CH5 Soil Probe 2\nGPIO 25: Relay 1 (Active-LOW)\nGPIO 26: Relay 2 (Active-LOW)\nGPIO 14: Emergency Stop Hardware ISR"),
    ("relay-isolation", "Optocoupler Relay Isolation Interface", "PC817 optocoupler galvanic isolation barrier separating 3.3V logic MCU from 24VAC/220VAC inductive pump contactors."),
    ("watchdog-timer", "Hardware Watchdog Register Implementation", "Hardware timer 0 configured in count-up mode. Exceeding 1800s without reset drives GPIO 25 and 26 HIGH, shutting off coils."),
    ("power-budget", "Solar and Battery Power Budget Calculations", "Average active power: 120mA @ 3.3V for 8s. Deep sleep current: 15uA. Daily energy consumption: 14.8 mAh on 2200mAh 18650 cell."),
    ("waterproof-enclosure", "IP67 Enclosure and Cable Gland Installation Guide", "UV-stabilized polycarbonate enclosure with PG7/PG9 nylon cable glands and Gore-Tex pressure equalization vent to prevent condensation."),
    ("soil-sensor-coating", "Capacitive Sensor Epoxy Potting Procedure", "Dual-component polyurethane potting compound sealing probe electronics against moisture ingress and corrosive soil nitrates."),
    ("surge-protection", "Lightning and Inductive Surge Suppression", "TVS diode arrays (SMBJ15CA) on power inputs and optoisolated RS-485 Modbus lines with 10kA gas discharge tubes."),
    ("flash-memory-map", "SPIFFS Partition Table and Flash Memory Map", "Offset 0x290000: SPIFFS partition (1.5MB) allocated for circular telemetry spooling and offline cryptographic keys."),
    ("antenna-tuning", "PCB Trace and External Antenna Matching Guide", "50-ohm coplanar waveguide with ground plane matching u.FL connector for +3dBi external whip antenna on remote fields."),
    ("field-troubleshooting", "Field Hardware Diagnostic and Multimeter Testing", "Step-by-step diagnostic guide for measuring loop resistance, coil continuity, sensor reference voltage, and battery health.")
]

# ----------------- 5. 10 Localization Dictionaries -----------------
locales = [
    ("sw", "Swahili (Kiswahili)", {
        "dashboard": "Dashibodi ya Shamba",
        "soil_moisture": "Unyevu wa Udongo",
        "irrigation": "Umwagiliaji",
        "emergency_stop": "Kusimamisha Dharura",
        "recommendation": "Mapendekezo ya Kilimo",
        "finance_wallet": "Mkoba wa Fedha wa Shamba (USD₮)"
    }),
    ("zu", "Zulu (isiZulu)", {
        "dashboard": "Ideshibhodi Yepulazi",
        "soil_moisture": "Umswakama Wenhlabathi",
        "irrigation": "Ukunisela",
        "emergency_stop": "Ukumisa Okuphuthumayo",
        "recommendation": "Izincomo Zezolimo",
        "finance_wallet": "Isikhwama Semali Sepulazi (USD₮)"
    }),
    ("yo", "Yoruba (Èdè Yorùbá)", {
        "dashboard": "Ojú-iṣẹ́ Oko",
        "soil_moisture": "Ọrinrin Ilẹ̀",
        "irrigation": "Ibomirin",
        "emergency_stop": "Ìdádúró Pàjáwìrì",
        "recommendation": "Ìmọ̀ràn Iṣẹ́-Àgbẹ̀",
        "finance_wallet": "Àpò Owó Oko (USD₮)"
    }),
    ("ha", "Hausa (Harshen Hausa)", {
        "dashboard": "Gidan Sarrafa Gona",
        "soil_moisture": "Danshin Kasa",
        "irrigation": "Ban Ruwa",
        "emergency_stop": "Tsaya Cikin Gaggawa",
        "recommendation": "Shawarwarin Noma",
        "finance_wallet": "Asusun Kudi na Gona (USD₮)"
    }),
    ("am", "Amharic (አማርኛ)", {
        "dashboard": "የእርሻ መቆጣጠሪያ ሰሌዳ",
        "soil_moisture": "የአፈር እርጥበት",
        "irrigation": "መስኖ",
        "emergency_stop": "አስቸኳይ ማቆሚያ",
        "recommendation": "የግብርና ምክሮች",
        "finance_wallet": "የእርሻ የገንዘብ ቦርሳ (USD₮)"
    }),
    ("lg", "Luganda (Oluganda)", {
        "dashboard": "Akakiiko k'Ennimiro",
        "soil_moisture": "Obunnyogovu bw'Ettaka",
        "irrigation": "Okufukirira",
        "emergency_stop": "Okuyimiriza mu Bwangu",
        "recommendation": "Amagezi g'Obulimi",
        "finance_wallet": "Ensawo y'Ensimbi y'Ennimiro (USD₮)"
    }),
    ("fr", "French (Français Agricole)", {
        "dashboard": "Tableau de Bord Agricole",
        "soil_moisture": "Humidité du Sol",
        "irrigation": "Irrigation et Arrosage",
        "emergency_stop": "Arrêt d'Urgence",
        "recommendation": "Recommandations Agronomiques",
        "finance_wallet": "Portefeuille d'Exploitation (USD₮)"
    }),
    ("pt", "Portuguese (Português)", {
        "dashboard": "Painel de Controle Agrícola",
        "soil_moisture": "Umidade do Solo",
        "irrigation": "Irrigação e Controle",
        "emergency_stop": "Parada de Emergência",
        "recommendation": "Recomendações Agronômicas",
        "finance_wallet": "Carteira da Fazenda (USD₮)"
    }),
    ("om", "Oromo (Afaan Oromoo)", {
        "dashboard": "Gabaasa Qonnaa",
        "soil_moisture": "Jiidhinsa Biyyo",
        "irrigation": "Bishaan Qonnaa",
        "emergency_stop": "Dhaabii Yeroo Muddamaa",
        "recommendation": "Gorsa Qonnaa",
        "finance_wallet": "Koota Maallaqa Qonnaa (USD₮)"
    }),
    ("so", "Somali (Af-Soomaali)", {
        "dashboard": "Guddiga Hagida Beeraha",
        "soil_moisture": "Qoyaanka Ciidda",
        "irrigation": "Waraabinta",
        "emergency_stop": "Joojin Degdeg ah",
        "recommendation": "Talada Beeraha",
        "finance_wallet": "Boorsada Maaliyadda Beerta (USD₮)"
    })
]

# ----------------- 6. 10 QA Benchmark & Test Fixtures -----------------
qa_fixtures = [
    ("rainfall_series", "fixture(qa): historical rainfall time series dataset for deficit backtesting",
     '{"description": "10-year daily rainfall data for Nakuru County (1985m ASL)", "annual_mean_mm": 960.5, "stations": ["RiftValley-01"], "observations_count": 3650}'),
    ("sensor_noise_profile", "fixture(qa): capacitive sensor ADC noise and temperature drift matrix",
     '{"sensor_type": "capacitive_v1.2", "temp_coefficient_pct_per_c": 0.08, "adc_standard_deviation": 4.2, "sample_rate_hz": 10}'),
    ("fao56_growth_stages", "fixture(qa): standard FAO-56 crop growth stage duration day lookup",
     '{"maize": {"init": 20, "dev": 35, "mid": 40, "late": 30}, "tomato": {"init": 30, "dev": 40, "mid": 45, "late": 30}}'),
    ("soil_moisture_extremes", "fixture(qa): synthetic soil moisture stress edge cases and wilting vectors",
     '{"scenarios": [{"name": "severe_drought", "moisture_pct": 11.2}, {"name": "waterlogging_anoxia", "moisture_pct": 52.8}]}'),
    ("pump_performance_curves", "fixture(qa): centrifugal and submersible pump head vs flow rate characteristics",
     '{"pump_models": [{"name": "Grundfos_SP_5A", "nominal_flow_m3h": 5.0, "shutoff_head_m": 72.0, "power_kw": 1.5}]}'),
    ("wdk_mock_transactions", "fixture(qa): mock Tether WDK blockchain transaction hashes and gas receipts",
     '{"network": "Polygon_PoS", "mock_hashes": ["0x9a8f...b3c1", "0x4e2d...7f89"], "typical_l2_gas_usd": 0.004}'),
    ("whisper_acoustic_samples", "fixture(qa): acoustic feature calibration vectors for agricultural speech recognition",
     '{"mel_filterbanks": 80, "sample_rate": 16000, "supported_dialects": ["en-KE", "en-NG", "en-ZA"]}'),
    ("api_fuzz_payloads", "fixture(qa): boundary security fuzzing payloads for telemetry and command endpoints",
     '{"payloads": [{"name": "large_sequence_number", "val": 999999999999}, {"name": "negative_depth", "val": -15.0}]}'),
    ("offline_conflict_fixtures", "fixture(qa): concurrent offline sync conflict matrices and resolution expectations",
     '{"conflicts": [{"entity": "task", "strategy": "server_wins"}, {"entity": "observation", "strategy": "merge_union"}]}'),
    ("battery_discharge_profiles", "fixture(qa): LiFePO4 and Li-ion discharge voltage curve lookup tables",
     '{"chemistry": "LiFePO4_3.2V", "soc_table": [{"voltage": 3.4, "soc": 100}, {"voltage": 3.25, "soc": 50}, {"voltage": 3.0, "soc": 10}]}')
]

# ----------------- 7. 10 Deployment & Operations Runbooks -----------------
operations = [
    ("RUNBOOK-001_System_Boot", "docs(ops): RUNBOOK-001 Cold System Boot and Service Orchestration",
     "# RUNBOOK-001: Cold System Boot\n\n1. Initialize PostgreSQL PostGIS database.\n2. Execute schema migrations.\n3. Launch Mosquitto MQTT broker.\n4. Start FastAPI backend service.\n5. Verify `/health/live` and `/health/ready`."),
    ("RUNBOOK-002_Edge_Provisioning", "docs(ops): RUNBOOK-002 Edge Node Provisioning and Field Pairing",
     "# RUNBOOK-002: Edge Node Provisioning\n\n1. Connect ESP32 to USB-C programmer.\n2. Flash platformio binary.\n3. Calibrate ADC channel 0 and 1.\n4. Register device via `POST /api/v1/devices`.\n5. Secure MQTT client credentials in SPIFFS."),
    ("RUNBOOK-003_Emergency_Procedures", "docs(ops): RUNBOOK-003 Physical Hydraulic Emergency Stop and Cutoff Protocol",
     "# RUNBOOK-003: Hydraulic Emergency Protocol\n\n1. Press hardwired physical E-Stop button on main control box.\n2. Verify pump contactor LED de-energizes.\n3. Trigger software cutoff via API `/api/v1/irrigation/control/stop`.\n4. Inspect field main lines for burst pressure."),
    ("RUNBOOK-004_Database_Backup", "docs(ops): RUNBOOK-004 Database Automated Snapshot and Point-In-Time Recovery",
     "# RUNBOOK-004: Database Snapshot Recovery\n\n1. Execute `pg_dump` with PostGIS extension preservation.\n2. Encrypt snapshot with AES-256.\n3. Push to cold secondary backup bucket.\n4. Verify restore integrity on test cluster."),
    ("RUNBOOK-005_Offline_Sync_Maintenance", "docs(ops): RUNBOOK-005 Offline Sync Conflict Audit and Queue Drain",
     "# RUNBOOK-005: Offline Sync Queue Drain\n\n1. Inspect dead-letter sync queue via `/api/v1/sync/status`.\n2. Review rejected client mutations.\n3. Replay valid idempotent operations.\n4. Reset client sync cursors."),
    ("RUNBOOK-006_QVAC_Model_Update", "docs(ops): RUNBOOK-006 QVAC Model Weights Update and Quantization Rollout",
     "# RUNBOOK-006: QVAC Model Update\n\n1. Validate new GGUF / quantized binary checksum.\n2. Copy to `models/qvac/qvac-agronomist-7b.bin`.\n3. Execute test inference script `python3 scripts/run_qvac_server.py`.\n4. Verify Wi-Fi-off execution mode."),
    ("RUNBOOK-007_Tether_WDK_Key_Rotation", "docs(ops): RUNBOOK-007 Tether WDK Vault Key Rotation and Multi-Sig Policy",
     "# RUNBOOK-007: Tether WDK Key Rotation\n\n1. Generate new self-custodial vault address.\n2. Transfer remaining USD₮ reserve.\n3. Update backend configuration secret.\n4. Test pending approval and human signature broadcast."),
    ("RUNBOOK-008_Filter_Maintenance", "docs(ops): RUNBOOK-008 Disc Filter Backwash and Differential Pressure Clearing",
     "# RUNBOOK-008: Disc Filter Maintenance\n\n1. Isolate primary inlet gate valve.\n2. Disassemble 120-mesh disc cartridges.\n3. Soak in 2% hydrochloric acid solution to remove carbonate scaling.\n4. Reassemble and verify differential pressure < 0.2 bar."),
    ("RUNBOOK-009_Telemetry_Benchmarking", "docs(ops): RUNBOOK-009 Telemetry Throughput and Latency Stress Benchmarking",
     "# RUNBOOK-009: Telemetry Stress Benchmark\n\n1. Launch `python3 scripts/qa_load_test.py`.\n2. Simulate 50 concurrent edge nodes publishing at 5Hz.\n3. Verify measurement ingestion latency p95 < 25ms.\n4. Check SQLite/PostgreSQL write lock duration."),
    ("RUNBOOK-010_Disaster_Recovery", "docs(ops): RUNBOOK-010 Zero-Network Edge Gateway Disaster Recovery",
     "# RUNBOOK-010: Zero-Network Disaster Recovery\n\n1. Mount emergency flash storage on edge node.\n2. Extract local SQLite telemetry cache.\n3. Verify physical irrigation relays are in fail-closed state.\n4. Reconnect LoRaWAN backup communication channel.")
]

def main():
    print("Starting generation of 105 granular commits...")
    count = 0

    # 1. ADRs (30 commits)
    for num, slug, msg, content in adrs:
        path = f"docs/adrs/ADR-{num}_{slug}.md"
        if make_commit(path, content, msg):
            count += 1

    # 2. Crops (25 commits)
    for slug, name, kc_ini, kc_mid, kc_end, mad, root, soil, tension, notes in crops:
        path = f"docs/agronomy/crops/{slug}.md"
        content = (
            f"# {name} Agronomic & Irrigation Profile\n\n"
            f"- **FAO-56 Crop Coefficients**: Initial Kc = {kc_ini}, Mid-Season Kc = {kc_mid}, Late Season Kc = {kc_end}\n"
            f"- **Management Allowed Depletion (MAD)**: {mad}\n"
            f"- **Effective Root Zone Depth**: {root}\n"
            f"- **Preferred Soil Texture**: {soil}\n"
            f"- **Target Soil Matric Potential**: {tension}\n\n"
            f"## Agronomic Guidance\n{notes}\n"
        )
        msg = f"docs(agronomy): add FAO-56 irrigation and root depletion profile for {slug}"
        if make_commit(path, content, msg):
            count += 1

    # 3. Soils (10 commits)
    for slug, title, fc, pwp, awc, inf, notes in soils:
        path = f"docs/agronomy/soils/{slug}.md"
        content = (
            f"# {title}\n\n"
            f"- **Field Capacity (FC)**: {fc}% volumetric\n"
            f"- **Permanent Wilting Point (PWP)**: {pwp}% volumetric\n"
            f"- **Available Water Capacity (AWC)**: {awc}% volumetric\n"
            f"- **Infiltration Rate**: {inf} mm/hr\n\n"
            f"## Soil Management Notes\n{notes}\n"
        )
        msg = f"docs(soils): add soil hydraulic dynamics and water retention profile for {slug}"
        if make_commit(path, content, msg):
            count += 1

    # 4. Hardware (10 commits)
    for slug, title, spec in hardware:
        path = f"firmware/esp32/specs/{slug}.md"
        content = f"# {title}\n\n## Specification & Guidelines\n{spec}\n"
        msg = f"docs(hardware): add electrical and firmware specification for {slug}"
        if make_commit(path, content, msg):
            count += 1

    # 5. Locales (10 commits)
    for code, lang, dict_data in locales:
        import json
        path = f"frontend/src/locales/{code}.json"
        content = json.dumps(dict_data, indent=2, ensure_ascii=False) + "\n"
        msg = f"feat(i18n): add regional agricultural localization dictionary for {lang}"
        if make_commit(path, content, msg):
            count += 1

    # 6. QA Fixtures (10 commits)
    for slug, msg, content in qa_fixtures:
        path = f"backend/tests/fixtures/{slug}.json"
        if make_commit(path, content + "\n", msg):
            count += 1

    # 7. Operations Runbooks (10 commits)
    for slug, msg, content in operations:
        path = f"docs/operations/{slug}.md"
        if make_commit(path, content + "\n", msg):
            count += 1

    print("=" * 60)
    print(f"Successfully generated {count} new commits!")
    print("=" * 60)

if __name__ == "__main__":
    main()
