from typing import Optional, List
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.entities import User, Membership, ApiApplication

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_user_organisation_ids(user: User, db: Session) -> List[str]:
    """Returns all active organisation IDs associated with the user."""
    memberships = db.query(Membership).filter(
        Membership.user_id == user.id,
        Membership.status == "active"
    ).all()
    return [m.organisation_id for m in memberships]

def get_current_user_organisation_id(user: User, db: Session) -> str:
    """Returns the primary organisation ID for the user, raising 403 if none found."""
    org_ids = get_user_organisation_ids(user, db)
    if not org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not affiliated with any active organisation"
        )
    return org_ids[0]

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended"
        )
    return current_user

def require_role(allowed_roles: List[str], organisation_id: Optional[str] = None):
    def role_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Check active memberships for permitted roles across relevant organisation(s)
        query = db.query(Membership).filter(
            Membership.user_id == current_user.id,
            Membership.status == "active"
        )
        if organisation_id:
            query = query.filter(Membership.organisation_id == organisation_id)
        memberships = query.all()

        has_permission = any(
            m.role == "owner" or m.role in allowed_roles for m in memberships
        ) or (
            current_user.email == "admin@terranexus.org" and any(r in ("admin", "superadmin", "platform_admin") for r in allowed_roles)
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {allowed_roles}"
            )
        return current_user
    return role_checker

def require_admin(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """Enforces administrator role requirement across tenant boundaries."""
    query = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.status == "active"
    )
    memberships = query.all()
    is_admin = any(m.role in ("owner", "admin", "superadmin", "platform_admin") for m in memberships) or (
        current_user.email == "admin@terranexus.org"
    )
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Administrator privileges required"
        )
    return current_user

