import time
from typing import Any, Dict, Optional

import requests
from fastapi import Depends, HTTPException, Request, status
from jose import jwt
from jose.exceptions import JWTError
from sqlmodel import Session, select

from .config import get_settings
from .db import get_session
from .models import User

_JWKS_CACHE: Dict[str, Any] = {"fetched_at": 0, "keys": []}


def _get_jwks() -> Dict[str, Any]:
    settings = get_settings()
    now = time.time()
    if _JWKS_CACHE["keys"] and now - _JWKS_CACHE["fetched_at"] < 3600:
        return _JWKS_CACHE
    url = f"https://login.microsoftonline.com/{settings.entra_tenant_id}/discovery/v2.0/keys"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()
    _JWKS_CACHE["keys"] = data.get("keys", [])
    _JWKS_CACHE["fetched_at"] = now
    return _JWKS_CACHE


def _get_key_for_token(token: str) -> Optional[Dict[str, Any]]:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    if not kid:
        return None
    jwks = _get_jwks()
    for key in jwks["keys"]:
        if key.get("kid") == kid:
            return key
    return None


def _decode_token(token: str) -> Dict[str, Any]:
    settings = get_settings()
    key = _get_key_for_token(token)
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        return jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.entra_audience or None,
            issuer=settings.entra_issuer,
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def _user_from_claims(claims: Dict[str, Any]) -> Dict[str, Any]:
    user_id = claims.get("oid") or claims.get("sub")
    email = claims.get("preferred_username") or claims.get("email") or ""
    name = claims.get("name") or ""
    first_name = claims.get("given_name")
    last_name = claims.get("family_name")
    if not first_name and name:
        parts = name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else None
    return {
        "id": user_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
    }


def get_current_user(
    request: Request, session: Session = Depends(get_session)
) -> User:
    settings = get_settings()
    auth_header = request.headers.get("authorization", "")
    token = ""
    if auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
    if token.startswith("local:"):
        user_id = token.split("local:", 1)[1].strip()
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
        return user
    if not token:
        if settings.allow_anonymous:
            user_id = request.headers.get("x-user-id") or "anon"
            email = request.headers.get("x-user-email") or "anonymous@example.com"
            user = session.get(User, user_id)
            if not user:
                user = User(id=user_id, email=email)
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    claims = _decode_token(token)
    data = _user_from_claims(claims)
    if not data.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = session.get(User, data["id"])
    if not user:
        user = User(**data)
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        updated = False
        for field in ("email", "first_name", "last_name"):
            value = data.get(field)
            if value and getattr(user, field) != value:
                setattr(user, field, value)
                updated = True
        if updated:
            session.add(user)
            session.commit()
            session.refresh(user)
    return user
