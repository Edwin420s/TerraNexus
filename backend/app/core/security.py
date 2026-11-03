import hashlib
import os
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from app.core.config import settings

def hash_password(password: str) -> str:
    """Secure password hashing using PBKDF2-HMAC-SHA256 with 260,000 iterations."""
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        260000
    ).hex()
    return f"pbkdf2_sha256$260000${salt}${key}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored PBKDF2 hash."""
    try:
        parts = hashed_password.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        iterations = int(parts[1])
        salt = parts[2]
        expected_key = parts[3]
        
        computed_key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        ).hex()
        return hmac.compare_digest(expected_key, computed_key)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({
        "iat": now,
        "exp": expire,
        "iss": "terranexus-platform"
    })
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer="terranexus-platform"
        )
        return payload
    except jwt.PyJWTError:
        return None
