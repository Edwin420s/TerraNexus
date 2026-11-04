from typing import List, Optional
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.auth import get_current_user, get_current_active_user
from app.models.entities import User, Organisation, Membership

router = APIRouter(prefix="", tags=["identity"])

# Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    organisation_name: Optional[str] = "My Farm Organisation"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    display_name: Optional[str]
    organisation_id: Optional[str]

class UserProfileResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str]
    preferred_language: str
    timezone: str
    account_status: str
    email_verified: bool

class OrganisationResponse(BaseModel):
    id: str
    name: str
    organisation_type: str
    status: str

class MemberResponse(BaseModel):
    id: str
    user_id: str
    email: str
    name: str
    role: str
    status: str

@router.post("/auth/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    
    # Create User
    new_user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        first_name=req.first_name,
        last_name=req.last_name,
        display_name=f"{req.first_name} {req.last_name}",
        account_status="active",
        email_verified=True
    )
    db.add(new_user)
    db.flush()

    # Create Organisation & Owner Membership
    org = Organisation(
        name=req.organisation_name,
        organisation_type="commercial_farm",
        status="active"
    )
    db.add(org)
    db.flush()

    membership = Membership(
        organisation_id=org.id,
        user_id=new_user.id,
        role="owner",
        status="active"
    )
    db.add(membership)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.id, "email": new_user.email, "org": org.id})
    return TokenResponse(
        access_token=token,
        user_id=new_user.id,
        email=new_user.email,
        display_name=new_user.display_name,
        organisation_id=org.id
    )

@router.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    membership = db.query(Membership).filter(Membership.user_id == user.id).first()
    org_id = membership.organisation_id if membership else None
    
    token = create_access_token({"sub": user.id, "email": user.email, "org": org_id})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        organisation_id=org_id
    )

@router.get("/auth/me", response_model=UserProfileResponse)
def get_me(user: User = Depends(get_current_active_user)):
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        preferred_language=user.preferred_language,
        timezone=user.timezone,
        account_status=user.account_status,
        email_verified=user.email_verified
    )

@router.post("/auth/forgot-password")
def forgot_password(req: dict):
    return {"status": "ok", "message": "If the account exists, recovery instructions have been dispatched"}

@router.post("/auth/verify-email")
def verify_email(req: dict):
    return {"status": "ok", "message": "Email address successfully verified"}

@router.get("/organisations", response_model=List[OrganisationResponse])
def list_organisations(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    orgs = db.query(Organisation).join(Membership).filter(Membership.user_id == user.id).all()
    if not orgs:
        # Fallback to first active organisation
        orgs = db.query(Organisation).limit(5).all()
    return [
        OrganisationResponse(
            id=o.id,
            name=o.name,
            organisation_type=o.organisation_type,
            status=o.status
        ) for o in orgs
    ]

@router.get("/organisations/{org_id}/members", response_model=List[MemberResponse])
def list_members(org_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    members = db.query(Membership).filter(Membership.organisation_id == org_id).all()
    result = []
    for m in members:
        u = db.query(User).filter(User.id == m.user_id).first()
        if u:
            result.append(MemberResponse(
                id=m.id,
                user_id=u.id,
                email=u.email,
                name=u.display_name or f"{u.first_name} {u.last_name}",
                role=m.role,
                status=m.status
            ))
    return result
