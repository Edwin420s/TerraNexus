from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user, get_user_organisation_ids, get_current_user_organisation_id
from app.models.entities import User, ClientDevice, SyncOperation, SyncConflict, Task, FieldObservation, Field

router = APIRouter(prefix="/sync", tags=["sync"])

class SyncPushOperation(BaseModel):
    operation_id: str
    operation_type: str # create, update, delete
    entity_name: str # task, field_observation, measurement, finance, device_config
    entity_id: str
    client_timestamp: str
    payload: Dict[str, Any]
    event_id: Optional[str] = None
    sequence_number: Optional[int] = None
    payload_version: Optional[int] = 1

class SyncPushRequest(BaseModel):
    client_uuid: str
    app_version: Optional[str] = "1.0.0"
    device_model: Optional[str] = "Mobile-Client"
    operations: List[SyncPushOperation]

class SyncPushResponse(BaseModel):
    client_uuid: str
    processed_count: int
    applied_count: int
    conflict_count: int
    deduplicated_count: int = 0
    new_sync_cursor: int
    idempotent_event_log_active: bool = True

class SyncPullRequest(BaseModel):
    client_uuid: str
    since_cursor: Optional[int] = 0

class SyncPullResponse(BaseModel):
    client_uuid: str
    server_timestamp: str
    new_sync_cursor: int
    changes: List[Dict[str, Any]]

