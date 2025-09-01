from fastapi import Header, HTTPException, status, Depends
from app.core.config import settings

def bearer_auth(authorization: str | None = Header(None)):
    if not settings.BEARER_TOKEN:
        return None
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ",1)[1].strip()
    if token != settings.BEARER_TOKEN:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return None
