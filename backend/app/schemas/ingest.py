from pydantic import BaseModel
from typing import Any, Dict
from typing import Literal

class IngestTextRequest(BaseModel):
    text: str
    title: str = "Untitled"
    metadata: Dict[str, Any] = {}

class IngestResponseData(BaseModel):
    job_id: str

class IngestResponse(BaseModel):
    status: Literal['success']
    data: IngestResponseData