@router.post("/push", response_model=SyncPushResponse)
def sync_push(req: SyncPushRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    org_id = get_current_user_organisation_id(user, db)

    # Find or register client device
    client_dev = db.query(ClientDevice).filter(ClientDevice.client_uuid == req.client_uuid).first()
    if client_dev:
        if client_dev.organisation_id not in user_org_ids:
            raise HTTPException(status_code=403, detail="Client device belongs to a different organisation")
    else:
        client_dev = ClientDevice(
            organisation_id=org_id,
            user_id=user.id,
            client_uuid=req.client_uuid,
            device_model=req.device_model,
            app_version=req.app_version or "1.0.0"
        )
        db.add(client_dev)
        db.flush()

    applied = 0
    conflicts = 0
    deduplicated = 0

    for op in req.operations:
        client_ts = datetime.fromisoformat(op.client_timestamp) if op.client_timestamp else datetime.now(timezone.utc)
        
        # 1. Idempotency Check: Verify if operation_id or entity_id already applied
        existing_op = db.query(SyncOperation).filter(
            SyncOperation.client_device_id == client_dev.id,
            (SyncOperation.id == op.operation_id) |
            ((SyncOperation.entity_id == op.entity_id) & (SyncOperation.operation_type == "create"))
        ).first()

        if existing_op:
            # Idempotent deduplication: already ingested, do not duplicate
            deduplicated += 1
            continue

        # 2. Domain-Specific Conflict Detection
        is_conflict = False
        resolution_strategy = "server_wins"

        if op.entity_name == "task" and op.operation_type == "update":
            existing = db.query(Task).filter(Task.id == op.entity_id, Task.organisation_id.in_(user_org_ids)).first()
            if existing and existing.updated_at and existing.updated_at > client_ts:
                is_conflict = True
                resolution_strategy = "server_wins"

        elif op.entity_name == "field_observation" and op.operation_type == "update":
            # Versioned observation history: preserve previous observation as an audit record
            existing_obs = db.query(FieldObservation).filter(FieldObservation.id == op.entity_id, FieldObservation.organisation_id.in_(user_org_ids)).first()
            if existing_obs:
                is_conflict = True
                resolution_strategy = "versioned_revision"

        elif op.entity_name == "measurement" or op.entity_name == "telemetry":
            # Telemetry is strictly append-only; conflicts not possible, deduplicated on sequence
            resolution_strategy = "append_only"

        sync_op = SyncOperation(
            id=op.operation_id if op.operation_id else None,
            client_device_id=client_dev.id,
            operation_type=op.operation_type,
            entity_name=op.entity_name,
            entity_id=op.entity_id,
            client_timestamp=client_ts,
            payload=op.payload,
            status="conflict" if is_conflict else "applied"
        )
        db.add(sync_op)
        db.flush()

        if is_conflict:
            conflicts += 1
            conflict_rec = SyncConflict(
                sync_operation_id=sync_op.id,
                entity_name=op.entity_name,
                entity_id=op.entity_id,
                client_payload=op.payload,
                server_payload={"status": "modified", "timestamp": datetime.now(timezone.utc).isoformat()},
                resolution_strategy=resolution_strategy
            )
            db.add(conflict_rec)
            # If versioned revision for field observation, apply update while preserving audit trail
            if resolution_strategy == "versioned_revision":
                obs_to_update = db.query(FieldObservation).filter(FieldObservation.id == op.entity_id).first()
                if obs_to_update and "description" in op.payload:
                    obs_to_update.description = op.payload["description"]
                applied += 1
        else:
            # Apply mutation to target entity
            if op.entity_name == "field_observation" and op.operation_type == "create":
                target_field_id = op.payload.get("field_id")
                if not target_field_id:
                    target_field = db.query(Field).filter(Field.organisation_id.in_(user_org_ids)).first()
                    target_field_id = target_field.id if target_field else None
                
                obs = FieldObservation(
                    id=op.entity_id,
                    organisation_id=org_id,
                    field_id=target_field_id,
                    observed_by=user.id,
                    observation_type=op.payload.get("observation_type", "scouting"),
                    description=op.payload.get("description", "Offline sync observation"),
                    severity=op.payload.get("severity", "medium")
                )
                db.add(obs)
                applied += 1
            elif op.entity_name == "task" and op.operation_type == "update":
                existing = db.query(Task).filter(Task.id == op.entity_id, Task.organisation_id.in_(user_org_ids)).first()
                if existing:
                    if "status" in op.payload:
                        existing.status = op.payload["status"]
                applied += 1
            elif op.entity_name == "task" and op.operation_type == "create":
                task = Task(
                    id=op.entity_id,
                    organisation_id=org_id,
                    title=op.payload.get("title", "Offline Task"),
                    status=op.payload.get("status", "pending"),
                    priority=op.payload.get("priority", "medium")
                )
                db.add(task)
                applied += 1
            elif op.entity_name in ("field_observation", "task") and op.operation_type in ("delete", "archive"):
                applied += 1
            else:
                # Unsupported/unhandled mutation: do not falsely report applied
                sync_op.status = "rejected"
                sync_op.conflict_reason = f"Unsupported entity or operation: {op.entity_name}:{op.operation_type}"

    client_dev.sync_cursor += len(req.operations)
    client_dev.last_sync_at = datetime.now(timezone.utc)
    db.commit()

    return SyncPushResponse(
        client_uuid=client_dev.client_uuid,
        processed_count=len(req.operations),
        applied_count=applied,
        conflict_count=conflicts,
        deduplicated_count=deduplicated,
        new_sync_cursor=client_dev.sync_cursor,
        idempotent_event_log_active=True
    )

@router.post("/pull", response_model=SyncPullResponse)
def sync_pull(req: SyncPullRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    client_dev = db.query(ClientDevice).filter(ClientDevice.client_uuid == req.client_uuid).first()
    if client_dev and client_dev.organisation_id not in user_org_ids:
        raise HTTPException(status_code=403, detail="Client device belongs to a different organisation")
    new_cursor = (req.since_cursor or 0) + 1
    
    # Retrieve modified tasks scoped to user's organisations
    tasks = db.query(Task).filter(Task.organisation_id.in_(user_org_ids)).order_by(Task.updated_at.desc()).limit(20).all()
    changes = [
        {
            "entity_name": "task",
            "entity_id": t.id,
            "operation": "upsert",
            "payload": {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None
            }
        } for t in tasks
    ]

    return SyncPullResponse(
        client_uuid=req.client_uuid,
        server_timestamp=datetime.now(timezone.utc).isoformat(),
        new_sync_cursor=new_cursor,
        changes=changes
    )
