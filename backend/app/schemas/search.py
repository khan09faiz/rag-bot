from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str
    top_k: int = 20
    hybrid: bool = True
    rerank: bool = False
