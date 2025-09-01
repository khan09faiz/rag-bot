from pydantic import BaseModel
from typing import List, Dict, Any

class ChatRequest(BaseModel):
    query: str
    top_k: int = 50
    hybrid: bool = True

class Citation(BaseModel):
    id: int
    title: str
    page: int | None = None
    url: str | None = None

class FinalEvent(BaseModel):
    citations: List[Citation]
    timings: Dict[str, Any]
