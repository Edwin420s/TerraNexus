"""
Tether WDK Agentic Finance Module Router (Week 2 Track)
Provides self-custodial USD₮ wallet management, automated input procurement preparation,
and MANDATORY HUMAN APPROVAL gates for every financial disbursement.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user, get_current_user_organisation_id, get_user_organisation_ids
from app.models.entities import User, AgentPayment, Membership
from app.services.qvac_service import TetherWDKFinanceAgent

router = APIRouter(prefix="/finance", tags=["finance"])

# Pydantic Schemas
class WalletBalances(BaseModel):
    available_usdt: float
    allocated_escrow_usdt: float
    total_usdt: float

class WalletSecurity(BaseModel):
    self_custodial: bool
    human_approval_enforced: bool
    max_unattended_allowance_usdt: float

class WalletSummaryResponse(BaseModel):
    wallet_address: str
    currency: str
    supported_chains: List[str]
    active_chain: str
    balances: WalletBalances
    security: WalletSecurity

class PreparePaymentRequest(BaseModel):
    purpose: str = Field(..., description="E.g., automated_drip_filter_procurement, soluble_fertilizer_restock")
    amount_usdt: float = Field(..., gt=0, description="Amount in USD₮ stablecoin")
    recipient_address: str = Field(..., description="Target vendor / supplier wallet address")
    description: Optional[str] = "Automated agricultural input replenishment proposal"
    agent_reasoning: Optional[str] = "Telemetry indicates threshold breach requiring automated replenishment."
    chain: Optional[str] = "Polygon"
    farm_id: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    organisation_id: str
    farm_id: Optional[str]
    wallet_address: str
    recipient_address: str
    amount_usdt: float
    currency: str
    chain: str
    purpose: str
    description: Optional[str]
    agent_reasoning: Optional[str]
    status: str
    requires_human_approval: bool
    approved_by: Optional[str]
    approved_at: Optional[str]
    transaction_hash: Optional[str]
    ledger_mode: str = "testnet_sandbox_proposal"
    created_at: str

class RejectPaymentRequest(BaseModel):
    reason: Optional[str] = "Operator declined payment request"

def _get_org_id(user: User, db: Session) -> str:
    org_id = get_current_user_organisation_id(user, db)
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have an active organisation membership"
        )
    return org_id

def check_finance_role(user: User, org_id: str, db: Session):
    mem = db.query(Membership).filter(
        Membership.user_id == user.id,
        Membership.organisation_id == org_id,
        Membership.status == "active"
    ).first()
    if not mem or mem.role not in ("owner", "admin", "finance", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Financial operations require owner, admin, or finance role"
        )

@router.get("/wallet", response_model=WalletSummaryResponse)
def get_wallet(user: User = Depends(get_current_active_user)):
    """Retrieve self-custodial Tether USD₮ wallet details and security policies."""
    summary = TetherWDKFinanceAgent.get_wallet_summary()
    return WalletSummaryResponse(**summary)

@router.get("/payments", response_model=List[PaymentResponse])
def list_payments(
    farm_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List agentic finance disbursements and pending approval requests."""
    org_id = _get_org_id(user, db)
    query = db.query(AgentPayment).filter(AgentPayment.organisation_id == org_id)
    if farm_id:
        query = query.filter(AgentPayment.farm_id == farm_id)
    if status_filter:
        query = query.filter(AgentPayment.status == status_filter)
    
    payments = query.order_by(AgentPayment.created_at.desc()).all()
    results = []
    for p in payments:
        results.append(PaymentResponse(
            id=p.id,
            organisation_id=p.organisation_id,
            farm_id=p.farm_id,
            wallet_address=p.wallet_address,
            recipient_address=p.recipient_address,
            amount_usdt=float(p.amount_usdt),
            currency=p.currency,
            chain=p.chain,
            purpose=p.purpose,
            description=p.description,
            agent_reasoning=p.agent_reasoning,
            status=p.status,
            requires_human_approval=p.requires_human_approval,
            approved_by=p.approved_by,
            approved_at=p.approved_at.isoformat() if p.approved_at else None,
            transaction_hash=p.transaction_hash,
            created_at=p.created_at.isoformat() if p.created_at else ""
        ))
    return results

