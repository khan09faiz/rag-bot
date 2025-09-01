from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from .config import settings

def add_cors(app: FastAPI):
    # ALLOWED_ORIGINS may be a comma-separated string in env; normalize to list
    origins = []
    raw = getattr(settings, 'ALLOWED_ORIGINS', None) or getattr(settings, 'allowed_origins', [])
    if isinstance(raw, str):
        origins = [o.strip() for o in raw.split(',') if o.strip()]
    elif isinstance(raw, (list, tuple)):
        origins = list(raw)
    else:
        origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
