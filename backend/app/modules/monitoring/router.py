from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user, get_user_organisation_ids, get_current_user_organisation_id
from app.models.entities import User, Alert, AlertRule, Notification, Farm

router = APIRouter(prefix="", tags=["monitoring"])

class AlertResponse(BaseModel):
    id: str
    farm_id: str
    field_id: Optional[str]
    title: str
    message: str
    severity: str
    status: str
    triggered_at: str
    acknowledged_at: Optional[str]
    resolved_at: Optional[str]

class AlertRuleResponse(BaseModel):
    id: str
    farm_id: str
    name: str
    rule_type: str
    measurement_type: Optional[str]
    conditions: Dict[str, Any]
    severity: str
    is_active: bool

class AlertRuleCreateRequest(BaseModel):
    farm_id: str
    field_id: Optional[str] = None
    name: str
    rule_type: str
    measurement_type: Optional[str] = None
    conditions: Dict[str, Any]
    severity: Optional[str] = "warning"
    channels: Optional[List[str]] = ["in_app"]

class NotificationResponse(BaseModel):
    id: str
    title: str
    body: str
    category: str
    is_read: bool
    created_at: str

@router.get("/alerts", response_model=List[AlertResponse])
def list_alerts(status: Optional[str] = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    query = db.query(Alert).filter(Alert.organisation_id.in_(user_org_ids))
    if status:
        query = query.filter(Alert.status == status)
    alerts = query.order_by(Alert.triggered_at.desc()).all()
    return [
        AlertResponse(
            id=a.id,
            farm_id=a.farm_id,
            field_id=a.field_id,
            title=a.title,
            message=a.message,
            severity=a.severity,
            status=a.status,
            triggered_at=a.triggered_at.isoformat() if a.triggered_at else "",
            acknowledged_at=a.acknowledged_at.isoformat() if a.acknowledged_at else None,
            resolved_at=a.resolved_at.isoformat() if a.resolved_at else None
        ) for a in alerts
    ]

@router.post("/alerts/{alert_id}/ack")
def acknowledge_alert(alert_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.organisation_id not in user_org_ids:
        raise HTTPException(status_code=403, detail="Unauthorized to acknowledge alert from another organisation")
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by = user.id
    db.commit()
    return {"status": "ok", "alert_id": alert.id, "new_status": alert.status}

@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: str, notes: Optional[str] = "Resolved by operator", user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.organisation_id not in user_org_ids:
        raise HTTPException(status_code=403, detail="Unauthorized to resolve alert from another organisation")
    alert.status = "resolved"
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by = user.id
    alert.resolution_notes = notes
    db.commit()
    return {"status": "ok", "alert_id": alert.id, "new_status": alert.status}

@router.get("/alert-rules", response_model=List[AlertRuleResponse])
def list_alert_rules(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    rules = db.query(AlertRule).filter(AlertRule.organisation_id.in_(user_org_ids)).all()
    return [
        AlertRuleResponse(
            id=r.id,
            farm_id=r.farm_id,
            name=r.name,
            rule_type=r.rule_type,
            measurement_type=r.measurement_type,
            conditions=r.conditions or {},
            severity=r.severity,
            is_active=r.is_active
        ) for r in rules
    ]

@router.post("/alert-rules", response_model=AlertRuleResponse)
def create_alert_rule(req: AlertRuleCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    farm = db.query(Farm).filter(Farm.id == req.farm_id, Farm.organisation_id.in_(user_org_ids)).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")

    rule = AlertRule(
        organisation_id=farm.organisation_id,
        farm_id=req.farm_id,
        field_id=req.field_id,
        name=req.name,
        rule_type=req.rule_type,
        measurement_type=req.measurement_type,
        conditions=req.conditions,
        severity=req.severity or "warning",
        channels=req.channels or ["in_app"],
        is_active=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return AlertRuleResponse(
        id=rule.id,
        farm_id=rule.farm_id,
        name=rule.name,
        rule_type=rule.rule_type,
        measurement_type=rule.measurement_type,
        conditions=rule.conditions or {},
        severity=rule.severity,
        is_active=rule.is_active
    )

@router.get("/notifications", response_model=List[NotificationResponse])
def list_notifications(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(20).all()
    if not notifs:
        return [
            NotificationResponse(
                id="demo-notif-1",
                title="Irrigation Recommendation Generated",
                body="New advisory for Greenhouse Tomatoes: 45 min drip cycle proposed.",
                category="recommendation",
                is_read=False,
                created_at=datetime.now(timezone.utc).isoformat()
            )
        ]
    return [
        NotificationResponse(
            id=n.id,
            title=n.title,
            body=n.body,
            category=n.category,
            is_read=n.is_read,
            created_at=n.created_at.isoformat() if n.created_at else ""
        ) for n in notifs
    ]
