import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_intel_001_weather_feed():
    """Verify local weather conditions feed returns climate metrics."""
    weather_resp = client.get("/api/v1/intelligence/weather")
    assert weather_resp.status_code == 200
    data = weather_resp.json()
    assert "current" in data or "daily" in data or "temperature_2m" in str(data)

def test_tc_intel_002_recommendations_and_evidence():
    """Verify agronomic recommendations listing, evidence metrics, and accept/reject."""
    recs_resp = client.get("/api/v1/intelligence/recommendations")
    assert recs_resp.status_code == 200
    recs = recs_resp.json()
    assert len(recs) > 0
    rec = recs[0]
    rec_id = rec["id"]
    assert "summary" in rec
    assert "evidence" in rec

    # Fetch specific recommendation
    single_resp = client.get(f"/api/v1/intelligence/recommendations/{rec_id}")
    assert single_resp.status_code == 200
    assert single_resp.json()["id"] == rec_id

    # Accept recommendation (no body)
    accept_resp = client.post(f"/api/v1/intelligence/recommendations/{rec_id}/accept")
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "ok"

def test_tc_intel_003_recommendation_rejection():
    """Verify rejection of agronomic recommendation with documented reason."""
    recs = client.get("/api/v1/intelligence/recommendations").json()
    rec_id = recs[-1]["id"]

    reject_resp = client.post(f"/api/v1/intelligence/recommendations/{rec_id}/reject?reason=Rain+expected")
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "ok"

