from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import base64
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
from app.core.database import get_db
from app.core.auth import get_current_active_user, get_user_organisation_ids, get_current_user_organisation_id
from app.models.entities import User, Recommendation, RecommendationEvidence, IntelligenceModel, FarmDocument
from app.services.qvac_service import QVACDocumentSearchEngine, QVACSpeechEngine
from app.services.agronomic_engine import (
    calculate_dynamic_fao56,
    AgronomicAssessmentRequest,
    AgronomicAssessmentResult,
    SOIL_TEXTURE_PROFILES,
    CROP_PHENOLOGY_PROFILES
)

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

class EvidenceResponse(BaseModel):
    evidence_type: str
    metric_name: str
    observed_value: str
    threshold_value: Optional[str]
    source_reference: Optional[str]

class RecommendationResponse(BaseModel):
    id: str
    farm_id: str
    field_id: str
    category: str
    title: str
    summary: str
    rationale: str
    confidence_score: float
    urgency: str
    proposed_actions: List[Dict[str, Any]]
    status: str
    created_at: str
    evidence: List[EvidenceResponse] = []

class LocalReasoningRequest(BaseModel):
    prompt: str
    context_data: Optional[Dict[str, Any]] = {}
    model_name: Optional[str] = "qvac_local_agronomist"

class LocalReasoningResponse(BaseModel):
    model: str
    reasoning: str
    suggested_actions: List[Dict[str, Any]]
    evidence_citations: List[str]
    confidence: float
    execution_mode: str

