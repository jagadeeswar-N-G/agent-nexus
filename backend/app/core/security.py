"""
Security utilities for Ed25519 authentication and JWT tokens
"""
import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional
import nacl.signing
import nacl.encoding
import nacl.exceptions
from jose import JWTError, jwt

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, use env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# In-memory challenge store (use Redis in production)
_challenge_store: dict[str, tuple[bytes, datetime]] = {}


def generate_challenge() -> bytes:
    """Generate a random 32-byte challenge"""
    return secrets.token_bytes(32)


def store_challenge(public_key: str, challenge: bytes, ttl_seconds: int = 300):
    """Store challenge with expiry (5 minutes default)"""
    expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    _challenge_store[public_key] = (challenge, expires_at)


def get_challenge(public_key: str) -> Optional[bytes]:
    """Retrieve and validate challenge"""
    if public_key not in _challenge_store:
        return None

    challenge, expires_at = _challenge_store[public_key]

    # Check if expired
    if datetime.utcnow() > expires_at:
        del _challenge_store[public_key]
        return None

    # Remove challenge after retrieval (single use)
    del _challenge_store[public_key]
    return challenge


def verify_ed25519_signature(
    public_key_b64: str,
    message: bytes,
    signature_b64: str
) -> bool:
    """
    Verify Ed25519 signature

    Args:
        public_key_b64: Base64-encoded public key
        message: Raw message bytes that were signed
        signature_b64: Base64-encoded signature

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Decode public key
        public_key_bytes = base64.b64decode(public_key_b64)
        verify_key = nacl.signing.VerifyKey(public_key_bytes)

        # Decode signature
        signature_bytes = base64.b64decode(signature_b64)

        # Verify signature
        verify_key.verify(message, signature_bytes)
        return True

    except (nacl.exceptions.BadSignatureError, ValueError, Exception):
        return False


def create_access_token(agent_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        agent_id: Agent's unique identifier (public key)
        expires_delta: Custom expiration time

    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": agent_id,  # Subject: agent identifier
        "exp": expire,    # Expiration time
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"  # Token type
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return agent_id

    Args:
        token: JWT token string

    Returns:
        agent_id if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        agent_id: str = payload.get("sub")

        if agent_id is None:
            return None

        return agent_id

    except JWTError:
        return None


def refresh_access_token(old_token: str) -> Optional[str]:
    """
    Refresh an access token (rolling refresh)

    Args:
        old_token: Existing JWT token

    Returns:
        New JWT token if old one is valid, None otherwise
    """
    agent_id = verify_token(old_token)

    if agent_id is None:
        return None

    # Issue new token
    return create_access_token(agent_id)
