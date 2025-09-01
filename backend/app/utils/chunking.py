from typing import List, Tuple
import math

# Simple char-based chunk approximating token sizes (~4 chars per token)

def chunk_text(text: str, target_tokens: int = 900, overlap_pct: int = 12) -> List[Tuple[str, int]]:
    if not text:
        return []
    approx_chars = target_tokens * 4
    overlap_chars = int(approx_chars * overlap_pct / 100)
    chunks: List[Tuple[str, int]] = []
    start = 0
    ordinal = 0
    while start < len(text):
        end = min(len(text), start + approx_chars)
        chunk = text[start:end]
        tokens_est = math.ceil(len(chunk) / 4)
        chunks.append((chunk, tokens_est))
        if end == len(text):
            break
        start = end - overlap_chars
        ordinal += 1
    return chunks