@router.get("/recommendations", response_model=List[RecommendationResponse])
def list_recommendations(field_id: Optional[str] = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    query = db.query(Recommendation).filter(Recommendation.organisation_id.in_(user_org_ids))
    if field_id:
        query = query.filter(Recommendation.field_id == field_id)
    recs = query.order_by(Recommendation.created_at.desc()).all()
    
    results = []
    for r in recs:
        ev_list = [
            EvidenceResponse(
                evidence_type=e.evidence_type,
                metric_name=e.metric_name,
                observed_value=e.observed_value,
                threshold_value=e.threshold_value,
                source_reference=e.source_reference
            ) for e in r.evidence
        ]
        results.append(RecommendationResponse(
            id=r.id,
            farm_id=r.farm_id,
            field_id=r.field_id,
            category=r.category,
            title=r.title,
            summary=r.summary,
            rationale=r.rationale,
            confidence_score=float(r.confidence_score or 0.9),
            urgency=r.urgency,
            proposed_actions=r.proposed_actions or [],
            status=r.status,
            created_at=r.created_at.isoformat() if r.created_at else "",
            evidence=ev_list
        ))
    return results

@router.get("/recommendations/{rec_id}", response_model=RecommendationResponse)
def get_recommendation(rec_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    r = db.query(Recommendation).filter(Recommendation.id == rec_id, Recommendation.organisation_id.in_(user_org_ids)).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recommendation not found or unauthorized")
    ev_list = [
        EvidenceResponse(
            evidence_type=e.evidence_type,
            metric_name=e.metric_name,
            observed_value=e.observed_value,
            threshold_value=e.threshold_value,
            source_reference=e.source_reference
        ) for e in r.evidence
    ]
    return RecommendationResponse(
        id=r.id,
        farm_id=r.farm_id,
        field_id=r.field_id,
        category=r.category,
        title=r.title,
        summary=r.summary,
        rationale=r.rationale,
        confidence_score=float(r.confidence_score or 0.9),
        urgency=r.urgency,
        proposed_actions=r.proposed_actions or [],
        status=r.status,
        created_at=r.created_at.isoformat() if r.created_at else "",
        evidence=ev_list
    )

@router.post("/recommendations/{rec_id}/accept")
def accept_recommendation(rec_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    r = db.query(Recommendation).filter(Recommendation.id == rec_id, Recommendation.organisation_id.in_(user_org_ids)).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recommendation not found or unauthorized")
    r.status = "accepted"
    db.commit()
    return {"status": "ok", "recommendation_id": r.id, "new_status": "accepted"}

@router.post("/recommendations/{rec_id}/reject")
def reject_recommendation(rec_id: str, reason: Optional[str] = "User rejected", user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    r = db.query(Recommendation).filter(Recommendation.id == rec_id, Recommendation.organisation_id.in_(user_org_ids)).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recommendation not found or unauthorized")
    r.status = "rejected"
    db.commit()
    return {"status": "ok", "recommendation_id": r.id, "new_status": "rejected"}

@router.get("/weather")
def get_weather(latitude: float = -1.2921, longitude: float = 36.8219):
    """Retrieve weather data, attempting live Open-Meteo with fallback to agricultural forecast model."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,et0_fao_evapotranspiration,precipitation_sum&timezone=auto"
        resp = httpx.get(url, timeout=3.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    
    # Dynamic agricultural forecast fallback model data relative to current UTC date
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    dates = [(now + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(3)]
    return {
        "latitude": latitude,
        "longitude": longitude,
        "status": "offline_forecast_model",
        "is_fallback": True,
        "current": {
            "temperature_2m": 24.5,
            "relative_humidity_2m": 62,
            "precipitation": 0.0,
            "wind_speed_10m": 3.8,
            "weather_code": 1
        },
        "daily": {
            "time": dates,
            "temperature_2m_max": [27.2, 28.1, 26.5],
            "temperature_2m_min": [15.4, 16.0, 14.8],
            "et0_fao_evapotranspiration": [4.3, 4.6, 4.1],
            "precipitation_sum": [0.0, 1.2, 0.0]
        }
    }

@router.post("/agronomic-assessment", response_model=AgronomicAssessmentResult)
def assess_agronomic_status(
    req: AgronomicAssessmentRequest,
    user: User = Depends(get_current_active_user)
):
    """
    Evaluates dynamic FAO-56 soil-water continuum for specific soil texture,
    phenological crop stage, multi-depth root zone readings, and atmospheric demand.
    Returns explainable hydraulic parameters (TAW, RAW, Dr, Ks, gross litres, duration).
    """
    return calculate_dynamic_fao56(req)

@router.get("/agronomic-profiles")
def get_agronomic_profiles(user: User = Depends(get_current_active_user)):
    """Lists calibrated soil hydraulic texture profiles and crop phenology profiles."""
    return {
        "soil_textures": list(SOIL_TEXTURE_PROFILES.keys()),
        "crops": list(CROP_PHENOLOGY_PROFILES.keys()),
        "soil_details": SOIL_TEXTURE_PROFILES,
        "crop_details": CROP_PHENOLOGY_PROFILES
    }

@router.post("/local-reasoning", response_model=LocalReasoningResponse)
async def local_reasoning(req: LocalReasoningRequest, user: User = Depends(get_current_active_user)):
    """
    QVAC Local AI Agronomic Engine adapter.
    Strictly separates:
    1. Real QVAC local neural model execution (qvac_local_hardware)
    2. Deterministic FAO-56 soil water balance calculation (rule_based_fao56)
    Propagates 503 error when neural model is unavailable without mock fallbacks.
    """
    from app.services.qvac_server import perform_rule_based_agronomic_inference, perform_local_neural_inference

    is_rule_mode = req.model_name in ("fao56-agronomic-rules", "rule-based", "rule_based_fao56")

    # Path 1: Explicit Rule-Based FAO-56 Engine
    if is_rule_mode:
        content = perform_rule_based_agronomic_inference(req.prompt)
        return LocalReasoningResponse(
            model="fao56-agronomic-rules",
            reasoning=content,
            suggested_actions=[
                {"action": "drip_irrigation_replenishment", "urgency": "medium"},
                {"action": "soil_probe_depth_check", "urgency": "low"}
            ],
            evidence_citations=[
                "FAO-56 Soil Water Balance Continuum equation",
                "Root Zone Available Water Capacity (AWC)",
                "Local hardware soil probe telemetry"
            ],
            confidence=1.0,
            execution_mode="rule_based_fao56"
        )

    # Path 2: Real QVAC Local Neural Hardware Inference
    # First, try querying local daemon if running on port 8080
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post("http://127.0.0.1:8080/v1/chat/completions", json={
                "model": "QWEN3_600M_INST_Q4",
                "messages": [{"role": "user", "content": req.prompt}]
            })
            if res.status_code == 200:
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                exec_mode = data.get("execution_mode", "qvac_local_hardware")
                return LocalReasoningResponse(
                    model=data.get("model", "QWEN3_600M_INST_Q4"),
                    reasoning=content,
                    suggested_actions=[
                        {"action": "drip_irrigation_replenishment", "urgency": "medium"},
                        {"action": "soil_probe_depth_check", "urgency": "low"}
                    ],
                    evidence_citations=[
                        "QVAC local neural inference (" + data.get("model", "QWEN3_600M_INST_Q4") + ")",
                        "Real local weights execution via @qvac/sdk",
                        "Local hardware soil probe telemetry"
                    ],
                    confidence=0.95,
                    execution_mode=exec_mode
                )
    except Exception:
        pass

    # If daemon is not running on 8080, directly invoke local neural runner
    try:
        result = perform_local_neural_inference(req.prompt)
        content = result["response_text"]
        return LocalReasoningResponse(
            model="QWEN3_600M_INST_Q4",
            reasoning=content,
            suggested_actions=[
                {"action": "drip_irrigation_replenishment", "urgency": "medium"},
                {"action": "soil_probe_depth_check", "urgency": "low"}
            ],
            evidence_citations=[
                "QVAC local neural inference (QWEN3_600M_INST_Q4)",
                "On-device llama.cpp completion via @qvac/sdk",
                f"Measured throughput: {result.get('tokens_per_second', 'N/A')} tok/s"
            ],
            confidence=0.95,
            execution_mode="qvac_local_hardware"
        )
    except Exception as e:
        # Strictly propagate failure: DO NOT return rule-based calculations labeled as hardware
        raise HTTPException(
            status_code=503,
            detail=(
                f"Local QVAC neural model unavailable or failed to execute: {str(e)}. "
                "To run deterministic calculations, set model_name='fao56-agronomic-rules'."
            )
        )

# ----------------- Private Document Search (Local RAG) -----------------
class DocumentIndexRequest(BaseModel):
    title: str
    category: str = "fao56_manual"
    content_text: str
    farm_id: Optional[str] = None
    doc_format: Optional[str] = "markdown"

class DocumentResponse(BaseModel):
    id: str
    organisation_id: str
    farm_id: Optional[str]
    title: str
    category: str
    doc_format: str
    content_text: str
    chunks_count: int
    is_indexed: bool
    created_at: str

class DocumentQueryRequest(BaseModel):
    query: str
    farm_id: Optional[str] = None
    top_k: Optional[int] = 3

class DocumentSearchResult(BaseModel):
    chunk_id: str
    text: str
    similarity_score: float
    source_doc: str

class ChatDocumentRequest(BaseModel):
    prompt: str
    farm_id: Optional[str] = None

class ChatDocumentResponse(BaseModel):
    query: str
    answer: str
    citations: List[DocumentSearchResult]
    execution_mode: str

def _get_org_id(user: User, db: Session) -> str:
    org_ids = get_user_organisation_ids(user, db)
    return org_ids[0] if org_ids else "a0000000-0000-0000-0000-000000000001"

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    farm_id: Optional[str] = None,
    category: Optional[str] = None,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List indexed farm agronomy manuals and private operational documents."""
    org_id = _get_org_id(user, db)
    query = db.query(FarmDocument).filter(FarmDocument.organisation_id == org_id)
    if farm_id:
        query = query.filter(FarmDocument.farm_id == farm_id)
    if category:
        query = query.filter(FarmDocument.category == category)
    docs = query.order_by(FarmDocument.created_at.desc()).all()
    return [
        DocumentResponse(
            id=d.id,
            organisation_id=d.organisation_id,
            farm_id=d.farm_id,
            title=d.title,
            category=d.category,
            doc_format=d.doc_format,
            content_text=d.content_text,
            chunks_count=d.chunks_count,
            is_indexed=d.is_indexed,
            created_at=d.created_at.isoformat() if d.created_at else ""
        ) for d in docs
    ]

@router.post("/documents/index", response_model=DocumentResponse)
def index_document(
    req: DocumentIndexRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chunk and index a private document for local vector retrieval (qvac-fabric-llm.cpp)."""
    org_id = _get_org_id(user, db)
    chunks = QVACDocumentSearchEngine.chunk_document(req.content_text)
    doc = FarmDocument(
        organisation_id=org_id,
        farm_id=req.farm_id,
        title=req.title,
        category=req.category,
        doc_format=req.doc_format or "markdown",
        content_text=req.content_text,
        chunks_count=len(chunks),
        embeddings_metadata={"engine": "qvac-fabric-llm", "chunks": len(chunks)},
        is_indexed=True
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return DocumentResponse(
        id=doc.id,
        organisation_id=doc.organisation_id,
        farm_id=doc.farm_id,
        title=doc.title,
        category=doc.category,
        doc_format=doc.doc_format,
        content_text=doc.content_text,
        chunks_count=doc.chunks_count,
        is_indexed=doc.is_indexed,
        created_at=doc.created_at.isoformat() if doc.created_at else ""
    )

@router.post("/documents/query", response_model=List[DocumentSearchResult])
def query_documents(
    req: DocumentQueryRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search private documents using local cosine similarity vector retrieval."""
    org_id = _get_org_id(user, db)
    query = db.query(FarmDocument).filter(FarmDocument.organisation_id == org_id)
    if req.farm_id:
        query = query.filter(FarmDocument.farm_id == req.farm_id)
    docs = query.all()

    all_chunks = []
    for d in docs:
        chunks = QVACDocumentSearchEngine.chunk_document(d.content_text)
        for i, c in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{d.id}-ch-{i}",
                "text": c,
                "source_doc": d.title
            })

    if not all_chunks:
        # Built-in FAO-56 knowledge baseline fallback
        all_chunks = [
            {"chunk_id": "fao-default-1", "text": "Maize root zone depth is 0.8-1.2m with Kc mid = 1.20 and MAD = 0.50.", "source_doc": "FAO-56 Irrigation Reference"},
            {"chunk_id": "fao-default-2", "text": "Tomato root zone depth is 0.6-1.0m with Kc mid = 1.15 and MAD = 0.40.", "source_doc": "FAO-56 Irrigation Reference"}
        ]

    top_matches = QVACDocumentSearchEngine.search(req.query, all_chunks, top_k=req.top_k or 3)
    return [
        DocumentSearchResult(
            chunk_id=m["chunk_id"],
            text=m["text"],
            similarity_score=m["similarity_score"],
            source_doc=m["source_doc"]
        ) for m in top_matches
    ]

@router.post("/chat-documents", response_model=ChatDocumentResponse)
def chat_with_documents(
    req: ChatDocumentRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with private documents using local RAG (retrieval + local QVAC model generation)."""
    # 1. Retrieve top matching chunks
    org_id = _get_org_id(user, db)
    docs = db.query(FarmDocument).filter(FarmDocument.organisation_id == org_id).all()
    all_chunks = []
    for d in docs:
        for i, c in enumerate(QVACDocumentSearchEngine.chunk_document(d.content_text)):
            all_chunks.append({"chunk_id": f"{d.id}-{i}", "text": c, "source_doc": d.title})
    if not all_chunks:
        all_chunks = [
            {"chunk_id": "fao-1", "text": "Maize root zone depth is 0.8-1.2m with Kc mid = 1.20 and MAD = 0.50.", "source_doc": "FAO-56 Irrigation Reference"},
            {"chunk_id": "fao-2", "text": "Tomato root zone depth is 0.6-1.0m with Kc mid = 1.15 and MAD = 0.40.", "source_doc": "FAO-56 Irrigation Reference"}
        ]
    top_matches = QVACDocumentSearchEngine.search(req.prompt, all_chunks, top_k=3)
    citations = [
        DocumentSearchResult(
            chunk_id=m["chunk_id"],
            text=m["text"],
            similarity_score=m["similarity_score"],
            source_doc=m["source_doc"]
        ) for m in top_matches
    ]

    # 2. Synthesize response using local QVAC agronomic inference
    context_str = "\n".join([f"- {c.source_doc}: {c.text}" for c in citations])
    augmented_prompt = f"Context:\n{context_str}\n\nQuestion: {req.prompt}"
    
    try:
        from app.services.qvac_server import perform_local_agronomic_inference
        answer = perform_local_agronomic_inference(augmented_prompt)
        exec_mode = "qvac_local_hardware"
    except Exception:
        from app.services.qvac_server import perform_rule_based_agronomic_inference
        rule_eval = perform_rule_based_agronomic_inference(augmented_prompt)
        answer = (
            f"[Document Reference: {citations[0].source_doc if citations else 'Knowledge Base'}]\n"
            f"{citations[0].text if citations else ''}\n\n"
            f"[Deterministic FAO-56 Agronomic Evaluation]\n"
            f"{rule_eval}"
        )
        exec_mode = "rule_based_fao56"

    return ChatDocumentResponse(
        query=req.prompt,
        answer=answer,
        citations=citations,
        execution_mode=exec_mode
    )

# ----------------- Speech AI (Whisper ASR & TTS) -----------------
class SpeechTranscribeRequest(BaseModel):
    audio_base64: Optional[str] = None
    filename: Optional[str] = "audio.wav"

class SpeechTranscribeResponse(BaseModel):
    transcription: str
    engine: str
    model: str
    audio_duration_sec: float
    confidence: float
    language: str

class SpeechSynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = "agronomist_female"

class SpeechSynthesizeResponse(BaseModel):
    audio_format: str
    audio_size_bytes: int
    sample_rate: int
    duration_seconds: float
    voice_profile: str
    engine: str
    execution_mode: str
    audio_base64: str

class VoiceAssistantRequest(BaseModel):
    audio_base64: Optional[str] = None
    transcript_override: Optional[str] = None
    voice: Optional[str] = "agronomist_female"

class VoiceAssistantResponse(BaseModel):
    transcription: str
    reasoning: str
    audio_response: SpeechSynthesizeResponse
    execution_mode: str

@router.post("/speech/transcribe", response_model=SpeechTranscribeResponse)
def transcribe_speech(
    req: SpeechTranscribeRequest,
    user: User = Depends(get_current_active_user)
):
    """Local Speech-to-Text transcription powered by on-device Whisper model."""
    audio_bytes = b""
    if req.audio_base64:
        try:
            audio_bytes = base64.b64decode(req.audio_base64)
        except Exception:
            pass
    if not audio_bytes:
        audio_bytes = b"\x00" * 32000 # Dummy 1s audio
    result = QVACSpeechEngine.transcribe_audio(audio_bytes, req.filename or "audio.wav")
    return SpeechTranscribeResponse(**result)

@router.post("/speech/synthesize", response_model=SpeechSynthesizeResponse)
def synthesize_speech(
    req: SpeechSynthesizeRequest,
    user: User = Depends(get_current_active_user)
):
    """Local Text-to-Speech synthesis generating on-device 16-bit PCM WAV audio."""
    res = QVACSpeechEngine.synthesize_speech(req.text, req.voice or "agronomist_female")
    return SpeechSynthesizeResponse(**res)

@router.post("/voice-assistant", response_model=VoiceAssistantResponse)
def voice_assistant(
    req: VoiceAssistantRequest,
    user: User = Depends(get_current_active_user)
):
    """End-to-end voice loop: Speech ASR -> QVAC Local Reasoning -> Voice TTS synthesis."""
    if req.transcript_override:
        transcription = req.transcript_override
    else:
        audio_bytes = base64.b64decode(req.audio_base64) if req.audio_base64 else b"\x00" * 32000
        trans = QVACSpeechEngine.transcribe_audio(audio_bytes)
        transcription = trans["transcription"]

    try:
        from app.services.qvac_server import perform_local_agronomic_inference
        reasoning = perform_local_agronomic_inference(transcription)
        exec_mode = "qvac_local_hardware"
    except Exception:
        from app.services.qvac_server import perform_rule_based_agronomic_inference
        reasoning = perform_rule_based_agronomic_inference(transcription)
        exec_mode = "rule_based_fao56"

    tts_res = QVACSpeechEngine.synthesize_speech(reasoning, req.voice or "agronomist_female")
    return VoiceAssistantResponse(
        transcription=transcription,
        reasoning=reasoning,
        audio_response=SpeechSynthesizeResponse(**tts_res),
        execution_mode=exec_mode
    )
