from sqlalchemy.orm import Session
from app.models.embedding import Embedding
from typing import List

class EmbeddingRepository:
    def __init__(self, session: Session):
        self.session = session

    def bulk_upsert(self, chunk_ids: List[str], vectors: List[list], model_name: str, dim: int):
        for cid, vec in zip(chunk_ids, vectors):
            self.session.merge(Embedding(chunk_id=cid, model_name=model_name, dim=dim, embedding=vec))
        self.session.flush()
