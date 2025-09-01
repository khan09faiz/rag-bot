from pydantic import BaseModel
from typing import Optional, List

class JobStatus(BaseModel):
    id: str
    status: str
    error: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None

class ChunkCandidate(BaseModel):
    id: str
    score: float
    doc_title: str
    page: int | None = None
    section: str | None = None
    snippet: str

class SearchResponse(BaseModel):
    candidates: List[ChunkCandidate]
    timings: dict
