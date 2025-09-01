from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db, engine
from app.core.response import success
from app.core.config import settings

router = APIRouter()

@router.get('/healthz')
def health(db: Session = Depends(get_db)):
    pg_ok = True
    err = None
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        pg_ok = False
        err = str(e).split('\n')[0][:300]
    data = {"service": "ok" if pg_ok else "fail", "pg": pg_ok, "models_loaded": True}
    # Include minimal diagnostics in non-production to aid setup
    if not pg_ok and getattr(settings, 'LOG_LEVEL', 'INFO') != 'PROD':
        data["pg_error"] = err
        try:
            # attempt direct connect to show if DNS vs auth
            with engine.connect() as conn:
                pass
        except Exception as e:
            data["engine_error"] = str(e).split('\n')[0][:300]
    return success(data)
