from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets

from fastapi import Depends, Request
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuthSession, User


_password_hasher = PasswordHash.recommended()
SESSION_COOKIE_NAME = "studyflow_session"
SESSION_LIFETIME = timedelta(hours=12)
SESSION_SAME_SITE = "lax"


def password_hash(password: str) -> str:
    """Return an Argon2 password hash suitable for database storage."""
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check a password against a previously stored password hash."""
    return _password_hasher.verify(password, password_hash)


def create_session_token() -> str:
    """Create an unpredictable token for a browser session."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Hash a high-entropy session token before storing or querying it."""
    return sha256(token.encode("utf-8")).hexdigest()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """Return the user for a valid session cookie, otherwise None."""
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None

    auth_session = db.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hash_session_token(token),
        )
    )
    if auth_session is None:
        return None

    expires_at = auth_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        return None

    return db.get(User, auth_session.user_id)
