from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.chat import ChatRequest
from app.core.config import settings
from app.repositories.search import SearchRepository
from app.repositories.queries import QueryRepository
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.embedding_service import embed_query
import json, re, time

router = APIRouter()

@router.post('/chat')
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    repo = SearchRepository(db)
    qrepo = QueryRepository(db)
    query_vec = embed_query(payload.query)
    # log query (store cleaned text + vector)
    from app.utils.clean import clean_for_embedding
    cleaned = clean_for_embedding(payload.query)
    try:
        qrepo.create(payload.query, cleaned, query_vec)
        db.commit()
    except Exception:
        db.rollback()
    t0 = time.perf_counter()
    vec_results = repo.vector_search(query_vec, settings.TOP_K)
    lists = [vec_results]
    if payload.hybrid:
        lex = repo.lexical_search(payload.query, settings.TOP_K)
        lists.append(lex)
    if len(lists) > 1:
        fused = repo.rrf(lists, settings.RRF_K)
    else:
        fused = vec_results
    filtered = [c for c in fused if c['score'] >= settings.SIMILARITY_THRESHOLD or payload.hybrid]
    top_context = filtered[:settings.TOP_M_CONTEXT]
    if not top_context:
        # fallback: answer directly without citations
        llm = ChatGoogleGenerativeAI(model=settings.GEMINI_CHAT_MODEL, google_api_key=settings.GEMINI_API_KEY, streaming=True, convert_system_message_to_human=True)
        async def direct_stream():
            from langchain.schema import HumanMessage, SystemMessage
            system_prompt = "You are a helpful assistant. Answer the user question."  # no sources
            async for chunk in llm.astream([SystemMessage(content=system_prompt), HumanMessage(content=payload.query)]):
                if hasattr(chunk, 'content') and chunk.content:
                    yield f"data: {json.dumps({'delta': chunk.content})}\n\n"
        return StreamingResponse(direct_stream(), media_type='text/event-stream')

    numbered = []
    citation_map = []
    for i, c in enumerate(top_context, start=1):
        numbered.append(f"[Source {i}]\n{c['text'][:2000]}")
        citation_map.append({"id": i, "title": c['title'], "page": c['page'], "url": None})
    context_block = "\n\n".join(numbered)

    system_prompt = ("You are a helpful assistant. Answer the user question strictly using the provided sources. "
                     "Cite sources inline using [Source n] where n is the source number. If unsure, say you do not know.")
    user_prompt = f"Question: {payload.query}\n\nSources:\n{context_block}\n\nAnswer:"

    llm = ChatGoogleGenerativeAI(model=settings.GEMINI_CHAT_MODEL, google_api_key=settings.GEMINI_API_KEY, streaming=True, convert_system_message_to_human=True)

    async def event_stream():
        final_text = []
        start_llm = time.perf_counter()
        from langchain.schema import HumanMessage, SystemMessage
        async for chunk in llm.astream([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]):
            if hasattr(chunk, 'content') and chunk.content:
                final_text.append(chunk.content)
                yield f"data: {json.dumps({'delta': chunk.content})}\n\n"
        llm_ms = int((time.perf_counter() - start_llm) * 1000)
        output = ''.join(final_text)
        used_ids = sorted({m for m in re.findall(r"\[Source (\d+)\]", output)})
        used = [c for c in citation_map if str(c['id']) in used_ids]
        timings = {"retrieve_ms": int((start_llm - t0) * 1000), "llm_ms": llm_ms}
        yield f"data: {json.dumps({'citations': used, 'timings': timings})}\n\n"

    return StreamingResponse(event_stream(), media_type='text/event-stream')
