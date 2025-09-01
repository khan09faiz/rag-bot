from functools import lru_cache
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings
from app.utils.clean import clean_for_embedding

@lru_cache(maxsize=1)
def _embedder() -> GoogleGenerativeAIEmbeddings:
    # settings.GEMINI_EMBED_MODEL already normalized
    return GoogleGenerativeAIEmbeddings(model=settings.GEMINI_EMBED_MODEL, google_api_key=settings.GEMINI_API_KEY)

def embed_query(text: str) -> list[float]:
    return _embedder().embed_query(clean_for_embedding(text))

def embed_texts(texts: list[str]) -> list[list[float]]:
    processed = [clean_for_embedding(t) for t in texts]
    return _embedder().embed_documents(processed)