@router.post("/payments/prepare", response_model=PaymentResponse)
def prepare_payment(
    req: PreparePaymentRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    AI Agent prepares an automated procurement proposal.
    Enforces MANDATORY HUMAN APPROVAL by persisting in 'pending_approval' status.
    """
    org_id = _get_org_id(user, db)
    payment = AgentPayment(
        organisation_id=org_id,
        farm_id=req.farm_id,
        wallet_address="0x71C...TetherFarmVault",
        recipient_address=req.recipient_address,
        amount_usdt=req.amount_usdt,
        currency="USD₮",
        chain=req.chain or "Polygon",
        purpose=req.purpose,
        description=req.description,
        agent_reasoning=req.agent_reasoning,
        status="pending_approval",
        requires_human_approval=True
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentResponse(
        id=payment.id,
        organisation_id=payment.organisation_id,
        farm_id=payment.farm_id,
        wallet_address=payment.wallet_address,
        recipient_address=payment.recipient_address,
        amount_usdt=float(payment.amount_usdt),
        currency=payment.currency,
        chain=payment.chain,
        purpose=payment.purpose,
        description=payment.description,
        agent_reasoning=payment.agent_reasoning,
        status=payment.status,
        requires_human_approval=payment.requires_human_approval,
        approved_by=payment.approved_by,
        approved_at=payment.approved_at.isoformat() if payment.approved_at else None,
        transaction_hash=payment.transaction_hash,
        created_at=payment.created_at.isoformat() if payment.created_at else ""
    )

@router.post("/payments/{payment_id}/approve", response_model=PaymentResponse)
def approve_payment(
    payment_id: str,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    HUMAN OPERATOR APPROVAL GATE:
    Operator explicitly signs off on payment.
    Requires owner, admin, or finance role within tenant organisation.
    Broadcasts simulated testnet / sandbox transaction proposal.
    """
    org_id = _get_org_id(user, db)
    check_finance_role(user, org_id, db)

    payment = db.query(AgentPayment).filter(
        AgentPayment.id == payment_id,
        AgentPayment.organisation_id == org_id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment request not found")

    if payment.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Payment already in '{payment.status}' state")

    # Execute human approval with explicit testnet sandbox proposal labelling
    tx_hash = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex}"[:66]
    now = datetime.now(timezone.utc)
    payment.status = "broadcasted"
    payment.approved_by = user.id
    payment.approved_at = now
    payment.transaction_hash = tx_hash
    payment.description = f"{payment.description or ''} [Simulated Sandbox Ledger Proposal]".strip()

    db.commit()
    db.refresh(payment)

    return PaymentResponse(
        id=payment.id,
        organisation_id=payment.organisation_id,
        farm_id=payment.farm_id,
        wallet_address=payment.wallet_address,
        recipient_address=payment.recipient_address,
        amount_usdt=float(payment.amount_usdt),
        currency=payment.currency,
        chain=payment.chain,
        purpose=payment.purpose,
        description=payment.description,
        agent_reasoning=payment.agent_reasoning,
        status=payment.status,
        requires_human_approval=payment.requires_human_approval,
        approved_by=payment.approved_by,
        approved_at=payment.approved_at.isoformat() if payment.approved_at else None,
        transaction_hash=payment.transaction_hash,
        ledger_mode="testnet_sandbox_proposal",
        created_at=payment.created_at.isoformat() if payment.created_at else ""
    )

@router.post("/payments/{payment_id}/reject", response_model=PaymentResponse)
def reject_payment(
    payment_id: str,
    req: RejectPaymentRequest = RejectPaymentRequest(),
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Human operator rejects proposed disbursement."""
    org_id = _get_org_id(user, db)
    check_finance_role(user, org_id, db)

    payment = db.query(AgentPayment).filter(
        AgentPayment.id == payment_id,
        AgentPayment.organisation_id == org_id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment request not found")

    if payment.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Payment already in '{payment.status}' state")

    payment.status = "rejected"
    payment.description = f"{payment.description or ''} [Rejected: {req.reason}]".strip()
    db.commit()
    db.refresh(payment)

    return PaymentResponse(
        id=payment.id,
        organisation_id=payment.organisation_id,
        farm_id=payment.farm_id,
        wallet_address=payment.wallet_address,
        recipient_address=payment.recipient_address,
        amount_usdt=float(payment.amount_usdt),
        currency=payment.currency,
        chain=payment.chain,
        purpose=payment.purpose,
        description=payment.description,
        agent_reasoning=payment.agent_reasoning,
        status=payment.status,
        requires_human_approval=payment.requires_human_approval,
        approved_by=payment.approved_by,
        approved_at=payment.approved_at.isoformat() if payment.approved_at else None,
        transaction_hash=payment.transaction_hash,
        ledger_mode="testnet_sandbox_proposal",
        created_at=payment.created_at.isoformat() if payment.created_at else ""
    )
    payment.description = f"{payment.description or ''} [Rejected: {req.reason}]".strip()
    db.commit()
    db.refresh(payment)

    return PaymentResponse(
        id=payment.id,
        organisation_id=payment.organisation_id,
        farm_id=payment.farm_id,
        wallet_address=payment.wallet_address,
        recipient_address=payment.recipient_address,
        amount_usdt=float(payment.amount_usdt),
        currency=payment.currency,
        chain=payment.chain,
        purpose=payment.purpose,
        description=payment.description,
        agent_reasoning=payment.agent_reasoning,
        status=payment.status,
        requires_human_approval=payment.requires_human_approval,
        approved_by=payment.approved_by,
        approved_at=payment.approved_at.isoformat() if payment.approved_at else None,
        transaction_hash=payment.transaction_hash,
        created_at=payment.created_at.isoformat() if payment.created_at else ""
    )
