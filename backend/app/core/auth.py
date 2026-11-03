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
        # Check if default test admin exists for local developer experience
        admin = db.query(User).filter(User.email == "admin@terranexus.org").first()
        if admin:
            return admin
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

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended"
        )
    return current_user

def require_role(allowed_roles: List[str]):
    def role_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Check if user has membership with allowed role in their organisation
        membership = db.query(Membership).filter(Membership.user_id == current_user.id).first()
        if not membership or membership.role not in allowed_roles:
            # Owner is always allowed
            if membership and membership.role == "owner":
                return current_user
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {allowed_roles}"
            )
        return current_user
    return role_checker
