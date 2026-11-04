from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.entities import User, ApiApplication, Webhook

router = APIRouter(prefix="/developer", tags=["developer"])

class ApiAppResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    api_key_prefix: Optional[str]
    status: str

class ApiAppCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None

class WebhookResponse(BaseModel):
    id: str
    name: str
    target_url: str
    event_subscriptions: List[str]
    is_active: bool

class WebhookCreateRequest(BaseModel):
    name: str
    target_url: str
    secret_token: Optional[str] = "whsec_terranexus_demo"
    event_subscriptions: Optional[List[str]] = ["telemetry.ingested", "alert.triggered"]

@router.get("/applications", response_model=List[ApiAppResponse])
def list_applications(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    apps = db.query(ApiApplication).all()
    if not apps:
        return [
            ApiAppResponse(
                id="demo-app-001",
                name="Tether WDK Farm Finance Agent",
                description="Agentic finance connector for automated farm input payments and micro-escrow",
                api_key_prefix="tnx_live_a1b2",
                status="active"
            )
        ]
    return [
        ApiAppResponse(
            id=a.id,
            name=a.name,
            description=a.description,
            api_key_prefix=a.api_key_prefix or "tnx_live_****",
            status=a.status
        ) for a in apps
    ]

@router.post("/applications", response_model=ApiAppResponse)
def create_application(req: ApiAppCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    app = ApiApplication(
        organisation_id="a0000000-0000-0000-0000-000000000001",
        name=req.name,
        description=req.description,
        api_key_prefix="tnx_live_key",
        status="active"
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return ApiAppResponse(
        id=app.id,
        name=app.name,
        description=app.description,
        api_key_prefix=app.api_key_prefix,
        status=app.status
    )

@router.get("/webhooks", response_model=List[WebhookResponse])
def list_webhooks(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    webhooks = db.query(Webhook).all()
    if not webhooks:
        return [
            WebhookResponse(
                id="demo-wh-001",
                name="Field Operations Dispatcher",
                target_url="https://api.farmops.net/webhook/events",
                event_subscriptions=["telemetry.ingested", "alert.triggered"],
                is_active=True
            )
        ]
    return [
        WebhookResponse(
            id=w.id,
            name=w.name,
            target_url=w.target_url,
            event_subscriptions=w.event_subscriptions or [],
            is_active=w.is_active
        ) for w in webhooks
    ]

@router.post("/webhooks", response_model=WebhookResponse)
def create_webhook(req: WebhookCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    wh = Webhook(
        organisation_id="a0000000-0000-0000-0000-000000000001",
        name=req.name,
        target_url=req.target_url,
        secret_token=req.secret_token or "secret",
        event_subscriptions=req.event_subscriptions or [],
        is_active=True
    )
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return WebhookResponse(
        id=wh.id,
        name=wh.name,
        target_url=wh.target_url,
        event_subscriptions=wh.event_subscriptions or [],
        is_active=wh.is_active
    )