def test_tc_intel_004_local_qvac_reasoning_offline_fallback():
    """Verify local offline reasoning engine adapter returns agronomic guidance in qvac_local_hardware mode."""
    req_payload = {
        "prompt": "Evaluate irrigation necessity for maize at mid season given 18% soil moisture.",
        "context_data": {
            "crop": "Maize",
            "growth_stage": "mid_season",
            "soil_moisture_pct": 18.2
        },
        "model_name": "qvac-agronomist-7b"
    }
    resp = client.post("/api/v1/intelligence/local-reasoning", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "reasoning" in data
    assert "suggested_actions" in data
    assert data["model"] == "qvac-agronomist-7b"
    assert data["execution_mode"] == "qvac_local_hardware"
    assert "Maize" in data["reasoning"]

def test_tc_intel_005_wifi_off_offline_hardware_reasoning():
    """Verify 100% offline local hardware execution when all external network is severed."""
    req_payload = {
        "prompt": "Evaluate Tomato greenhouse soil moisture at 16.2% with root zone depletion assessment."
    }
    resp = client.post("/api/v1/intelligence/local-reasoning", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["execution_mode"] == "qvac_local_hardware"
    assert "Tomato" in data["reasoning"]
    assert "DEFICIT_TRIGGERED" in data["reasoning"]

def test_tc_qvac_006_farm_document_rag_retrieval():
    """Verify private document indexing and local cosine similarity retrieval (qvac-fabric-llm.cpp)."""
    # 1. Verify seeded FAO-56 manual exists
    docs_resp = client.get("/api/v1/intelligence/documents")
    assert docs_resp.status_code == 200
    docs = docs_resp.json()
    assert len(docs) > 0
    assert any("FAO-56" in d["title"] for d in docs)

    # 2. Index custom private agronomic handbook
    new_doc_payload = {
        "title": "Avocado Hass Irrigation and Root Phytophthora Defense",
        "category": "agronomy_guide",
        "content_text": (
            "# Avocado Water Management\n\n"
            "Avocado trees are sensitive to both water stress and waterlogging. "
            "Root depth is shallow (0.4 - 0.7m). Optimal soil tension is -25 to -35 kPa. "
            "Over-irrigation induces Phytophthora cinnamomi root rot. "
            "Drip pulse irrigation is mandatory during fruit sizing."
        )
    }
    index_resp = client.post("/api/v1/intelligence/documents/index", json=new_doc_payload)
    assert index_resp.status_code == 200
    created_doc = index_resp.json()
    assert created_doc["title"] == new_doc_payload["title"]
    assert created_doc["chunks_count"] >= 1
    assert created_doc["is_indexed"] is True

    # 3. Query documents via local cosine similarity vector retrieval
    query_payload = {"query": "What is the optimal soil tension and root depth for avocado?", "top_k": 2}
    search_resp = client.post("/api/v1/intelligence/documents/query", json=query_payload)
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) > 0
    assert results[0]["similarity_score"] > 0.0
    assert "Avocado" in results[0]["text"]

    # 4. Chat with private documents via local RAG
    chat_resp = client.post("/api/v1/intelligence/chat-documents", json={"prompt": "Explain avocado irrigation guidelines."})
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "answer" in chat_data
    assert len(chat_data["citations"]) > 0
    assert chat_data["execution_mode"] == "qvac_local_hardware"

def test_tc_qvac_007_local_speech_transcription_and_synthesis():
    """Verify on-device Whisper speech-to-text and TTS audio synthesis (qvac-fabric-speech.cpp)."""
    # 1. Transcribe audio
    trans_resp = client.post("/api/v1/intelligence/speech/transcribe", json={"filename": "field_query.wav"})
    assert trans_resp.status_code == 200
    trans_data = trans_resp.json()
    assert "transcription" in trans_data
    assert trans_data["engine"] == "qvac-fabric-speech-whisper"
    assert trans_data["confidence"] > 0.9

    # 2. Synthesize spoken audio WAV
    tts_payload = {"text": "Soil moisture is 18.5%. Drip irrigation replenishment recommended.", "voice": "agronomist_female"}
    tts_resp = client.post("/api/v1/intelligence/speech/synthesize", json=tts_payload)
    assert tts_resp.status_code == 200
    tts_data = tts_resp.json()
    assert tts_data["audio_format"] == "audio/wav"
    assert tts_data["audio_size_bytes"] > 44
    assert len(tts_data["audio_base64"]) > 0
    assert tts_data["execution_mode"] == "qvac_local_hardware"

    # 3. Voice assistant loop (speech in -> LLM reasoning -> voice out)
    va_resp = client.post("/api/v1/intelligence/voice-assistant", json={"transcript_override": "Evaluate tomato greenhouse soil moisture."})
    assert va_resp.status_code == 200
    va_data = va_resp.json()
    assert va_data["transcription"] == "Evaluate tomato greenhouse soil moisture."
    assert "reasoning" in va_data
    assert va_data["audio_response"]["audio_format"] == "audio/wav"
    assert len(va_data["audio_response"]["audio_base64"]) > 0

def test_tc_wdk_008_agentic_finance_human_approval_lifecycle():
    """Verify Tether WDK self-custodial USD₮ wallet and MANDATORY HUMAN APPROVAL gates."""
    # 1. Get wallet summary
    wallet_resp = client.get("/api/v1/finance/wallet")
    assert wallet_resp.status_code == 200
    wallet = wallet_resp.json()
    assert wallet["currency"] == "USD₮"
    assert wallet["security"]["self_custodial"] is True
    assert wallet["security"]["human_approval_enforced"] is True
    assert wallet["balances"]["available_usdt"] > 0

    # 2. Verify seeded pending disbursement
    pmts_resp = client.get("/api/v1/finance/payments")
    assert pmts_resp.status_code == 200
    pmts = pmts_resp.json()
    assert len(pmts) > 0

    # 3. Agent prepares automated procurement payment (must be pending_approval)
    prep_payload = {
        "purpose": "automated_solenoid_valve_replacement",
        "amount_usdt": 85.00,
        "recipient_address": "0x44B...AgriTechSolutions",
        "description": "Procurement of 24VAC 1-inch solenoid valve for greenhouse zone Z-GH2.",
        "agent_reasoning": "Solenoid coil resistance anomalous. Agent recommends ordering replacement before scheduled fertigation."
    }
    prep_resp = client.post("/api/v1/finance/payments/prepare", json=prep_payload)
    assert prep_resp.status_code == 200
    new_pmt = prep_resp.json()
    pmt_id = new_pmt["id"]
    assert new_pmt["status"] == "pending_approval"
    assert new_pmt["requires_human_approval"] is True
    assert new_pmt["transaction_hash"] is None

    # 4. Operator approves payment (Human Gate)
    approve_resp = client.post(f"/api/v1/finance/payments/{pmt_id}/approve")
    assert approve_resp.status_code == 200
    approved_pmt = approve_resp.json()
    assert approved_pmt["status"] == "broadcasted"
    assert approved_pmt["transaction_hash"].startswith("0x")
    assert approved_pmt["approved_by"] is not None

    # 5. Agent prepares another payment and operator rejects
    prep_reject_resp = client.post("/api/v1/finance/payments/prepare", json={
        "purpose": "unplanned_chemical_pesticide",
        "amount_usdt": 220.00,
        "recipient_address": "0x999...AgroChem",
        "description": "Broad spectrum synthetic insecticide restock."
    })
    reject_id = prep_reject_resp.json()["id"]

    reject_resp = client.post(f"/api/v1/finance/payments/{reject_id}/reject", json={"reason": "Organic certification forbids this chemical."})
    assert reject_resp.status_code == 200
    rejected_pmt = reject_resp.json()
    assert rejected_pmt["status"] == "rejected"
    assert "Organic certification" in rejected_pmt["description"]

